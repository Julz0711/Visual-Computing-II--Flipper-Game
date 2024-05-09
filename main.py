##### Imports #####

import pygame
import sys
import math
from pygame.locals import *
from config import *



##### Initialisierungen #####

# Initialisierung von Pygame für Grafik und Schriftarten
pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 24)

# Initialisierung der Kugel mit Startposition und Geschwindigkeit
ball_pos = [WIDTH // 2, HEIGHT // 4]
ball_vel = [0, 0]

# Initialisierung der Flipper
left_flipper_angle = 0
right_flipper_angle = 0
left_flipper_pos = [0, HEIGHT - 100]
right_flipper_pos = [WIDTH, HEIGHT - 100]

# Initialisierung des Bumpers
bumpers = [{'pos': [100, 300], 'radius': BUMPER_RADIUS, 'color': RED, 'active': False, 'timer': 0}]

# Cooldown für Kollisionen, um unmittelbare Mehrfachkollisionen zu vermeiden
collision_cooldown = 0
COLLISION_COOLDOWN_MAX = 30

# Initialisierung des Fensters
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flipper")

# Initialisierung der Uhr für die Spielsteuerung der Framerate
clock = pygame.time.Clock()



##### Ball Physics #####

def move_ball():
    global GRAVITY, INITIAL_BALL_IMPULSE, BUMPER_BOUNCE

    # Wenn das Spiel nicht gestartet ist, wird die Funktion vorzeitig verlassen.
    if not GAME_STARTED:
        return
    
    # Wenn die Kugel noch keine Anfangsgeschwindigkeit hat
    if ball_vel == [0, 0]:
        ball_vel[1] = INITIAL_BALL_IMPULSE  # Setze den Anfangsimpuls nach unten

    # Schwerkraft anwenden, die die Kugel nach unten zieht
    ball_vel[1] += GRAVITY 

    # Aktualisiere die horizontale / vertikale Position der Kugel
    ball_pos[0] += ball_vel[0]
    ball_pos[1] += ball_vel[1]

    # Überprüfung auf Kollision mit den Seitenwänden des Spielfelds
    if ball_pos[0] <= BALL_RADIUS or ball_pos[0] >= WIDTH - BALL_RADIUS:
        # Kehre die horizontale Geschwindigkeit um
        ball_vel[0] = -ball_vel[0]

    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        # Kehre die vertikale Geschwindigkeit um
        ball_vel[1] = -ball_vel[1]
    
    # Kollision mit Bumpern
    for bumper in bumpers:
        if math.hypot(ball_pos[0] - bumper['pos'][0], ball_pos[1] - bumper['pos'][1]) < BALL_RADIUS + bumper['radius']:
            if not bumper['active']:
                bumper['active'] = True
                bumper['timer'] = 10  # Anzahl der Frames, die die Animation dauert
            angle = math.atan2(ball_pos[1] - bumper['pos'][1], ball_pos[0] - bumper['pos'][0])
            ball_vel[0] += BUMPER_BOUNCE * math.cos(angle)
            ball_vel[1] += BUMPER_BOUNCE * math.sin(angle)


def draw_ball():
    # Zeichnet die Kugel an ihrer aktuellen Position auf dem Spielfeld.
    pygame.draw.circle(window, WHITE, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

def segment_intersection(p1, p2, p3, p4):
    # Prüft, ob zwei Segmente (p1-p2 und p3-p4) sich schneiden
    dx1 = p2[0] - p1[0]
    dy1 = p2[1] - p1[1]
    dx2 = p4[0] - p3[0]
    dy2 = p4[1] - p3[1]
    delta = dx2 * dy1 - dy2 * dx1

    # Parallele Linien haben keine Schnittpunkte
    if delta == 0:  
        return False
    
    s = (dx1 * (p3[1] - p1[1]) + dy1 * (p1[0] - p3[0])) / delta
    t = (dx2 * (p1[1] - p3[1]) + dy2 * (p3[0] - p1[0])) / -delta

    # Prüft, ob die Schnittpunkte innerhalb der Segmente liegen
    return (0 <= s <= 1) and (0 <= t <= 1)

def will_collide(ball_pos, ball_vel, flipper_start, flipper_end):
    # Bestimmt, ob die Kugel auf ihrem Weg mit einem Flipper kollidieren wird
    future_ball_pos = [ball_pos[0] + ball_vel[0], ball_pos[1] + ball_vel[1]]
    return segment_intersection(ball_pos, future_ball_pos, flipper_start, flipper_end)

def get_line_normal(start, end):
    # Berechnet den Normalenvektor einer Linie, die durch zwei Punkte definiert ist
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    # Der Normalenvektor ist senkrecht zur Linie
    normal = (-dy, dx)
    length = math.sqrt(normal[0]**2 + normal[1]**2)

    # Normierung des Vektors
    return (normal[0] / length, normal[1] / length)

def reflect_ball(start, end):
    # Reflektiert die Geschwindigkeit der Kugel basierend auf der Normale der Kollisionsfläche.
    normal = get_line_normal(start, end)
    new_velocity = reflect((ball_vel[0], ball_vel[1]), normal)

    # Verstärkt die Reflexion leicht, um zu verhindern, dass die Kugel an der Fläche "kleben" bleibt
    ball_vel[0] = new_velocity[0] + normal[0] * FLIPPER_BOUNCE
    ball_vel[1] = new_velocity[1] + normal[1] * FLIPPER_BOUNCE

    # # Ein kleiner Schub, um Überlappungen nach der Kollision zu vermeiden
    escape_distance = 2
    ball_pos[0] += normal[0] * escape_distance
    ball_pos[1] += normal[1] * escape_distance

def reflect(velocity, normal):
    # Reflektiert eine gegebene Geschwindigkeit an einer Fläche mit gegebenem Normalenvektor
    dot_product = velocity[0] * normal[0] + velocity[1] * normal[1]
    reflected_velocity = (
        velocity[0] - 2 * dot_product * normal[0],
        velocity[1] - 2 * dot_product * normal[1]
    )
    return reflected_velocity

def check_collision():
    # Überprüft Kollisionen zwischen der Kugel und den Flippern und handhabt die Folgen einer Kollision
    global ball_pos, ball_vel, collision_cooldown

    # Verhindert wiederholte Kollisionen in kurzen Zeitabständen
    if collision_cooldown > 0:
        collision_cooldown -= 1
        return

    for flipper_pos, angle, is_right in [(left_flipper_pos, left_flipper_angle, False), (right_flipper_pos, right_flipper_angle, True)]:
        # Berechne die Positionen der Außenwände des Flippers
        start_x, start_y = flipper_pos
        end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
        end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))
        normal = get_line_normal((start_x, start_y), (end_x, end_y))
        perpendicular = (-normal[1], normal[0])  # Berechne die senkrechte Richtung zur Flipperrichtung

        # Überprüfe Kollision mit den Außenwänden des Flippers
        wall_start = (start_x + perpendicular[0] * FLIPPER_WIDTH / 2, start_y + perpendicular[1] * FLIPPER_WIDTH / 2)
        wall_end = (end_x + perpendicular[0] * FLIPPER_WIDTH / 2, end_y + perpendicular[1] * FLIPPER_WIDTH / 2)
        if point_line_distance(ball_pos, wall_start, wall_end) <= BALL_RADIUS:
            reflect_ball(wall_start, wall_end)
            collision_cooldown = COLLISION_COOLDOWN_MAX
            break

