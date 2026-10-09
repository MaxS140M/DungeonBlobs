"""Settings and account screens. While open, each menu receives every event via
handle_event, which returns True when the player backs out to the lobby."""
import pygame

from core import audio, display
from core.numbers import format_number
from core.settings import COLORS, PROFILE_NAME_MAX_LENGTH, VOLUME_STEP, WINDOW_SIZES
from progress.user_settings import load_user_settings, save_user_settings
from ui.buttons import Button, back_button
from ui.rendering import draw_menu_screen, menu_row_rect

SETTINGS_ROWS = [("window_size", "Window Size"), ("music_volume", "Music Volume"), ("sfx_volume", "Sound Effects")]


# Readable name for a window size option, e.g. Large (1200 x 800).
def window_size_label(index):
    name, size = WINDOW_SIZES[index]
    return name if size is None else f"{name} ({size[0]} x {size[1]})"


class SettingsMenu:
    # Loads the saved settings and makes a < and > button for each row.
    def __init__(self):
        self.values = load_user_settings()
        self.back_button = back_button()
        self.selected = 0
        self.step_buttons = []  # (row index, step, button)
        for index in range(len(SETTINGS_ROWS)):
            row = menu_row_rect(index)
            self.step_buttons.append((index, -1, Button(row.right - 110, row.y + 4, 46, 28, "<")))
            self.step_buttons.append((index, 1, Button(row.right - 56, row.y + 4, 46, 28, ">")))

    # Nothing to reset when the settings screen opens.
    def open(self):
        pass

    # Changes one setting by one step, applies it straight away and saves.
    def _change(self, index, step):
        key = SETTINGS_ROWS[index][0]
        if key == "window_size":
            self.values[key] = (self.values[key] + step) % len(WINDOW_SIZES)
            display.apply_window_size(self.values[key])
        else:
            self.values[key] = max(0, min(100, self.values[key] + step * VOLUME_STEP))
            audio.set_volumes(self.values["music_volume"], self.values["sfx_volume"])
            if key == "sfx_volume":
                audio.play("click")  # preview the new effects volume
        save_user_settings(self.values)

    # < / > buttons, or UP/DOWN to pick a row and LEFT/RIGHT to change it. Returns True to go back.
    def handle_event(self, event):
        if self.back_button.is_clicked(event):
            return True
        for index, step, button in self.step_buttons:
            if button.is_clicked(event):
                self.selected = index
                self._change(index, step)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                return True
            if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
                move = -1 if event.key in (pygame.K_UP, pygame.K_w) else 1
                self.selected = (self.selected + move) % len(SETTINGS_ROWS)
            step = {pygame.K_LEFT: -1, pygame.K_a: -1, pygame.K_RIGHT: 1, pygame.K_d: 1}.get(event.key, 0)
            if step:
                self._change(self.selected, step)
        return False

    # Draws each setting with its value, a bar for volumes, and its < > buttons.
    def draw(self):
        rows = []
        for key, label in SETTINGS_ROWS:
            value = window_size_label(self.values[key]) if key == "window_size" else f"{self.values[key]}%"
            rows.append((label, value))
        draw_menu_screen("SETTINGS", rows, self.selected, "Click < > or use the arrow keys    ESC back", "The dungeon grid stays the same at every window size.")
        for index, (key, _) in enumerate(SETTINGS_ROWS):
            if key != "window_size":
                row = menu_row_rect(index)
                bar = pygame.Rect(470, row.y + 12, 300, 12)
                pygame.draw.rect(display.screen, (40, 44, 62), bar, border_radius=4)
                pygame.draw.rect(display.screen, COLORS["gold"], (bar.x, bar.y, bar.width * self.values[key] // 100, bar.height), border_radius=4)
        for _, _, button in self.step_buttons:
            button.draw()
        self.back_button.draw()


class AccountMenu:
    # Sets up the account screen for the given Accounts.
    def __init__(self, accounts):
        self.accounts = accounts
        self.selected = 0
        self.typed_name = None  # not None while entering a new account name
        self.pending_delete = False
        self.message = ""
        self.message_color = COLORS["muted"]
        self.back_button = back_button()

    # Resets the screen each time it opens, with the active account selected.
    def open(self):
        self.selected = self.accounts.names.index(self.accounts.active)
        self.typed_name = None
        self.pending_delete = False
        self.message = ""

    # Shows a green (success) or red (error) message.
    def _say(self, ok, message):
        self.message = message
        self.message_color = COLORS["exit"] if ok else COLORS["danger"]

    # Click an account (or select + ENTER) to play as it; also creates and deletes accounts. Returns True to go back.
    def handle_event(self, event):
        names = self.accounts.names
        if self.typed_name is None and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_button.is_clicked(event):
                return True
            for index, name in enumerate(names):
                if menu_row_rect(index).collidepoint(display.to_canvas(event.pos)):
                    audio.play("click")
                    self.accounts.switch(name)
                    return True
        if event.type != pygame.KEYDOWN:
            return False
        if self.typed_name is not None:
            self._handle_typing(event)
            return False

        if event.key == pygame.K_ESCAPE:
            return True
        if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
            step = -1 if event.key in (pygame.K_UP, pygame.K_w) else 1
            self.selected = (self.selected + step) % len(names)
            self.pending_delete = False
            self.message = ""
        elif event.key == pygame.K_RETURN:
            self.accounts.switch(names[self.selected])
            return True
        elif event.key == pygame.K_n:
            self.typed_name = ""
            self.message = ""
        elif event.key in (pygame.K_DELETE, pygame.K_x):
            name = names[self.selected]
            if not self.pending_delete:
                self.pending_delete = True
                self._say(False, f"Press DELETE again to permanently delete '{name}'.")
            else:
                self.pending_delete = False
                self._say(*self.accounts.delete(name))
                self.selected = min(self.selected, len(self.accounts.names) - 1)
        return False

    # Handles keys while typing a new account name.
    def _handle_typing(self, event):
        if event.key == pygame.K_ESCAPE:
            self.typed_name = None
        elif event.key == pygame.K_RETURN:
            ok, message = self.accounts.create(self.typed_name)
            self._say(ok, message)
            if ok:
                self.typed_name = None
                self.selected = self.accounts.names.index(self.accounts.active)
        elif event.key == pygame.K_BACKSPACE:
            self.typed_name = self.typed_name[:-1]
        elif event.unicode and event.unicode.isprintable() and len(self.typed_name) < PROFILE_NAME_MAX_LENGTH:
            self.typed_name += event.unicode

    # Draws the account list, or the name prompt while creating one.
    def draw(self):
        rows = []
        for name, progression in self.accounts.profiles.items():
            label = f"{name} (active)" if name == self.accounts.active else name
            detail = f"{format_number(progression.relics)} relics - {format_number(progression.diamonds)} diamonds - checkpoint floor {progression.checkpoint_floor}"
            rows.append((label, detail))
        if self.typed_name is not None:
            draw_menu_screen("ACCOUNTS", rows, -1, "Type a name    ENTER create    ESC cancel", f"New account name: {self.typed_name}_", COLORS["text"])
        else:
            draw_menu_screen("ACCOUNTS", rows, self.selected, "Click or ENTER to play as    N new    DELETE remove    ESC back", self.message, self.message_color)
            self.back_button.draw()
