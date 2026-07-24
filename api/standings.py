"""
PWHL NEXUS
League Command Center

v1.5 - Multi-Source Standings
"""

from __future__ import annotations

from api.pwhl_client import PWHLClient


def get_placeholder_standings():
    """Safe final fallback so the graphical dashboard never crashes."""
    teams = [
        "Boston",
        "Minnesota",
        "Montreal",
        "New York",
        "Ottawa",
        "Seattle",
        "Toronto",
        "Vancouver",
    ]

    return [
        {
            "rank": rank,
            "team": team,
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "otl": 0,
            "points": 0,
            "source": "placeholder",
        }
        for rank, team in enumerate(teams, start=1)
    ]


def get_standings():
    """
    Return normalized standings while preserving the interface used by
    main.py and dashboard_gui.py.
    """
    client = PWHLClient()
    standings = client.get_standings()

    if standings:
        return standings

    print("No live or cached standings available.")
    print("Using safe placeholder standings.")
    return get_placeholder_standings()


if __name__ == "__main__":
    standings = get_standings()

    print()
    print("● ON ICE")
    print("PWHL NEXUS")
    print("League Command Center")
    print()
    print("STANDINGS")
    print("-" * 58)

    for team in standings:
        print(
            f"{team['rank']:>2}. "
            f"{team['team']:<12} "
            f"GP {team.get('games_played', 0):>2}  "
            f"{team['wins']:>2}-{team['losses']:>2}-"
            f"{team['otl']:<2}  "
            f"{team['points']:>3} pts  "
            f"[{team.get('source', 'merged')}]"
        )

    print("-" * 58)