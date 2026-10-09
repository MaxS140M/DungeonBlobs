"""Background music and sound effects from the Sounds folder. If there is no audio
device, or a file is missing, the game simply stays silent instead of crashing."""
import os

import pygame

from core.settings import MUSIC_FILE, SOUND_EFFECTS, SOUNDS_DIR

_sounds = {}  # loaded sound effects (None if a file couldn't be loaded)
_sfx_volume = 1.0
_audio_available = True


# True if the mixer is (or can be) started; remembers failure so it isn't retried every call.
def _mixer_ready():
    global _audio_available
    if _audio_available and not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except pygame.error:
            _audio_available = False
    return _audio_available


# Applies the music and sound-effect volumes (0-100, from the settings screen).
def set_volumes(music_volume, sfx_volume):
    global _sfx_volume
    _sfx_volume = sfx_volume / 100
    if _mixer_ready():
        pygame.mixer.music.set_volume(music_volume / 100)


# Starts the background music looping forever.
def start_music():
    if not _mixer_ready():
        return
    try:
        pygame.mixer.music.load(os.path.join(SOUNDS_DIR, MUSIC_FILE))
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass  # missing or unreadable music file: play without music


# Plays a sound effect by its SOUND_EFFECTS key, e.g. play("coin").
def play(name):
    if not _mixer_ready() or _sfx_volume <= 0:
        return
    if name not in _sounds:
        try:
            _sounds[name] = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, SOUND_EFFECTS[name]))
        except (pygame.error, OSError):
            _sounds[name] = None
    sound = _sounds[name]
    if sound:
        sound.set_volume(_sfx_volume)
        sound.play()
