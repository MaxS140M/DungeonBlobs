"""Permanent currency and upgrade levels."""
import json

from settings import (
    ATTACK_UPGRADE_AMOUNT,
    ATTACK_UPGRADE_BASE_COST,
    HEALTH_UPGRADE_AMOUNT,
    HEALTH_UPGRADE_BASE_COST,
    RELIC_YIELD_UPGRADE_AMOUNT,
    RELIC_YIELD_UPGRADE_BASE_COST,
    SAVE_FILE,
    SPEED_UPGRADE_AMOUNT,
    SPEED_UPGRADE_BASE_COST,
    STARTING_ATTACK_DAMAGE,
    STARTING_CURRENCY,
    STARTING_MAX_HEALTH,
    STARTING_MOVE_SPEED,
    STARTING_RELIC_YIELD,
    UPGRADE_COST_GROWTH,
)


def upgrade_cost(base_cost, level):
    return int(round(base_cost * (UPGRADE_COST_GROWTH ** level)))


class PermanentProgression:
    """Currency and upgrade levels that persist across runs (saved to disk)."""

    def __init__(self, relics=STARTING_CURRENCY, health_level=0, attack_level=0, relic_yield_level=0, speed_level=0):
        self.relics = relics
        self.health_level = health_level
        self.attack_level = attack_level
        self.relic_yield_level = relic_yield_level
        self.speed_level = speed_level

    @property
    def max_health(self):
        return STARTING_MAX_HEALTH + self.health_level * HEALTH_UPGRADE_AMOUNT

    @property
    def attack_damage(self):
        return STARTING_ATTACK_DAMAGE + self.attack_level * ATTACK_UPGRADE_AMOUNT

    @property
    def relic_yield(self):
        return STARTING_RELIC_YIELD + self.relic_yield_level * RELIC_YIELD_UPGRADE_AMOUNT

    @property
    def move_speed(self):
        return STARTING_MOVE_SPEED + self.speed_level * SPEED_UPGRADE_AMOUNT

    def health_upgrade_cost(self):
        return upgrade_cost(HEALTH_UPGRADE_BASE_COST, self.health_level)

    def attack_upgrade_cost(self):
        return upgrade_cost(ATTACK_UPGRADE_BASE_COST, self.attack_level)

    def relic_yield_upgrade_cost(self):
        return upgrade_cost(RELIC_YIELD_UPGRADE_BASE_COST, self.relic_yield_level)

    def speed_upgrade_cost(self):
        return upgrade_cost(SPEED_UPGRADE_BASE_COST, self.speed_level)

    def to_dict(self):
        return {
            "relics": self.relics,
            "health_level": self.health_level,
            "attack_level": self.attack_level,
            "relic_yield_level": self.relic_yield_level,
            "speed_level": self.speed_level,
        }

    @classmethod
    def from_dict(cls, data):
        try:
            return cls(
                relics=max(0, int(data.get("relics", STARTING_CURRENCY))),
                health_level=max(0, int(data.get("health_level", 0))),
                attack_level=max(0, int(data.get("attack_level", 0))),
                relic_yield_level=max(0, int(data.get("relic_yield_level", 0))),
                speed_level=max(0, int(data.get("speed_level", 0))),
            )
        except (TypeError, ValueError, AttributeError):
            return cls()


def load_progression():
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as save_file:
            data = json.load(save_file)
        return PermanentProgression.from_dict(data)
    except (OSError, ValueError, json.JSONDecodeError):
        return PermanentProgression()


def save_progression(progression):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as save_file:
            json.dump(progression.to_dict(), save_file, indent=2)
    except OSError:
        pass  # saving is best-effort; a failed write should not crash the game


def try_buy_health(progression):
    cost = progression.health_upgrade_cost()
    if progression.relics < cost:
        return False, f"Need {cost} relics for a Vitality Charm."
    progression.relics -= cost
    progression.health_level += 1
    save_progression(progression)
    return True, f"Vitality Charm purchased! Max HP is now {progression.max_health}."


def try_buy_attack(progression):
    cost = progression.attack_upgrade_cost()
    if progression.relics < cost:
        return False, f"Need {cost} relics for a Whetstone."
    progression.relics -= cost
    progression.attack_level += 1
    save_progression(progression)
    return True, f"Whetstone purchased! Attack damage is now {progression.attack_damage}."


def try_buy_relic_yield(progression):
    cost = progression.relic_yield_upgrade_cost()
    if progression.relics < cost:
        return False, f"Need {cost} relics for a Fortune Idol."
    progression.relics -= cost
    progression.relic_yield_level += 1
    save_progression(progression)
    return True, f"Fortune Idol purchased! Relic yield is now x{progression.relic_yield}."


def try_buy_speed(progression):
    cost = progression.speed_upgrade_cost()
    if progression.relics < cost:
        return False, f"Need {cost} relics for Swift Boots."
    progression.relics -= cost
    progression.speed_level += 1
    save_progression(progression)
    return True, f"Swift Boots purchased! Move speed is now {progression.move_speed}."
    save_progression(progression)
    return True, f"Swift Boots purchased! Move speed is now {progression.move_speed}."
