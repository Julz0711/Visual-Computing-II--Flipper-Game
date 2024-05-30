##### Imports #####
###

import random
import pygame
import sys
import math
from pygame.locals import *
from config import *
import pygame_gui
from pygame_gui.elements import UIHorizontalSlider, UILabel, UITextBox, UIDropDownMenu, UIButton, UIPanel
from pygame_gui.core import ObjectID

###
### Initialisierungen ###
###

# Initialisierung von Pygame für Grafik und Schriftarten
pygame.init()
pygame.font.init()
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Initialisiere den UI Manager und lade das Theme aus der theme.json-Datei
manager = pygame_gui.UIManager((WIDTH, HEIGHT), 'data/theme/theme.json')

# Initialisierung der Kugel mit Startposition und Geschwindigkeit
ball_pos = [GAME_WIDTH // 2, HEIGHT // 4]
ball_vel = [0, 0]
ball_angular_vel = 0
ball_angle = 0

# Positionierung der Rampen
ramp_left_start = (0, HEIGHT - 200)
ramp_left_end = (ramp_left_start[0] + RAMP_LENGTH * math.cos(math.radians(RAMP_ANGLE)),
                 ramp_left_start[1] - RAMP_LENGTH * math.sin(math.radians(RAMP_ANGLE)))

ramp_right_start = (GAME_WIDTH, HEIGHT - 200)
ramp_right_end = (ramp_right_start[0] - RAMP_LENGTH * math.cos(math.radians(RAMP_ANGLE)),
                  ramp_right_start[1] - RAMP_LENGTH * math.sin(math.radians(RAMP_ANGLE)))

# Positionierung der Flipper
left_flipper_pos = ramp_left_end
right_flipper_pos = ramp_right_end
left_flipper_angle = 0
right_flipper_angle = 0

# Initialisierung der Bumpers
bumpers = [
    {'pos': [100, 300], 'radius': BUMPER_RADIUS, 'color': BLUE, 'active': False, 'timer': 0},
    {'pos': [400, 450], 'radius': BUMPER_RADIUS, 'color': BLUE, 'active': False, 'timer': 0}
]


###
### Partikel-System für visuelle Effekte ###
###

particles = []

# Fügt Partikel an einer gegebenen Position hinzu
def add_particles(pos):
    for _ in range(20): 
        particles.append({
            # Position des Partikels
            'pos': list(pos),
            # Zufällige Geschwindigkeit des Partikels
            'vel': [random.uniform(-2, 2), random.uniform(-2, 2)],
            # Lebensdauer des Partikels
            'timer': random.randint(10, 20),
            # Zufällige Farbe des Partikels
            'color': random.choice([RED, GREEN, BLUE, PURPLE, CYAN, WHITE])
        })


# Aktualisiert die Position und den Timer der Partikel
def update_particles():
    global particles
    for particle in particles:
        # Aktualisiert die x- und y-Positionen des Partikels
        particle['pos'][0] += particle['vel'][0]
        particle['pos'][1] += particle['vel'][1]
        particle['timer'] -= 1
    # Entfernt Partikel, deren Timer abgelaufen ist
    particles = [p for p in particles if p['timer'] > 0]


# Zeichnet alle aktiven Partikel auf das Fenster
def draw_particles():
     for particle in particles:
        pygame.draw.circle(window, particle['color'], (int(particle['pos'][0]), int(particle['pos'][1])), 2)



###
### Ball Physics ###
###

# Reflektiert die Geschwindigkeit der Kugel bei Kollision mit einem Bumper
def reflect_ball_velocity(ball_pos, ball_vel, bumper_pos, bumper_radius):
    global ball_angular_vel

    # Berechnet den Einfallswinkel
    angle_of_incidence = math.atan2(ball_pos[1] - bumper_pos[1], ball_pos[0] - bumper_pos[0])
    
    # Reflektiert den Geschwindigkeitsvektor
    normal = (math.cos(angle_of_incidence), math.sin(angle_of_incidence))
    dot_product = ball_vel[0] * normal[0] + ball_vel[1] * normal[1]
    ball_vel[0] -= 2 * dot_product * normal[0]
    ball_vel[1] -= 2 * dot_product * normal[1]

    # Multipliziert die Geschwindigkeit mit dem Bumper-Bounce-Faktor
    ball_vel[0] *= BUMPER_BOUNCE
    ball_vel[1] *= BUMPER_BOUNCE
    
    # Wendet Drehmoment basierend auf der Kollision an
    collision_vector = [ball_pos[0] - bumper_pos[0], ball_pos[1] - bumper_pos[1]]
    torque = (collision_vector[0] * ball_vel[1] - collision_vector[1] * ball_vel[0]) / (BALL_RADIUS ** 2)
    ball_angular_vel += torque

    # Stellt sicher, dass die Kugel nicht zu weit in den Bumper eindringt
    distance = math.hypot(ball_pos[0] - bumper_pos[0], ball_pos[1] - bumper_pos[1])
    overlap = BALL_RADIUS + bumper_radius - distance
    if overlap > 0:
        ball_pos[0] += overlap * normal[0]
        ball_pos[1] += overlap * normal[1]

    # Fügt Partikel an der Kollisionsstelle hinzu
    add_particles(ball_pos)


# Reflektiert die Kugel bei Kollision mit einer Linie (Flipper oder Rampe)
def reflect_ball(start, end):
    global ball_angular_vel

    # Berechnet den Normalenvektor der Linie
    normal = get_line_normal(start, end)
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    ball_to_midpoint = (midpoint[0] - ball_pos[0], midpoint[1] - ball_pos[1])

    if (ball_to_midpoint[0] * normal[0] + ball_to_midpoint[1] * normal[1]) > 0:
        normal = (-normal[0], -normal[1])

    ball_vel[0], ball_vel[1] = reflect(ball_vel, normal)

    # Wendet Drehmoment basierend auf der Kollision an
    collision_vector = [ball_pos[0] - midpoint[0], ball_pos[1] - midpoint[1]]
    torque = (collision_vector[0] * ball_vel[1] - collision_vector[1] * ball_vel[0]) / (BALL_RADIUS ** 2)
    ball_angular_vel += torque

    # Stellt sicher, dass die Kugel nicht zu weit in das Objekt eindringt
    while point_line_distance(ball_pos, start, end) <= BALL_RADIUS:
        ball_pos[0] += normal[0] * 0.1
        ball_pos[1] += normal[1] * 0.1


# Reflektiert eine gegebene Geschwindigkeit an einer Fläche mit gegebenem Normalenvektor
def reflect(velocity, normal):
    # Berechnet das Skalarprodukt der Geschwindigkeit und des Normalenvektors
    dot_product = velocity[0] * normal[0] + velocity[1] * normal[1]
    
    # Berechnet den reflektierten Geschwindigkeitsvektor
    reflected_velocity = (
        velocity[0] - 2 * dot_product * normal[0],
        velocity[1] - 2 * dot_product * normal[1]
    )
    return reflected_velocity



###
### move ball ###
###

# Bewegt die Kugel und aktualisiert ihre Position und Geschwindigkeit
def move_ball():
    global GRAVITY, INITIAL_BALL_IMPULSE, BUMPER_BOUNCE, ball_angle, ball_angular_vel, ball_vel, ball_pos

    if not GAME_STARTED:
        return
    
    # Default
    if ball_vel == [0, 0] and GAME_STARTED:
        angle_rad = math.radians(BALL_ANGLE + 90)
        ball_vel[0] = INITIAL_BALL_IMPULSE * math.cos(angle_rad)
        ball_vel[1] = INITIAL_BALL_IMPULSE * math.sin(angle_rad)

    # Fügt die Schwerkraft hinzu
    ball_vel[1] += GRAVITY * dt

    # Aktualisiert die Position der Kugel
    ball_pos[0] += ball_vel[0] * dt
    ball_pos[1] += ball_vel[1] * dt

    # Aktualisiert die Winkelposition
    ball_angle += ball_angular_vel * dt

    # Wendet Dämpfung an
    ball_vel[0] *= DAMPING_FACTOR
    ball_vel[1] *= DAMPING_FACTOR
    ball_angular_vel *= DAMPING_FACTOR

    # Überprüft, ob die Geschwindigkeit unterhalb des Schwellenwerts liegt, und stoppt die Kugel, wenn ja
    if math.hypot(ball_vel[0], ball_vel[1]) < VELOCITY_THRESHOLD:
        ball_vel = [0, 0]
        ball_angular_vel = 0

    # Begrenzt die Position der Kugel auf die Spielfeldgrenzen
    ball_pos[0] = max(min(ball_pos[0], GAME_WIDTH - BALL_RADIUS), BALL_RADIUS)
    ball_pos[1] = max(min(ball_pos[1], HEIGHT - BALL_RADIUS), BALL_RADIUS)
    
    # Kollisionslogik für Bumper
    for bumper in bumpers:
        if math.hypot(ball_pos[0] - bumper['pos'][0], ball_pos[1] - bumper['pos'][1]) < BALL_RADIUS + bumper['radius']:
            if not bumper['active']:
                bumper['active'] = True
                bumper['timer'] = 10
            reflect_ball_velocity(ball_pos, ball_vel, bumper['pos'], bumper['radius'])

    # Überprüft, ob die Kugel auf den Flippern rollt
    check_ball_on_flipper()



###
### Kollisionen ###
###

# Überprüft, ob die Kugel auf einem der Flipper rollt
def check_ball_on_flipper():
    for flipper_pos, angle, is_right in [(left_flipper_pos, left_flipper_angle, False), (right_flipper_pos, right_flipper_angle, True)]:
        start_x, start_y = flipper_pos
        end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
        end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))

        # Überprüft, ob die Kugel auf dem Flipper ist
        if is_ball_on_flipper(ball_pos, (start_x, start_y), (end_x, end_y)):
            # Wendet die Physik des Rollens an
            apply_flipper_physics(ball_pos, ball_vel, (start_x, start_y), (end_x, end_y))