def point_line_distance(point, start, end):
    # Berechnet den Abstand eines Punktes von einer Linie, definiert durch zwei Punkte.
    px, py = point
    sx, sy = start
    ex, ey = end

    line_vec = (ex - sx, ey - sy)
    point_vec = (px - sx, py - sy)

    line_len = math.sqrt(line_vec[0]**2 + line_vec[1]**2)
    line_unitvec = (line_vec[0] / line_len, line_vec[1] / line_len)

    proj_length = point_vec[0] * line_unitvec[0] + point_vec[1] * line_unitvec[1]

    # Projizierte Länge auf der Linie
    proj_length = max(0, min(proj_length, line_len))
    nearest = (sx + line_unitvec[0] * proj_length, sy + line_unitvec[1] * proj_length)

    # Berechnet den minimalen Abstand
    dist = math.sqrt((px - nearest[0])**2 + (py - nearest[1])**2)
    return dist

def draw_flipper(position, angle, is_right):
    start_x, start_y = position
    end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
    end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))
    pygame.draw.line(window, WHITE, (start_x, start_y), (end_x, end_y), FLIPPER_WIDTH)

def draw_bumpers():
    for bumper in bumpers:
        if bumper['active']:  # Vergrößerungsfaktor für aktive Bumper
            scaled_radius = int(bumper['radius'] * BUMPER_SCALE)
            pygame.draw.circle(window, bumper['color'], (int(bumper['pos'][0]), int(bumper['pos'][1])), scaled_radius)
            bumper['timer'] -= 1
            if bumper['timer'] <= 0:
                bumper['active'] = False
        else:
            pygame.draw.circle(window, bumper['color'], (int(bumper['pos'][0]), int(bumper['pos'][1])), bumper['radius'])

