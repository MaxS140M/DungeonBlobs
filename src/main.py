"""Entry point"""
import random
import sys

import pygame

import dungeon
from display import clock
from progression import (
    load_progression,
    save_progression,
    try_buy_attack,
    try_buy_health,
    try_buy_relic_yield,
    try_buy_speed,
)
from rendering import draw_dungeon, draw_floor_banner, draw_hud, draw_lobby, draw_relic, overlay
from settings import COLORS, DUNGEON_LAYOUTS, FPS
from waves import build_wave, start_run


def main():
    progression = load_progression()
    state = "lobby"
    run = None
    lobby_message = ""
    lobby_message_color = COLORS["muted"]
    lobby_message_timer = 0.0
    death_summary = None

    while True:
        dt = min(clock.tick(FPS) / 1000, 0.05)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if state == "lobby":
                    purchased = None
                    if event.key == pygame.K_1:
                        purchased, lobby_message = try_buy_health(progression)
                    elif event.key == pygame.K_2:
                        purchased, lobby_message = try_buy_attack(progression)
                    elif event.key == pygame.K_3:
                        purchased, lobby_message = try_buy_relic_yield(progression)
                    elif event.key == pygame.K_4:
                        purchased, lobby_message = try_buy_speed(progression)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        run = start_run(progression)
                        state = "playing"
                    if purchased is not None:
                        lobby_message_color = COLORS["exit"] if purchased else COLORS["danger"]
                        lobby_message_timer = 2.4
                elif state == "playing":
                    if event.key == pygame.K_SPACE:
                        run["player"].attack()
                elif state == "dead":
                    if event.key in (pygame.K_RETURN, pygame.K_r):
                        state = "lobby"
                        death_summary = None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and state == "playing":
                run["player"].attack()

        if state == "playing":
            run["elapsed"] += dt
            run["floor_banner"] = max(0.0, run["floor_banner"] - dt)
            player = run["player"]
            player.update(dt)
            for enemy in run["enemies"]:
                enemy.update(player, dt)

            if player.attack_timer:
                strike = player.attack_rect()
                for enemy in run["enemies"][:]:
                    if strike.colliderect(enemy.rect):
                        enemy.health -= player.attack_damage
                        enemy.hit_flash = 0.12
                        knockback = pygame.Vector2(enemy.rect.center) - player.rect.center
                        if knockback.length_squared():
                            dungeon.move_with_walls(enemy, knockback.normalize() * 15)
                        if enemy.health <= 0:
                            run["enemies"].remove(enemy)

            collected = [relic for relic in run["relics"] if player.rect.colliderect(relic)]
            if collected:
                run["relics"] = [relic for relic in run["relics"] if relic not in collected]
                run["run_relics"] += progression.relic_yield * len(collected)

            if not run["enemies"]:
                run["floor"] += 1
                layout = random.choice(DUNGEON_LAYOUTS)
                dungeon.set_current_dungeon(layout)
                spawn = layout["spawn"]
                player.teleport_to(spawn)
                run["enemies"], run["relics"] = build_wave(run["floor"], spawn)
                run["dungeon_name"] = layout["name"]
                run["floor_banner"] = 2.0

            if player.health <= 0:
                progression.relics += run["run_relics"]
                save_progression(progression)
                death_summary = {"floor": run["floor"], "relics": run["run_relics"]}
                state = "dead"

        if state == "lobby":
            lobby_message_timer = max(0.0, lobby_message_timer - dt)
            draw_lobby(progression, lobby_message if lobby_message_timer > 0 else "", lobby_message_color)
        else:
            draw_dungeon()
            for relic in run["relics"]:
                draw_relic(relic)
            for enemy in run["enemies"]:
                enemy.draw()
            run["player"].draw()
            draw_hud(run["player"], run["run_relics"], run["floor"])
            if run["floor_banner"] > 0:
                draw_floor_banner(run["floor"], run["dungeon_name"])
            if state == "dead":
                overlay(
                    "YOU FELL",
                    f"Floor {death_summary['floor']} reached - {death_summary['relics']} relics banked to your stash",
                    COLORS["danger"],
                    "Press ENTER to return to the lobby",
                )

        pygame.display.flip()


if __name__ == "__main__":
    main()