# Überprüft, ob die Kugel auf dem Flipper ist, indem der Abstand zum Flipper berechnet wird
def is_ball_on_flipper(ball_pos, flipper_start, flipper_end):
    # Überprüft, ob die Kugel auf dem Flipper ist, indem der Punkt-Linien-Abstand berechnet wird
    return point_line_distance(ball_pos, flipper_start, flipper_end) <= BALL_RADIUS
    

# Wendet die Physik des Rollens der Kugel auf dem Flipper an
def apply_flipper_physics(ball_pos, ball_vel, flipper_start, flipper_end):
    flipper_angle = math.atan2(flipper_end[1] - flipper_start[1], flipper_end[0] - flipper_start[0])
    gravity_parallel = GRAVITY * math.sin(flipper_angle)
    
    # Aktualisiert die Geschwindigkeit der Kugel basierend auf der Schwerkraft entlang des Flipperwinkels
    ball_vel[0] += gravity_parallel * dt * math.cos(flipper_angle)
    ball_vel[1] += gravity_parallel * dt * math.sin(flipper_angle)

    # Berechnet die projizierte Position der Kugel nach der Geschwindigkeit
    projected_pos = [ball_pos[0] + ball_vel[0] * dt, ball_pos[1] + ball_vel[1] * dt]

    # Berechnet den Abstand der projizierten Position zum Flipper
    dist_to_flipper = point_line_distance(projected_pos, flipper_start, flipper_end)

    # Wenn die Kugel den Flipper verlässt, korrigiert die Position, damit sie darauf bleibt
    if dist_to_flipper > BALL_RADIUS:
        normal = get_line_normal(flipper_start, flipper_end)
        ball_pos[0] -= normal[0] * (dist_to_flipper - BALL_RADIUS)
        ball_pos[1] -= normal[1] * (dist_to_flipper - BALL_RADIUS)


