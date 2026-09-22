"""Static configuration and data tables: window/tile sizes, colors, costs, enemy
types, and dungeon layouts. No game logic lives here, just constants."""
import os
import sys

WIDTH, HEIGHT = 960, 640
TILE = 48
MAP_WIDTH, MAP_HEIGHT = 18, 12
FPS = 60

COLORS = {
    "background": (11, 13, 21),
    "floor": (39, 42, 58),
    "floor_alt": (44, 47, 64),
    "wall": (20, 23, 35),
    "wall_edge": (74, 64, 83),
    "gold": (246, 190, 76),
    "gold_light": (255, 226, 133),
    "player": (101, 193, 255),
    "player_light": (194, 239, 255),
    "enemy": (224, 83, 92),
    "enemy_dark": (117, 36, 61),
    "exit": (111, 224, 160),
    "text": (234, 237, 246),
    "muted": (151, 158, 178),
    "danger": (255, 116, 111),
}

# --- Permanent progression configuration (persists across runs in SAVE_FILE) ---
STARTING_MAX_HEALTH = 100
STARTING_ATTACK_DAMAGE = 10
STARTING_RELIC_YIELD = 1
STARTING_CURRENCY = 0

STARTING_MOVE_SPEED = 185

HEALTH_UPGRADE_BASE_COST = 5
ATTACK_UPGRADE_BASE_COST = 5
RELIC_YIELD_UPGRADE_BASE_COST = 10
SPEED_UPGRADE_BASE_COST = 8
UPGRADE_COST_GROWTH = 1.6  # cost = base_cost * growth ** level

HEALTH_UPGRADE_AMOUNT = 20
ATTACK_UPGRADE_AMOUNT = 2
RELIC_YIELD_UPGRADE_AMOUNT = 1
SPEED_UPGRADE_AMOUNT = 15

SAVE_FILE = os.path.join(
    # PyInstaller extracts to a temp dir, so save next to the .exe instead of __file__ when frozen.
    os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__)),
    "save_data.json",
)

# --- Player combat/visual configuration ---
ATTACK_DURATION = 0.18
ATTACK_COOLDOWN = 0.36

# Every 10 attack-upgrade levels unlocks a new look for the player blob, shown
# both in the lobby preview and during gameplay. Add more entries to extend it.
PLAYER_VISUAL_TIERS = [
    {"name": "Recruit", "body_color": (101, 193, 255), "accent_color": (194, 239, 255), "outline": None, "aura": None, "spikes": False, "crown": False},
    {"name": "Veteran", "body_color": (101, 193, 255), "accent_color": (255, 226, 133), "outline": (255, 226, 133), "aura": None, "spikes": False, "crown": False},
    {"name": "Champion", "body_color": (120, 170, 255), "accent_color": (255, 226, 133), "outline": (255, 226, 133), "aura": (255, 226, 133, 60), "spikes": True, "crown": False},
    {"name": "Ascended", "body_color": (180, 140, 255), "accent_color": (255, 255, 255), "outline": (255, 255, 255), "aura": (196, 140, 255, 80), "spikes": True, "crown": True},
]
PLAYER_VISUAL_TIER_STEP = 10  # attack-upgrade levels per visual tier

# --- Infinite dungeon difficulty configuration ---
# Tuned so difficulty ramps gradually instead of spiking: enemy count grows by
# one per floor (capped), health/damage/speed bonuses are small per-floor steps.
ENEMY_COUNT_BASE = 3
ENEMY_COUNT_PER_FLOOR = 1
ENEMY_COUNT_MAX = 10
RELIC_COUNT_BASE = 2
RELIC_COUNT_FLOOR_DIVISOR = 3
RELIC_COUNT_MAX = 6
ENEMY_HEALTH_PER_FLOOR = 4
ENEMY_DAMAGE_PER_FLOOR = 1
ENEMY_SPEED_PER_FLOOR = 3
ENEMY_SPEED_CAP_MULTIPLIER = 1.6

ENEMY_TYPES = {
    "grunt": {"health": 20, "speed": 70, "damage": 8, "radius": 14, "color": (224, 83, 92), "weight": 5, "unlock_floor": 1},
    "brute": {"health": 46, "speed": 46, "damage": 14, "radius": 18, "color": (168, 76, 60), "weight": 3, "unlock_floor": 3},
    "sprinter": {"health": 12, "speed": 122, "damage": 6, "radius": 12, "color": (196, 120, 214), "weight": 2, "unlock_floor": 5},
}

# Multiple room designs; one is picked at random for every floor. Each layout
# must be MAP_WIDTH x MAP_HEIGHT with a border of "#" and its own guaranteed-open
# spawn tile (checked at runtime via reachable_tiles, not just assumed).
DUNGEON_LAYOUTS = [
    {
        "name": "Chambers",
        "spawn": (2, 4),
        "grid": [
            "##################",
            "#........#.......#",
            "#........#.......#",
            "#........#.......#",
            "#........#.......#",
            "#................#",
            "#..####..#..###..#",
            "#..#.....#....#..#",
            "#..#..........#..#",
            "#..####..#..###..#",
            "#........#.......#",
            "#........#.......#",
            "##################",
        ],
    },
    {
        "name": "The Hollow",
        "spawn": (2, 4),
        "grid": [
            "##################",
            "#................#",
            "#..##........##..#",
            "#..##........##..#",
            "#................#",
            "#....##....##....#",
            "#....##....##....#",
            "#................#",
            "#..##........##..#",
            "#..##........##..#",
            "#................#",
            "##################",
        ],
    },
    {
        "name": "Twin Halls",
        "spawn": (2, 2),
        "grid": [
            "##################",
            "#................#",
            "#................#",
            "#................#",
            "#................#",
            "#................#",
            "#####....#....####",
            "#................#",
            "#................#",
            "#................#",
            "#................#",
            "##################",
        ],
    },
    {
        "name": "Crossroads",
        "spawn": (8, 5),
        "grid": [
            "##################",
            "######......######",
            "######......######",
            "######......######",
            "######......######",
            "#................#",
            "#................#",
            "######......######",
            "######......######",
            "######......######",
            "######......######",
            "##################",
        ],
    },
]
