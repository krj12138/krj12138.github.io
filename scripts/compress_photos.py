# -*- coding: utf-8 -*-
"""按 scripts/photo_config.json 压缩精选照片为 WebP，并生成 src/photos-data.js。

用法: py scripts/compress_photos.py
输出: public/photos/*.webp（1600 长边，质量 80）+ src/photos-data.js
"""
import json
import os
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
CFG = json.load(open(os.path.join(ROOT, "photo_config.json"), encoding="utf-8"))
OUT_DIR = os.path.join(PROJ, "public", "photos")
os.makedirs(OUT_DIR, exist_ok=True)

MAX_SIDE = 1600
HERO_SIDE = 1500


def to_win(p):
    return p.replace("/d/", "D:/")


def compress(src, out_name, max_side):
    im = Image.open(to_win(src))
    im = ImageOps.exif_transpose(im)
    if im.mode != "RGB":
        im = im.convert("RGB")
    im.thumbnail((max_side, max_side), Image.LANCZOS)
    out = os.path.join(OUT_DIR, out_name)
    im.save(out, "WEBP", quality=80, method=6)
    size_kb = os.path.getsize(out) / 1024
    print(f"{out_name:16s} {im.width}x{im.height}  {size_kb:.0f} KB")
    return size_kb


def main():
    total = 0
    h = CFG["hero"]
    print("== HERO ==")
    total += compress(h["src"], h["file"], HERO_SIDE)

    data = []
    for g in CFG["groups"]:
        photos = []
        print(f"== GROUP {g['no']} : {g['title']} ==")
        for p in g["photos"]:
            total += compress(p["src"], p["file"], MAX_SIDE)
            photos.append({
                "src": "/photos/" + p["file"],
                "title": p["title"],
                "meta": p["meta"],
                "size": p.get("size", "ph-item--sm"),
            })
        data.append({
            "no": g["no"],
            "title": g["title"],
            "en": g["en"],
            "note": g.get("note", ""),
            "photos": photos,
        })

    js = (
        "// 本文件由 scripts/compress_photos.py 自动生成，请勿手改。\n"
        "// 图片数据定义在 scripts/photo_config.json。\n"
        "export const photoGroups = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n"
    )
    js_path = os.path.join(PROJ, "src", "photos-data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js)
    print("WROTE", js_path)
    print(f"TOTAL {len(CFG['groups'])} groups, {total} images")


if __name__ == "__main__":
    main()
