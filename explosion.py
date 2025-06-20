import pygame
import random
import math

from circleshape import CircleShape

class Particle(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, 2)
        self.lifetime = random.uniform(1.0, 2.0)
        self.max_lifetime = self.lifetime
        
        # Random velocity for explosion effect
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 150)
        self.velocity = pygame.Vector2(math.cos(angle), math.sin(angle)) * speed
        
    def update(self, dt):
        self.position += self.velocity * dt
        self.lifetime -= dt
        
        # Slow down over time
        self.velocity *= 0.98
        
        if self.lifetime <= 0:
            self.kill()
    
    def draw(self, screen):
        # Fade out as lifetime decreases
        alpha = max(0, self.lifetime / self.max_lifetime)
        color_value = max(0, min(255, int(255 * alpha)))
        color = (color_value, color_value, color_value)
        pygame.draw.circle(screen, color, (int(self.position.x), int(self.position.y)), int(self.radius))

class PlayerExplosion:
    def __init__(self, x, y, rotation):
        self.position = pygame.Vector2(x, y)
        self.rotation = rotation
        self.rotation_speed = random.uniform(300, 600)
        self.scale = 1.0
        self.lifetime = 1.5
        self.max_lifetime = self.lifetime
        self.particles = pygame.sprite.Group()
        
        # Create explosion particles
        for _ in range(15):
            particle = Particle(x, y)
            self.particles.add(particle)
    
    def update(self, dt):
        self.lifetime -= dt
        self.rotation += self.rotation_speed * dt
        self.scale -= dt * 1.5  # Shrink to a point
        self.scale = max(0, self.scale)  # Don't go negative
        
        self.particles.update(dt)
        
        return self.lifetime > 0
    
    def draw(self, screen):
        # Draw spinning ship getting larger
        if self.lifetime > 0.5:  # Only draw ship for first half of explosion
            alpha = (self.lifetime - 0.5) * 2  # Fade out
            forward = pygame.Vector2(0, 1).rotate(self.rotation)
            right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * 20 * self.scale / 1.5
            
            a = self.position + forward * 20 * self.scale
            b = self.position - forward * 20 * self.scale - right
            c = self.position - forward * 20 * self.scale + right
            
            color_value = max(0, min(255, int(255 * alpha)))
            color = (color_value, color_value, color_value)
            pygame.draw.polygon(screen, color, [a, b, c], 2)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(screen)