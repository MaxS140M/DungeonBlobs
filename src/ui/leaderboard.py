"""Leaderboard of every local account, ranked by highest floor or total relics."""
import pygame

from core.display import large_font, screen, small_font
from core.numbers import format_number
from core.settings import COLORS, WIDTH
from ui.buttons import Button, back_button
from ui.rendering import draw_menu_background, draw_text

# (tab label, sort key). Ties are broken by the other stat.
SORTS = [
    ("Highest Floor", lambda progression: (progression.best_floor, progression.total_relics_earned)),
    ("Total Relics", lambda progression: (progression.total_relics_earned, progression.best_floor)),
    ("Rekindles", lambda progression: (progression.rekindles, progression.best_floor)),
]
COLUMNS = {"rank": 80, "name": 140, "floor": 400, "relics": 580, "rekindles": 760}


class LeaderboardMenu:
    # Sets up the sort tabs and Back button for the given Accounts.
    def __init__(self, accounts):
        self.accounts = accounts
        self.sort_index = 0
        self.back_button = back_button()
        self.tabs = [Button(WIDTH // 2 - 320 + i * 220, 115, 200, 38, label) for i, (label, _) in enumerate(SORTS)]

    # Nothing to reset when the leaderboard opens.
    def open(self):
        pass

    # Clicking a tab (or LEFT/RIGHT) changes the ranking. Returns True to go back.
    def handle_event(self, event):
        if self.back_button.is_clicked(event):
            return True
        for index, tab in enumerate(self.tabs):
            if tab.is_clicked(event):
                self.sort_index = index
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return True
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d, pygame.K_TAB):
                self.sort_index = (self.sort_index + 1) % len(SORTS)
        return False

    # Draws the ranked table, highlighting the account currently being played.
    def draw(self):
        draw_menu_background()
        title_surface = large_font.render("LEADERBOARD", True, COLORS["gold_light"])
        screen.blit(title_surface, title_surface.get_rect(center=(WIDTH // 2, 70)))
        self.back_button.draw()
        for index, tab in enumerate(self.tabs):
            tab.draw(selected=index == self.sort_index)

        header_y = 180
        for column, label in (("rank", "#"), ("name", "Account"), ("floor", "Highest Floor"), ("relics", "Total Relics"), ("rekindles", "Rekindles")):
            draw_text(label, (COLUMNS[column], header_y), COLORS["muted"])
        pygame.draw.line(screen, COLORS["wall_edge"], (60, header_y + 26), (WIDTH - 60, header_y + 26), 2)

        sort_key = SORTS[self.sort_index][1]
        ranked = sorted(self.accounts.profiles.items(), key=lambda item: sort_key(item[1]), reverse=True)
        y = header_y + 42
        for rank, (name, progression) in enumerate(ranked, start=1):
            is_active = name == self.accounts.active
            if is_active:
                pygame.draw.rect(screen, (30, 33, 48), (60, y - 8, WIDTH - 120, 36), border_radius=6)
            color = COLORS["gold_light"] if rank == 1 else COLORS["text"]
            draw_text(str(rank), (COLUMNS["rank"], y), color)
            draw_text(f"{name} (you)" if is_active else name, (COLUMNS["name"], y), color)
            draw_text(str(progression.best_floor), (COLUMNS["floor"], y), COLORS["text"])
            draw_text(format_number(progression.total_relics_earned), (COLUMNS["relics"], y), COLORS["gold"])
            draw_text(str(progression.rekindles), (COLUMNS["rekindles"], y), COLORS["danger"])
            y += 44

        draw_text("Stats update when a run ends. Click a tab or press LEFT / RIGHT to change the ranking.", (60, 600), COLORS["muted"], small_font)
