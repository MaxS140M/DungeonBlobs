"""Enemy/relic wave generation and run bootstrapping for a new dungeon run."""
import math
import random

import pygame

from game import dungeon
from game.entities import Boss, Enemy, Player
from game.partner import Partner
from core.settings import (
    BOSS_FLOOR_INTERVAL,
    BOSS_MINION_COUNT,
    DIAMOND_FLOOR_INTERVAL,
    DUNGEON_LAYOUTS,
    ENEMY_COUNT_BASE,
    ENEMY_COUNT_MAX,
    ENEMY_COUNT_PER_FLOOR,
    ENEMY_TYPES,
    RELIC_COUNT_BASE,
    RELIC_COUNT_FLOOR_DIVISOR,
    RELIC_COUNT_MAX,
    TILE,
)


# True on every BOSS_FLOOR_INTERVAL-th floor.
def is_boss_floor(floor):
    return floor % BOSS_FLOOR_INTERVAL == 0


# True on floors that spawn a diamond.
def is_diamond_floor(floor):
    return floor % DIAMOND_FLOOR_INTERVAL == 0


# Lists the enemy kinds unlocked by this floor.
def enemy_kinds_for_floor(floor):
    return [kind for kind, stats in ENEMY_TYPES.items() if floor >= stats["unlock_floor"]]


# Picks a random unlocked enemy kind, weighted by each kind's weight.
def pick_enemy_kind(floor):
    kinds = enemy_kinds_for_floor(floor)
    weights = [ENEMY_TYPES[kind]["weight"] for kind in kinds]
    return random.choices(kinds, weights=weights, k=1)[0]


# How many regular enemies spawn on a floor (capped at ENEMY_COUNT_MAX).
def wave_enemy_count(floor):
    return min(ENEMY_COUNT_BASE + (floor - 1) * ENEMY_COUNT_PER_FLOOR, ENEMY_COUNT_MAX)


# How many relics spawn on a floor (capped at RELIC_COUNT_MAX).
def wave_relic_count(floor):
    return min(RELIC_COUNT_BASE + floor // RELIC_COUNT_FLOOR_DIVISOR, RELIC_COUNT_MAX)


# Picks random reachable tiles, preferring ones away from the spawn tile.
def random_open_positions(count, spawn_tile, min_distance=2.5):
    far_tiles = [pos for pos in dungeon.CURRENT_OPEN_TILES if math.hypot(pos[0] - spawn_tile[0], pos[1] - spawn_tile[1]) >= min_distance]
    pool = far_tiles if len(far_tiles) >= count else list(dungeon.CURRENT_OPEN_TILES)
    random.shuffle(pool)
    if len(pool) >= count:
        return pool[:count]
    return [random.choice(pool) for _ in range(count)]  # not enough unique tiles; allow repeats


# Farthest open tile from spawn whose 8 neighbours are open too, so the oversized boss never starts stuck in a wall.
def boss_tile(spawn_tile):
    open_tiles = set(dungeon.CURRENT_OPEN_TILES)
    roomy = [
        (x, y) for x, y in open_tiles
        if all((x + dx, y + dy) in open_tiles for dx in (-1, 0, 1) for dy in (-1, 0, 1))
    ]
    return max(roomy or open_tiles, key=lambda pos: math.hypot(pos[0] - spawn_tile[0], pos[1] - spawn_tile[1]))


# Returns the hitbox for a relic or diamond on tile (x, y).
def pickup_rect(x, y):
    return pygame.Rect(x * TILE + 12, y * TILE + 12, 24, 24)


# Creates the enemies (plus boss on boss floors), relics and diamonds for a floor.
def build_wave(floor, spawn_tile):
    boss_floor = is_boss_floor(floor)
    enemy_count = BOSS_MINION_COUNT if boss_floor else wave_enemy_count(floor)
    relic_count = wave_relic_count(floor)
    diamond_count = 1 if is_diamond_floor(floor) else 0
    positions = random_open_positions(enemy_count + relic_count + diamond_count, spawn_tile)
    enemies = [Enemy(x, y, pick_enemy_kind(floor), floor) for x, y in positions[:enemy_count]]
    if boss_floor:
        enemies.append(Boss(*boss_tile(spawn_tile), floor))
    relics = [pickup_rect(x, y) for x, y in positions[enemy_count:enemy_count + relic_count]]
    diamonds = [pickup_rect(x, y) for x, y in positions[enemy_count + relic_count:]]
    return enemies, relics, diamonds


# Loads a random layout, moves the player to its spawn and fills it for this floor.
def enter_floor(run, floor):
    layout = random.choice(DUNGEON_LAYOUTS)
    dungeon.set_current_dungeon(layout)
    spawn = layout["spawn"]
    run["player"].teleport_to(spawn)
    if run["partner"]:
        run["partner"].teleport_to(run["player"])
    run["enemies"], run["relics"], run["diamonds"] = build_wave(floor, spawn)
    run["floor"] = floor
    run["dungeon_name"] = layout["name"]
    run["floor_banner"] = 2.0


# Creates a fresh run dictionary and enters the starting floor.
def start_run(progression, start_floor=1):
    # Spawn tile is a placeholder; enter_floor moves the player to the real one.
    player = Player(progression.max_health, progression.attack_damage, progression.move_speed, (0, 0), progression.attack_level, progression.attack_reach)
    run = {
        "player": player,
        "partner": Partner(progression.partner, player) if progression.partner else None,
        "run_relics": 0,
        "run_diamonds": 0,
        "elapsed": 0.0,
        "toast": "",
        "toast_timer": 0.0,
    }
    enter_floor(run, start_floor)
    return run
