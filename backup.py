import pygame
import sys
import math

# Konstanten
WIDTH, HEIGHT = 500, 800
BALL_RADIUS = 10
FLIPPER_LENGTH = 200  # Länge der Flipper
FLIPPER_WIDTH = 20
GRAVITY = 0.2
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Initialisierung von Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Kugel Eigenschaften
ball_pos = [WIDTH // 2, HEIGHT // 4]
ball_vel = [0, 2]
ball_acc = [0, GRAVITY]

# Flipper Eigenschaften
left_flipper_angle = 0
right_flipper_angle = 0
left_flipper_pos = [0, HEIGHT - 100]
right_flipper_pos = [WIDTH, HEIGHT - 100]

def move_ball():
    # Bewegt die Kugel basierend auf ihrer Geschwindigkeit und Beschleunigung
    ball_vel[0] += ball_acc[0]
    ball_vel[1] += ball_acc[1]
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Kollision mit den Wänden
    if ball_pos[0] <= BALL_RADIUS or ball_pos[0] >= WIDTH - BALL_RADIUS:
        ball_vel[0] = -ball_vel[0]
    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]

def draw_ball():
    # Zeichnet die Kugel auf dem Bildschirm
    pygame.draw.circle(screen, WHITE, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

def draw_flipper(position, angle, is_right):
    # Zeichnet einen Flipper, berücksichtigt die Seite für den Pivot
    if is_right:
        start_pos = (
            position[0] - FLIPPER_LENGTH * math.cos(math.radians(angle)),
            position[1] + FLIPPER_LENGTH * math.sin(math.radians(angle))
        )
        end_pos = position
    else:
        start_pos = position
        end_pos = (
            position[0] + FLIPPER_LENGTH * math.cos(math.radians(angle)),
            position[1] - FLIPPER_LENGTH * math.sin(math.radians(angle))
        )
    pygame.draw.line(screen, WHITE, start_pos, end_pos, FLIPPER_WIDTH)

def handle_keys():
    global left_flipper_angle, right_flipper_angle
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        left_flipper_angle = 30
    else:
        left_flipper_angle = 0
    if keys[pygame.K_d]:
        right_flipper_angle = -30
    else:
        right_flipper_angle = 0

def game_loop():
    while True:
        for event in pygame.event.get():
            if event.type is pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill(BLACK)  # Hintergrund

        move_ball()  # Bewegt die Kugel
        draw_ball()  # Zeichnet die Kugel
        handle_keys()  # Tastenbehandlung für Flipper
        draw_flipper(left_flipper_pos, left_flipper_angle, False)
        draw_flipper(right_flipper_pos, right_flipper_angle, True)

        pygame.display.flip()  # Aktualisiert den gesamten Bildschirm
        clock.tick(60)  # Framerate

if __name__ == '__main__':
    game_loop()
