"""Permanent currency and upgrade levels (saved per account by accounts.py)."""
from core.numbers import format_number, grow, scale
from core.settings import (
    ATTACK_UPGRADE_AMOUNT,
    ATTACK_UPGRADE_BASE_COST,
    EMBER_BONUS_PERCENT,
    HEALTH_UPGRADE_AMOUNT,
    HEALTH_UPGRADE_BASE_COST,
    HEIRLOOMS,
    PARTNER_ROLES,
    REACH_UPGRADE_AMOUNT,
    REACH_UPGRADE_BASE_COST,
    REGEN_UPGRADE_AMOUNT,
    REGEN_UPGRADE_BASE_COST,
    RELIC_YIELD_UPGRADE_AMOUNT,
    RELIC_YIELD_UPGRADE_BASE_COST,
    SPEED_UPGRADE_AMOUNT,
    SPEED_UPGRADE_BASE_COST,
    STARTING_ATTACK_DAMAGE,
    STARTING_CURRENCY,
    STARTING_MAX_HEALTH,
    STARTING_MOVE_SPEED,
    STARTING_RELIC_YIELD,
    UPGRADE_COST_GROWTH,
)


# Cost of the next level of an upgrade; grows by UPGRADE_COST_GROWTH each level.
def upgrade_cost(base_cost, level):
    return grow(base_cost, UPGRADE_COST_GROWTH, level)


