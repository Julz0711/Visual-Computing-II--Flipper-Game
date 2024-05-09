import pygame
import sys
import math
from config import *
from pygame.locals import *
# from gui import draw_gui

# Initialisierung von Pygame
pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 24) 

# Kugel Eigenschaften
ball_pos = [WIDTH // 2, HEIGHT // 4]
ball_vel = [0, 0]

# Flipper Eigenschaften
left_flipper_angle = 0
right_flipper_angle = 0
left_flipper_pos = [0, HEIGHT - 100]
right_flipper_pos = [WIDTH, HEIGHT - 100]

# Bumper
bumpers = [{'pos': [100, 300], 'radius': BUMPER_RADIUS, 'color': RED}]

def move_ball():
    if not GAME_STARTED:
        return
    ball_vel[1] += GRAVITY
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]
    if ball_pos[0] <= BALL_RADIUS or ball_pos[0] >= WIDTH - BALL_RADIUS:
        ball_vel[0] = -ball_vel[0]
    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]
    for bumper in bumpers:
        if math.hypot(ball_pos[0] - bumper['pos'][0], ball_pos[1] - bumper['pos'][1]) < BALL_RADIUS + bumper['radius']:
            angle = math.atan2(ball_pos[1] - bumper['pos'][1], ball_pos[0] - bumper['pos'][0])
            ball_vel[0] += 5 * math.cos(angle)
            ball_vel[1] += 5 * math.sin(angle)

def draw_ball():
    pygame.draw.circle(window, WHITE, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

def segment_intersection(p1, p2, p3, p4):
    """Prüft, ob zwei Segmente (p1-p2 und p3-p4) sich schneiden"""
    dx1 = p2[0] - p1[0]
    dy1 = p2[1] - p1[1]
    dx2 = p4[0] - p3[0]
    dy2 = p4[1] - p3[1]
    delta = dx2 * dy1 - dy2 * dx1
    if delta == 0:  # Parallele Linien
        return False
    s = (dx1 * (p3[1] - p1[1]) + dy1 * (p1[0] - p3[0])) / delta
    t = (dx2 * (p1[1] - p3[1]) + dy2 * (p3[0] - p1[0])) / -delta
    return (0 <= s <= 1) and (0 <= t <= 1)

def will_collide(ball_pos, ball_vel, flipper_start, flipper_end):
    """Überprüft, ob die Kugel auf ihrem Weg mit dem Flipper kollidieren wird"""
    future_ball_pos = [ball_pos[0] + ball_vel[0], ball_pos[1] + ball_vel[1]]
    return segment_intersection(ball_pos, future_ball_pos, flipper_start, flipper_end)

def get_line_normal(start, end):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    normal = (-dy, dx)
    length = math.sqrt(normal[0]**2 + normal[1]**2)
    return (normal[0] / length, normal[1] / length)

def reflect_ball(start, end):
    normal = get_line_normal(start, end)
    new_velocity = reflect((ball_vel[0], ball_vel[1]), normal)
    ball_vel[0] = new_velocity[0]
    ball_vel[1] = new_velocity[1]
    # Einen kleinen Schub hinzufügen, um zu verhindern, dass die Kugel stecken bleibt
    escape_distance = 2
    ball_pos[0] += normal[0] * escape_distance
    ball_pos[1] += normal[1] * escape_distance

def reflect(velocity, normal):
    dot_product = velocity[0] * normal[0] + velocity[1] * normal[1]
    reflected_velocity = (
        velocity[0] - 2 * dot_product * normal[0],
        velocity[1] - 2 * dot_product * normal[1]
    )
    return reflected_velocity

def check_collision():
    global ball_pos, ball_vel
    for flipper_pos, angle, is_right in [(left_flipper_pos, left_flipper_angle, False), (right_flipper_pos, right_flipper_angle, True)]:
        end_x = flipper_pos[0] + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
        end_y = flipper_pos[1] - FLIPPER_LENGTH * math.sin(math.radians(angle))
        if point_line_distance(ball_pos, flipper_pos, (end_x, end_y)) <= BALL_RADIUS:
            reflect_ball((flipper_pos[0], flipper_pos[1]), (end_x, end_y))

def point_line_distance(point, start, end):
    px, py = point
    sx, sy = start
    ex, ey = end

    line_vec = (ex - sx, ey - sy)
    point_vec = (px - sx, py - sy)

    line_len = math.sqrt(line_vec[0]**2 + line_vec[1]**2)
    line_unitvec = (line_vec[0] / line_len, line_vec[1] / line_len)

    proj_length = point_vec[0] * line_unitvec[0] + point_vec[1] * line_unitvec[1]
    proj_length = max(0, min(proj_length, line_len))
    nearest = (sx + line_unitvec[0] * proj_length, sy + line_unitvec[1] * proj_length)

    dist = math.sqrt((px - nearest[0])**2 + (py - nearest[1])**2)
    return dist


def draw_flipper(position, angle, is_right):
    start_x, start_y = position
    end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
    end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))
    pygame.draw.line(window, WHITE, (start_x, start_y), (end_x, end_y), FLIPPER_WIDTH)

def draw_bumpers():
    for bumper in bumpers:
        pygame.draw.circle(window, bumper['color'], (int(bumper['pos'][0]), int(bumper['pos'][1])), bumper['radius'])

def handle_keys():
    global left_flipper_angle, right_flipper_angle
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        left_flipper_angle = 30
    else:
        left_flipper_angle = 0
    if keys[pygame.K_d]:
        right_flipper_angle = 30
    else:
        right_flipper_angle = 0

def handle_mouse():
    global ball_pos, ball_vel, GAME_STARTED
    if pygame.mouse.get_pressed()[0] and not GAME_STARTED:
        ball_pos = list(pygame.mouse.get_pos())
        ball_vel = [0, 0]
        GAME_STARTED = True

def draw_gui():
    # Display GUI elements
    speed = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2)
    position_text = f'X: {ball_pos[0]:.2f}, Y: {ball_pos[1]:.2f}'
    speed_text = f'Speed: {speed:.2f}'  # Display speed with 2 decimal places
    position_surf = font.render(position_text, True, pygame.Color('white'))
    speed_surf = font.render(speed_text, True, pygame.Color('white'))
    window.blit(position_surf, (10, 10))
    window.blit(speed_surf, (10, 40))

def game_loop():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        window.fill(BLACK)
        move_ball()
        draw_ball()
        handle_keys()
        handle_mouse()
        draw_flipper(left_flipper_pos, left_flipper_angle, False)
        draw_flipper(right_flipper_pos, right_flipper_angle, True)
        draw_bumpers()
        check_collision()

        # Draw GUI    
        draw_gui()

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    game_loop()