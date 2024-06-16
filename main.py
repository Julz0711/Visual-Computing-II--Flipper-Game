##### Imports #####
###

import random
import pygame
import sys
import math
from pygame.locals import *
from config import *
import pygame_gui
import pygame_gui.data
from pygame_gui.elements import UIHorizontalSlider, UILabel, UITextBox, UIDropDownMenu, UIButton, UIPanel
from pygame_gui.core import ObjectID
from endgame import end_game_screen

###
### Initialisierungen ###
###

# Initialisierung von Pygame für Grafik und Schriftarten
pygame.init()
pygame.font.init()
pygame.mixer.init()
font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Initialisiere den UI Manager und lade das Theme aus der theme.json-Datei
manager = pygame_gui.UIManager((WIDTH, HEIGHT), 'data/theme.json')

# Hintergrundmusik laden und abspielen
pygame.mixer.music.load('data/pinbolchill.mp3')
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1) 

# Initialisierung der Kugel mit Startposition und Geschwindigkeit
ball_pos = [GAME_WIDTH // 2, BALL_START_Y]
ball_vel = [0, 0]
ball_angular_vel = 0
ball_angle = 0
ball_color = 'White'

# Initialiserung des Pause Menu
is_pause_menu_open = False
pause_panel = None
continue_button = None
quit_button = None 
pregame_label = None

# GUI Sichtbarkeit
def set_gui_visibility(visible):
    initial_impulse_slider.sliding_button.visible = visible
    gravity_strength_slider.sliding_button.visible = visible
    launch_angle_slider.sliding_button.visible = visible

# Positionierung der Rampen
ramp_left_start = (0, HEIGHT - 300)
ramp_left_end = (ramp_left_start[0] + RAMP_LENGTH * math.cos(math.radians(RAMP_ANGLE)),
                 ramp_left_start[1] - RAMP_LENGTH * math.sin(math.radians(RAMP_ANGLE)))

ramp_right_start = (GAME_WIDTH, HEIGHT - 300)
ramp_right_end = (ramp_right_start[0] - RAMP_LENGTH * math.cos(math.radians(RAMP_ANGLE)),
                  ramp_right_start[1] - RAMP_LENGTH * math.sin(math.radians(RAMP_ANGLE)))

# Positionierung der Flipper
left_flipper_pos = ramp_left_end
right_flipper_pos = ramp_right_end
left_flipper_angle = -30
right_flipper_angle = -30
left_flipper_active = False
right_flipper_active = False
left_flipper_color = FLIPPER_COLOUR
right_flipper_color = FLIPPER_COLOUR

# Initialisierung der Bumpers
bumpers = [
    {'pos': [175, 450], 'radius': BUMPER_RADIUS, 'color': BUMPER_COLOUR, 'active': False, 'timer': 0},
    {'pos': [GAME_WIDTH - 175, 450], 'radius': BUMPER_RADIUS, 'color': BUMPER_COLOUR, 'active': False, 'timer': 0},
    {'pos': [GAME_WIDTH / 2, 350], 'radius': BUMPER_RADIUS * 1.5, 'color': BUMPER_COLOUR, 'active': False, 'timer': 0}
]


###
### Ramps
###

class Ramp:
    def __init__(self, start_pos, angle, length):
        self.start_pos = start_pos
        self.angle = angle
        self.length = length
        self.end_pos = (
            start_pos[0] + length * math.cos(math.radians(angle)),
            start_pos[1] - length * math.sin(math.radians(angle))
        )

    def draw(self, window, color=WHITE):
        pygame.draw.line(window, color, self.start_pos, self.end_pos, FLIPPER_WIDTH)

    def check_collision(self, ball_pos, ball_vel):
        if point_line_distance(ball_pos, self.start_pos, self.end_pos) <= BALL_RADIUS:
            reflect_ball(self.start_pos, self.end_pos)


# Initialize ramps
ramps = [
    # Flipper Rampen
    Ramp((0, HEIGHT - 300), RAMP_ANGLE, RAMP_LENGTH),
    Ramp((GAME_WIDTH, HEIGHT - 300), 180 - RAMP_ANGLE, RAMP_LENGTH),
    # Spielfeld Rampen
    Ramp((125, 600), 120, 150),
    Ramp((GAME_WIDTH - 125, 600), 60, 150),
    Ramp((50, 470), 90, 250),
    Ramp((GAME_WIDTH - 50, 470), 90, 250),
    Ramp((75, 150), -30, 150),
    Ramp((GAME_WIDTH - 75, 150), -150, 150),
    # Ramp((GAME_WIDTH / 2 - 100, 400), 0, 200)
]



###
### Partikel-System für visuelle Effekte ###
###

particles = []

# Fügt Partikel an einer gegebenen Position hinzu
def add_particles(pos, color=None):
    for _ in range(20): 
        particles.append({
            # Position des Partikels
            'pos': list(pos),
            # Zufällige Geschwindigkeit des Partikels
            'vel': [random.uniform(-2, 2), random.uniform(-2, 2)],
            # Lebensdauer des Partikels
            'timer': random.randint(10, 20),
            # Zufällige Farbe des Partikels
            'color': color if color else random.choice([RED, GREEN, BLUE, PURPLE, CYAN, WHITE])
        })

# Fügt spezielle Partikel für die Flipper hinzu
def add_flipper_particles(pos):
    flipper_color = (42, 254, 183)
    add_particles(pos, flipper_color)

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
def reflect_ball(start, end, is_flipper=False, flipper_velocity=0):
    global ball_pos, ball_vel, ball_angular_vel

    # Calculate the normal vector of the line
    normal = get_line_normal(start, end)
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    ball_to_midpoint = (midpoint[0] - ball_pos[0], midpoint[1] - ball_pos[1])

    if (ball_to_midpoint[0] * normal[0] + ball_to_midpoint[1] * normal[1]) > 0:
        normal = (-normal[0], -normal[1])

    ball_vel[0], ball_vel[1] = reflect(ball_vel, normal)

    # Apply torque based on the collision
    collision_vector = [ball_pos[0] - midpoint[0], ball_pos[1] - midpoint[1]]
    torque = (collision_vector[0] * ball_vel[1] - collision_vector[1] * ball_vel[0]) / (BALL_RADIUS ** 2)
    ball_angular_vel += torque

    # Ensure the ball does not penetrate the object too much
    while point_line_distance(ball_pos, start, end) <= BALL_RADIUS:
        ball_pos = [ball_pos[0] + normal[0] * 0.1, ball_pos[1] + normal[1] * 0.1]

    # Apply additional impulse if colliding with a flipper
    if is_flipper:
        impulse = flipper_velocity * FLIPPER_IMPULSE
        ball_vel[0] += normal[0] * impulse
        ball_vel[1] += normal[1] * impulse
        add_flipper_particles(ball_pos)


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
    ball_pos[0] += ball_vel[0] * dt + 0.5 * DAMPING_FACTOR * dt**2
    ball_pos[1] += ball_vel[1] * dt + 0.5 * GRAVITY * DAMPING_FACTOR * dt**2

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
    # check_ball_on_flipper()



###
### Kollisionen ###
###

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


def check_continuous_collision(ball_pos, ball_vel, flipper_start, flipper_end):
    # Calculate the number of steps based on the speed of the ball
    steps = int(math.hypot(ball_vel[0], ball_vel[1]) / BALL_RADIUS)
    steps = max(steps, 1)  # Ensure at least one step

    for i in range(steps):
        # Calculate the interpolated position of the ball
        interpolated_pos = (
            ball_pos[0] + ball_vel[0] * (i / steps) * dt,
            ball_pos[1] + ball_vel[1] * (i / steps) * dt
        )

        # Check for collision at this interpolated position
        if point_line_distance(interpolated_pos, flipper_start, flipper_end) <= BALL_RADIUS:
            return True, interpolated_pos

    return False, ball_pos


# Überprüft Kollisionen der Kugel mit den Flippern und Spielfeldgrenzen
def check_collision():
    global ball_pos, ball_vel

    # Check for collisions with the flippers
    for flipper_pos, angle, is_right, flipper_active, flipper_velocity in [
        (left_flipper_pos, left_flipper_angle, False, left_flipper_active, FLIPPER_ANGLE_STEP if left_flipper_active else 0),
        (right_flipper_pos, right_flipper_angle, True, right_flipper_active, FLIPPER_ANGLE_STEP if right_flipper_active else 0)]:

        start_x, start_y = flipper_pos
        end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
        end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))

        flipper_start = (start_x, start_y)
        flipper_end = (end_x, end_y)

        collision, collision_pos = check_continuous_collision(ball_pos, ball_vel, flipper_start, flipper_end)
        if collision:
            ball_pos = collision_pos  # Update ball position to the collision point
            reflect_ball(flipper_start, flipper_end, is_flipper=True, flipper_velocity=flipper_velocity)
            break

    # Check for collisions with the playfield boundaries
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


