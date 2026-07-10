# Demon Arena

Demon Arena is a simple 3D survival shooter made with Python, PyOpenGL, GLUT, and basic OpenGL primitives.

## Academic Context

This project was developed as part of the CSE423 Computer Graphics course. It demonstrates basic 3D rendering, player movement, camera control, collision detection, animation, HUD design, minimap rendering, and simple game logic using Python, PyOpenGL, and GLUT.

## Features

- Start menu with keyboard controls
- First-person and third-person camera modes
- Player walking animation
- Extended arena map with wall collision
- Three weapons: Pistol, Rifle, and Rocket Launcher
- Three demon types:
  - Normal Demon
  - Flying Demon
  - Bulky Tank Demon
- Enemy health bars
- Minimap
- Powerups
- Reload and ammo system
- Rocket explosion area damage
- Game restart and main menu return

## Controls

| Key | Action |
| --- | --- |
| ENTER / S | Start game |
| E / ESC | Exit from menu |
| W A S D | Move |
| Arrow Left / Right | Turn camera |
| Arrow Up / Down | Aim up or down |
| SPACE | Shoot |
| B | Reload |
| 1 | Select Pistol |
| 2 | Select Rifle |
| 3 | Select Rocket Launcher |
| C | Switch camera mode |
| J | Toggle cheat mode |
| R | Restart after game over |
| M | Return to main menu |

## Requirements

Install Python 3 and the required OpenGL packages:

```bash
pip install PyOpenGL PyOpenGL_accelerate
```

If GLUT does not run on your system, install FreeGLUT.

## Run

```bash
python demon_arena.py
```

## Project Structure

```text
demon_arena.py   # Main game source code
README.md        # Project documentation
```

## Notes

This project uses only built-in OpenGL/GLUT drawing primitives. It does not use external textures, 3D models, or game engines.
