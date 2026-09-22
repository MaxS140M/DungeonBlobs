"""Enemy/relic wave generation and run bootstrapping for a new dungeon run."""
import math
import random

import pygame

import dungeon
from entities import Enemy, Player
from settings import (
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


def enemy_kinds_for_floor(floor):
    return [kind for kind, stats in ENEMY_TYPES.items() if floor >= stats["unlock_floor"]]


def pick_enemy_kind(floor):
    kinds = enemy_kinds_for_floor(floor)
    weights = [ENEMY_TYPES[kind]["weight"] for kind in kinds]
    return random.choices(kinds, weights=weights, k=1)[0]


def wave_enemy_count(floor):
    return min(ENEMY_COUNT_BASE + (floor - 1) * ENEMY_COUNT_PER_FLOOR, ENEMY_COUNT_MAX)


def wave_relic_count(floor):
    return min(RELIC_COUNT_BASE + floor // RELIC_COUNT_FLOOR_DIVISOR, RELIC_COUNT_MAX)


def random_open_positions(count, spawn_tile, min_distance=2.5):
    far_tiles = [pos for pos in dungeon.CURRENT_OPEN_TILES if math.hypot(pos[0] - spawn_tile[0], pos[1] - spawn_tile[1]) >= min_distance]
    pool = far_tiles if len(far_tiles) >= count else list(dungeon.CURRENT_OPEN_TILES)
    random.shuffle(pool)
    if len(pool) >= count:
        return pool[:count]
    return [random.choice(pool) for _ in range(count)]  # not enough unique tiles; allow repeats


def build_wave(floor, spawn_tile):
    enemy_count = wave_enemy_count(floor)
    relic_count = wave_relic_count(floor)
    positions = random_open_positions(enemy_count + relic_count, spawn_tile)
    enemies = [Enemy(x, y, pick_enemy_kind(floor), floor) for x, y in positions[:enemy_count]]
    relics = [
        pygame.Rect(x * TILE + 12, y * TILE + 12, 24, 24)
        for x, y in positions[enemy_count:enemy_count + relic_count]
    ]
    return enemies, relics


def start_run(progression):
    layout = random.choice(DUNGEON_LAYOUTS)
    dungeon.set_current_dungeon(layout)
    spawn = layout["spawn"]
    player = Player(progression.max_health, progression.attack_damage, progression.move_speed, spawn, progression.attack_level)
    floor = 1
    enemies, relics = build_wave(floor, spawn)
    return {
        "player": player,
        "enemies": enemies,
        "relics": relics,
        "floor": floor,
        "run_relics": 0,
        "elapsed": 0.0,
        "floor_banner": 2.0,
        "dungeon_name": layout["name"],
    }
