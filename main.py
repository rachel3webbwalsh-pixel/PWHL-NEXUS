"""
PWHL NEXUS
League Command Center

v1.0 - Dashboard Framework
"""

from api.standings import get_standings
from widgets.dashboard import draw_dashboard


standings = get_standings()

draw_dashboard(standings)