##### Imports #####
###

import random
import pygame
import sys
import math
import os
from pygame.locals import *
from config import *
import pygame_gui
import pygame_gui.data
from pygame_gui.elements import UIHorizontalSlider, UILabel, UITextBox, UIDropDownMenu, UIButton, UIPanel
from pygame_gui.core import ObjectID
from endgame import end_game_screen



###
### Resources ###
###

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

config_file = resource_path('config.py')
highscore_file = resource_path('highscore.txt')
icon_ico_file = resource_path('icon.ico')
icon_png_file = resource_path('icon.png')
gameover_bg = pygame.image.load(resource_path('data/gameover_bg.png'))
gui_bg = pygame.image.load(resource_path('data/gui_bg_v2.png'))
pause_bg = pygame.image.load(resource_path('data/pause_bg_v2.png'))
pinbolchill_mp3 = resource_path('data/pinbolchill.mp3')
press_start_font = resource_path('data/PressStart2P-Regular.ttf')
theme_file = resource_path('data/theme.json')



###
### Initialisierungen ###
###

# Initialisierung von Pygame für Grafik und Schriftarten
pygame.init()
pygame.font.init()
pygame.mixer.init()
icon_image = pygame.image.load('icon.png')
pygame.display.set_icon(icon_image)
font = pygame.font.SysFont(None, 24)
custom_font = pygame.font.Font('data/PressStart2P-Regular.ttf', 12)  
clock = pygame.time.Clock()
window = pygame.display.set_mode((WIDTH, HEIGHT))

# Laden der Hintergrundbilder
background_image = pygame.image.load('data/gui_bg_v2.png')
pause_image = pygame.image.load('data/pause_bg_v2.png')

# Initialisiere den UI Manager und lade das Theme aus der theme.json-Datei
manager = pygame_gui.UIManager((WIDTH, HEIGHT), 'data/theme.json')

# Hintergrundmusik laden und abspielen
pygame.mixer.music.load('data/pinbolchill.mp3')
pygame.mixer.music.set_volume(.5)
pygame.mixer.music.play(-1) 

# Load sound effects
sound_effect = pygame.mixer.Sound('data/hit.wav')
sound_bumper = pygame.mixer.Sound('data/bumper.mp3')

# Set volume if necessary
sound_effect_volume = 0.3
sound_effect.set_volume(sound_effect_volume)
sound_bumper.set_volume(sound_effect_volume)


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
    # Sichtbarkeit der Slider
    initial_impulse_slider.sliding_button.visible = visible
    gravity_strength_slider.sliding_button.visible = visible
    launch_angle_slider.sliding_button.visible = visible
    initial_impulse_slider.visible = visible
    gravity_strength_slider.visible = visible
    launch_angle_slider.visible = visible
    # Sichtbarkeit der Labels
    initial_impulse_label.visible = visible
    gravity_strength_label.visible = visible
    launch_angle_label.visible = visible
    # Sichtbarkeit der Textboxen und Buttons
    speed_value.visible = visible
    position_value.visible = visible
    play_button.visible = visible
    pause_button.visible = visible
    reset_button.visible = visible
    score_value.visible = visible
    high_score_value.visible = visible

# Positionierung der Rampen
ramp_left_start = (58, HEIGHT - 240)
ramp_left_end = (ramp_left_start[0] + RAMP_LENGTH * math.cos(math.radians(RAMP_ANGLE)),
                 ramp_left_start[1] - RAMP_LENGTH * math.sin(math.radians(RAMP_ANGLE)))

ramp_right_start = (GAME_WIDTH - 58, HEIGHT - 240)
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

# Berechnung der korrekten Positionen für die Flipper-Rampenenden basierend auf den Winkeln
left_flipper_ramp_end = (left_flipper_pos[0] * math.cos(math.radians(left_flipper_angle)),
                         left_flipper_pos[1] * math.sin(math.radians(left_flipper_angle)))
right_flipper_ramp_end = (right_flipper_pos[0] * math.cos(math.radians(right_flipper_angle)),
                          right_flipper_pos[1] * math.sin(math.radians(right_flipper_angle)))

# Anpassung der Winkel, damit die Rampen in die richtige Richtung zeigen
left_ramp_angle = left_flipper_angle + 180
right_ramp_angle = right_flipper_angle + 60

# Punktestand (Score)
high_score = 0
score = 0

# Funktion zum Zurücksetzen des Punktestands
def reset_score():
    global score
    score = 0
    
# Funktion zum Speichern des Highscores
def save_high_score():
    with open('highscore.txt', 'w') as file:
        file.write(str(high_score))

# Funktion zum Laden des Highscores
def load_high_score():
    global high_score
    try:
        with open('highscore.txt', 'r') as file:
            high_score = int(file.read())
    except FileNotFoundError:
        high_score = 0

# Update des Highscores
def update_high_score():
    global high_score, score
    if score > high_score:
        high_score = score
        save_high_score()



###
### Bumpers
###

# Funktion zur Berechnung der Punkte für dreieckige Bumper
def calculate_triangle_points(x, y, base, height, angle, is_right):
    angle_rad = math.radians(angle)
    base_x_offset = base * math.cos(angle_rad)
    base_y_offset = base * math.sin(angle_rad)
    height_y_offset = height * math.cos(angle_rad)

    if is_right:
        points = [
            (x, y),
            (x + base_x_offset, y - base_y_offset),
            (x + base_x_offset, y - base_y_offset - height_y_offset)
        ]
    else:
        points = [
            (x, y),
            (x - base_x_offset, y - base_y_offset),
            (x - base_x_offset, y - base_y_offset - height_y_offset)
        ]
    return points

# Initialisierung der Bumpers
bumpers = [
    # Mini Bumper Außen
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [15, 300], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_3, 'active': False, 'timer': 0, 'score': TIER_3, 'show_score': False},
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [50, 375], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_3, 'active': False, 'timer': 0, 'score': TIER_3, 'show_score': False},
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [15, 450], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_3, 'active': False, 'timer': 0, 'score': TIER_3, 'show_score': False},
    {'type': 'decrease', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [50, 525], 'radius': BUMPER_RADIUS / 3, 'color': BUMPER_COLOUR_TIER_3, 'active': False, 'timer': 0, 'score': TIER_3, 'show_score': False},
    
    # Große Bumper Oben (1000 Punkte)
    {'type': 'increase', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [140, 70], 'radius': BUMPER_RADIUS * 1.1, 'color': BUMPER_COLOUR_TIER_1, 'active': False, 'timer': 0, 'score': TIER_1, 'show_score': True, 'max_velocity': MAX_BUMPER_SPEED},
    {'type': 'increase', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [260, 70], 'radius': BUMPER_RADIUS * 1.1, 'color': BUMPER_COLOUR_TIER_1, 'active': False, 'timer': 0, 'score': TIER_1, 'show_score': True, 'max_velocity': MAX_BUMPER_SPEED},
    
    # Großer Bumper Oben Mitte (500 Punkte)
    {'type': 'increase', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [200, 140], 'radius': BUMPER_RADIUS * 1, 'color': BUMPER_COLOUR_TIER_2, 'active': False, 'timer': 0, 'score': TIER_2, 'show_score': True},
    
    # Dreieckige Bumper Unten
    {'type': 'triangle', 'shape': BUMPER_TYPE_TRIANGLE, 'points': calculate_triangle_points(150, HEIGHT - 200, TRIANGLE_BUMPER_BASE, TRIANGLE_BUMPER_HEIGHT, FLIPPER_ANGLE, is_right=False), 'color': BUMPER_COLOR_TRIANGLE, 'active': False, 'timer': 0, 'score': TIER_4, 'show_score': False},
    {'type': 'triangle', 'shape': BUMPER_TYPE_TRIANGLE, 'points': calculate_triangle_points(GAME_WIDTH - 146, HEIGHT - 202, TRIANGLE_BUMPER_BASE, TRIANGLE_BUMPER_HEIGHT, FLIPPER_ANGLE, is_right=True), 'color': BUMPER_COLOR_TRIANGLE, 'active': False, 'timer': 0, 'score': TIER_4, 'show_score': False},
]



