"""
Mira Corp. — Blender Procedural ロゴ生成スクリプト
「あ」の文字やAロゴを3Dオブジェクトとして生成する。
Meshyではできない、完全スクリプト制御の3Dオブジェクト生成。

Usage: Blenderの Scripting タブで実行。
"""
import bpy
import bmesh
import math

def log(msg): print(f'[MiraLogo] {msg}')

def clear_scene():
    """Remove all mesh objects."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes:    bpy.data.meshes.remove(block)
    for block in bpy.data.materials: bpy.data.materials.remove(block)
    log('シーンをクリア')

def create_material(name, color, metallic=0.0, roughness=0.5, emission=None):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value   = (*color, 1.0)
    bsdf.inputs['Metallic'].default_value     = metallic
    bsdf.inputs['Roughness'].default_value    = roughness
    if emission:
        bsdf.inputs['Emission Color'].default_value    = (*emission, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 2.0
    return mat

def add_crown(location=(0,0,2.5), scale=1.0):
    """Create a 3-point crown shape."""
    bm = bmesh.new()
    verts = []
    # Crown base rectangle
    base = [(-1,0,0),(1,0,0),(1,0,0.3),(-1,0,0.3)]
    for v in base: verts.append(bm.verts.new([v[0]*scale, v[1]*scale, v[2]*scale]))
    bm.faces.new(verts)

    # Three crown points
    tips = [(-0.7,0,1), (0,0,1.3), (0.7,0,1)]
    for tip_x, tip_y, tip_z in tips:
        tl = bm.verts.new([tip_x*scale, 0, (tip_z-0.3)*scale])
        tr = bm.verts.new([(tip_x+0.2)*scale, 0, (tip_z-0.3)*scale])
        tt = bm.verts.new([((tip_x+0.1)*scale), 0, tip_z*scale])
        bm.faces.new([tl, tr, tt])

    bm.normal_update()
    me = bpy.data.meshes.new('CrownMesh')
    bm.to_mesh(me)
    bm.free()
    obj = bpy.data.objects.new('Crown', me)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_add(type='SOLIDIFY')
    obj.modifiers['Solidify'].thickness = 0.1 * scale
    return obj

def create_letter_A(extrude_depth=0.3):
    """Create the letter A using a bezier curve then convert to mesh."""
    # Use a text object (simplest reliable method)
    bpy.ops.object.text_add(location=(0, 0, 0))
    text_obj = bpy.context.active_object
    text_obj.data.body = 'A'
    text_obj.data.extrude = extrude_depth
    text_obj.data.bevel_depth = 0.02
    text_obj.data.align_x = 'CENTER'
    text_obj.data.size = 2.0

    # Convert to mesh
    bpy.ops.object.convert(target='MESH')
    text_obj.name = 'Logo_A'
    return text_obj

# ─── Main ─────────────────────────────────────────────────────────────────────
clear_scene()
log('Mira Corp. ロゴ 3D生成開始')

# Create the A
log('文字 A を生成中...')
letter = create_letter_A(extrude_depth=0.4)
letter.location = (0, 0, 0)

# Add subdivision surface for smoothness
sub_mod = letter.modifiers.new('Subdivision', 'SUBSURF')
sub_mod.levels = 2
sub_mod.render_levels = 3

# Purple gradient material
mat_a = create_material('Mira_Purple', (0.49, 0.23, 0.93), metallic=0.3, roughness=0.2,
                        emission=(0.49, 0.23, 0.93))
letter.data.materials.append(mat_a)
log(f'  ✓ マテリアル: パープル (metallic=0.3)')

# Crown on top
log('王冠を生成中...')
crown = add_crown(location=(0, 0, 2.2), scale=0.8)
mat_gold = create_material('Gold', (1.0, 0.77, 0.0), metallic=0.9, roughness=0.1)
crown.data.materials.append(mat_gold)
log(f'  ✓ マテリアル: ゴールド (metallic=0.9)')

# Ground plane with reflection
bpy.ops.mesh.primitive_plane_add(size=10, location=(0, 0, -0.5))
ground = bpy.context.active_object
ground.name = 'Ground'
mat_ground = create_material('Ground', (0.04, 0.04, 0.08), metallic=0.0, roughness=0.05)
ground.data.materials.append(mat_ground)

# ─── Lighting ─────────────────────────────────────────────────────────────────
# Key light
bpy.ops.object.light_add(type='AREA', location=(3, -3, 5))
key = bpy.context.active_object
key.data.energy = 500
key.data.size = 3
key.data.color = (1.0, 0.95, 0.9)

# Fill light (purple tint)
bpy.ops.object.light_add(type='AREA', location=(-3, 3, 3))
fill = bpy.context.active_object
fill.data.energy = 200
fill.data.color = (0.6, 0.4, 1.0)

# Rim light (gold)
bpy.ops.object.light_add(type='SPOT', location=(0, 5, 3))
rim = bpy.context.active_object
rim.data.energy = 1000
rim.data.color = (1.0, 0.8, 0.0)
rim.data.spot_size = math.radians(45)

# ─── Camera ───────────────────────────────────────────────────────────────────
bpy.ops.object.camera_add(location=(0, -6, 2.5))
cam = bpy.context.active_object
cam.rotation_euler = (math.radians(80), 0, 0)
bpy.context.scene.camera = cam

# ─── World / HDRI (procedural sky) ───────────────────────────────────────────
world = bpy.context.scene.world
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs['Color'].default_value = (0.02, 0.02, 0.08, 1.0)
    bg_node.inputs['Strength'].default_value = 0.5

# ─── Render settings ─────────────────────────────────────────────────────────
scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.samples = 128
scene.render.resolution_x = 1920
scene.render.resolution_y = 1080
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = '//mira_logo_render.png'

log('\nロゴ生成完了！')
log('レンダリング: F12 または bpy.ops.render.render(write_still=True)')
log(f'出力: {scene.render.filepath}')