class PermanentProgression:
    """Currency and upgrade levels that persist across runs (saved to disk)."""

    # Stores currencies, upgrade levels and the checkpoint floor.
    def __init__(self, relics=STARTING_CURRENCY, health_level=0, attack_level=0, relic_yield_level=0, speed_level=0, regen_level=0, reach_level=0, diamonds=0, checkpoint_floor=0, best_floor=0, total_relics_earned=0, embers=0, rekindles=0, cycle_best_floor=None, heirlooms=None, partner=None):
        self.relics = relics
        self.diamonds = diamonds
        self.checkpoint_floor = checkpoint_floor  # highest boss floor beaten; runs may start on the floor after it
        self.best_floor = max(best_floor, checkpoint_floor)  # leaderboard stat: highest floor ever reached
        self.total_relics_earned = total_relics_earned  # leaderboard stat: every relic banked, spent or not
        # Highest floor since the last rekindle (decides how many Embers a rekindle gives).
        self.cycle_best_floor = self.best_floor if cycle_best_floor is None else cycle_best_floor
        self.embers = embers
        self.rekindles = rekindles
        self.heirlooms = {key: (heirlooms or {}).get(key, 0) for key in HEIRLOOMS}  # heirloom key -> level
        self.partner = partner if partner in PARTNER_ROLES else None  # chosen partner role, picked when rekindling
        self.health_level = health_level
        self.attack_level = attack_level
        self.relic_yield_level = relic_yield_level
        self.speed_level = speed_level
        self.regen_level = regen_level
        self.reach_level = reach_level

    # Total bonus from an heirloom: its level times its per-level amount.
    def heirloom_bonus(self, key):
        return self.heirlooms[key] * HEIRLOOMS[key]["per_level"]

    # Percent bonus to damage and relics from Embers.
    @property
    def ember_bonus_percent(self):
        return self.embers * EMBER_BONUS_PERCENT

    # Max HP including Vitality Charm upgrades and the Amber Heart heirloom.
    @property
    def max_health(self):
        base = STARTING_MAX_HEALTH + self.health_level * HEALTH_UPGRADE_AMOUNT
        return round(base * (1 + self.heirloom_bonus("amber_heart") / 100))

    # Attack damage including Whetstone upgrades, the Ember bonus and the Bloodstone heirloom.
    @property
    def attack_damage(self):
        base = STARTING_ATTACK_DAMAGE + self.attack_level * ATTACK_UPGRADE_AMOUNT
        return round(base * (1 + self.ember_bonus_percent / 100) * (1 + self.heirloom_bonus("bloodstone") / 100), 1)

    # Multiplier applied to relics when a run is banked (Embers and Golden Lens).
    @property
    def relic_multiplier(self):
        return (1 + self.ember_bonus_percent / 100) * (1 + self.heirloom_bonus("golden_lens") / 100)

    # Relics gained per pickup including Fortune Idol upgrades.
    @property
    def relic_yield(self):
        return STARTING_RELIC_YIELD + self.relic_yield_level * RELIC_YIELD_UPGRADE_AMOUNT

    # Movement speed including Swift Boots upgrades.
    @property
    def move_speed(self):
        return STARTING_MOVE_SPEED + self.speed_level * SPEED_UPGRADE_AMOUNT

    # Percent of max HP restored each time a floor is cleared (Healing Herb upgrades).
    @property
    def floor_heal_percent(self):
        return self.regen_level * REGEN_UPGRADE_AMOUNT

    # Sword swing size multiplier including Long Blade upgrades (1.0 = normal).
    @property
    def attack_reach(self):
        return 1 + self.reach_level * REACH_UPGRADE_AMOUNT / 100

    # Applies the Merchant's Scale discount to a relic upgrade price (never below 1).
    def _discounted(self, cost):
        return max(1, scale(cost, 1 - self.heirloom_bonus("merchants_scale") / 100))

    # Price of the next Vitality Charm.
    def health_upgrade_cost(self):
        return self._discounted(upgrade_cost(HEALTH_UPGRADE_BASE_COST, self.health_level))

    # Price of the next Whetstone.
    def attack_upgrade_cost(self):
        return self._discounted(upgrade_cost(ATTACK_UPGRADE_BASE_COST, self.attack_level))

    # Price of the next Fortune Idol.
    def relic_yield_upgrade_cost(self):
        return self._discounted(upgrade_cost(RELIC_YIELD_UPGRADE_BASE_COST, self.relic_yield_level))

    # Price of the next Swift Boots.
    def speed_upgrade_cost(self):
        return self._discounted(upgrade_cost(SPEED_UPGRADE_BASE_COST, self.speed_level))

    # Price of the next Healing Herb.
    def regen_upgrade_cost(self):
        return self._discounted(upgrade_cost(REGEN_UPGRADE_BASE_COST, self.regen_level))

    # Price of the next Long Blade.
    def reach_upgrade_cost(self):
        return self._discounted(upgrade_cost(REACH_UPGRADE_BASE_COST, self.reach_level))

    # Converts to a plain dict for saving as JSON.
    def to_dict(self):
        return {
            "relics": self.relics,
            "health_level": self.health_level,
            "attack_level": self.attack_level,
            "relic_yield_level": self.relic_yield_level,
            "speed_level": self.speed_level,
            "regen_level": self.regen_level,
            "reach_level": self.reach_level,
            "diamonds": self.diamonds,
            "checkpoint_floor": self.checkpoint_floor,
            "best_floor": self.best_floor,
            "total_relics_earned": self.total_relics_earned,
            "cycle_best_floor": self.cycle_best_floor,
            "embers": self.embers,
            "rekindles": self.rekindles,
            "heirlooms": dict(self.heirlooms),
            "partner": self.partner,
        }

    # Builds from saved JSON data, falling back to defaults if it is invalid.
    @classmethod
    def from_dict(cls, data):
        try:
            return cls(
                relics=max(0, int(data.get("relics", STARTING_CURRENCY))),
                health_level=max(0, int(data.get("health_level", 0))),
                attack_level=max(0, int(data.get("attack_level", 0))),
                relic_yield_level=max(0, int(data.get("relic_yield_level", 0))),
                speed_level=max(0, int(data.get("speed_level", 0))),
                regen_level=max(0, int(data.get("regen_level", 0))),
                reach_level=max(0, int(data.get("reach_level", 0))),
                diamonds=max(0, int(data.get("diamonds", 0))),
                checkpoint_floor=max(0, int(data.get("checkpoint_floor", 0))),
                best_floor=max(0, int(data.get("best_floor", 0))),
                total_relics_earned=max(0, int(data.get("total_relics_earned", 0))),
                embers=max(0, int(data.get("embers", 0))),
                rekindles=max(0, int(data.get("rekindles", 0))),
                cycle_best_floor=max(0, int(data["cycle_best_floor"])) if "cycle_best_floor" in data else None,
                heirlooms={key: max(0, int(level)) for key, level in data.get("heirlooms", {}).items()},
                partner=data.get("partner"),
            )
        except (TypeError, ValueError, AttributeError):
            return cls()

    # Banks a finished run (relics boosted by relic_multiplier, diamonds by Prism Shard)
    # and updates the stats. Returns (relics banked, diamonds banked).
    def record_run(self, floor, relics, diamonds):
        banked_relics = scale(relics, self.relic_multiplier)
        banked_diamonds = scale(diamonds, 1 + self.heirloom_bonus("prism_shard") / 100)
        self.relics += banked_relics
        self.diamonds += banked_diamonds
        self.total_relics_earned += banked_relics
        self.best_floor = max(self.best_floor, floor)
        self.cycle_best_floor = max(self.cycle_best_floor, floor)
        return banked_relics, banked_diamonds


