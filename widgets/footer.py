from theme import LINE_LENGTH, STATUS_MESSAGE, VERSION


def draw_footer():
    print("-" * LINE_LENGTH)
    print(f"STATUS: {STATUS_MESSAGE}")
    print(VERSION)