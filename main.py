import pygame
import sys
import random
import math
from pygame.locals import *

# Konstanten definieren
WINDOW_WIDTH, WINDOW_HEIGHT = 500, 800
BALL_INITIAL_SPEED = 5  # Geschwindigkeit des Balls beim Start
BALL_DIAMETER = 20
BALL_RADIUS = BALL_DIAMETER // 2
FLIPPER_WIDTH, FLIPPER_HEIGHT = 200, 10
GRAVITY = 0.1
FLIPPER_ANGLE_SPEED = 5  # Rotationsgeschwindigkeit in Grad

# Pygame initialisieren
pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Flipper-Spiel')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24) 

def reset_ball():
    x_pos = random.randint(BALL_DIAMETER, WINDOW_WIDTH - BALL_DIAMETER)
    y_pos = 50  # Startposition des Balls in y-Richtung
    ball_speed_x = random.choice([-1, 1]) * BALL_INITIAL_SPEED  # Zufällige horizontale Richtung
    ball_speed_y = BALL_INITIAL_SPEED  # Startgeschwindigkeit nach unten
    return pygame.Rect(x_pos, y_pos, BALL_DIAMETER, BALL_DIAMETER), ball_speed_x, ball_speed_y

ball, ball_speed_x, ball_speed_y = reset_ball()

# Button Konfiguration
button_color = (255, 0, 0)  # Rot
button_hover_color = (200, 0, 0)  # Dunkelrot
button_rect = pygame.Rect(WINDOW_WIDTH - 110, 10, 100, 30)
button_text = font.render('Close', True, pygame.Color('white'))

# Flipper-Positionen und Drehpunkte
flipper_left_pivot = (0, WINDOW_HEIGHT - 60)
flipper_right_pivot = (WINDOW_WIDTH, WINDOW_HEIGHT - 60)
flipper_left_angle, flipper_right_angle = 0, 0

def rotate_flipper(pivot, angle, length, flipper_side):
    rad_angle = math.radians(angle)
    if flipper_side == 'left':
        end_x = pivot[0] + length * math.cos(rad_angle)
        end_y = pivot[1] - length * math.sin(rad_angle)
        return (pivot[0], pivot[1], end_x, end_y)
    else:
        start_x = pivot[0] - length * math.cos(rad_angle)
        start_y = pivot[1] + length * math.sin(rad_angle)
        return (start_x, start_y, pivot[0], pivot[1])

def move_ball():
    global ball, ball_speed_x, ball_speed_y
    ball.x += ball_speed_x
    ball.y += ball_speed_y
    ball_speed_y += GRAVITY

    if ball.left <= 0 or ball.right >= WINDOW_WIDTH:
        ball_speed_x = -ball_speed_x
    if ball.top <= 0:
        ball_speed_y = -ball_speed_y
    if ball.bottom > WINDOW_HEIGHT:
        ball, ball_speed_x, ball_speed_y = reset_ball()

