import pygame

from circleshape import CircleShape
from shot import Shot
from constants import PLAYER_RADIUS, PLAYER_TURN_ACCELERATION, PLAYER_MAX_TURN_SPEED, PLAYER_TURN_DRAG, PLAYER_ACCELERATION, PLAYER_MAX_SPEED, PLAYER_DRAG, PLAYER_SHOOT_SPEED, PLAYER_SHOOT_COOLDOWN

class Player(CircleShape):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_RADIUS)

        self.rotation = 0
        self.rotation_velocity = 0
        self.shooting_limiter = 0

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right

        return [a, b, c]

    def draw(self, screen):
        pygame.draw.polygon(screen, "white", self.triangle(), 2)

    def update(self, dt):
        self.shooting_limiter -= dt
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.rotate_accelerate(-dt)
        if keys[pygame.K_d]:
            self.rotate_accelerate(dt)
        
        if keys[pygame.K_w]:
            self.accelerate(dt)
        if keys[pygame.K_s]:
            self.accelerate(-dt)
        if keys[pygame.K_SPACE]:
            self.shoot(dt)
        
        # Apply drag and update position and rotation
        self.velocity *= PLAYER_DRAG
        self.rotation_velocity *= PLAYER_TURN_DRAG
        self.position += self.velocity * dt
        self.rotation += self.rotation_velocity * dt

    def rotate_accelerate(self, dt):
        rotation_accel = PLAYER_TURN_ACCELERATION * dt
        self.rotation_velocity += rotation_accel
        
        # Cap rotation velocity at max speed
        if abs(self.rotation_velocity) > PLAYER_MAX_TURN_SPEED:
            self.rotation_velocity = PLAYER_MAX_TURN_SPEED if self.rotation_velocity > 0 else -PLAYER_MAX_TURN_SPEED

    def accelerate(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        acceleration = forward * PLAYER_ACCELERATION * dt
        self.velocity += acceleration
        
        # Cap velocity at max speed
        if self.velocity.length() > PLAYER_MAX_SPEED:
            self.velocity = self.velocity.normalize() * PLAYER_MAX_SPEED

    def shoot(self, dt):
        if self.shooting_limiter > 0:
            return

        self.shooting_limiter = PLAYER_SHOOT_COOLDOWN
        shot = Shot(self.position.x, self.position.y)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
