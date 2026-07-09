from widgets.header import draw_header
from widgets.game_center import draw_game_center
from widgets.team_hub import draw_team_hub
from widgets.standings_widget import draw_standings
from widgets.footer import draw_footer


def draw_dashboard(standings, games):
    draw_header()
    draw_game_center(games)
    draw_team_hub(standings)
    draw_standings(standings)
    draw_footer()