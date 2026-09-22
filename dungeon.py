import pygame

from settings import DUNGEON_LAYOUTS, MAP_HEIGHT, MAP_WIDTH, TILE

CURRENT_DUNGEON = None
CURRENT_OPEN_TILES = None


def reachable_tiles(grid, spawn):
    """Flood-fills from spawn so relics/enemies never land in an unreachable pocket."""
    width, height = len(grid[0]), len(grid)
    visited = {spawn}
    stack = [spawn]
    while stack:
        x, y = stack.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and grid[ny][nx] != "#" and (nx, ny) not in visited:
                visited.add((nx, ny))
                stack.append((nx, ny))
    return sorted(visited)


def set_current_dungeon(layout):
    global CURRENT_DUNGEON, CURRENT_OPEN_TILES
    CURRENT_DUNGEON = layout["grid"]
    CURRENT_OPEN_TILES = reachable_tiles(CURRENT_DUNGEON, layout["spawn"])


set_current_dungeon(DUNGEON_LAYOUTS[0])


def tile_rect(x, y):
    return pygame.Rect(x * TILE, y * TILE, TILE, TILE)


def is_wall_at(rect):
    left = max(0, rect.left // TILE)
    right = min(MAP_WIDTH - 1, rect.right // TILE)
    top = max(0, rect.top // TILE)
    bottom = min(MAP_HEIGHT - 1, rect.bottom // TILE)
    for grid_y in range(top, bottom + 1):
        for grid_x in range(left, right + 1):
            if CURRENT_DUNGEON[grid_y][grid_x] == "#" and rect.colliderect(tile_rect(grid_x, grid_y)):
                return True
    return False


def move_with_walls(entity, movement):
    entity.rect.x += round(movement.x)
    if is_wall_at(entity.rect):
        entity.rect.x -= round(movement.x)
    entity.rect.y += round(movement.y)
    if is_wall_at(entity.rect):
        entity.rect.y -= round(movement.y)
