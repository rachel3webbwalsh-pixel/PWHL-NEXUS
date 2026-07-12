"""
PWHL NEXUS
League Command Center

v1.4.0 - Fullscreen Graphical Framework
"""

import math
import sys

import pygame

from api.teams import TEAMS
from theme import FAVORITE_TEAM 

# Core colors
BLACK = (0, 0, 0)
PANEL_BLACK = (12, 12, 16)
NEON_PURPLE = (177, 92, 255)
SOFT_PURPLE = (126, 72, 170)
WHITE = (245, 245, 245)
MUTED_TEXT = (150, 150, 165)


def scaled(value: int, scale: float) -> int:
    """Scale a layout measurement while keeping it at least one pixel."""
    return max(1, round(value * scale))


def draw_glowing_dot(
    screen: pygame.Surface,
    center: tuple[int, int],
    radius: int,
    pulse: float,
) -> None:
    """Draw the animated purple ON ICE indicator."""

    glow_radius = radius * 4
    glow_surface = pygame.Surface(
        (glow_radius * 2, glow_radius * 2),
        pygame.SRCALPHA,
    )

    glow_alpha = int(45 + (pulse * 35))

    pygame.draw.circle(
        glow_surface,
        (*NEON_PURPLE, glow_alpha),
        (glow_radius, glow_radius),
        radius * 3,
    )

    pygame.draw.circle(
        glow_surface,
        (*NEON_PURPLE, 90),
        (glow_radius, glow_radius),
        radius * 2,
    )

    screen.blit(
        glow_surface,
        (
            center[0] - glow_radius,
            center[1] - glow_radius,
        ),
    )

    pygame.draw.circle(screen, NEON_PURPLE, center, radius)


def draw_panel(
    screen: pygame.Surface,
    rectangle: pygame.Rect,
    title: str,
    title_font: pygame.font.Font,
    border_width: int,
    corner_radius: int,
    padding: int,
) -> None:
    """Draw one outlined dashboard section."""

    pygame.draw.rect(
        screen,
        PANEL_BLACK,
        rectangle,
        border_radius=corner_radius,
    )

    pygame.draw.rect(
        screen,
        SOFT_PURPLE,
        rectangle,
        width=border_width,
        border_radius=corner_radius,
    )

    title_surface = title_font.render(title, True, NEON_PURPLE)

    screen.blit(
        title_surface,
        (
            rectangle.left + padding,
            rectangle.top + padding,
        ),
    )


