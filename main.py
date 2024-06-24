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
custom_font = pygame.font.Font('data/PressStart2P-Regular.ttf', 12)  # Adjust the font size as needed
clock = pygame.time.Clock()
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Load the background image
background_image = pygame.image.load('data/gui_bg.png')
pause_image = pygame.image.load('data/pause_bg_v2.png')

# Initialisiere den UI Manager und lade das Theme aus der theme.json-Datei
manager = pygame_gui.UIManager((WIDTH, HEIGHT), 'data/theme.json')

# Hintergrundmusik laden und abspielen
pygame.mixer.music.load('data/pinbolchill.mp3')
pygame.mixer.music.set_volume(0)
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
    initial_impulse_slider.visible = visible
    gravity_strength_slider.visible = visible
    launch_angle_slider.visible = visible
    initial_impulse_label.visible = visible
    gravity_strength_label.visible = visible
    launch_angle_label.visible = visible
    speed_value.visible = visible
    position_value.visible = visible
    play_button.visible = visible
    pause_button.visible = visible
    reset_button.visible = visible
    high_score_value.visible = visible

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

# Calculate the correct positions for the flipper ramps
flipper_length = FLIPPER_LENGTH - 10  # Adjust to ensure the ramp connects properly
left_flipper_ramp_end = (left_flipper_pos[0] + flipper_length * math.cos(math.radians(left_flipper_angle)),
                         left_flipper_pos[1] - flipper_length * math.sin(math.radians(left_flipper_angle)))
right_flipper_ramp_end = (right_flipper_pos[0] + flipper_length * math.cos(math.radians(right_flipper_angle)),
                          right_flipper_pos[1] - flipper_length * math.sin(math.radians(right_flipper_angle)))

# Adjust angles so ramps face the correct direction
left_ramp_angle = left_flipper_angle + 180
right_ramp_angle = right_flipper_angle + 60

# Function to calculate points for the triangular bumpers
def calculate_triangle_points(x, y, base, height, angle, is_right):
    angle_rad = math.radians(angle)
    base_x_offset = base * math.cos(angle_rad)
    base_y_offset = base * math.sin(angle_rad)
    height_y_offset = height * math.cos(angle_rad)

    if is_right:
        points = [
            (x, y),  # Bottom-left point
            (x + base_x_offset, y - base_y_offset),  # Bottom-right point
            (x + base_x_offset, y - base_y_offset - height_y_offset)  # Top point
        ]
    else:
        points = [
            (x, y),  # Bottom-right point
            (x - base_x_offset, y - base_y_offset),  # Bottom-left point
            (x - base_x_offset, y - base_y_offset - height_y_offset)  # Top point
        ]
    return points

FLIPPER_ANGLE = 30

