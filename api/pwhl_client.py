"""
PWHL NEXUS
League Command Center

Multi-source standings client.

Sources:
1. Official PWHL standings webpage
2. Existing HockeyTech / LeagueStat feed
3. Last-good local cache
"""

from __future__ import annotations

import json
import re
import unicodedata
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

import requests


OFFICIAL_STANDINGS_URLS = (
    "https://www.thepwhl.com/en/standings-old",
    "https://www.thepwhl.com/en/standings",
)

LEAGUESTAT_BASE_URL = "https://lscluster.hockeytech.com/feed/"
LEAGUESTAT_KEY = "446521baf8c38984"
CLIENT_CODE = "pwhl"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = PROJECT_ROOT / "data" / "standings_cache.json"

REQUEST_HEADERS = {
    "User-Agent": (
        "PWHL-NEXUS/1.5 "
        "(Raspberry Pi league dashboard; standings reader)"
    )
}

TEAM_ALIASES = {
    "boston": "Boston",
    "boston fleet": "Boston",
    "minnesota": "Minnesota",
    "minnesota frost": "Minnesota",
    "montreal": "Montreal",
    "montréal": "Montreal",
    "montreal victoire": "Montreal",
    "montréal victoire": "Montreal",
    "new york": "New York",
    "new york sirens": "New York",
    "ottawa": "Ottawa",
    "ottawa charge": "Ottawa",
    "seattle": "Seattle",
    "seattle torrent": "Seattle",
    "toronto": "Toronto",
    "toronto sceptres": "Toronto",
    "vancouver": "Vancouver",
    "vancouver goldeneyes": "Vancouver",
}


def _plain_text(value: Any) -> str:
    """Return normalized text suitable for matching."""
    text = unicodedata.normalize("NFKC", str(value or ""))
    return " ".join(text.replace("\xa0", " ").split())


def _team_key(value: Any) -> str:
    """Normalize an official/full team name to the project team key."""
    text = _plain_text(value)
    text = re.sub(r"^[xyez]\s*-\s*", "", text, flags=re.IGNORECASE)
    lowered = text.casefold()

    if lowered in TEAM_ALIASES:
        return TEAM_ALIASES[lowered]

    # Handle decorations such as ranking markers or playoff labels.
    for alias, project_name in TEAM_ALIASES.items():
        if alias in lowered:
            return project_name

    return text


def _as_int(value: Any, default: int = 0) -> int:
    """Extract the first integer from a value."""
    match = re.search(r"-?\d+", _plain_text(value))
    return int(match.group()) if match else default


def _as_float(value: Any) -> float | None:
    """Extract a floating-point value when available."""
    match = re.search(r"-?(?:\d+\.\d+|\d+)", _plain_text(value))
    return float(match.group()) if match else None