###
### Ramps
###

# Klasse für die Rampen im Spielfeld
class Ramp:
    def __init__(self, start_pos, angle, length, width=RAMP_WIDTH):
        # Initialisiert eine Rampe mit Startposition, Winkel und Länge
        self.start_pos = start_pos
        self.angle = angle
        self.length = length
        self.width = width
        # Berechnet die Endposition der Rampe basierend auf dem Winkel und der Länge
        self.end_pos = (
            start_pos[0] + length * math.cos(math.radians(angle)),
            start_pos[1] - length * math.sin(math.radians(angle))
        )

    def draw(self, window, color=WHITE):
        # Zeichnet die Rampe als Linie
        pygame.draw.line(window, color, self.start_pos, self.end_pos, self.width)
    
    # Überprüft die Kollision der Kugel mit der Rampe
    def check_collision(self, ball_pos, ball_vel):
        if point_line_distance(ball_pos, self.start_pos, self.end_pos) <= BALL_RADIUS:
            reflect_ball(self.start_pos, self.end_pos)
            sound_effect.play()


ball_radius_ramps = BALL_RADIUS * 2 + 2

# Initialisierung der Rampen im Spielfeld
ramps = [
    # Flipper Rampen
    Ramp(ramp_left_end, left_ramp_angle, RAMP_LENGTH, 6),
    Ramp(ramp_right_end, right_ramp_angle, RAMP_LENGTH, 6),

    # Spielfeld Rampen
    # Schräge Rampen unter den dreieckigen Bumpern innen
    Ramp((150, 609), left_ramp_angle, 80),
    Ramp((GAME_WIDTH - 150, 609), right_ramp_angle, 80),

    # Äußere Wände
    Ramp((80, 570), 90, 335),
    Ramp((GAME_WIDTH - 80, 570), 90, 100),

    # Schräge Rampen unter den dreieckigen Bumpern außen
    Ramp((150, 639), left_ramp_angle, 92),
    Ramp((GAME_WIDTH - 150, 639), right_ramp_angle, 94),

    # Innere Wände
    Ramp((70, 592), 90, 380),
    Ramp((GAME_WIDTH - 70, 592), 90, 105),
    
    Ramp((70, 210), right_ramp_angle, 57),
    Ramp((80, 235), right_ramp_angle, 45),
    Ramp((118, 213), 90, ball_radius_ramps),

    Ramp((GAME_WIDTH - 150, 640), 90, ball_radius_ramps),
    Ramp((150, 640), 90, ball_radius_ramps),

    # weitere Wände werden im weiteren Verlauf mit Ramps.append() hinzugefügt
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
def reflect_ball_bumper(ball_pos, ball_vel, bumper):
    global ball_angular_vel, score

    if bumper['shape'] == BUMPER_TYPE_TRIANGLE:
        reflect_ball_from_triangle(ball_pos, ball_vel, bumper)
    else:
        bumper_pos = bumper['pos']
        angle_of_incidence = math.atan2(ball_pos[1] - bumper_pos[1], ball_pos[0] - bumper_pos[0])
        
        # Normalenvektor und Skalarprodukt berechnen
        normal = (math.cos(angle_of_incidence), math.sin(angle_of_incidence))
        dot_product = ball_vel[0] * normal[0] + ball_vel[1] * normal[1]

        # Geschwindigkeit reflektieren
        ball_vel[0] -= 2 * dot_product * normal[0]
        ball_vel[1] -= 2 * dot_product * normal[1]

        # Geschwindigkeitsfaktor des jeweiligen Bumper anwenden
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
    score += bumper['score']

    # Maximalgeschwindigkeit anwenden, falls angegeben
    if 'max_velocity' in bumper:
        limit_velocity(ball_vel, bumper['max_velocity'])
    else:
        limit_velocity(ball_vel, MAX_VELOCITY)

    # Geschwindigkeit der Kugel begrenzen
    limit_velocity(ball_vel, MAX_VELOCITY)
    bumper['timer'] = 10
    sound_bumper.play()


# Reflektiert die Kugelgeschwindigkeit bei Kollision mit einem dreieckigen Bumper
def reflect_ball_from_triangle(ball_pos, ball_vel, start, end):
    global ball_angular_vel, score

    # Normalenvektor der Linie berechnen
    normal = get_line_normal(start, end)

    # Mittelpunkt der Linie und Vektor von der Kugel zum Mittelpunkt berechnen
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    ball_to_midpoint = (midpoint[0] - ball_pos[0], midpoint[1] - ball_pos[1])

    if (ball_to_midpoint[0] * normal[0] + ball_to_midpoint[1] * normal[1]) > 0:
        normal = (-normal[0], -normal[1])

    # Skalarprodukt berechnen
    dot_product = ball_vel[0] * normal[0] + ball_vel[1] * normal[1]

    # Geschwindigkeit reflektieren
    ball_vel[0] -= 2 * dot_product * normal[0]
    ball_vel[1] -= 2 * dot_product * normal[1]

    # Geschwindigkeitsfaktor des dreieckigen Bumpers anwenden
    ball_vel[0] *= BUMPER_PROPERTIES['triangle']['velocity_factor']
    ball_vel[1] *= BUMPER_PROPERTIES['triangle']['velocity_factor']

    # Kollisionsvektor berechnen
    collision_vector = [ball_pos[0] - midpoint[0], ball_pos[1] - midpoint[1]]
    torque = (collision_vector[0] * ball_vel[1] - collision_vector[1] * ball_vel[0]) / (BALL_RADIUS ** 2)
    ball_angular_vel += torque

    distance = point_line_distance(ball_pos, start, end)
    overlap = BALL_RADIUS - distance
    if overlap > 0:
        ball_pos[0] += overlap * normal[0]
        ball_pos[1] += overlap * normal[1]

    add_particles(ball_pos)
    score += 100
    sound_bumper.play()


# Berechnet den Abprall der Kugel
def reflect_ball(start, end, is_flipper=False, flipper_angular_velocity=0, flipper_moving=False):
    global ball_pos, ball_vel, ball_angular_vel

    # Berechnet den Normalenvektor der Linie
    normal = get_line_normal(start, end)
    midpoint = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
    ball_to_midpoint = (midpoint[0] - ball_pos[0], midpoint[1] - ball_pos[1])

    # Wenn der Vektor von der Kugel zum Mittelpunkt und der Normalenvektor in die gleiche Richtung zeigen, Normalenvektor umkehren
    if (ball_to_midpoint[0] * normal[0] + ball_to_midpoint[1] * normal[1]) > 0:
        normal = (-normal[0], -normal[1])

    # Reflektiert die Geschwindigkeit basierend auf dem Normalenvektor
    dot_product = ball_vel[0] * normal[0] + ball_vel[1] * normal[1]
    ball_vel[0] -= 2 * dot_product * normal[0]
    ball_vel[1] -= 2 * dot_product * normal[1]

    # Wendet den Rückprallkoeffizienten an
    ball_vel[0] *= COEFFICIENT_OF_RESTITUTION
    ball_vel[1] *= COEFFICIENT_OF_RESTITUTION

    # Schwellenwert zur Bestimmung eines signifikanten Aufpralls
    impact_threshold = BALL_RADIUS + 5

    if is_flipper and flipper_moving:
        # Berechnet die Entfernung vom Flipper-Drehpunkt
        distance_from_pivot = math.sqrt((ball_pos[0] - start[0])**2 + (ball_pos[1] - start[1])**2)

        # Berechnet die lineare Geschwindigkeit am Kollisionspunkt
        linear_velocity = distance_from_pivot * flipper_angular_velocity

        # Verringert den Geschwindigkeitsmultiplikator mit zunehmender Entfernung vom Drehpunkt
        velocity_multiplier = max(0.5, 1.5 - (distance_from_pivot / FLIPPER_LENGTH))

        # Wendet die Impulsübertragung vom Flipper auf die Kugel mit angepasstem Multiplikator an
        ball_vel[0] += normal[0] * linear_velocity * velocity_multiplier
        ball_vel[1] += normal[1] * linear_velocity * velocity_multiplier

        # Fügt zusätzliche Geschwindigkeit hinzu, wenn die Kugel sehr nah am Flipper ist
        if point_line_distance(ball_pos, start, end) <= impact_threshold:
            extra_velocity = FLIPPER_MOTION_MOMENTUM * linear_velocity
            ball_vel[0] += normal[0] * extra_velocity
            ball_vel[1] += normal[1] * extra_velocity

    # Fügt Flipper-Partikel hinzu, wenn es sich um einen Flipper handelt
    if is_flipper:
        add_flipper_particles(ball_pos)

    # Wendet Drehmoment basierend auf der Kollision an
    collision_vector = [ball_pos[0] - midpoint[0], ball_pos[1] - midpoint[1]]
    torque = (collision_vector[0] * ball_vel[1] - collision_vector[1] * ball_vel[0]) / (BALL_RADIUS ** 2)
    ball_angular_vel += torque

    # Stellt sicher, dass die Kugel nicht zu tief in das Objekt eindringt
    while point_line_distance(ball_pos, start, end) <= BALL_RADIUS:
        ball_pos = [ball_pos[0] + normal[0] * 0.1, ball_pos[1] + normal[1] * 0.1]



###
### move ball ###
###

# Bewegt die Kugel und aktualisiert ihre Position und Geschwindigkeit
def move_ball():
    global GRAVITY, INITIAL_BALL_IMPULSE, ball_angle, ball_angular_vel, ball_vel, ball_pos, ball_in_black_hole

    if not GAME_STARTED:
        return
    
    # Initiale Bewegung der Kugel, wenn das Spiel beginnt
    if ball_vel == [0, 0] and GAME_STARTED:
        angle_rad = math.radians(BALL_ANGLE + 90)
        ball_vel[0] = INITIAL_BALL_IMPULSE * math.cos(angle_rad)
        ball_vel[1] = INITIAL_BALL_IMPULSE * math.sin(angle_rad)

    # Überprüft Kollisionen mit dem schwarzen Loch, bevor Position und Geschwindigkeit aktualisiert werden
    if not ball_in_black_hole:
        check_hole_collision(ball_pos, ball_vel)

    # Setzt die Geschwindigkeit zurück, wenn die Kugel im schwarzen Loch ist
    if ball_in_black_hole:
        ball_vel = [random.uniform(-2 * METER, 2 * METER), 1 * METER]
        ball_angular_vel = 0
        ball_in_black_hole = False

    # Fügt die Schwerkraft zur Geschwindigkeit hinzu
    ball_vel[1] += GRAVITY * dt

    # Aktualisiert die Position der Kugel
    ball_pos[0] += ball_vel[0] * dt + 0.5 * DAMPING_FACTOR * dt**2
    ball_pos[1] += ball_vel[1] * dt + 0.5 * GRAVITY * DAMPING_FACTOR * dt**2

    # Aktualisiert die Winkelposition der Kugel
    ball_angle += ball_angular_vel * dt

    # Wendet Dämpfung an
    ball_vel[0] *= DAMPING_FACTOR
    ball_vel[1] *= DAMPING_FACTOR
    ball_angular_vel *= DAMPING_FACTOR
    
    # Begrenze die Geschwindigkeit der Kugel
    limit_velocity(ball_vel, MAX_VELOCITY)
    
    # Überprüfe Kollisionen mit Bumpern
    check_bumper_collision(ball_pos, ball_vel)
    

# Begrenze die Geschwindigkeit der Kugel auf eine maximale Geschwindigkeit
def limit_velocity(ball_vel, max_velocity):
    speed = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2)
    if speed > max_velocity:
        scale = max_velocity / speed
        ball_vel[0] *= scale
        ball_vel[1] *= scale



