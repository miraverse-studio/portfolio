"""
Mira Corp. — Blender Batch Render Script
Usage: blender --background scene.blend --python batch_render.py -- output_dir fps
実行例:
  blender --background my_scene.blend --python batch_render.py -- C:/renders 24
"""
import bpy
import os
import sys
import datetime

# ─── Parse CLI arguments ──────────────────────────────────────────────────────
argv = sys.argv
script_args_start = argv.index('--') + 1 if '--' in argv else len(argv)
extra_args = argv[script_args_start:]

OUTPUT_DIR = extra_args[0] if len(extra_args) > 0 else os.path.join(os.path.expanduser('~'), 'renders')
FPS        = int(extra_args[1]) if len(extra_args) > 1 else 24

os.makedirs(OUTPUT_DIR, exist_ok=True)

scene = bpy.context.scene
now   = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

# ─── Render settings ──────────────────────────────────────────────────────────
scene.render.fps          = FPS
scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode  = 'RGBA'
scene.render.film_transparent           = True   # transparent background
scene.render.resolution_percentage      = 100

# Output path with timestamp folder
out_folder = os.path.join(OUTPUT_DIR, f'render_{now}')
os.makedirs(out_folder, exist_ok=True)
scene.render.filepath = os.path.join(out_folder, 'frame_')

print(f'[Mira] 出力先: {out_folder}')
print(f'[Mira] フレーム範囲: {scene.frame_start} - {scene.frame_end}')
print(f'[Mira] FPS: {FPS} / 解像度: {scene.render.resolution_x}×{scene.render.resolution_y}')
print(f'[Mira] レンダリング開始...')

# ─── Render all frames ────────────────────────────────────────────────────────
start = datetime.datetime.now()
for frame in range(scene.frame_start, scene.frame_end + 1):
    scene.frame_set(frame)
    bpy.ops.render.render(write_still=True)
    pct = (frame - scene.frame_start) / max(1, scene.frame_end - scene.frame_start) * 100
    print(f'[Mira] フレーム {frame}/{scene.frame_end} ({pct:.0f}%)')

elapsed = (datetime.datetime.now() - start).total_seconds()
total   = scene.frame_end - scene.frame_start + 1
print()
print(f'[Mira] 完了: {total}フレーム / {elapsed:.1f}秒 ({elapsed/total:.2f}s/frame)')
print(f'[Mira] 出力: {out_folder}')