# Check collisions with all ramps
def check_ramp_collision():
    global ball_pos, ball_vel
    for ramp in ramps:
        ramp.check_collision(ball_pos, ball_vel)



###
### Draw Funktionen ###
###

# Zeichnet die Kugel an ihrer aktuellen Position auf dem Spielfeld
def draw_ball():
    # Zeichnet die Kugel
    pygame.draw.circle(window, pygame.Color(ball_color.lower()), (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

    # Zeichnet eine Linie, die die Richtung der Kugelgeschwindigkeit anzeigt
    direction_length = 30 * math.sqrt(ball_vel[0]**2 + ball_vel[1]**2) / 100
    angle = math.atan2(ball_vel[1], ball_vel[0])
    end_pos = (ball_pos[0] + direction_length * math.cos(angle), ball_pos[1] + direction_length * math.sin(angle))
    pygame.draw.line(window, RED, (ball_pos[0], ball_pos[1]), end_pos, 2)


# Zeichnet den Flipper an der gegebenen Position und mit dem gegebenen Winkel
def draw_flipper(position, angle, is_right, color):
    # Berechnet die Start- und Endpunkte des Flippers basierend auf seiner Position, dem Winkel und der Ausrichtung
    start_x, start_y = position

    # Bestimmt die Richtung des Flippers basierend darauf, ob er rechts oder links ist
    end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
    end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))

    # Zeichnet eine Linie, die den Flipper darstellt
    pygame.draw.line(window, color, (start_x, start_y), (end_x, end_y), FLIPPER_WIDTH)



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
    for ramp in ramps:
        ramp.draw(window)


