# -*- coding: utf-8 -*-
"""生成候选照片的 contact sheet（缩略图拼版），供人工筛选。

用法: python scripts/make_sheets.py
输出: scripts/sheets/sheet-01.png ...（每张 12 图，4 列 x 3 行）
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
CAND = os.path.join(ROOT, "candidates.txt")
OUT_DIR = os.path.join(ROOT, "sheets")
os.makedirs(OUT_DIR, exist_ok=True)

COLS = 4
ROWS = 3
CELL_W = 400
CELL_H = 300  # 缩略 400x267 + 33 标签区
LABEL_H = 34

def load():
    paths = []
    with open(CAND, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                paths.append(line.replace("/d/", "D:/"))
    return paths

def main():
    paths = load()
    per_sheet = COLS * ROWS
    sheet_idx = 0
    for s in range(0, len(paths), per_sheet):
        batch = paths[s:s + per_sheet]
        sheet = Image.new("RGB", (COLS * CELL_W, ROWS * CELL_H), (250, 250, 250))
        draw = ImageDraw.Draw(sheet)
        for i, p in enumerate(batch):
            col, row = i % COLS, i // COLS
            x0, y0 = col * CELL_W, row * CELL_H
            try:
                im = Image.open(p)
                im.thumbnail((CELL_W - 8, CELL_H - LABEL_H - 8))
                bg = Image.new("RGB", (CELL_W - 8, CELL_H - LABEL_H - 8), (255, 255, 255))
                bg.paste(im, ((bg.width - im.width) // 2, (bg.height - im.height) // 2))
                sheet.paste(bg, (x0 + 4, y0 + 4))
                label = os.path.basename(p)
                draw.text((x0 + 8, y0 + CELL_H - LABEL_H + 4), f"[{s + i + 1}] {label[:38]}", fill=(30, 30, 30))
                draw.rectangle([x0, y0, x0 + CELL_W - 1, y0 + CELL_H - 1], outline=(200, 200, 200))
            except Exception as e:
                draw.text((x0 + 8, y0 + 8), f"ERROR {p}: {e}", fill=(200, 0, 0))
        out = os.path.join(OUT_DIR, f"sheet-{sheet_idx + 1:02d}.png")
        sheet.save(out)
        print("WROTE", out)
        sheet_idx += 1
    print("done", sheet_idx, "sheets for", len(paths), "candidates")

if __name__ == "__main__":
    main()
