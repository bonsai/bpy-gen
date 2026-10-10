# bpy-gen

Blender Python (bpy) scripts for procedural character generation and art experiments.

## Tools

- `tools/doraemon_bpy.py` — Generate a simplified Doraemon in Blender with auto-camera-fit
- `render.sh` — Headless render wrapper (Windows Blender → WSL output)

## Quick Render

```bash
./render.sh doraemon     # ドラえもん
./render.sh pagoda       # 五重塔
./render.sh bear         # ローポリ木彫りクマ
```

Output: `~/bpy-gen/outputs/YYYYMMDD_HHMMSS_<model>.png`

## Manual

Open Blender → Scripting editor → Open `tools/doraemon_bpy.py` → Run Script

Or CLI:

```bash
blender --background --python tools/doraemon_bpy.py -- --output ~/data-bpy-gen/renders/doraemon.png
```

## Output locations

- Renders: `~/data-bpy-gen/renders/`
- Scripts: `~/.skills/bpy-gen/tools/`

## Future

- LLM-driven character description → bpy mesh generation via Sakura API
- Rendering pipeline for training data generation
- Drawing improvement learning experiments on Colab GPU
