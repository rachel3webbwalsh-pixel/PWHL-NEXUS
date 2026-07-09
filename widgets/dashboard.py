from widgets.header import draw_header
from widgets.standings_widget import draw_standings
from widgets.footer import draw_footer

def draw_dashboard(standings):
    draw_header()
    draw_standings(standings)
    draw_footer()