###
### Kollisionen ###
###

def check_continuous_collision(ball_pos, ball_vel, flipper_start, flipper_end):
    # Berechnet die Anzahl der Schritte basierend auf der Geschwindigkeit der Kugel
    steps = int(math.hypot(ball_vel[0], ball_vel[1]) / BALL_RADIUS)
    steps = max(steps, 1)

    for i in range(steps):
        # Berechnet die interpolierte Position der Kugel
        interpolated_pos = (
            ball_pos[0] + ball_vel[0] * (i / steps) * dt,
            ball_pos[1] + ball_vel[1] * (i / steps) * dt
        )

        # Überprüft auf eine Kollision an dieser interpolierten Position
        if point_line_distance(interpolated_pos, flipper_start, flipper_end) <= BALL_RADIUS:
            return True, interpolated_pos

    return False, ball_pos


# Überprüft Kollisionen der Kugel mit den Flippern und Spielfeldgrenzen
def check_collision():
    global ball_pos, ball_vel

    # Überprüft Kollisionen mit den Flippern
    for flipper_pos, angle, is_right, flipper_active, flipper_angular_velocity, flipper_moving in [
        (left_flipper_pos, left_flipper_angle, False, left_flipper_active, FLIPPER_ANGLE_STEP if left_flipper_active else 0, left_flipper_moving),
        (right_flipper_pos, right_flipper_angle, True, right_flipper_active, FLIPPER_ANGLE_STEP if right_flipper_active else 0, right_flipper_moving)]:

        # Berechnet die Start- und Endpunkte des Flippers basierend auf seiner Position, dem Winkel und der Ausrichtung
        start_x, start_y = flipper_pos
        end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
        end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))

        flipper_start = (start_x, start_y)
        flipper_end = (end_x, end_y)

        # Überprüft kontinuierlich Kollisionen der Kugel mit dem Flipper
        collision, collision_pos = check_continuous_collision(ball_pos, ball_vel, flipper_start, flipper_end)
        if collision:
            ball_pos = collision_pos  # Update ball position to the collision point
            reflect_ball(flipper_start, flipper_end, is_flipper=True, flipper_angular_velocity=flipper_angular_velocity, flipper_moving=flipper_moving)
            sound_effect.play()
            break

    # Überprüft Kollisionen mit Rampen/Wänden
    for ramp in ramps:
        ramp.check_collision(ball_pos, ball_vel)

    # Überprüft Kollisionen mit den Spielfeldgrenzen
    if ball_pos[0] <= BALL_RADIUS or ball_pos[0] >= GAME_WIDTH - BALL_RADIUS:
        ball_vel[0] = -ball_vel[0] * COEFFICIENT_OF_RESTITUTION
        ball_pos[0] = max(min(ball_pos[0], GAME_WIDTH - BALL_RADIUS), BALL_RADIUS)

    if ball_pos[1] <= BALL_RADIUS:
        ball_vel[1] = -ball_vel[1] * COEFFICIENT_OF_RESTITUTION
        ball_pos[1] = BALL_RADIUS

    if ball_pos[1] >= HEIGHT - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1] * COEFFICIENT_OF_RESTITUTION
        ball_pos[1] = HEIGHT - BALL_RADIUS


