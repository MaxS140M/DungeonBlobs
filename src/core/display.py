import pygame

from core.settings import HEIGHT, WIDTH, WINDOW_SIZES
from progress.user_settings import load_user_settings

pygame.init()
pygame.display.set_caption("The Lantern Vault")

# Everything draws to this fixed-size canvas; present() scales it to fit the real
# window, so the grid and layout are identical at every window size.
screen = pygame.Surface((WIDTH, HEIGHT))
window = None
clock = pygame.time.Clock()
font = pygame.font.Font(None, 25)
small_font = pygame.font.Font(None, 19)
large_font = pygame.font.Font(None, 64)


# Opens (or resizes) the real window using an option from WINDOW_SIZES.
def apply_window_size(index):
    global window
    size = WINDOW_SIZES[index][1]
    window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if size is None else pygame.display.set_mode(size)


# Where the scaled canvas sits inside the window (centred, keeping its aspect ratio).
def canvas_area():
    window_rect = window.get_rect()
    scale = min(window_rect.width / WIDTH, window_rect.height / HEIGHT)
    area = pygame.Rect(0, 0, round(WIDTH * scale), round(HEIGHT * scale))
    area.center = window_rect.center
    return area


# Converts a window position (e.g. the mouse) into canvas coordinates, undoing the scaling.
def to_canvas(window_pos):
    area = canvas_area()
    return (
        int((window_pos[0] - area.x) * WIDTH / area.width),
        int((window_pos[1] - area.y) * HEIGHT / area.height),
    )


# Scales the canvas to fit the window (black bars keep the aspect ratio) and shows the frame.
def present():
    area = canvas_area()
    frame = screen if area.size == (WIDTH, HEIGHT) else pygame.transform.smoothscale(screen, area.size)
    window.fill((0, 0, 0))
    window.blit(frame, area)
    pygame.display.flip()


apply_window_size(load_user_settings()["window_size"])
