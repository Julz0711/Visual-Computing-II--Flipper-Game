import pygame
import random
from config_alt import *

class Ball:
    def __init__(self):
        self.radius = BALL_DIAMETER // 2  # Assuming BALL_DIAMETER is defined in your config
        self.rect = pygame.Rect(0, 0, BALL_DIAMETER, BALL_DIAMETER)  # Initialize the rect
        self.speed_x = 0  # Initial horizontal speed
        self.speed_y = 0  # Initial vertical speed
        self.active = False  # Indicates whether the ball is active or not

    def set_position(self, x, y):
        """Sets the ball's position to a new location, adjusting for the center of the ball."""
        self.rect.x = x - self.radius
        self.rect.y = y - self.radius
        self.speed_x = random.choice([-1, 1]) * BALL_INITIAL_SPEED  # Randomly choose initial horizontal speed
        self.speed_y = BALL_INITIAL_SPEED  # Set initial vertical speed
        self.active = True  # Activate the ball to start moving

    def move(self):
        """Updates the ball's position based on its speed, and handles wall collisions."""
        if not self.active:
            return  # Skip moving if the ball isn't active

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        # Apply gravity, if your game logic includes it
        self.speed_y += GRAVITY

        # Handle collisions with the window boundaries
        if self.rect.left <= 0 or self.rect.right >= WINDOW_WIDTH:
            self.speed_x = -self.speed_x
        if self.rect.top <= 0:
            self.speed_y = -self.speed_y
        if self.rect.bottom >= WINDOW_HEIGHT:
            self.active = False  # Optionally deactivate the ball

    def draw(self, surface):
        """Draw the ball on the specified surface."""
        pygame.draw.circle(surface, (255, 255, 255), self.rect.center, self.radius)
