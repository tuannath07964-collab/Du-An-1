# Blender 3.6+ script: An Yen restaurant cutaway diorama.
# Run from Blender's Scripting workspace. It saves .blend, .glb and a PNG render beside this file.

import bpy
import math
from pathlib import Path
from mathutils import Vector

OUT = Path(r"D:\AnYen-Reservation-Concept")
OUT.mkdir(parents=True, exist_ok=True)

# Start with an empty scene.
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.materials, bpy.data.curves, bpy.data.cameras, bpy.data.lights):
    # Keep the scene self-contained; orphan data is harmless, so no global purge is needed.
    pass

def material(name, color, metallic=0.0, roughness=0.55, emission=None):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        emission_color = bsdf.inputs.get("Emission Color")
        if emission_color is None:
            emission_color = bsdf.inputs.get("Emission")
        if emission_color is not None:
            emission_color.default_value = (*color, 1.0)
        emission_strength = bsdf.inputs.get("Emission Strength")
        if emission_strength is not None:
            emission_strength.default_value = emission
    return m

charcoal = material("Charcoal | lacquer", (0.045, 0.058, 0.049), 0.18, 0.28)
deep_green = material("Deep green | walls", (0.12, 0.19, 0.15), 0.05, 0.7)
mint = material("Mint | edge light", (0.18, 0.95, 0.62), 0.12, 0.3, 0.28)
cream = material("Warm ivory | stone", (0.91, 0.79, 0.56), 0.0, 0.48)
amber = material("Amber | wood", (0.55, 0.29, 0.12), 0.0, 0.62)
red = material("Oxblood | accent", (0.38, 0.045, 0.035), 0.05, 0.42)
metal = material("Brushed bronze", (0.32, 0.22, 0.12), 0.72, 0.28)
leaf = material("Garden green", (0.08, 0.34, 0.2), 0.0, 0.7)

def finish(obj, name, mat, bevel=0.0):
    obj.name = name
    if mat:
        obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new("Soft cut edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    return obj

def box(name, loc, dims, mat, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.object
    obj.dimensions = dims
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)

def cylinder(name, loc, radius, depth, mat, vertices=32, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    return finish(bpy.context.object, name, mat, bevel)

def sphere(name, loc, scale, mat, ico=False):
    if ico:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=loc)
    else:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, radius=1, location=loc)
    obj = bpy.context.object
    obj.scale = scale
    return finish(obj, name, mat)

# Square plinth and the open-front, open-roof restaurant shell.
box("Square floating plinth", (0, 0, 0.05), (6.5, 6.5, 0.42), charcoal, 0.13)
box("Copper reveal band", (0, 0, 0.28), (6.22, 6.22, 0.12), amber, 0.035)
box("Restaurant floor", (0, 0, 0.43), (5.95, 5.95, 0.18), cream, 0.05)
# Floor inlay grid.
for x in (-1.95, 0, 1.95):
    box("Floor inlay", (x, 0, 0.527), (0.025, 5.55, 0.009), metal)
for y in (-1.95, 0, 1.95):
    box("Floor inlay", (0, y, 0.528), (5.55, 0.025, 0.009), metal)

# Back and side walls. The open front and top keep the interior readable.
box("Back wall", (0, 2.83, 2.02), (5.95, 0.22, 3.05), deep_green, 0.06)
box("Right wall", (2.83, 0.15, 2.02), (0.22, 5.58, 3.05), charcoal, 0.06)
box("Left low divider", (-2.83, 1.0, 1.26), (0.22, 3.65, 1.48), deep_green, 0.05)
# Warm wood slats and mint trim.
for x in (-2.42, -2.12, -1.82, -1.52):
    box("Back wall timber slat", (x, 2.69, 2.10), (0.075, 0.06, 2.45), amber, 0.018)
box("Mint back edge", (0, 2.69, 3.56), (5.72, 0.05, 0.055), mint, 0.018)
box("Mint side edge", (2.69, 0, 3.56), (0.05, 5.55, 0.055), mint, 0.018)
# A low counter and service niche.
box("Service counter base", (1.73, 1.94, 0.93), (1.72, 0.55, 0.72), amber, 0.07)
box("Service counter stone", (1.73, 1.94, 1.31), (1.82, 0.62, 0.09), cream, 0.035)
box("Back niche", (1.73, 2.68, 2.22), (1.55, 0.08, 1.05), charcoal, 0.035)
for i, c in enumerate((amber, red, mint)):
    box("Niche bottle", (1.28 + i*0.42, 2.60, 1.91), (0.16, 0.13, 0.45 + (i%2)*0.12), c, 0.04)