# Initialisierung der Bumpers
bumpers = [
    # Kleine Bumper oben
    {'type': 'default', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [175, 325], 'radius': BUMPER_RADIUS, 'color': BUMPER_COLOUR_TIER_3, 'active': False, 'timer': 0, 'score': TIER_3, 'show_score': True},
    {'type': 'default', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [GAME_WIDTH - 175, 325], 'radius': BUMPER_RADIUS, 'color': BUMPER_COLOUR_TIER_3, 'active': False, 'timer': 0, 'score': TIER_3, 'show_score': True},
     {'type': 'default', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [100, 150], 'radius': BUMPER_RADIUS, 'color': BUMPER_COLOUR_TIER_3, 'active': False, 'timer': 0, 'score': TIER_3, 'show_score': True},
    {'type': 'default', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [GAME_WIDTH - 100, 150], 'radius': BUMPER_RADIUS, 'color': BUMPER_COLOUR_TIER_3, 'active': False, 'timer': 0, 'score': TIER_3, 'show_score': True},
    # Mini Bumper Außen
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [45, 300], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_2, 'active': False, 'timer': 0, 'score': TIER_2, 'show_score': False},
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [GAME_WIDTH - 45, 300], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_2, 'active': False, 'timer': 0, 'score': TIER_2, 'show_score': False},
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [45, 375], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_2, 'active': False, 'timer': 0, 'score': TIER_2, 'show_score': False},
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [GAME_WIDTH - 45, 375], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_2, 'active': False, 'timer': 0, 'score': TIER_2, 'show_score': False},
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [45, 450], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_2, 'active': False, 'timer': 0, 'score': TIER_2, 'show_score': False},
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [GAME_WIDTH - 45, 450], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_2, 'active': False, 'timer': 0, 'score': TIER_2, 'show_score': False},
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [45, 525], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_2, 'active': False, 'timer': 0, 'score': TIER_2, 'show_score': False},
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [GAME_WIDTH - 45, 525], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_2, 'active': False, 'timer': 0, 'score': TIER_2, 'show_score': False},
    #{'type': 'default', 'shape': BUMPER_TYPE_SQUARE, 'pos': [175, 450], 'radius': BUMPER_RADIUS * 1.15, 'color': BUMPER_COLOR_DEFAULT, 'active': False, 'timer': 0, 'score': TIER_3},
    #{'type': 'default', 'shape': BUMPER_TYPE_SQUARE, 'pos': [GAME_WIDTH - 175, 450], 'radius': BUMPER_RADIUS * 1.15, 'color': BUMPER_COLOR_DEFAULT, 'active': False, 'timer': 0, 'score': TIER_3},
    # Großer Bumper Mitte (500 Punkte)
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [GAME_WIDTH / 2, 400], 'radius': BUMPER_RADIUS * 1.5, 'color': BUMPER_COLOUR_TIER_2, 'active': False, 'timer': 0, 'score': TIER_2, 'show_score': True},
    # Großer Bumper Oben (1000 Punkte)
    {'type': 'increase', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [GAME_WIDTH / 2, 200], 'radius': BUMPER_RADIUS * 1.33, 'color': BUMPER_COLOUR_TIER_1, 'active': False, 'timer': 0, 'score': TIER_1, 'show_score': True},
    # Dreieckige Bumper Unten
    {'type': 'triangle', 'shape': BUMPER_TYPE_TRIANGLE, 'points': calculate_triangle_points(174, HEIGHT - 175, TRIANGLE_BUMPER_BASE, TRIANGLE_BUMPER_HEIGHT, FLIPPER_ANGLE, is_right=False), 'color': BUMPER_COLOR_TRIANGLE, 'active': False, 'timer': 0, 'score': TIER_4, 'show_score': False},
    {'type': 'triangle', 'shape': BUMPER_TYPE_TRIANGLE, 'points': calculate_triangle_points(GAME_WIDTH - 174, HEIGHT - 175, TRIANGLE_BUMPER_BASE, TRIANGLE_BUMPER_HEIGHT, FLIPPER_ANGLE, is_right=True), 'color': BUMPER_COLOR_TRIANGLE, 'active': False, 'timer': 0, 'score': TIER_4, 'show_score': False},
]

# Score
high_score = 0

