##### Imports #####

import pygame
import sys
import math
from pygame.locals import *
from config import *
import pygame_gui


##### Initialisierungen #####

# Initialisierung von Pygame für Grafik und Schriftarten
pygame.init()
pygame.font.init()
manager = pygame_gui.UIManager((WIDTH, HEIGHT), 'theme.json')
font = pygame.font.SysFont(None, 24)

# Initialisierung der Kugel mit Startposition und Geschwindigkeit
ball_pos = [GAME_WIDTH // 2, HEIGHT // 4]
ball_vel = [0, 0]

# Initialisierung der Flipper
left_flipper_angle = 0
right_flipper_angle = 0
left_flipper_pos = [0, HEIGHT - 100]
right_flipper_pos = [GAME_WIDTH, HEIGHT - 100]

# Initialisierung des Bumpers
bumpers = [{'pos': [100, 300], 'radius': BUMPER_RADIUS, 'color': RED, 'active': False, 'timer': 0}]


# Initialisierung des Fensters
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Initialisierung der Uhr für die Spielsteuerung der Framerate
clock = pygame.time.Clock()



##### Ball Physics #####

def move_ball():
    global GRAVITY, INITIAL_BALL_IMPULSE, BUMPER_BOUNCE

    if not GAME_STARTED:
        return
    
    if ball_vel == [0, 0]:
        ball_vel[0] = INITIAL_BALL_IMPULSE
        ball_vel[1] = INITIAL_BALL_IMPULSE

    ball_vel[1] += GRAVITY * dt

    ball_pos[0] += ball_vel[0] * dt
    ball_pos[1] += ball_vel[1] * dt

    # Ensure the ball doesn't move too far in a single frame
    max_step = BALL_RADIUS / 2
    ball_pos[0] = max(min(ball_pos[0], GAME_WIDTH - BALL_RADIUS), BALL_RADIUS)
    ball_pos[1] = max(min(ball_pos[1], HEIGHT - BALL_RADIUS), BALL_RADIUS)

    if ball_pos[0] <= BALL_RADIUS or ball_pos[0] >= GAME_WIDTH - BALL_RADIUS:
        ball_vel[0] = -ball_vel[0]

    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]
    
    for bumper in bumpers:
        if math.hypot(ball_pos[0] - bumper['pos'][0], ball_pos[1] - bumper['pos'][1]) < BALL_RADIUS + bumper['radius']:
            if not bumper['active']:
                bumper['active'] = True
                bumper['timer'] = 10
            angle = math.atan2(ball_pos[1] - bumper['pos'][1], ball_pos[0] - bumper['pos'][0])
            ball_vel[0] += BUMPER_BOUNCE * math.cos(angle)
            ball_vel[1] += BUMPER_BOUNCE * math.sin(angle)

    # Check if the ball is rolling on the flippers
    check_ball_on_flipper()


# Physics for is ball on flipper and rolling on flipper

def check_ball_on_flipper():
    for flipper_pos, angle, is_right in [(left_flipper_pos, left_flipper_angle, False), (right_flipper_pos, right_flipper_angle, True)]:
        start_x, start_y = flipper_pos
        end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
        end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))

        # is ball on flipper?
        if is_ball_on_flipper(ball_pos, ball_vel, (start_x, start_y), (end_x, end_y)):
            # rolling physics
            apply_flipper_physics(ball_pos, ball_vel, (start_x, start_y), (end_x, end_y))

def is_ball_on_flipper(ball_pos, ball_vel, flipper_start, flipper_end):
    # Check if the ball is on the flipper using the point-line distance
    return point_line_distance(ball_pos, flipper_start, flipper_end) <= BALL_RADIUS


