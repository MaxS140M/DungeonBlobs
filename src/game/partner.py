"""Partner blobs: computer-controlled spirit allies unlocked through rekindling.
They float over walls (so they can never get stuck) and can't be hurt."""
import math

import pygame

from core import audio
from core.display import screen
from core.settings import (
    COLORS,
    MAP_HEIGHT,
    MAP_WIDTH,
    PARTNER_HEAL_INTERVAL,
    PARTNER_HEAL_PERCENT,
    PARTNER_ROLES,
    PARTNER_SPEED,
    PARTNER_STRIKE_COOLDOWN,
    PARTNER_STRIKE_DAMAGE,
    PARTNER_STRIKE_RANGE,
    PARTNER_TAUNT_DURATION,
    PARTNER_TAUNT_INTERVAL,
    PARTNER_TAUNT_RADIUS,
    TILE,
)

MAP_BOUNDS = pygame.Rect(TILE, TILE, (MAP_WIDTH - 2) * TILE, (MAP_HEIGHT - 2) * TILE)  # inside the border walls


# Distance between two rect centres.
def distance(rect_a, rect_b):
    return math.dist(rect_a.center, rect_b.center)


class Partner:
    # Creates a partner of the given role (a PARTNER_ROLES key) next to the player.
    def __init__(self, role, player):
        self.role = role
        self.name = PARTNER_ROLES[role]["name"]
        self.color = PARTNER_ROLES[role]["color"]
        self.rect = pygame.Rect(0, 0, 20, 20)
        self.role_timer = 0.0  # counts up to the next heal / taunt
        self.strike_cooldown = 0.0
        self.taunting = 0.0  # seconds of taunt left (Guard)
        self.pulse = 0.0  # seconds left on the heal/taunt ring effect
        self.teleport_to(player)

    # Puts the partner right next to the player (start of each floor).
    def teleport_to(self, player):
        self.rect.center = player.rect.center

    # Where the partner wants to be this frame; depends on its role.
    def _target(self, run):
        player = run["player"]
        if self.role == "striker":
            nearby = [enemy for enemy in run["enemies"] if distance(enemy.rect, player.rect) < PARTNER_STRIKE_RANGE]
            if nearby:
                return min(nearby, key=lambda enemy: distance(enemy.rect, self.rect)).rect.center
        elif self.role == "collector":
            pickups = run["relics"] + run["diamonds"]
            if pickups:
                return min(pickups, key=lambda pickup: distance(pickup, self.rect)).center
        elif self.role == "guard":
            # Stands in front of the player so taunted enemies bunch up where you swing.
            return pygame.Vector2(player.rect.center) + player.facing * 55
        return pygame.Vector2(player.rect.center) - player.facing * 34  # follow just behind

    # Moves towards its target and applies its role's effect.
    def update(self, run, progression, dt):
        player = run["player"]
        self.strike_cooldown = max(0.0, self.strike_cooldown - dt)
        self.taunting = max(0.0, self.taunting - dt)
        self.pulse = max(0.0, self.pulse - dt)

        offset = pygame.Vector2(self._target(run)) - self.rect.center
        step = max(PARTNER_SPEED, player.move_speed * 1.15) * dt
        if offset.length() > step:
            offset.scale_to_length(step)
        self.rect.center = (round(self.rect.centerx + offset.x), round(self.rect.centery + offset.y))
        self.rect.clamp_ip(MAP_BOUNDS)

        if self.role == "striker":
            self._strike(run)
        elif self.role == "collector":
            self._collect(run, progression)
        elif self.role == "healer":
            self.role_timer += dt
            if self.role_timer >= PARTNER_HEAL_INTERVAL:
                self.role_timer = 0.0
                if player.health < player.max_health:
                    player.heal_percent(PARTNER_HEAL_PERCENT)
                    self.pulse = 0.5
        elif self.role == "guard":
            self.role_timer += dt
            if self.role_timer >= PARTNER_TAUNT_INTERVAL:
                self.role_timer = 0.0
                self.taunting = PARTNER_TAUNT_DURATION

    # Striker: hits an enemy it is touching (dead enemies are removed by the main loop).
    def _strike(self, run):
        if self.strike_cooldown > 0:
            return
        for enemy in run["enemies"]:
            if self.rect.colliderect(enemy.rect):
                enemy.health -= run["player"].attack_damage * PARTNER_STRIKE_DAMAGE
                enemy.hit_flash = 0.12
                self.strike_cooldown = PARTNER_STRIKE_COOLDOWN
                return

    # Collector: picks up any relic or diamond it touches.
    def _collect(self, run, progression):
        relics = [relic for relic in run["relics"] if self.rect.colliderect(relic)]
        diamonds = [diamond for diamond in run["diamonds"] if self.rect.colliderect(diamond)]
        for relic in relics:
            run["relics"].remove(relic)
            run["run_relics"] += progression.relic_yield
        for diamond in diamonds:
            run["diamonds"].remove(diamond)
            run["run_diamonds"] += 1
        if relics or diamonds:
            audio.play("coin")

    # Guard: while taunting, nearby enemies chase the partner instead of the player.
    # Returns the rect the enemy should chase, or None to chase the player as normal.
    def taunt_target(self, enemy):
        if self.taunting > 0 and distance(enemy.rect, self.rect) < PARTNER_TAUNT_RADIUS:
            return self.rect
        return None

    # Draws a small glowing blob in the role's colour, plus a ring while healing/taunting.
    def draw(self):
        bob = round(2 * math.sin(pygame.time.get_ticks() / 180))
        body = self.rect.move(0, bob)
        glow = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 50), (20, 20), 19)
        screen.blit(glow, glow.get_rect(center=body.center))
        pygame.draw.rect(screen, self.color, body, border_radius=7)
        pygame.draw.rect(screen, COLORS["background"], (body.x + 5, body.y + 5, 4, 4), border_radius=2)
        pygame.draw.rect(screen, COLORS["background"], (body.right - 9, body.y + 5, 4, 4), border_radius=2)
        if self.taunting > 0:
            radius = 24 + round(4 * math.sin(pygame.time.get_ticks() / 90))
            pygame.draw.circle(screen, self.color, body.center, radius, 2)
        if self.pulse > 0:
            pygame.draw.circle(screen, self.color, body.center, round(18 + (0.5 - self.pulse) * 80), 2)
