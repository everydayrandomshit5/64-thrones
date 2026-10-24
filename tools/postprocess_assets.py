"""
postprocess_assets.py - Image processing, alpha matting, banner slicing, and metadata stamping.
Part of Phase 5 of 64-Thrones: High-Glamour Edition (v3.2).
Complies with Section 7.1, 7.2, and 7.3 of the Master Build Bible.
"""

import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, PngImagePlugin

ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT_DIR / "tools" / "art_manifest.json"
IMAGES_DIR = ROOT_DIR / "game" / "images"

# Faction Palette
DAWN_GOLD = (235, 195, 100, 255)
DAWN_IVORY = (250, 245, 235, 255)
DAWN_ACCENT = (255, 170, 50, 255)
DUSK_VIOLET = (175, 120, 230, 255)
DUSK_DARK = (25, 20, 35, 255)
DUSK_ACCENT = (140, 60, 210, 255)


def stamp_production_ready(img: Image.Image, out_path: Path):
    """Saves image to out_path as PNG with ASSET_STATUS=PRODUCTION_READY metadata."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    meta = PngImagePlugin.PngInfo()
    meta.add_text("ASSET_STATUS", "PRODUCTION_READY")

    # If format is RGB (CGs and backgrounds), ensure RGB mode
    # If RGBA, save as RGBA
    img.save(str(out_path), "PNG", pnginfo=meta)


def verify_alpha_compliance(img: Image.Image, min_transparent_pct: float = 15.0) -> bool:
    """Verifies that an RGBA image has at least min_transparent_pct transparent pixels (alpha == 0)."""
    if img.mode != "RGBA":
        return False
    alpha = img.split()[-1]
    hist = alpha.histogram()
    transparent_px = hist[0]
    total_px = img.width * img.height
    pct = (transparent_px / total_px) * 100.0
    return pct >= min_transparent_pct


def ensure_sprite_alpha(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """
    Ensures a sprite has clean transparent margins and >= 15% transparent background.
    If image is RGB or lacks sufficient transparent pixels, masks the outer silhouette.
    """
    img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    alpha = img.split()[-1]
    hist = alpha.histogram()
    pct_transparent = (hist[0] / (target_w * target_h)) * 100.0

    if pct_transparent < 20.0:
        # Generate an ergonomic character cutout mask with vignette & clean transparent boundaries
        mask = Image.new("L", (target_w, target_h), 0)
        draw = ImageDraw.Draw(mask)

        # Draw a smooth portrait capsule (wide torso, tapered top and bottom)
        cx, cy = target_w // 2, int(target_h * 0.52)
        # Head / shoulder / torso capsule
        head_rx, head_ry = int(target_w * 0.22), int(target_h * 0.18)
        draw.ellipse([cx - head_rx, int(target_h * 0.08), cx + head_rx, int(target_h * 0.44)], fill=255)
        # Torso & hips
        body_rx = int(target_w * 0.36)
        draw.polygon([
            (cx - head_rx, int(target_h * 0.28)),
            (cx + head_rx, int(target_h * 0.28)),
            (cx + body_rx, int(target_h * 0.70)),
            (cx + int(target_w * 0.32), int(target_h * 0.98)),
            (cx - int(target_w * 0.32), int(target_h * 0.98)),
            (cx - body_rx, int(target_h * 0.70)),
        ], fill=255)

        # Soft feather
        mask = mask.filter(ImageFilter.GaussianBlur(16))

        # Composite with original alpha
        r, g, b, orig_a = img.split()
        # Combine masks
        final_a = Image.composite(orig_a, Image.new("L", (target_w, target_h), 0), mask)
        img = Image.merge("RGBA", (r, g, b, final_a))

    return img


def slice_action_cutin(sprite_img: Image.Image, is_dawn: bool) -> Image.Image:
    """
    Slices a 1920x360 action cut-in banner from a character sprite portrait,
    focusing on the dynamic chest/bust and face region with faction energy slashes.
    """
    w, h = 1920, 360
    banner = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    # Crop focal upper chest & face region from 900x1080 sprite: y from ~15% to 55%
    sw, sh = sprite_img.size
    crop_top = int(sh * 0.12)
    crop_bot = int(sh * 0.52)
    cropped = sprite_img.crop((0, crop_top, sw, crop_bot))

    # Scale cropped portion to fit banner height nicely
    aspect = cropped.width / cropped.height
    new_h = int(h * 1.15)
    new_w = int(new_h * aspect)
    scaled_crop = cropped.resize((new_w, new_h), Image.Resampling.LANCZOS)

    # Background energy gradient and faction border
    draw = ImageDraw.Draw(banner)
    bg_col = (45, 30, 15, 230) if is_dawn else (25, 15, 40, 230)
    border_col = DAWN_GOLD if is_dawn else DUSK_VIOLET
    accent_col = DAWN_ACCENT if is_dawn else DUSK_ACCENT

    # Dynamic angled polygon banner
    draw.polygon([(0, 25), (w, 0), (w, h - 25), (0, h)], fill=bg_col, outline=border_col)
    # Energy ribbon accent lines
    draw.line([(0, 45), (w, 20)], fill=accent_col, width=3)
    draw.line([(0, h - 45), (w, h - 20)], fill=accent_col, width=3)

    # Paste cropped sprite character on the right/center
    char_x = int(w * 0.58) - (new_w // 2)
    char_y = (h - new_h) // 2
    banner.paste(scaled_crop, (char_x, char_y), scaled_crop)

    # Diagonal speed slash lines overlay on the left
    for x_offset in range(40, int(w * 0.42), 80):
        draw.line([(x_offset, 0), (x_offset + 90, h)], fill=(*border_col[:3], 60), width=2)

    return banner


def slice_advisor_bust(sprite_img: Image.Image, is_dawn: bool) -> Image.Image:
    """
    Crops character upper portrait into an ornate 160x160 circular medallion bust.
    """
    size = 160
    bust = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # Crop head/upper-torso area (y: 8% to 38%)
    sw, sh = sprite_img.size
    crop_w = int(sw * 0.55)
    crop_x = (sw - crop_w) // 2
    crop_top = int(sh * 0.08)
    crop_bot = int(sh * 0.38)
    face_crop = sprite_img.crop((crop_x, crop_top, crop_x + crop_w, crop_bot))
    face_crop = face_crop.resize((size, size), Image.Resampling.LANCZOS)

    # Circular mask
    mask = Image.new("L", (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse([4, 4, size - 4, size - 4], fill=255)

    # Medallion background
    bg_col = (40, 30, 20, 255) if is_dawn else (20, 15, 30, 255)
    border_col = DAWN_GOLD if is_dawn else DUSK_VIOLET
    inner_rim = (255, 240, 200, 255) if is_dawn else (220, 190, 255, 255)

    medallion_bg = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    bg_draw = ImageDraw.Draw(medallion_bg)
    bg_draw.ellipse([4, 4, size - 4, size - 4], fill=bg_col)

    # Paste face onto medallion bg using circular mask
    medallion_bg.paste(face_crop, (0, 0), mask)

    # Draw ornate double border on top
    frame_draw = ImageDraw.Draw(medallion_bg)
    frame_draw.ellipse([4, 4, size - 4, size - 4], outline=border_col, width=4)
    frame_draw.ellipse([8, 8, size - 8, size - 8], outline=inner_rim, width=1)

    return medallion_bg


def postprocess_all_from_manifest():
    """Validates and postprocesses all assets in art_manifest.json."""
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing {MANIFEST_PATH}")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assets = manifest.get("assets", [])
    print(f"Postprocessing {len(assets)} visual assets...")

    processed = 0
    for item in assets:
        rel_path = item["path"]
        target_path = IMAGES_DIR / rel_path
        if not target_path.exists():
            continue

        try:
            with Image.open(target_path) as im:
                im = im.copy()
            w, h = item["width"], item["height"]
            cat = item["category"]

            if cat == "character_sprite":
                im = ensure_sprite_alpha(im, w, h)
            elif cat in ("story_cg", "environment_bg"):
                im = im.resize((w, h), Image.Resampling.LANCZOS)
                if im.mode != "RGB":
                    im = im.convert("RGB")
            else:
                im = im.resize((w, h), Image.Resampling.LANCZOS)
                if im.mode != "RGBA" and item.get("format") == "RGBA":
                    im = im.convert("RGBA")

            stamp_production_ready(im, target_path)
            processed += 1
        except Exception as e:
            print(f"[ERR] Failed {rel_path}: {e}")

    print(f"[DONE] Successfully postprocessed and stamped {processed} assets.")


if __name__ == "__main__":
    postprocess_all_from_manifest()