class _TableParser(HTMLParser):
    """Collect HTML table rows and cells without extra dependencies."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._table_depth = 0
        self._current_table: list[list[str]] | None = None
        self._current_row: list[str] | None = None
        self._cell_parts: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        tag = tag.lower()

        if tag == "table":
            self._table_depth += 1
            if self._table_depth == 1:
                self._current_table = []

        elif self._table_depth == 1 and tag == "tr":
            self._current_row = []

        elif (
            self._table_depth == 1
            and tag in {"th", "td"}
            and self._current_row is not None
        ):
            self._cell_parts = []

        elif self._cell_parts is not None and tag in {"br", "p", "div"}:
            self._cell_parts.append(" ")

    def handle_data(self, data: str) -> None:
        if self._cell_parts is not None:
            self._cell_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()

        if (
            self._table_depth == 1
            and tag in {"th", "td"}
            and self._cell_parts is not None
            and self._current_row is not None
        ):
            self._current_row.append(_plain_text("".join(self._cell_parts)))
            self._cell_parts = None

        elif (
            self._table_depth == 1
            and tag == "tr"
            and self._current_row is not None
            and self._current_table is not None
        ):
            if any(self._current_row):
                self._current_table.append(self._current_row)
            self._current_row = None

        elif tag == "table":
            if self._table_depth == 1 and self._current_table:
                self.tables.append(self._current_table)
                self._current_table = None
            self._table_depth = max(0, self._table_depth - 1)


def _header_name(value: str) -> str:
    text = _plain_text(value).casefold()
    aliases = {
        "pwhl": "team",
        "club": "team",
        "team": "team",
        "gp": "games_played",
        "games played": "games_played",
        "pts": "points",
        "points": "points",
        "w": "regulation_wins",
        "rw": "regulation_wins",
        "otw": "overtime_wins",
        "ow": "overtime_wins",
        "otl": "otl",
        "ol": "otl",
        "l": "losses",
        "losses": "losses",
        "pct": "points_percentage",
        "p%": "points_percentage",
        "gf": "goals_for",
        "ga": "goals_against",
        "diff": "goal_differential",
        "gd": "goal_differential",
    }
    return aliases.get(text, text)


def _parse_official_table(html: str) -> list[dict[str, Any]]:
    parser = _TableParser()
    parser.feed(html)

    for table in parser.tables:
        if len(table) < 2:
            continue

        # Locate the row that looks like the standings header.
        header_index = None
        mapped_headers: list[str] = []

        for index, row in enumerate(table[:8]):
            headers = [_header_name(cell) for cell in row]
            if (
                "team" in headers
                and "points" in headers
                and (
                    "games_played" in headers
                    or "regulation_wins" in headers
                )
            ):
                header_index = index
                mapped_headers = headers
                break

        if header_index is None:
            continue

        standings: list[dict[str, Any]] = []

        for row in table[header_index + 1 :]:
            if len(row) < 3:
                continue

            values = {
                mapped_headers[index]: cell
                for index, cell in enumerate(row)
                if index < len(mapped_headers)
            }

            team = _team_key(values.get("team", ""))
            if team not in set(TEAM_ALIASES.values()):
                continue

            regulation_wins = _as_int(values.get("regulation_wins"))
            overtime_wins = _as_int(values.get("overtime_wins"))
            total_wins = regulation_wins + overtime_wins

            item: dict[str, Any] = {
                "rank": len(standings) + 1,
                "team": team,
                "games_played": _as_int(values.get("games_played")),
                "wins": total_wins,
                "regulation_wins": regulation_wins,
                "overtime_wins": overtime_wins,
                "losses": _as_int(values.get("losses")),
                "otl": _as_int(values.get("otl")),
                "points": _as_int(values.get("points")),
                "source": "official_pwhl_website",
            }

            percentage = _as_float(values.get("points_percentage"))
            if percentage is not None:
                item["points_percentage"] = percentage

            for source_key, output_key in (
                ("goals_for", "goals_for"),
                ("goals_against", "goals_against"),
                ("goal_differential", "goal_differential"),
            ):
                if source_key in values:
                    item[output_key] = _as_int(values[source_key])

            standings.append(item)

        if standings:
            standings.sort(
                key=lambda team: (
                    -team.get("points", 0),
                    -team.get("regulation_wins", 0),
                    team.get("games_played", 0),
                )
            )
            for rank, team in enumerate(standings, start=1):
                team["rank"] = rank
            return standings

    return []


def get_official_website_standings(
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """Read standings displayed on the official PWHL website."""
    http = session or requests.Session()
    errors: list[str] = []

    for url in OFFICIAL_STANDINGS_URLS:
        try:
            response = http.get(
                url,
                headers=REQUEST_HEADERS,
                timeout=15,
            )
            response.raise_for_status()

            standings = _parse_official_table(response.text)
            if standings:
                print(
                    f"Official PWHL website connected: "
                    f"{len(standings)} teams."
                )
                return standings

            errors.append(f"{url}: no standings table found")

        except requests.RequestException as error:
            errors.append(f"{url}: {error}")

    print("Official PWHL website standings unavailable.")
    for error in errors:
        print(" -", error)

    return []


def _find_candidate_lists(value: Any):
    """Yield nested lists from an unknown API response."""
    if isinstance(value, list):
        yield value
        for item in value:
            yield from _find_candidate_lists(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _find_candidate_lists(item)


def _first_value(item: dict[str, Any], names: tuple[str, ...]) -> Any:
    lowered = {str(key).casefold(): value for key, value in item.items()}
    for name in names:
        if name.casefold() in lowered:
            return lowered[name.casefold()]
    return None


def _parse_leaguestat_payload(payload: Any) -> list[dict[str, Any]]:
    """Best-effort normalization for HockeyTech's nested JSON."""
    for candidate in _find_candidate_lists(payload):
        parsed: list[dict[str, Any]] = []

        for raw_item in candidate:
            if not isinstance(raw_item, dict):
                continue

            raw_team = _first_value(
                raw_item,
                (
                    "team",
                    "team_name",
                    "name",
                    "teamname",
                    "teamName",
                    "team_code",
                ),
            )
            team = _team_key(raw_team)

            if team not in set(TEAM_ALIASES.values()):
                continue

            points_value = _first_value(
                raw_item,
                ("points", "pts", "team_points"),
            )
            wins_value = _first_value(
                raw_item,
                ("wins", "w", "total_wins"),
            )

            # A real standings row should contain at least points or wins.
            if points_value is None and wins_value is None:
                continue

            parsed.append(
                {
                    "rank": _as_int(
                        _first_value(
                            raw_item,
                            ("rank", "position", "overall_rank"),
                        ),
                        len(parsed) + 1,
                    ),
                    "team": team,
                    "games_played": _as_int(
                        _first_value(
                            raw_item,
                            ("games_played", "gp", "games"),
                        )
                    ),
                    "wins": _as_int(wins_value),
                    "losses": _as_int(
                        _first_value(
                            raw_item,
                            ("losses", "l"),
                        )
                    ),
                    "otl": _as_int(
                        _first_value(
                            raw_item,
                            ("otl", "ot_losses", "overtime_losses"),
                        )
                    ),
                    "points": _as_int(points_value),
                    "source": "hockeytech_api",
                }
            )

        if len(parsed) >= 4:
            parsed.sort(
                key=lambda team: (
                    team.get("rank", 999),
                    -team.get("points", 0),
                )
            )
            for rank, team in enumerate(parsed, start=1):
                team["rank"] = rank
            return parsed

    return []