def apply_flipper_physics(ball_pos, ball_vel, flipper_start, flipper_end):
    flipper_angle = math.atan2(flipper_end[1] - flipper_start[1], flipper_end[0] - flipper_start[0])
    gravity_parallel = GRAVITY * math.sin(flipper_angle)
    
    ball_vel[0] += gravity_parallel * dt * math.cos(flipper_angle)
    ball_vel[1] += gravity_parallel * dt * math.sin(flipper_angle)

    projected_pos = [ball_pos[0] + ball_vel[0] * dt, ball_pos[1] + ball_vel[1] * dt]
    dist_to_flipper = point_line_distance(projected_pos, flipper_start, flipper_end)
    if dist_to_flipper > BALL_RADIUS:
        normal = get_line_normal(flipper_start, flipper_end)
        ball_pos[0] -= normal[0] * (dist_to_flipper - BALL_RADIUS)
        ball_pos[1] -= normal[1] * (dist_to_flipper - BALL_RADIUS)

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
    normal = get_line_normal(start, end)
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    ball_to_midpoint = (midpoint[0] - ball_pos[0], midpoint[1] - ball_pos[1])

    if (ball_to_midpoint[0] * normal[0] + ball_to_midpoint[1] * normal[1]) > 0:
        normal = (-normal[0], -normal[1])

    new_velocity = reflect(ball_vel, normal)

    ball_vel[0] = new_velocity[0]
    ball_vel[1] = new_velocity[1]

    # Ensure the ball doesn't move too far into the object
    while point_line_distance(ball_pos, start, end) <= BALL_RADIUS:
        ball_pos[0] += normal[0] * 0.1
        ball_pos[1] += normal[1] * 0.1


def reflect(velocity, normal):
    # Reflektiert eine gegebene Geschwindigkeit an einer Fläche mit gegebenem Normalenvektor
    dot_product = velocity[0] * normal[0] + velocity[1] * normal[1]
    reflected_velocity = (
        velocity[0] - 2 * dot_product * normal[0],
        velocity[1] - 2 * dot_product * normal[1]
    )
    return reflected_velocity

def check_collision():
    global ball_pos, ball_vel

    for flipper_pos, angle, is_right in [(left_flipper_pos, left_flipper_angle, False), (right_flipper_pos, right_flipper_angle, True)]:
        start_x, start_y = flipper_pos
        end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
        end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))

        flipper_start = (start_x, start_y)
        flipper_end = (end_x, end_y)
        
        if point_line_distance(ball_pos, flipper_start, flipper_end) <= BALL_RADIUS:
            reflect_ball(flipper_start, flipper_end)
            break

    # Additional collision check for walls
    if ball_pos[0] <= BALL_RADIUS or ball_pos[0] >= GAME_WIDTH - BALL_RADIUS:
        ball_vel[0] = -ball_vel[0]

    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]


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



##### Flipper Logic #####

def draw_flipper(position, angle, is_right):
    # Berechnet die Start- und Endpunkte des Flippers basierend auf seiner Position, dem Winkel und der Ausrichtung.
    start_x, start_y = position

    # Bestimmt die Richtung des Flippers basierend darauf, ob er rechts oder links ist.
    end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
    end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))

    # Zeichnet eine Linie, die den Flipper darstellt.
    pygame.draw.line(window, WHITE, (start_x, start_y), (end_x, end_y), FLIPPER_WIDTH)

def draw_bumpers():
    # Durchläuft alle Bumper und zeichnet sie je nach ihrem Aktivierungsstatus.
    for bumper in bumpers:
        # Wenn der Bumper aktiv ist, zeichne ihn vergrößert.
        if bumper['active']:
            # Vergrößerungsfaktor für aktive Bumper  
            scaled_radius = int(bumper['radius'] * BUMPER_SCALE)
            pygame.draw.circle(window, bumper['color'], (int(bumper['pos'][0]), int(bumper['pos'][1])), scaled_radius)

            # Timer, die bestimmen, wie lange ein Bumper aktiv bleibt.
            bumper['timer'] -= 1

            # Deaktiviere den Bumper, wenn der Timer abgelaufen ist.
            if bumper['timer'] <= 0:
                bumper['active'] = False
        else:
            # Zeichne den Bumper in normaler Größe, wenn er nicht aktiv ist.
            pygame.draw.circle(window, bumper['color'], (int(bumper['pos'][0]), int(bumper['pos'][1])), bumper['radius'])