def reset_high_score():
    global high_score
    high_score = 0



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
    Ramp(left_flipper_pos, left_ramp_angle, RAMP_LENGTH - 85),
    Ramp(right_flipper_pos, right_ramp_angle, RAMP_LENGTH - 85),
    # Spielfeld Rampen
    Ramp((174, 628), left_ramp_angle, RAMP_LENGTH - 115),
    Ramp((GAME_WIDTH - 174, 628), right_ramp_angle, RAMP_LENGTH - 115),
    Ramp((100, 585), 90, 350),
    Ramp((GAME_WIDTH - 100, 585), 90, 350),

    Ramp((174, 639), left_ramp_angle, RAMP_LENGTH - 102),
    Ramp((GAME_WIDTH - 174, 639), right_ramp_angle, RAMP_LENGTH - 102),
    Ramp((90, 590), 90, 355),
    Ramp((GAME_WIDTH - 90, 590), 90, 355),

    Ramp((GAME_WIDTH - 90, 237), 180, 10),
    Ramp((90, 237), 0, 10),
    Ramp((GAME_WIDTH - 172, 638), 90, 10),
    Ramp((172, 638), 90, 10),
    
   # Ramp((185, 500), -30, 75),
   # Ramp((GAME_WIDTH - 185, 500), -150, 75),
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
def reflect_ball_velocity(ball_pos, ball_vel, bumper):
    global ball_angular_vel, high_score

    if bumper['shape'] == BUMPER_TYPE_TRIANGLE:
        reflect_ball_from_triangle(ball_pos, ball_vel, bumper)
    else:
        bumper_pos = bumper['pos']
        angle_of_incidence = math.atan2(ball_pos[1] - bumper_pos[1], ball_pos[0] - bumper_pos[0])
        
        normal = (math.cos(angle_of_incidence), math.sin(angle_of_incidence))
        dot_product = ball_vel[0] * normal[0] + ball_vel[1] * normal[1]
        ball_vel[0] -= 2 * dot_product * normal[0]
        ball_vel[1] -= 2 * dot_product * normal[1]

        ball_vel[0] *= BUMPER_PROPERTIES[bumper['type']]['velocity_factor']
        ball_vel[1] *= BUMPER_PROPERTIES[bumper['type']]['velocity_factor']
        
        collision_vector = [ball_pos[0] - bumper_pos[0], ball_pos[1] - bumper_pos[1]]
        torque = (collision_vector[0] * ball_vel[1] - collision_vector[1] * ball_vel[0]) / (BALL_RADIUS ** 2)
        ball_angular_vel += torque

        distance = math.hypot(ball_pos[0] - bumper_pos[0], ball_pos[1] - bumper_pos[1])
        overlap = BALL_RADIUS + bumper['radius'] - distance
        if overlap > 0:
            ball_pos[0] += overlap * normal[0]
            ball_pos[1] += overlap * normal[1]

    add_particles(ball_pos)
    high_score += bumper['score']

    bumper['timer'] = 10


def reflect_ball_from_triangle(ball_pos, ball_vel, start, end):
    global ball_angular_vel, high_score

    normal = get_line_normal(start, end)
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    ball_to_midpoint = (midpoint[0] - ball_pos[0], midpoint[1] - ball_pos[1])

    if (ball_to_midpoint[0] * normal[0] + ball_to_midpoint[1] * normal[1]) > 0:
        normal = (-normal[0], -normal[1])

    dot_product = ball_vel[0] * normal[0] + ball_vel[1] * normal[1]
    ball_vel[0] -= 2 * dot_product * normal[0]
    ball_vel[1] -= 2 * dot_product * normal[1]

    ball_vel[0] *= BUMPER_PROPERTIES['triangle']['velocity_factor']
    ball_vel[1] *= BUMPER_PROPERTIES['triangle']['velocity_factor']

    collision_vector = [ball_pos[0] - midpoint[0], ball_pos[1] - midpoint[1]]
    torque = (collision_vector[0] * ball_vel[1] - collision_vector[1] * ball_vel[0]) / (BALL_RADIUS ** 2)
    ball_angular_vel += torque

    distance = point_line_distance(ball_pos, start, end)
    overlap = BALL_RADIUS - distance
    if overlap > 0:
        ball_pos[0] += overlap * normal[0]
        ball_pos[1] += overlap * normal[1]

    add_particles(ball_pos)
    high_score += 100


