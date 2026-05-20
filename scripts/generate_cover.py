#!/usr/bin/env python3
"""
Parameterized WeChat cover image generator. 900x500 PNG.
Supports multiple themes with command-line customization.

Usage:
  python generate_cover.py --theme zen --title "《心经》260字" --highlight "放下，即是拥有"
  python generate_cover.py --theme literary --title "豆豆三部曲" --highlight "走自己的路"
"""
import argparse, os, math, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path


# ── Theme definitions ──────────────────────────────────────────
THEMES = {
    "zen": {
        "name": "禅意",
        "accent": (198, 160, 70),        # warm gold
        "accent_light": (218, 185, 100),
        "accent_dim": (160, 130, 60),
        "bg_top": (32, 30, 40),          # ink mid
        "bg_bot": (22, 21, 28),          # ink deep
        "text_primary": (235, 230, 218), # rice paper white
        "text_dim": (180, 175, 165),
        "text_faint": (140, 136, 130),
        "features": ["enso_large", "enso_small", "ink_wash", "scroll_lines", "noise"],
    },
    "literary": {
        "name": "文学",
        "accent": (255, 149, 0),         # warm orange
        "accent_light": (255, 170, 40),
        "accent_dim": (220, 120, 0),
        "bg_top": (32, 34, 46),          # dark blue-gray
        "bg_bot": (22, 23, 32),
        "text_primary": (238, 238, 240),
        "text_dim": (170, 170, 180),
        "text_faint": (130, 130, 145),
        "features": ["book_spines", "translucent_rects", "horiz_lines"],
    },
    "clean": {
        "name": "极简",
        "accent": (255, 255, 255),
        "accent_light": (200, 200, 200),
        "accent_dim": (120, 120, 120),
        "bg_top": (10, 10, 10),
        "bg_bot": (5, 5, 5),
        "text_primary": (245, 245, 245),
        "text_dim": (160, 160, 160),
        "text_faint": (100, 100, 100),
        "features": ["geometric_lines"],
    },
}


# ── Font discovery ─────────────────────────────────────────────
def find_fonts():
    candidates = [
        "C:/Windows/Fonts/STKAITI.TTF",
        "C:/Windows/Fonts/STFANGSO.TTF",
        "C:/Windows/Fonts/STZHONGS.TTF",
        "C:/Windows/Fonts/simkai.ttf",
        "C:/Windows/Fonts/STSONG.TTF",
        "C:/Windows/Fonts/FANGSONG.TTF",
        "C:/Windows/Fonts/simsun.ttc",
    ]
    found = [p for p in candidates if os.path.exists(p)]
    if not found:
        print("[ERROR] No Chinese fonts found")
        sys.exit(1)
    return found


