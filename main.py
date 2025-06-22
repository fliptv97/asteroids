import pygame
import sys
import random

from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from explosion import PlayerExplosion, AsteroidExplosion
from gamestate import GameStateMachine, StartState, PlayingState, GameOverState


def main():
  pygame.init()
  screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
  font = pygame.font.Font("medodica/MedodicaRegular.otf", 36)
  title_font = pygame.font.Font("medodica/MedodicaRegular.otf", 72)
  
  def draw_heart(surface, x, y, size=16):
    # Draw a simple pixel-art heart
    heart_color = "white"
    pixel_size = size // 8
    
    # Heart pattern (8x8 grid)
    heart_pattern = [
      [0,1,1,0,0,1,1,0],
      [1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1],
      [1,1,1,1,1,1,1,1],
      [0,1,1,1,1,1,1,0],
      [0,0,1,1,1,1,0,0],
      [0,0,0,1,1,0,0,0],
      [0,0,0,0,0,0,0,0]
    ]
    
    for row in range(8):
      for col in range(8):
        if heart_pattern[row][col]:
          pygame.draw.rect(surface, heart_color, 
                         (x + col * pixel_size, y + row * pixel_size, pixel_size, pixel_size))

  updatable = pygame.sprite.Group()
  drawable = pygame.sprite.Group()
  asteroids = pygame.sprite.Group()
  shots = pygame.sprite.Group()

  Player.containers = (updatable, drawable)
  Asteroid.containers = (asteroids, updatable, drawable)
  AsteroidField.containers = updatable
  Shot.containers = (shots, updatable, drawable)

  clock = pygame.time.Clock()
  dt = 0

  def spawn_player():
    return Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
  
  def create_explosion(position):
    return AsteroidExplosion(position.x, position.y, 30)
  
  class ScoreAnimation:
    def __init__(self, x, y, text):
      self.text = text
      self.x = x
      self.y = y
      self.lifetime = 1.0
      self.max_lifetime = 1.0
    
    def update(self, dt):
      self.lifetime -= dt
      self.y -= 50 * dt  # Move up
      return self.lifetime > 0
    
    def draw(self, screen):
      if self.lifetime > 0:
        alpha = self.lifetime / self.max_lifetime
        color_value = max(0, min(255, int(255 * alpha)))
        color = (color_value, color_value, color_value)
        
        # Create surface with per-pixel alpha
        text_surface = font.render(self.text, True, color)
        screen.blit(text_surface, (self.x, self.y))
  
  # Create game objects dictionary for state machine
  game_objects = {
    'updatable': updatable,
    'drawable': drawable,
    'asteroids': asteroids,
    'shots': shots,
    'lives': PLAYER_LIVES,
    'respawn_timer': 0,
    'player': None,
    'explosion': None,
    'score': 0,
    'score_animations': [],
    'asteroid_explosions': [],
    'spawn_player': spawn_player,
    'create_explosion': create_explosion,
    'draw_heart': draw_heart,
    'font': font,
    'ScoreAnimation': ScoreAnimation,
    'AsteroidField': AsteroidField
  }
  
  # Create state machine
  state_machine = GameStateMachine()
  state_machine.add_state('start', StartState(state_machine, font, title_font))
  state_machine.add_state('playing', PlayingState(state_machine, game_objects))
  state_machine.add_state('game_over', GameOverState(state_machine, game_objects))
  
  # Start with the start state
  state_machine.change_state('start')

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        return
      
      # Let state machine handle events
      if not state_machine.handle_event(event):
        return  # State machine signaled to quit

    # Update state machine
    state_machine.update(dt)

    screen.fill("black")
    
    # Draw current state
    state_machine.draw(screen)
    
    pygame.display.flip()
    dt = clock.tick(60) / 1000

if __name__ == "__main__":
  main()
