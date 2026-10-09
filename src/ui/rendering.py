"""Drawing/rendering functions for the dungeon, HUD, menus, and overlays."""
import math

import pygame

from game import dungeon
from core.assets import load_image
from core.display import font, large_font, screen, small_font
from core.numbers import format_number
from core.settings import COLORS, HEIGHT, MENU_BACKGROUND_DIM, MENU_BACKGROUND_IMAGE, TILE_IMAGES, WIDTH

_menu_background = None  # built on first use: the background image with the darkening baked in


# Draws a line of text with its top-left corner at position.
def draw_text(text, position, color=COLORS["text"], selected_font=font):
    screen.blit(selected_font.render(text, True, color), position)


# Draws text word-wrapped to `width` pixels from (x, y); "\n" starts a new paragraph.
# Returns the y position just below the last line.
def draw_wrapped(text, x, y, width, color=COLORS["text"], selected_font=font, paragraph_gap=8):
    line_height = selected_font.get_linesize() + 2
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split(" "):
            candidate = f"{line} {word}".strip()
            if line and selected_font.size(candidate)[0] > width:
                draw_text(line, (x, y), color, selected_font)
                y += line_height
                line = word
            else:
                line = candidate
        if line:
            draw_text(line, (x, y), color, selected_font)
            y += line_height
        y += paragraph_gap
    return y


# Fills the screen behind the lobby and menus: the darkened background image if
# Assets has one, otherwise the plain background colour.
def draw_menu_background():
    global _menu_background
    if _menu_background is None:
        image = load_image(MENU_BACKGROUND_IMAGE)
        if image is None:
            _menu_background = False  # no image; don't try loading again every frame
        else:
            _menu_background = pygame.transform.smoothscale(image, (WIDTH, HEIGHT))
            veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            veil.fill((*COLORS["background"], MENU_BACKGROUND_DIM))
            _menu_background.blit(veil, (0, 0))
    if _menu_background:
        screen.blit(_menu_background, (0, 0))
    else:
        screen.fill(COLORS["background"])


# Draws the walls and checkerboard floor of the current map, using the tile images
# from Assets where they exist and plain coloured squares where they don't.
def draw_dungeon():
    screen.fill(COLORS["background"])
    wall_image = load_image(TILE_IMAGES["wall"])
    floor_images = (load_image(TILE_IMAGES["floor"]), load_image(TILE_IMAGES["floor_alt"]))
    for y, row in enumerate(dungeon.CURRENT_DUNGEON):
        for x, tile in enumerate(row):
            rect = dungeon.tile_rect(x, y)
            if tile == "#":
                if wall_image:
                    screen.blit(wall_image, rect)
                else:
                    pygame.draw.rect(screen, COLORS["wall"], rect)
                    pygame.draw.line(screen, COLORS["wall_edge"], rect.topleft, rect.topright, 2)
            else:
                checker = (x + y) % 2
                if floor_images[checker]:
                    screen.blit(floor_images[checker], rect)
                else:
                    pygame.draw.rect(screen, COLORS["floor_alt"] if checker else COLORS["floor"], rect)
                    pygame.draw.line(screen, (50, 53, 70), rect.bottomleft, rect.bottomright, 1)


