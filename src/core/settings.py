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
    "player": (92, 214, 120),  # the player blob is always green
    "player_face": (24, 60, 34),
    "enemy": (224, 83, 92),
    "enemy_dark": (117, 36, 61),
    "exit": (111, 224, 160),
    "text": (234, 237, 246),
    "muted": (151, 158, 178),
    "danger": (255, 116, 111),
    "diamond": (120, 230, 255),
    "diamond_light": (225, 250, 255),
}

# Window size options. The game always renders to a fixed WIDTH x HEIGHT canvas
# that is scaled to fit the window, so the grid and layout never change.
WINDOW_SIZES = [
    ("Small", (720, 480)),
    ("Default", (WIDTH, HEIGHT)),
    ("Large", (1200, 800)),
    ("Huge", (1440, 960)),
    ("Fullscreen", None),
]
DEFAULT_WINDOW_SIZE_INDEX = 1
DEFAULT_MUSIC_VOLUME = 50  # percent
DEFAULT_SFX_VOLUME = 80  # percent
VOLUME_STEP = 10  # how much one click / key press changes a volume

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
REGEN_UPGRADE_BASE_COST = 12
REACH_UPGRADE_BASE_COST = 10
UPGRADE_COST_GROWTH = 1.6  # cost = base_cost * growth ** level

HEALTH_UPGRADE_AMOUNT = 20
ATTACK_UPGRADE_AMOUNT = 2
RELIC_YIELD_UPGRADE_AMOUNT = 1
SPEED_UPGRADE_AMOUNT = 15
REGEN_UPGRADE_AMOUNT = 1  # % of max HP healed per floor cleared, per level
REACH_UPGRADE_AMOUNT = 10  # % bigger sword swing (hitbox and blade) per level

# Saves live in src/ (next to main.py), or next to the .exe when frozen since PyInstaller extracts to a temp dir.
SAVE_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVE_FILE = os.path.join(SAVE_DIR, "save_data.json")  # accounts + their progression
USER_SETTINGS_FILE = os.path.join(SAVE_DIR, "user_settings.json")  # per-device options like window size

# Images live in the Assets folder at the project root. A built .exe bundles that
# folder (see main.spec), and PyInstaller unpacks bundled files into sys._MEIPASS.
ASSETS_DIR = os.path.join(sys._MEIPASS, "Assets") if getattr(sys, "frozen", False) else os.path.join(os.path.dirname(SAVE_DIR), "Assets")
MENU_BACKGROUND_IMAGE = "background1.png"  # shown behind the lobby and menu screens
MENU_BACKGROUND_DIM = 165  # 0-255: how much it is darkened so menu text stays readable
# 48x48 dungeon tiles. The two floor tiles alternate in a checkerboard.
TILE_IMAGES = {"floor": "tile1.png", "floor_alt": "tile2.png", "wall": "wall1.png"}

# Music and sound effects live in the Sounds folder at the project root (bundled like Assets).
SOUNDS_DIR = os.path.join(sys._MEIPASS, "Sounds") if getattr(sys, "frozen", False) else os.path.join(os.path.dirname(SAVE_DIR), "Sounds")
MUSIC_FILE = "Background_music_loop (1).mp3"  # loops the whole time
SOUND_EFFECTS = {
    "click": "Button Click.mp3",  # any button clicked
    "start": "Gamestart.mp3",  # a run starts
    "coin": "coin_collect.mp3",  # relic or diamond picked up
}

# --- Local accounts ---
DEFAULT_PROFILE_NAME = "Player"
MAX_PROFILES = 6
PROFILE_NAME_MAX_LENGTH = 14

# --- Rekindling (the prestige reset) ---
# Rekindling resets relics, the relic upgrades and the checkpoint, and gives
# Embers based on the best floor reached this cycle. Diamonds, Heirlooms and
# leaderboard stats are kept.
REKINDLE_UNLOCK_FLOOR = 25  # must have beaten this floor's boss (i.e. checkpoint >= it)
EMBER_FLOOR_OFFSET = 20  # Embers = (best floor this cycle - offset)^2 / EMBER_DIVISOR
EMBER_DIVISOR = 5
EMBER_BONUS_PERCENT = 2  # each Ember: +2% damage and +2% relics banked

