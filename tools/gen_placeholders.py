"""
gen_placeholders.py - Generates metadata-tagged dimension-accurate layout placeholders.
Part of Phase 2 of 64-Thrones: High-Glamour Edition (v3.2).
Complies with Section 7.1 & 7.3 of the Master Build Bible.
"""

import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT_DIR / "tools" / "art_manifest.json"
IMAGES_DIR = ROOT_DIR / "game" / "images"

# Faction Color Palettes
DAWN_GOLD = (235, 195, 100, 255)
DAWN_IVORY = (250, 245, 235, 255)
DAWN_BG = (45, 35, 30, 255)

DUSK_VIOLET = (175, 120, 230, 255)
DUSK_DARK = (25, 20, 35, 255)
DUSK_TEXT = (235, 225, 250, 255)


def get_font(size: int):
    """Attempts to load a standard truetype font or falls back to default."""
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except Exception:
            return ImageFont.load_default()


def create_placeholder(asset: dict) -> Image.Image:
    """Creates a dimension-accurate, cleanly styled placeholder image."""
    w, h = asset["width"], asset["height"]
    cat = asset["category"]
    fmt = asset.get("format", "RGBA")

    if cat == "character_sprite":
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        char_id = asset.get("char_id", "")
        state = asset.get("state", "state_a_battle")
        is_dawn = char_id.startswith("dawn")
        color = DAWN_GOLD if is_dawn else DUSK_VIOLET
        bg_tint = (50, 40, 20, 180) if is_dawn else (35, 20, 50, 180)

        # Silhouette Card
        margin = 30
        draw.rounded_rectangle(
            [margin, margin, w - margin, h - margin],
            radius=24,
            fill=bg_tint,
            outline=color,
            width=4,
        )

        # Title & State Label
        font_lg = get_font(42)
        font_sm = get_font(28)
        draw.text((w // 2, 80), char_id.upper(), fill=color, anchor="mm", font=font_lg)
        draw.text((w // 2, 140), f"[{state}]", fill=(255, 255, 255, 230), anchor="mm", font=font_sm)

        # Hourglass / Portrait guide
        draw.ellipse([w // 2 - 140, 240, w // 2 + 140, 520], outline=color, width=3)
        draw.rectangle([w // 2 - 160, 500, w // 2 + 160, 920], outline=color, width=3)
        draw.text((w // 2, 700), "PIN-UP SPRITE GUIDE\n900 x 1080 RGBA", fill=(200, 200, 200, 200), anchor="mm", font=font_sm)

        return im

    elif cat == "action_cutin":
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        char_id = asset.get("char_id", "")
        is_dawn = "dawn" in char_id
        c1 = (80, 50, 20, 230) if is_dawn else (40, 20, 60, 230)
        c2 = DAWN_GOLD if is_dawn else DUSK_VIOLET

        # Dynamic diagonal slash banner
        draw.polygon([(0, 20), (w, 0), (w, h - 20), (0, h)], fill=c1, outline=c2)
        draw.line([(0, 40), (w, 20)], fill=c2, width=3)
        draw.line([(0, h - 40), (w, h - 20)], fill=c2, width=3)

        font_lg = get_font(48)
        font_sm = get_font(24)
        draw.text((w // 2, h // 2 - 20), f"ACTION CUT-IN: {char_id.upper()}", fill=c2, anchor="mm", font=font_lg)
        draw.text((w // 2, h // 2 + 35), "1920x360 RGBA — BATTLE DAMAGE / ASCENSION BANNER", fill=(255, 255, 255, 220), anchor="mm", font=font_sm)
        return im

    elif cat == "advisor_bust":
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        char_id = asset.get("char_id", "")
        is_dawn = "dawn" in char_id
        border_col = DAWN_GOLD if is_dawn else DUSK_VIOLET
        inner_bg = (40, 30, 20, 240) if is_dawn else (20, 15, 30, 240)

        # Circular Medallion
        draw.ellipse([4, 4, w - 4, h - 4], fill=inner_bg, outline=border_col, width=4)
        draw.ellipse([10, 10, w - 10, h - 10], outline=(255, 255, 255, 120), width=1)
        font_sm = get_font(18)
        draw.text((w // 2, h // 2), f"{char_id.split('_')[1].upper()}\nBUST", fill=border_col, anchor="mm", font=font_sm)
        return im

    elif cat == "piece_token":
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        faction = asset.get("faction", "dawn")
        piece = asset.get("piece_type", "pawn")
        is_dawn = (faction == "dawn")
        bg_col = (245, 240, 225, 240) if is_dawn else (30, 25, 40, 240)
        border_col = (190, 150, 60, 255) if is_dawn else (150, 100, 210, 255)
        text_col = (60, 40, 10, 255) if is_dawn else (230, 220, 250, 255)

        draw.ellipse([4, 4, w - 4, h - 4], fill=bg_col, outline=border_col, width=3)
        piece_symbol = {"king": "K", "queen": "Q", "rook": "R", "bishop": "B", "knight": "N", "pawn": "P"}.get(piece, "?")
        font = get_font(32)
        draw.text((w // 2, h // 2), piece_symbol, fill=text_col, anchor="mm", font=font)
        return im

    elif cat == "story_cg":
        im = Image.new("RGB", (w, h), (20, 15, 25))
        draw = ImageDraw.Draw(im)
        title = asset.get("title", "Event CG")

        # Atmospheric gradient box
        draw.rectangle([60, 60, w - 60, h - 60], outline=DAWN_GOLD, width=4)
        draw.rectangle([80, 80, w - 80, h - 80], outline=(150, 120, 200), width=2)

        font_lg = get_font(52)
        font_sm = get_font(28)
        draw.text((w // 2, h // 2 - 40), title.upper(), fill=DAWN_GOLD, anchor="mm", font=font_lg)
        draw.text((w // 2, h // 2 + 30), "STORY & FELLOWSHIP CG — 1920x1080 16:9", fill=(220, 220, 220), anchor="mm", font=font_sm)
        return im

    elif cat == "environment_bg":
        im = Image.new("RGB", (w, h), (15, 20, 30))
        draw = ImageDraw.Draw(im)
        p = Path(asset["path"]).stem

        draw.rectangle([40, 40, w - 40, h - 40], outline=(100, 140, 180), width=3)
        font_lg = get_font(48)
        font_sm = get_font(26)
        draw.text((w // 2, h // 2 - 30), p.replace("bg_", "").replace("_", " ").upper(), fill=(200, 230, 255), anchor="mm", font=font_lg)
        draw.text((w // 2, h // 2 + 30), "ENVIRONMENT BACKGROUND — 1920x1080", fill=(140, 160, 190), anchor="mm", font=font_sm)
        return im

    elif cat == "ui_texture":
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(im)
        p = asset["path"]

        if "tile_dawnstone" in p:
            draw.rectangle([0, 0, w, h], fill=(240, 235, 220, 255), outline=(210, 185, 120, 255), width=2)
            draw.rectangle([4, 4, w - 4, h - 4], outline=(255, 250, 235, 180), width=1)
        elif "tile_duskstone" in p:
            draw.rectangle([0, 0, w, h], fill=(30, 25, 40, 255), outline=(100, 70, 140, 255), width=2)
            draw.rectangle([4, 4, w - 4, h - 4], outline=(70, 50, 100, 180), width=1)
        elif "highlight_move" in p:
            draw.rectangle([2, 2, w - 2, h - 2], fill=(100, 255, 120, 80), outline=(80, 240, 100, 220), width=3)
            draw.ellipse([w // 2 - 12, h // 2 - 12, w // 2 + 12, h // 2 + 12], fill=(80, 240, 100, 200))
        elif "highlight_capture" in p:
            draw.rectangle([2, 2, w - 2, h - 2], fill=(255, 60, 60, 90), outline=(240, 40, 40, 230), width=4)
        elif "highlight_check" in p:
            draw.rectangle([2, 2, w - 2, h - 2], fill=(255, 160, 30, 100), outline=(255, 140, 0, 240), width=4)
        elif "highlight_oracle" in p:
            draw.rectangle([2, 2, w - 2, h - 2], fill=(180, 100, 255, 90), outline=(200, 120, 255, 230), width=4)
        elif "ward_aegis" in p:
            draw.ellipse([4, 4, w - 4, h - 4], fill=(255, 215, 0, 110), outline=(255, 230, 80, 240), width=4)
        elif "arrow_" in p:
            # 280x28 vector arrow texture pointing right
            color = (240, 60, 60, 230)
            if "blue" in p:
                color = (60, 140, 240, 230)
            elif "violet" in p:
                color = (180, 80, 240, 230)
            elif "gold" in p:
                color = (255, 210, 50, 230)
            # Arrow body and tip
            draw.rectangle([0, 8, w - 24, 20], fill=color)
            draw.polygon([(w - 24, 0), (w, 14), (w - 24, 28)], fill=color)
        elif "spell_" in p:
            draw.ellipse([4, 4, w - 4, h - 4], fill=(40, 35, 55, 240), outline=DAWN_GOLD, width=3)
            font = get_font(14)
            name = Path(p).stem.replace("spell_", "").upper()
            draw.text((w // 2, h // 2), name, fill=DAWN_GOLD, anchor="mm", font=font)
        elif "frame_hud_panel" in p:
            draw.rounded_rectangle([4, 4, w - 4, h - 4], radius=16, fill=(20, 15, 25, 210), outline=DAWN_GOLD, width=3)
            draw.rounded_rectangle([12, 12, w - 12, h - 12], radius=12, outline=(120, 90, 160, 150), width=1)
        else:
            draw.rectangle([0, 0, w, h], fill=(80, 80, 80, 180), outline=(200, 200, 200), width=2)

        return im

    # Fallback generic image
    im = Image.new("RGBA", (w, h), (60, 60, 60, 200))
    return im


def generate_all_placeholders():
    """Generates all 110 visual assets with ASSET_STATUS=DEV_PLACEHOLDER."""
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing {MANIFEST_PATH}. Run build_manifest.py first.")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assets = manifest.get("assets", [])
    print(f"Generating {len(assets)} metadata-tagged placeholders in {IMAGES_DIR}...")

    # PNG Metadata Tagging: ASSET_STATUS=DEV_PLACEHOLDER (Section 7.3)
    meta = PngImagePlugin.PngInfo()
    meta.add_text("ASSET_STATUS", "DEV_PLACEHOLDER")

    count = 0
    for asset in assets:
        rel_path = asset["path"]
        out_path = IMAGES_DIR / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)

        img = create_placeholder(asset)
        img.save(out_path, "PNG", pnginfo=meta)
        count += 1

    print(f"Successfully generated all {count} placeholders with ASSET_STATUS=DEV_PLACEHOLDER.")


if __name__ == "__main__":
    generate_all_placeholders()