# Four round tables with bronze stems and simple chairs.
table_positions = [(-1.38, -1.2), (0.62, -1.2), (-1.38, 0.86), (0.62, 0.86)]
for idx, (x, y) in enumerate(table_positions, 1):
    cylinder(f"Table {idx} | pedestal foot", (x, y, 0.66), 0.30, 0.10, metal, 32, 0.02)
    cylinder(f"Table {idx} | pedestal", (x, y, 0.99), 0.085, 0.62, metal, 24, 0.018)
    cylinder(f"Table {idx} | ivory top", (x, y, 1.34), 0.57, 0.13, cream, 48, 0.035)
    # Tiny centerpiece.
    cylinder(f"Table {idx} | vase", (x, y, 1.49), 0.095, 0.18, amber, 20, 0.02)
    sphere(f"Table {idx} | leaves", (x, y, 1.63), (0.19, 0.15, 0.22), leaf, True)
    # Two chairs facing each table.
    for side in (-1, 1):
        cy = y - side*0.84
        box(f"Chair {idx}-{side} | seat", (x, cy, 0.88), (0.58, 0.52, 0.13), charcoal, 0.055)
        box(f"Chair {idx}-{side} | back", (x, cy-side*0.23, 1.22), (0.58, 0.10, 0.62), amber, 0.045)
        for dx in (-0.21, 0.21):
            box(f"Chair {idx}-{side} | leg", (x+dx, cy, 0.68), (0.055, 0.055, 0.36), metal, 0.012)

# Pendant lights over the dining area.
for x, y in [(-1.38, -1.2), (0.62, -1.2), (-1.38, 0.86), (0.62, 0.86)]:
    cylinder("Pendant | stem", (x, y, 3.07), 0.018, 0.72, metal, 16)
    bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.30, radius2=0.12, depth=0.22, location=(x, y, 2.68))
    finish(bpy.context.object, "Pendant | warm shade", amber, 0.025)
    sphere("Pendant | glowing core", (x, y, 2.55), (0.09, 0.09, 0.07), cream)
# Small indoor garden at the open corner.
cylinder("Planter", (-2.17, -2.08, 0.74), 0.48, 0.42, charcoal, 8, 0.045)
for i, (dx, dy, dz) in enumerate(((-.18,0,.55),(.13,.08,.7),(.04,-.13,.47),(.2,-.08,.59))):
    sphere(f"Garden leaf {i}", (-2.17+dx, -2.08+dy, 0.96+dz), (0.18,0.11,0.34), leaf, True)

# Front entrance step and small standalone signage on the plinth.
box("Entry step", (0, -3.25, 0.24), (2.1, 0.34, 0.23), cream, 0.04)
box("Entry accent", (0, -3.44, 0.13), (1.18, 0.025, 0.035), red, 0.01)

# Camera and soft studio lighting.
def aim(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

bpy.ops.object.camera_add(location=(9.2, -11.5, 9.4))
camera = bpy.context.object
camera.name = "Camera | isometric hero"
aim(camera, (0, 0, 1.55))
camera.data.type = "ORTHO"
camera.data.ortho_scale = 10.4
bpy.context.scene.camera = camera

def area_light(name, loc, power, size, color, target=(0,0,1)):
    bpy.ops.object.light_add(type="AREA", location=loc)
    light = bpy.context.object
    light.name = name
    light.data.energy = power
    light.data.shape = "DISK"
    light.data.size = size
    light.data.color = color
    aim(light, target)

area_light("Key | warm softbox", (1,-5,9), 1150, 7, (1.0,.76,.48))
area_light("Fill | mint rim", (-5,1,6), 950, 6, (.42,1.0,.78))
area_light("Back | amber", (4,5,7), 1250, 5, (1.0,.52,.22))

scene = bpy.context.scene
try:
    scene.render.engine = "BLENDER_EEVEE_NEXT"
except (TypeError, ValueError):
    scene.render.engine = "BLENDER_EEVEE"
eevee_settings = getattr(scene, "eevee", None)
if eevee_settings is not None and hasattr(eevee_settings, "taa_render_samples"):
    eevee_settings.taa_render_samples = 64
scene.render.resolution_x = 1200
scene.render.resolution_y = 1200
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(OUT / "restaurant-cube-render.png")
scene.world.color = (0.025, 0.03, 0.025)
scene.view_settings.view_transform = "AgX"
scene.render.film_transparent = True

# Select model meshes only for web export; keep camera and lights in the .blend project.
bpy.ops.object.select_all(action="DESELECT")
for obj in scene.objects:
    if obj.type == "MESH":
        obj.select_set(True)
bpy.context.view_layer.objects.active = next(obj for obj in scene.objects if obj.type == "MESH")
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "restaurant-cube.blend"))
bpy.ops.export_scene.gltf(filepath=str(OUT / "restaurant-cube.glb"), export_format="GLB", use_selection=True)
# Render an easy-to-review transparent PNG.
bpy.ops.object.select_all(action="DESELECT")
bpy.ops.render.render(write_still=True)
print("Created restaurant-cube.blend, restaurant-cube.glb, and restaurant-cube-render.png")
