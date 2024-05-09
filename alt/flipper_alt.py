import pygame
import math

class Flipper:
    def __init__(self, pivot_x, pivot_y, length, angle, color):
        self.pivot_x = pivot_x
        self.pivot_y = pivot_y
        self.length = length
        self.angle = angle
        self.color = color
        self.calculate_endpoints()

    def calculate_endpoints(self):
        """ Calculate the end points based on the current angle. """
        rad_angle = math.radians(self.angle)
        self.end_x = self.pivot_x + self.length * math.cos(rad_angle)
        self.end_y = self.pivot_y - self.length * math.sin(rad_angle)

    def rotate(self, direction, speed):
        """ Rotate the flipper within allowed angle limits. """
        new_angle = self.angle + (direction * speed)
        if -30 <= new_angle <= 30:  # Assuming flipper can rotate between -30 to 30 degrees
            self.angle = new_angle
        self.calculate_endpoints()

    def draw(self, window):
        """ Draw the flipper on the window. """
        start = (self.pivot_x, self.pivot_y)
        end = (self.end_x, self.end_y)
        pygame.draw.line(window, self.color, start, end, 10)  # 10 is the line thickness

    def get_line(self):
        """ Get the line representing the flipper for collision calculations. """
        return (self.pivot_x, self.pivot_y, self.end_x, self.end_y)

    def reflect(self, ball_speed):
        """ Reflects the ball's velocity based on the flipper's orientation. """
        normal = self.get_normal()
        speed_mag = math.sqrt(ball_speed[0]**2 + ball_speed[1]**2)
        dot_product = ball_speed[0] * normal[0] + ball_speed[1] * normal[1]
        reflected = (
            ball_speed[0] - 2 * dot_product * normal[0],
            ball_speed[1] - 2 * dot_product * normal[1]
        )
        reflected_mag = math.sqrt(reflected[0]**2 + reflected[1]**2)
        return (reflected[0] / reflected_mag * speed_mag, reflected[1] / reflected_mag * speed_mag)

    def get_normal(self):
        """ Calculate the normal to the line of the flipper for physics calculations. """
        dx = self.end_x - self.pivot_x
        dy = self.end_y - self.pivot_y
        normal = (-dy, dx)
        normal_length = math.sqrt(normal[0]**2 + normal[1]**2)
        return (normal[0] / normal_length, normal[1] / normal_length)