# Überprüft Kollision der Kugel mit Bumpern
def check_bumper_collision(ball_pos, ball_vel):
    # Schleife durch alle Bumper
    for bumper in bumpers:
        # Überprüft Kollisionen mit kreisförmigen Bumpern
        if bumper['shape'] == BUMPER_TYPE_CIRCLE:
            # Berechnet die Entfernung zwischen der Kugel und dem Bumper
            if math.hypot(ball_pos[0] - bumper['pos'][0], ball_pos[1] - bumper['pos'][1]) < BALL_RADIUS + bumper['radius']:
                if not bumper['active']:
                    bumper['active'] = True
                    bumper['timer'] = 10
                # Reflektiert die Kugelgeschwindigkeit bei Kollision mit dem Bumper
                reflect_ball_bumper(ball_pos, ball_vel, bumper)

        # Überprüft Kollisionen mit dreieckigen Bumpern
        elif bumper['shape'] == BUMPER_TYPE_TRIANGLE:
            # Überprüft Kollisionen mit den Kanten des dreieckigen Bumpers
            for i in range(3):
                start = bumper['points'][i]
                end = bumper['points'][(i + 1) % 3]
                if point_line_distance(ball_pos, start, end) <= BALL_RADIUS:
                    if not bumper['active']:
                        bumper['active'] = True
                        bumper['timer'] = 10
                    # Reflektiert die Kugelgeschwindigkeit bei Kollision mit der Kante des dreieckigen Bumpers
                    reflect_ball_from_triangle(ball_pos, ball_vel, start, end)
                    break
            
            # Überprüft, ob die Kugel innerhalb des dreieckigen Bumpers liegt
            if point_in_triangle(ball_pos[0], ball_pos[1], bumper['points']):
                for i in range(3):
                    start = bumper['points'][i]
                    end = bumper['points'][(i + 1) % 3]
                    if point_line_distance(ball_pos, start, end) > BALL_RADIUS:
                        reflect_ball_from_triangle(ball_pos, ball_vel, start, end)
                        break
        
        # Deaktiviert den Bumper, wenn der Timer abgelaufen ist
        if bumper['active']:
            bumper['timer'] -= 1
            if bumper['timer'] <= 0:
                bumper['active'] = False



###
### Helper Funktionen
###

# Berechnet den Normalenvektor einer Linie, die durch zwei Punkte definiert ist
def get_line_normal(start, end):
    # Berechnet die Differenzen der x- und y-Koordinaten zwischen dem Start- und Endpunkt der Linie
    dx = end[0] - start[0]
    dy = end[1] - start[1]

    # Der Normalenvektor ist senkrecht zur Linie
    normal = (-dy, dx)
    length = math.sqrt(normal[0]**2 + normal[1]**2)

    # Normierung des Vektors
    return (normal[0] / length, normal[1] / length)


# Berechnet den Abstand eines Punktes von einer Linie, definiert durch zwei Punkte
def point_line_distance(point, start, end):
    px, py = point
    sx, sy = start
    ex, ey = end

    # Vektor des Liniensegments
    line_vec = (ex - sx, ey - sy)
    
    # Vektor vom Startpunkt des Liniensegments zum Punkt
    point_vec = (px - sx, py - sy)
   
    # Länge des Liniensegments
    line_len = math.sqrt(line_vec[0]**2 + line_vec[1]**2)
    
    # Normalisierter Linienvektor
    line_unitvec = (line_vec[0] / line_len, line_vec[1] / line_len)

    # Projektion des Punktvektors auf die Linie
    proj_length = point_vec[0] * line_unitvec[0] + point_vec[1] * line_unitvec[1]

    # Einschränkung der Projektion auf die Länge des Liniensegments
    proj_length = max(0, min(proj_length, line_len))
    nearest = (sx + line_unitvec[0] * proj_length, sy + line_unitvec[1] * proj_length)

    # Berechnung der Entfernung vom Punkt zum nächsten Punkt auf dem Liniensegment
    dist = math.sqrt((px - nearest[0])**2 + (py - nearest[1])**2)
    return dist


# Überprüft, ob ein Punkt innerhalb eines Dreiecks liegt
def point_in_triangle(px, py, triangle_points):
    ax, ay = triangle_points[0]
    bx, by = triangle_points[1]
    cx, cy = triangle_points[2]

    # Berechnet Vektoren
    v0 = (cx - ax, cy - ay)
    v1 = (bx - ax, by - ay)
    v2 = (px - ax, py - ay)

    # Berechnet Skalarprodukte
    dot00 = v0[0] * v0[0] + v0[1] * v0[1]
    dot01 = v0[0] * v1[0] + v0[1] * v1[1]
    dot02 = v0[0] * v2[0] + v0[1] * v2[1]
    dot11 = v1[0] * v1[0] + v1[1] * v1[1]
    dot12 = v1[0] * v2[0] + v1[1] * v2[1]

    # Berechnet baryzentrische Koordinaten
    inv_denom = 1 / (dot00 * dot11 - dot01 * dot01)
    u = (dot11 * dot02 - dot01 * dot12) * inv_denom
    v = (dot00 * dot12 - dot01 * dot02) * inv_denom

    # Überprüft, ob der Punkt im Dreieck liegt
    return (u >= 0) and (v >= 0) and (u + v < 1)



###
### Draw Funktionen ###
###

draw_ball_direction_line = 'on'

# Zeichnet die Kugel an ihrer aktuellen Position auf dem Spielfeld
def draw_ball():
    global teleporting
    # Zeichnet die Kugel
    if teleporting == False:
        pygame.draw.circle(window, pygame.Color(ball_color.lower()), (int(ball_pos[0]), int(ball_pos[1])), BALL_RADIUS)

        if draw_ball_direction_line:
            # Zeichnet eine Linie, die die Richtung der Kugelgeschwindigkeit anzeigt
            direction_length = 30 * math.sqrt(ball_vel[0]**2 + ball_vel[1]**2) / 100
            angle = math.atan2(ball_vel[1], ball_vel[0])
            end_pos = (ball_pos[0] + direction_length * math.cos(angle), ball_pos[1] + direction_length * math.sin(angle))
            pygame.draw.line(window, RED, (ball_pos[0], ball_pos[1]), end_pos, 2)
        else:
            return


# Zeichnet den Flipper an der gegebenen Position und mit dem gegebenen Winkel
def draw_flipper(position, angle, is_right, color):
    # Berechnet die Start- und Endpunkte des Flippers basierend auf seiner Position, dem Winkel und der Ausrichtung
    start_x, start_y = position

    # Bestimmt die Richtung des Flippers basierend darauf, ob er rechts oder links ist
    end_x = start_x + FLIPPER_LENGTH * math.cos(math.radians(angle)) * (-1 if is_right else 1)
    end_y = start_y - FLIPPER_LENGTH * math.sin(math.radians(angle))

    # Zeichnet eine Linie, die den Flipper darstellt
    pygame.draw.line(window, color, (start_x, start_y), (end_x, end_y), FLIPPER_WIDTH)


# Zeichnet einen dreieckigen Bumper mit benutzerdefinierten Punkten
def draw_triangle_bumper(window, bumper):
    # Skaliert den Bumper, wenn er aktiv ist
    if bumper['active']:
        scale_factor = BUMPER_TRIANGULAR_SCALE
    else:
        scale_factor = .8

    # Berechnet den Schwerpunkt des Dreiecks
    centroid_x = sum(point[0] for point in bumper['points']) / 3
    centroid_y = sum(point[1] for point in bumper['points']) / 3

    # Skaliert die Punkte des Dreiecks basierend auf dem Skalierungsfaktor
    scaled_points = [
        (
            int(centroid_x + (point[0] - centroid_x) * scale_factor),
            int(centroid_y + (point[1] - centroid_y) * scale_factor)
        )
        for point in bumper['points']
    ]

    # Zeichnet das Dreieck mit den skalierten Punkten
    pygame.draw.polygon(window, pygame.Color(bumper['color']), scaled_points)

    # Berechnet den Schwerpunkt des skalierten Dreiecks
    centroid_x = sum(point[0] for point in scaled_points) / 3
    centroid_y = sum(point[1] for point in scaled_points) / 3

    # Zeichnet die Punktzahl des Bumpers, wenn sie angezeigt werden soll
    if bumper['show_score']:
        label = custom_font.render(str(bumper['score']), True, pygame.Color('#121212'))
        label_rect = label.get_rect(center=(int(centroid_x), int(centroid_y) + 2))
        window.blit(label, label_rect)


