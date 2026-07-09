from theme import LINE_LENGTH


def draw_game_center(games):
    print()
    print("GAME CENTER")
    print("-" * LINE_LENGTH)

    if not games:
        print("OFF SEASON")
        print("No games scheduled.")
        print("See you when the puck drops!")
        print()
        return

    for game in games:
        print(f"{game['away']} @ {game['home']}")
        print(f"{game['time']}")