def reflect_ball(start, end, is_flipper=False, flipper_angular_velocity=0, flipper_moving=False):
    global ball_pos, ball_vel, ball_angular_vel

    # Calculate the normal vector of the line
    normal = get_line_normal(start, end)
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    ball_to_midpoint = (midpoint[0] - ball_pos[0], midpoint[1] - ball_pos[1])

    if (ball_to_midpoint[0] * normal[0] + ball_to_midpoint[1] * normal[1]) > 0:
        normal = (-normal[0], -normal[1])

    # Reflect velocity based on the normal
    dot_product = ball_vel[0] * normal[0] + ball_vel[1] * normal[1]
    ball_vel[0] -= 2 * dot_product * normal[0]
    ball_vel[1] -= 2 * dot_product * normal[1]

    # Apply the coefficient of restitution
    ball_vel[0] *= COEFFICIENT_OF_RESTITUTION
    ball_vel[1] *= COEFFICIENT_OF_RESTITUTION

    # Threshold to determine significant impact
    impact_threshold = BALL_RADIUS + 5

    if is_flipper and flipper_moving:
        # Calculate the distance from the flipper pivot
        distance_from_pivot = math.sqrt((ball_pos[0] - start[0])**2 + (ball_pos[1] - start[1])**2)

        # Calculate the linear velocity at the point of collision
        linear_velocity = distance_from_pivot * flipper_angular_velocity

        # Decrease velocity multiplier as the distance from the pivot increases
        velocity_multiplier = max(0.5, 1.5 - (distance_from_pivot / FLIPPER_LENGTH))

        # Apply momentum transfer from flipper to ball with adjusted multiplier
        ball_vel[0] += normal[0] * linear_velocity * velocity_multiplier
        ball_vel[1] += normal[1] * linear_velocity * velocity_multiplier

        # Add extra velocity if the ball is very close to the flipper
        if point_line_distance(ball_pos, start, end) <= impact_threshold:
            extra_velocity = FLIPPER_MOTION_MOMENTUM * linear_velocity
            ball_vel[0] += normal[0] * extra_velocity
            ball_vel[1] += normal[1] * extra_velocity

    if is_flipper:
        add_flipper_particles(ball_pos)

    # Apply torque based on the collision
    collision_vector = [ball_pos[0] - midpoint[0], ball_pos[1] - midpoint[1]]
    torque = (collision_vector[0] * ball_vel[1] - collision_vector[1] * ball_vel[0]) / (BALL_RADIUS ** 2)
    ball_angular_vel += torque

    # Ensure the ball does not penetrate the object too much
    while point_line_distance(ball_pos, start, end) <= BALL_RADIUS:
        ball_pos = [ball_pos[0] + normal[0] * 0.1, ball_pos[1] + normal[1] * 0.1]


# Reflektiert eine gegebene Geschwindigkeit an einer Fläche mit gegebenem Normalenvektor
def reflect(velocity, normal, is_flipper=False):
    # Berechnet das Skalarprodukt der Geschwindigkeit und des Normalenvektors
    dot_product = velocity[0] * normal[0] + velocity[1] * normal[1]
    
    # Berechnet den reflektierten Geschwindigkeitsvektor
    reflected_velocity = (
        (velocity[0] - 2 * dot_product * normal[0]) * (COEFFICIENT_OF_RESTITUTION if not is_flipper else 1),
        (velocity[1] - 2 * dot_product * normal[1]) * (COEFFICIENT_OF_RESTITUTION if not is_flipper else 1)
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
    
    check_bumper_collision(ball_pos, ball_vel)



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
    
    # Apply gravity parallel to the flipper angle
    ball_vel[0] += gravity_parallel * dt * math.cos(flipper_angle)
    ball_vel[1] += gravity_parallel * dt * math.sin(flipper_angle)

    # Ensure the ball rolls off the flipper naturally
    projected_pos = [ball_pos[0] + ball_vel[0] * dt, ball_pos[1] + ball_vel[1] * dt]
    dist_to_flipper = point_line_distance(projected_pos, flipper_start, flipper_end)

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
    for flipper_pos, angle, is_right, flipper_active, flipper_angular_velocity, flipper_moving in [
        (left_flipper_pos, left_flipper_angle, False, left_flipper_active, FLIPPER_ANGLE_STEP if left_flipper_active else 0, left_flipper_moving),
        (right_flipper_pos, right_flipper_angle, True, right_flipper_active, FLIPPER_ANGLE_STEP if right_flipper_active else 0, right_flipper_moving)]:

        start_x, start_y = flipper_pos
        end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
        end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))

        flipper_start = (start_x, start_y)
        flipper_end = (end_x, end_y)

        collision, collision_pos = check_continuous_collision(ball_pos, ball_vel, flipper_start, flipper_end)
        if collision:
            ball_pos = collision_pos  # Update ball position to the collision point
            reflect_ball(flipper_start, flipper_end, is_flipper=True, flipper_angular_velocity=flipper_angular_velocity, flipper_moving=flipper_moving)
            break

    # Check for collisions with the playfield boundaries
    if ball_pos[0] <= BALL_RADIUS or ball_pos[0] >= GAME_WIDTH - BALL_RADIUS:
        ball_vel[0] = -ball_vel[0] * COEFFICIENT_OF_RESTITUTION  # Reflect and reduce velocity based on COR
        ball_pos[0] = max(min(ball_pos[0], GAME_WIDTH - BALL_RADIUS), BALL_RADIUS)

    if ball_pos[1] <= BALL_RADIUS or ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1] * COEFFICIENT_OF_RESTITUTION  # Reflect and reduce velocity based on COR
        ball_pos[1] = max(min(ball_pos[1], HEIGHT - BALL_RADIUS), BALL_RADIUS)

        