def get_hockeytech_standings(
    session: requests.Session | None = None,
) -> list[dict[str, Any]]:
    """Try the project's existing HockeyTech / LeagueStat source."""
    http = session or requests.Session()
    params = {
        "feed": "modulekit",
        "view": "statviewtype",
        "key": LEAGUESTAT_KEY,
        "fmt": "json",
        "client_code": CLIENT_CODE,
    }

    try:
        response = http.get(
            LEAGUESTAT_BASE_URL,
            params=params,
            headers=REQUEST_HEADERS,
            timeout=12,
        )
        response.raise_for_status()
        standings = _parse_leaguestat_payload(response.json())

        if standings:
            print(
                f"HockeyTech API connected: "
                f"{len(standings)} teams."
            )
        else:
            print("HockeyTech responded, but no standings rows were found.")

        return standings

    except (requests.RequestException, ValueError) as error:
        print("HockeyTech standings unavailable:", error)
        return []


def merge_standings(
    official: list[dict[str, Any]],
    api: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Use official standings as the base and fill missing fields from the API.

    API-only teams are retained, allowing future expansion without changing
    the dashboard code.
    """
    if not official:
        return api
    if not api:
        return official

    api_by_team = {item["team"]: item for item in api}
    merged: list[dict[str, Any]] = []

    for official_item in official:
        item = dict(official_item)
        api_item = api_by_team.pop(item["team"], None)

        if api_item:
            for key, value in api_item.items():
                if key not in item or item[key] in (None, ""):
                    item[key] = value
            item["sources"] = [
                "official_pwhl_website",
                "hockeytech_api",
            ]

        merged.append(item)

    merged.extend(api_by_team.values())
    merged.sort(
        key=lambda team: (
            -team.get("points", 0),
            -team.get("regulation_wins", team.get("wins", 0)),
            team.get("games_played", 0),
        )
    )

    for rank, team in enumerate(merged, start=1):
        team["rank"] = rank

    return merged


def save_cache(standings: list[dict[str, Any]]) -> None:
    if not standings:
        return

    try:
        CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        CACHE_PATH.write_text(
            json.dumps(standings, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    except OSError as error:
        print("Could not save standings cache:", error)


def load_cache() -> list[dict[str, Any]]:
    try:
        cached = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        if isinstance(cached, list) and cached:
            print(f"Using cached standings: {len(cached)} teams.")
            return cached
    except (OSError, ValueError, TypeError):
        pass

    return []


class PWHLClient:
    """Central data client used by PWHL NEXUS."""

    def __init__(self) -> None:
        self.session = requests.Session()

    def get_standings(self) -> list[dict[str, Any]]:
        official = get_official_website_standings(self.session)
        api = get_hockeytech_standings(self.session)
        standings = merge_standings(official, api)

        if standings:
            save_cache(standings)
            return standings

        return load_cache()

    def test_connection(self) -> None:
        print("Testing PWHL data sources...")
        standings = self.get_standings()
        print(f"Standings rows available: {len(standings)}")


if __name__ == "__main__":
    client = PWHLClient()
    client.test_connection()