# Draw the separator line
def draw_separator():
    pygame.draw.rect(window, SEPARATOR_COLOR, (SEPARATOR_POS, 0, SEPARATOR_WIDTH, HEIGHT))


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
        pygame.draw.line(window, RED, (ball_pos[0], ball_pos[1]), end_pos, 2)



###
### Flipper Animation
###

# Target angles for the flippers
left_flipper_target_angle = -30
right_flipper_target_angle = -30

# Update flippers to animate their movement
def update_flippers():
    global left_flipper_angle, right_flipper_angle

    # Update left flipper angle
    if left_flipper_angle < left_flipper_target_angle:
        left_flipper_angle = min(left_flipper_angle + FLIPPER_ANGLE_STEP, left_flipper_target_angle)
    elif left_flipper_angle > left_flipper_target_angle:
        left_flipper_angle = max(left_flipper_angle - FLIPPER_ANGLE_STEP, left_flipper_target_angle)

    # Update right flipper angle
    if right_flipper_angle < right_flipper_target_angle:
        right_flipper_angle = min(right_flipper_angle + FLIPPER_ANGLE_STEP, right_flipper_target_angle)
    elif right_flipper_angle > right_flipper_target_angle:
        right_flipper_angle = max(right_flipper_angle - FLIPPER_ANGLE_STEP, right_flipper_target_angle)


