import pygame
import sys

from constants import *
from player import Player
from asteroid import Asteroid
from asteroidfield import AsteroidField
from shot import Shot


def main():
  pygame.init()
  screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

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

  player = Player(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
  AsteroidField()

  while True:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        return

    updatable.update(dt)

    for asteroid in asteroids:
      if asteroid.colliding_with(player):
        print("Game over!")

        sys.exit(1)

      for shot in shots:
        if asteroid.colliding_with(shot):
          asteroid.split()
          shot.kill()

    screen.fill("black")
    for d in drawable:
      d.draw(screen)
    pygame.display.flip()

    dt = clock.tick(60) / 1000

if __name__ == "__main__":
  main()
