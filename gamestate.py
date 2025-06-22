import pygame
from abc import ABC, abstractmethod
from constants import *


class GameState(ABC):
    """Base class for all game states"""
    
    def __init__(self, state_machine):
        self.state_machine = state_machine
    
    @abstractmethod
    def handle_event(self, event):
        """Handle pygame events in this state"""
        pass
    
    @abstractmethod
    def update(self, dt):
        """Update game logic for this state"""
        pass
    
    @abstractmethod
    def draw(self, screen):
        """Draw the current state to screen"""
        pass
    
    def enter(self):
        """Called when entering this state"""
        pass
    
    def exit(self):
        """Called when exiting this state"""
        pass


class StartState(GameState):
    """Start screen state"""
    
    def __init__(self, state_machine, font, title_font):
        super().__init__(state_machine)
        self.font = font
        self.title_font = title_font
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.state_machine.change_state('playing')
            elif event.key == pygame.K_q:
                return False  # Signal to quit
        return True
    
    def update(self, dt):
        pass
    
    def draw(self, screen):
        # Draw title
        title_text = self.title_font.render("ASTEROIDS", True, "white")
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100))
        screen.blit(title_text, title_rect)
        
        # Draw start option
        start_text = self.font.render("Press SPACE to Start", True, "white")
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(start_text, start_rect)
        
        # Draw quit option
        quit_text = self.font.render("Press Q to Quit", True, "white")
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60))
        screen.blit(quit_text, quit_rect)


class PlayingState(GameState):
    """Main gameplay state"""
    
    def __init__(self, state_machine, game_objects):
        super().__init__(state_machine)
        self.game_objects = game_objects
        self.paused = False
    
    def enter(self):
        # Initialize/reset game state
        self.game_objects['lives'] = PLAYER_LIVES
        self.game_objects['respawn_timer'] = 0
        self.game_objects['player'] = self.game_objects['spawn_player']()
        self.game_objects['explosion'] = None
        self.paused = False
        self.game_objects['score'] = 0
        self.game_objects['score_animations'] = []
        self.game_objects['asteroid_explosions'] = []
        
        # Clear existing objects
        for asteroid in self.game_objects['asteroids']:
            asteroid.kill()
        for shot in self.game_objects['shots']:
            shot.kill()
        
        # Create asteroid field
        self.game_objects['AsteroidField']()
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.paused = not self.paused
        return True
    
    def update(self, dt):
        if not self.paused:
            self.game_objects['updatable'].update(dt)
            
            # Update score animations
            for animation in self.game_objects['score_animations'][:]:
                animation.update(dt)
                if animation.lifetime <= 0:
                    self.game_objects['score_animations'].remove(animation)
            
            # Update asteroid explosions
            for explosion in self.game_objects['asteroid_explosions'][:]:
                explosion.update(dt)
                if explosion.lifetime <= 0:
                    self.game_objects['asteroid_explosions'].remove(explosion)
            
            # Collision detection - player vs asteroids
            if (self.game_objects['player'] and 
                self.game_objects['respawn_timer'] <= 0 and 
                not self.game_objects['explosion']):
                for asteroid in self.game_objects['asteroids']:
                    if asteroid.colliding_with(self.game_objects['player']):
                        from explosion import PlayerExplosion
                        self.game_objects['explosion'] = PlayerExplosion(
                            self.game_objects['player'].position.x, 
                            self.game_objects['player'].position.y, 
                            self.game_objects['player'].rotation
                        )
                        self.game_objects['player'].kill()
                        self.game_objects['player'] = None
                        self.game_objects['lives'] -= 1
                        self.game_objects['respawn_timer'] = RESPAWN_TIME
                        
                        # Clear screen
                        for ast in self.game_objects['asteroids']:
                            ast.kill()
                        for shot in self.game_objects['shots']:
                            shot.kill()
                        break
            
            # Collision detection - shots vs asteroids
            for asteroid in self.game_objects['asteroids']:
                for shot in self.game_objects['shots']:
                    if asteroid.colliding_with(shot):
                        self.game_objects['score'] += 100
                        self.game_objects['score_animations'].append(
                            self.game_objects['ScoreAnimation'](asteroid.position.x, asteroid.position.y, "+100")
                        )
                        self.game_objects['asteroid_explosions'].append(
                            self.game_objects['create_explosion'](asteroid.position)
                        )
                        asteroid.split()
                        shot.kill()
                        break
            
            # Handle explosion
            if self.game_objects['explosion']:
                if not self.game_objects['explosion'].update(dt):
                    self.game_objects['explosion'] = None
                    if self.game_objects['lives'] <= 0:
                        self.state_machine.change_state('game_over')
            
            # Handle respawning
            if self.game_objects['respawn_timer'] > 0:
                self.game_objects['respawn_timer'] -= dt
                if (self.game_objects['respawn_timer'] <= 0 and 
                    not self.game_objects['explosion']):
                    self.game_objects['player'] = self.game_objects['spawn_player']()
    
    def draw(self, screen):
        # Draw game objects
        for d in self.game_objects['drawable']:
            d.draw(screen)
        
        # Draw explosion if active
        if self.game_objects['explosion']:
            self.game_objects['explosion'].draw(screen)
        
        # Draw asteroid explosions
        for explosion in self.game_objects['asteroid_explosions']:
            explosion.draw(screen)
        
        # Draw score animations
        for animation in self.game_objects['score_animations']:
            animation.draw(screen)
        
        # Draw heart icon and lives count
        self.game_objects['draw_heart'](screen, 10, 15, 24)
        lives_text = self.game_objects['font'].render(f"x{self.game_objects['lives']}", True, "white")
        screen.blit(lives_text, (40, 10))
        
        # Draw score
        score_text = self.game_objects['font'].render(f"Score: {self.game_objects['score']}", True, "white")
        score_rect = score_text.get_rect()
        score_rect.topright = (SCREEN_WIDTH - 10, 10)
        screen.blit(score_text, score_rect)
        
        # Draw pause screen
        if self.paused:
            pause_text = self.game_objects['font'].render("PAUSED", True, "white")
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20))
            screen.blit(pause_text, pause_rect)
            
            resume_text = self.game_objects['font'].render("Press ESC to Resume", True, "white")
            resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
            screen.blit(resume_text, resume_rect)


