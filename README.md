# Dungeon Blobs - The Lantern Vault

A small endless top-down dungeon crawler made with Pygame.

## To run

**Play:** download `DungeonBlobs.exe` from the
[latest release](https://github.com/MaxS140M/DungeonBlobs/releases/latest) and open it.
Your progress is saved in `save_data.json` next to the exe.

**From the source code:**

```powershell
python -m pip install -r requirements.txt
cd src
python main.py
```

**Build the exe yourself:** `python -m PyInstaller main.spec` (the exe appears in `dist/`).

## Controls

- `WASD` to move
- `Space` or left mouse button to attack
- Defeat every enemy on a floor to go deeper; grab the relics and diamonds on the way
- `Enter` (or `R`) returns to the lobby after a run ends
- `Esc` or the **Leave** button ends a run early (relics and diamonds are still banked); in the lobby `Esc` quits

The lobby, settings, accounts and leaderboard screens all work with the mouse:
click **Buy** to upgrade, **START RUN** to play, and **< Back** to return.
Keyboard shortcuts still work in the lobby: `1`-`6` buy, `Enter` start, `C` checkpoint,
`H` how to play, `S` settings, `A` accounts, `L` leaderboard, `R` rekindle.

The leaderboard ranks your local accounts by highest floor reached or total relics earned.

Diamonds appear once every 3 floors.

## Rekindling

Once you've beaten the floor 25 boss you can **Rekindle**: your relics, relic upgrades
and checkpoint reset, and you gain **Embers** based on the deepest floor you reached
this cycle (more the further past floor 20 you got). Each Ember permanently gives
+2% damage and +2% relics.

Diamonds buy **Heirlooms**, which are never reset:

- **Golden Lens** - more relics banked
- **Amber Heart** - more max HP
- **Bloodstone** - more damage
- **Echo Stone** - keep part of your upgrade levels when you rekindle
- **Deep Map** - start each new cycle with a checkpoint further down
- **Merchant's Scale** - relic upgrades cost less
- **Prism Shard** - more diamonds banked from each run
- **Crown Breaker** - more damage to bosses and more relics from them
- **Lodestone** - pick up relics and diamonds from further away

All the numbers live in `src/core/settings.py` under "Rekindling".

## Partner blobs

A new partner unlocks every 5 rekindles: **Striker** (fights enemies near you),
**Collector** (grabs relics and diamonds), **Healer** (heals you over time) and
**Guard** (draws enemies onto itself). Choose which one joins you each time you
rekindle. Partners float over walls and can't be hurt.

The in-game **How to Play** screen (lobby, or `H`) explains everything above.

## Project layout

```
src/
  main.py      entry point and main game loop
  core/        settings (all tunable numbers), window/display
  game/        dungeon map, player/enemies/boss, wave spawning
  progress/    accounts, permanent upgrades, per-computer settings
  ui/          drawing code, settings and account screens
```