def run_dashboard(standings, games) -> None:
    """Launch the graphical PWHL NEXUS dashboard."""

    pygame.init()

    try:
        screen = pygame.display.set_mode((720, 1280))

    except pygame.error as error:
        pygame.quit()
        raise RuntimeError(
            f"Unable to open the dashboard: {error}"
        ) from error

    pygame.display.set_caption("PWHL NEXUS")
    pygame.mouse.set_visible(False)

    screen_width, screen_height = screen.get_size()

    # Designed around the official 720 × 1280 portrait display.
    scale = min(
        screen_width / 720,
        screen_height / 1280,
    )

    outer_padding = scaled(42, scale)
    panel_gap = scaled(24, scale)
    panel_padding = scaled(24, scale)
    border_width = scaled(2, scale)
    corner_radius = scaled(16, scale)

    title_font = pygame.font.Font(None, scaled(72, scale))
    subtitle_font = pygame.font.Font(None, scaled(36, scale))
    status_font = pygame.font.Font(None, scaled(34, scale))
    section_font = pygame.font.Font(None, scaled(34, scale))
    body_font = pygame.font.Font(None, scaled(30, scale))
    small_font = pygame.font.Font(None, scaled(25, scale))
    footer_font = pygame.font.Font(None, scaled(25, scale))
    exit_font = pygame.font.Font(None, scaled(34, scale))

    title_surface = title_font.render(
        "PWHL NEXUS",
        True,
        WHITE,
    )

    subtitle_surface = subtitle_font.render(
        "LEAGUE COMMAND CENTER",
        True,
        NEON_PURPLE,
    )

    status_surface = status_font.render(
        "ON ICE",
        True,
        WHITE,
    )

    version_surface = footer_font.render(
        "v1.4.0 • FULLSCREEN FRAMEWORK",
        True,
        MUTED_TEXT,
    )

    exit_surface = exit_font.render("×", True, MUTED_TEXT)

    exit_rect = exit_surface.get_rect(
        topright=(
            screen_width - outer_padding,
            outer_padding,
        )
    )

    header_top = scaled(58, scale)
    status_y = scaled(235, scale)
    divider_y = scaled(300, scale)

    available_width = screen_width - (outer_padding * 2)

    game_center_rect = pygame.Rect(
        outer_padding,
        divider_y + panel_gap,
        available_width,
        scaled(240, scale),
    )

    team_hub_rect = pygame.Rect(
        outer_padding,
        game_center_rect.bottom + panel_gap,
        available_width,
        scaled(260, scale),
    )

    standings_rect = pygame.Rect(
            outer_padding,
            team_hub_rect.bottom + panel_gap,
            available_width,
            scaled(330, scale),
        )

    favorite = next(
        (
            team
            for team in standings
            if team.get("team") == FAVORITE_TEAM
        ),
        None,
    )

    team_info = TEAMS.get(FAVORITE_TEAM, {})
    display_name = team_info.get("display_name", FAVORITE_TEAM)
    abbr = team_info.get("abbr", "")

    clock = pygame.time.Clock()
    running = True

    while running:
            elapsed_seconds = pygame.time.get_ticks() / 1000
            pulse = (math.sin(elapsed_seconds * 2.8) + 1) / 2

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if exit_rect.collidepoint(event.pos):
                        running = False

            screen.fill(BLACK)

            # Header
            screen.blit(
                title_surface,
                (
                    outer_padding,
                    header_top,
                ),
            )

            screen.blit(
                subtitle_surface,
                (
                    outer_padding,
                    header_top + scaled(78, scale),
                ),
            )

            screen.blit(exit_surface, exit_rect)

            # ON ICE status
            status_dot_center = (
                outer_padding + scaled(11, scale),
                status_y,
            )

            draw_glowing_dot(
                screen,
                status_dot_center,
                scaled(8, scale),
                pulse,
            )

            screen.blit(
                status_surface,
                (
                    outer_padding + scaled(34, scale),
                    status_y - (status_surface.get_height() // 2),
                ),
            )

            # Purple divider
            pygame.draw.line(
                screen,
                NEON_PURPLE,
                (
                    outer_padding,
                    divider_y,
                ),
                (
                    screen_width - outer_padding,
                    divider_y,
                ),
                scaled(2, scale),
            )

            # Dashboard framework panels
            draw_panel(
                screen,
                game_center_rect,
                "GAME CENTER",
                section_font,
                border_width,
                corner_radius,
                panel_padding,
            )

            draw_panel(
                screen,
                team_hub_rect,
                "TEAM HUB",
                section_font,
                border_width,
                corner_radius,
                panel_padding,
            )
            team_text_x = team_hub_rect.left + panel_padding
    team_text_y = team_hub_rect.top + scaled(78, scale)

    name_surface = body_font.render(
        f"{display_name} ({abbr})",
        True,
        WHITE,
    )
    screen.blit(name_surface, (team_text_x, team_text_y))

    if favorite:
        record = (
            f"{favorite.get('wins', 0)}-"
            f"{favorite.get('losses', 0)}-"
            f"{favorite.get('otl', 0)}"
        )

        details = [
            "STATUS: PRESEASON",
            f"RECORD: {record}",
            f"POINTS: {favorite.get('points', 0)}",
        ]
    else:
        details = [
            "STATUS: WAITING FOR DATA",
            "RECORD: --",
            "POINTS: --",
        ]

    for index, line in enumerate(details):
        line_surface = small_font.render(
            line,
            True,
            MUTED_TEXT,
        )

        screen.blit(
            line_surface,
            (
                team_text_x,
                team_text_y
                + scaled(48, scale)
                + index * scaled(38, scale),
            ),
        )

        draw_panel(
                screen,
                standings_rect,
                "STANDINGS",
                section_font,
                border_width,
                corner_radius,
                panel_padding,
            )

            # Footer
        screen.blit(
                version_surface,
                (
                    outer_padding,
                    screen_height
                    - outer_padding
                    - version_surface.get_height(),
                ),
            )

        pygame.display.flip()
        clock.tick(60)

    pygame.mouse.set_visible(True)
    pygame.quit()
    sys.exit(0)