###
### Event Handler ###
###

# Überprüft, welche Tasten gedrückt wurden und führt entsprechende Aktionen aus.
def handle_keys():
    global left_flipper_target_angle, right_flipper_target_angle, left_flipper_active, right_flipper_active, left_flipper_color, right_flipper_color, ball_pos, ball_vel, GAME_STARTED
    keys = pygame.key.get_pressed()

    # Left flipper
    if keys[pygame.K_a]:
        if not left_flipper_active:
            left_flipper_target_angle = FLIPPER_MAX_ANGLE
            left_flipper_active = True
            left_flipper_color = ACTIVE_FLIPPER_COLOUR  # Change color
    else:
        left_flipper_target_angle = -30
        left_flipper_active = False
        left_flipper_color = FLIPPER_COLOUR  # Reset color

    # Right flipper
    if keys[pygame.K_d]:
        if not right_flipper_active:
            right_flipper_target_angle = FLIPPER_MAX_ANGLE
            right_flipper_active = True
            right_flipper_color = ACTIVE_FLIPPER_COLOUR  # Change color
    else:
        right_flipper_target_angle = -30
        right_flipper_active = False
        right_flipper_color = FLIPPER_COLOUR  # Reset color

    # Reset game
    if keys[pygame.K_r]:
        ball_pos = [GAME_WIDTH // 2, BALL_START_Y]
        ball_vel = [0, 0]
        GAME_STARTED = False



# Überprüft, ob die Maus geklickt wurde, und führt entsprechende Aktionen aus
def handle_mouse():
    global ball_pos
    if pygame.mouse.get_pressed()[0] and not GAME_STARTED:
        mouse_x, mouse_y = pygame.mouse.get_pos()
        # Setzt die Startposition der Kugel
        if mouse_x < GAME_WIDTH:
            ball_pos = list(pygame.mouse.get_pos())



# Event Handler for Buttons
def handle_buttons(event):
    global GAME_STARTED, ball_pos, ball_vel, is_pause_menu_open, pause_panel

    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        if is_pause_menu_open:
            is_pause_menu_open = False
            if pause_panel:
                pause_panel.kill()
                pause_panel = None
        else:
            pause_menu()
        return

    if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if event.ui_element == pause_button:
            pause_menu()
        elif event.ui_element == reset_button:
            ball_pos = [GAME_WIDTH // 2, BALL_START_Y]
            ball_vel = [0, 0]
            GAME_STARTED = False
        elif event.ui_element == play_button:
            if ball_pos != [GAME_WIDTH // 2, BALL_START_Y]:  
                angle_rad = math.radians(BALL_ANGLE + 90)
                ball_vel = [
                    INITIAL_BALL_IMPULSE * math.cos(angle_rad),
                    INITIAL_BALL_IMPULSE * math.sin(angle_rad)
                ]
                GAME_STARTED = True
        elif event.ui_element == continue_button:
            is_pause_menu_open = False
            if pause_panel:
                pause_panel.kill()
                pause_panel = None
        elif event.ui_element == quit_button:
            pygame.quit()
            sys.exit()



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

ball_settings_label = UITextBox(
    relative_rect=pygame.Rect((GAME_WIDTH + 14, 240), (SLIDER_WIDTH - 8, 310)),
    html_text="Ball Settings:",
    manager=manager,
    object_id=ObjectID(class_id='@text_box', object_id='#ball_label')
)

# Beschriftung für den initialen Impuls-Slider
initial_impulse_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 26, 300), (SLIDER_WIDTH - 8, 30)),
    text=f"Initial Impulse: {INITIAL_BALL_IMPULSE / METER:.2f} m/s",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#ii_label')
)

