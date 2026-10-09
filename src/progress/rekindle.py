"""Rekindling: the prestige reset. Trades relics, relic upgrades and the checkpoint
for Embers, and sells Heirlooms (permanent, bought with diamonds)."""
from core.numbers import format_number, grow
from core.settings import (
    EMBER_DIVISOR,
    EMBER_FLOOR_OFFSET,
    HEIRLOOM_COST_GROWTH,
    HEIRLOOMS,
    PARTNER_ROLES,
    PARTNER_UNLOCK_EVERY,
    REKINDLE_UNLOCK_FLOOR,
)

# The relic-bought upgrades that a rekindle resets.
UPGRADE_LEVEL_FIELDS = ["health_level", "attack_level", "relic_yield_level", "speed_level", "regen_level", "reach_level"]


# Embers earned for reaching `floor` this cycle. Squared, so pushing deeper pays off more.
def embers_for_floor(floor):
    return max(0, floor - EMBER_FLOOR_OFFSET) ** 2 // EMBER_DIVISOR


# The first floor past `floor` that would give at least one more Ember.
def next_ember_floor(floor):
    current = embers_for_floor(floor)
    next_floor = floor + 1
    while embers_for_floor(next_floor) <= current:
        next_floor += 1
    return next_floor


# True once the player has beaten the boss on REKINDLE_UNLOCK_FLOOR.
def can_rekindle(progression):
    return progression.checkpoint_floor >= REKINDLE_UNLOCK_FLOOR


# Partner roles unlocked after `rekindles` rekindles (one more every PARTNER_UNLOCK_EVERY).
def unlocked_partners(rekindles):
    return list(PARTNER_ROLES)[:rekindles // PARTNER_UNLOCK_EVERY]


# How many rekindles in total are needed to unlock the partner role `role`.
def partner_unlock_rekindles(role):
    return (list(PARTNER_ROLES).index(role) + 1) * PARTNER_UNLOCK_EVERY


# Resets this cycle's progress, awards Embers and sets the partner for the next
# cycle (None = no partner). Returns how many Embers were gained.
def rekindle(progression, partner=None):
    gained = embers_for_floor(progression.cycle_best_floor)
    progression.embers += gained
    progression.rekindles += 1
    progression.partner = partner if partner in unlocked_partners(progression.rekindles) else None
    keep = progression.heirloom_bonus("echo_stone") / 100
    for field in UPGRADE_LEVEL_FIELDS:
        setattr(progression, field, int(getattr(progression, field) * keep))
    progression.relics = 0
    progression.checkpoint_floor = progression.heirloom_bonus("deep_map")
    progression.cycle_best_floor = progression.checkpoint_floor
    return gained


# True if this heirloom has reached its max level (if it has one).
def heirloom_maxed(progression, key):
    max_level = HEIRLOOMS[key]["max_level"]
    return max_level is not None and progression.heirlooms[key] >= max_level


# Diamond price of the next level of an heirloom.
def heirloom_cost(progression, key):
    return grow(HEIRLOOMS[key]["base_cost"], HEIRLOOM_COST_GROWTH, progression.heirlooms[key])


# Buys the next level of an heirloom with diamonds. Returns (success, message).
def try_buy_heirloom(progression, key):
    name = HEIRLOOMS[key]["name"]
    if heirloom_maxed(progression, key):
        return False, f"{name} is already at max level."
    cost = heirloom_cost(progression, key)
    if progression.diamonds < cost:
        return False, f"Need {format_number(cost)} diamonds for {name}."
    progression.diamonds -= cost
    progression.heirlooms[key] += 1
    return True, f"{name} is now level {progression.heirlooms[key]}!"
