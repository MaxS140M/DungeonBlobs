"""The lobby: upgrade shop, run start and links to the other screens, all usable
with the mouse (keyboard shortcuts still work)."""
import pygame

from core.display import font, large_font, screen, small_font
from core.numbers import format_number
from core.settings import (
    ATTACK_UPGRADE_AMOUNT,
    BOSS_FLOOR_INTERVAL,
    COLORS,
    HEALTH_UPGRADE_AMOUNT,
    HEIGHT,
    PLAYER_VISUAL_TIER_STEP,
    PARTNER_ROLES,
    PLAYER_VISUAL_TIERS,
    REACH_UPGRADE_AMOUNT,
    REGEN_UPGRADE_AMOUNT,
    RELIC_YIELD_UPGRADE_AMOUNT,
    SPEED_UPGRADE_AMOUNT,
    WIDTH,
)
from game.entities import draw_player_blob, player_visual_tier_index
from progress.progression import (
    try_buy_attack,
    try_buy_health,
    try_buy_reach,
    try_buy_regen,
    try_buy_relic_yield,
    try_buy_speed,
)
from ui.buttons import Button
from ui.rendering import draw_menu_background, draw_text

UPGRADE_ROW_TOP = 192
UPGRADE_ROW_HEIGHT = 40
SHORTCUTS = {pygame.K_h: "guide", pygame.K_s: "settings", pygame.K_a: "accounts", pygame.K_l: "leaderboard", pygame.K_r: "rekindle", pygame.K_ESCAPE: "quit"}


# One row per upgrade: (name, buy function, current stat, gain per level, cost).
def upgrade_rows(progression):
    return [
        ("Vitality Charm", try_buy_health, f"Max HP {format_number(progression.max_health)}", f"+{HEALTH_UPGRADE_AMOUNT} HP", progression.health_upgrade_cost()),
        ("Whetstone", try_buy_attack, f"Attack {format_number(progression.attack_damage)}", f"+{ATTACK_UPGRADE_AMOUNT} dmg", progression.attack_upgrade_cost()),
        ("Fortune Idol", try_buy_relic_yield, f"Relic Yield x{format_number(progression.relic_yield)}", f"+{RELIC_YIELD_UPGRADE_AMOUNT} per pickup", progression.relic_yield_upgrade_cost()),
        ("Swift Boots", try_buy_speed, f"Move Speed {format_number(progression.move_speed)}", f"+{SPEED_UPGRADE_AMOUNT} speed", progression.speed_upgrade_cost()),
        ("Healing Herb", try_buy_regen, f"Floor Heal {progression.floor_heal_percent}%", f"+{REGEN_UPGRADE_AMOUNT}% HP per floor", progression.regen_upgrade_cost()),
        ("Long Blade", try_buy_reach, f"Swing Size {round(progression.attack_reach * 100)}%", f"+{REACH_UPGRADE_AMOUNT}% swing", progression.reach_upgrade_cost()),
    ]