# Zeichnet alle Bumper, basierend auf ihrem Aktivierungsstatus
def draw_bumpers():
    # Schleife durch alle Bumper in der Liste der Bumper
    for bumper in bumpers:
        # Überprüft, ob der Bumper ein Kreis ist
        if bumper['shape'] == BUMPER_TYPE_CIRCLE:
            if bumper['active']:
                # Skaliert den Radius des Bumpers, wenn er aktiv ist
                scaled_radius = int(bumper['radius'] * BUMPER_SCALE)
                # Zeichnet einen Kreis mit dem skalierten Radius
                pygame.draw.circle(window, bumper['color'], (int(bumper['pos'][0]), int(bumper['pos'][1])), scaled_radius)
                # Reduziert den Timer des aktiven Bumpers
                bumper['timer'] -= 1
                if bumper['timer'] <= 0:
                    bumper['active'] = False
            else:
                # Zeichnet einen Kreis mit dem ursprünglichen Radius
                pygame.draw.circle(window, bumper['color'], (int(bumper['pos'][0]), int(bumper['pos'][1])), bumper['radius'])
        
        # Überprüft, ob der Bumper ein Dreieck ist        
        elif bumper['shape'] == BUMPER_TYPE_TRIANGLE:
            # Zeichnet den dreieckigen Bumper mit benutzerdefinierten Punkten
            draw_triangle_bumper(window, bumper)

        # Zeichnet die Punktzahl des Bumpers, wenn sie angezeigt werden soll
        if bumper['show_score']:
            label = custom_font.render(str(bumper['score']), True, pygame.Color('#121212'))
            label_rect = label.get_rect(center=(int(bumper['pos'][0]), int(bumper['pos'][1]) + 2))
            window.blit(label, label_rect)



# Zeichnet die Rampen auf das Spielfeld
def draw_ramps():
    # Schleife durch alle Rampen in der Liste der Rampen
    for ramp in ramps:
        # Zeichnet die aktuelle Rampe
        ramp.draw(window)


# Zeichnet die Trennlinie
def draw_separator():
    # Zeichnet ein Rechteck als Trennlinie auf dem Spielfeld
    pygame.draw.rect(window, SEPARATOR_COLOR, (SEPARATOR_POS, 0, SEPARATOR_WIDTH, HEIGHT))


# Zeichnet einen Indicator vor dem starten des Spiels, wo die Kugel hinfliegen wird
def draw_initial_trajectory():
    if not GAME_STARTED:
        # Berechnet den Winkel der Kugel in Bogenmaß und die anfängliche Geschwindigkeit
        angle_rad = math.radians(BALL_ANGLE + 90)
        initial_vel = [
            INITIAL_BALL_IMPULSE * math.cos(angle_rad),
            INITIAL_BALL_IMPULSE * math.sin(angle_rad)
        ]

        # Zeichnet eine Linie, die die Richtung und den erwarteten Flug der Kugel anzeigt
        # Die Länge der Richtungslinie wird basierend auf der Geschwindigkeit der Kugel berechnet
        direction_length = 50 * math.sqrt(initial_vel[0]**2 + initial_vel[1]**2) / 100
        # Berechnet den Winkel der Geschwindigkeit
        angle = math.atan2(initial_vel[1], initial_vel[0])
        # Berechnet die Endposition der Richtungslinie
        end_pos = (ball_pos[0] + direction_length * math.cos(angle), ball_pos[1] + direction_length * math.sin(angle))
        # Zeichnet die Linie von der aktuellen Position der Kugel zur berechneten Endposition
        pygame.draw.line(window, RED, (ball_pos[0], ball_pos[1]), end_pos, 2)



###
### Flipper Animation
###

# Flipper Winkel
left_flipper_target_angle = -30
right_flipper_target_angle = -30

# Boolean des Flipper Status
left_flipper_moving = False
right_flipper_moving = False