# Prüft, ob zwei Segmente (p1-p2 und p3-p4) sich schneiden
def segment_intersection(p1, p2, p3, p4):
    # Berechnet die Differenzen der Koordinaten
    dx1 = p2[0] - p1[0]
    dy1 = p2[1] - p1[1]
    dx2 = p4[0] - p3[0]
    dy2 = p4[1] - p3[1]
    delta = dx2 * dy1 - dy2 * dx1

    # Parallele Linien haben keine Schnittpunkte
    if delta == 0:  
        return False
    
    # Berechnet die Parameter s und t für die Schnittpunkte
    s = (dx1 * (p3[1] - p1[1]) + dy1 * (p1[0] - p3[0])) / delta
    t = (dx2 * (p1[1] - p3[1]) + dy2 * (p3[0] - p1[0])) / -delta

    # Prüft, ob die Schnittpunkte innerhalb der Segmente liegen
    return (0 <= s <= 1) and (0 <= t <= 1)


# Berechnet den Normalenvektor einer Linie, die durch zwei Punkte definiert ist
def get_line_normal(start, end):
    # Berechnet die Differenzen der Koordinaten
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    # Der Normalenvektor ist senkrecht zur Linie
    normal = (-dy, dx)
    length = math.sqrt(normal[0]**2 + normal[1]**2)

    # Normierung des Vektors
    return (normal[0] / length, normal[1] / length)


