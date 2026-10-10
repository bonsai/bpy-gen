# bpy-gen

Blender Python を使った作画・3D生成スキル。サーベイとは別のインテント。

## 提供ツール

- `doraemon_bpy.py` — ドラえもん簡易モデルの生成

## 使い方

Blender の Scripting エディタで `tools/doraemon_bpy.py` を実行するか:

```bash
blender --python tools/doraemon_bpy.py
```

## 今後

- LLM（Sakura / NVIDIA）→ 自然言語指示 → bpy 自動生成
- レンダリングパイプラインで学習用画像を量産
- Colab GPU で PyTorch + bpy 連携実験
