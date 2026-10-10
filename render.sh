#!/usr/bin/env bash
# Render Doraemon via Windows Blender, save to ~/data-bpy-gen/renders/
set -euo pipefail

RENDER_DIR="$HOME/data-bpy-gen/renders"
mkdir -p "$RENDER_DIR"

WIN_RENDER_DIR=$(wslpath -w "$RENDER_DIR")
WIN_SCRIPT=$(wslpath -w "$HOME/.skills/bpy-gen/tools/doraemon_bpy.py")
BLENDER="/mnt/c/Program Files/Blender Foundation/Blender 5.0/blender.exe"

"$BLENDER" --background --python "$WIN_SCRIPT" -- --output "$WIN_RENDER_DIR/doraemon.png"

# Show local path
echo "Saved: $RENDER_DIR/doraemon.png"
