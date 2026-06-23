"""
Mira Corp. — Meshy 3Dモデル マテリアルセットアップスクリプト
Meshyからダウンロードしたモデルのテクスチャを自動でBlenderのPBRマテリアルに割り当てる。

Usage: Blenderの Scripting タブで実行。
前提: モデルをBlenderにインポート済み。テクスチャが同じフォルダにあること。
対応テクスチャ名:
  *_basecolor.png / *_albedo.png / *_diffuse.png
  *_normal.png / *_normalmap.png
  *_roughness.png
  *_metallic.png / *_metalness.png
  *_ao.png / *_occlusion.png / *_ambient.png
  *_emission.png / *_emissive.png
"""
import bpy
import os
import re

def log(msg): print(f'[MeshySetup] {msg}')

def find_texture(folder, patterns):
    """Find the first file in folder matching any of the glob-like patterns."""
    for f in os.listdir(folder):
        name_lower = f.lower()
        for pat in patterns:
            if re.search(pat, name_lower):
                return os.path.join(folder, f)
    return None

def load_image(path):
    if path is None: return None
    # Check if already loaded
    for img in bpy.data.images:
        if img.filepath == path: return img
    return bpy.data.images.load(path)

def setup_pbr_material(obj, texture_dir):
    """Set up a PBR material on obj using textures from texture_dir."""
    if not obj.data.materials:
        mat = bpy.data.materials.new(name=obj.name + '_mat')
        obj.data.materials.append(mat)
    else:
        mat = obj.data.materials[0]

    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    nodes.clear()

    # Output
    out_node = nodes.new('ShaderNodeOutputMaterial')
    out_node.location = (600, 0)

    # Principled BSDF
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

    def add_texture_node(img, label, x, y, is_non_color=False):
        node = nodes.new('ShaderNodeTexImage')
        node.label = label
        node.location = (x, y)
        if img:
            node.image = img
            if is_non_color:
                node.image.colorspace_settings.name = 'Non-Color'
        return node

    # UV Map node
    uv_node = nodes.new('ShaderNodeTexCoord')
    uv_node.location = (-700, 0)

    Y_OFFSET = 250

    # Base Color
    bc_path = find_texture(texture_dir, [r'base.?color', r'albedo', r'diffuse', r'color'])
    bc_img  = load_image(bc_path)
    bc_node = add_texture_node(bc_img, 'Base Color', -300, 200)
    if bc_img:
        links.new(bc_node.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(uv_node.outputs['UV'], bc_node.inputs['Vector'])
        log(f'  ✓ Base Color: {os.path.basename(bc_path)}')
    else:
        bsdf.inputs['Base Color'].default_value = (0.8, 0.8, 0.8, 1.0)
        log('  ⚠ Base Color: テクスチャ未発見 → デフォルト白')

    # Normal Map
    nm_path = find_texture(texture_dir, [r'normal', r'normalmap'])
    nm_img  = load_image(nm_path)
    if nm_img:
        nm_node   = add_texture_node(nm_img, 'Normal', -300, 200-Y_OFFSET, is_non_color=True)
        nmap_node = nodes.new('ShaderNodeNormalMap')
        nmap_node.location = (-50, 200-Y_OFFSET)
        links.new(uv_node.outputs['UV'], nm_node.inputs['Vector'])
        links.new(nm_node.outputs['Color'], nmap_node.inputs['Color'])
        links.new(nmap_node.outputs['Normal'], bsdf.inputs['Normal'])
        log(f'  ✓ Normal Map: {os.path.basename(nm_path)}')

    # Roughness
    rg_path = find_texture(texture_dir, [r'roughness', r'rough'])
    rg_img  = load_image(rg_path)
    if rg_img:
        rg_node = add_texture_node(rg_img, 'Roughness', -300, 200-Y_OFFSET*2, is_non_color=True)
        links.new(uv_node.outputs['UV'], rg_node.inputs['Vector'])
        links.new(rg_node.outputs['Color'], bsdf.inputs['Roughness'])
        log(f'  ✓ Roughness: {os.path.basename(rg_path)}')
    else:
        bsdf.inputs['Roughness'].default_value = 0.5

    # Metallic
    mt_path = find_texture(texture_dir, [r'metallic', r'metalness', r'metal'])
    mt_img  = load_image(mt_path)
    if mt_img:
        mt_node = add_texture_node(mt_img, 'Metallic', -300, 200-Y_OFFSET*3, is_non_color=True)
        links.new(uv_node.outputs['UV'], mt_node.inputs['Vector'])
        links.new(mt_node.outputs['Color'], bsdf.inputs['Metallic'])
        log(f'  ✓ Metallic: {os.path.basename(mt_path)}')

    # AO (Ambient Occlusion) — mix with base color
    ao_path = find_texture(texture_dir, [r'\bao\b', r'occlusion', r'ambient'])
    ao_img  = load_image(ao_path)
    if ao_img and bc_img:
        ao_node = add_texture_node(ao_img, 'AO', -500, 300, is_non_color=True)
        mix_node = nodes.new('ShaderNodeMixRGB')
        mix_node.blend_type = 'MULTIPLY'
        mix_node.inputs['Fac'].default_value = 0.8
        mix_node.location = (-100, 300)
        links.new(uv_node.outputs['UV'], ao_node.inputs['Vector'])
        links.new(bc_node.outputs['Color'], mix_node.inputs['Color1'])
        links.new(ao_node.outputs['Color'], mix_node.inputs['Color2'])
        links.new(mix_node.outputs['Color'], bsdf.inputs['Base Color'])
        log(f'  ✓ AO: {os.path.basename(ao_path)}')

    # Emission
    em_path = find_texture(texture_dir, [r'emis', r'emission'])
    em_img  = load_image(em_path)
    if em_img:
        em_node = add_texture_node(em_img, 'Emission', -300, 200-Y_OFFSET*4)
        links.new(uv_node.outputs['UV'], em_node.inputs['Vector'])
        links.new(em_node.outputs['Color'], bsdf.inputs['Emission Color'])
        bsdf.inputs['Emission Strength'].default_value = 1.0
        log(f'  ✓ Emission: {os.path.basename(em_path)}')

    return mat

# ─── Main ─────────────────────────────────────────────────────────────────────
log('Meshy マテリアルセットアップ開始')

selected = [o for o in bpy.context.selected_objects if o.type == 'MESH']
if not selected:
    selected = [o for o in bpy.data.objects if o.type == 'MESH']

for obj in selected:
    log(f'\nオブジェクト: {obj.name}')

    # Look for textures next to the blend file, or in the object's material directory
    blend_dir = os.path.dirname(bpy.data.filepath) if bpy.data.filepath else os.getcwd()
    tex_dir   = blend_dir

    # Check for a subfolder named after the object
    obj_subfolder = os.path.join(blend_dir, obj.name)
    if os.path.isdir(obj_subfolder): tex_dir = obj_subfolder

    log(f'  テクスチャ検索先: {tex_dir}')
    setup_pbr_material(obj, tex_dir)

log('\n全マテリアルセットアップ完了！')
log('次のステップ: Blender Cycles / EEVEE でレンダリング、またはglTFでエクスポート')