# Draws the bottom bar: floor, relics, diamonds and the HP bar.
def draw_hud(player, run_relics, run_diamonds, floor):
    pygame.draw.rect(screen, (14, 16, 27), (0, HEIGHT - 62, WIDTH, 62))
    pygame.draw.line(screen, COLORS["wall_edge"], (0, HEIGHT - 62), (WIDTH, HEIGHT - 62), 2)
    draw_text("LANTERN VAULT", (22, HEIGHT - 49), COLORS["gold_light"])
    draw_text(f"FLOOR {floor}", (230, HEIGHT - 49), COLORS["gold_light"])
    draw_text(f"RELICS {format_number(run_relics)}", (340, HEIGHT - 49), COLORS["gold"])
    draw_text(f"DIAMONDS {format_number(run_diamonds)}", (470, HEIGHT - 49), COLORS["diamond"])
    draw_text("SPACE attack", (610, HEIGHT - 47), COLORS["muted"], small_font)

    bar_x, bar_y, bar_w, bar_h = 700, HEIGHT - 42, 220, 16
    draw_text(f"HP {format_number(max(0, player.health))}/{format_number(player.max_health)}", (bar_x, HEIGHT - 58), COLORS["text"], small_font)
    pygame.draw.rect(screen, (62, 43, 53), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    ratio = max(0, player.health) / player.max_health if player.max_health else 0
    pygame.draw.rect(screen, COLORS["danger"], (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
    pygame.draw.rect(screen, COLORS["wall_edge"], (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)


# Draws a relic pickup.
def draw_relic(rect):
    center = rect.center
    pygame.draw.circle(screen, (91, 64, 44), center, 16)
    pygame.draw.circle(screen, COLORS["gold"], center, 11)
    pygame.draw.polygon(screen, COLORS["gold_light"], [(center[0], center[1] - 9), (center[0] + 7, center[1]), (center[0], center[1] + 9), (center[0] - 7, center[1])])


# Draws a diamond pickup with a pulsing glow.
def draw_diamond(rect):
    cx, cy = rect.center
    glow = 13 + int(2 * math.sin(pygame.time.get_ticks() / 200))
    pygame.draw.circle(screen, (34, 70, 92), (cx, cy), glow)
    pygame.draw.polygon(screen, COLORS["diamond"], [(cx, cy - 12), (cx + 10, cy - 3), (cx, cy + 12), (cx - 10, cy - 3)])
    pygame.draw.polygon(screen, COLORS["diamond_light"], [(cx, cy - 12), (cx + 10, cy - 3), (cx, cy - 1), (cx - 10, cy - 3)])


# Draws the boss name and health bar at the top of the screen.
def draw_boss_bar(boss):
    bar_w, bar_h = 420, 14
    bar_x, bar_y = (WIDTH - bar_w) // 2, 30
    name_surface = small_font.render(boss.name.upper(), True, COLORS["danger"])
    screen.blit(name_surface, name_surface.get_rect(midbottom=(WIDTH // 2, bar_y - 3)))
    pygame.draw.rect(screen, (40, 20, 24), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    ratio = max(0, boss.health) / boss.max_health
    pygame.draw.rect(screen, COLORS["danger"], (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
    pygame.draw.rect(screen, COLORS["wall_edge"], (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)


# Draws a short message (e.g. boss rewards) near the top of the screen.
def draw_toast(text):
    surface = font.render(text, True, COLORS["gold_light"])
    backdrop = pygame.Rect(0, 0, surface.get_width() + 30, surface.get_height() + 14)
    backdrop.center = (WIDTH // 2, 175)
    veil = pygame.Surface(backdrop.size, pygame.SRCALPHA)
    veil.fill((5, 7, 14, 190))
    screen.blit(veil, backdrop)
    screen.blit(surface, surface.get_rect(center=backdrop.center))


# Draws the FLOOR n banner shown when entering a floor (red on boss floors).
def draw_floor_banner(floor, dungeon_name, boss_floor=False):
    title = f"BOSS - FLOOR {floor}" if boss_floor else f"FLOOR {floor}"
    text_surface = large_font.render(title, True, COLORS["danger"] if boss_floor else COLORS["gold_light"])
    name_surface = small_font.render(dungeon_name, True, COLORS["muted"])
    width = max(text_surface.get_width(), name_surface.get_width()) + 40
    height = text_surface.get_height() + name_surface.get_height() + 16
    backdrop = pygame.Surface((width, height), pygame.SRCALPHA)
    backdrop.fill((5, 7, 14, 160))
    backdrop_rect = backdrop.get_rect(center=(WIDTH // 2, 100))
    screen.blit(backdrop, backdrop_rect)
    screen.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, backdrop_rect.top + text_surface.get_height() // 2 + 6)))
    screen.blit(name_surface, name_surface.get_rect(center=(WIDTH // 2, backdrop_rect.bottom - name_surface.get_height() // 2 - 6)))


# Darkens the screen and shows a title, subtitle and prompt (e.g. the death screen).
def overlay(title, subtitle, accent, prompt="Press ENTER to continue"):
    veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    veil.fill((5, 7, 14, 205))
    screen.blit(veil, (0, 0))
    title_surface = large_font.render(title, True, accent)
    screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 255)))
    message = font.render(subtitle, True, COLORS["text"])
    screen.blit(message, message.get_rect(center=(WIDTH // 2, 320)))
    prompt_surface = small_font.render(prompt, True, COLORS["muted"])
    screen.blit(prompt_surface, prompt_surface.get_rect(center=(WIDTH // 2, 365)))


# The clickable area of row `index` on a menu screen.
def menu_row_rect(index):
    return pygame.Rect(40, 142 + index * 44, WIDTH - 80, 36)


# Shared layout for the settings and account screens. rows: (label, detail) pairs.
def draw_menu_screen(title, rows, selected, footer, message="", message_color=COLORS["muted"]):
    draw_menu_background()
    title_surface = large_font.render(title, True, COLORS["gold_light"])
    screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 70)))
    for index, (label, detail) in enumerate(rows):
        row = menu_row_rect(index)
        is_selected = index == selected
        if is_selected:
            pygame.draw.rect(screen, (30, 33, 48), row, border_radius=6)
        draw_text(("> " if is_selected else "  ") + label, (60, row.y + 8), COLORS["gold_light"] if is_selected else COLORS["text"])
        draw_text(detail, (380, row.y + 10), COLORS["muted"], small_font)
    if message:
        message_surface = font.render(message, True, message_color)
        screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, HEIGHT - 90)))
    draw_text(footer, (60, HEIGHT - 40), COLORS["muted"], small_font)