##### Event Handler ######

def handle_keys():
    # Überprüft, welche Tasten gedrückt wurden und führt entsprechende Aktionen aus.
    global left_flipper_angle, right_flipper_angle, ball_pos, ball_vel, GAME_STARTED
    keys = pygame.key.get_pressed()

    # Bewegt den linken Flipper nach oben, wenn die Taste 'A' gedrückt wird.
    if keys[pygame.K_a]:
        left_flipper_angle = 30
    else:
        left_flipper_angle = 0

    # Bewegt den rechten Flipper nach oben, wenn die Taste 'D' gedrückt wird.
    if keys[pygame.K_d]:
        right_flipper_angle = 30
    else:
        right_flipper_angle = 0

    # Setzt das Spiel zurück, wenn die Taste 'R' gedrückt wird.
    if keys[pygame.K_r]:
        ball_pos = [GAME_WIDTH // 2, HEIGHT // 4]
        ball_vel = [0, 0]
        GAME_STARTED = False

def handle_mouse():
    global ball_pos, ball_vel, GAME_STARTED
    if pygame.mouse.get_pressed()[0]:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Ensure the game starts only if the click is outside any UI elements and the game hasn't started yet
        if mouse_x < GAME_WIDTH and not (initial_impulse_slider.get_abs_rect().collidepoint(mouse_x, mouse_y) or
                                         gravity_strength_slider.get_abs_rect().collidepoint(mouse_x, mouse_y) or
                                         launch_angle_slider.get_abs_rect().collidepoint(mouse_x, mouse_y)):
            if not GAME_STARTED:
                angle_rad = math.radians(BALL_ANGLE + 90)
                ball_vel = [
                    INITIAL_BALL_IMPULSE * math.cos(angle_rad),
                    INITIAL_BALL_IMPULSE * math.sin(angle_rad)
                ]
                ball_pos = list(pygame.mouse.get_pos())
                GAME_STARTED = True





##### GUI #####

def draw_gui():
    pygame.draw.rect(window, GREY, pygame.Rect(GAME_WIDTH, 0, UI_WIDTH, HEIGHT))

    # Display GUI elements, including the current position and speed of the ball
    position_text = f'X: {ball_pos[0]:.2f}, Y: {ball_pos[1]:.2f}'

    speed = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2) / 100
    speed_text = f'Speed: {speed:.2f}'

    pause_text = "Drücke ESC zum Pausieren"

    position_surf = font.render(position_text, True, pygame.Color('white'))
    speed_surf = font.render(speed_text, True, pygame.Color('white'))
    pause_surf = font.render(pause_text, True, pygame.Color('yellow'))

    window.blit(pause_surf, (GAME_WIDTH + 10, 10))
    window.blit(position_surf, (GAME_WIDTH + 10, 40))
    window.blit(speed_surf, (GAME_WIDTH + 10, 70))



# Slider with Labels
from pygame_gui.elements import UIHorizontalSlider
from pygame_gui.elements import UILabel

initial_impulse_slider = UIHorizontalSlider(relative_rect=pygame.Rect((GAME_WIDTH + 10, 130), (SLIDER_WIDTH, SLIDER_HEIGHT)),
                                            start_value=INITIAL_BALL_IMPULSE / METER,  # Adjust to show the value in m/s
                                            value_range=(SLIDER_MIN_VALUE, SLIDER_MAX_VALUE),
                                            manager=manager)

gravity_strength_slider = UIHorizontalSlider(relative_rect=pygame.Rect((GAME_WIDTH + 10, 200), (SLIDER_WIDTH, SLIDER_HEIGHT)),
                                             start_value=GRAVITY_STRENGTH,
                                             value_range=(SLIDER_MIN_VALUE, SLIDER_MAX_VALUE),
                                             manager=manager)

