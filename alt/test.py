import pygame

# Pygame initialisieren
pygame.init()

import sys
import math
from alt.config_alt import *
from alt.ui_alt import *
from alt.ball_alt import Ball
from alt.ui_alt import draw_gui, Slider

from alt.flipper_alt import Flipper

# Pygame initialisieren
pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Flipper-Spiel')
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24) 

# Erstelle eine Instanz des Balls
ball = Ball()

# Flipper-Positionen und Drehpunkte
flipper_left_pivot = (0, WINDOW_HEIGHT - 60)
flipper_right_pivot = (WINDOW_WIDTH, WINDOW_HEIGHT - 60)
flipper_left_angle, flipper_right_angle = 0, 0

# Initialize flippers
left_flipper = Flipper(0, WINDOW_HEIGHT - 60, 100, 0, (255, 0, 0))
right_flipper = Flipper(WINDOW_WIDTH - 100, WINDOW_HEIGHT - 60, 100, 0, (0, 0, 255))

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

def get_line_normal(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    normal = (-dy, dx)
    normal_length = math.sqrt(normal[0]**2 + normal[1]**2)
    return (normal[0] / normal_length, normal[1] / normal_length)

def reflect(ball_speed, normal):
    """Reflects the velocity vector of the ball off the normal of the flipper surface."""
    speed_mag = math.sqrt(ball_speed[0]**2 + ball_speed[1]**2)
    dot_product = ball_speed[0] * normal[0] + ball_speed[1] * normal[1]
    reflected = (
        ball_speed[0] - 2 * dot_product * normal[0],
        ball_speed[1] - 2 * dot_product * normal[1]
    )
    reflected_mag = math.sqrt(reflected[0]**2 + reflected[1]**2)
    return (reflected[0] / reflected_mag * speed_mag, reflected[1] / reflected_mag * speed_mag)

def update_ball_speed(ball, flipper_line):
    """Updates the ball's speed based on collision with the flipper."""
    start, end = flipper_line[0:2], flipper_line[2:4]
    normal = get_line_normal(start, end)
    new_speed_x, new_speed_y = reflect((ball.speed_x, ball.speed_y), normal)
    ball.speed_x = new_speed_x
    ball.speed_y = new_speed_y


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
    ball_center_x = ball.rect.x + BALL_RADIUS
    ball_center_y = ball.rect.y + BALL_RADIUS
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
    window.fill((0, 0, 0))  # Bildschirm löschen
    if ball.active:
        pygame.draw.ellipse(window, (255, 255, 255), ball.rect)  # Ball zeichnen

    # Flipper zeichnen
    left_flipper_line = rotate_flipper(flipper_left_pivot, flipper_left_angle, FLIPPER_WIDTH, 'left')
    right_flipper_line = rotate_flipper(flipper_right_pivot, flipper_right_angle, FLIPPER_WIDTH, 'right')
    
    pygame.draw.line(window, (255, 0, 0), (left_flipper_line[0], left_flipper_line[1]), (left_flipper_line[2], left_flipper_line[3]), FLIPPER_HEIGHT)
    pygame.draw.line(window, (255, 0, 0), (right_flipper_line[0], right_flipper_line[1]), (right_flipper_line[2], right_flipper_line[3]), FLIPPER_HEIGHT)

slider_width = 200
slider_height = 20
margin = 10  # Margin from the right edge
font = pygame.font.SysFont(None, 24)

# Position sliders at top right
speed_slider_x = WINDOW_WIDTH - slider_width - margin
gravity_slider_x = speed_slider_x  # Same x position for both
speed_slider_y = 20
gravity_slider_y = 80

speed_slider = Slider(speed_slider_x, speed_slider_y, slider_width, slider_height, 1, 10, BALL_INITIAL_SPEED, "Speed", font)
gravity_slider = Slider(gravity_slider_x, gravity_slider_y, slider_width, slider_height, 0.1, 1, GRAVITY, "Gravity", font)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Check for left mouse click
            # Handle slider interaction separately
            if speed_slider.track.collidepoint(event.pos) or gravity_slider.track.collidepoint(event.pos):
                speed_slider.handle_event(event)
                gravity_slider.handle_event(event)
            # Set the ball's position if not on sliders and the ball is not active
            elif not ball.active:
                mouse_x, mouse_y = event.pos
                if not (speed_slider.track.collidepoint(mouse_x, mouse_y) or gravity_slider.track.collidepoint(mouse_x, mouse_y)):
                    ball.set_position(mouse_x, mouse_y)
                    ball.speed_y = speed_slider.get_value()  # Set vertical speed from slider
                    GRAVITY = gravity_slider.get_value()  # Update gravity from slider
                    ball.active = True  # Activate the ball to start moving
        elif event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEMOTION:
            speed_slider.handle_event(event)
            gravity_slider.handle_event(event)

    # Game logic
    if ball.active:
        ball.move()

    # Check for collisions and update speed
    left_flipper_line = rotate_flipper(flipper_left_pivot, flipper_left_angle, FLIPPER_WIDTH, 'left')
    right_flipper_line = rotate_flipper(flipper_right_pivot, flipper_right_angle, FLIPPER_WIDTH, 'right')

    if check_collision(ball, left_flipper_line):
        update_ball_speed(ball, left_flipper_line)
    if check_collision(ball, right_flipper_line):
        update_ball_speed(ball, right_flipper_line)

    window.fill((0, 0, 0)) 
    handle_input()
    draw()
    draw_gui(ball, window, font)
    
    speed_slider.draw(window)
    gravity_slider.draw(window)

    pygame.display.update() 

    clock.tick(60)

pygame.quit()
sys.exit()