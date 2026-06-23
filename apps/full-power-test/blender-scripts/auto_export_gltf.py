"""
Mira Corp. — Blender → glTF/FBX 自動エクスポートスクリプト
Meshy で作成した 3D モデルを Blender で処理して Godot 用にエクスポートする。

Usage (Blender コンテキスト内で実行):
  Scriptingタブ → このファイルを開いて Run Script
  または: blender --background model.blend --python auto_export_gltf.py -- output_dir

エクスポート形式: glTF 2.0 (.glb) + FBX (オプション)
"""
import bpy
import os
import sys
import datetime

# ─── Arguments ────────────────────────────────────────────────────────────────
argv = sys.argv
extra = argv[argv.index('--')+1:] if '--' in argv else []
OUTPUT_DIR   = extra[0] if extra else os.path.join(os.path.expanduser('~'), 'Desktop', 'mira_exports')
EXPORT_FBX   = '--fbx' in sys.argv
EXPORT_OBJ   = '--obj' in sys.argv
APPLY_MODS   = True   # Apply all modifiers before export

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Helpers ──────────────────────────────────────────────────────────────────
def log(msg): print(f'[MiraExport] {msg}')

def clean_name(name):
    return name.replace(' ', '_').replace('.', '_').lower()

# ─── Process each object ─────────────────────────────────────────────────────
log(f'出力先: {OUTPUT_DIR}')
log(f'オブジェクト数: {len(bpy.data.objects)}')

mesh_objects = [o for o in bpy.data.objects if o.type == 'MESH']
log(f'メッシュオブジェクト数: {len(mesh_objects)}')

for obj in mesh_objects:
    log(f'  処理中: {obj.name}')

    # Select only this object
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Apply modifiers
    if APPLY_MODS:
        for mod in obj.modifiers:
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
                log(f'    モディファイア適用: {mod.name}')
            except Exception as e:
                log(f'    モディファイア適用失敗: {mod.name} — {e}')

    base_name = clean_name(obj.name)
    now = datetime.datetime.now().strftime('%Y%m%d')

    # ─── Export glTF (.glb) ───────────────────────────────────────────────────
    glb_path = os.path.join(OUTPUT_DIR, f'{base_name}_{now}.glb')
    bpy.ops.export_scene.gltf(
        filepath      = glb_path,
        use_selection = True,
        export_format = 'GLB',
        export_texcoords = True,
        export_normals   = True,
        export_materials = 'EXPORT',
        export_yup       = True,        # Godot uses Y-up
        export_animations= True,
        export_skins     = True,
    )
    log(f'    → glTF: {glb_path}')

    # ─── Export FBX (for Unity / Unreal compatibility) ────────────────────────
    if EXPORT_FBX:
        fbx_path = os.path.join(OUTPUT_DIR, f'{base_name}_{now}.fbx')
        bpy.ops.export_scene.fbx(
            filepath         = fbx_path,
            use_selection    = True,
            apply_unit_scale = True,
            bake_space_transform = True,
            mesh_smooth_type = 'FACE',
            use_mesh_modifiers = True,
            use_armature_deform_only = True,
            add_leaf_bones   = False,
        )
        log(f'    → FBX: {fbx_path}')

    # ─── Export OBJ ──────────────────────────────────────────────────────────
    if EXPORT_OBJ:
        obj_path = os.path.join(OUTPUT_DIR, f'{base_name}_{now}.obj')
        bpy.ops.wm.obj_export(
            filepath     = obj_path,
            check_existing = False,
            export_selected_objects = True,
            export_uv    = True,
            export_normals = True,
            export_materials = True,
        )
        log(f'    → OBJ: {obj_path}')

log('')
log(f'エクスポート完了: {len(mesh_objects)}個のメッシュ → {OUTPUT_DIR}')
log('Godot でインポート: プロジェクト → インポート → glTF シーン')
