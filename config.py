# Konstanten
GAME_STARTED = False

# Umrechnungsfaktor 100 Pixel = 1 Meter
METER = 100

# Beschleunigungen
INITIAL_BALL_IMPULSE = 1 * METER
GRAVITY_STRENGTH = 1

# Fenstergrößen
GAME_WIDTH, UI_WIDTH = 500, 300
WIDTH, HEIGHT = GAME_WIDTH + UI_WIDTH, 800

# Ball
BALL_RADIUS = 15
BALL_ANGLE = 0
VELOCITY_THRESHOLD = .1
BALL_START_Y = -1000

# Flipper
FLIPPER_LENGTH = 125
FLIPPER_WIDTH = 5
FLIPPER_IMPULSE = 1 * METER
FLIPPER_COLOUR = '#389ebf'
# Step for changing the flipper angle
FLIPPER_ANGLE_STEP = 5
FLIPPER_MAX_ANGLE = 0
FLIPPER_COLOUR = (56, 158, 191)
ACTIVE_FLIPPER_COLOUR = (42, 254, 183)

# Bumper
BUMPER_RADIUS = 25
BUMPER_BOUNCE = 1.15
BUMPER_SCALE = 1.25
BUMPER_COLOUR = '#862dc6'

# Gravity
GRAVITY = 9.81 * METER * GRAVITY_STRENGTH

# Delta Time
dt = 1 / 60

# Farben
WHITE = (250, 250, 250)
BLACK = (5, 5, 5)
RED = (255, 0, 0)
GREY = (25, 25, 25)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
GAME_BG_COLOR = (20, 20, 20)
GUI_BG_COLOR = (5, 5, 5)

# Slider
SLIDER_WIDTH = 280
SLIDER_HEIGHT = 40
SLIDER_MAX_VALUE = 10
SLIDER_MIN_VALUE = 1
SLIDER_MAX_GRAVITY = 2
SLIDER_MIN_GRAVITY = .2
SLIDER_MIN_ANGLE = 0
SLIDER_MAX_ANGLE = 359
SLIDER_COLOR = (100, 100, 100)
SLIDER_HANDLE_COLOR = (150, 150, 150)
SLIDER_TEXT_COLOR = (255, 255, 255)

# Dampening
DAMPING_FACTOR = 0.99

# Friction
ROLLING_FRICTION_COEFFICIENT = 0.01

# Rampen
RAMP_ANGLE = -60
RAMP_LENGTH = 200

SEPARATOR_WIDTH = 8
SEPARATOR_POS = GAME_WIDTH - SEPARATOR_WIDTH / 2
SEPARATOR_COLOR = (0, 0, 0)