# Aktualisiert die Flipper
def update_flippers():
    global left_flipper_angle, right_flipper_angle, left_flipper_moving, right_flipper_moving

    # Aktualisiert den Winkel des linken Flippers
    if left_flipper_angle < left_flipper_target_angle:
        left_flipper_angle = min(left_flipper_angle + FLIPPER_ANGLE_STEP, left_flipper_target_angle)
        left_flipper_moving = True
    elif left_flipper_angle > left_flipper_target_angle:
        left_flipper_angle = max(left_flipper_angle - FLIPPER_ANGLE_STEP, left_flipper_target_angle)
        left_flipper_moving = True
    else:
        left_flipper_moving = False

    # Aktualisiert den Winkel des rechten Flippers
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
    global game_freeze, left_flipper_target_angle, right_flipper_target_angle, left_flipper_active, right_flipper_active, left_flipper_color, right_flipper_color, ball_pos, ball_vel, GAME_STARTED, score
    
    # Überprüft den Status aller Tasten
    keys = pygame.key.get_pressed()

    # Linker Flipper
    if keys[pygame.K_a]:
        if not left_flipper_active:
            # Setzt den Zielwinkel des linken Flippers auf den maximalen Winkel
            left_flipper_target_angle = FLIPPER_MAX_ANGLE
            left_flipper_active = True
            left_flipper_color = ACTIVE_FLIPPER_COLOUR
    else:
        left_flipper_target_angle = -30
        left_flipper_active = False
        left_flipper_color = FLIPPER_COLOUR

    # Rechter Flipper
    if keys[pygame.K_d]:
        if not right_flipper_active:
            # Setzt den Zielwinkel des rechten Flippers auf den maximalen Winkel
            right_flipper_target_angle = FLIPPER_MAX_ANGLE
            right_flipper_active = True
            right_flipper_color = ACTIVE_FLIPPER_COLOUR
    else:
        right_flipper_target_angle = -30
        right_flipper_active = False
        right_flipper_color = FLIPPER_COLOUR

    # Spiel zurücksetzen
    if keys[pygame.K_r]:
        ball_pos = [GAME_WIDTH // 2, BALL_START_Y]
        ball_vel = [0, 0]
        GAME_STARTED = False
        score = 0

    # Spiel einfrieren (Freeze-Funktion)
    if keys[pygame.K_f]:
        game_freeze = not game_freeze


dragging_ball = False

# Überprüft, ob die Maus geklickt wurde, und führt entsprechende Aktionen aus
def handle_mouse():
    global ball_pos, dragging_ball

    mouse_x, mouse_y = pygame.mouse.get_pos()
    
    if not GAME_STARTED:
        # Überprüfe, ob die linke Maustaste gedrückt wurde
        if pygame.mouse.get_pressed()[0]:
            # Wenn die Kugel noch nicht gezogen wird, überprüfe, ob der Klick innerhalb der Kugel stattfindet
            if not dragging_ball:
                if math.hypot(mouse_x - ball_pos[0], mouse_y - ball_pos[1]) <= BALL_RADIUS:
                    dragging_ball = True
            
            # Wenn die Kugel gezogen wird, aktualisiere ihre Position basierend auf der Mausposition
            if dragging_ball:
                if mouse_x < GAME_WIDTH:
                    ball_pos = [mouse_x, mouse_y]
        else:
            dragging_ball = False


# Initial Values
INITIAL_GRAVITY_STRENGTH = GRAVITY_STRENGTH
INITIAL_BALL_ANGLE = BALL_ANGLE
INITIAL_INITAL_BALL_IMPULSE = INITIAL_BALL_IMPULSE

# Event Handler for Buttons
def handle_buttons(event):
    global GAME_STARTED, ball_pos, ball_vel, is_pause_menu_open, pause_panel, GRAVITY_STRENGTH, BALL_ANGLE, INITIAL_BALL_IMPULSE

    # Überprüft, ob die ESC-Taste gedrückt wurde
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        # Schließt das Pause-Menü, wenn es geöffnet ist
        if is_pause_menu_open:
            is_pause_menu_open = False
            if pause_panel:
                pause_panel.kill()
                pause_panel = None
        else:
            # Öffnet das Pause-Menü, wenn es nicht geöffnet ist
            pause_menu()
        return

    # Überprüft, ob ein Button gedrückt wurde
    if event.type == pygame_gui.UI_BUTTON_PRESSED:
        # Überprüft, ob der Pause-Button gedrückt wurde
        if event.ui_element == pause_button:
            pause_menu()
        # Überprüft, ob der Reset-Button gedrückt wurde
        elif event.ui_element == reset_button:
            reset_score()
            save_high_score()
            ball_pos = [GAME_WIDTH // 2, BALL_START_Y]
            ball_vel = [0, 0]
            GAME_STARTED = False
            # Reset sliders to initial values
            initial_impulse_slider.set_current_value(INITIAL_GRAVITY_STRENGTH)
            gravity_strength_slider.set_current_value(INITIAL_GRAVITY_STRENGTH)
            launch_angle_slider.set_current_value(INITIAL_BALL_ANGLE)

            # Update labels to reflect initial values
            initial_impulse_label.set_text(f"Initial Speed: {INITIAL_INITAL_BALL_IMPULSE / METER:.1f} m/s")
            gravity_strength_label.set_text(f"Gravity Strength: {INITIAL_GRAVITY_STRENGTH:.1f}")
            launch_angle_label.set_text(f"Launch Angle: {INITIAL_BALL_ANGLE} deg")
        # Überprüft, ob der Play-Button gedrückt wurde
        elif event.ui_element == play_button:
            if ball_pos != [GAME_WIDTH // 2, BALL_START_Y]:  
                angle_rad = math.radians(BALL_ANGLE + 90)
                ball_vel = [
                    INITIAL_BALL_IMPULSE * math.cos(angle_rad),
                    INITIAL_BALL_IMPULSE * math.sin(angle_rad)
                ]
                GAME_STARTED = True
        # Überprüft, ob der Continue-Button im Pause-Menü gedrückt wurde
        elif event.ui_element == continue_button:
            is_pause_menu_open = False
            if pause_panel:
                pause_panel.kill()
                pause_panel = None
        # Überprüft, ob der Quit-Button im Pause-Menü gedrückt wurde
        elif event.ui_element == quit_button:
            pygame.quit()
            sys.exit()



###
### Graphical User Interface (GUI) ###
###

# Default Score value
score_value = UITextBox(
    relative_rect=pygame.Rect((GAME_WIDTH + 14, 44), (UI_WIDTH - 28, 80)),
    html_text="0",
    manager=manager,
    object_id=ObjectID(class_id='@text_box', object_id='#score_value')
)

# Highcore value
high_score_value = UITextBox(
    relative_rect=pygame.Rect((GAME_WIDTH + 150, 114), (100, 80)),
    html_text="0",
    manager=manager,
    object_id=ObjectID(class_id='@text_box', object_id='#high_score_value')
)

# Zeichnet die grafische Benutzeroberfläche (GUI) auf das Fenster
def draw_gui():
    global pregame_label
    # Zeichnet den Hintergrund des GUI-Bereichs
    position_text = f'X: {ball_pos[0]:.0f} Y: {ball_pos[1]:.0f}'
    speed = math.sqrt(ball_vel[0]**2 + ball_vel[1]**2) / 100
    speed_text = f'{speed:.1f}'
    score_text = f'{score}'
    high_score_text = f'{high_score}'

    position_value.set_text(position_text)
    speed_value.set_text(speed_text)
    score_value.set_text(score_text)
    high_score_value.set_text(high_score_text)

    # Tooltip vor dem Spielstart
    if not GAME_STARTED: 
        if pregame_label is None:
            pregame_label = UILabel(
                relative_rect=pygame.Rect((GAME_WIDTH // 2 - 200, HEIGHT - 65), (400, 50)),
                text="Drag the ball to your desired position",
                manager=manager,
                object_id=ObjectID(class_id='@label', object_id='#pregame_label')
            )
        draw_initial_trajectory()
    else:
        if pregame_label is not None:
            pregame_label.kill()
            pregame_label = None

position_value = UITextBox(
    relative_rect=pygame.Rect((GAME_WIDTH + 12, 216), (150, 40)),
    html_text="X: 0 Y: 0",
    manager=manager,
    object_id=ObjectID(class_id='@text_box', object_id='#position_value')
)

speed_value = UITextBox(
    relative_rect=pygame.Rect((GAME_WIDTH + 184, 216), (102, 40)),
    html_text="0.0",
    manager=manager,
    object_id=ObjectID(class_id='@text_box', object_id='#speed_value')
)

# Beschriftung für den initialen Impuls-Slider
initial_impulse_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 41, 344), (SLIDER_WIDTH - 8, 30)),
    text=f"Initial Speed: {INITIAL_BALL_IMPULSE / METER:.1f} m/s",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#ii_label')
)

# Initialisierung des Sliders für den initialen Impuls
initial_impulse_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 39, 374), (SLIDER_WIDTH - 28, SLIDER_HEIGHT)),
    start_value=INITIAL_BALL_IMPULSE / METER,
    value_range=(SLIDER_MIN_VALUE, SLIDER_MAX_VALUE),
    manager=manager,
    object_id=ObjectID(class_id='@horizontal_slider', object_id='#ii_slider')
)

# Beschriftung für den Schwerkraftstärke-Slider
gravity_strength_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 41, 424), (SLIDER_WIDTH - 8, 30)),
    text=f"Gravity Strength: {GRAVITY / METER / 9.81:.1f}",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#gs_label')
)

# Initialisierung des Sliders für die Schwerkraftstärke
gravity_strength_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 39, 454), (SLIDER_WIDTH - 28, SLIDER_HEIGHT)),
    start_value=GRAVITY_STRENGTH,
    value_range=(SLIDER_MIN_GRAVITY, SLIDER_MAX_GRAVITY),
    manager=manager,
    object_id=ObjectID(class_id='@horizontal_slider', object_id='#gs_slider')
)

# Beschriftung für den Abschusswinkel-Slider
launch_angle_label = UILabel(
    relative_rect=pygame.Rect((GAME_WIDTH + 41, 504), (SLIDER_WIDTH - 8, 30)),
    text=f"Launch Angle: {BALL_ANGLE} deg",
    manager=manager,
    object_id=ObjectID(class_id='@label', object_id='#la_label')
)