# Check collisions with all ramps
def check_ramp_collision():
    global ball_pos, ball_vel
    for ramp in ramps:
        ramp.check_collision(ball_pos, ball_vel)
        

def check_bumper_collision(ball_pos, ball_vel):
    for bumper in bumpers:
        if bumper['shape'] == BUMPER_TYPE_CIRCLE or bumper['shape'] == BUMPER_TYPE_SQUARE:
            if math.hypot(ball_pos[0] - bumper['pos'][0], ball_pos[1] - bumper['pos'][1]) < BALL_RADIUS + bumper['radius']:
                if not bumper['active']:
                    bumper['active'] = True
                    bumper['timer'] = 10
                reflect_ball_velocity(ball_pos, ball_vel, bumper)
        elif bumper['shape'] == BUMPER_TYPE_TRIANGLE:
            for i in range(3):
                start = bumper['points'][i]
                end = bumper['points'][(i + 1) % 3]
                if point_line_distance(ball_pos, start, end) <= BALL_RADIUS:
                    if not bumper['active']:
                        bumper['active'] = True
                        bumper['timer'] = 10
                    reflect_ball_from_triangle(ball_pos, ball_vel, start, end)
                    break

            if point_in_triangle(ball_pos[0], ball_pos[1], bumper['points']):
                for i in range(3):
                    start = bumper['points'][i]
                    end = bumper['points'][(i + 1) % 3]
                    if point_line_distance(ball_pos, start, end) > BALL_RADIUS:
                        reflect_ball_from_triangle(ball_pos, ball_vel, start, end)
                        break

        if bumper['active']:
            bumper['timer'] -= 1
            if bumper['timer'] <= 0:
                bumper['active'] = False



###
### Helper Funktionen
###

# Berechnet den Abstand eines Punktes von einer Linie, definiert durch zwei Punkte
def point_line_distance(point, start, end):
    px, py = point
    sx, sy = start
    ex, ey = end

    # Line segment vector
    line_vec = (ex - sx, ey - sy)
    
    # Vector from start of line segment to the point
    point_vec = (px - sx, py - sy)
   
    # Length of the line segment
    line_len = math.sqrt(line_vec[0]**2 + line_vec[1]**2)
    
    # Normalized line vector
    line_unitvec = (line_vec[0] / line_len, line_vec[1] / line_len)

    # Projection of point vector onto the line
    proj_length = point_vec[0] * line_unitvec[0] + point_vec[1] * line_unitvec[1]

    # Constrain the projection length to the length of the line segment
    proj_length = max(0, min(proj_length, line_len))
    nearest = (sx + line_unitvec[0] * proj_length, sy + line_unitvec[1] * proj_length)

    # Calculate the distance from the point to the nearest point on the line segment
    dist = math.sqrt((px - nearest[0])**2 + (py - nearest[1])**2)
    return dist


# Check if point is inside triangle
def point_in_triangle(px, py, triangle_points):
    ax, ay = triangle_points[0]
    bx, by = triangle_points[1]
    cx, cy = triangle_points[2]

    # Compute vectors
    v0 = (cx - ax, cy - ay)
    v1 = (bx - ax, by - ay)
    v2 = (px - ax, py - ay)

    # Compute dot products
    dot00 = v0[0] * v0[0] + v0[1] * v0[1]
    dot01 = v0[0] * v1[0] + v0[1] * v1[1]
    dot02 = v0[0] * v2[0] + v0[1] * v2[1]
    dot11 = v1[0] * v1[0] + v1[1] * v1[1]
    dot12 = v1[0] * v2[0] + v1[1] * v2[1]

    # Compute barycentric coordinates
    inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
    u = (dot11 * dot02 - dot01 * dot12) * inv_denom
    v = (dot00 * dot12 - dot01 * dot02) * inv_denom

    # Check if point is in triangle
    return (u >= 0) and (v >= 0) and (u + v < 1)



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


