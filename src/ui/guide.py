"""How to Play: a tabbed guide explaining every system. The text is built from
core.settings, so it stays correct when numbers are rebalanced."""
import pygame

from core.display import large_font, screen, small_font
from core.settings import (
    ATTACK_UPGRADE_AMOUNT,
    BOSS_FLOOR_INTERVAL,
    COLORS,
    DIAMOND_FLOOR_INTERVAL,
    EMBER_BONUS_PERCENT,
    EMBER_DIVISOR,
    EMBER_FLOOR_OFFSET,
    HEALTH_UPGRADE_AMOUNT,
    HEIRLOOMS,
    PARTNER_ROLES,
    PARTNER_UNLOCK_EVERY,
    REACH_UPGRADE_AMOUNT,
    REGEN_UPGRADE_AMOUNT,
    REKINDLE_UNLOCK_FLOOR,
    RELIC_YIELD_UPGRADE_AMOUNT,
    SPEED_UPGRADE_AMOUNT,
    UPGRADE_COST_GROWTH,
    WIDTH,
)
from ui.buttons import Button, back_button
from ui.rendering import draw_menu_background, draw_wrapped


# Builds the (tab name, text) pages. "\n" separates paragraphs.
def guide_pages():
    heirloom_lines = "\n".join(
        f"{heirloom['name']}: level 1 = {heirloom['effect'].format(heirloom['per_level'])}"
        + ("" if heirloom["max_level"] is None else f" (max level {heirloom['max_level']})")
        for heirloom in HEIRLOOMS.values()
    )
    partner_lines = "\n".join(
        f"{role['name']} (unlocks at {(index + 1) * PARTNER_UNLOCK_EVERY} rekindles): {role['description']}"
        for index, role in enumerate(PARTNER_ROLES.values())
    )
    growth = round((UPGRADE_COST_GROWTH - 1) * 100)
    return [
        ("Basics", (
            "Move with WASD. Attack with SPACE or the left mouse button - your sword swings in the direction you last moved.\n"
            "Each floor is a room full of blobs. Defeat every enemy to drop to the next floor. Grab the gold relics "
            "(and any diamonds) before you finish the last enemy, or they are left behind.\n"
            "Your health does NOT refill between floors, so the run gets harder the deeper you go. When you fall, "
            "every relic and diamond you collected is banked and you return to the lobby.\n"
            "Want to stop early? Click Leave (top right) or press ESC during a run. Leaving counts the same as "
            "falling: everything you collected that run is banked."
        )),
        ("Upgrades", (
            "Spend relics in the lobby on permanent upgrades. Click Buy, or press 1-6.\n"
            f"Vitality Charm: +{HEALTH_UPGRADE_AMOUNT} max HP.\n"
            f"Whetstone: +{ATTACK_UPGRADE_AMOUNT} attack damage. Every 10 levels your blob gets a new look.\n"
            f"Fortune Idol: +{RELIC_YIELD_UPGRADE_AMOUNT} relic per pickup.\n"
            f"Swift Boots: +{SPEED_UPGRADE_AMOUNT} move speed.\n"
            f"Healing Herb: heal +{REGEN_UPGRADE_AMOUNT}% of your max HP every time you clear a floor.\n"
            f"Long Blade: +{REACH_UPGRADE_AMOUNT}% bigger sword swing.\n"
            f"Each level costs {growth}% more than the last."
        )),
        ("Bosses", (
            f"Every {BOSS_FLOOR_INTERVAL}th floor is a boss floor. The boss chases you and, every few seconds, "
            "flashes before charging in a straight line - move out of the way when it flashes!\n"
            "Beating a boss gives a big pile of relics and saves a checkpoint. In the lobby, the Start floor "
            "button lets you begin your next run on the floor after your checkpoint (or from floor 1).\n"
            f"Diamonds: one rare diamond appears every {DIAMOND_FLOOR_INTERVAL} floors. Diamonds buy Heirlooms."
        )),
        ("Rekindle", (
            f"Once you have beaten the floor {REKINDLE_UNLOCK_FLOOR} boss you can Rekindle from the lobby.\n"
            "Rekindling resets your relics, relic upgrades and checkpoint. In return you get Embers based on the "
            f"deepest floor you reached this cycle: (floor - {EMBER_FLOOR_OFFSET}) squared, divided by {EMBER_DIVISOR}. "
            "Pushing a few floors deeper before rekindling gives many more Embers.\n"
            f"Each Ember permanently gives +{EMBER_BONUS_PERCENT}% damage and +{EMBER_BONUS_PERCENT}% relics, so every "
            "cycle you climb faster and further.\n"
            "Kept forever: diamonds, Embers, Heirlooms and your leaderboard stats."
        )),
        ("Heirlooms", (
            "Heirlooms are bought with diamonds on the Rekindle screen and are never reset. "
            "Each extra level adds the same amount again.\n" + heirloom_lines
        )),
        ("Partners", (
            f"Every {PARTNER_UNLOCK_EVERY} rekindles a new partner blob unlocks. When you rekindle, choose which "
            "partner joins you for the next cycle (or none).\n"
            "Partners are spirits: they float over walls, keep up with you and can't be hurt.\n" + partner_lines
        )),
        ("Menus", (
            "Accounts: each account has its own progress. Create one with N, click one to play as it.\n"
            "Leaderboard: compares your accounts by highest floor, total relics earned and rekindles.\n"
            "Settings: change the window size, music volume and sound effects volume.\n"
            "Lobby shortcuts: ENTER start, 1-6 buy, C checkpoint, H guide, S settings, A accounts, L leaderboard, R rekindle."
        )),
    ]


class GuideMenu:
    # Creates one tab button per guide page plus a Back button.
    def __init__(self):
        self.back_button = back_button()
        self.page = 0
        tab_width, gap = 118, 8
        left = (WIDTH - (len(guide_pages()) * (tab_width + gap) - gap)) // 2
        self.tabs = [Button(left + i * (tab_width + gap), 100, tab_width, 36, name) for i, (name, _) in enumerate(guide_pages())]

    # Nothing to reset when the guide opens; it remembers the last page read.
    def open(self):
        pass

    # Tabs (or LEFT/RIGHT) change page. Returns True to go back.
    def handle_event(self, event):
        if self.back_button.is_clicked(event):
            return True
        for index, tab in enumerate(self.tabs):
            if tab.is_clicked(event):
                self.page = index
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return True
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.page = (self.page - 1) % len(self.tabs)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.page = (self.page + 1) % len(self.tabs)
        return False

    # Draws the tabs and the current page's text.
    def draw(self):
        draw_menu_background()
        self.back_button.draw()
        title_surface = large_font.render("HOW TO PLAY", True, COLORS["gold_light"])
        screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 55)))
        for index, tab in enumerate(self.tabs):
            tab.draw(selected=index == self.page)
        name, text = guide_pages()[self.page]
        pygame.draw.rect(screen, (22, 25, 38), (40, 150, WIDTH - 80, 440), border_radius=10)
        draw_wrapped(text, 64, 170, WIDTH - 128)
        hint = small_font.render(f"Page {self.page + 1} of {len(self.tabs)}  -  click a tab or press LEFT / RIGHT  -  ESC back", True, COLORS["muted"])
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, 612)))
