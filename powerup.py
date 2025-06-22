import pygame
import math
from abc import ABC, abstractmethod
from circleshape import CircleShape
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class PowerUp(CircleShape):
    """Base class for all power-ups"""
    
    def __init__(self, x, y, radius=15):
        super().__init__(x, y, radius)
        self.lifetime = 30.0  # Power-ups disappear after 30 seconds
        self.pulse_timer = 0.0  # For pulsing animation
    
    def update(self, dt):
        self.lifetime -= dt
        self.pulse_timer += dt * 3  # Pulse animation speed
        
        # Remove power-up if lifetime expired
        if self.lifetime <= 0:
            self.kill()
        
        # Wrap around screen edges
        self.wrap_screen()
    
    @abstractmethod
    def apply_to_player(self, player):
        """Apply the power-up effect to the player"""
        pass
    
    @abstractmethod
    def get_type(self):
        """Return the power-up type identifier"""
        pass


class ShieldPowerUp(PowerUp):
    """Shield power-up that gives the player a protective shield"""
    
    def __init__(self, x, y):
        super().__init__(x, y, 12)
        self.color = "cyan"
    
    def draw(self, screen):
        # Pulsing effect
        pulse = abs(math.sin(self.pulse_timer))
        alpha_factor = 0.6 + 0.4 * pulse
        
        # Draw outer ring (shield visual)
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), 
                         self.radius, 2)
        
        # Draw inner core
        inner_radius = max(3, int(self.radius * 0.3 * alpha_factor))
        pygame.draw.circle(screen, self.color, (int(self.position.x), int(self.position.y)), 
                         inner_radius)
        
        # Draw power-up symbol (+ sign)
        center_x, center_y = int(self.position.x), int(self.position.y)
        symbol_size = 4
        pygame.draw.line(screen, "white", 
                        (center_x - symbol_size, center_y), 
                        (center_x + symbol_size, center_y), 2)
        pygame.draw.line(screen, "white", 
                        (center_x, center_y - symbol_size), 
                        (center_x, center_y + symbol_size), 2)
    
    def apply_to_player(self, player):
        """Give the player a shield"""
        return player.add_shield()
    
    def get_type(self):
        return "shield"


class PlayerShield:
    """Shield effect for the player"""
    
    def __init__(self):
        self.active = True
        self.pulse_timer = 0.0
        self.hit_flash = 0.0  # Flash effect when hit
    
    def update(self, dt):
        self.pulse_timer += dt * 2
        if self.hit_flash > 0:
            self.hit_flash -= dt * 5
    
    def draw(self, screen, player_position, player_radius):
        if not self.active:
            return
        
        # Pulsing shield effect
        pulse = abs(math.sin(self.pulse_timer))
        
        # Shield color - flashes red when hit
        if self.hit_flash > 0:
            color = "red"
            alpha_factor = 0.8 + 0.2 * pulse
        else:
            color = "cyan"
            alpha_factor = 0.4 + 0.3 * pulse
        
        # Draw shield circle around player
        shield_radius = player_radius + 15
        pygame.draw.circle(screen, color, 
                         (int(player_position.x), int(player_position.y)), 
                         shield_radius, 2)
        
        # Draw shield energy particles
        for i in range(8):
            angle = (i * 45) + (self.pulse_timer * 30)
            particle_distance = shield_radius - 2
            particle_x = player_position.x + math.cos(math.radians(angle)) * particle_distance
            particle_y = player_position.y + math.sin(math.radians(angle)) * particle_distance
            
            particle_alpha = alpha_factor * (0.5 + 0.5 * math.sin(self.pulse_timer + i))
            if particle_alpha > 0.3:
                pygame.draw.circle(screen, color, 
                                 (int(particle_x), int(particle_y)), 1)
    
    def take_hit(self):
        """Called when shield takes a hit"""
        self.hit_flash = 1.0
        self.active = False
        return True  # Shield absorbed the hit