# Draw a triangular bumper with custom points
def draw_triangle_bumper(window, bumper):
    if bumper['active']:
        scale_factor = BUMPER_TRIANGULAR_SCALE
    else:
        scale_factor = 1

    # Calculate the centroid of the triangle
    centroid_x = sum(point[0] for point in bumper['points']) / 3
    centroid_y = sum(point[1] for point in bumper['points']) / 3

    scaled_points = [
        (
            int(centroid_x + (point[0] - centroid_x) * scale_factor),
            int(centroid_y + (point[1] - centroid_y) * scale_factor)
        )
        for point in bumper['points']
    ]

    pygame.draw.polygon(window, pygame.Color(bumper['color']), scaled_points)
    centroid_x = sum(point[0] for point in scaled_points) / 3
    centroid_y = sum(point[1] for point in scaled_points) / 3

    if bumper['show_score']:
        label = custom_font.render(str(bumper['score']), True, pygame.Color('#121212'))
        label_rect = label.get_rect(center=(int(centroid_x), int(centroid_y) + 2))
        window.blit(label, label_rect)



# Zeichnet alle Bumper, basierend auf ihrem Aktivierungsstatus
def draw_bumpers():
    for bumper in bumpers:
        if bumper['shape'] == BUMPER_TYPE_CIRCLE:
            if bumper['active']:
                scaled_radius = int(bumper['radius'] * BUMPER_SCALE)
                pygame.draw.circle(window, bumper['color'], (int(bumper['pos'][0]), int(bumper['pos'][1])), scaled_radius)

                bumper['timer'] -= 1
                if bumper['timer'] <= 0:
                    bumper['active'] = False
            else:
                pygame.draw.circle(window, bumper['color'], (int(bumper['pos'][0]), int(bumper['pos'][1])), bumper['radius'])
        elif bumper['shape'] == BUMPER_TYPE_SQUARE:
            if bumper['active']:
                scaled_radius = int(bumper['radius'] * BUMPER_SCALE)
                pygame.draw.rect(window, pygame.Color(bumper['color']), 
                                 (bumper['pos'][0] - scaled_radius, bumper['pos'][1] - scaled_radius, scaled_radius * 2, scaled_radius * 2))
                
                bumper['timer'] -= 1
                if bumper['timer'] <= 0:
                    bumper['active'] = False
            else:
                pygame.draw.rect(window, pygame.Color(bumper['color']), 
                                 (bumper['pos'][0] - bumper['radius'], bumper['pos'][1] - bumper['radius'], bumper['radius'] * 2, bumper['radius'] * 2))
        elif bumper['shape'] == BUMPER_TYPE_TRIANGLE:
            draw_triangle_bumper(window, bumper)
        
        if bumper['show_score']:
            label = custom_font.render(str(bumper['score']), True, pygame.Color('#121212'))
            label_rect = label.get_rect(center=(int(bumper['pos'][0]), int(bumper['pos'][1]) + 2))
            window.blit(label, label_rect)



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

# Initialize flipper_moving states
left_flipper_moving = False
right_flipper_moving = False

def update_flippers():
    global left_flipper_angle, right_flipper_angle, left_flipper_moving, right_flipper_moving

    # Update left flipper angle
    if left_flipper_angle < left_flipper_target_angle:
        left_flipper_angle = min(left_flipper_angle + FLIPPER_ANGLE_STEP, left_flipper_target_angle)
        left_flipper_moving = True
    elif left_flipper_angle > left_flipper_target_angle:
        left_flipper_angle = max(left_flipper_angle - FLIPPER_ANGLE_STEP, left_flipper_target_angle)
        left_flipper_moving = True
    else:
        left_flipper_moving = False

    # Update right flipper angle
    if right_flipper_angle < right_flipper_target_angle:
        right_flipper_angle = min(right_flipper_angle + FLIPPER_ANGLE_STEP, right_flipper_target_angle)
        right_flipper_moving = True
    elif right_flipper_angle > right_flipper_target_angle:
        right_flipper_angle = max(right_flipper_angle - FLIPPER_ANGLE_STEP, right_flipper_target_angle)
        right_flipper_moving = True
    else:
        right_flipper_moving = False



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

