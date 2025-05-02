import pygame
import random

from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS


class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)

    def update(self, dt):
        self.position += self.velocity * dt

    def split(self):
        self.kill()

        if self.radius == ASTEROID_MIN_RADIUS:
            return

        new_radius = self.radius - ASTEROID_MIN_RADIUS
        angle = random.uniform(25, 50)

        fst = Asteroid(self.position.x, self.position.y, new_radius)
        fst.velocity = self.velocity.rotate(angle) * 1.2
        
        snd = Asteroid(self.position.x, self.position.y, new_radius)
        snd.velocity = self.velocity.rotate(-angle) * 1.2