def get_line_normal(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    normal = (-dy, dx)
    normal_length = math.sqrt(normal[0]**2 + normal[1]**2)
    return (normal[0] / normal_length, normal[1] / normal_length)

def reflect(ball_speed, normal):
    """Reflektiert den Geschwindigkeitsvektor des Balls an der Normalen der Flipperoberfläche."""
    speed_mag = math.sqrt(ball_speed[0]**2 + ball_speed[1]**2)
    dot_product = ball_speed[0] * normal[0] + ball_speed[1] * normal[1]
    reflected = (
        ball_speed[0] - 2 * dot_product * normal[0],
        ball_speed[1] - 2 * dot_product * normal[1]
    )
    # Skaliert die reflektierte Geschwindigkeit zurück auf die ursprüngliche Geschwindigkeitsmagnitude
    reflected_mag = math.sqrt(reflected[0]**2 + reflected[1]**2)
    return (reflected[0] / reflected_mag * speed_mag, reflected[1] / reflected_mag * speed_mag)

def update_ball_speed(ball_speed, flipper_line):
    """Aktualisiert die Ballgeschwindigkeit basierend auf der Kollision mit dem Flipper."""
    start, end = (flipper_line[0], flipper_line[1]), (flipper_line[2], flipper_line[3])
    normal = get_line_normal(start, end)
    return reflect(ball_speed, normal)

def point_to_line_distance(px, py, x1, y1, x2, y2):
    norm = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    if norm == 0:
        return math.sqrt((px - x1)**2 + (py - y1)**2)
    u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / float(norm**2)
    closest_x = x1 + u * (x2 - x1)
    closest_y = y1 + u * (y2 - y1)
    distance = math.sqrt((closest_x - px)**2 + (closest_y - py)**2)
    return distance

def check_collision(ball, flipper_line):
    ball_center_x = ball.x + BALL_RADIUS
    ball_center_y = ball.y + BALL_RADIUS
    start_x, start_y, end_x, end_y = flipper_line
    distance = point_to_line_distance(ball_center_x, ball_center_y, start_x, start_y, end_x, end_y)
    return distance <= BALL_RADIUS and (min(start_x, end_x) <= ball_center_x <= max(start_x, end_x) or min(start_y, end_y) <= ball_center_y <= max(start_y, end_y))

def handle_input():
    global flipper_left_angle, flipper_right_angle
    keys = pygame.key.get_pressed()
    if keys[K_a]:
        flipper_left_angle = min(30, flipper_left_angle + FLIPPER_ANGLE_SPEED)
    else:
        flipper_left_angle = max(0, flipper_left_angle - FLIPPER_ANGLE_SPEED)
    if keys[K_d]:
        flipper_right_angle = max(-30, flipper_right_angle - FLIPPER_ANGLE_SPEED)
    else:
        flipper_right_angle = min(0, flipper_right_angle + FLIPPER_ANGLE_SPEED)

# (Füge hier den oberen Teil des vorherigen Codes ein, einschließlich der Importe und Definitionen von reset_ball, rotate_flipper, usw.)

def draw():
    window.fill((0, 0, 0))
    pygame.draw.ellipse(window, (255, 255, 255), ball)
    left_flipper_line = rotate_flipper(flipper_left_pivot, flipper_left_angle, FLIPPER_WIDTH, 'left')
    right_flipper_line = rotate_flipper(flipper_right_pivot, flipper_right_angle, FLIPPER_WIDTH, 'right')
    pygame.draw.line(window, (255, 0, 0), (left_flipper_line[0], left_flipper_line[1]), (left_flipper_line[2], left_flipper_line[3]), FLIPPER_HEIGHT)
    pygame.draw.line(window, (255, 0, 0), (right_flipper_line[0], right_flipper_line[1]), (right_flipper_line[2], right_flipper_line[3]), FLIPPER_HEIGHT)

def draw_gui():
    # Zeigt die GUI-Elemente an
    speed = math.sqrt(ball_speed_x**2 + ball_speed_y**2)
    position_text = f'X: {ball.x}, Y: {ball.y}'
    speed_text = f'Speed: {speed:.2f}'
    position_surf = font.render(position_text, True, pygame.Color('white'))
    speed_surf = font.render(speed_text, True, pygame.Color('white'))
    window.blit(position_surf, (10, 10))
    window.blit(speed_surf, (10, 40))
    # Button zeichnen
    mouse_pos = pygame.mouse.get_pos()
    if button_rect.collidepoint(mouse_pos):
        pygame.draw.rect(window, button_hover_color, button_rect)
    else:
        pygame.draw.rect(window, button_color, button_rect)
    window.blit(button_text, (button_rect.x + 5, button_rect.y + 5))

def check_button(mouse_pos):
    return button_rect.collidepoint(mouse_pos)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Linke Maustaste
            if check_button(event.pos):
                running = False
    
    window.fill((0, 0, 0)) 
    handle_input()
    move_ball()
    draw()
    draw_gui()
    pygame.display.update() 

    left_flipper_line = rotate_flipper(flipper_left_pivot, flipper_left_angle, FLIPPER_WIDTH, 'left')
    right_flipper_line = rotate_flipper(flipper_right_pivot, flipper_right_angle, FLIPPER_WIDTH, 'right')
    if check_collision(ball, left_flipper_line):
        ball_speed_x, ball_speed_y = update_ball_speed((ball_speed_x, ball_speed_y), left_flipper_line)
    if check_collision(ball, right_flipper_line):
        ball_speed_x, ball_speed_y = update_ball_speed((ball_speed_x, ball_speed_y), right_flipper_line)
    
    clock.tick(60)

pygame.quit()
sys.exit()
