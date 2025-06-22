import pygame
import sys
import random

from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot
from explosion import PlayerExplosion, AsteroidExplosion


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
  lives = PLAYER_LIVES
  respawn_timer = 0
  player = None
  game_state = GAME_STATE_START
  explosion = None
  paused = False
  score = 0
  score_animations = []
  asteroid_explosions = []

  def spawn_player():
    return Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
  
  def clear_screen():
    # Clear all asteroids and shots
    for asteroid in asteroids:
      asteroid.kill()
    for shot in shots:
      shot.kill()
  
  class ScoreAnimation:
    def __init__(self, text, x, y):
      self.text = text
      self.x = x
      self.y = y
      self.start_y = y
      self.lifetime = 1.0
      self.max_lifetime = 1.0
    
    def update(self, dt):
      self.lifetime -= dt
      self.y -= 50 * dt  # Move up
      return self.lifetime > 0
    
    def draw(self, screen, font):
      if self.lifetime > 0:
        alpha = self.lifetime / self.max_lifetime
        color_value = max(0, min(255, int(255 * alpha)))
        color = (color_value, color_value, color_value)
        
        # Create surface with per-pixel alpha
        text_surface = font.render(self.text, True, color)
        screen.blit(text_surface, (self.x, self.y))
  
  def draw_start_screen():
    # Draw title
    title_text = title_font.render("ASTEROIDS", True, "white")
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 100))
    screen.blit(title_text, title_rect)
    
    # Draw start option
    start_text = font.render("Press SPACE to Start", True, "white")
    start_rect = start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
    screen.blit(start_text, start_rect)
    
    # Draw quit option
    quit_text = font.render("Press Q to Quit", True, "white")
    quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60))
    screen.blit(quit_text, quit_rect)

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        return
      
      # Handle keyboard input
      if event.type == pygame.KEYDOWN:
        if game_state == GAME_STATE_START:
          if event.key == pygame.K_SPACE:  # Start game
            game_state = GAME_STATE_PLAYING
            lives = PLAYER_LIVES
            respawn_timer = 0
            player = spawn_player()
            explosion = None
            paused = False
            score = 0
            score_animations = []
            asteroid_explosions = []
            # Clear any existing objects
            for asteroid in asteroids:
              asteroid.kill()
            for shot in shots:
              shot.kill()
            # Create asteroid field
            AsteroidField()
          elif event.key == pygame.K_q:  # Quit
            return
        elif game_state == GAME_STATE_PLAYING:
          if event.key == pygame.K_ESCAPE:
            paused = not paused  # Toggle pause
        elif game_state == GAME_STATE_GAME_OVER:
          if event.key == pygame.K_r:  # Retry
            game_state = GAME_STATE_PLAYING
            lives = PLAYER_LIVES
            respawn_timer = 0
            player = spawn_player()
            explosion = None
            paused = False
            score = 0
            score_animations = []
            asteroid_explosions = []
            # Clear all existing objects
            for asteroid in asteroids:
              asteroid.kill()
            for shot in shots:
              shot.kill()
            # Create asteroid field
            AsteroidField()
          elif event.key == pygame.K_q:  # Quit
            return

    if game_state == GAME_STATE_PLAYING and not paused:
      updatable.update(dt)
      
      # Update score animations
      score_animations = [anim for anim in score_animations if anim.update(dt)]
      
      # Update asteroid explosions
      asteroid_explosions = [exp for exp in asteroid_explosions if exp.update(dt)]

      if player and respawn_timer <= 0 and not explosion:
        for asteroid in asteroids:
          if asteroid.colliding_with(player):
            # Create explosion at player position
            explosion = PlayerExplosion(player.position.x, player.position.y, player.rotation)
            player.kill()
            player = None
            lives -= 1
            respawn_timer = RESPAWN_TIME
            clear_screen()  # Clear screen immediately when player dies
            
            if lives <= 0:
              # Don't set game_over immediately, let explosion finish first
              respawn_timer = 0  # Stop respawn timer on game over
              # Ensure player is completely removed
              if player:
                player.kill()
                player = None
              print("Game over!")
            else:
              print(f"Lives remaining: {lives}")
            break

      # Update explosion
      if explosion:
        if not explosion.update(dt):
          explosion = None
          # Check if game should end after explosion finishes
          if lives <= 0:
            game_state = GAME_STATE_GAME_OVER

      if respawn_timer > 0:
        respawn_timer -= dt
        if respawn_timer <= 0 and game_state == GAME_STATE_PLAYING and not explosion:
          player = spawn_player()

      for asteroid in asteroids:
        for shot in shots:
          if asteroid.colliding_with(shot):
            # Get score position for animation
            score_rect = font.render(f"{score:06d}", True, "white").get_rect()
            score_rect.topright = (SCREEN_WIDTH - 10, 10)
            
            # Create explosion at asteroid position
            asteroid_explosions.append(AsteroidExplosion(asteroid.position.x, asteroid.position.y, asteroid.radius))
            
            asteroid.split()
            shot.kill()
            # Increase score
            score += 100
            if score > 999999:
              score = 999999
            
            # Add score animation
            score_animations.append(ScoreAnimation("+100", score_rect.right - 60, score_rect.bottom + 5))

    screen.fill("black")
    
    if game_state == GAME_STATE_START:
      draw_start_screen()
    elif game_state == GAME_STATE_PLAYING:
      # Draw game objects
      for d in drawable:
        d.draw(screen)
      
      # Draw explosion if active
      if explosion:
        explosion.draw(screen)
      
      # Draw asteroid explosions
      for asteroid_explosion in asteroid_explosions:
        asteroid_explosion.draw(screen)
      
      # Draw heart icon and lives count
      draw_heart(screen, 10, 15, 24)
      lives_text = font.render(f"x{lives}", True, "white")
      screen.blit(lives_text, (40, 10))
      
      # Draw score animations first (behind score)
      for anim in score_animations:
        anim.draw(screen, font)
      
      # Draw score in upper-right corner (on top)
      score_text = font.render(f"{score:06d}", True, "white")
      score_rect = score_text.get_rect()
      score_rect.topright = (SCREEN_WIDTH - 10, 10)
      screen.blit(score_text, score_rect)
    elif game_state == GAME_STATE_GAME_OVER:
      # Draw remaining game objects without player
      for d in drawable:
        if not hasattr(d, 'rotation'):  # Player has rotation attribute
          d.draw(screen)
      
      # Draw explosion if active
      if explosion:
        explosion.draw(screen)
      
      # Draw asteroid explosions
      for asteroid_explosion in asteroid_explosions:
        asteroid_explosion.draw(screen)
    
    # Draw pause screen
    if paused and game_state == GAME_STATE_PLAYING:
      pause_text = font.render("PAUSED", True, "white")
      pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 20))
      screen.blit(pause_text, pause_rect)
      
      resume_text = font.render("Press ESC to Resume", True, "white")
      resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
      screen.blit(resume_text, resume_rect)
    
    if game_state == GAME_STATE_GAME_OVER:
      game_over_text = font.render("GAME OVER", True, "white")
      text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40))
      screen.blit(game_over_text, text_rect)
      
      retry_text = font.render("Press R to Retry", True, "white")
      retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20))
      screen.blit(retry_text, retry_rect)
      
      quit_text = font.render("Press Q to Quit", True, "white")
      quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 60))
      screen.blit(quit_text, quit_rect)
    
    pygame.display.flip()
    dt = clock.tick(60) / 1000

if __name__ == "__main__":
  main()
