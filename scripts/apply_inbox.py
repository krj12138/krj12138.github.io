# -*- coding: utf-8 -*-
"""替换网站照片：把 photos-inbox/ 里的新照片压缩并覆盖 public/photos/ 下同名的 WebP。

用法: py scripts/apply_inbox.py [--dry-run]
规则: 投放箱内照片的文件名（不含扩展名）必须与 public/photos/ 下某个 .webp 同名。
      例如 street-01.jpg 会替换 street-01.webp（标题、图注、分组不变）。
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(ROOT)
INBOX = os.path.join(PROJ, "photos-inbox")
OUT_DIR = os.path.join(PROJ, "public", "photos")

from PIL import Image, ImageOps  # noqa: E402

MAX_SIDE = 1600
DRY = "--dry-run" in sys.argv


def main():
    existing = {}
    for name in os.listdir(OUT_DIR):
        if name.endswith(".webp"):
            existing[name[:-5].lower()] = name

    uploads = []
    for name in os.listdir(INBOX):
        ext = os.path.splitext(name)[1].lower()
        if ext in (".jpg", ".jpeg", ".png", ".webp"):
            uploads.append(name)

    if not uploads:
        print("photos-inbox/ 里没有新照片可替换（支持 .jpg/.png/.webp）。")
        return

    ok, missed = [], []
    for name in sorted(uploads):
        stem = os.path.splitext(name)[0].lower()
        target = existing.get(stem)
        if not target:
            missed.append(name)
            continue
        src = os.path.join(INBOX, name)
        if DRY:
            print(f"[dry-run] {name} -> 将替换 {target}")
            ok.append(name)
            continue
        im = Image.open(src)
        im = ImageOps.exif_transpose(im)
        if im.mode != "RGB":
            im = im.convert("RGB")
        im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
        out = os.path.join(OUT_DIR, target)
        im.save(out, "WEBP", quality=80, method=6)
        size_kb = os.path.getsize(out) / 1024
        print(f"REPLACED {target:16s} {im.width}x{im.height}  {size_kb:.0f} KB")
        ok.append(name)

    if missed:
        print("\n未匹配上的照片（请改名为现有照片名，见 photos-inbox/README.txt）：")
        for m in missed:
            print("  -", m)

    print(f"\n完成：{len(ok)} 张{'（预演）' if DRY else ''}，未匹配 {len(missed)} 张。")
    if not DRY:
        print("若 npm dev 正在运行，浏览器刷新即可看到新照片。")


if __name__ == "__main__":
    main()
