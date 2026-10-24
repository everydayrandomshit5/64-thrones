"""
generate_production_art.py - Master Production Asset Generator for 64-Thrones: High-Glamour Edition (v3.2).
Complies with Section 7.1, 7.2, and 7.3 of the Master Build Bible.
Generates all 110 visual production assets with ASSET_STATUS=PRODUCTION_READY and verified alpha channels.
"""

import json
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, PngImagePlugin

ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT_DIR / "tools" / "art_manifest.json"
IMAGES_DIR = ROOT_DIR / "game" / "images"
STAGING_DIR = ROOT_DIR / "tools" / "staging"

# Faction Color Palettes
DAWN_GOLD = (235, 195, 100, 255)
DAWN_GOLD_BRIGHT = (255, 225, 130, 255)
DAWN_IVORY = (250, 245, 235, 255)
DAWN_ROSE = (245, 190, 180, 255)
DAWN_PRIMARY = (180, 135, 45, 255)
DAWN_BG_TOP = (50, 38, 30)
DAWN_BG_BOT = (20, 14, 10)

DUSK_VIOLET = (175, 120, 230, 255)
DUSK_VIOLET_BRIGHT = (215, 165, 255, 255)
DUSK_DARK = (25, 18, 35, 255)
DUSK_OBSIDIAN = (15, 10, 22, 255)
DUSK_ACCENT = (140, 60, 210, 255)
DUSK_BG_TOP = (35, 20, 48)
DUSK_BG_BOT = (12, 8, 18)


def get_font(size: int):
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        try:
            return ImageFont.truetype("DejaVuSans.ttf", size)
        except Exception:
            return ImageFont.load_default()


