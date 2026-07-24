"""HTTP client for official PWHL/HockeyTech data."""

from __future__ import annotations

from typing import Any

import requests


BASE_URL = "https://lscluster.hockeytech.com/feed/index.php"
CLIENT_CODE = "pwhl"
API_KEY = "446521baf8c38984"

DEFAULT_TIMEOUT = 15


class PWHLClientError(RuntimeError):
    """Raised when PWHL data cannot be retrieved or understood."""


def _request(params: dict[str, Any]) -> dict[str, Any]:
    request_params = {
        "key": API_KEY,
        "client_code": CLIENT_CODE,
        **params,
    }

    try:
        response = requests.get(
            BASE_URL,
            params=request_params,
            timeout=DEFAULT_TIMEOUT,
            headers={
                "User-Agent": "PWHL-NEXUS/1.5",
                "Accept": "application/json",
            },
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise PWHLClientError(f"PWHL request failed: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        preview = response.text[:200].replace("\n", " ")
        raise PWHLClientError(
            f"PWHL returned invalid JSON: {preview}"
        ) from exc

    if not isinstance(payload, dict):
        raise PWHLClientError(
            f"Unexpected PWHL response type: {type(payload).__name__}"
        )

    if payload.get("error"):
        raise PWHLClientError(str(payload["error"]))

    return payload


def get_seasons() -> dict[str, Any]:
    """Return the official list of PWHL seasons."""

    return _request(
        {
            "feed": "modulekit",
            "view": "seasons",
        }
    )


def get_official_standings(season_id: int = 8) -> dict[str, Any]:
    """Return official standings data for one PWHL season."""

    return _request(
        {
            "feed": "modulekit",
            "view": "statviewtype",
            "stat": "conference",
            "type": "standings",
            "season_id": season_id,
        }
    )


if __name__ == "__main__":
    from pprint import pprint

    print("Testing official PWHL standings connection...")
    pprint(get_official_standings())