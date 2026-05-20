#!/usr/bin/env python3
"""
Generate a WeChat Official Account cover image for the 豆豆三部曲 article.
Output: 900x500 PNG (standard WeChat cover ratio).
Design: Dark literary aesthetic with warm orange/gold accents.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path


def find_chinese_font():
    """Try to find an available Chinese font on Windows, prefer serif/kai for literary feel."""
    candidates = [
        "C:/Windows/Fonts/STKAITI.TTF",       # 华文楷体 (prefer for literary)
        "C:/Windows/Fonts/STFANGSO.TTF",      # 华文仿宋
        "C:/Windows/Fonts/STSONG.TTF",        # 华文宋体
        "C:/Windows/Fonts/STZHONGS.TTF",      # 华文中宋
        "C:/Windows/Fonts/simkai.ttf",        # 楷体
        "C:/Windows/Fonts/FANGSONG.TTF",      # 仿宋
        "C:/Windows/Fonts/simsun.ttc",        # 宋体
        "C:/Windows/Fonts/simhei.ttf",        # 黑体
        "C:/Windows/Fonts/msyh.ttc",          # 微软雅黑
        "C:/Windows/Fonts/msyhbd.ttc",        # 微软雅黑粗体
    ]
    found = []
    for path in candidates:
        if os.path.exists(path):
            found.append(path)
    return found


def create_cover(output_path: str):
    """Create a professionally designed cover image."""
    width, height = 900, 500

    # ── Color palette ──
    bg_darkest = (22, 23, 32)
    bg_dark = (32, 34, 46)
    orange = (255, 149, 0)          # warm orange, matches article accent
    orange_dim = (255, 149, 0, 80)
    orange_faint = (255, 149, 0, 30)
    white_primary = (238, 238, 240)
    white_dim = (170, 170, 180)
    white_faint = (130, 130, 145)

    # ── Build image with gradient ──
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Vertical gradient from slightly lighter at top to darker at bottom
    for y in range(height):
        ratio = y / height
        r = int(bg_dark[0] + (bg_darkest[0] - bg_dark[0]) * ratio)
        g = int(bg_dark[1] + (bg_darkest[1] - bg_dark[1]) * ratio)
        b = int(bg_dark[2] + (bg_darkest[2] - bg_dark[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # ── Load fonts ──
    font_paths = find_chinese_font()
    if not font_paths:
        print("[警告] 未找到中文字体")
        return

    # Use first available serif/kai font for title, second for body
    font_path_title = font_paths[0]
    font_path_body = font_paths[0] if len(font_paths) < 2 else font_paths[1]

    print(f"[i] 标题字体: {os.path.basename(font_path_title)}")
    print(f"[i] 正文字体: {os.path.basename(font_path_body)}")

    font_main = ImageFont.truetype(font_path_title, 52)       # main title line
    font_subtitle = ImageFont.truetype(font_path_body, 28)     # subtitle
    font_label = ImageFont.truetype(font_path_body, 18)        # small labels
    font_tag = ImageFont.truetype(font_path_body, 16)          # tagline
    font_concept = ImageFont.truetype(font_path_body, 17)      # concept text

    # ── Helper: draw right-aligned text (PIL 10+) ──
    def text_size(font, text):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def draw_center(text, y, font, fill):
        tw, _ = text_size(font, text)
        x = (width - tw) // 2
        draw.text((x, y), text, fill=fill, font=font)

    def draw_right(text, y, font, fill):
        tw, _ = text_size(font, text)
        x = width - 60 - tw
        draw.text((x, y), text, fill=fill, font=font)

    # ── Design elements ──

    # Top thin accent line
    draw.rectangle([(60, 0), (width - 60, 2)], fill=orange)

    # Three vertical book-spine elements on the far left (subtle)
    spine_x = 90
    spine_width = 4
    spine_heights = [280, 320, 260]
    spine_starts = [130, 100, 140]
    spine_colors = [orange + (90,), orange + (60,), orange + (40,)]
    for sx, sh, ss, sc in zip(
        [spine_x, spine_x + 18, spine_x + 36],
        spine_heights,
        spine_starts,
        spine_colors,
    ):
        draw.rectangle([(sx, ss), (sx + spine_width, ss + sh)], fill=sc)

    # Three overlapping translucent book rectangles (right side, symbolic)
    book_data = [
        (600, 100, 840, 380, orange + (18,), orange + (45,)),
        (625, 85, 855, 370, orange + (12,), orange + (30,)),
        (650, 70, 870, 360, orange + (8,), orange + (22,)),
    ]
    for x1, y1, x2, y2, fill_c, outline_c in book_data:
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        od.rounded_rectangle(
            [(x1, y1), (x2, y2)], radius=6, fill=fill_c, outline=outline_c, width=1
        )
        img = Image.alpha_composite(img, overlay)
        draw = ImageDraw.Draw(img)

    # Horizontal decorative line: subtle division
    for i in range(1, 4):
        y_pos = 295 + i * 8
        alpha = 100 - i * 25
        draw.line(
            [(160, y_pos), (550, y_pos)], fill=orange + (alpha,), width=1
        )

    # ── Text content ──

    # Top-left label
    draw.text((140, 80), "深度阅读", fill=orange, font=font_tag)

    # Main title - first line
    line1 = "读完豆豆三部曲"
    draw.text((140, 130), line1, fill=white_primary, font=font_main)

    # Main title - second line
    line2 = "才明白"
    draw.text((140, 195), line2, fill=white_dim, font=font_subtitle)

    # Highlighted line - the thesis statement
    highlight = "大多数人一辈子都在"
    highlight2 = "走别人的路"
    th = text_size(font_subtitle, highlight)[1]
    draw.text((140, 245), highlight, fill=white_faint, font=font_subtitle)
    tw_h2, _ = text_size(font_main, highlight2)
    draw.text((140, 245 + th + 4), highlight2, fill=orange, font=font_main)

    # Bottom section ---
    bottom_y = 410

    # Three concept labels in a row
    concepts = [
        ("《背叛》", "不能做什么"),
        ("《天幕红尘》", "怎么做"),
        ("《遥远的救世主》", "该做什么"),
    ]
    # But actually, the logical order is 背叛→救世主→天幕红尘
    concepts_ordered = [
        ("《背叛》", "何为禁忌"),
        ("《遥远的救世主》", "何为方向"),
        ("《天幕红尘》", "何为方法"),
    ]

    start_x = 140
    gap = 170
    for i, (book, meaning) in enumerate(concepts_ordered):
        cx = start_x + i * gap
        # Book title in orange
        draw.text((cx, bottom_y), book, fill=orange, font=font_concept)
        # Meaning in white
        draw.text((cx + 3, bottom_y + 24), meaning, fill=white_faint, font=font_tag)

    # Right side tagline
    tagline = "实事求是  ·  见路不走"
    draw_right(tagline, 460, font_tag, orange_dim[:3] + (150,))

    # Bottom fine line
    draw.rectangle([(60, height - 2), (width - 60, height - 1)], fill=orange + (60,))

    # ── Composite to flat RGB and save ──
    final = Image.new("RGB", (width, height), bg_darkest)
    final.paste(img, (0, 0), img)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    final.save(output_path, "PNG", quality=95)
    print(f"[√] 封面图已生成: {output_path} ({width}x{height}px)")


if __name__ == "__main__":
    output = Path(__file__).resolve().parent.parent / "阅读" / "cover.jpg"
    create_cover(str(output))
