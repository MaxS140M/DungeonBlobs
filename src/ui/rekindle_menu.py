"""The Rekindle screen: reset this cycle for Embers (choosing a partner blob for the
next cycle), and spend diamonds on Heirlooms."""
import pygame

from core.display import font, large_font, screen, small_font
from core.numbers import format_number
from core.settings import (
    COLORS,
    EMBER_BONUS_PERCENT,
    HEIGHT,
    HEIRLOOMS,
    PARTNER_ROLES,
    PARTNER_UNLOCK_EVERY,
    REKINDLE_UNLOCK_FLOOR,
    WIDTH,
)
from progress.rekindle import (
    can_rekindle,
    embers_for_floor,
    heirloom_cost,
    heirloom_maxed,
    next_ember_floor,
    partner_unlock_rekindles,
    rekindle,
    try_buy_heirloom,
    unlocked_partners,
)
from ui.buttons import Button, back_button
from ui.rendering import draw_menu_background, draw_text, draw_wrapped

HEIRLOOM_ROW_TOP = 282
HEIRLOOM_ROW_HEIGHT = 33
PANEL = pygame.Rect(130, 105, 700, 430)  # the rekindle confirm panel
NO_PARTNER = None


class RekindleMenu:
    # Sets up the Rekindle button, heirloom Buy buttons and Back button.
    def __init__(self, accounts):
        self.accounts = accounts
        self.back_button = back_button()
        self.rekindle_button = Button(WIDTH // 2 - 160, 172, 320, 40)
        self.heirloom_buttons = {key: Button(670, HEIRLOOM_ROW_TOP - 5 + i * HEIRLOOM_ROW_HEIGHT, 230, 29) for i, key in enumerate(HEIRLOOMS)}
        choices = [*PARTNER_ROLES, NO_PARTNER]
        self.partner_buttons = {role: Button(PANEL.x + 24 + i * 132, 262, 124, 38) for i, role in enumerate(choices)}
        self.confirm_button = Button(WIDTH // 2 - 190, 462, 180, 46, "Rekindle!")
        self.cancel_button = Button(WIDTH // 2 + 10, 462, 180, 46, "Cancel")
        self.open()

    # Resets the confirm panel and message each time the screen opens.
    def open(self):
        self.confirming = False
        self.partner_choice = NO_PARTNER
        self.message = ""
        self.message_color = COLORS["muted"]

    # Partner roles that will be unlocked once this rekindle happens.
    def _choosable_partners(self):
        return unlocked_partners(self.accounts.progression.rekindles + 1)

    # Opens the confirm panel, pre-selecting the current partner (or the newest unlocked one).
    def _open_confirm_panel(self):
        choosable = self._choosable_partners()
        current = self.accounts.progression.partner
        self.partner_choice = current if current in choosable else (choosable[-1] if choosable else NO_PARTNER)
        self.confirming = True

    # Handles Back, opening the confirm panel and heirloom purchases. Returns True to go back.
    def handle_event(self, event):
        if self.confirming:
            self._handle_confirm_panel(event)
            return False
        progression = self.accounts.progression
        if self.back_button.is_clicked(event) or (event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE)):
            return True
        if can_rekindle(progression) and self.rekindle_button.is_clicked(event):
            self._open_confirm_panel()
            return False
        for key, button in self.heirloom_buttons.items():
            if button.is_clicked(event):
                ok, message = try_buy_heirloom(progression, key)
                if ok:
                    self.accounts.save()
                self._say(ok, message)
        return False

    # Confirm panel: pick a partner, then Rekindle! or Cancel (ENTER / ESC also work).
    def _handle_confirm_panel(self, event):
        for role, button in self.partner_buttons.items():
            if button.is_clicked(event) and (role is NO_PARTNER or role in self._choosable_partners()):
                self.partner_choice = role
        pressed = event.key if event.type == pygame.KEYDOWN else None
        if self.cancel_button.is_clicked(event) or pressed == pygame.K_ESCAPE:
            self.confirming = False
        elif self.confirm_button.is_clicked(event) or pressed == pygame.K_RETURN:
            progression = self.accounts.progression
            gained = rekindle(progression, self.partner_choice)
            self.accounts.save()
            self.confirming = False
            partner = PARTNER_ROLES[progression.partner]["name"] if progression.partner else "none"
            self._say(True, f"The lantern burns brighter! +{format_number(gained)} Embers. Partner: {partner}.")

    # Shows a green (success) or red (error) message.
    def _say(self, ok, message):
        self.message = message
        self.message_color = COLORS["exit"] if ok else COLORS["danger"]

    # Draws Ember totals, the rekindle preview/button and the heirloom shop.
    def draw(self):
        progression = self.accounts.progression
        draw_menu_background()
        self.back_button.draw()
        title_surface = large_font.render("REKINDLE", True, COLORS["gold_light"])
        screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 45)))
        subtitle = small_font.render("Reset your relics, upgrades and checkpoint to gain Embers. Diamonds and Heirlooms are kept.", True, COLORS["muted"])
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 80)))

        draw_text(f"Embers: {format_number(progression.embers)}  (+{format_number(progression.ember_bonus_percent)}% damage and relics)", (60, 104), COLORS["danger"])
        draw_text(f"Diamonds: {format_number(progression.diamonds)}", (700, 104), COLORS["diamond"])

        best = progression.cycle_best_floor
        if can_rekindle(progression):
            preview = f"Best floor this cycle: {best}  -  rekindle now for {format_number(embers_for_floor(best))} Embers  (more at floor {next_ember_floor(best)})"
            label, enabled = "REKINDLE", True
        else:
            preview = f"Beat the boss on floor {REKINDLE_UNLOCK_FLOOR} to rekindle  (your checkpoint: floor {progression.checkpoint_floor})"
            label, enabled = "Locked", False
        preview_surface = font.render(preview, True, COLORS["text"])
        screen.blit(preview_surface, preview_surface.get_rect(center=(WIDTH // 2, 150)))
        self.rekindle_button.draw(enabled=enabled, label=label)
        draw_text(f"Each Ember: +{EMBER_BONUS_PERCENT}% damage and relics. Rekindled {progression.rekindles} times.", (60, 222), COLORS["muted"], small_font)

        draw_text("HEIRLOOMS  (bought with diamonds, never reset)", (60, HEIRLOOM_ROW_TOP - 32), COLORS["gold_light"])
        for index, (key, heirloom) in enumerate(HEIRLOOMS.items()):
            y = HEIRLOOM_ROW_TOP + index * HEIRLOOM_ROW_HEIGHT
            level = progression.heirlooms[key]
            draw_text(heirloom["name"], (60, y), COLORS["text"])
            draw_text(f"Lv {level}", (230, y + 2), COLORS["muted"], small_font)
            draw_text(heirloom["effect"].format(progression.heirloom_bonus(key)), (290, y + 2), COLORS["muted"], small_font)
            button = self.heirloom_buttons[key]
            if heirloom_maxed(progression, key):
                button.draw(enabled=False, label="MAX")
            else:
                cost = heirloom_cost(progression, key)
                button.draw(enabled=progression.diamonds >= cost, label=f"Buy - {format_number(cost)} diamonds")

        if self.message:
            message_surface = font.render(self.message, True, self.message_color)
            screen.blit(message_surface, message_surface.get_rect(center=(WIDTH // 2, 588)))
        draw_text("ESC back.", (60, 616), COLORS["muted"], small_font)
        if self.confirming:
            self._draw_confirm_panel()

    # Draws the confirm panel over the screen: Ember gain, partner choice, Rekindle!/Cancel.
    def _draw_confirm_panel(self):
        progression = self.accounts.progression
        veil = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        veil.fill((5, 7, 14, 215))
        screen.blit(veil, (0, 0))
        pygame.draw.rect(screen, (22, 25, 38), PANEL, border_radius=10)
        pygame.draw.rect(screen, COLORS["gold_light"], PANEL, 2, border_radius=10)

        title_surface = large_font.render("REKINDLE?", True, COLORS["gold_light"])
        screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 150)))
        gain = embers_for_floor(progression.cycle_best_floor)
        summary = font.render(f"+{format_number(gain)} Embers. Your relics, upgrades and checkpoint will reset.", True, COLORS["text"])
        screen.blit(summary, summary.get_rect(center=(WIDTH // 2, 200)))
        draw_text("Partner for the next cycle:", (PANEL.x + 24, 234), COLORS["gold_light"])

        choosable = self._choosable_partners()
        for role, button in self.partner_buttons.items():
            name = "No partner" if role is NO_PARTNER else PARTNER_ROLES[role]["name"]
            available = role is NO_PARTNER or role in choosable
            button.draw(enabled=available, selected=role == self.partner_choice, label=name if available else "Locked")

        if self.partner_choice is NO_PARTNER:
            description = "Go it alone this cycle."
        else:
            description = PARTNER_ROLES[self.partner_choice]["description"]
        y = draw_wrapped(description, PANEL.x + 24, 318, PANEL.width - 48, COLORS["text"])
        locked = [role for role in PARTNER_ROLES if role not in choosable]
        if locked:
            next_name = PARTNER_ROLES[locked[0]]["name"]
            hint = (f"A new partner unlocks every {PARTNER_UNLOCK_EVERY} rekindles. Next: {next_name} "
                    f"at {partner_unlock_rekindles(locked[0])} rekindles (this will be rekindle {progression.rekindles + 1}).")
            draw_wrapped(hint, PANEL.x + 24, max(y, 370), PANEL.width - 48, COLORS["muted"], small_font)
        self.confirm_button.draw()
        self.cancel_button.draw()