# Initialisierung des Sliders für den Abschusswinkel der Kugel
launch_angle_slider = UIHorizontalSlider(
    relative_rect=pygame.Rect((GAME_WIDTH + 39, 534), (SLIDER_WIDTH - 28, SLIDER_HEIGHT)),
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
    global is_pause_menu_open, pause_panel, continue_button, quit_button, volume_slider, volume_value_label, volume
    is_pause_menu_open = True

    # Blendet die GUI-Elemente des Spiels aus
    set_gui_visibility(False)
    
    padding = 48

    # Erstellt eine Oberfläche für das Pause-Menü
    pause_surface = pygame.Surface((WIDTH, HEIGHT))
    pause_surface.blit(pause_image, (0, 0))

    # Erstellt ein Panel, das das gesamte Fenster abdeckt
    pause_panel = UIPanel(
        relative_rect=pygame.Rect(0, 0, WIDTH, HEIGHT),
        manager=manager
    )

    # Dropdown-Menü für die Farbauswahl der Kugel
    ball_preview_width = 48
    dropdown_width = WIDTH / 2 - padding - padding - 56 - ball_preview_width
    volume_width = WIDTH - padding - padding - 64 - ball_preview_width

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
        relative_rect=pygame.Rect(padding + dropdown_width + padding, 480, ball_preview_width, ball_preview_width),
        text="",
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@ball_preview', object_id='#ball_preview')
    )

    # Initiale runde Kugelvorschau zeichnen
    update_ball_preview(ball_color)

    # Dropdown-Menü für die Anzeige der Ballgeschwindigkeitslinie
    line_dropdown = UIDropDownMenu(
        options_list=['On', 'Off'],
        starting_option='On' if draw_ball_direction_line else 'Off',
        relative_rect=pygame.Rect(WIDTH / 2 + padding + 24, 480, dropdown_width + padding, 50),
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@dropdown', object_id='#ball_dropdown')
    )

    # Funktion zum Aktualisieren der Einstellung der Linienanzeige
    def update_ball_line_display(option):
        global draw_ball_direction_line
        draw_ball_direction_line = (option == 'On')

    # Event-Handler für Änderungen im Dropdown-Menü
    def handle_line_dropdown_event(event):
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == line_dropdown:
                update_ball_line_display(event.text.lower())

    volume_value_label = UILabel(
        relative_rect=pygame.Rect(volume_width + padding + 32, 627, 50, SLIDER_HEIGHT + 12 - 4),
        text=str(int(pygame.mixer.music.get_volume() * 100)),
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@label', object_id='#volume_value')
    )

    volume_slider = UIHorizontalSlider(
        relative_rect=pygame.Rect(padding + 24, 625, volume_width, SLIDER_HEIGHT + 12),
        start_value=pygame.mixer.music.get_volume() * 100,
        value_range=(0, 100),
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='@horizontal_slider', object_id='#volume_slider')
    )

    # Fügt den "Fortsetzen"-Button hinzu
    continue_button = UIButton(
        relative_rect=pygame.Rect((WIDTH / 2 - 200, HEIGHT - 80), (200, 60)),
        text="Continue",
        manager=manager,
        container=pause_panel,
        object_id=ObjectID(class_id='', object_id='#play_button')
    )

    # Fügt den "Beenden"-Button hinzu
    quit_button = UIButton(
        relative_rect=pygame.Rect((WIDTH / 2 + 20, HEIGHT - 73), (140, 46)),
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
                elif event.ui_element == line_dropdown:
                    update_ball_line_display(event.text)
            elif event.type == pygame_gui.UI_HORIZONTAL_SLIDER_MOVED:
                if event.ui_element == volume_slider:
                    volume = event.value / 100
                    pygame.mixer.music.set_volume(volume)
                    sound_effect.set_volume(volume)
                    sound_bumper.set_volume(volume)
                    volume_value_label.set_text(str(int(volume * 100)))

            manager.process_events(event)

            if not GAME_STARTED:
                pregame_label.visible = False

        manager.update(time_delta)
        window.blit(pause_surface, (0, 0))
        manager.draw_ui(window)
        pygame.display.flip()



###
### Scoring Lines
###

# Definitionen der Scoring Lines
scoring_lines = [
    {'start': (GAME_WIDTH - 150, 325), 'end': (GAME_WIDTH - 80, 325), 'idle_color': LIGHT_GREY, 'flash_color': BUMPER_COLOUR_TIER_1, 'score': 400},
    {'start': (GAME_WIDTH - 150, 345), 'end': (GAME_WIDTH - 80, 345), 'idle_color': LIGHT_GREY, 'flash_color': BUMPER_COLOUR_TIER_2, 'score': 300},
    {'start': (GAME_WIDTH - 150, 365), 'end': (GAME_WIDTH - 80, 365), 'idle_color': LIGHT_GREY, 'flash_color': BUMPER_COLOUR_TIER_3, 'score': 200},
    {'start': (GAME_WIDTH - 150, 385), 'end': (GAME_WIDTH - 80, 385), 'idle_color': LIGHT_GREY, 'flash_color': BUMPER_COLOR_TRIANGLE, 'score': 100},
]

# Positionen der Wände
wall_left_start = (GAME_WIDTH - 150, 410)
wall_right_start = (GAME_WIDTH - 80, 510)


ramps.append(Ramp(wall_right_start, 90, 275))
ramps.append(Ramp((wall_right_start[0] + 10, wall_right_start[1]), 90, 283))

# Walls Innen
ramps.append(Ramp(wall_left_start, 90, 120))
ramps.append(Ramp((wall_left_start[0] - ball_radius_ramps, wall_left_start[1] + 14), 90, 142))
ramps.append(Ramp((GAME_WIDTH - 150, 290), 165, ball_radius_ramps))
ramps.append(Ramp((GAME_WIDTH - 150, 410), 205, ball_radius_ramps))

crossed_lines = {i: {'crossed': False, 'last_flash_time': 0} for i in range(len(scoring_lines))}


# Überprüft, ob die Kugel eine Linie überquert hat
def check_line_crossing(ball_pos, prev_ball_pos, line_start, line_end):
    # Hilfsfunktion zur Bestimmung, auf welcher Seite der Linie ein Punkt liegt
    def side_of_line(point, line_start, line_end):
        return (line_end[0] - line_start[0]) * (point[1] - line_start[1]) - (line_end[1] - line_start[1]) * (point[0] - line_start[0])

    # Bestimmt, auf welcher Seite der Linie die Kugel sich vorher befand
    side_prev = side_of_line(prev_ball_pos, line_start, line_end)
    # Bestimmt, auf welcher Seite der Linie die Kugel sich aktuell befindet
    side_current = side_of_line(ball_pos, line_start, line_end)

    # Überprüft, ob die Kugel sich nach oben bewegt
    if ball_pos[1] < prev_ball_pos[1]:
        # Überprüft, ob die Kugel die Linie überquert hat
        if side_prev * side_current < 0:
            # Überprüft, ob die Kugel sich innerhalb der x-Koordinaten der Linie befindet
            if min(line_start[0], line_end[0]) <= ball_pos[0] <= max(line_start[0], line_end[0]):
                return True
    return False


# Überprüft, ob die Kugel eine der Scoring-Linien überquert hat
def check_scoring_lines(ball_pos, prev_ball_pos):
    global score

    # Schleife durch alle Scoring-Linien
    for i, line in enumerate(scoring_lines):
        # Überprüft, ob die Kugel die aktuelle Linie überquert hat
        if check_line_crossing(ball_pos, prev_ball_pos, line['start'], line['end']):
            # Überprüft, ob die Linie zuvor nicht überquert wurde
            if not crossed_lines[i]['crossed']:
                # Erhöht den Highscore um die Punktzahl der Linie
                score += line['score']
                # Markiert die Linie als überquert und speichert die Zeit des Überquerens
                crossed_lines[i] = {'crossed': True, 'last_flash_time': pygame.time.get_ticks()}


# Zeichnet die Scoring-Linien auf das Spielfeld
def draw_scoring_lines():
    current_time = pygame.time.get_ticks()

    # Schleife durch alle Scoring-Linien
    for i, line in enumerate(scoring_lines):
        color = line['idle_color']
        # Überprüft, ob die Linie überquert wurde
        if crossed_lines[i]['crossed']:
            # Überprüft, ob die Linie innerhalb der Blinkzeit überquert wurde
            if current_time - crossed_lines[i]['last_flash_time'] <= FLASHING_TIME:
                color = line['flash_color']
            else:
                crossed_lines[i]['crossed'] = False
        
        # Zeichnet die Linie auf das Spielfeld
        pygame.draw.line(window, color, line['start'], line['end'], 10)



###
### Teleport
###

# Erzeugt Partikel für das Schwarze Loch
def generate_black_hole_particles(black_hole_pos, particles, num_particles=1):
    for _ in range(num_particles):
        angle = random.uniform(0, 2 * math.pi)
        radius = random.uniform(HOLE_RADIUS, HOLE_RADIUS * 1.5)
        x = black_hole_pos[0] + radius * math.cos(angle)
        y = black_hole_pos[1] + radius * math.sin(angle)
        particles.append({
            'pos': [x, y],
            'vel': [(black_hole_pos[0] - x) / 75, (black_hole_pos[1] - y) / 75],
            'color': PARTICLE_COLOUR_BLACK_HOLE,
            'timer': 30
        })
    return particles


# Aktualisiert die Partikel des Schwarzen Lochs
def update_black_hole_particles(particles, black_hole_pos):
    for particle in particles:
        # Bewegt das Partikel in Richtung des Zentrums des Schwarzen Lochs
        particle['pos'][0] += particle['vel'][0]
        particle['pos'][1] += particle['vel'][1]
        particle['timer'] -= 1

    # Entfernt Partikel, die das Zentrum erreicht haben oder abgelaufen sind
    particles = [p for p in particles if p['timer'] > 0 and (p['pos'][0], p['pos'][1]) != (black_hole_pos[0], black_hole_pos[1])]
    return particles


# Zeichnet die Partikel des Schwarzen Lochs
def draw_black_hole_particles(window, particles):
    for particle in particles:
        pygame.draw.circle(window, particle['color'], (int(particle['pos'][0]), int(particle['pos'][1])), 2)


# Loch Positionen
black_hole_pos = (115, 350)
exit_hole_pos = (GAME_WIDTH - 80, HOLE_RADIUS + 8)
ball_in_black_hole = False

teleporting = False
teleport_start_time = 0

def check_hole_collision(ball_pos, ball_vel):
    global black_hole_pos, exit_hole_pos, ball_angular_vel, ball_in_black_hole, teleporting, teleport_start_time

    # Überprüft, ob der Ball das Loch berührt
    if math.hypot(ball_pos[0] - black_hole_pos[0], ball_pos[1] - black_hole_pos[1]) <= HOLE_RADIUS:
        # Setzt den Teleportstatus und den Startzeitpunkt
        teleporting = True
        teleport_start_time = pygame.time.get_ticks()

        # Ball wird teleportiert und die Geschwindigkeit zurückgesetzt
        ball_angular_vel = 0
        
        # Fügt Partikel am Schwarzen Loch und am Ausgang hinzu
        add_particles(black_hole_pos, BLACK)
        add_particles(exit_hole_pos, PARTICLE_COLOUR_BLACK_HOLE)


# Zeichnet die Löcher (Schwarzes Loch und Ausgangsloch)
def draw_holes():
    pygame.draw.circle(window, BLACK, black_hole_pos, HOLE_RADIUS)
    pygame.draw.circle(window, BLACK, exit_hole_pos, HOLE_RADIUS)


# Bumpers
bumpers.append({'type': 'teleport', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [GAME_WIDTH - 50, 100], 'radius': BUMPER_RADIUS / 2.25, 'color': BUMPER_COLOUR_TIER_3, 'active': False, 'timer': 0, 'score': TIER_3, 'show_score': False, 'max_velocity': MAX_BUMPER_SPEED})
bumpers.append({'type': 'teleport', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [GAME_WIDTH - 110, 100], 'radius': BUMPER_RADIUS / 2.25, 'color': BUMPER_COLOUR_TIER_3, 'active': False, 'timer': 0, 'score': TIER_3, 'show_score': False, 'max_velocity': MAX_BUMPER_SPEED})
bumpers.append({'type': 'teleport', 'shape': BUMPER_TYPE_CIRCLE, 'pos': [GAME_WIDTH - 80, 160], 'radius': BUMPER_RADIUS / 1.75, 'color': BUMPER_COLOUR_TIER_2, 'active': False, 'timer': 0, 'score': TIER_2, 'show_score': False, 'max_velocity': MAX_BUMPER_SPEED})

# Wände am Out-Loch
ramps.append(Ramp((GAME_WIDTH - 162, 202), 90, 202))
ramps.append(Ramp((GAME_WIDTH - 172, 212), 90, 212))
ramps.append(Ramp((GAME_WIDTH - 162, 203), -15, 96))
ramps.append(Ramp((GAME_WIDTH - 172, 210), -15, 96))

# Wände am In-Loch
ramps.append(Ramp((145, 406), 90, 120))
ramps.append(Ramp((145 + ball_radius_ramps, 420), 90, 142))
ramps.append(Ramp((145 + ball_radius_ramps, 276), -165, ball_radius_ramps))
ramps.append(Ramp((145 + ball_radius_ramps, 420), -205, ball_radius_ramps))

# Particle Initialisierung
black_hole_particles = []



###
### Game Loop ###
###

# Hauptspiel-Schleife, die alle anderen Funktionen aufruft und das Spiel steuert
def game_loop():
    global game_freeze, current_volume, INITIAL_BALL_IMPULSE, GRAVITY_STRENGTH, GRAVITY, GAME_STARTED, BALL_ANGLE, is_pause_menu_open, pause_panel, pregame_label, ball_pos, ball_vel, prev_ball_pos, score, black_hole_particles, teleporting, teleport_start_time

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score()
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    game_freeze = not game_freeze

            handle_buttons(event)
            
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
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP or event.type == pygame.MOUSEMOTION:
                    handle_mouse()

                manager.process_events(event)

        manager.update(dt)
        
        window.fill(GAME_BG_COLOR, rect=pygame.Rect(0, 0, GAME_WIDTH, HEIGHT))
        window.fill(GUI_BG_COLOR, rect=pygame.Rect(GAME_WIDTH, 0, UI_WIDTH, HEIGHT))

        # Blit the background image
        window.blit(background_image, (GAME_WIDTH, 0))

        handle_keys()

        if not is_pause_menu_open:
            draw_flipper(left_flipper_pos, left_flipper_angle, False, left_flipper_color)
            draw_flipper(right_flipper_pos, right_flipper_angle, True, right_flipper_color)
            draw_bumpers()
            draw_scoring_lines()
            draw_ramps()
            draw_gui()
            draw_particles()
            update_particles()
            draw_separator()
            draw_holes()
            draw_black_hole_particles(window, black_hole_particles)
            update_high_score()

            if not teleporting:
                draw_ball()

            # Überprüft ob die Kugel den unteren Spielfeldrand berührt und triggert dann den End-Game-Screen
            if ball_pos[1] >= HEIGHT - BALL_RADIUS:
                result = end_game_screen(manager, window, clock, set_gui_visibility, score)
                if result == 'new_game':
                    update_high_score()
                    ball_pos = [GAME_WIDTH // 2, BALL_START_Y]
                    ball_vel = [0, 0]
                    GAME_STARTED = False
                    reset_score()
                    set_gui_visibility(True)
                    continue

        if not game_freeze and not is_pause_menu_open:
            prev_ball_pos = ball_pos.copy()
            
            move_ball()
            check_collision()
            update_flippers()
            check_hole_collision(ball_pos, ball_vel)
            check_scoring_lines(ball_pos, prev_ball_pos)
            black_hole_particles = generate_black_hole_particles(black_hole_pos, black_hole_particles)
            black_hole_particles = update_black_hole_particles(black_hole_particles, black_hole_pos)

            # Teleport-Delay von 500ms implementieren
            if teleporting:
                current_time = pygame.time.get_ticks()
                if current_time - teleport_start_time >= 500:
                    ball_pos[0], ball_pos[1] = exit_hole_pos
                    ball_vel = [random.uniform(-2 * METER, 2 * METER), 1 * METER]
                    teleporting = False

        manager.draw_ui(window)

        pygame.display.flip()
        pygame.display.set_caption(f"Flippernator3000 - FPS: {clock.get_fps():.2f}")
        clock.tick(60)


if __name__ == '__main__':
    # Setzt den Spielstatus auf nicht gestartet
    GAME_STARTED = False
    # Lädt den gespeicherten Highscore
    load_high_score()
    # Startet die Hauptspiel-Schleife
    game_loop()