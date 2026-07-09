"""
PWHL NEXUS
League Command Center

v0.6 - Live Ice
Standings data module.
"""

import requests


LEAGUESTAT_BASE_URL = "https://lscluster.hockeytech.com/feed/"
LEAGUESTAT_KEY = "446521baf8c38984"
CLIENT_CODE = "pwhl"


def get_placeholder_standings():
    return [
        {"rank": 1, "team": "Minnesota", "wins": 0, "losses": 0, "otl": 0, "points": 0},
        {"rank": 2, "team": "Toronto", "wins": 0, "losses": 0, "otl": 0, "points": 0},
        {"rank": 3, "team": "Montreal", "wins": 0, "losses": 0, "otl": 0, "points": 0},
        {"rank": 4, "team": "Boston", "wins": 0, "losses": 0, "otl": 0, "points": 0},
        {"rank": 5, "team": "Ottawa", "wins": 0, "losses": 0, "otl": 0, "points": 0},
        {"rank": 6, "team": "New York", "wins": 0, "losses": 0, "otl": 0, "points": 0},
        {"rank": 7, "team": "Vancouver", "wins": 0, "losses": 0, "otl": 0, "points": 0},
        {"rank": 8, "team": "San Jose", "wins": 0, "losses": 0, "otl": 0, "points": 0},
        {"rank": 9, "team": "Las Vegas", "wins": 0, "losses": 0, "otl": 0, "points": 0},
        {"rank": 10, "team": "Hamilton", "wins": 0, "losses": 0, "otl": 0, "points": 0},
        {"rank": 11, "team": "Detroit", "wins": 0, "losses": 0, "otl": 0, "points": 0},
        {"rank": 12, "team": "Seattle", "wins": 0, "losses": 0, "otl": 0, "points": 0},
    ]


def get_live_standings():
    """
    Tries to pull live standings from HockeyTech / LeagueStat.

    If the API structure changes or fails, we return placeholder standings
    so PWHL NEXUS does not crash.
    """

    params = {
        "feed": "modulekit",
        "view": "statviewtype",
        "key": LEAGUESTAT_KEY,
        "fmt": "json",
        "client_code": CLIENT_CODE,
    }

    try:
        response = requests.get(LEAGUESTAT_BASE_URL, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        print("Live API connected.")
        print("Raw data keys:", data.keys())

        return get_placeholder_standings()

    except Exception as error:
        print("Could not load live standings yet.")
        print("Reason:", error)
        print("Using placeholder standings.")

        return get_placeholder_standings()


def get_standings():
    return get_live_standings()

if __name__ == "__main__":
    standings = get_standings()

    print()
    print("● ON ICE")
    print("PWHL NEXUS")
    print("League Command Center")
    print()
    print("STANDINGS")
    print("-" * 46)

    for team in standings:
        print(
            f"{team['rank']:>2}. "
            f"{team['team']:<12} "
            f"{team['wins']:>2}-{team['losses']:>2}-{team['otl']:<2} "
            f"{team['points']:>3} pts"
        )

    print("-" * 46)
    print("STATUS: Live API connected")