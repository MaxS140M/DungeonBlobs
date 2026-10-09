"""Entry point"""
import sys

import pygame

from core import audio
from core.display import clock, present
from core.numbers import format_number, scale
from core.settings import BOSS_RELIC_REWARD, COLORS, FPS
from game import dungeon
from game.entities import Boss
from game.waves import enter_floor, is_boss_floor, start_run
from progress.accounts import Accounts
from progress.user_settings import load_user_settings
from ui.buttons import Button
from ui.guide import GuideMenu
from ui.leaderboard import LeaderboardMenu
from ui.lobby import Lobby
from ui.menus import AccountMenu, SettingsMenu
from ui.rekindle_menu import RekindleMenu
from ui.rendering import draw_boss_bar, draw_diamond, draw_dungeon, draw_floor_banner, draw_hud, draw_relic, draw_toast, overlay


# Awards the boss relic bonus and permanently saves the checkpoint floor.
def defeat_boss(run, accounts, boss):
    progression = accounts.progression
    crown_breaker = 1 + progression.heirloom_bonus("crown_breaker") / 100
    reward = scale(BOSS_RELIC_REWARD * boss.boss_number * progression.relic_yield, crown_breaker)
    run["run_relics"] += reward
    progression.checkpoint_floor = max(progression.checkpoint_floor, run["floor"])
    accounts.save()  # the checkpoint is kept even though relics are only banked on death
    run["toast"] = f"BOSS DEFEATED!  +{format_number(reward)} relics  -  checkpoint: floor {run['floor'] + 1}"
    run["toast_timer"] = 3.5


# Ends the run (death or leaving): banks relics/diamonds, saves, and returns the summary to show.
def end_run(run, accounts, title):
    banked_relics, banked_diamonds = accounts.progression.record_run(run["floor"], run["run_relics"], run["run_diamonds"])
    accounts.save()
    return {"title": title, "floor": run["floor"], "relics": banked_relics, "diamonds": banked_diamonds}


# Main game loop: handles input, updates the current state and draws each frame.
def main():
    accounts = Accounts.load()
    user_settings = load_user_settings()
    audio.set_volumes(user_settings["music_volume"], user_settings["sfx_volume"])
    audio.start_music()
    lobby = Lobby(accounts)
    menus = {
        "settings": SettingsMenu(),
        "accounts": AccountMenu(accounts),
        "leaderboard": LeaderboardMenu(accounts),
        "rekindle": RekindleMenu(accounts),
        "guide": GuideMenu(),
    }
    leave_button = Button(872, 12, 80, 34, "Leave")  # in the strip right of the map
    state = "lobby"
    run = None
    death_summary = None

    while True:
        dt = min(clock.tick(FPS) / 1000, 0.05)
        progression = accounts.progression
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if state in menus:
                if menus[state].handle_event(event):
                    state = "lobby"
                continue
            if state == "lobby":
                action = lobby.handle_event(event)
                if action == "quit":
                    pygame.quit()
                    sys.exit()
                elif action == "start":
                    audio.play("start")
                    run = start_run(accounts.progression, lobby.start_floor())
                    state = "playing"
                elif action:
                    menus[action].open()
                    state = action
                continue
            clicked = event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            escape = event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
            if state == "playing" and (leave_button.is_clicked(event) or escape):
                # Leaving counts the same as falling: the run's relics and diamonds are banked.
                death_summary = end_run(run, accounts, "YOU LEFT")
                state = "dead"
            elif escape:
                pygame.quit()
                sys.exit()
            elif state == "playing" and (clicked or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)):
                run["player"].attack()
            # Death screen is keyboard-only so a frantic attack click doesn't skip the summary.
            elif state == "dead" and event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_r):
                state = "lobby"
                death_summary = None

        if state == "playing":
            run["elapsed"] += dt
            run["floor_banner"] = max(0.0, run["floor_banner"] - dt)
            run["toast_timer"] = max(0.0, run["toast_timer"] - dt)
            player = run["player"]
            player.update(dt)
            partner = run["partner"]
            if partner:
                partner.update(run, progression, dt)
            for enemy in run["enemies"]:
                enemy.update(player, dt, partner.taunt_target(enemy) if partner else None)

            if player.attack_timer:
                strike = player.attack_rect()
                for enemy in run["enemies"]:
                    if strike.colliderect(enemy.rect):
                        damage = player.attack_damage
                        if isinstance(enemy, Boss):
                            damage *= 1 + progression.heirloom_bonus("crown_breaker") / 100
                        enemy.health -= damage
                        enemy.hit_flash = 0.12
                        knockback = pygame.Vector2(enemy.rect.center) - player.rect.center
                        if knockback.length_squared() and enemy.knockback:
                            dungeon.move_with_walls(enemy, knockback.normalize() * 15 * enemy.knockback)

            # Remove everything killed this frame, by the player or the partner.
            for enemy in [enemy for enemy in run["enemies"] if enemy.health <= 0]:
                run["enemies"].remove(enemy)
                if isinstance(enemy, Boss):
                    defeat_boss(run, accounts, enemy)

            magnet = progression.heirloom_bonus("lodestone")  # extra pickup range in pixels
            pickup_area = player.rect.inflate(magnet * 2, magnet * 2)
            collected = [relic for relic in run["relics"] if pickup_area.colliderect(relic)]
            if collected:
                run["relics"] = [relic for relic in run["relics"] if relic not in collected]
                run["run_relics"] += progression.relic_yield * len(collected)

            found = [diamond for diamond in run["diamonds"] if pickup_area.colliderect(diamond)]
            if found:
                run["diamonds"] = [diamond for diamond in run["diamonds"] if diamond not in found]
                run["run_diamonds"] += len(found)
            if collected or found:
                audio.play("coin")

            if not run["enemies"] and player.health > 0:
                player.heal_percent(progression.floor_heal_percent)
                enter_floor(run, run["floor"] + 1)

            if player.health <= 0:
                death_summary = end_run(run, accounts, "YOU FELL")
                state = "dead"

        if state == "lobby":
            lobby.update(dt)
            lobby.draw()
        elif state in menus:
            menus[state].draw()
        else:
            draw_dungeon()
            for relic in run["relics"]:
                draw_relic(relic)
            for diamond in run["diamonds"]:
                draw_diamond(diamond)
            for enemy in run["enemies"]:
                enemy.draw()
            if run["partner"]:
                run["partner"].draw()
            run["player"].draw()
            draw_hud(run["player"], run["run_relics"], run["run_diamonds"], run["floor"])
            boss = next((enemy for enemy in run["enemies"] if isinstance(enemy, Boss)), None)
            if boss:
                draw_boss_bar(boss)
            if run["floor_banner"] > 0:
                draw_floor_banner(run["floor"], run["dungeon_name"], is_boss_floor(run["floor"]))
            if run["toast_timer"] > 0:
                draw_toast(run["toast"])
            if state == "playing":
                leave_button.draw()
            if state == "dead":
                overlay(
                    death_summary["title"],
                    f"Floor {death_summary['floor']} reached - {format_number(death_summary['relics'])} relics and {format_number(death_summary['diamonds'])} diamonds banked",
                    COLORS["danger"],
                    "Press ENTER to return to the lobby",
                )

        present()


if __name__ == "__main__":
    main()