# Überprüft Kollisionen der Kugel mit den Flippern und Spielfeldgrenzen
def check_collision():
    global ball_pos, ball_vel

    # Überprüft Kollisionen mit den Flippern
    for flipper_pos, angle, is_right in [(left_flipper_pos, left_flipper_angle, False), (right_flipper_pos, right_flipper_angle, True)]:
        start_x, start_y = flipper_pos
        end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
        end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))

        flipper_start = (start_x, start_y)
        flipper_end = (end_x, end_y)
        
        if point_line_distance(ball_pos, flipper_start, flipper_end) <= BALL_RADIUS:
            reflect_ball(flipper_start, flipper_end)
            break
    
    # Überprüft Kollisionen mit den Spielfeldgrenzen
    if ball_pos[0] <= BALL_RADIUS or ball_pos[0] >= GAME_WIDTH - BALL_RADIUS:
        ball_vel[0] = -ball_vel[0]

    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]


# Berechnet den Abstand eines Punktes von einer Linie, definiert durch zwei Punkte
def point_line_distance(point, start, end):
    px, py = point
    sx, sy = start
    ex, ey = end

    # Vektor der Linie
    line_vec = (ex - sx, ey - sy)
    
    # Vektor vom Startpunkt der Linie zum Punkt
    point_vec = (px - sx, py - sy)
   
    # Länge der Linie
    line_len = math.sqrt(line_vec[0]**2 + line_vec[1]**2)
    
    # Einheitlicher Vektor der Linie
    line_unitvec = (line_vec[0] / line_len, line_vec[1] / line_len)

    # Projektion der Punktkoordinate auf die Linie
    proj_length = point_vec[0] * line_unitvec[0] + point_vec[1] * line_unitvec[1]

    # Beschränkung der projizierten Länge auf die Länge der Linie
    proj_length = max(0, min(proj_length, line_len))
    nearest = (sx + line_unitvec[0] * proj_length, sy + line_unitvec[1] * proj_length)

    # Berechnet den minimalen Abstand zwischen dem Punkt und der Linie
    dist = math.sqrt((px - nearest[0])**2 + (py - nearest[1])**2)
    return dist


# Überprüft Kollisionen der Kugel mit den Rampen
def check_ramp_collision():
    global ball_pos, ball_vel

    # Durchläuft alle Rampen und überprüft, ob die Kugel eine Kollision hat
    for ramp_start, ramp_end in [(ramp_left_start, ramp_left_end), (ramp_right_start, ramp_right_end)]:
        if point_line_distance(ball_pos, ramp_start, ramp_end) <= BALL_RADIUS:
            reflect_ball(ramp_start, ramp_end)
            break



###
### Draw Funktionen ###
###

# Zeichnet die Kugel an ihrer aktuellen Position auf dem Spielfeld
def draw_ball():
    # Zeichnet die Kugel
    pygame.draw.circle(window, WHITE, (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

    # Zeichnet eine Linie, die die Richtung der Kugelgeschwindigkeit anzeigt
    direction_length = 30 * math.sqrt(ball_vel[0]**2 + ball_vel[1]**2) / 100
    angle = math.atan2(ball_vel[1], ball_vel[0])
    end_pos = (ball_pos[0] + direction_length * math.cos(angle), ball_pos[1] + direction_length * math.sin(angle))
    pygame.draw.line(window, PURPLE, (ball_pos[0], ball_pos[1]), end_pos, 2)


# Zeichnet den Flipper an der gegebenen Position und mit dem gegebenen Winkel
def draw_flipper(position, angle, is_right):
    # Berechnet die Start- und Endpunkte des Flippers basierend auf seiner Position, dem Winkel und der Ausrichtung
    start_x, start_y = position

    # Bestimmt die Richtung des Flippers basierend darauf, ob er rechts oder links ist
    end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
    end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))

    # Zeichnet eine Linie, die den Flipper darstellt
    pygame.draw.line(window, RED, (start_x, start_y), (end_x, end_y), FLIPPER_WIDTH)


