"""Loads optional images from the Assets folder. A missing or broken file gives
None, so the game falls back to drawing its usual shapes."""
import os

import pygame

from core.settings import ASSETS_DIR

_cache = {}


# Loads Assets/<name> once and caches it, or returns None if it can't be loaded.
def load_image(name):
    if name not in _cache:
        try:
            _cache[name] = pygame.image.load(os.path.join(ASSETS_DIR, name)).convert_alpha()
        except (pygame.error, OSError):
            _cache[name] = None
    return _cache[name]