# Initialisierung des Sliders für den initialen Impuls
initial_impulse_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 24, 330), (SLIDER_WIDTH - 28, SLIDER_HEIGHT)),
    start_value=INITIAL_BALL_IMPULSE / METER,
    value_range=(SLIDER_MIN_VALUE, SLIDER_MAX_VALUE),
    manager=manager,
    object_id=ObjectID(class_id='@horizontal_slider', object_id='#ii_slider')
)

# Beschriftung für den Schwerkraftstärke-Slider
gravity_strength_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 26, 380), (SLIDER_WIDTH - 8, 30)),
    text=f"Gravity Strength: {GRAVITY / METER / 9.81:.2f}",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#gs_label')
)

# Initialisierung des Sliders für die Schwerkraftstärke
gravity_strength_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 24, 410), (SLIDER_WIDTH - 28, SLIDER_HEIGHT)),
    start_value=GRAVITY_STRENGTH,
    value_range=(SLIDER_MIN_GRAVITY, SLIDER_MAX_GRAVITY),
    manager=manager,
    object_id=ObjectID(class_id='@horizontal_slider', object_id='#gs_slider')
)

# Beschriftung für den Abschusswinkel-Slider
launch_angle_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 26, 460), (SLIDER_WIDTH - 8, 30)),
    text=f"Launch Angle: {BALL_ANGLE:.2f} degrees",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#la_label')
)

# Initialisierung des Sliders für den Abschusswinkel der Kugel
launch_angle_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 24, 490), (SLIDER_WIDTH - 28, SLIDER_HEIGHT)),
    start_value=BALL_ANGLE,
    value_range=(SLIDER_MIN_ANGLE, SLIDER_MAX_ANGLE),
    manager=manager,
    object_id=ObjectID(class_id='@horizontal_slider', object_id='#la_slider')
)

# Play Button
play_button = UIButton(
    relative_rect=pygame.Rect((WIDTH - SLIDER_WIDTH - 8, HEIGHT - 130), (SLIDER_WIDTH - 8, 65)),
    text="Play",
    manager=manager,
    object_id=ObjectID(class_id='button', object_id='#play_button')
)

# Pause Button
pause_button = UIButton(
    relative_rect=pygame.Rect((WIDTH - SLIDER_WIDTH - 8, HEIGHT - 60), (SLIDER_WIDTH / 2 - 4, 50)),
    text="Pause",
    manager=manager,
    object_id=ObjectID(class_id='button', object_id='#pause_button')
)

# Reset Button
reset_button = UIButton(
    relative_rect=pygame.Rect((WIDTH - SLIDER_WIDTH / 2 - 8, HEIGHT - 60), (SLIDER_WIDTH / 2 - 8, 50)),
    text="Reset",
    manager=manager,
    object_id=ObjectID(class_id='button', object_id='#reset_button')
)



###
### Pause Menu ###
###