def handle_keys():
    global left_flipper_angle, right_flipper_angle, ball_pos, ball_vel, GAME_STARTED
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        left_flipper_angle = 30
    else:
        left_flipper_angle = 0
    if keys[pygame.K_d]:
        right_flipper_angle = 30
    else:
        right_flipper_angle = 0
    if keys[pygame.K_r]:
        ball_pos = [WIDTH // 2, HEIGHT // 4]
        ball_vel = [0, 0]
        GAME_STARTED = False

def handle_mouse():
    global ball_pos, ball_vel, GAME_STARTED
    if pygame.mouse.get_pressed()[0] and not GAME_STARTED:
        if not (slider1_rect.collidepoint(pygame.mouse.get_pos()) or slider2_rect.collidepoint(pygame.mouse.get_pos())):
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

def draw_slider(slider_rect, slider_value, text, text_pos):
    # Draw slider bar
    pygame.draw.rect(window, SLIDER_COLOR, slider_rect)
    # Calculate handle position
    handle_pos = slider_rect.left + (slider_value - SLIDER_MIN_VALUE) / (SLIDER_MAX_VALUE - SLIDER_MIN_VALUE) * (slider_rect.width - SLIDER_HEIGHT)

    handle_rect = pygame.Rect(handle_pos, slider_rect.centery - SLIDER_HEIGHT // 2, SLIDER_HEIGHT, SLIDER_HEIGHT)
    # Draw slider handle
    pygame.draw.rect(window, SLIDER_HANDLE_COLOR, handle_rect)
    # Draw slider text with value
    text_with_value = f"{text}: {slider_value}"
    text_surf = font.render(text_with_value, True, SLIDER_TEXT_COLOR)
    window.blit(text_surf, text_pos)

def show_controls_popup():
    popup_font = pygame.font.SysFont(None, 24)
    popup_text = [
        "Controls:",
        "A - Activate left flipper",
        "D - Activate right flipper",
        "R - Reset game"
    ]

    popup_rect = pygame.Rect(0, 0, 500, 800)
    popup_surface = pygame.Surface((popup_rect.width, popup_rect.height))
    popup_surface.fill((25, 25, 25))

    for i, line in enumerate(popup_text):
        text_surf = popup_font.render(line, True, pygame.Color('white'))
        popup_surface.blit(text_surf, (25, 25 + i * 25))

    continue_button_rect = pygame.Rect(25, 150, 150, 50)
    pygame.draw.rect(popup_surface, (RED), continue_button_rect)
    continue_button_text = popup_font.render("Continue", True, pygame.Color('white'))
    popup_surface.blit(continue_button_text, (60, 168))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_RETURN:
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if continue_button_rect.collidepoint(mouse_pos):
                    return

        window.blit(popup_surface, popup_rect.topleft)
        pygame.display.flip()
        clock.tick(60)

def game_loop():
    global collision_cooldown, slider1_rect, slider2_rect, INITIAL_BALL_IMPULSE, GRAVITY_STRENGTH, GRAVITY, GAME_STARTED

    slider1_rect = pygame.Rect(300, 40, SLIDER_WIDTH, SLIDER_HEIGHT)
    slider2_rect = pygame.Rect(300, 90, SLIDER_WIDTH, SLIDER_HEIGHT)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_controls_popup()

        # Slider events handling
        if pygame.mouse.get_pressed()[0] and not GAME_STARTED:
            mouse_pos = pygame.mouse.get_pos()
            if slider1_rect.collidepoint(mouse_pos):
                # Update INITIAL_BALL_IMPULSE based on slider value
                INITIAL_BALL_IMPULSE = int((mouse_pos[0] - slider1_rect.left) / slider1_rect.width * (SLIDER_MAX_VALUE - SLIDER_MIN_VALUE) + SLIDER_MIN_VALUE)
            elif slider2_rect.collidepoint(mouse_pos):
                # Update GRAVITY_STRENGTH based on slider value
                GRAVITY_STRENGTH = int((mouse_pos[0] - slider2_rect.left) / slider2_rect.width * (SLIDER_MAX_VALUE - SLIDER_MIN_VALUE) + SLIDER_MIN_VALUE)
                GRAVITY = 0.1 * GRAVITY_STRENGTH  # Adjust gravity strength

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

        # Draw sliders
        draw_slider(slider1_rect, INITIAL_BALL_IMPULSE, "Initial Ball Impulse", (300, 20))
        draw_slider(slider2_rect, GRAVITY_STRENGTH, "Gravity Strength", (300, 70))

        pygame.display.flip()
        clock.tick(60)

if __name__ == '__main__':
    GAME_STARTED = False
    game_loop()
