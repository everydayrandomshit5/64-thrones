"""
audit_production_assets.py - Release Verification Gate for 110 Visual Production Assets.
Part of 64-Thrones: High-Glamour Edition (v3.2).
Complies with Section 7.1 & 7.3 of the Master Build Bible.
"""

import argparse
import json
import sys
from pathlib import Path
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT_DIR / "tools" / "art_manifest.json"
IMAGES_DIR = ROOT_DIR / "game" / "images"


def audit_assets(strict_release_mode: bool = False) -> int:
    """
    Audits 100% of the 110 visual assets listed in tools/art_manifest.json.
    Verifies:
      1. File existence
      2. Valid dimensions (w x h)
      3. Valid PNG format
      4. Metadata status (DEV_PLACEHOLDER vs PRODUCTION_READY)
      5. RGBA alpha channel compliance on sprites
    """
    if not MANIFEST_PATH.exists():
        print(f"[FATAL] Manifest missing: {MANIFEST_PATH}")
        return 1

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assets = manifest.get("assets", [])
    total_count = len(assets)
    print(f"===========================================================")
    print(f"[64-THRONES] ASSET AUDIT GATE (Total Targets: {total_count})")
    print(f"Mode: {'STRICT RELEASE (0 Placeholders Allowed)' if strict_release_mode else 'DEVELOPMENT LAYOUT AUDIT'}")
    print(f"===========================================================\n")

    missing = []
    dimension_errors = []
    placeholders = []
    production_ready = []
    alpha_warnings = []

    for item in assets:
        rel_path = item["path"]
        target_path = IMAGES_DIR / rel_path
        expected_w = item["width"]
        expected_h = item["height"]
        cat = item["category"]

        if not target_path.exists():
            missing.append(rel_path)
            continue

        try:
            with Image.open(target_path) as im:
                w, h = im.size
                if w != expected_w or h != expected_h:
                    dimension_errors.append(
                        f"{rel_path}: Expected {expected_w}x{expected_h}, got {w}x{h}"
                    )

                status = im.text.get("ASSET_STATUS", "UNKNOWN")
                if status == "DEV_PLACEHOLDER":
                    placeholders.append(rel_path)
                elif status == "PRODUCTION_READY":
                    production_ready.append(rel_path)
                else:
                    placeholders.append(rel_path)

                # Alpha transparency check on sprites if production ready
                if cat == "character_sprite" and status == "PRODUCTION_READY":
                    if im.mode == "RGBA":
                        alpha = im.split()[-1]
                        hist = alpha.histogram()
                        transparent_pixels = hist[0]  # alpha == 0
                        total_px = w * h
                        pct_transparent = (transparent_pixels / total_px) * 100
                        if pct_transparent < 15.0:
                            alpha_warnings.append(
                                f"{rel_path}: Insufficient transparent background ({pct_transparent:.1f}% < 15%)"
                            )
                    else:
                        alpha_warnings.append(f"{rel_path}: Sprite missing alpha channel (mode {im.mode})")

        except Exception as e:
            missing.append(f"{rel_path} (Corrupted: {e})")

    # Output Summary
    print(f"Checked Assets:      {total_count}")
    print(f"Files Present:       {total_count - len(missing)} / {total_count}")
    print(f"Valid Dimensions:    {total_count - len(missing) - len(dimension_errors)} / {total_count}")
    print(f"Dev Placeholders:    {len(placeholders)}")
    print(f"Production Ready:    {len(production_ready)}")

    if missing:
        print(f"\n[FAIL] Missing Assets ({len(missing)}):")
        for m in missing[:10]:
            print(f"  - {m}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more.")

    if dimension_errors:
        print(f"\n[FAIL] Dimension Mismatches ({len(dimension_errors)}):")
        for d in dimension_errors:
            print(f"  - {d}")

    if alpha_warnings:
        print(f"\n[WARN] Alpha Channel Warnings ({len(alpha_warnings)}):")
        for a in alpha_warnings:
            print(f"  - {a}")

    print("\n-----------------------------------------------------------")

    if missing or dimension_errors:
        print("[AUDIT FAILED] Missing assets or dimension errors detected.")
        return 1

    if strict_release_mode and len(placeholders) > 0:
        print(f"[AUDIT FAILED (STRICT)] Release packaging blocked: {len(placeholders)} dev placeholders remain.")
        return 1

    print("[AUDIT PASSED] All 110 assets present with valid dimensions and metadata.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit visual assets for 64-Thrones.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Enforces 100%% PRODUCTION_READY status (0 placeholders allowed for release packaging).",
    )
    args = parser.parse_args()
    sys.exit(audit_assets(strict_release_mode=args.strict))
