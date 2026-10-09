"""Simple local accounts: each named profile owns its own PermanentProgression.

Saved to SAVE_FILE as {"active": name, "profiles": {name: progression_dict}}.
An old single-profile save is migrated into a profile named DEFAULT_PROFILE_NAME.
Linking a profile to an online (e.g. Google) account later only needs another
field per profile; nothing else reads this file directly."""
import json

from progress.progression import PermanentProgression
from core.settings import DEFAULT_PROFILE_NAME, MAX_PROFILES, PROFILE_NAME_MAX_LENGTH, SAVE_FILE


class Accounts:
    # Holds every profile's progression and the name of the active one.
    def __init__(self, profiles, active):
        self.profiles = profiles
        self.active = active

    # The active account's PermanentProgression.
    @property
    def progression(self):
        return self.profiles[self.active]

    # All account names, in creation order.
    @property
    def names(self):
        return list(self.profiles)

    # Adds a new account and switches to it. Returns (success, message).
    def create(self, name):
        name = name.strip()
        if not name:
            return False, "Name can't be empty."
        if len(name) > PROFILE_NAME_MAX_LENGTH:
            return False, f"Names can be at most {PROFILE_NAME_MAX_LENGTH} characters."
        if name in self.profiles:
            return False, f"'{name}' already exists."
        if len(self.profiles) >= MAX_PROFILES:
            return False, f"Only {MAX_PROFILES} accounts allowed."
        self.profiles[name] = PermanentProgression()
        self.active = name
        self.save()
        return True, f"Created '{name}'."

    # Makes another account the active one.
    def switch(self, name):
        self.active = name
        self.save()

    # Removes an account (never the last one). Returns (success, message).
    def delete(self, name):
        if len(self.profiles) == 1:
            return False, "Can't delete your only account."
        del self.profiles[name]
        if self.active == name:
            self.active = self.names[0]
        self.save()
        return True, f"Deleted '{name}'."

    # Writes all accounts to SAVE_FILE.
    def save(self):
        data = {"active": self.active, "profiles": {name: progression.to_dict() for name, progression in self.profiles.items()}}
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as save_file:
                json.dump(data, save_file, indent=2)
        except OSError:
            pass  # saving is best-effort; a failed write should not crash the game

    # Reads accounts from SAVE_FILE, converting an old single-profile save if found.
    @classmethod
    def load(cls):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as save_file:
                data = json.load(save_file)
        except (OSError, ValueError):
            data = {}
        if not isinstance(data, dict):
            data = {}

        raw_profiles = data.get("profiles")
        if isinstance(raw_profiles, dict):
            profiles = {str(name): PermanentProgression.from_dict(values) for name, values in raw_profiles.items()}
        elif data:
            profiles = {DEFAULT_PROFILE_NAME: PermanentProgression.from_dict(data)}  # pre-accounts save
        else:
            profiles = {}
        if not profiles:
            profiles = {DEFAULT_PROFILE_NAME: PermanentProgression()}

        active = data.get("active")
        return cls(profiles, active if active in profiles else next(iter(profiles)))
