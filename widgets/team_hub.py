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

    print(f"Favorite Team: {favorite['team']}")
    print(f"Rank: {favorite['rank']}")
    print(f"Record: {favorite['wins']}-{favorite['losses']}-{favorite['otl']}")
    print(f"Points: {favorite['points']}")