"""Drawing/rendering functions for the dungeon, HUD, lobby, and overlays."""
import pygame

import dungeon
from display import font, large_font, screen, small_font
from entities import draw_player_blob, player_visual_tier_index
from settings import (
    ATTACK_UPGRADE_AMOUNT,
    COLORS,
    HEALTH_UPGRADE_AMOUNT,
    HEIGHT,
    PLAYER_VISUAL_TIER_STEP,
    PLAYER_VISUAL_TIERS,
    RELIC_YIELD_UPGRADE_AMOUNT,
    SPEED_UPGRADE_AMOUNT,
    WIDTH,
)


def draw_text(text, position, color=COLORS["text"], selected_font=font):
    screen.blit(selected_font.render(text, True, color), position)


def draw_dungeon():
    screen.fill(COLORS["background"])
    for y, row in enumerate(dungeon.CURRENT_DUNGEON):
        for x, tile in enumerate(row):
            rect = dungeon.tile_rect(x, y)
            if tile == "#":
                pygame.draw.rect(screen, COLORS["wall"], rect)
                pygame.draw.line(screen, COLORS["wall_edge"], rect.topleft, rect.topright, 2)
            else:
                floor_color = COLORS["floor_alt"] if (x + y) % 2 else COLORS["floor"]
                pygame.draw.rect(screen, floor_color, rect)
                pygame.draw.line(screen, (50, 53, 70), rect.bottomleft, rect.bottomright, 1)


def draw_hud(player, run_relics, floor):
    pygame.draw.rect(screen, (14, 16, 27), (0, HEIGHT - 62, WIDTH, 62))
    pygame.draw.line(screen, COLORS["wall_edge"], (0, HEIGHT - 62), (WIDTH, HEIGHT - 62), 2)
    draw_text("LANTERN VAULT", (22, HEIGHT - 49), COLORS["gold_light"])
    draw_text(f"FLOOR {floor}", (230, HEIGHT - 49), COLORS["gold_light"])
    draw_text(f"RELICS {run_relics}", (340, HEIGHT - 49), COLORS["gold"])
    draw_text("SPACE / Click attack", (470, HEIGHT - 49), COLORS["muted"], small_font)

    bar_x, bar_y, bar_w, bar_h = 700, HEIGHT - 42, 220, 16
    draw_text(f"HP {max(0, player.health)}/{player.max_health}", (bar_x, HEIGHT - 58), COLORS["text"], small_font)
    pygame.draw.rect(screen, (62, 43, 53), (bar_x, bar_y, bar_w, bar_h), border_radius=4)
    ratio = max(0, player.health) / player.max_health if player.max_health else 0
    pygame.draw.rect(screen, COLORS["danger"], (bar_x, bar_y, int(bar_w * ratio), bar_h), border_radius=4)
    pygame.draw.rect(screen, COLORS["wall_edge"], (bar_x, bar_y, bar_w, bar_h), 2, border_radius=4)


def draw_relic(rect):
    center = rect.center
    pygame.draw.circle(screen, (91, 64, 44), center, 16)
    pygame.draw.circle(screen, COLORS["gold"], center, 11)
    pygame.draw.polygon(screen, COLORS["gold_light"], [(center[0], center[1] - 9), (center[0] + 7, center[1]), (center[0], center[1] + 9), (center[0] - 7, center[1])])


def draw_floor_banner(floor, dungeon_name):
    text_surface = large_font.render(f"FLOOR {floor}", True, COLORS["gold_light"])
    name_surface = small_font.render(dungeon_name, True, COLORS["muted"])
    width = max(text_surface.get_width(), name_surface.get_width()) + 40
    height = text_surface.get_height() + name_surface.get_height() + 16
    backdrop = pygame.Surface((width, height), pygame.SRCALPHA)
    backdrop.fill((5, 7, 14, 160))
    backdrop_rect = backdrop.get_rect(center=(WIDTH // 2, 100))
    screen.blit(backdrop, backdrop_rect)
    screen.blit(text_surface, text_surface.get_rect(center=(WIDTH // 2, backdrop_rect.top + text_surface.get_height() // 2 + 6)))
    screen.blit(name_surface, name_surface.get_rect(center=(WIDTH // 2, backdrop_rect.bottom - name_surface.get_height() // 2 - 6)))


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


def draw_lobby(progression, message, message_color):
    screen.fill(COLORS["background"])
    title_surface = large_font.render("THE LOBBY", True, COLORS["gold_light"])
    screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 70)))
    subtitle_surface = small_font.render("Spend relics on permanent upgrades. Enter the Dungeon and find all relics and kill all enemies.", True, COLORS["muted"])
    screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(WIDTH // 2, 108)))

    draw_text(f"Relics available: {progression.relics}", (60, 150), COLORS["gold"])

    preview_center = (900, 165)
    preview_rect = pygame.Rect(0, 0, 44, 44)
    preview_rect.center = preview_center
    tier_index = player_visual_tier_index(progression.attack_level)
    tier = PLAYER_VISUAL_TIERS[tier_index]
    draw_player_blob(screen, preview_rect, tier, time_now=pygame.time.get_ticks() / 1000.0)
    tier_label_surface = small_font.render(tier["name"], True, COLORS["gold_light"])
    screen.blit(tier_label_surface, tier_label_surface.get_rect(center=(preview_center[0], preview_center[1] + 40)))
    if tier_index < len(PLAYER_VISUAL_TIERS) - 1:
        next_level = (tier_index + 1) * PLAYER_VISUAL_TIER_STEP
        hint_surface = small_font.render(f"Next look: Lv {next_level}", True, COLORS["muted"])
        screen.blit(hint_surface, hint_surface.get_rect(center=(preview_center[0], preview_center[1] + 58)))

    rows = [
        ("1", "Vitality Charm", f"Max HP {progression.max_health}", f"+{HEALTH_UPGRADE_AMOUNT} HP", progression.health_upgrade_cost()),
        ("2", "Whetstone", f"Attack {progression.attack_damage}", f"+{ATTACK_UPGRADE_AMOUNT} dmg", progression.attack_upgrade_cost()),
        ("3", "Fortune Idol", f"Relic Yield x{progression.relic_yield}", f"+{RELIC_YIELD_UPGRADE_AMOUNT} per pickup", progression.relic_yield_upgrade_cost()),
        ("4", "Swift Boots", f"Move Speed {progression.move_speed}", f"+{SPEED_UPGRADE_AMOUNT} speed", progression.speed_upgrade_cost()),
    ]
    y = 200
    for key, name, current, gain, cost in rows:
        draw_text(f"[{key}] {name}", (60, y), COLORS["text"])
        draw_text(current, (330, y), COLORS["muted"], small_font)
        draw_text(gain, (520, y), COLORS["muted"], small_font)
        draw_text(f"Cost: {cost} relics", (700, y), COLORS["gold_light"], small_font)
        y += 46

    if message:
        message_surface = font.render(message, True, message_color)
        screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, y + 30)))

    draw_text("Upgrades are permanent and carry into every future run.", (60, HEIGHT - 90), COLORS["muted"], small_font)
    draw_text("Press ENTER or SPACE to start a run.", (60, HEIGHT - 60), COLORS["gold_light"])
    draw_text("Press ESC to quit.", (60, HEIGHT - 34), COLORS["muted"], small_font)