# High score value
high_score_value = UITextBox(
    relative_rect=pygame.Rect((GAME_WIDTH + 12, 48), (UI_WIDTH - 28, 80)),
    html_text="0",
    manager=manager,
    object_id=ObjectID(class_id='@text_box', object_id='#highscore_value')
)

# Zeichnet die grafische Benutzeroberfläche (GUI) auf das Fenster
def draw_gui():
    global pregame_label
    # Zeichnet den Hintergrund des GUI-Bereichs
    position_text = f'X: {ball_pos[0]:.0f} Y: {ball_pos[1]:.0f}'
    speed = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2) / 100
    speed_text = f'{speed:.1f}'
    high_score_text = f'{high_score}'

    position_value.set_text(position_text)
    speed_value.set_text(speed_text)
    high_score_value.set_text(high_score_text)

    # Tooltip vor dem Spielstart
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

position_value = UITextBox(
    relative_rect=pygame.Rect((GAME_WIDTH + 12, 192), (150, 40)),
    html_text="X: 0 Y: 0",
    manager=manager,
    object_id=ObjectID(class_id='@text_box', object_id='#position_value')
)

speed_value = UITextBox(
    relative_rect=pygame.Rect((GAME_WIDTH + 184, 192), (102, 40)),
    html_text="0.00",
    manager=manager,
    object_id=ObjectID(class_id='@text_box', object_id='#speed_value')
)

# Beschriftung für den initialen Impuls-Slider
initial_impulse_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 41, 340), (SLIDER_WIDTH - 8, 30)),
    text=f"Initial Speed: {INITIAL_BALL_IMPULSE / METER:.1f} m/s",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#ii_label')
)

# Initialisierung des Sliders für den initialen Impuls
initial_impulse_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 39, 370), (SLIDER_WIDTH - 28, SLIDER_HEIGHT)),
    start_value=INITIAL_BALL_IMPULSE / METER,
    value_range=(SLIDER_MIN_VALUE, SLIDER_MAX_VALUE),
    manager=manager,
    object_id=ObjectID(class_id='@horizontal_slider', object_id='#ii_slider')
)

# Beschriftung für den Schwerkraftstärke-Slider
gravity_strength_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 41, 420), (SLIDER_WIDTH - 8, 30)),
    text=f"Gravity Strength: {GRAVITY / METER / 9.81:.1f}",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#gs_label')
)

# Initialisierung des Sliders für die Schwerkraftstärke
gravity_strength_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 39, 450), (SLIDER_WIDTH - 28, SLIDER_HEIGHT)),
    start_value=GRAVITY_STRENGTH,
    value_range=(SLIDER_MIN_GRAVITY, SLIDER_MAX_GRAVITY),
    manager=manager,
    object_id=ObjectID(class_id='@horizontal_slider', object_id='#gs_slider')
)

# Beschriftung für den Abschusswinkel-Slider
launch_angle_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 41, 500), (SLIDER_WIDTH - 8, 30)),
    text=f"Launch Angle: {BALL_ANGLE:.1f} deg",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#la_label')
)

# Initialisierung des Sliders für den Abschusswinkel der Kugel
launch_angle_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 39, 530), (SLIDER_WIDTH - 28, SLIDER_HEIGHT)),
    start_value=BALL_ANGLE,
    value_range=(SLIDER_MIN_ANGLE, SLIDER_MAX_ANGLE),
    manager=manager,
    object_id=ObjectID(class_id='@horizontal_slider', object_id='#la_slider')
)

# Play Button
play_button = UIButton(
    relative_rect=pygame.Rect((WIDTH - SLIDER_WIDTH - 16, HEIGHT - 150), (SLIDER_WIDTH - 12, 65)),
    text="Play",
    manager=manager,
    object_id=ObjectID(class_id='button', object_id='#play_button')
)

# Pause Button
pause_button = UIButton(
    relative_rect=pygame.Rect((WIDTH - SLIDER_WIDTH - 16, HEIGHT - 80), (SLIDER_WIDTH / 2 - 8, 50)),
    text="Pause",
    manager=manager,
    object_id=ObjectID(class_id='button', object_id='#pause_button')
)

