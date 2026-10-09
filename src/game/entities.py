"""Player, Enemy and Boss game objects, plus the player's cosmetic visual tiers."""
import math
import random

import pygame

from core.display import screen
from game.dungeon import move_with_walls
from core.settings import (
    ATTACK_COOLDOWN,
    ATTACK_DURATION,
    BOSS,
    BOSS_FLOOR_INTERVAL,
    COLORS,
    ENEMY_DAMAGE_PER_FLOOR,
    ENEMY_HEALTH_PER_FLOOR,
    ENEMY_SPEED_CAP_MULTIPLIER,
    ENEMY_SPEED_PER_FLOOR,
    ENEMY_TYPES,
    PLAYER_VISUAL_TIER_STEP,
    PLAYER_VISUAL_TIERS,
    TILE,
)


# Returns which visual tier the player has reached for an attack level.
def player_visual_tier_index(attack_level):
    return min(attack_level // PLAYER_VISUAL_TIER_STEP, len(PLAYER_VISUAL_TIERS) - 1)


# Returns the visual tier data (colours, aura, crown...) for an attack level.
def player_visual_tier(attack_level):
    return PLAYER_VISUAL_TIERS[player_visual_tier_index(attack_level)]


# Draws a small gold crown centred on (cx, cy).
def draw_crown(surface, cx, cy):
    pygame.draw.polygon(surface, COLORS["gold_light"], [(cx - 10, cy + 4), (cx - 10, cy - 4), (cx - 4, cy), (cx, cy - 8), (cx + 4, cy), (cx + 10, cy - 4), (cx + 10, cy + 4)])


# Draws two eyes and a smile on the player blob, scaled to its size (gameplay and lobby preview).
def draw_smiley(surface, rect):
    face = COLORS["player_face"]
    eye_radius = max(2, rect.width // 12)
    eye_y = rect.y + rect.height * 0.38
    for eye_x in (rect.centerx - rect.width * 0.2, rect.centerx + rect.width * 0.2):
        pygame.draw.circle(surface, face, (round(eye_x), round(eye_y)), eye_radius)
    mouth = pygame.Rect(0, 0, round(rect.width * 0.5), round(rect.height * 0.36))
    mouth.center = (rect.centerx, round(rect.y + rect.height * 0.52))
    pygame.draw.arc(surface, face, mouth, math.pi + 0.35, 2 * math.pi - 0.35, max(2, rect.width // 14))


# Draws the player blob with the cosmetics unlocked by the given visual tier.
def draw_player_blob(surface, rect, tier, time_now=0.0):
    if tier["aura"]:
        aura_radius = max(rect.width, rect.height) // 2 + 10 + int(3 * math.sin(time_now * 4))
        aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surface, tier["aura"], (aura_radius, aura_radius), aura_radius)
        surface.blit(aura_surface, aura_surface.get_rect(center=rect.center))
    pygame.draw.ellipse(surface, (9, 12, 20), rect.move(3, 5))
    pygame.draw.rect(surface, COLORS["player"], rect, border_radius=8)
    if tier["outline"]:
        pygame.draw.rect(surface, tier["outline"], rect, width=2, border_radius=8)
    draw_smiley(surface, rect)
    if tier["spikes"]:
        spike_color = tier["outline"]
        pygame.draw.polygon(surface, spike_color, [(rect.x + 3, rect.y + 2), (rect.x + 9, rect.y - 8), (rect.x + 15, rect.y + 2)])
        pygame.draw.polygon(surface, spike_color, [(rect.right - 15, rect.y + 2), (rect.right - 9, rect.y - 8), (rect.right - 3, rect.y + 2)])
    if tier["crown"]:
        draw_crown(surface, rect.centerx, rect.y - 6)


class Player:
    # Creates the player on a spawn tile with stats from permanent upgrades.
    def __init__(self, max_health, attack_damage, move_speed, spawn_tile, attack_level=0, attack_reach=1.0):
        self.rect = pygame.Rect(spawn_tile[0] * TILE + 10, spawn_tile[1] * TILE + 10, 28, 28)
        self.max_health = max_health
        self.health = max_health
        self.attack_damage = attack_damage
        self.move_speed = move_speed
        self.attack_level = attack_level
        self.attack_reach = attack_reach  # multiplies swing hitbox and blade size
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.invulnerable = 0
        self.facing = pygame.Vector2(1, 0)

    # Restores a percentage of max HP (Healing Herb upgrade), never above max.
    def heal_percent(self, percent):
        self.health = min(self.max_health, self.health + math.ceil(self.max_health * percent / 100))

    # Moves the player onto a spawn tile (used when entering a new floor).
    def teleport_to(self, spawn_tile):
        self.rect.topleft = (spawn_tile[0] * TILE + 10, spawn_tile[1] * TILE + 10)

    # Reads WASD movement and counts down attack and invulnerability timers.
    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(
            keys[pygame.K_d] - keys[pygame.K_a],
            keys[pygame.K_s] - keys[pygame.K_w],
        )
        if direction.length_squared():
            direction = direction.normalize()
            self.facing = direction
            move_with_walls(self, direction * self.move_speed * dt)
        self.attack_timer = max(0, self.attack_timer - dt)
        self.attack_cooldown = max(0, self.attack_cooldown - dt)
        self.invulnerable = max(0, self.invulnerable - dt)

    # Starts a sword swing if the attack cooldown has finished.
    def attack(self):
        if self.attack_cooldown <= 0:
            self.attack_timer = ATTACK_DURATION
            self.attack_cooldown = ATTACK_COOLDOWN

    # Returns the hitbox of the current swing, in front of where the player faces.
    def attack_rect(self):
        size = round(46 * self.attack_reach)
        center = pygame.Vector2(self.rect.center) + self.facing * 27 * self.attack_reach
        return pygame.Rect(0, 0, size, size).move(center.x - size / 2, center.y - size / 2)

    # Draws the sword arc with a fading trail.
    def _draw_attack_swing(self):
        progress = min(1.0, max(0.0, 1 - (self.attack_timer / ATTACK_DURATION)))
        facing_angle = math.atan2(self.facing.y, self.facing.x)
        swing_span = math.radians(110)
        start_angle = facing_angle - swing_span / 2
        current_angle = start_angle + swing_span * progress
        center = pygame.Vector2(self.rect.center)
        blade_length = 34 * self.attack_reach
        for step in range(3, 0, -1):
            trail_progress = progress - step * 0.08
            if trail_progress <= 0:
                continue
            trail_angle = start_angle + swing_span * trail_progress
            fade = (4 - step) / 4
            color = tuple(int(channel * fade) for channel in COLORS["gold_light"])
            tip = center + pygame.Vector2(math.cos(trail_angle), math.sin(trail_angle)) * blade_length
            pygame.draw.line(screen, color, center, tip, 3)
        tip = center + pygame.Vector2(math.cos(current_angle), math.sin(current_angle)) * blade_length
        pygame.draw.line(screen, COLORS["gold_light"], center, tip, 4)
        pygame.draw.circle(screen, COLORS["gold_light"], (int(tip.x), int(tip.y)), 5)

    # Draws the player (blinking while invulnerable) and any active swing.
    def draw(self):
        if self.invulnerable and int(self.invulnerable * 16) % 2 == 0:
            return
        tier = player_visual_tier(self.attack_level)
        draw_player_blob(screen, self.rect, tier, time_now=pygame.time.get_ticks() / 1000.0)
        if self.attack_timer:
            self._draw_attack_swing()


class Enemy:
    knockback = 1.0  # multiplier on how far a hit pushes this enemy back

    # Creates an enemy of the given kind with stats scaled to the floor number.
    def __init__(self, x, y, kind, floor):
        stats = ENEMY_TYPES[kind]
        self.kind = kind
        self.radius = stats["radius"]
        size = self.radius * 2
        self.rect = pygame.Rect(x * TILE + (TILE - size) // 2, y * TILE + (TILE - size) // 2, size, size)
        self.max_health = stats["health"] + (floor - 1) * ENEMY_HEALTH_PER_FLOOR
        self.health = self.max_health
        self.damage = stats["damage"] + ((floor - 1) // 2) * ENEMY_DAMAGE_PER_FLOOR
        base_speed = stats["speed"] + (floor - 1) * ENEMY_SPEED_PER_FLOOR
        self.speed = min(base_speed, stats["speed"] * ENEMY_SPEED_CAP_MULTIPLIER)
        self.color = stats["color"]
        self.hit_flash = 0
        self.attack_delay = random.uniform(0, 0.6)

    # Chases the player (or chase_rect, e.g. a taunting Guard) when close enough, then tries to hit the player.
    def update(self, player, dt, chase_rect=None):
        self.hit_flash = max(0, self.hit_flash - dt)
        self.attack_delay = max(0, self.attack_delay - dt)
        offset = pygame.Vector2((chase_rect or player.rect).center) - self.rect.center
        if offset.length_squared() and offset.length() < 270:
            move_with_walls(self, offset.normalize() * self.speed * dt)
        self.touch_player(player)

    # Damages the player on contact, respecting attack delay and invulnerability.
    def touch_player(self, player):
        if self.rect.colliderect(player.rect) and self.attack_delay <= 0:
            if player.invulnerable <= 0:
                player.health -= self.damage
                player.invulnerable = 0.8
            self.attack_delay = 0.9

    # Draws the enemy body, eyes and (once damaged) a health bar.
    def draw(self):
        color = COLORS["gold_light"] if self.hit_flash else self.color
        pygame.draw.ellipse(screen, (9, 12, 20), self.rect.move(2, 4))
        pygame.draw.circle(screen, color, self.rect.center, self.radius)
        pygame.draw.circle(screen, COLORS["enemy_dark"], (self.rect.centerx - self.radius // 2, self.rect.centery - 2), 3)
        pygame.draw.circle(screen, COLORS["enemy_dark"], (self.rect.centerx + self.radius // 2, self.rect.centery - 2), 3)
        if self.health < self.max_health:
            bar_width = self.radius * 2
            bar_x = self.rect.centerx - self.radius
            bar_y = self.rect.top - 10
            pygame.draw.rect(screen, (40, 20, 24), (bar_x, bar_y, bar_width, 4))
            ratio = max(0, self.health) / self.max_health
            pygame.draw.rect(screen, COLORS["danger"], (bar_x, bar_y, int(bar_width * ratio), 4))


class Boss(Enemy):
    """Appears every BOSS_FLOOR_INTERVAL floors. Immune to knockback; chases the
    player, then periodically flashes (wind-up) and charges in a straight line."""
    knockback = 0.0

    # Creates the boss with health and damage scaled by how many bosses came before it.
    def __init__(self, x, y, floor):
        self.name = BOSS["name"]
        self.boss_number = floor // BOSS_FLOOR_INTERVAL
        self.radius = BOSS["radius"]
        size = self.radius * 2
        self.rect = pygame.Rect(x * TILE + (TILE - size) // 2, y * TILE + (TILE - size) // 2, size, size)
        self.max_health = BOSS["health"] + (self.boss_number - 1) * BOSS["health_per_boss"]
        self.health = self.max_health
        self.damage = BOSS["damage"] + (self.boss_number - 1) * BOSS["damage_per_boss"]
        self.speed = BOSS["speed"]
        self.color = BOSS["color"]
        self.hit_flash = 0
        self.attack_delay = 0.6
        self.mode = "chase"
        self.mode_timer = BOSS["charge_interval"]
        self.charge_direction = pygame.Vector2(1, 0)

    # Runs the chase -> wind-up -> charge cycle, then tries to hit the player.
    def update(self, player, dt, chase_rect=None):
        self.hit_flash = max(0, self.hit_flash - dt)
        self.attack_delay = max(0, self.attack_delay - dt)
        self.mode_timer -= dt
        to_player = pygame.Vector2((chase_rect or player.rect).center) - self.rect.center
        if self.mode == "chase":
            if to_player.length_squared():
                move_with_walls(self, to_player.normalize() * self.speed * dt)
            if self.mode_timer <= 0:
                self.mode, self.mode_timer = "windup", BOSS["charge_windup"]
        elif self.mode == "windup":
            if self.mode_timer <= 0:
                if to_player.length_squared():
                    self.charge_direction = to_player.normalize()
                self.mode, self.mode_timer = "charge", BOSS["charge_duration"]
        else:
            before = self.rect.topleft
            move_with_walls(self, self.charge_direction * BOSS["charge_speed"] * dt)
            if self.mode_timer <= 0 or self.rect.topleft == before:  # charge ends early on hitting a wall
                self.mode, self.mode_timer = "chase", BOSS["charge_interval"]
        self.touch_player(player)

    # Draws the boss, flashing during its wind-up so the player can dodge the charge.
    def draw(self):
        winding_up = self.mode == "windup" and int(self.mode_timer * 12) % 2 == 0
        color = COLORS["gold_light"] if self.hit_flash or winding_up else self.color
        pygame.draw.ellipse(screen, (9, 12, 20), self.rect.move(3, 6))
        pygame.draw.circle(screen, color, self.rect.center, self.radius)
        pygame.draw.circle(screen, COLORS["enemy_dark"], self.rect.center, self.radius, 3)
        eye_y = self.rect.centery - 4
        for eye_x in (self.rect.centerx - self.radius // 3, self.rect.centerx + self.radius // 3):
            pygame.draw.circle(screen, COLORS["enemy_dark"], (eye_x, eye_y), 5)
        draw_crown(screen, self.rect.centerx, self.rect.top - 2)
