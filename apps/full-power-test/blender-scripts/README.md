# Mira Blender スクリプト集

Meshy生成モデルの処理・エクスポート・ロゴ生成を自動化するBlender Pythonスクリプト。

## スクリプト一覧

| ファイル | 用途 |
|---------|------|
| `batch_render.py` | バックグラウンドでフレームを連番レンダリング |
| `auto_export_gltf.py` | 全メッシュをglTF(.glb) + FBXに自動エクスポート |
| `meshy_material_setup.py` | Meshyテクスチャを自動PBRマテリアルに設定 |
| `procedural_logo.py` | 「A」ロゴ + 王冠を3Dオブジェクトとして生成 |

## 実行方法

### Blender GUIで実行
1. Blender → Scripting タブ
2. Open → スクリプトファイルを開く
3. ▶ Run Script ボタン (または Alt+P)

### コマンドライン (CIパイプライン向け)

```powershell
# バッチレンダリング
blender --background scene.blend --python batch_render.py -- C:\renders 24

# glTFエクスポート
blender --background model.blend --python auto_export_gltf.py -- C:\exports

# FBXも同時にエクスポート
blender --background model.blend --python auto_export_gltf.py -- C:\exports --fbx
```

### Meshyモデルのフルパイプライン
```powershell
# 1. Meshyからダウンロード → フォルダに展開
# 2. Blenderでインポート (File → Import → FBX/OBJ/glTF)
# 3. マテリアルを自動設定
blender model.blend --python meshy_material_setup.py
# 4. Godot用にglTFエクスポート
blender model.blend --python auto_export_gltf.py -- C:\godot_project\assets
```

## 技術メモ

- **bpy**: Blender Python API。Blender内蔵、別途インストール不要
- **bmesh**: メッシュ編集API。頂点/辺/面の直接操作
- **glTF 2.0**: Godot Engine の標準3Dフォーマット (`.glb` = バイナリ)
- **Cycles vs EEVEE**: レンダリング品質(Cycles) vs 速度(EEVEE)のトレードオフ
- テクスチャは `Non-Color` スペースで読み込む必要あり (Normal/Roughness/Metallic)