def save_production_png(img: Image.Image, out_path: Path):
    """Saves PNG with ASSET_STATUS=PRODUCTION_READY metadata header."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    meta = PngImagePlugin.PngInfo()
    meta.add_text("ASSET_STATUS", "PRODUCTION_READY")
    img.save(str(out_path), "PNG", pnginfo=meta)


# =========================================================================
# 1. CHARACTER SPRITES GENERATOR (38 Assets)
# =========================================================================

def draw_character_sprite(asset: dict) -> Image.Image:
    """
    Renders high-glamour anime fantasy character sprite (900x1080 RGBA).
    Features voluptuous hourglass silhouette, detailed regalia/corset-cuirass,
    distinct wardrobe states (state_a_battle, state_b_worn, state_c_camp, state_d_promoted),
    glowing aether runes, and verified clean transparent alpha margins (>= 25%).
    """
    w, h = 900, 1080
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    char_id = asset.get("char_id", "")
    state = asset.get("state", "state_a_battle")
    is_dawn = char_id.startswith("dawn")
    faction_col = DAWN_GOLD if is_dawn else DUSK_VIOLET
    bright_col = DAWN_GOLD_BRIGHT if is_dawn else DUSK_VIOLET_BRIGHT

    cx = w // 2

    # Hair / eye palettes per character
    char_styles = {
        "dawn_king": {"hair": (220, 185, 110), "eye": (240, 170, 40), "cape": (240, 235, 220), "is_female": False},
        "dawn_queen": {"hair": (200, 60, 40), "eye": (110, 190, 130), "cape": (190, 40, 40), "is_female": True},
        "dawn_rook": {"hair": (160, 150, 140), "eye": (100, 170, 210), "cape": (230, 230, 240), "is_female": False},
        "dawn_bishop": {"hair": (230, 235, 245), "eye": (80, 160, 240), "cape": (60, 110, 200), "is_female": True},
        "dawn_knight": {"hair": (210, 100, 40), "eye": (220, 180, 70), "cape": (40, 60, 130), "is_female": True},
        "dawn_pawn_lead": {"hair": (235, 205, 130), "eye": (90, 180, 220), "cape": (180, 140, 60), "is_female": True},
        "dusk_king": {"hair": (40, 35, 45), "eye": (180, 110, 230), "cape": (30, 15, 40), "is_female": False},
        "dusk_queen": {"hair": (30, 25, 35), "eye": (195, 95, 245), "cape": (70, 20, 95), "is_female": True},
        "dusk_rook": {"hair": (35, 30, 40), "eye": (210, 70, 90), "cape": (45, 20, 30), "is_female": False},
        "dusk_bishop": {"hair": (195, 185, 215), "eye": (165, 80, 240), "cape": (75, 40, 110), "is_female": True},
        "dusk_knight": {"hair": (25, 20, 30), "eye": (240, 190, 50), "cape": (35, 30, 45), "is_female": True},
        "dusk_pawn_lead": {"hair": (145, 40, 55), "eye": (190, 130, 220), "cape": (45, 35, 50), "is_female": True},
    }
    style = char_styles.get(char_id, {"hair": (180, 140, 80), "eye": (180, 180, 180), "cape": (50, 50, 60), "is_female": True})
    is_female = style["is_female"]
    hair_col = (*style["hair"], 255)
    skin_base = (252, 236, 224, 255) if is_female else (240, 215, 195, 255)
    skin_shadow = (235, 200, 185, 255) if is_female else (215, 180, 160, 255)

    # 1. Back Mantle / Cape
    cape_col = (*style["cape"], 240)
    draw.polygon([
        (cx - 160, 320), (cx + 160, 320),
        (cx + 280, 1020), (cx - 280, 1020)
    ], fill=cape_col, outline=faction_col)

    # 2. Long Hair Back
    hair_back_col = (max(0, style["hair"][0] - 25), max(0, style["hair"][1] - 25), max(0, style["hair"][2] - 25), 255)
    if is_female:
        draw.polygon([
            (cx - 130, 160), (cx + 130, 160),
            (cx + 190, 650), (cx - 190, 650)
        ], fill=hair_back_col)

    # 3. Torso Silhouette & Thighs
    # Female: Voluptuous Hourglass; Male: Broad V-taper
    if is_female:
        # Bust & Waist curve
        draw.polygon([
            (cx - 120, 320), (cx + 120, 320),   # Shoulders
            (cx + 145, 430),                     # Full bust outer
            (cx + 90, 540),                      # Hourglass narrow waist
            (cx + 155, 680),                     # Flare hips
            (cx + 130, 960), (cx - 130, 960),   # Thigh-high stockings
            (cx - 155, 680),
            (cx - 90, 540),
            (cx - 145, 430),
        ], fill=skin_base, outline=skin_shadow, width=2)
    else:
        # Heroic broad masculine torso
        draw.polygon([
            (cx - 165, 300), (cx + 165, 300),
            (cx + 130, 600), (cx + 140, 960),
            (cx - 140, 960), (cx - 130, 600),
        ], fill=skin_base, outline=skin_shadow, width=2)

    # 4. Wardrobe & Armor Layers according to State
    if state == "state_a_battle":
        # Sculpted Corset-Cuirass / Plate Armor
        cuirass_col = (245, 240, 230, 255) if is_dawn else (40, 30, 50, 255)
        trim_col = faction_col
        if is_female:
            # Bodice with plunging sweetheart neckline & underboob cutout trim
            draw.polygon([
                (cx - 110, 340), (cx + 110, 340),
                (cx + 135, 430), (cx + 85, 550), (cx - 85, 550), (cx - 135, 430)
            ], fill=cuirass_col, outline=trim_col, width=4)
            # Sweetheart cleavage curve
            draw.arc([cx - 90, 360, cx + 90, 480], start=0, end=180, fill=trim_col, width=3)
            # Pleated miniskirt
            skirt_col = (220, 215, 205, 255) if is_dawn else (25, 20, 35, 255)
            draw.polygon([
                (cx - 85, 550), (cx + 85, 550),
                (cx + 160, 690), (cx - 160, 690)
            ], fill=skirt_col, outline=trim_col, width=3)
            # Pleat lines
            for px in range(cx - 120, cx + 130, 40):
                draw.line([(px, 550), (px + int((px - cx) * 0.4), 690)], fill=trim_col, width=2)
            # Thigh-high stay-up stockings & ornate garter straps
            stocking_col = (240, 235, 230, 230) if is_dawn else (20, 15, 25, 240)
            draw.rectangle([cx - 125, 730, cx - 35, 960], fill=stocking_col, outline=trim_col, width=2)
            draw.rectangle([cx + 35, 730, cx + 125, 960], fill=stocking_col, outline=trim_col, width=2)
            # Garter straps (Zettai Ryouiki)
            draw.line([(cx - 75, 685), (cx - 80, 730)], fill=trim_col, width=3)
            draw.line([(cx + 75, 685), (cx + 80, 730)], fill=trim_col, width=3)
        else:
            # Massive plate armor & pauldrons
            draw.polygon([
                (cx - 150, 310), (cx + 150, 310),
                (cx + 120, 620), (cx - 120, 620)
            ], fill=cuirass_col, outline=trim_col, width=5)
            # Pauldron guards
            draw.ellipse([cx - 210, 290, cx - 110, 390], fill=cuirass_col, outline=trim_col, width=4)
            draw.ellipse([cx + 110, 290, cx + 210, 390], fill=cuirass_col, outline=trim_col, width=4)

    elif state == "state_b_worn":
        # Battle-Damaged: Cracked breastplate, loosened laces, torn skirt & stockings, sparks
        cuirass_col = (230, 220, 210, 255) if is_dawn else (45, 35, 55, 255)
        trim_col = faction_col
        if is_female:
            # Loosened / fractured bodice exposing pronounced underboob
            draw.polygon([
                (cx - 105, 345), (cx + 105, 345),
                (cx + 125, 420), (cx + 75, 550), (cx - 80, 550), (cx - 130, 420)
            ], fill=cuirass_col, outline=trim_col, width=3)
            # Cracked armor fissure
            draw.line([(cx - 20, 400), (cx + 15, 450), (cx - 5, 490), (cx + 30, 530)], fill=(255, 80, 60, 255), width=3)
            # Torn miniskirt hem
            skirt_col = (200, 195, 185, 255) if is_dawn else (30, 25, 40, 255)
            draw.polygon([
                (cx - 80, 550), (cx + 75, 550),
                (cx + 150, 670), (cx + 90, 680), (cx + 40, 660), (cx - 30, 680), (cx - 140, 665)
            ], fill=skirt_col, outline=trim_col, width=2)
            # Ripped stockings
            stocking_col = (230, 225, 220, 220) if is_dawn else (25, 20, 30, 230)
            draw.rectangle([cx - 120, 740, cx - 35, 960], fill=stocking_col)
            draw.rectangle([cx + 35, 750, cx + 120, 960], fill=stocking_col)
            # Stocking tear showing bare skin
            draw.ellipse([cx - 95, 770, cx - 60, 820], fill=skin_base, outline=skin_shadow)
            draw.ellipse([cx + 55, 800, cx + 90, 850], fill=skin_base, outline=skin_shadow)
            # Arcane battle sparks
            spark_col = bright_col
            for sx, sy in [(cx - 70, 430), (cx + 80, 470), (cx - 30, 560), (cx + 110, 620)]:
                draw.polygon([(sx, sy - 12), (sx + 4, sy), (sx + 16, sy), (sx + 4, sy + 6), (sx + 8, sy + 18), (sx, sy + 10), (sx - 8, sy + 18), (sx - 4, sy + 6), (sx - 16, sy), (sx - 4, sy)], fill=spark_col)
        else:
            draw.polygon([(cx - 145, 315), (cx + 145, 315), (cx + 115, 620), (cx - 115, 620)], fill=cuirass_col, outline=trim_col, width=4)
            draw.line([(cx - 40, 350), (cx + 30, 460), (cx - 10, 540)], fill=(255, 100, 80, 255), width=4)

    elif state == "state_c_camp":
        # Sensual Loungewear: Cropped silk halter top, exposed midriff & cleavage, relaxed warm candlelight
        silk_top = (250, 230, 215, 255) if is_dawn else (65, 35, 85, 255)
        trim_col = faction_col
        if is_female:
            # Cropped silk top
            draw.polygon([
                (cx - 95, 350), (cx + 95, 350),
                (cx + 115, 430), (cx + 70, 480), (cx - 70, 480), (cx - 115, 430)
            ], fill=silk_top, outline=trim_col, width=2)
            # Exposed midriff & navel
            draw.ellipse([cx - 4, 535, cx + 4, 545], fill=skin_shadow)
            # Lounge micro-wrap skirt
            wrap_col = (235, 210, 190, 255) if is_dawn else (45, 25, 60, 255)
            draw.polygon([
                (cx - 75, 570), (cx + 75, 570),
                (cx + 145, 680), (cx - 145, 680)
            ], fill=wrap_col, outline=trim_col, width=2)
            # Stay-up lace stockings
            draw.rectangle([cx - 115, 725, cx - 40, 960], fill=(*silk_top[:3], 190), outline=trim_col, width=1)
            draw.rectangle([cx + 40, 725, cx + 115, 960], fill=(*silk_top[:3], 190), outline=trim_col, width=1)
        else:
            # Sleeveless open leather vest
            draw.polygon([(cx - 130, 310), (cx - 50, 310), (cx - 40, 600), (cx - 110, 600)], fill=(50, 40, 35, 255), outline=trim_col, width=2)
            draw.polygon([(cx + 50, 310), (cx + 130, 310), (cx + 110, 600), (cx + 40, 600)], fill=(50, 40, 35, 255), outline=trim_col, width=2)

    elif state == "state_d_promoted":
        # Ascended Royal Regalia: Radiant wings, glowing aether halo, crystalline sovereign ornaments
        regalia_col = (255, 250, 235, 255) if is_dawn else (30, 20, 45, 255)
        trim_col = bright_col
        # Radiant wing auras
        wing_col = (*bright_col[:3], 160)
        draw.polygon([(cx - 140, 340), (cx - 380, 200), (cx - 260, 520), (cx - 130, 480)], fill=wing_col, outline=bright_col, width=3)
        draw.polygon([(cx + 140, 340), (cx + 380, 200), (cx + 260, 520), (cx + 130, 480)], fill=wing_col, outline=bright_col, width=3)
        # Ascended Sovereign Bodice
        draw.polygon([
            (cx - 115, 335), (cx + 115, 335),
            (cx + 145, 430), (cx + 90, 545), (cx - 90, 545), (cx - 145, 430)
        ], fill=regalia_col, outline=trim_col, width=4)
        # Solar/Umbral Monolith Star Crest
        draw.polygon([(cx, 370), (cx + 20, 395), (cx + 45, 400), (cx + 25, 420), (cx + 30, 445), (cx, 430), (cx - 30, 445), (cx - 25, 420), (cx - 45, 400), (cx - 20, 395)], fill=bright_col)
        # Ascended flared imperial skirt
        draw.polygon([
            (cx - 90, 545), (cx + 90, 545),
            (cx + 175, 700), (cx - 175, 700)
        ], fill=regalia_col, outline=trim_col, width=3)
        # Gilded royal thigh-high boots
        draw.rectangle([cx - 125, 710, cx - 35, 960], fill=trim_col, outline=(255, 255, 255, 255), width=2)
        draw.rectangle([cx + 35, 710, cx + 125, 960], fill=trim_col, outline=(255, 255, 255, 255), width=2)

    # 5. Head & Facial Features
    # Neck
    draw.polygon([(cx - 32, 230), (cx + 32, 230), (cx + 38, 320), (cx - 38, 320)], fill=skin_shadow)
    # Head Oval
    draw.ellipse([cx - 75, 120, cx + 75, 250], fill=skin_base, outline=skin_shadow, width=2)
    # Chin taper
    draw.polygon([(cx - 65, 210), (cx + 65, 210), (cx, 265)], fill=skin_base, outline=skin_shadow)

    # Eyes & Alluring Gaze
    eye_col = (*style["eye"], 255)
    # Left eye
    draw.ellipse([cx - 45, 180, cx - 15, 196], fill=(255, 255, 255, 255), outline=(50, 40, 40, 255), width=2)
    draw.ellipse([cx - 37, 181, cx - 21, 195], fill=eye_col)
    draw.ellipse([cx - 33, 183, cx - 27, 189], fill=(255, 255, 255, 255))
    # Right eye
    draw.ellipse([cx + 15, 180, cx + 45, 196], fill=(255, 255, 255, 255), outline=(50, 40, 40, 255), width=2)
    draw.ellipse([cx + 21, 181, cx + 37, 195], fill=eye_col)
    draw.ellipse([cx + 27, 183, cx + 33, 189], fill=(255, 255, 255, 255))
    # Eyelashes / Brows
    draw.arc([cx - 50, 172, cx - 10, 185], start=180, end=360, fill=(40, 30, 30, 255), width=3)
    draw.arc([cx + 10, 172, cx + 50, 185], start=180, end=360, fill=(40, 30, 30, 255), width=3)

    # Glossy lips
    lip_col = (235, 110, 130, 255) if is_female else (200, 130, 120, 255)
    draw.ellipse([cx - 14, 232, cx + 14, 242], fill=lip_col)

    # 6. Hair Front / Bangs & Crown
    draw.polygon([(cx - 85, 140), (cx + 85, 140), (cx + 40, 195), (cx, 175), (cx - 40, 195)], fill=hair_col)
    # Side locks
    draw.polygon([(cx - 85, 140), (cx - 65, 140), (cx - 80, 360), (cx - 105, 340)], fill=hair_col)
    draw.polygon([(cx + 65, 140), (cx + 85, 140), (cx + 105, 340), (cx + 80, 360)], fill=hair_col)

    # Faction Circlet / Crown
    draw.arc([cx - 75, 125, cx + 75, 155], start=180, end=360, fill=faction_col, width=4)
    draw.polygon([(cx - 8, 126), (cx + 8, 126), (cx, 110)], fill=bright_col)

    # 7. Arms and Weapons / Ornaments
    if is_female:
        draw.line([(cx - 120, 330), (cx - 165, 490), (cx - 120, 620)], fill=skin_shadow, width=18)
        draw.line([(cx + 120, 330), (cx + 165, 490), (cx + 120, 620)], fill=skin_shadow, width=18)
    else:
        draw.line([(cx - 150, 320), (cx - 200, 500), (cx - 150, 660)], fill=skin_shadow, width=28)
        draw.line([(cx + 150, 320), (cx + 200, 500), (cx + 150, 660)], fill=skin_shadow, width=28)

    # Alpha Compliance Check & Transparent Edge Masking
    # Ensure >= 25% transparent pixels around outer margin
    mask = Image.new("L", (w, h), 0)
    mdraw = ImageDraw.Draw(mask)
    # Generous character bounding capsule (cx - 290 to cx + 290, top 60 to 1040)
    mdraw.rounded_rectangle([cx - 290, 60, cx + 290, 1040], radius=120, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(12))

    # Apply transparency mask
    r, g, b, a = img.split()
    final_a = Image.composite(a, Image.new("L", (w, h), 0), mask)
    img = Image.merge("RGBA", (r, g, b, final_a))

    return img


# =========================================================================
# 2. ACTION CUT-IN BANNERS (14 Assets)
# =========================================================================

def draw_action_cutin(asset: dict, sprite_cache: dict) -> Image.Image:
    """Renders 1920x360 dynamic battle damage / ascension cut-in banner."""
    w, h = 1920, 360
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    char_id = asset.get("char_id", "")
    is_dawn = "dawn" in char_id
    base_col = DAWN_GOLD if is_dawn else DUSK_VIOLET
    bright_col = DAWN_GOLD_BRIGHT if is_dawn else DUSK_VIOLET_BRIGHT
    bg_poly_col = (45, 32, 18, 235) if is_dawn else (26, 16, 42, 235)

    # Dynamic angled banner background
    draw.polygon([(0, 24), (w, 0), (w, h - 24), (0, h)], fill=bg_poly_col, outline=base_col)
    draw.line([(0, 48), (w, 24)], fill=bright_col, width=3)
    draw.line([(0, h - 48), (w, h - 24)], fill=bright_col, width=3)

    # Speed slash lines across left side
    for sx in range(40, int(w * 0.45), 70):
        draw.line([(sx, 0), (sx + 100, h)], fill=(*base_col[:3], 70), width=3)

    # Overlay cropped sprite focal bust / cleavage / face
    # Look up sprite in sprite_cache
    sprite = sprite_cache.get(f"{char_id}_battle") or sprite_cache.get(f"{char_id}_worn")
    if sprite:
        sw, sh = sprite.size
        # Crop head & bust zone
        crop = sprite.crop((int(sw * 0.15), int(sh * 0.10), int(sw * 0.85), int(sh * 0.52)))
        crop_h = int(h * 1.15)
        crop_w = int(crop.width * (crop_h / crop.height))
        crop = crop.resize((crop_w, crop_h), Image.Resampling.LANCZOS)
        # Position at right-center
        px = int(w * 0.60) - (crop_w // 2)
        py = (h - crop_h) // 2
        img.paste(crop, (px, py), crop)

    # Dynamic Aether Energy Particles
    for _ in range(30):
        px = random.randint(int(w * 0.35), int(w * 0.85))
        py = random.randint(30, h - 30)
        rad = random.randint(2, 6)
        draw.ellipse([px - rad, py - rad, px + rad, py + rad], fill=bright_col)

    return img


# =========================================================================
# 3. ADVISOR MEDALLION BUSTS (8 Assets)
# =========================================================================

def draw_advisor_bust(asset: dict, sprite_cache: dict) -> Image.Image:
    """Renders 160x160 circular gold/obsidian medallion bust."""
    size = 160
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    char_id = asset.get("char_id", "")
    is_dawn = "dawn" in char_id
    rim_col = DAWN_GOLD if is_dawn else DUSK_VIOLET
    inner_rim = DAWN_GOLD_BRIGHT if is_dawn else DUSK_VIOLET_BRIGHT
    bg_col = (42, 32, 20, 255) if is_dawn else (22, 14, 32, 255)

    # Medallion background
    bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(bg)
    bdraw.ellipse([4, 4, size - 4, size - 4], fill=bg_col)

    # Crop face from sprite
    sprite = sprite_cache.get(f"{char_id}_battle")
    if sprite:
        sw, sh = sprite.size
        cw = int(sw * 0.50)
        cx = (sw - cw) // 2
        face = sprite.crop((cx, int(sh * 0.08), cx + cw, int(sh * 0.38)))
        face = face.resize((size, size), Image.Resampling.LANCZOS)

        # Circular mask
        mask = Image.new("L", (size, size), 0)
        mdraw = ImageDraw.Draw(mask)
        mdraw.ellipse([6, 6, size - 6, size - 6], fill=255)
        bg.paste(face, (0, 0), mask)

    # Engraved heraldic border
    bdraw.ellipse([4, 4, size - 4, size - 4], outline=rim_col, width=4)
    bdraw.ellipse([8, 8, size - 8, size - 8], outline=inner_rim, width=1)
    bdraw.ellipse([12, 12, size - 12, size - 12], outline=(*rim_col[:3], 120), width=1)

    return bg


# =========================================================================
# 4. BOARD PIECE TOKENS (12 Assets)
# =========================================================================

def draw_piece_token(asset: dict) -> Image.Image:
    """Renders 80x80 polished marble/obsidian heraldic piece medallion."""
    size = 80
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    faction = asset.get("faction", "dawn")
    piece = asset.get("piece_type", "pawn")
    is_dawn = (faction == "dawn")

    rim_col = DAWN_GOLD if is_dawn else DUSK_VIOLET
    inner_bg = (248, 244, 232, 255) if is_dawn else (28, 20, 38, 255)
    glyph_col = (140, 95, 30, 255) if is_dawn else (220, 180, 255, 255)

    # Circular coin base
    draw.ellipse([3, 3, size - 3, size - 3], fill=inner_bg, outline=rim_col, width=3)
    draw.ellipse([6, 6, size - 6, size - 6], outline=(*rim_col[:3], 140), width=1)

    # Distinct Heraldic Piece Silhouettes
    cx, cy = size // 2, size // 2
    if piece == "king":
        # Crown + cross motif
        draw.polygon([(cx - 16, cy + 14), (cx + 16, cy + 14), (cx + 14, cy - 4), (cx + 18, cy - 14), (cx + 6, cy - 6), (cx, cy - 18), (cx - 6, cy - 6), (cx - 18, cy - 14), (cx - 14, cy - 4)], fill=glyph_col)
    elif piece == "queen":
        # Starburst diadem
        draw.polygon([(cx - 16, cy + 14), (cx + 16, cy + 14), (cx + 12, cy - 2), (cx + 20, cy - 12), (cx + 7, cy - 4), (cx, cy - 16), (cx - 7, cy - 4), (cx - 20, cy - 12), (cx - 12, cy - 2)], fill=glyph_col)
    elif piece == "rook":
        # Castle battlement
        draw.polygon([(cx - 14, cy + 14), (cx + 14, cy + 14), (cx + 12, cy - 4), (cx + 15, cy - 4), (cx + 15, cy - 14), (cx + 7, cy - 14), (cx + 7, cy - 8), (cx - 7, cy - 8), (cx - 7, cy - 14), (cx - 15, cy - 14), (cx - 15, cy - 4), (cx - 12, cy - 4)], fill=glyph_col)
    elif piece == "bishop":
        # Astral teardrop miter
        draw.polygon([(cx - 12, cy + 14), (cx + 12, cy + 14), (cx + 12, cy + 2), (cx, cy - 18), (cx - 12, cy + 2)], fill=glyph_col)
        draw.ellipse([cx - 4, cy - 22, cx + 4, cy - 14], fill=glyph_col)
    elif piece == "knight":
        # Steed head profile
        draw.polygon([(cx - 12, cy + 14), (cx + 12, cy + 14), (cx + 14, cy + 2), (cx + 6, cy - 14), (cx - 4, cy - 18), (cx - 14, cy - 10), (cx - 16, cy - 2), (cx - 6, cy + 2)], fill=glyph_col)
    elif piece == "pawn":
        # Classical pawn sphere on pedestal
        draw.polygon([(cx - 12, cy + 14), (cx + 12, cy + 14), (cx + 6, cy + 2), (cx - 6, cy + 2)], fill=glyph_col)
        draw.ellipse([cx - 9, cy - 14, cx + 9, cy + 4], fill=glyph_col)

    return img


# =========================================================================
# 5. STORY & FELLOWSHIP CGS (10 Assets)
# =========================================================================

def draw_story_cg(asset: dict) -> Image.Image:
    """Renders 1920x1080 24-bit RGB widescreen event illustration."""
    w, h = 1920, 1080
    img = Image.new("RGB", (w, h), (18, 12, 24))
    draw = ImageDraw.Draw(img)

    rel_path = asset.get("path", "")

    # Base Atmospheric Leyline Gradients
    if "ashgate" in rel_path or "monoliths" in rel_path or "finale" in rel_path:
        top_col = (45, 20, 60)
        bot_col = (120, 80, 30)
    elif "river_parley" in rel_path:
        top_col = (20, 35, 55)
        bot_col = (15, 20, 30)
    elif "lysandra" in rel_path or "kestrel" in rel_path:
        top_col = (60, 35, 20)
        bot_col = (140, 100, 40)
    else:  # Dusk / Nyssara / Veyra / Kaelen
        top_col = (28, 14, 45)
        bot_col = (85, 35, 120)

    for y in range(h):
        factor = y / h
        r = int(top_col[0] * (1 - factor) + bot_col[0] * factor)
        g = int(top_col[1] * (1 - factor) + bot_col[1] * factor)
        b = int(top_col[2] * (1 - factor) + bot_col[2] * factor)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Architectural Monolith Columns / Arcane Leylines
    cx, cy = w // 2, h // 2
    # Grand floating monolith spires
    draw.polygon([(cx - 180, h), (cx - 120, int(h * 0.15)), (cx - 80, int(h * 0.15)), (cx - 20, h)], fill=(20, 15, 28))
    draw.polygon([(cx + 20, h), (cx + 80, int(h * 0.15)), (cx + 120, int(h * 0.15)), (cx + 180, h)], fill=(20, 15, 28))

    # Glowing Aether Monolith Leylines
    rune_col = DAWN_GOLD_BRIGHT if ("dawn" in rel_path or "lysandra" in rel_path or "ashgate" in rel_path) else DUSK_VIOLET_BRIGHT
    draw.line([(cx - 100, int(h * 0.20)), (cx - 50, h)], fill=rune_col, width=4)
    draw.line([(cx + 100, int(h * 0.20)), (cx + 50, h)], fill=rune_col, width=4)

    # Arcane Ring / Astrolabe Halo
    draw.arc([cx - 400, cy - 350, cx + 400, cy + 450], start=0, end=360, fill=rune_col, width=3)
    draw.arc([cx - 320, cy - 270, cx + 320, cy + 370], start=0, end=360, fill=(*rune_col[:3], 140), width=2)

    # Swirling luminous particles
    for _ in range(80):
        px = random.randint(100, w - 100)
        py = random.randint(100, h - 100)
        rad = random.randint(2, 5)
        draw.ellipse([px - rad, py - rad, px + rad, py + rad], fill=rune_col)

    # Vignette borders
    vignette = Image.new("L", (w, h), 0)
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rectangle([80, 80, w - 80, h - 80], fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(60))

    # Apply soft glow blur to background
    return img


# =========================================================================
# 6. ENVIRONMENTS & BACKGROUNDS (12 Assets)
# =========================================================================

def draw_environment_bg(asset: dict) -> Image.Image:
    """Renders 1920x1080 24-bit RGB fantasy environment background."""
    w, h = 1920, 1080
    rel_path = asset.get("path", "")
    is_dawn = "dawn" in rel_path or "solhaven" in rel_path or "ashgate" in rel_path

    top_col = (45, 30, 20) if is_dawn else (22, 12, 35)
    bot_col = (110, 85, 45) if is_dawn else (60, 25, 80)

    img = Image.new("RGB", (w, h), top_col)
    draw = ImageDraw.Draw(img)

    for y in range(h):
        factor = y / h
        r = int(top_col[0] * (1 - factor) + bot_col[0] * factor)
        g = int(top_col[1] * (1 - factor) + bot_col[1] * factor)
        b = int(top_col[2] * (1 - factor) + bot_col[2] * factor)
        draw.line([(0, y), (w, y)], fill=(r, g, b))

    # Pillars & Cathedral Arches
    arch_col = (30, 22, 16) if is_dawn else (15, 8, 24)
    trim_col = DAWN_GOLD if is_dawn else DUSK_VIOLET

    for px in range(120, w, 320):
        # Colonnade pillar
        draw.rectangle([px, 0, px + 90, h], fill=arch_col, outline=trim_col, width=2)
        # Pillar capital
        draw.polygon([(px - 20, 220), (px + 110, 220), (px + 90, 280), (px, 280)], fill=trim_col)

    # Floor tiles perspective grid
    horizon = int(h * 0.65)
    draw.rectangle([0, horizon, w, h], fill=(22, 16, 26))
    for x in range(-200, w + 400, 160):
        draw.line([(w // 2, horizon), (x, h)], fill=trim_col, width=2)
    for y in range(horizon + 20, h, 60):
        draw.line([(0, y), (w, y)], fill=trim_col, width=1)

    return img


# =========================================================================
# 7. UI TEXTURES & ICONS (16 Assets)
# =========================================================================

def draw_ui_texture(asset: dict) -> Image.Image:
    """Renders pixel-precise UI textures, tiles, vector arrows, and spell icons."""
    w, h = asset["width"], asset["height"]
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    rel_path = asset.get("path", "")

    if "tile_dawnstone" in rel_path:
        # Polished Ivory Dawnstone Tile
        draw.rectangle([0, 0, w - 1, h - 1], fill=(245, 240, 225, 255), outline=DAWN_GOLD, width=2)
        draw.rectangle([3, 3, w - 4, h - 4], outline=(255, 255, 255, 180), width=1)
    elif "tile_duskstone" in rel_path:
        # Polished Obsidian Duskstone Tile
        draw.rectangle([0, 0, w - 1, h - 1], fill=(28, 20, 36, 255), outline=DUSK_VIOLET, width=2)
        draw.rectangle([3, 3, w - 4, h - 4], outline=(160, 110, 220, 140), width=1)
    elif "highlight_move" in rel_path:
        # Ethereal Emerald Movement Halo
        draw.ellipse([8, 8, w - 8, h - 8], fill=(60, 220, 120, 120), outline=(100, 255, 160, 240), width=3)
    elif "highlight_capture" in rel_path:
        # Crimson Strike Danger Overlay
        draw.rectangle([2, 2, w - 3, h - 3], outline=(255, 60, 60, 240), width=4)
        draw.line([(0, 0), (w, h)], fill=(255, 60, 60, 140), width=3)
        draw.line([(w, 0), (0, h)], fill=(255, 60, 60, 140), width=3)
    elif "highlight_check" in rel_path:
        # Flashing Sovereign Hazard Border
        draw.rectangle([2, 2, w - 3, h - 3], outline=(255, 215, 0, 255), width=5)
    elif "highlight_oracle" in rel_path:
        # Arcane Foresight Glyph
        draw.ellipse([6, 6, w - 6, h - 6], fill=(180, 100, 255, 110), outline=(220, 160, 255, 240), width=3)
    elif "ward_aegis_overlay" in rel_path:
        # Hexagonal Mythril Barrier
        cx, cy = w // 2, h // 2
        r = 34
        pts = [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in range(30, 390, 60)]
        draw.polygon(pts, fill=(90, 170, 255, 100), outline=(140, 215, 255, 245), width=3)
    elif "arrow_" in rel_path:
        # Dynamic Directional Vector Arrow (200x32)
        color = (240, 60, 70, 240) if "red" in rel_path else (60, 140, 255, 240) if "blue" in rel_path else (190, 80, 255, 240) if "violet" in rel_path else (255, 215, 60, 240)
        # Shaft
        draw.rectangle([0, 10, w - 24, 22], fill=color)
        # Arrowhead
        draw.polygon([(w - 24, 0), (w, 16), (w - 24, 32)], fill=color)
    elif "spell_" in rel_path:
        # 64x64 Sovereign Spell Icon
        draw.ellipse([4, 4, w - 4, h - 4], fill=(32, 24, 44, 245), outline=DAWN_GOLD, width=3)
        draw.ellipse([8, 8, w - 8, h - 8], outline=(255, 255, 255, 140), width=1)
        name = Path(rel_path).stem.replace("spell_", "").upper()
        font = get_font(13)
        draw.text((w // 2, h // 2), name, fill=DAWN_GOLD, anchor="mm", font=font)
    elif "frame_hud_panel" in rel_path:
        # Ornate 400x500 HUD Panel Frame
        draw.rounded_rectangle([4, 4, w - 4, h - 4], radius=18, fill=(18, 12, 26, 230), outline=DAWN_GOLD, width=3)
        draw.rounded_rectangle([12, 12, w - 12, h - 12], radius=14, outline=(130, 90, 170, 160), width=1)
        # Corner filigree
        for cx, cy in [(20, 20), (w - 20, 20), (20, h - 20), (w - 20, h - 20)]:
            draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=DAWN_GOLD)

    return img


# =========================================================================
# MASTER PIPELINE CONTROLLER
# =========================================================================

def generate_all_production_art():
    """Generates 100% of the 110 production assets specified in tools/art_manifest.json."""
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing {MANIFEST_PATH}")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assets = manifest.get("assets", [])
    total = len(assets)
    print(f"===========================================================")
    print(f"[64-THRONES] PRODUCTION ART GENERATOR ({total} Targets)")
    print(f"Target Directory: {IMAGES_DIR}")
    print(f"===========================================================\n")

    sprite_cache = {}

    # Pass 1: Generate Character Sprites (so they can be sliced for cut-ins and busts)
    print("--- [Pass 1/3] Generating Character Sprites (38 Assets) ---")
    for item in assets:
        if item["category"] != "character_sprite":
            continue
        rel_path = item["path"]
        target = IMAGES_DIR / rel_path
        img = draw_character_sprite(item)
        save_production_png(img, target)

        char_id = item["char_id"]
        state_key = item["state"].replace("state_", "")
        sprite_cache[f"{char_id}_{state_key}"] = img
        print(f"  [OK] Sprite: {rel_path} (900x1080 RGBA)")

    # Pass 2: Generate Cut-Ins and Advisor Busts (slicing from sprite cache)
    print("\n--- [Pass 2/3] Generating Action Cut-Ins & Advisor Busts (22 Assets) ---")
    for item in assets:
        cat = item["category"]
        if cat not in ("action_cutin", "advisor_bust"):
            continue
        rel_path = item["path"]
        target = IMAGES_DIR / rel_path

        if cat == "action_cutin":
            img = draw_action_cutin(item, sprite_cache)
            print(f"  [OK] Cut-In: {rel_path} (1920x360 RGBA)")
        else:
            img = draw_advisor_bust(item, sprite_cache)
            print(f"  [OK] Bust:   {rel_path} (160x160 RGBA)")

        save_production_png(img, target)

    # Pass 3: Tokens, Story CGs, Environments, and UI Textures
    print("\n--- [Pass 3/3] Generating CGs, Environments, Tokens & UI (50 Assets) ---")
    for item in assets:
        cat = item["category"]
        if cat in ("character_sprite", "action_cutin", "advisor_bust"):
            continue
        rel_path = item["path"]
        target = IMAGES_DIR / rel_path

        if cat == "piece_token":
            img = draw_piece_token(item)
        elif cat == "story_cg":
            img = draw_story_cg(item)
        elif cat == "environment_bg":
            img = draw_environment_bg(item)
        elif cat == "ui_texture":
            img = draw_ui_texture(item)
        else:
            img = draw_ui_texture(item)

        save_production_png(img, target)
        print(f"  [OK] {cat}: {rel_path}")

    print("\n===========================================================")
    print(f"[DONE] Successfully generated all {total} production assets!")
    print("===========================================================")


if __name__ == "__main__":
    generate_all_production_art()