# Zeigt ein Popup-Fenster mit den Spielsteuerungen an
def pause_menu():
    global is_pause_menu_open, pause_panel, continue_button, quit_button, volume_slider, volume_label, volume_value_label
    is_pause_menu_open = True
    set_gui_visibility(False)

    padding = 48

    # Erstellt ein Panel, das das gesamte Fenster abdeckt
    pause_panel = UIPanel(
        relative_rect=pygame.Rect(0, 0, WIDTH, HEIGHT),
        manager=manager
    )

    # Header
    menu_title = UILabel(
        relative_rect=pygame.Rect((32, 32), (WIDTH, 100)),
        text=f"Pause Menu",
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@label', object_id='#menu_title')
    )

    controls_text = "Controls:"
    dropdown_text = "Ball Colour:"
    volume_text = "Volume:" + str(int(pygame.mixer.music.get_volume() * 100))

    # Spielsteuerung
    controls_label = UILabel(
        relative_rect=pygame.Rect(padding + 2, 150, WIDTH, 30),
        text=controls_text,
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@label', object_id='#menu_label')
    )

    controls_list = UITextBox(
        relative_rect=pygame.Rect((padding, 190), (WIDTH - 64 - 32, 170)),
        html_text="A - Activate left flipper<br>D - Activate right flipper<br>R - Reset game<br>ESC - Pause/Continue Game",
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@text_box', object_id='#controls_list')
    )
    
    # Dropdown Menü für die Farbe der Kugel
    dropdown_label = UILabel(
        relative_rect=pygame.Rect(padding + 2, 400, WIDTH, 30),
        text=dropdown_text,
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@label', object_id='#menu_label')
    )

    ball_preview_width = 48
    dropdown_width = WIDTH - padding - padding - 32 - ball_preview_width

    dropdown = UIDropDownMenu(
        options_list=['White', 'Red', 'Green', 'Blue', 'Purple', 'Orange', 'Yellow'],
        starting_option=ball_color,
        relative_rect=pygame.Rect(padding, 440, dropdown_width, 50),
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@dropdown', object_id='#ball_dropdown')
    )

    # Funktion zum Aktualisieren der Vorschau der Kugel
    def update_ball_preview(color):
        global ball_color
        ball_color = color

        # Neue Oberfläche für die Kugelvorschau erstellen
        ball_preview_surface = pygame.Surface((ball_preview_width, ball_preview_width), pygame.SRCALPHA)
        ball_preview_surface.fill((0, 0, 0, 0))  # Transparenter Hintergrund
        pygame.draw.circle(ball_preview_surface, pygame.Color(color.lower()), (ball_preview_width // 2, ball_preview_width // 2), ball_preview_width // 2)

        ball_preview_label.set_image(ball_preview_surface)

    # Vorschau der Kugel
    ball_preview_label = UILabel(
        relative_rect=pygame.Rect(padding + dropdown_width + 28, 440, ball_preview_width, ball_preview_width),
        text="",
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@ball_preview', object_id='#ball_preview')
    )

    # Initiale runde Kugelvorschau zeichnen
    update_ball_preview(ball_color)

    # Volume-Slider hinzufügen
    volume_label = UILabel(
        relative_rect=pygame.Rect(padding + 2, 520, 200, 30),
        text="Volume:",
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@label', object_id='#menu_label')
    )

    volume_value_label = UILabel(
        relative_rect=pygame.Rect(dropdown_width + padding + 28, 562, 50, SLIDER_HEIGHT + 12 - 4),
        text=str(int(pygame.mixer.music.get_volume() * 100)),
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@label', object_id='#volume_value')
    )

    volume_slider = UIHorizontalSlider(
        relative_rect=pygame.Rect(padding, 560, dropdown_width, SLIDER_HEIGHT + 12),
        start_value=pygame.mixer.music.get_volume() * 100,
        value_range=(0, 100),
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@horizontal_slider', object_id='#volume_slider')
    )

    # Fügt den "Fortsetzen"-Button hinzu
    continue_button = UIButton(
        relative_rect=pygame.Rect((padding, HEIGHT - 120), (250, 80)),
        text="Continue",
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='', object_id='#continue_button')
    )

    # Fügt den "Beenden"-Button hinzu
    quit_button = UIButton(
        relative_rect=pygame.Rect((WIDTH - padding - 200, HEIGHT - 100), (200, 60)),
        text="Quit",
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='', object_id='#quit_button')
    )

    # Aktiviert das Menü
    is_running = True
    while is_running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    is_running = False
                    is_pause_menu_open = False
                    set_gui_visibility(True)
                    if pause_panel:
                        pause_panel.kill()
                        pause_panel = None
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == continue_button:
                    is_running = False
                    is_pause_menu_open = False
                    set_gui_visibility(True)
                    if pause_panel:
                        pause_panel.kill()
                        pause_panel = None
                elif event.ui_element == quit_button:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == dropdown:
                    update_ball_preview(event.text)
            elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == volume_slider:
                    volume = event.value / 100
                    pygame.mixer.music.set_volume(volume)
                    volume_value_label.set_text(str(int(volume * 100)))

            manager.process_events(event)

        manager.update(time_delta)
        window.fill(GAME_BG_COLOR)
        manager.draw_ui(window)
        pygame.display.flip()



