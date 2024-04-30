import pygame
import sys
import math

# Initialisierung von Pygame
pygame.init()

# Fenstergröße
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flipper Game")

# Farben
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Ball
ball_radius = 20
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_speed_x, ball_speed_y = 5, 5

# Schläger-Parameter
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
PADDLE_COLOR = (0, 255, 0)
PADDLE_SPEED = 5

# Schläger-Initialisierung
paddle_left = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2 - 40, HEIGHT - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle_right = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2 + 40, HEIGHT - PADDLE_HEIGHT, PADDLE_WIDTH, PADDLE_HEIGHT)

# Schläger-Status
left_paddle_active = False
right_paddle_active = False

# Winkel für die Paddelrotation (30 Grad in Bogenmaß)
paddle_rotation_angle = math.radians(30)

# Haupt-Game-Loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Schläger-Bewegung
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            left_paddle_active = True
        if keys[pygame.K_d]:
            right_paddle_active = True

    # Bewegung des Balls
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Kollision mit den Wänden
    if ball_x <= 0 or ball_x >= WIDTH:
        ball_speed_x *= -1
    if ball_y <= 0 or ball_y >= HEIGHT:
        ball_speed_y *= -1

    # Kollision mit den Schlägern
    if left_paddle_active and ball.colliderect(paddle_left):
        ball_speed_y *= -1
    if right_paddle_active and ball.colliderect(paddle_right):
        ball_speed_y *= -1

    # Paddelrotation
    paddle_left.centerx += PADDLE_SPEED * math.cos(paddle_rotation_angle)
    paddle_left.centery += PADDLE_SPEED * math.sin(paddle_rotation_angle)
    paddle_right.centerx += PADDLE_SPEED * math.cos(paddle_rotation_angle)
    paddle_right.centery += PADDLE_SPEED * math.sin(paddle_rotation_angle)

    # Zeichnen
    screen.fill(BLACK)
    pygame.draw.circle(screen, WHITE, (ball_x, ball_y), ball_radius)
    pygame.draw.rect(screen, PADDLE_COLOR, paddle_left)
    pygame.draw.rect(screen, PADDLE_COLOR, paddle_right)
    pygame.display.flip()

    # Begrenzung der Framerate
    pygame.time.Clock().tick(60)