class Lobby:
    # Creates the lobby's buttons for the given Accounts.
    def __init__(self, accounts):
        self.accounts = accounts
        self.use_checkpoint = True
        self.message = ""
        self.message_color = COLORS["muted"]
        self.message_timer = 0.0
        self.buy_buttons = [Button(660, UPGRADE_ROW_TOP - 7 + i * UPGRADE_ROW_HEIGHT, 170, 32) for i in range(6)]
        self.checkpoint_button = Button(60, 458, 330, 34)
        self.start_button = Button(60, 504, 260, 50, "START RUN")
        nav = [("guide", "How to Play"), ("settings", "Settings"), ("accounts", "Accounts"), ("leaderboard", "Leaderboard"), ("rekindle", "Rekindle"), ("quit", "Quit")]
        self.nav_buttons = {action: Button(40 + i * 148, 576, 136, 40, label) for i, (action, label) in enumerate(nav)}

    # The floor the next run starts on (after the checkpoint if it is switched on).
    def start_floor(self):
        return self.accounts.progression.checkpoint_floor + 1 if self.use_checkpoint else 1

    # Counts down how long the last purchase message stays on screen.
    def update(self, dt):
        self.message_timer = max(0.0, self.message_timer - dt)

    # Tries to buy upgrade number `index` and shows the result.
    def _buy(self, index):
        buy = upgrade_rows(self.accounts.progression)[index][1]
        purchased, self.message = buy(self.accounts.progression)
        if purchased:
            self.accounts.save()
        self.message_color = COLORS["exit"] if purchased else COLORS["danger"]
        self.message_timer = 2.4

    # Handles clicks and shortcuts. Returns "start", "quit", the name of a screen to open, or None.
    def handle_event(self, event):
        for index, button in enumerate(self.buy_buttons):
            if button.is_clicked(event):
                self._buy(index)
                return None
        if self.accounts.progression.checkpoint_floor and self.checkpoint_button.is_clicked(event):
            self.use_checkpoint = not self.use_checkpoint
        if self.start_button.is_clicked(event):
            return "start"
        for action, button in self.nav_buttons.items():
            if button.is_clicked(event):
                return action

        if event.type == pygame.KEYDOWN:
            if pygame.K_1 <= event.key < pygame.K_1 + len(self.buy_buttons):
                self._buy(event.key - pygame.K_1)
            elif event.key == pygame.K_c and self.accounts.progression.checkpoint_floor:
                self.use_checkpoint = not self.use_checkpoint
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                return "start"
            return SHORTCUTS.get(event.key)
        return None

    # Draws the lobby: currencies, upgrade shop, player preview, checkpoint option and buttons.
    def draw(self):
        progression = self.accounts.progression
        draw_menu_background()
        partner = PARTNER_ROLES[progression.partner]["name"] if progression.partner else "none"
        draw_text(f"Account: {self.accounts.active}    Partner: {partner}", (20, 16), COLORS["muted"], small_font)
        title_surface = large_font.render("THE LOBBY", True, COLORS["gold_light"])
        screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 70)))
        subtitle_surface = small_font.render("Spend relics on permanent upgrades. Enter the Dungeon and find all relics and kill all enemies.", True, COLORS["muted"])
        screen.blit(subtitle_surface, subtitle_surface.get_rect(center=(WIDTH // 2, 108)))

        draw_text(f"Relics available: {format_number(progression.relics)}", (60, 150), COLORS["gold"])
        draw_text(f"Diamonds: {format_number(progression.diamonds)}", (330, 150), COLORS["diamond"])
        if progression.embers:
            draw_text(f"Embers: {format_number(progression.embers)}", (560, 150), COLORS["danger"])
        self._draw_player_preview(progression)

        for index, (name, _, current, gain, cost) in enumerate(upgrade_rows(progression)):
            y = UPGRADE_ROW_TOP + index * UPGRADE_ROW_HEIGHT
            draw_text(name, (60, y), COLORS["text"])
            draw_text(current, (330, y), COLORS["muted"], small_font)
            draw_text(gain, (520, y), COLORS["muted"], small_font)
            self.buy_buttons[index].draw(enabled=progression.relics >= cost, label=f"Buy - {format_number(cost)}")

        if self.message_timer > 0:
            message_surface = font.render(self.message, True, self.message_color)
            screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, 436)))

        if progression.checkpoint_floor:
            where = "checkpoint" if self.use_checkpoint else "from the start"
            self.checkpoint_button.draw(label=f"Start floor: {self.start_floor()} ({where})")
            draw_text("Click to switch", (405, 468), COLORS["muted"], small_font)
        else:
            draw_text(f"Beat the boss on floor {BOSS_FLOOR_INTERVAL} to unlock a checkpoint.", (60, 468), COLORS["muted"], small_font)
        self.start_button.draw()
        for button in self.nav_buttons.values():
            button.draw()

    # Shows how the player blob currently looks and when its next look unlocks.
    def _draw_player_preview(self, progression):
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
