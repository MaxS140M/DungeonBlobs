"""Player and Enemy game objects, plus the player's cosmetic visual tiers."""
import math
import random

import pygame

from display import screen
from dungeon import move_with_walls
from settings import (
    ATTACK_COOLDOWN,
    ATTACK_DURATION,
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


def player_visual_tier_index(attack_level):
    return min(attack_level // PLAYER_VISUAL_TIER_STEP, len(PLAYER_VISUAL_TIERS) - 1)


def player_visual_tier(attack_level):
    return PLAYER_VISUAL_TIERS[player_visual_tier_index(attack_level)]


def draw_player_blob(surface, rect, tier, time_now=0.0):
    """Draws the player blob with cosmetics unlocked by the given visual tier."""
    if tier["aura"]:
        aura_radius = max(rect.width, rect.height) // 2 + 10 + int(3 * math.sin(time_now * 4))
        aura_surface = pygame.Surface((aura_radius * 2, aura_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(aura_surface, tier["aura"], (aura_radius, aura_radius), aura_radius)
        surface.blit(aura_surface, aura_surface.get_rect(center=rect.center))
    pygame.draw.ellipse(surface, (9, 12, 20), rect.move(3, 5))
    pygame.draw.rect(surface, tier["body_color"], rect, border_radius=8)
    if tier["outline"]:
        pygame.draw.rect(surface, tier["outline"], rect, width=2, border_radius=8)
    pygame.draw.rect(surface, tier["accent_color"], (rect.x + 7, rect.y + 5, 8, 8), border_radius=4)
    if tier["spikes"]:
        spike_color = tier["outline"] or tier["accent_color"]
        pygame.draw.polygon(surface, spike_color, [(rect.x + 3, rect.y + 2), (rect.x + 9, rect.y - 8), (rect.x + 15, rect.y + 2)])
        pygame.draw.polygon(surface, spike_color, [(rect.right - 15, rect.y + 2), (rect.right - 9, rect.y - 8), (rect.right - 3, rect.y + 2)])
    if tier["crown"]:
        crown_color = COLORS["gold_light"]
        cx, cy = rect.centerx, rect.y - 6
        pygame.draw.polygon(surface, crown_color, [(cx - 10, cy + 4), (cx - 10, cy - 4), (cx - 4, cy), (cx, cy - 8), (cx + 4, cy), (cx + 10, cy - 4), (cx + 10, cy + 4)])


class Player:
    def __init__(self, max_health, attack_damage, move_speed, spawn_tile, attack_level=0):
        self.rect = pygame.Rect(spawn_tile[0] * TILE + 10, spawn_tile[1] * TILE + 10, 28, 28)
        self.max_health = max_health
        self.health = max_health
        self.attack_damage = attack_damage
        self.move_speed = move_speed
        self.attack_level = attack_level
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.invulnerable = 0
        self.facing = pygame.Vector2(1, 0)

    def teleport_to(self, spawn_tile):
        self.rect.topleft = (spawn_tile[0] * TILE + 10, spawn_tile[1] * TILE + 10)

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

    def attack(self):
        if self.attack_cooldown <= 0:
            self.attack_timer = ATTACK_DURATION
            self.attack_cooldown = ATTACK_COOLDOWN

    def attack_rect(self):
        center = pygame.Vector2(self.rect.center) + self.facing * 27
        return pygame.Rect(0, 0, 46, 46).move(center.x - 23, center.y - 23)

    def _draw_attack_swing(self):
        progress = min(1.0, max(0.0, 1 - (self.attack_timer / ATTACK_DURATION)))
        facing_angle = math.atan2(self.facing.y, self.facing.x)
        swing_span = math.radians(110)
        start_angle = facing_angle - swing_span / 2
        current_angle = start_angle + swing_span * progress
        center = pygame.Vector2(self.rect.center)
        blade_length = 34
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

    def draw(self):
        if self.invulnerable and int(self.invulnerable * 16) % 2 == 0:
            return
        tier = player_visual_tier(self.attack_level)
        draw_player_blob(screen, self.rect, tier, time_now=pygame.time.get_ticks() / 1000.0)
        if self.attack_timer:
            self._draw_attack_swing()


class Enemy:
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

    def update(self, player, dt):
        self.hit_flash = max(0, self.hit_flash - dt)
        self.attack_delay = max(0, self.attack_delay - dt)
        offset = pygame.Vector2(player.rect.center) - self.rect.center
        if offset.length_squared() and offset.length() < 270:
            move_with_walls(self, offset.normalize() * self.speed * dt)
        if self.rect.colliderect(player.rect) and self.attack_delay <= 0:
            if player.invulnerable <= 0:
                player.health -= self.damage
                player.invulnerable = 0.8
            self.attack_delay = 0.9

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
