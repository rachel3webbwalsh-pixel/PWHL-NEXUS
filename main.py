"""
PWHL NEXUS
League Command Center

v1.4.1 - Graphical Team Hub
"""

from api.schedule import get_today_games
from api.standings import get_standings
from widgets.dashboard_gui import run_dashboard


def main() -> None:
    standings = get_standings()
    games = get_today_games()

    run_dashboard(standings, games)


if __name__ == "__main__":
    main()