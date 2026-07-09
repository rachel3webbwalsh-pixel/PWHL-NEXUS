from theme import LINE_LENGTH


def draw_standings(standings):

    print("STANDINGS")
    print("-" * LINE_LENGTH)

    for team in standings:
        print(
            f"{team['rank']:>2}. "
            f"{team['team']:<12} "
            f"{team['wins']}-{team['losses']}-{team['otl']} "
            f"{team['points']} pts"
        )