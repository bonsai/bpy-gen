"""
Blender Python (bpy) script — simplified Doraemon generator.
Run inside Blender's Scripting editor or headless:
    blender --background --python doraemon_bpy.py -- --output /tmp/doraemon.png
"""
import bpy
import math
import mathutils
import sys
import argparse


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for m in bpy.data.materials:
        bpy.data.materials.remove(m)


def make_mat(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def add_sphere(name, loc, radius, mat, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=32, ring_count=16)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    return obj


def add_cylinder(name, loc, radius, depth, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def add_torus(name, loc, major, minor, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=32, minor_segments=16, major_radius=major, minor_radius=minor, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def doraemon():
    clear_scene()

    blue = make_mat("Blue", (0.12, 0.42, 0.85))
    white = make_mat("White", (0.98, 0.98, 0.98))
    red = make_mat("Red", (0.95, 0.15, 0.15))
    yellow = make_mat("Yellow", (0.98, 0.85, 0.1))
    black = make_mat("Black", (0.05, 0.05, 0.05))

    # Body
    add_sphere("Body", (0, 0, 1.1), 0.75, blue, (1.0, 1.0, 0.95))
    add_sphere("Belly", (0, 0.35, 1.0), 0.55, white, (1.0, 0.6, 1.0))

    # Head
    add_sphere("Head", (0, 0, 2.15), 0.65, blue)
    add_sphere("Face", (0, 0.32, 2.2), 0.50, white, (1.0, 0.65, 1.0))

    # Eyes
    add_sphere("EyeL", (-0.18, 0.55, 2.55), 0.14, white)
    add_sphere("EyeR", ( 0.18, 0.55, 2.55), 0.14, white)
    add_sphere("PupilL", (-0.18, 0.62, 2.62), 0.04, black)
    add_sphere("PupilR", ( 0.18, 0.62, 2.62), 0.04, black)

    # Nose
    add_sphere("Nose", (0, 0.75, 2.45), 0.07, red)
    add_cylinder("NoseLine", (0, 0.55, 2.2), 0.015, 0.45, black, (math.radians(90), 0, 0))

    # Whiskers
    for i, angle in enumerate([-30, 0, 30]):
        rad = math.radians(angle)
        ox = math.sin(rad) * 0.35
        oz = math.cos(rad) * 0.35
        add_cylinder(f"WhiskerL{i}", (-0.15 - abs(ox), 0.65, 2.2 + oz), 0.008, 0.22, black, (0, math.radians(-10 + angle/3), math.radians(80)))
        add_cylinder(f"WhiskerR{i}", (0.15 + abs(ox), 0.65, 2.2 + oz), 0.008, 0.22, black, (0, math.radians(10 - angle/3), math.radians(-80)))

    # Mouth / Collar / Bell
    add_torus("Mouth", (0, 0.45, 2.05), 0.18, 0.025, red, (math.radians(70), 0, 0))
    add_torus("Collar", (0, 0, 2.0), 0.52, 0.04, red, (math.radians(90), 0, 0))
    add_sphere("Bell", (0, -0.05, 1.85), 0.10, yellow)
    add_cylinder("BellSlot", (0, -0.09, 1.85), 0.09, 0.015, black, (math.radians(90), 0, 0))
    add_cylinder("BellHole", (0, -0.13, 1.85), 0.02, 0.01, black, (math.radians(90), 0, 0))

    # Arms / Hands
    add_cylinder("ArmL", (-0.85, -0.05, 1.35), 0.10, 0.55, blue, (0, 0, math.radians(70)))
    add_cylinder("ArmR", ( 0.85, -0.05, 1.35), 0.10, 0.55, blue, (0, 0, math.radians(-70)))
    add_sphere("HandL", (-1.05, -0.05, 1.05), 0.13, white)
    add_sphere("HandR", ( 1.05, -0.05, 1.05), 0.13, white)

    # Feet / Tail
    add_sphere("FootL", (-0.30, 0, 0.35), 0.18, white, (0.8, 1.0, 0.5))
    add_sphere("FootR", ( 0.30, 0, 0.35), 0.18, white, (0.8, 1.0, 0.5))
    add_sphere("Tail", (0, -0.75, 1.1), 0.06, red)

    # Camera auto-fit
    camera_fit(padding=1.3)

    # Light
    bpy.ops.object.light_add(type="SUN", location=(3, -5, 6))
    sun = bpy.context.active_object
    sun.data.energy = 3.0

    # Ground
    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
    gmat = make_mat("Ground", (0.9, 0.9, 0.9), roughness=0.9)
    bpy.context.active_object.data.materials.append(gmat)


def camera_fit(padding=1.3):
    """Position scene camera to fit all mesh objects (ignoring Ground)."""
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and o.name != "Ground"]
    if not meshes:
        return
    min_co = mathutils.Vector((float("inf"),) * 3)
    max_co = mathutils.Vector((float("-inf"),) * 3)
    for obj in meshes:
        for v in obj.bound_box:
            world_v = obj.matrix_world @ mathutils.Vector(v)
            for i in range(3):
                min_co[i] = min(min_co[i], world_v[i])
                max_co[i] = max(max_co[i], world_v[i])
    center = (min_co + max_co) / 2
    size = (max_co - min_co).length / 2
    cam = bpy.context.scene.camera
    if not cam:
        bpy.ops.object.camera_add(location=(0, 0, 0))
        cam = bpy.context.active_object
        bpy.context.scene.camera = cam
    direction = mathutils.Vector((1.0, -1.8, 0.9)).normalized()
    fov = cam.data.angle if cam.data.angle > 0 else math.radians(39.6)
    distance = (size * padding) / math.tan(fov / 2)
    cam.location = center + direction * distance
    look = center - cam.location
    cam.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()


def render(output_path: str, engine: str | None = None):
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = "PNG"

    engines = [engine] if engine else ["BLENDER_EEVEE", "BLENDER_WORKBENCH"]
    for e in engines:
        if e in ("BLENDER_EEVEE", "BLENDER_WORKBENCH", "CYCLES"):
            try:
                scene.render.engine = e
                bpy.ops.render.render(write_still=True)
                print(f"Saved: {output_path} (engine={e})")
                return
            except Exception as exc:
                print(f"Engine {e} failed: {exc}")
                continue
    raise RuntimeError("No render engine succeeded.")


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="/tmp/doraemon.png")
    parser.add_argument("--engine", default=None, help="Render engine override")
    args = parser.parse_args(argv)

    doraemon()
    render(args.output, args.engine)
