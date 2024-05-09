import pygame
import math
from config_alt import *
from pygame.locals import *
from config_alt import *

font = pygame.font.SysFont(None, 24) 
    
class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, start_val, label, font):
        self.track = pygame.Rect(x, y, w, h)
        self.handle = pygame.Rect(x, y, h, h)  # Create a square handle
        self.min_val = min_val
        self.max_val = max_val
        self.val = start_val
        self.dragging = False
        self.label = label
        self.font = font

        # Update the handle position to reflect the initial value
        self.update_handle_position()

    def update_handle_position(self):
        """Adjust the handle position based on the slider's current value."""
        # Calculate the position fraction along the track
        position_fraction = (self.val - self.min_val) / (self.max_val - self.min_val)
        # Calculate the new x position of the handle
        handle_x = self.track.left + position_fraction * (self.track.width - self.handle.width)
        # Update the handle's x coordinate
        self.handle.x = handle_x

    def get_value(self):
        """Returns the current value of the slider."""
        return self.val

    def draw(self, window):
        # Draw label with value
        label_surf = self.font.render(f'{self.label}: {self.val:.2f}', True, pygame.Color('white'))
        window.blit(label_surf, (self.track.left, self.track.top - 20))

        # Draw the track
        pygame.draw.rect(window, (200, 200, 200), self.track)
        # Draw the handle
        pygame.draw.rect(window, (100, 100, 100), self.handle)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.handle.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Constrain handle movement within the track
            new_x = max(self.track.left, min(event.pos[0] - self.handle.width // 2, self.track.right - self.handle.width))
            self.handle.x = new_x
            # Update value based on handle's position
            self.val = self.min_val + (self.handle.x - self.track.left) / (self.track.width - self.handle.width) * (self.max_val - self.min_val)


def draw_gui(ball, window, font):
    # Berechnet die Geschwindigkeit aus den Geschwindigkeitskomponenten des Balls
    speed = math.sqrt(ball.speed_x**2 + ball.speed_y**2)
    # Erstellt Text für Position und Geschwindigkeit
    position_text = f'X: {ball.rect.x}, Y: {ball.rect.y}'
    speed_text = f'Speed: {speed:.2f}'
    # Rendert den Text
    position_surf = font.render(position_text, True, pygame.Color('white'))
    speed_surf = font.render(speed_text, True, pygame.Color('white'))
    # Zeichnet Text auf das Fenster
    window.blit(position_surf, (10, 10))
    window.blit(speed_surf, (10, 40))