"""
Blender Python — procedural five-story pagoda (五重塔).
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


def make_mat(name, color, roughness=0.6):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def add_cube(name, loc, size, mat, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_cube_add(size=size, location=loc)
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


def add_cone(name, loc, radius1, radius2, depth, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=radius1, radius2=radius2, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def add_torus(name, loc, major, minor, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=48, minor_segments=16, major_radius=major, minor_radius=minor, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def add_sphere(name, loc, radius, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=radius, location=loc, segments=16, ring_count=12)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def camera_fit(padding=1.3):
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH" and "Ground" not in o.name]
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
    direction = mathutils.Vector((1.2, -1.8, 0.8)).normalized()
    fov = cam.data.angle if cam.data.angle > 0 else math.radians(39.6)
    distance = (size * padding) / math.tan(fov / 2)
    cam.location = center + direction * distance
    look = center - cam.location
    cam.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()


def render(output_path: str, engine: str = "BLENDER_WORKBENCH"):
    scene = bpy.context.scene
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.filepath = output_path
    scene.render.image_settings.file_format = "PNG"
    scene.render.engine = engine
    bpy.ops.render.render(write_still=True)
    print(f"Saved: {output_path}")


def pagoda(stories: int = 5):
    clear_scene()

    stone = make_mat("Stone", (0.55, 0.52, 0.48), roughness=0.85)
    wood = make_mat("Wood", (0.42, 0.18, 0.14), roughness=0.5)
    roof = make_mat("Roof", (0.15, 0.18, 0.25), roughness=0.45)
    gold = make_mat("Gold", (0.85, 0.7, 0.2), roughness=0.25)

    # ── Stone base ──
    add_cube("Base1", (0, 0, 0.15), 1.0, stone, (2.0, 2.0, 0.3))
    add_cube("Base2", (0, 0, 0.38), 1.0, stone, (1.7, 1.7, 0.16))

    current_y = 0.46
    pillar_h = 0.55
    roof_thickness = 0.06

    tier_widths = [1.5, 1.35, 1.2, 1.05, 0.9]
    tier_depths = [0.45, 0.42, 0.38, 0.34, 0.30]

    for i in range(stories):
        w = tier_widths[i]
        h = tier_depths[i]
        floor_z = current_y

        # pillars (4 corners)
        off = w * 0.38
        add_cylinder(f"Pillar_{i}_FL", (-off, -off, floor_z + h / 2), 0.04, h, wood)
        add_cylinder(f"Pillar_{i}_FR", ( off, -off, floor_z + h / 2), 0.04, h, wood)
        add_cylinder(f"Pillar_{i}_BL", (-off,  off, floor_z + h / 2), 0.04, h, wood)
        add_cylinder(f"Pillar_{i}_BR", ( off,  off, floor_z + h / 2), 0.04, h, wood)

        # wall panels
        add_cube(f"Wall_{i}_F", (0, -off, floor_z + h / 2), 1.0, wood, (w * 0.8, 0.04, h * 0.9))
        add_cube(f"Wall_{i}_B", (0,  off, floor_z + h / 2), 1.0, wood, (w * 0.8, 0.04, h * 0.9))
        add_cube(f"Wall_{i}_L", (-off, 0, floor_z + h / 2), 1.0, wood, (0.04, w * 0.8, h * 0.9))
        add_cube(f"Wall_{i}_R", ( off, 0, floor_z + h / 2), 1.0, wood, (0.04, w * 0.8, h * 0.9))

        # floor / ceiling
        add_cube(f"Floor_{i}", (0, 0, floor_z), 1.0, wood, (w * 0.85, w * 0.85, 0.04))

        # roof eaves (torus ring for curve)
        roof_z = floor_z + h + 0.02
        roof_radius = w * 0.62
        add_cone(f"RoofCone_{i}", (0, 0, roof_z + 0.18), roof_radius, roof_radius * 0.15, 0.35, roof, rot=(0, 0, 0))
        add_torus(f"RoofEave_{i}", (0, 0, roof_z + 0.06), roof_radius * 0.85, 0.025, roof)

        current_y = roof_z + 0.20

    # ── Sorin (spire) ──
    spire_z = current_y
    add_cylinder("SorinPole", (0, 0, spire_z + 0.35), 0.04, 0.7, gold)
    for j in range(5):
        add_torus(f"SorinRing_{j}", (0, 0, spire_z + 0.1 + j * 0.12), 0.12 - j * 0.015, 0.018, gold)
    add_cone("SorinTip", (0, 0, spire_z + 0.75), 0.04, 0.0, 0.15, gold)

    # ── Ground ──
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    gmat = make_mat("Ground", (0.88, 0.88, 0.85), roughness=0.95)
    ground.data.materials.append(gmat)

    # Camera & Light
    bpy.ops.object.camera_add(location=(0, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object
    camera_fit(padding=1.4)

    bpy.ops.object.light_add(type="SUN", location=(4, -6, 8))
    sun = bpy.context.active_object
    sun.data.energy = 3.5


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="/tmp/pagoda.png")
    args = parser.parse_args(argv)
    pagoda(5)
    render(args.output)