# Buys a Vitality Charm if affordable. Returns (success, message).
def try_buy_health(progression):
    cost = progression.health_upgrade_cost()
    if progression.relics < cost:
        return False, f"Need {format_number(cost)} relics for a Vitality Charm."
    progression.relics -= cost
    progression.health_level += 1
    return True, f"Vitality Charm purchased! Max HP is now {format_number(progression.max_health)}."


# Buys a Whetstone if affordable. Returns (success, message).
def try_buy_attack(progression):
    cost = progression.attack_upgrade_cost()
    if progression.relics < cost:
        return False, f"Need {format_number(cost)} relics for a Whetstone."
    progression.relics -= cost
    progression.attack_level += 1
    return True, f"Whetstone purchased! Attack damage is now {format_number(progression.attack_damage)}."


# Buys a Fortune Idol if affordable. Returns (success, message).
def try_buy_relic_yield(progression):
    cost = progression.relic_yield_upgrade_cost()
    if progression.relics < cost:
        return False, f"Need {format_number(cost)} relics for a Fortune Idol."
    progression.relics -= cost
    progression.relic_yield_level += 1
    return True, f"Fortune Idol purchased! Relic yield is now x{format_number(progression.relic_yield)}."


# Buys Swift Boots if affordable. Returns (success, message).
def try_buy_speed(progression):
    cost = progression.speed_upgrade_cost()
    if progression.relics < cost:
        return False, f"Need {format_number(cost)} relics for Swift Boots."
    progression.relics -= cost
    progression.speed_level += 1
    return True, f"Swift Boots purchased! Move speed is now {format_number(progression.move_speed)}."


# Buys a Healing Herb if affordable. Returns (success, message).
def try_buy_regen(progression):
    cost = progression.regen_upgrade_cost()
    if progression.relics < cost:
        return False, f"Need {format_number(cost)} relics for a Healing Herb."
    progression.relics -= cost
    progression.regen_level += 1
    return True, f"Healing Herb purchased! Clearing a floor now heals {progression.floor_heal_percent}% HP."


# Buys a Long Blade if affordable. Returns (success, message).
def try_buy_reach(progression):
    cost = progression.reach_upgrade_cost()
    if progression.relics < cost:
        return False, f"Need {format_number(cost)} relics for a Long Blade."
    progression.relics -= cost
    progression.reach_level += 1
    return True, f"Long Blade purchased! Sword swing is now {round(progression.attack_reach * 100)}% size."