class GameOverState(GameState):
    """Game over state"""
    
    def __init__(self, state_machine, game_objects):
        super().__init__(state_machine)
        self.game_objects = game_objects
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.state_machine.change_state('playing')
            elif event.key == pygame.K_q:
                return False  # Signal to quit
        return True
    
    def update(self, dt):
        # Update explosions and score animations
        for animation in self.game_objects['score_animations'][:]:
            animation.update(dt)
            if animation.lifetime <= 0:
                self.game_objects['score_animations'].remove(animation)
        
        for explosion in self.game_objects['asteroid_explosions'][:]:
            explosion.update(dt)
            if explosion.lifetime <= 0:
                self.game_objects['asteroid_explosions'].remove(explosion)
        
        if self.game_objects['explosion']:
            self.game_objects['explosion'].update(dt)
            if self.game_objects['explosion'].lifetime <= 0:
                self.game_objects['explosion'] = None
    
    def draw(self, screen):
        # Draw remaining game objects without player
        for d in self.game_objects['drawable']:
            if not hasattr(d, 'rotation'):  # Player has rotation attribute
                d.draw(screen)
        
        # Draw explosion if active
        if self.game_objects['explosion']:
            self.game_objects['explosion'].draw(screen)
        
        # Draw asteroid explosions
        for explosion in self.game_objects['asteroid_explosions']:
            explosion.draw(screen)
        
        # Draw score animations
        for animation in self.game_objects['score_animations']:
            animation.draw(screen)
        
        # Draw game over screen
        game_over_text = self.game_objects['font'].render("GAME OVER", True, "white")
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40))
        screen.blit(game_over_text, text_rect)
        
        # Draw final score
        final_score_text = self.game_objects['font'].render(f"Final Score: {self.game_objects['score']}", True, "white")
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        screen.blit(final_score_text, score_rect)
        
        # Draw options
        retry_text = self.game_objects['font'].render("Press R to Retry or Q to Quit", True, "white")
        retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 40))
        screen.blit(retry_text, retry_rect)


class GameStateMachine:
    """Finite state machine for managing game states"""
    
    def __init__(self):
        self.states = {}
        self.current_state = None
    
    def add_state(self, name, state):
        """Add a state to the state machine"""
        self.states[name] = state
    
    def change_state(self, state_name):
        """Change to a different state"""
        if state_name not in self.states:
            raise ValueError(f"State '{state_name}' not found")
        
        # Exit current state
        if self.current_state:
            self.current_state.exit()
        
        # Enter new state
        self.current_state = self.states[state_name]
        self.current_state.enter()
    
    def handle_event(self, event):
        """Handle events in the current state"""
        if self.current_state:
            return self.current_state.handle_event(event)
        return True
    
    def update(self, dt):
        """Update the current state"""
        if self.current_state:
            self.current_state.update(dt)
    
    def draw(self, screen):
        """Draw the current state"""
        if self.current_state:
            self.current_state.draw(screen)