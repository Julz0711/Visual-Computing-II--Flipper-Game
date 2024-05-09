import pygame

# Konstanten
WIDTH, HEIGHT = 500, 800
BALL_RADIUS = 15
FLIPPER_LENGTH = 200  # Länge der Flipper
FLIPPER_WIDTH = 30
BUMPER_RADIUS = 25
GRAVITY = 0.2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GAME_STARTED = False

window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()