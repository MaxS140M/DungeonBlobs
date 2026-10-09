"""Clickable buttons. Rects are in canvas coordinates, so they line up with the
mouse at every window size."""
import pygame

from core import audio
from core.display import font, screen, to_canvas
from core.settings import COLORS


class Button:
    # Creates a button covering the given canvas rectangle.
    def __init__(self, x, y, width, height, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label

    # True while the mouse is over the button.
    def is_hovered(self):
        return self.rect.collidepoint(to_canvas(pygame.mouse.get_pos()))

    # True if this event is a left click on the button (and plays the click sound).
    def is_clicked(self, event):
        clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.rect.collidepoint(to_canvas(event.pos))
        if clicked:
            audio.play("click")
        return clicked

    # Draws the button. Disabled buttons are greyed out; selected ones stay highlighted (e.g. the active tab).
    def draw(self, enabled=True, selected=False, label=None):
        hovered = enabled and self.is_hovered()
        fill = (52, 57, 80) if hovered else (40, 44, 62) if selected else (28, 31, 45)
        border = COLORS["gold_light"] if hovered or selected else COLORS["wall_edge"]
        text_color = (COLORS["gold_light"] if hovered or selected else COLORS["text"]) if enabled else COLORS["muted"]
        pygame.draw.rect(screen, fill, self.rect, border_radius=6)
        pygame.draw.rect(screen, border, self.rect, 2, border_radius=6)
        text = font.render(self.label if label is None else label, True, text_color)
        screen.blit(text, text.get_rect(center=self.rect.center))


# The Back button shown in the top-left corner of every sub-screen.
def back_button():
    return Button(20, 20, 100, 36, "< Back")