# ── Drawing helpers ────────────────────────────────────────────
class Cover:
    def __init__(self, theme_name: str):
        self.t = THEMES[theme_name]
        self.W, self.H = 900, 500
        self.img = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.img)

    def text_size(self, font, text):
        bbox = self.draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    def draw_center(self, text, y, font, fill):
        tw, _ = self.text_size(font, text)
        self.draw.text(((self.W - tw) // 2, y), text, fill=fill, font=font)

    def draw_right(self, text, y, font, fill):
        tw, _ = self.text_size(font, text)
        self.draw.text((self.W - 60 - tw, y), text, fill=fill, font=font)

    # ── Background ──────────────────────────────────────────────
    def bg_gradient(self):
        bg_top, bg_bot = self.t["bg_top"], self.t["bg_bot"]
        for y in range(self.H):
            ratio = y / self.H
            curve = ratio ** 1.3
            r = int(bg_top[0] + (bg_bot[0] - bg_top[0]) * curve)
            g = int(bg_top[1] + (bg_bot[1] - bg_top[1]) * curve)
            b = int(bg_top[2] + (bg_bot[2] - bg_top[2]) * curve)
            self.draw.line([(0, y), (self.W, y)], fill=(r, g, b))

    def bg_noise(self):
        random.seed(42)
        for _ in range(3000):
            x, y = random.randint(0, self.W - 1), random.randint(0, self.H - 1)
            alpha = random.randint(1, 3)
            v = self.t["bg_top"][0] + random.randint(-3, 2)
            self.draw.point((x, y), fill=(v, v, v + 2, alpha))

    def bg_ink_wash(self):
        overlay = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        idraw = ImageDraw.Draw(overlay)
        spots = [
            (680, 160, 280, 260, (50, 48, 60, 15)),
            (720, 380, 200, 180, (45, 43, 55, 12)),
            (550, 420, 340, 140, (40, 38, 50, 10)),
            (100, 300, 180, 220, (48, 46, 58, 8)),
        ]
        for cx, cy, rw, rh, color in spots:
            idraw.ellipse([(cx - rw // 2, cy - rh // 2), (cx + rw // 2, cy + rh // 2)], fill=color)
        overlay = overlay.filter(ImageFilter.GaussianBlur(radius=30))
        self.img = Image.alpha_composite(self.img, overlay)
        self.draw = ImageDraw.Draw(self.img)

    # ── Zen features ────────────────────────────────────────────
    def enso_large(self):
        overlay = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        ed = ImageDraw.Draw(overlay)
        gold = self.t["accent"]
        cx, cy, r = 670, 250, 155
        for angle in range(195, 355, 2):
            rad = math.radians(angle)
            wr = r + random.uniform(-1.5, 1.5)
            px, py = cx + wr * math.cos(rad), cy + wr * math.sin(rad)
            progress = (angle - 195) / 160
            if progress < 0.15:
                a = int(40 + progress * 200)
            elif progress > 0.85:
                a = int(40 + (1 - progress) * 200)
            else:
                a = int(55 + 15 * math.sin(progress * math.pi))
            a = min(a, 100)
            thickness = 3.5 + 1.5 * math.sin(progress * 3.5)
            for t in range(int(thickness)):
                offset_r = wr + t * 0.6
                tx, ty = cx + offset_r * math.cos(rad), cy + offset_r * math.sin(rad)
                ed.point((int(tx), int(ty)), fill=gold + (a,))
        # double-stroke
        for angle in range(200, 350, 3):
            rad = math.radians(angle)
            wr = r + random.uniform(-1, 1) - 3
            px, py = cx + wr * math.cos(rad), cy + wr * math.sin(rad)
            progress = (angle - 200) / 150
            a = int(10 + 10 * math.sin(progress * math.pi))
            ed.point((int(px), int(py)), fill=(220, 200, 150, a))
        self.img = Image.alpha_composite(self.img, overlay)
        self.draw = ImageDraw.Draw(self.img)

    def enso_small(self):
        overlay = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        ed = ImageDraw.Draw(overlay)
        gold = self.t["accent"]
        cx, cy, r = 100, 170, 38
        for angle in range(0, 360, 3):
            rad = math.radians(angle)
            wr = r + random.uniform(-0.8, 0.8)
            px, py = cx + wr * math.cos(rad), cy + wr * math.sin(rad)
            a = 15 + int(10 * math.sin(angle / 40))
            for t in range(2):
                ed.point((int(px + t), int(py)), fill=gold + (a,))
        self.img = Image.alpha_composite(self.img, overlay)
        self.draw = ImageDraw.Draw(self.img)

    def scroll_lines(self):
        gold = self.t["accent"]
        for i in range(3):
            x = 55 + i * 12
            a = 25 - i * 8
            self.draw.line([(x, 40), (x, self.H - 40)], fill=gold + (a,), width=1)

    # ── Literary features ───────────────────────────────────────
    def book_spines(self):
        gold = self.t["accent"]
        spine_x = 90
        heights = [280, 320, 260]
        starts = [130, 100, 140]
        alphas = [90, 60, 40]
        for i, (h, s, a) in enumerate(zip(heights, starts, alphas)):
            x = spine_x + i * 18
            self.draw.rectangle([(x, s), (x + 4, s + h)], fill=gold + (a,))

    def translucent_rects(self):
        gold = self.t["accent"]
        books = [
            (600, 100, 840, 380, 18, 45),
            (625, 85, 855, 370, 12, 30),
            (650, 70, 870, 360, 8, 22),
        ]
        for x1, y1, x2, y2, fa, oa in books:
            overlay = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
            od = ImageDraw.Draw(overlay)
            od.rounded_rectangle([(x1, y1), (x2, y2)], radius=6, fill=gold + (fa,), outline=gold + (oa,), width=1)
            self.img = Image.alpha_composite(self.img, overlay)
            self.draw = ImageDraw.Draw(self.img)

    def horiz_lines(self):
        gold = self.t["accent"]
        for i in range(1, 4):
            y = 295 + i * 8
            a = 100 - i * 25
            self.draw.line([(160, y), (550, y)], fill=gold + (a,), width=1)

    # ── Clean features ──────────────────────────────────────────
    def geometric_lines(self):
        white = self.t["accent"]
        # Top accent
        self.draw.rectangle([(80, 0), (self.W - 80, 2)], fill=white + (80,))
        self.draw.rectangle([(80, self.H - 2), (self.W - 80, self.H)], fill=white + (40,))

    # ── Common elements ─────────────────────────────────────────
    def edge_lines(self):
        gold = self.t["accent"]
        self.draw.rectangle([(55, 0), (self.W - 55, 1)], fill=gold + (35,))
        self.draw.rectangle([(55, self.H - 1), (self.W - 55, self.H)], fill=gold + (25,))

    def divider_line(self, y_start=335):
        gold = self.t["accent"]
        for i in range(3):
            y = y_start + i * 4
            a = 35 - i * 10
            self.draw.line([(160, y), (520, y)], fill=gold + (a,), width=1)

    # ── Typography ──────────────────────────────────────────────
    def render_text(self, title, subtitle, highlight, tags, source):
        fonts = find_fonts()
        title_font_path = fonts[0]
        body_font_path = fonts[1] if len(fonts) > 1 else fonts[0]

        print(f"[fonts] title: {os.path.basename(title_font_path)} | body: {os.path.basename(body_font_path)}")

        font_title   = ImageFont.truetype(title_font_path, 52)
        font_sub     = ImageFont.truetype(body_font_path, 24)
        font_small   = ImageFont.truetype(body_font_path, 15)
        font_tag     = ImageFont.truetype(body_font_path, 14)
        font_bottom  = ImageFont.truetype(body_font_path, 18)

        gold = self.t["accent"]
        gold_dim = self.t["accent_dim"]
        text_p = self.t["text_primary"]
        text_d = self.t["text_dim"]
        text_f = self.t["text_faint"]

        # Top label
        self.draw.text((145, 60), "深 度 阅 读", fill=gold + (180,), font=font_small)

        # Source
        if source:
            self.draw.text((145, 85), source, fill=gold_dim + (100,), font=font_tag)

        # Title
        self.draw.text((145, 125), title, fill=text_p, font=font_title)

        # Subtitle
        if subtitle:
            self.draw.text((145, 188), subtitle, fill=text_d, font=font_sub)

        # Highlight
        if highlight:
            parts = highlight.split("，") if "，" in highlight else [highlight, ""]
            h1 = parts[0] + ("，" if len(parts) > 1 and "，" in highlight else "")
            h2 = "".join(parts[1:]) if len(parts) > 1 else ""
            thesis_y = 238

            if h1:
                h1w, _ = self.text_size(font_title, h1)
                self.draw.text((145, thesis_y), h1, fill=gold, font=font_title)
            if h2:
                self.draw.text((145 + (h1w if h1 else 0), thesis_y), h2, fill=text_p, font=font_title)

        # Divider
        self.divider_line()

        # Bottom tags
        if tags:
            bottom_y = 400
            start_x = 145
            spacing = 185
            for i, (key, meaning) in enumerate(tags):
                px = start_x + i * spacing
                self.draw.text((px, bottom_y), key, fill=gold + (200,), font=font_bottom)
                self.draw.text((px + 2, bottom_y + 26), meaning, fill=text_f + (120,), font=font_tag)

        # Right side verse
        if source:
            verse = source.replace("《", "").replace("》", "")
            tw, _ = self.text_size(font_tag, verse)
            self.draw_right(verse, 467, font_tag, gold_dim + (100,))

    # ── Build ───────────────────────────────────────────────────
    def build(self, title="", subtitle="", highlight="", tags=None, source=""):
        features = self.t.get("features", [])

        self.bg_gradient()
        if "noise" in features:
            self.bg_noise()
        if "ink_wash" in features:
            self.bg_ink_wash()
        if "enso_large" in features:
            self.enso_large()
        if "enso_small" in features:
            self.enso_small()
        if "scroll_lines" in features:
            self.scroll_lines()
        if "book_spines" in features:
            self.book_spines()
        if "translucent_rects" in features:
            self.translucent_rects()
        if "horiz_lines" in features:
            self.horiz_lines()
        if "geometric_lines" in features:
            self.geometric_lines()

        self.edge_lines()
        self.render_text(title, subtitle, highlight, tags, source)

    def save(self, path):
        final = Image.new("RGB", (self.W, self.H), self.t["bg_bot"])
        final.paste(self.img, (0, 0), self.img)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        final.save(path, "PNG", quality=95)
        print(f"[OK] Cover saved: {path} ({self.W}x{self.H})")


# ── CLI ────────────────────────────────────────────────────────
def parse_tags(tag_str: str):
    """Parse 'key1:val1,key2:val2' into [(key1, val1), (key2, val2)]"""
    if not tag_str:
        return None
    pairs = []
    for item in tag_str.split(","):
        if ":" in item:
            k, v = item.split(":", 1)
            pairs.append((k.strip(), v.strip()))
    return pairs if pairs else None


def main():
    parser = argparse.ArgumentParser(description="Generate WeChat cover image (900x500)")
    parser.add_argument("--theme", "-t", default="zen", choices=["zen", "literary", "clean"],
                        help="Design theme (default: zen)")
    parser.add_argument("--title", required=True, help="Main title text")
    parser.add_argument("--subtitle", default="", help="Subtitle text")
    parser.add_argument("--highlight", default="", help="Highlight / thesis text")
    parser.add_argument("--tags", default="", help="Bottom tags, format: key1:val1,key2:val2")
    parser.add_argument("--source", default="", help="Source label (e.g. '《般若波罗蜜多心经》')")
    parser.add_argument("--output", "-o", default="cover.png", help="Output file path")

    args = parser.parse_args()

    cover = Cover(args.theme)
    cover.build(
        title=args.title,
        subtitle=args.subtitle,
        highlight=args.highlight,
        tags=parse_tags(args.tags),
        source=args.source,
    )
    cover.save(str(Path(args.output).resolve()))


if __name__ == "__main__":
    main()