# Zeichnet alle Bumper, basierend auf ihrem Aktivierungsstatus
def draw_bumpers():
    # Durchläuft alle Bumper und zeichnet sie je nach ihrem Aktivierungsstatus.
    for bumper in bumpers:
        # Wenn der Bumper aktiv ist, zeichne ihn vergrößert
        if bumper['active']:
            # Vergrößerungsfaktor für aktive Bumper
            scaled_radius = int(bumper['radius'] * BUMPER_SCALE)
            pygame.draw.circle(window, bumper['color'], (int(bumper['pos'][0]), int(bumper['pos'][1])), scaled_radius)

            # Verringert den Timer, der bestimmt, wie lange ein Bumper aktiv bleibt
            bumper['timer'] -= 1

            # Deaktiviert den Bumper, wenn der Timer abgelaufen ist
            if bumper['timer'] <= 0:
                bumper['active'] = False
        else:
            # Zeichne den Bumper in normaler Größe, wenn er nicht aktiv ist
            pygame.draw.circle(window, bumper['color'], (int(bumper['pos'][0]), int(bumper['pos'][1])), bumper['radius'])


# Zeichnet die Rampen auf das Spielfeld
def draw_ramps():
    # linke Rampe
    pygame.draw.line(window, WHITE, ramp_left_start, ramp_left_end, 3)
    # rechte Rampe
    pygame.draw.line(window, WHITE, ramp_right_start, ramp_right_end, 3)

# Zeichnet einen Indicator vor dem starten des Spiels, wo die Kugel hinfliegen wird
def draw_initial_trajectory():
    if not GAME_STARTED:
        angle_rad = math.radians(BALL_ANGLE + 90)
        initial_vel = [
            INITIAL_BALL_IMPULSE * math.cos(angle_rad),
            INITIAL_BALL_IMPULSE * math.sin(angle_rad)
        ]

        # Zeichnet eine Linie, die die Richtung und den erwarteten Flug der Kugel anzeigt
        direction_length = 50 * math.sqrt(initial_vel[0]**2 + initial_vel[1]**2) / 100
        angle = math.atan2(initial_vel[1], initial_vel[0])
        end_pos = (ball_pos[0] + direction_length * math.cos(angle), ball_pos[1] + direction_length * math.sin(angle))
        pygame.draw.line(window, PURPLE, (ball_pos[0], ball_pos[1]), end_pos, 2)



###
### Event Handler ###
###

# Überprüft, welche Tasten gedrückt wurden und führt entsprechende Aktionen aus.
def handle_keys():
    global left_flipper_angle, right_flipper_angle, ball_pos, ball_vel, GAME_STARTED
    keys = pygame.key.get_pressed()

    # Bewegt den linken Flipper nach oben, wenn die Taste 'A' gedrückt wird
    if keys[pygame.K_a]:
        left_flipper_angle = 30
    else:
        left_flipper_angle = 0

    # Bewegt den rechten Flipper nach oben, wenn die Taste 'D' gedrückt wird
    if keys[pygame.K_d]:
        right_flipper_angle = 30
    else:
        right_flipper_angle = 0

    # Setzt das Spiel zurück, wenn die Taste 'R' gedrückt wird
    if keys[pygame.K_r]:
        ball_pos = [GAME_WIDTH // 2, HEIGHT // 4]
        ball_vel = [0, 0]
        GAME_STARTED = False


# Überprüft, ob die Maus geklickt wurde, und führt entsprechende Aktionen aus
def handle_mouse():
    global ball_pos
    if pygame.mouse.get_pressed()[0] and not GAME_STARTED:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Setzt die Startposition der Kugel
        if mouse_x < GAME_WIDTH and not (initial_impulse_slider.get_abs_rect().collidepoint(mouse_x, mouse_y) or
                                         gravity_strength_slider.get_abs_rect().collidepoint(mouse_x, mouse_y) or
                                         launch_angle_slider.get_abs_rect().collidepoint(mouse_x, mouse_y)):
            ball_pos = list(pygame.mouse.get_pos())



# Event Handler for Buttons
def handle_buttons(event):
    global GAME_STARTED, ball_pos, ball_vel
    if event.ui_element == pause_button:
        show_controls_popup()
    elif event.ui_element == reset_button:
        ball_pos = [GAME_WIDTH // 2, HEIGHT // 4]
        ball_vel = [0, 0]
        GAME_STARTED = False
    elif event.ui_element == play_button:
        if ball_pos != [GAME_WIDTH // 2, HEIGHT // 4]:  
            angle_rad = math.radians(BALL_ANGLE + 90)
            ball_vel = [
                INITIAL_BALL_IMPULSE * math.cos(angle_rad),
                INITIAL_BALL_IMPULSE * math.sin(angle_rad)
            ]
            GAME_STARTED = True



###
### Graphical User Interface (GUI) ###
###

# Zeichnet die grafische Benutzeroberfläche (GUI) auf das Fenster
def draw_gui():
    # Zeichnet den Hintergrund des GUI-Bereichs
    position_text = f'X: {ball_pos[0]:.2f}, Y: {ball_pos[1]:.2f}'
    speed = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2) / 100
    speed_text = f'{speed:.2f}'

    position_value.set_text(position_text)
    speed_value.set_text(speed_text)

pause_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 14, 10), (UI_WIDTH - 28, 40)),
    text="Drücke ESC zum Pausieren",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#pause_label')
)

