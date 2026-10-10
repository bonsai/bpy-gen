"""
Blender Python — bear catching a salmon (鮭をとる熊).
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


def make_mat(name, color, roughness=0.8):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    return mat


def add_ico(name, loc, radius, mat, subdiv=1, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=radius, location=loc, subdivisions=subdiv)
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


def add_cube(name, loc, size, mat, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_cube_add(size=size, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    obj.data.materials.append(mat)
    return obj


def add_cone(name, loc, radius1, radius2, depth, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(radius1=radius1, radius2=radius2, depth=depth, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.data.materials.append(mat)
    return obj


def camera_fit(padding=1.4):
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
    direction = mathutils.Vector((1.5, -2.2, 0.9)).normalized()
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


def salmon_bear():
    clear_scene()

    # Materials
    bear_fur = make_mat("BearFur", (0.45, 0.30, 0.18), roughness=0.75)
    bear_dark = make_mat("BearDark", (0.30, 0.20, 0.12), roughness=0.85)
    bear_black = make_mat("BearBlack", (0.05, 0.05, 0.05), roughness=0.4)
    salmon_body = make_mat("Salmon", (0.82, 0.45, 0.30), roughness=0.35)
    salmon_belly = make_mat("SalmonBelly", (0.95, 0.75, 0.60), roughness=0.3)
    water = make_mat("Water", (0.25, 0.45, 0.65), roughness=0.15)
    foam = make_mat("Foam", (0.92, 0.95, 0.97), roughness=0.5)
    stone = make_mat("Stone", (0.50, 0.48, 0.45), roughness=0.9)

    # === BEAR (standing, reaching down) ===
    # Body — angling forward
    body = add_ico("Body", (0, 0, 1.0), 0.42, bear_fur, subdiv=1, scale=(1.0, 0.85, 1.1))
    body.rotation_euler = (math.radians(25), 0, 0)

    # Head — looking down at water
    head = add_ico("Head", (0, 0.25, 1.55), 0.28, bear_fur, subdiv=1, scale=(1.05, 0.95, 1.0))
    head.rotation_euler = (math.radians(35), 0, 0)

    # Snout
    add_ico("Snout", (0, 0.42, 1.48), 0.10, bear_dark, subdiv=1, scale=(1.0, 0.8, 0.7))
    add_ico("Nose", (0, 0.50, 1.50), 0.035, bear_black, subdiv=1)

    # Eyes
    add_ico("EyeL", (-0.09, 0.18, 1.60), 0.035, bear_black, subdiv=1)
    add_ico("EyeR", ( 0.09, 0.18, 1.60), 0.035, bear_black, subdiv=1)

    # Ears
    add_ico("EarL", (-0.20, -0.08, 1.78), 0.09, bear_fur, subdiv=1)
    add_ico("EarR", ( 0.20, -0.08, 1.78), 0.09, bear_fur, subdiv=1)

    # Left arm (back / balance)
    add_cylinder("ArmL", (-0.42, -0.20, 0.85), 0.08, 0.60, bear_fur, (math.radians(30), 0, math.radians(50)))

    # Right arm — reaching DOWN into water
    # Upper arm
    upper_arm = add_cylinder("ArmR_Upper", (0.38, 0.15, 0.95), 0.09, 0.40, bear_fur, (math.radians(55), 0, math.radians(-25)))
    # Lower arm (forearm extending down)
    add_cylinder("ArmR_Lower", (0.52, 0.30, 0.55), 0.08, 0.35, bear_fur, (math.radians(70), 0, math.radians(-15)))
    # Paw
    add_ico("PawR", (0.58, 0.38, 0.35), 0.10, bear_dark, subdiv=1, scale=(1.1, 1.2, 0.7))

    # Legs — standing in stream
    add_cylinder("LegL", (-0.22, -0.10, 0.35), 0.11, 0.70, bear_fur)
    add_cylinder("LegR", ( 0.22, -0.10, 0.35), 0.11, 0.70, bear_fur)
    # Paws in water
    add_ico("FootL", (-0.22, -0.10, 0.02), 0.12, bear_dark, subdiv=1, scale=(1.1, 1.3, 0.5))
    add_ico("FootR", ( 0.22, -0.10, 0.02), 0.12, bear_dark, subdiv=1, scale=(1.1, 1.3, 0.5))

    # Tail
    add_ico("Tail", (0, -0.38, 0.90), 0.08, bear_fur, subdiv=1)

    # === SALMON — leaping out of water toward bear's paw ===
    # Body
    salmon = add_ico("SalmonBody", (0.55, 0.45, 0.42), 0.14, salmon_body, subdiv=1, scale=(2.2, 0.7, 0.6))
    salmon.rotation_euler = (math.radians(20), math.radians(15), math.radians(-40))

    # Belly (lighter underside)
    belly = add_ico("SalmonBelly", (0.55, 0.43, 0.40), 0.11, salmon_belly, subdiv=1, scale=(2.0, 0.5, 0.4))
    belly.rotation_euler = (math.radians(20), math.radians(15), math.radians(-40))

    # Tail fin
    add_cone("SalmonTail", (0.82, 0.58, 0.50), 0.08, 0.0, 0.12, salmon_body, (0, math.radians(45), math.radians(-30)))

    # Dorsal fin
    add_cone("SalmonDorsal", (0.48, 0.42, 0.52), 0.04, 0.0, 0.08, salmon_body, (math.radians(-80), 0, math.radians(-40)))

    # Water splash around salmon & paw
    for i in range(6):
        x = 0.45 + (i % 3) * 0.12
        y = 0.30 + (i // 3) * 0.12
        z = 0.28 + (i % 2) * 0.08
        add_ico(f"Splash_{i}", (x, y, z), 0.04 + (i % 3) * 0.02, foam, subdiv=1)

    # Water surface (stream)
    bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0.15))
    water_plane = bpy.context.active_object
    water_plane.name = "WaterSurface"
    water_plane.data.materials.append(water)

    # Ripples (slightly raised rings)
    for i, (wx, wy) in enumerate([(0.55, 0.38), (0.35, 0.25), (0.65, 0.45)]):
        add_cylinder(f"Ripple_{i}", (wx, wy, 0.18), 0.15 + i * 0.08, 0.01, foam, rot=(0, 0, 0))

    # === GROUND / STREAM BED ===
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, -0.05))
    ground = bpy.context.active_object
    ground.name = "Ground"
    gmat = make_mat("Ground", (0.55, 0.50, 0.42), roughness=0.95)
    ground.data.materials.append(gmat)

    # Rocks in stream
    add_ico("Rock1", (-0.6, 0.3, 0.08), 0.12, stone, subdiv=1, scale=(1.3, 1.0, 0.8))
    add_ico("Rock2", (0.8, -0.2, 0.06), 0.10, stone, subdiv=1, scale=(1.0, 1.2, 0.6))
    add_ico("Rock3", (-0.3, -0.5, 0.05), 0.08, stone, subdiv=1, scale=(0.9, 1.1, 0.5))

    # === CAMERA & LIGHT ===
    bpy.ops.object.camera_add(location=(0, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object
    camera_fit(padding=1.35)

    bpy.ops.object.light_add(type="SUN", location=(3, -5, 6))
    sun = bpy.context.active_object
    sun.data.energy = 4.0

    # Rim light for drama
    bpy.ops.object.light_add(type="AREA", location=(-2, 2, 3))
    rim = bpy.context.active_object
    rim.data.energy = 2.0
    rim.data.color = (0.9, 0.95, 1.0)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="/tmp/salmon_bear.png")
    args = parser.parse_args(argv)
    salmon_bear()
    render(args.output)
