#!/usr/bin/env bash
# Render any bpy-gen model via Windows Blender.
# Usage: ./render.sh <model_name>
#   model_name: doraemon | pagoda | bear
set -euo pipefail

SCRIPT_NAME="${1:-doraemon}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RENDER_DIR="$HOME/bpy-gen/outputs"
mkdir -p "$RENDER_DIR"

# Map aliases to script files
case "$SCRIPT_NAME" in
  doraemon|ドラえもん) SCRIPT="tools/doraemon_bpy.py" ;;
  pagoda|五重塔)        SCRIPT="tools/pagoda_bpy.py" ;;
  bear|クマ|木彫り)     SCRIPT="tools/bear_bpy.py" ;;
  *)
    echo "Unknown model: $SCRIPT_NAME"
    echo "Available: doraemon, pagoda, bear"
    exit 1
    ;;
esac

SKILL_DIR="$HOME/.skills/bpy-gen"
WIN_RENDER_DIR=$(wslpath -w "$RENDER_DIR")
WIN_SCRIPT=$(wslpath -w "$SKILL_DIR/$SCRIPT")
BLENDER="/mnt/c/Program Files/Blender Foundation/Blender 5.0/blender.exe"

OUTPUT_NAME="${TIMESTAMP}_${SCRIPT_NAME}.png"
OUTPUT_FILE="${WIN_RENDER_DIR}\\${OUTPUT_NAME}"

"$BLENDER" --background --python "$WIN_SCRIPT" -- --output "$OUTPUT_FILE"

python3 "$SKILL_DIR/tools/log_render.py" "$SCRIPT_NAME" "$RENDER_DIR/$OUTPUT_NAME" "ok"

echo "Saved: $RENDER_DIR/$OUTPUT_NAME"
