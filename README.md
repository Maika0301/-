# NiuTube 3D PC Builder

Python + pyglet prototype of a NiuTube-style game where you:

- Build a PC (choose Windows/Ubuntu, buy parts)
- Run an in-game video site (VM/PC builds, AI battles, tools/sites)
- Use a GUI HUD on top of a simple 3D scene (no CLI, no movie.py)

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Controls
- `1` Toggle OS (Windows/Ubuntu)
- `2` Buy next PC part
- `3` Create channel (prompts in terminal once)
- `4` Publish next video category
- `Tab` Toggle site feed view
- `R` Reset session

## Notes
- 3D rendering uses pyglet (spinning cubes for rig/monitors). The pin to `pyglet==1.5.29` keeps compatibility with older OpenGL drivers that lack `glCreateShader`.
- If your GPU/driver supports OpenGL 2.1+, you can try a newer pyglet (e.g., `pip install \"pyglet>=2.0.10\"`) but older drivers may fail to export `glCreateShader`.
- No external textures or assets required; all geometry is generated.
