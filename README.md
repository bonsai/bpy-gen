# bpy-gen

Blender Python (bpy) scripts for procedural character generation and art experiments.

## Tools

- `tools/doraemon_bpy.py` — ドラえもん
- `tools/pagoda_bpy.py` — 五重塔
- `tools/bear_bpy.py` — ローポリ木彫りクマ
- `render.sh` — Headless render + MEGA sync wrapper

## Quick Render

```bash
./render.sh doraemon     # ドラえもん
./render.sh pagoda       # 五重塔
./render.sh bear         # ローポリ木彫りクマ
```

Output: `~/bpy-gen/outputs/YYYYMMDD_HHMMSS_<model>.png`

## Output locations

- Renders: `~/bpy-gen/outputs/`
- MEGA: `MEGA/bpy-gen/outputs/`
- Scripts: `~/.skills/bpy-gen/tools/`

## MEGA setup

```bash
rclone config
# Create new remote → mega → enter username + password
```

After setup, `render.sh` auto-syncs renders to MEGA.

## Future

- LLM-driven character description → bpy mesh generation via Sakura API
- Drawing improvement learning experiments on Colab GPU
