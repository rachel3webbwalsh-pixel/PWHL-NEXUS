"""Normalized standings provider for PWHL NEXUS."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from api.pwhl_client import PWHLClientError, get_official_standings


CURRENT_SEASON_ID = 8

CACHE_FILE = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "standings_cache.json"
)


PLACEHOLDER_STANDINGS = [
    {
        "rank": 1,
        "team": "Montréal Victoire",
        "abbreviation": "MTL",
        "gp": 0,
        "rw": 0,
        "otw": 0,
        "otl": 0,
        "losses": 0,
        "points": 0,
        "pct": 0.0,
    },
    {
        "rank": 2,
        "team": "Ottawa Charge",
        "abbreviation": "OTT",
        "gp": 0,
        "rw": 0,
        "otw": 0,
        "otl": 0,
        "losses": 0,
        "points": 0,
        "pct": 0.0,
    },
    {
        "rank": 3,
        "team": "Minnesota Frost",
        "abbreviation": "MIN",
        "gp": 0,
        "rw": 0,
        "otw": 0,
        "otl": 0,
        "losses": 0,
        "points": 0,
        "pct": 0.0,
    },
    {
        "rank": 4,
        "team": "Boston Fleet",
        "abbreviation": "BOS",
        "gp": 0,
        "rw": 0,
        "otw": 0,
        "otl": 0,
        "losses": 0,
        "points": 0,
        "pct": 0.0,
    },
]


def _first_value(
    row: dict[str, Any],
    names: Iterable[str],
    default: Any = None,
) -> Any:
    """Return the first matching non-empty field from a row."""

    lowered = {
        str(key).lower(): value
        for key, value in row.items()
    }

    for name in names:
        value = lowered.get(name.lower())
        if value not in (None, ""):
            return value

    return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _looks_like_standing(row: Any) -> bool:
    if not isinstance(row, dict):
        return False

    keys = {str(key).lower() for key in row}

    has_team = bool(
        keys
        & {
            "team",
            "team_name",
            "name",
            "teamname",
            "team_code",
            "shortname",
        }
    )

    has_record = bool(
        keys
        & {
            "points",
            "pts",
            "games_played",
            "gamesplayed",
            "gp",
            "wins",
            "losses",
        }
    )

    return has_team and has_record


def _find_standing_rows(value: Any) -> list[dict[str, Any]]:
    """
    Recursively find the list that contains standings rows.

    HockeyTech sometimes wraps data differently depending on the
    selected season or standings type, so this avoids relying on one
    fragile response path.
    """

    if isinstance(value, list):
        matching = [
            item for item in value
            if _looks_like_standing(item)
        ]

        if matching:
            return matching

        for item in value:
            found = _find_standing_rows(item)
            if found:
                return found

    elif isinstance(value, dict):
        preferred_keys = (
            "teams",
            "standings",
            "data",
            "sections",
            "records",
        )

        for key in preferred_keys:
            if key in value:
                found = _find_standing_rows(value[key])
                if found:
                    return found

        for child in value.values():
            found = _find_standing_rows(child)
            if found:
                return found

    return []


def _normalize_row(
    row: dict[str, Any],
    fallback_rank: int,
) -> dict[str, Any]:
    team = str(
        _first_value(
            row,
            (
                "team_name",
                "teamname",
                "team",
                "name",
                "team_long_name",
            ),
            "Unknown Team",
        )
    ).strip()

    abbreviation = str(
        _first_value(
            row,
            (
                "team_code",
                "teamcode",
                "abbreviation",
                "shortname",
                "team_short_name",
            ),
            "",
        )
    ).strip().upper()

    rank = _to_int(
        _first_value(
            row,
            ("rank", "position", "overall_rank", "place"),
            fallback_rank,
        ),
        fallback_rank,
    )

    gp = _to_int(
        _first_value(
            row,
            ("games_played", "gamesplayed", "gp"),
        )
    )

    points = _to_int(
        _first_value(
            row,
            ("points", "pts"),
        )
    )

    rw = _to_int(
        _first_value(
            row,
            (
                "regulation_wins",
                "regulationwins",
                "rw",
                "wins",
            ),
        )
    )

    otw = _to_int(
        _first_value(
            row,
            (
                "overtime_wins",
                "overtimewins",
                "ot_wins",
                "otw",
            ),
        )
    )

    otl = _to_int(
        _first_value(
            row,
            (
                "overtime_losses",
                "overtimelosses",
                "ot_losses",
                "otl",
            ),
        )
    )

    losses = _to_int(
        _first_value(
            row,
            (
                "regulation_losses",
                "regulationlosses",
                "losses",
                "l",
            ),
        )
    )

    pct = _to_float(
        _first_value(
            row,
            (
                "percentage",
                "pct",
                "point_percentage",
                "pointpercentage",
            ),
        )
    )

    return {
        "rank": rank,
        "team": team,
        "abbreviation": abbreviation,
        "gp": gp,
        "rw": rw,
        "otw": otw,
        "otl": otl,
        "losses": losses,
        "points": points,
        "pct": pct,
    }


def parse_official_standings(
    payload: dict[str, Any],
) -> list[dict[str, Any]]:
    rows = _find_standing_rows(payload)

    if not rows:
        raise ValueError(
            "Official PWHL response contained no recognizable "
            "standings rows."
        )

    normalized = [
        _normalize_row(row, index)
        for index, row in enumerate(rows, start=1)
    ]

    normalized = [
        row
        for row in normalized
        if row["team"] != "Unknown Team"
    ]

    if not normalized:
        raise ValueError(
            "PWHL standings rows could not be normalized."
        )

    normalized.sort(
        key=lambda row: (
            row["rank"],
            -row["points"],
            row["team"],
        )
    )

    return normalized


def _save_cache(standings: list[dict[str, Any]]) -> None:
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)

    CACHE_FILE.write_text(
        json.dumps(
            standings,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def _load_cache() -> list[dict[str, Any]]:
    if not CACHE_FILE.exists():
        return []

    try:
        data = json.loads(
            CACHE_FILE.read_text(encoding="utf-8")
        )
    except (OSError, json.JSONDecodeError):
        return []

    if not isinstance(data, list):
        return []

    return [
        row for row in data
        if isinstance(row, dict)
    ]


def get_standings(
    season_id: int = CURRENT_SEASON_ID,
) -> list[dict[str, Any]]:
    """
    Return normalized PWHL standings.

    Source order:
    1. Official HockeyTech/PWHL feed
    2. Last successful local cache
    3. Safe placeholder data
    """

    try:
        payload = get_official_standings(season_id)
        standings = parse_official_standings(payload)

        _save_cache(standings)

        print(
            f"Loaded {len(standings)} teams from "
            "official PWHL standings."
        )

        return standings

    except (PWHLClientError, ValueError, OSError) as exc:
        print(f"Official PWHL standings unavailable: {exc}")

    cached = _load_cache()

    if cached:
        print(
            f"Using cached standings "
            f"({len(cached)} teams)."
        )
        return cached

    print("Using safe placeholder standings.")
    return PLACEHOLDER_STANDINGS.copy()


if __name__ == "__main__":
    from pprint import pprint

    pprint(get_standings())