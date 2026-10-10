# bpy-gen

Blender Python を使った作画・3D生成スキル。サーベイとは別のインテント。

## 提供ツール

- `doraemon_bpy.py` — ドラえもん簡易モデル＋カメラオートフィット生成
- `render.sh` — Windows Blender ヘッドレスレンダリング

## 使い方

```bash
./render.sh
```

出力先: `~/data-bpy-gen/renders/doraemon.png`

## 構成

- ソース: `~/.skills/bpy-gen/tools/`
- 出力: `~/data-bpy-gen/renders/`

## 今後

- LLM（Sakura）→ 自然言語指示 → bpy 自動生成
- レンダリングパイプラインで学習用画像を量産
- Colab GPU で PyTorch + bpy 連携実験
