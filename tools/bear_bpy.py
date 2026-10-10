"""
Blender Python — low-poly wooden carved bear (木彫りクマ).
"""
import bpy
import math
import mathutils


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
    direction = mathutils.Vector((1.2, -1.6, 0.7)).normalized()
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


def bear():
    clear_scene()

    wood = make_mat("Wood", (0.50, 0.35, 0.22), roughness=0.75)
    dark = make_mat("DarkWood", (0.35, 0.24, 0.15), roughness=0.85)
    black = make_mat("Black", (0.06, 0.06, 0.06), roughness=0.4)

    # Body — chunky low-poly torso
    add_ico("Body", (0, 0, 0.55), 0.38, wood, subdiv=1, scale=(1.0, 0.85, 1.05))

    # Head
    add_ico("Head", (0, 0.05, 1.05), 0.30, wood, subdiv=1, scale=(1.05, 0.95, 1.0))

    # Snout
    add_ico("Snout", (0, 0.28, 0.98), 0.12, dark, subdiv=1, scale=(1.0, 0.8, 0.7))

    # Nose tip
    add_ico("Nose", (0, 0.38, 1.02), 0.04, black, subdiv=1)

    # Eyes (small dark spheres)
    add_ico("EyeL", (-0.10, 0.18, 1.10), 0.04, black, subdiv=1)
    add_ico("EyeR", ( 0.10, 0.18, 1.10), 0.04, black, subdiv=1)

    # Ears
    add_ico("EarL", (-0.22, -0.05, 1.30), 0.10, wood, subdiv=1)
    add_ico("EarR", ( 0.22, -0.05, 1.30), 0.10, wood, subdiv=1)

    # Inner ears
    add_ico("EarInnerL", (-0.22, -0.02, 1.30), 0.05, dark, subdiv=1)
    add_ico("EarInnerR", ( 0.22, -0.02, 1.30), 0.05, dark, subdiv=1)

    # Arms
    add_cylinder("ArmL", (-0.42, 0.05, 0.60), 0.09, 0.45, wood, (0, 0, math.radians(65)))
    add_cylinder("ArmR", ( 0.42, 0.05, 0.60), 0.09, 0.45, wood, (0, 0, math.radians(-65)))

    # Legs
    add_cylinder("LegL", (-0.20, 0, 0.18), 0.10, 0.35, wood)
    add_cylinder("LegR", ( 0.20, 0, 0.18), 0.10, 0.35, wood)

    # Paws
    add_ico("PawL", (-0.20, 0.08, 0.05), 0.10, dark, subdiv=1, scale=(1.0, 1.2, 0.6))
    add_ico("PawR", ( 0.20, 0.08, 0.05), 0.10, dark, subdiv=1, scale=(1.0, 1.2, 0.6))

    # Tail stub
    add_ico("Tail", (0, -0.35, 0.55), 0.08, wood, subdiv=1)

    # Ground
    bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, 0))
    ground = bpy.context.active_object
    ground.name = "Ground"
    gmat = make_mat("Ground", (0.85, 0.83, 0.80), roughness=0.95)
    ground.data.materials.append(gmat)

    # Camera / Light
    bpy.ops.object.camera_add(location=(0, 0, 0))
    bpy.context.scene.camera = bpy.context.active_object
    camera_fit(padding=1.4)

    bpy.ops.object.light_add(type="SUN", location=(3, -5, 5))
    sun = bpy.context.active_object
    sun.data.energy = 3.0


if __name__ == "__main__":
    bear()
    render("/tmp/bear.png")
