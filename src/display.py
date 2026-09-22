import pygame

from settings import WIDTH, HEIGHT

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Lantern Vault")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 25)
small_font = pygame.font.Font(None, 19)
large_font = pygame.font.Font(None, 64)