###
### Game Loop ###
###

# Hauptspiel-Schleife, die alle anderen Funktionen aufruft und das Spiel steuert
def game_loop():
    global INITIAL_BALL_IMPULSE, GRAVITY_STRENGTH, GRAVITY, GAME_STARTED, BALL_ANGLE, is_pause_menu_open, pause_panel, pregame_label, ball_pos, ball_vel

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            handle_buttons(event)  # Handle button events, including ESC key press
            
            if is_pause_menu_open:
                manager.process_events(event)
            else:
                # Slider-Werte werden angewendet
                if event.type == pygame.USEREVENT:
                    if hasattr(event, 'user_type') and event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                        handle_buttons(event)
                    elif hasattr(event, 'user_type') and event.user_type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                        if event.ui_element == initial_impulse_slider:
                            INITIAL_BALL_IMPULSE = event.value * METER
                            initial_impulse_label.set_text(f"Initial Impulse: {INITIAL_BALL_IMPULSE / METER:.2f} m/s")
                        elif event.ui_element == gravity_strength_slider:
                            GRAVITY_STRENGTH = event.value
                            GRAVITY = 9.81 * METER * GRAVITY_STRENGTH
                            gravity_strength_label.set_text(f"Gravity Strength: {GRAVITY/METER/9.81:.2f}")
                        elif event.ui_element == launch_angle_slider:
                            BALL_ANGLE = event.value
                            launch_angle_label.set_text(f"Launch Angle: {BALL_ANGLE} degrees")

                # Mausereignisse nur verarbeiten, wenn das Pause-Menü nicht geöffnet ist
                if event.type == pygame.MOUSEBUTTONDOWN:
                    handle_mouse()

                manager.process_events(event)

        manager.update(dt)
        
        window.fill(GAME_BG_COLOR, rect=pygame.Rect(0, 0, GAME_WIDTH, HEIGHT))
        window.fill(GUI_BG_COLOR, rect=pygame.Rect(GAME_WIDTH, 0, UI_WIDTH, HEIGHT))

        if not GAME_STARTED:
            if pregame_label is None:
                pregame_label = UILabel(
                    relative_rect=pygame.Rect((GAME_WIDTH / 2 - 125, 25), (250, 50)),
                    text="Please place the ball",
                    manager=manager,
                    object_id=ObjectID(class_id='@label', object_id='#pregame_label')
                )
            draw_initial_trajectory()
        else:
            if pregame_label is not None:
                pregame_label.kill()
                pregame_label = None

        if not is_pause_menu_open:
            move_ball()
            draw_ball()
            handle_keys()
            check_collision()
            check_ramp_collision()
            draw_flipper(left_flipper_pos, left_flipper_angle, False, left_flipper_color)
            draw_flipper(right_flipper_pos, right_flipper_angle, True, right_flipper_color)
            draw_bumpers()
            draw_ramps() 
            draw_gui()
            draw_particles()
            update_particles()
            update_flippers()
            draw_separator()

            # Check if the ball has hit the bottom of the window
            if ball_pos[1] >= HEIGHT - BALL_RADIUS:
                result = end_game_screen(manager, window, clock, set_gui_visibility)
                if result == 'new_game':
                    ball_pos = [GAME_WIDTH // 2, BALL_START_Y]
                    ball_vel = [0, 0]
                    GAME_STARTED = False
                    set_gui_visibility(True)
                    continue

        manager.draw_ui(window)

        pygame.display.flip()
        pygame.display.set_caption(f"Flippernator3000 - FPS: {clock.get_fps():.2f}")
        clock.tick(60)


if __name__ == '__main__':
    # Setzt den Spielstatus auf nicht gestartet
    GAME_STARTED = False
    # Startet die Hauptspiel-Schleife
    game_loop()
