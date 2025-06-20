import pygame
import random
import math

from circleshape import CircleShape
from constants import ASTEROID_MIN_RADIUS


class Asteroid(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.lumps = self._generate_lumps()

    def _generate_lumps(self):
        num_points = random.randint(8, 12)
        points = []
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            radius_variation = random.uniform(0.7, 1.3)
            actual_radius = self.radius * radius_variation
            x = actual_radius * math.cos(angle)
            y = actual_radius * math.sin(angle)
            points.append(pygame.Vector2(x, y))
        return points

    def draw(self, screen):
        world_points = []
        for point in self.lumps:
            world_point = self.position + point
            world_points.append(world_point)
        
        if len(world_points) > 2:
            pygame.draw.polygon(screen, "white", world_points, 2)

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