launch_angle_slider = UIHorizontalSlider(relative_rect=pygame.Rect((GAME_WIDTH + 10, 270), (SLIDER_WIDTH, SLIDER_HEIGHT)),
                                         start_value=BALL_ANGLE,
                                         value_range=(SLIDER_MIN_ANGLE, SLIDER_MAX_ANGLE),
                                         manager=manager)

initial_impulse_label = UILabel(relative_rect=pygame.Rect((GAME_WIDTH + 10, 100), (SLIDER_WIDTH, 30)),
                                text=f"Initial Impulse: {INITIAL_BALL_IMPULSE / METER:.2f} m/s",
                                manager=manager)

gravity_strength_label = UILabel(relative_rect=pygame.Rect((GAME_WIDTH + 10, 170), (SLIDER_WIDTH, 30)),
                                 text=f"Gravity Strength: {GRAVITY / METER / 9.81:.2f}",
                                 manager=manager)

launch_angle_label = UILabel(relative_rect=pygame.Rect((GAME_WIDTH + 10, 240), (SLIDER_WIDTH, 30)),
                             text=f"Launch Angle: {BALL_ANGLE:.2f} degrees",
                             manager=manager)



##### Pause Menu #####

def show_controls_popup():
    # Zeigt ein Popup-Fenster mit den Spielsteuerungen an.
    popup_font = pygame.font.SysFont(None, 24)
    popup_text = [
        "Controls:",
        "A - Activate left flipper",
        "D - Activate right flipper",
        "R - Reset game"
    ]

    # Pop-Up Menu Initialisierung
    popup_rect = pygame.Rect(0, 0, 500, 800)
    popup_surface = pygame.Surface((popup_rect.width, popup_rect.height))
    popup_surface.fill((25, 25, 25))

    for i, line in enumerate(popup_text):
        text_surf = popup_font.render(line, True, pygame.Color('white'))
        popup_surface.blit(text_surf, (25, 25 + i * 25))

    # Button
    continue_button_rect = pygame.Rect(25, 150, 150, 50)
    pygame.draw.rect(popup_surface, (RED), continue_button_rect)
    continue_button_text = popup_font.render("Continue", True, pygame.Color('white'))
    popup_surface.blit(continue_button_text, (60, 168))

    # Aktivieren des Menü
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



##### Game Loop #####

def game_loop():
     # Hauptspiel-Schleife, die alle anderen Funktionen aufruft und das Spiel steuert.
    global INITIAL_BALL_IMPULSE, GRAVITY_STRENGTH, GRAVITY, GAME_STARTED, BALL_ANGLE

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Pause Menu
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_controls_popup()

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == initial_impulse_slider:
                        INITIAL_BALL_IMPULSE = event.value * METER
                        initial_impulse_label.set_text(f"Initial Impulse: {INITIAL_BALL_IMPULSE / METER:.2f} m/s")  # Assuming meters/second
                    elif event.ui_element == gravity_strength_slider:
                        GRAVITY_STRENGTH = event.value
                        GRAVITY = 9.81 * METER * GRAVITY_STRENGTH
                        gravity_strength_label.set_text(f"Gravity Strength: {GRAVITY/METER/9.81:.2f} m/s")
                    elif event.ui_element == launch_angle_slider:
                        BALL_ANGLE = event.value
                        launch_angle_label.set_text(f"Launch Angle: {BALL_ANGLE} degrees")


            manager.process_events(event)
 
        manager.update(dt)
        
        window.fill(BLACK)
        move_ball()
        draw_ball()
        handle_keys()
        handle_mouse()
        check_collision()
        draw_flipper(left_flipper_pos, left_flipper_angle, False)
        draw_flipper(right_flipper_pos, right_flipper_angle, True)
        draw_bumpers()
        draw_gui()
        manager.draw_ui(window)

        pygame.display.flip()
        pygame.display.set_caption(f"Flippernator3000 - FPS: {clock.get_fps():.2f}")
        clock.tick(60)

if __name__ == '__main__':
    GAME_STARTED = False
    game_loop()
