from api.teams import TEAMS
from theme import FAVORITE_TEAM, LINE_LENGTH


def draw_team_hub(standings):
    print()
    print("TEAM HUB")
    print("-" * LINE_LENGTH)

    favorite = None

    for team in standings:
        if team["team"] == FAVORITE_TEAM:
            favorite = team
            break

    if favorite is None:
        print(f"{FAVORITE_TEAM} not found.")
        return

    team_info = TEAMS.get(FAVORITE_TEAM, {})
    display_name = team_info.get("display_name", FAVORITE_TEAM)
    abbr = team_info.get("abbr", "")

    record = f"{favorite['wins']}-{favorite['losses']}-{favorite['otl']}"

    is_preseason = (
        favorite["wins"] == 0
        and favorite["losses"] == 0
        and favorite["otl"] == 0
        and favorite["points"] == 0
    )

    print(f"{display_name} ({abbr})")

    if is_preseason:
        print("Status: PRESEASON")
        print("League standings begin when the puck drops.")
    else:
        print(f"League Rank: #{favorite['rank']}")

    print(f"Record: {record}")
    print(f"Points: {favorite['points']}")
    print()