"""
PWHL NEXUS
League Command Center

v1.2 - Team Hub
"""

from api.standings import get_standings
from api.schedule import get_today_games
from widgets.dashboard import draw_dashboard


standings = get_standings()
games = get_today_games()

draw_dashboard(standings, games)