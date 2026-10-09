"""Per-device preferences (window size and volumes), stored apart from account saves so they
don't follow an account to another machine."""
import json

from core.settings import DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME, DEFAULT_WINDOW_SIZE_INDEX, USER_SETTINGS_FILE, WINDOW_SIZES


# Reads this computer's settings, replacing missing or invalid values with defaults.
def load_user_settings():
    try:
        with open(USER_SETTINGS_FILE, "r", encoding="utf-8") as settings_file:
            data = json.load(settings_file)
    except (OSError, ValueError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    return {
        "window_size": _valid_int(data.get("window_size"), 0, len(WINDOW_SIZES) - 1, DEFAULT_WINDOW_SIZE_INDEX),
        "music_volume": _valid_int(data.get("music_volume"), 0, 100, DEFAULT_MUSIC_VOLUME),
        "sfx_volume": _valid_int(data.get("sfx_volume"), 0, 100, DEFAULT_SFX_VOLUME),
    }


# Returns value if it is a whole number between low and high, otherwise the default.
def _valid_int(value, low, high, default):
    return value if isinstance(value, int) and low <= value <= high else default


# Writes this computer's settings to USER_SETTINGS_FILE.
def save_user_settings(values):
    try:
        with open(USER_SETTINGS_FILE, "w", encoding="utf-8") as settings_file:
            json.dump(values, settings_file, indent=2)
    except OSError:
        pass  # best-effort, like the account save