position_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 14, 70), (UI_WIDTH - 28, 30)),
    text="Position",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#position_label')
)

position_value = UITextBox(
    relative_rect=pygame.Rect((GAME_WIDTH + 12, 100), (UI_WIDTH - 24, 40)),
    html_text="X: 0.00, Y: 0.00",
    manager=manager,
    object_id=ObjectID(class_id='@text_box', object_id='#position_value')
)

speed_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 14, 150), (UI_WIDTH - 28, 30)),
    text="Speed",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#speed_label')
)

speed_value = UITextBox(
    relative_rect=pygame.Rect((GAME_WIDTH + 12, 180), (UI_WIDTH - 24, 40)),
    html_text="0.00",
    manager=manager,
    object_id=ObjectID(class_id='@text_box', object_id='#speed_value')
)


# Beschriftung für die Slider
ball_settings_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 14, 240), (SLIDER_WIDTH - 8, 50)),
    text=f"Ball Settings",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#ball_label')
)

# Initialisierung des Sliders für den initialen Impuls
initial_impulse_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 10, 335), (SLIDER_WIDTH, SLIDER_HEIGHT)),
    start_value=INITIAL_BALL_IMPULSE / METER,
    value_range=(SLIDER_MIN_VALUE, SLIDER_MAX_VALUE),
    manager=manager,
    object_id=ObjectID(class_id='@horizontal_slider', object_id='#ii_slider')
)

# Initialisierung des Sliders für die Schwerkraftstärke
gravity_strength_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 10, 425), (SLIDER_WIDTH, SLIDER_HEIGHT)),
    start_value=GRAVITY_STRENGTH,
    value_range=(SLIDER_MIN_VALUE, SLIDER_MAX_VALUE),
    manager=manager,
    object_id=ObjectID(class_id='@horizontal_slider', object_id='#gs_slider')
)

# Initialisierung des Sliders für den Abschusswinkel der Kugel
launch_angle_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 10, 515), (SLIDER_WIDTH, SLIDER_HEIGHT)),
    start_value=BALL_ANGLE,
    value_range=(SLIDER_MIN_ANGLE, SLIDER_MAX_ANGLE),
    manager=manager,
    object_id=ObjectID(class_id='@horizontal_slider', object_id='#la_slider')
)

# Beschriftung für den initialen Impuls-Slider
initial_impulse_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 14, 300), (SLIDER_WIDTH - 8, 30)),
    text=f"Initial Impulse: {INITIAL_BALL_IMPULSE / METER:.2f} m/s",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#ii_label')
)

# Beschriftung für den Schwerkraftstärke-Slider
gravity_strength_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 14, 390), (SLIDER_WIDTH - 8, 30)),
    text=f"Gravity Strength: {GRAVITY / METER / 9.81:.2f} m/s",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#gs_label')
)

# Beschriftung für den Abschusswinkel-Slider
launch_angle_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 14, 480), (SLIDER_WIDTH - 8, 30)),
    text=f"Launch Angle: {BALL_ANGLE:.2f} degrees",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#la_label')
)

