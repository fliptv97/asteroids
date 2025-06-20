# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a classic Asteroids game implemented in Python using pygame. The game features a player ship that can move, rotate, and shoot at asteroids that spawn from the screen edges and split into smaller pieces when hit.

## Development Commands

### Running the Game
```bash
python3 main.py
```

### Setting up Environment
```bash
pip install -r requirements.txt
```

The only dependency is pygame==2.6.1.

## Architecture

### Core Game Loop
The main game loop is in `main.py:11-57` and follows the standard pygame pattern:
- Event handling (quit detection)
- Update all game objects via sprite groups
- Collision detection between player/asteroids and shots/asteroids
- Render all drawable objects
- Maintain 60 FPS with clock timing

### Sprite Group System
The game uses pygame's sprite group system for efficient object management:
- `updatable`: All objects that need update() called
- `drawable`: All objects that need draw() called  
- `asteroids`: Asteroid objects for collision detection
- `shots`: Shot objects for collision detection

### Class Hierarchy
- `CircleShape` (circleshape.py): Base class with position, velocity, radius, and collision detection
- `Player` (player.py): Inherits from CircleShape, handles input and shooting
- `Asteroid` (asteroid.py): Inherits from CircleShape, handles splitting behavior
- `Shot` (shot.py): Inherits from CircleShape, represents bullets
- `AsteroidField` (asteroidfield.py): Spawns asteroids from screen edges

### Key Systems

**Movement**: All objects use pygame.Vector2 for position and velocity with delta-time based movement.

**Collision**: Simple circle-to-circle collision using distance calculation in `CircleShape.colliding_with()`.

**Controls**: WASD for movement/rotation, SPACE for shooting with cooldown system.

**Asteroid Spawning**: `AsteroidField` spawns asteroids at random edges with random velocities every 0.8 seconds.

**Asteroid Splitting**: When shot, asteroids split into two smaller asteroids (unless already minimum size) with rotated velocities.

## Game Constants

All game parameters are centralized in `constants.py` including screen dimensions, speeds, spawn rates, and object sizes.

## Future Enhancements

See `todo.md` for planned features including scoring, multiple lives, explosions, power-ups, and visual improvements.