# Reset Button
reset_button = UIButton(
    relative_rect=pygame.Rect((WIDTH - SLIDER_WIDTH / 2 - 20, HEIGHT - 80), (SLIDER_WIDTH / 2 - 8, 50)),
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

    # Create a surface for the pause menu
    pause_surface = pygame.Surface((WIDTH, HEIGHT))
    pause_surface.blit(pause_image, (0, 0))

    padding = 48

    # Erstellt ein Panel, das das gesamte Fenster abdeckt
    pause_panel = UIPanel(
        relative_rect=pygame.Rect(0, 0, WIDTH, HEIGHT),
        manager=manager
    )

    ball_preview_width = 48
    dropdown_width = WIDTH - padding - padding - 64 - ball_preview_width

    dropdown = UIDropDownMenu(
        options_list=['White', 'Red', 'Green', 'Blue', 'Purple', 'Orange', 'Yellow'],
        starting_option=ball_color,
        relative_rect=pygame.Rect(padding + 24, 480, dropdown_width, 50),
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
        relative_rect=pygame.Rect(padding + dropdown_width + 32, 480, ball_preview_width, ball_preview_width),
        text="",
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@ball_preview', object_id='#ball_preview')
    )

    # Initiale runde Kugelvorschau zeichnen
    update_ball_preview(ball_color)

    volume_value_label = UILabel(
        relative_rect=pygame.Rect(dropdown_width + padding + 32, 627, 50, SLIDER_HEIGHT + 12 - 4),
        text=str(int(pygame.mixer.music.get_volume() * 100)),
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@label', object_id='#volume_value')
    )

    volume_slider = UIHorizontalSlider(
        relative_rect=pygame.Rect(padding + 24, 625, dropdown_width, SLIDER_HEIGHT + 12),
        start_value=pygame.mixer.music.get_volume() * 100,
        value_range=(0, 100),
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@horizontal_slider', object_id='#volume_slider')
    )

    # Fügt den "Fortsetzen"-Button hinzu
    continue_button = UIButton(
        relative_rect=pygame.Rect((WIDTH / 2 - 220, HEIGHT - 80), (200, 60)),
        text="Continue",
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='', object_id='#play_button')
    )

    # Fügt den "Beenden"-Button hinzu
    quit_button = UIButton(
        relative_rect=pygame.Rect((WIDTH / 2 + 20, HEIGHT - 80), (200, 60)),
        text="Quit",
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='', object_id='#pause_button')
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

            if not GAME_STARTED:
                pregame_label.visible = False

        manager.update(time_delta)
        window.blit(pause_surface, (0, 0))
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
                            initial_impulse_label.set_text(f"Initial Speed: {INITIAL_BALL_IMPULSE / METER:.1f} m/s")
                        elif event.ui_element == gravity_strength_slider:
                            GRAVITY_STRENGTH = event.value
                            GRAVITY = 9.81 * METER * GRAVITY_STRENGTH
                            gravity_strength_label.set_text(f"Gravity Strength: {GRAVITY/METER/9.81:.1f}")
                        elif event.ui_element == launch_angle_slider:
                            BALL_ANGLE = event.value
                            launch_angle_label.set_text(f"Launch Angle: {BALL_ANGLE} deg")

                # Mausereignisse nur verarbeiten, wenn das Pause-Menü nicht geöffnet ist
                if event.type == pygame.MOUSEBUTTONDOWN:
                    handle_mouse()

                manager.process_events(event)

        manager.update(dt)
        
        window.fill(GAME_BG_COLOR, rect=pygame.Rect(0, 0, GAME_WIDTH, HEIGHT))
        window.fill(GUI_BG_COLOR, rect=pygame.Rect(GAME_WIDTH, 0, UI_WIDTH, HEIGHT))

        # Blit the background image
        window.blit(background_image, (GAME_WIDTH, 0))

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
                result = end_game_screen(manager, window, clock, set_gui_visibility, high_score)
                if result == 'new_game':
                    ball_pos = [GAME_WIDTH // 2, BALL_START_Y]
                    ball_vel = [0, 0]
                    GAME_STARTED = False
                    reset_high_score()
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