# Play Button
play_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - SLIDER_WIDTH - 8, HEIGHT - 130), (SLIDER_WIDTH - 8, 65)),
    text="Play",
    manager=manager,
    object_id=ObjectID(class_id='button', object_id='#play_button')
)

# Pause Button
pause_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - SLIDER_WIDTH - 8, HEIGHT - 60), (SLIDER_WIDTH / 2 - 4, 50)),
    text="Pause",
    manager=manager,
    object_id=ObjectID(class_id='button', object_id='#pause_button')
)

# Reset Button
reset_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((WIDTH - SLIDER_WIDTH / 2 - 8, HEIGHT - 60), (SLIDER_WIDTH / 2 - 8, 50)),
    text="Reset",
    manager=manager,
    object_id=ObjectID(class_id='button', object_id='#reset_button')
)



###
### Pause Menu ###
###

# Zeigt ein Popup-Fenster mit den Spielsteuerungen an
def show_controls_popup():
    popup_font = pygame.font.SysFont(None, 24)
    popup_text = [
        "Controls:",
        "A - Activate left flipper",
        "D - Activate right flipper",
        "R - Reset game"
    ]

    # Initialisierung des Pop-Up-Menüs
    popup_rect = pygame.Rect(0, 0, 500, 800)
    popup_surface = pygame.Surface((popup_rect.width, popup_rect.height))
    popup_surface.fill((25, 25, 25))

    # Zeichnet den Text für die Steuerungen
    for i, line in enumerate(popup_text):
        text_surf = popup_font.render(line, True, pygame.Color('white'))
        popup_surface.blit(text_surf, (25, 25 + i * 25))

    # Zeichnet den "Weiter"-Button
    continue_button_rect = pygame.Rect(25, 150, 150, 50)
    pygame.draw.rect(popup_surface, (RED), continue_button_rect)
    continue_button_text = popup_font.render("Continue", True, pygame.Color('white'))
    popup_surface.blit(continue_button_text, (60, 168))

    # Aktiviert das Menü
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



###
### Game Loop ###
###

# Hauptspiel-Schleife, die alle anderen Funktionen aufruft und das Spiel steuert
def game_loop():
    global INITIAL_BALL_IMPULSE, GRAVITY_STRENGTH, GRAVITY, GAME_STARTED, BALL_ANGLE

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # Pause-Menü anzeigen, wenn ESC gedrückt wird
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    show_controls_popup()

            # Slider-Werte werden angewendet
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    handle_buttons(event)
                elif event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                    if event.ui_element == initial_impulse_slider:
                        INITIAL_BALL_IMPULSE = event.value * METER
                        initial_impulse_label.set_text(f"Initial Impulse: {INITIAL_BALL_IMPULSE / METER:.2f} m/s")
                    elif event.ui_element == gravity_strength_slider:
                        GRAVITY_STRENGTH = event.value
                        GRAVITY = 9.81 * METER * GRAVITY_STRENGTH
                        gravity_strength_label.set_text(f"Gravity Strength: {GRAVITY/METER/9.81:.2f} m/s")
                    elif event.ui_element == launch_angle_slider:
                        BALL_ANGLE = event.value
                        launch_angle_label.set_text(f"Launch Angle: {BALL_ANGLE} degrees")


            manager.process_events(event)
 
        manager.update(dt)
        
        window.fill(GAME_BG_COLOR, rect=pygame.Rect(0, 0, GAME_WIDTH, HEIGHT))
        window.fill(GUI_BG_COLOR, rect=pygame.Rect(GAME_WIDTH, 0, UI_WIDTH, HEIGHT))

        if not GAME_STARTED:
            draw_initial_trajectory()

        move_ball()
        draw_ball()
        handle_keys()
        handle_mouse()
        check_collision()
        check_ramp_collision()
        draw_flipper(left_flipper_pos, left_flipper_angle, False)
        draw_flipper(right_flipper_pos, right_flipper_angle, True)
        draw_bumpers()
        draw_ramps() 
        draw_gui()
        draw_particles()
        update_particles()

        manager.draw_ui(window)

        pygame.display.flip()
        pygame.display.set_caption(f"Flippernator3000 - FPS: {clock.get_fps():.2f}")
        clock.tick(60)

if __name__ == '__main__':
    # Setzt den Spielstatus auf nicht gestartet
    GAME_STARTED = False
    # Startet die Hauptspiel-Schleife
    game_loop()