# Heirlooms are permanent upgrades bought with diamonds; they survive rekindling.
# per_level is a percent, except Deep Map where it is floors. max_level None = no cap.
HEIRLOOM_COST_GROWTH = 1.5
HEIRLOOMS = {
    "golden_lens": {"name": "Golden Lens", "effect": "+{}% relics banked", "per_level": 10, "base_cost": 3, "max_level": None},
    "amber_heart": {"name": "Amber Heart", "effect": "+{}% max HP", "per_level": 5, "base_cost": 3, "max_level": None},
    "bloodstone": {"name": "Bloodstone", "effect": "+{}% damage", "per_level": 5, "base_cost": 3, "max_level": None},
    "echo_stone": {"name": "Echo Stone", "effect": "Keep {}% of upgrade levels on rekindle", "per_level": 5, "base_cost": 5, "max_level": 10},
    "deep_map": {"name": "Deep Map", "effect": "Rekindle with a floor {} checkpoint", "per_level": 5, "base_cost": 4, "max_level": 4},
    "merchants_scale": {"name": "Merchant's Scale", "effect": "Relic upgrades cost {}% less", "per_level": 3, "base_cost": 4, "max_level": 15},
    "prism_shard": {"name": "Prism Shard", "effect": "+{}% diamonds banked", "per_level": 20, "base_cost": 6, "max_level": None},
    "crown_breaker": {"name": "Crown Breaker", "effect": "+{}% boss damage and boss relics", "per_level": 15, "base_cost": 4, "max_level": None},
    "lodestone": {"name": "Lodestone", "effect": "Pick up relics/diamonds {}px further", "per_level": 8, "base_cost": 3, "max_level": 10},
}

# --- Partner blobs ---
# A new partner role unlocks every PARTNER_UNLOCK_EVERY rekindles, in this order.
# You pick which partner joins you when you rekindle. Partners are spirits: they
# float over walls and can't be hurt.
PARTNER_UNLOCK_EVERY = 5
PARTNER_SPEED = 230  # minimum; partners also keep up with fast players
PARTNER_ROLES = {
    "striker": {"name": "Striker", "color": (255, 150, 80), "description": "Hunts enemies near you and hits them for 40% of your damage."},
    "collector": {"name": "Collector", "color": (246, 190, 76), "description": "Flies to relics and diamonds and grabs them for you."},
    "healer": {"name": "Healer", "color": (255, 140, 190), "description": "Stays close and heals 3% of your max HP every 5 seconds."},
    "guard": {"name": "Guard", "color": (205, 210, 225), "description": "Every 8 seconds, draws nearby enemies to itself for 3 seconds."},
}
PARTNER_STRIKE_DAMAGE = 0.4  # fraction of the player's attack damage
PARTNER_STRIKE_COOLDOWN = 0.6
PARTNER_STRIKE_RANGE = 230  # only chases enemies this close to the player
PARTNER_HEAL_PERCENT = 3
PARTNER_HEAL_INTERVAL = 5.0
PARTNER_TAUNT_INTERVAL = 8.0
PARTNER_TAUNT_DURATION = 3.0
PARTNER_TAUNT_RADIUS = 170

# --- Player combat/visual configuration ---
ATTACK_DURATION = 0.18
ATTACK_COOLDOWN = 0.36

# Every 10 attack-upgrade levels unlocks a new look for the player blob, shown
# both in the lobby preview and during gameplay. Add more entries to extend it.
PLAYER_VISUAL_TIERS = [
    {"name": "Recruit", "outline": None, "aura": None, "spikes": False, "crown": False},
    {"name": "Veteran", "outline": (255, 226, 133), "aura": None, "spikes": False, "crown": False},
    {"name": "Champion", "outline": (255, 226, 133), "aura": (255, 226, 133, 60), "spikes": True, "crown": False},
    {"name": "Ascended", "outline": (255, 255, 255), "aura": (196, 140, 255, 80), "spikes": True, "crown": True},
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

# Every BOSS_FLOOR_INTERVAL-th floor is a boss floor; beating it saves a checkpoint
# so later runs can start on the floor after it.
BOSS_FLOOR_INTERVAL = 5
BOSS_MINION_COUNT = 2
BOSS_RELIC_REWARD = 15  # multiplied by boss number (1 on floor 5, 2 on floor 10...) and relic yield
BOSS = {
    "name": "The Blob King",
    "health": 600,
    "health_per_boss": 450,
    "damage": 18,
    "damage_per_boss": 6,
    "speed": 58,
    "radius": 32,
    "color": (140, 70, 190),
    "charge_interval": 3.2,  # seconds of chasing between charges
    "charge_windup": 0.75,  # flashing tell before a charge
    "charge_duration": 0.55,
    "charge_speed": 360,
}

# Rare diamonds (future transcendence currency) appear once on every Nth floor.
DIAMOND_FLOOR_INTERVAL = 3

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
