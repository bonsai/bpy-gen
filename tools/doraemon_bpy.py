"""
Blender Python (bpy) script — simplified Doraemon generator.
Run inside Blender's Scripting editor or: blender --python doraemon_bpy.py
"""

import bpy
import bmesh
import math


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


def add_circle(name, loc, radius, mat):
    bpy.ops.mesh.primitive_circle_add(radius=radius, location=loc, fill_type="NGON")
    obj = bpy.context.active_object
    obj.name = name
    # flatten to face forward
    obj.rotation_euler = (0, math.radians(90), 0)
    obj.data.materials.append(mat)
    # solidify slightly
    mod = obj.modifiers.new(name="Solid", type="SOLIDIFY")
    mod.thickness = 0.02
    return obj


def doraemon():
    clear_scene()

    # Palette
    blue = make_mat("Blue", (0.12, 0.42, 0.85))
    white = make_mat("White", (0.98, 0.98, 0.98))
    red = make_mat("Red", (0.95, 0.15, 0.15))
    yellow = make_mat("Yellow", (0.98, 0.85, 0.1))
    black = make_mat("Black", (0.05, 0.05, 0.05))

    # ── Body ──
    add_sphere("Body", (0, 0, 1.1), 0.75, blue, (1.0, 1.0, 0.95))

    # ── Belly (white patch) ──
    add_sphere("Belly", (0, 0.35, 1.0), 0.55, white, (1.0, 0.6, 1.0))

    # ── Head ──
    add_sphere("Head", (0, 0, 2.15), 0.65, blue)

    # ── Face (white front) ──
    add_sphere("Face", (0, 0.32, 2.2), 0.50, white, (1.0, 0.65, 1.0))

    # ── Eyes ──
    add_sphere("EyeL", (-0.18, 0.55, 2.55), 0.14, white)
    add_sphere("EyeR", ( 0.18, 0.55, 2.55), 0.14, white)
    add_sphere("PupilL", (-0.18, 0.62, 2.62), 0.04, black)
    add_sphere("PupilR", ( 0.18, 0.62, 2.62), 0.04, black)

    # ── Nose ──
    add_sphere("Nose", (0, 0.75, 2.45), 0.07, red)
    # Nose line
    add_cylinder("NoseLine", (0, 0.55, 2.2), 0.015, 0.45, black, (math.radians(90), 0, 0))

    # ── Whiskers ──
    for i, angle in enumerate([-30, 0, 30]):
        rad = math.radians(angle)
        ox = math.sin(rad) * 0.35
        oz = math.cos(rad) * 0.35
        # left
        add_cylinder(f"WhiskerL{i}", (-0.15 - abs(ox), 0.65, 2.2 + oz), 0.008, 0.22, black, (0, math.radians(-10 + angle/3), math.radians(80)))
        # right
        add_cylinder(f"WhiskerR{i}", (0.15 + abs(ox), 0.65, 2.2 + oz), 0.008, 0.22, black, (0, math.radians(10 - angle/3), math.radians(-80)))

    # ── Mouth ──
    add_torus("Mouth", (0, 0.45, 2.05), 0.18, 0.025, red, (math.radians(70), 0, 0))

    # ── Collar ──
    add_torus("Collar", (0, 0, 2.0), 0.52, 0.04, red, (math.radians(90), 0, 0))

    # ── Bell ──
    add_sphere("Bell", (0, -0.05, 1.85), 0.10, yellow)
    add_cylinder("BellSlot", (0, -0.09, 1.85), 0.09, 0.015, black, (math.radians(90), 0, 0))
    add_cylinder("BellHole", (0, -0.13, 1.85), 0.02, 0.01, black, (math.radians(90), 0, 0))

    # ── Arms ──
    add_cylinder("ArmL", (-0.85, -0.05, 1.35), 0.10, 0.55, blue, (0, 0, math.radians(70)))
    add_cylinder("ArmR", ( 0.85, -0.05, 1.35), 0.10, 0.55, blue, (0, 0, math.radians(-70)))
    # Hands
    add_sphere("HandL", (-1.05, -0.05, 1.05), 0.13, white)
    add_sphere("HandR", ( 1.05, -0.05, 1.05), 0.13, white)

    # ── Feet ──
    add_sphere("FootL", (-0.30, 0, 0.35), 0.18, white, (0.8, 1.0, 0.5))
    add_sphere("FootR", ( 0.30, 0, 0.35), 0.18, white, (0.8, 1.0, 0.5))

    # ── Tail ──
    add_sphere("Tail", (0, -0.75, 1.1), 0.06, red)

    # ── Camera & Light ──
    bpy.ops.object.camera_add(location=(2.5, -3.5, 2.8), rotation=(math.radians(65), 0, math.radians(35)))
    cam = bpy.context.active_object
    bpy.context.scene.camera = cam

    bpy.ops.object.light_add(type="SUN", location=(3, -5, 6))
    sun = bpy.context.active_object
    sun.data.energy = 3.0

    # ground plane
    bpy.ops.mesh.primitive_plane_add(size=6, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    gmat = make_mat("Ground", (0.9, 0.9, 0.9), roughness=0.9)
    ground.data.materials.append(gmat)

    print("Doraemon generated! Press F12 to render.")


if __name__ == "__main__":
    doraemon()
