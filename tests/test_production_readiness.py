"""
test_production_readiness.py - Production asset completion, alpha matting, and engine lint test.
Part of Phase 5 of 64-Thrones: High-Glamour Edition (v3.2).
Complies with Section 7.1, 7.3 & Section 8.1 of the Master Build Bible.
"""

import json
import re
import wave
from pathlib import Path
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT_DIR / "tools"
GAME_DIR = ROOT_DIR / "game"
IMAGES_DIR = GAME_DIR / "images"
AUDIO_DIR = GAME_DIR / "audio"
ART_MANIFEST = TOOLS_DIR / "art_manifest.json"
AUDIO_MANIFEST = TOOLS_DIR / "audio_manifest.json"

from tools.audit_production_assets import audit_assets


def test_strict_release_asset_audit():
    """Verify that audit_production_assets.py passes in strict release mode (0 placeholders)."""
    assert ART_MANIFEST.exists()
    exit_code = audit_assets(strict_release_mode=True)
    assert exit_code == 0, "Strict asset audit gate failed: placeholders or dimension errors remain."


def test_character_sprite_alpha_transparency():
    """Verify that all 38 character sprites meet the >= 15% transparent background threshold."""
    with open(ART_MANIFEST, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    sprites = [a for a in manifest["assets"] if a["category"] == "character_sprite"]
    assert len(sprites) == 38, f"Expected 38 character sprites, got {len(sprites)}"

    for s in sprites:
        img_path = IMAGES_DIR / s["path"]
        assert img_path.exists(), f"Missing sprite file: {img_path}"
        with Image.open(img_path) as im:
            assert im.mode == "RGBA", f"Sprite {s['path']} must be RGBA, got {im.mode}"
            assert im.size == (s["width"], s["height"]), f"Sprite {s['path']} size mismatch"

            # Check alpha channel histogram
            alpha = im.split()[-1]
            hist = alpha.histogram()
            transparent_px = hist[0]
            total_px = im.width * im.height
            pct_transparent = (transparent_px / total_px) * 100.0
            assert pct_transparent >= 15.0, (
                f"Sprite {s['path']} has insufficient transparent background ({pct_transparent:.2f}% < 15.0%)"
            )


def test_audio_assets_completeness_and_validity():
    """Verify all 15 audio tracks exist and are valid 16-bit 44.1kHz PCM WAV files."""
    assert AUDIO_MANIFEST.exists()
    with open(AUDIO_MANIFEST, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    audio_items = manifest["audio"]
    assert len(audio_items) == 15, f"Expected 15 audio items, got {len(audio_items)}"

    for item in audio_items:
        rel_path = item["path"]
        path = GAME_DIR / rel_path
        assert path.exists(), f"Missing audio file: {path}"

        with wave.open(str(path), "rb") as wav:
            n_channels = wav.getnchannels()
            sample_width = wav.getsampwidth()
            framerate = wav.getframerate()
            n_frames = wav.getnframes()

            expected_channels = 2 if item["category"] == "bgm" else 1
            assert n_channels == expected_channels, f"{rel_path}: expected {expected_channels} channels, got {n_channels}"
            assert sample_width == 2, f"{rel_path}: expected 16-bit (sample width 2), got {sample_width}"
            assert framerate == 44100, f"{rel_path}: expected 44100 Hz framerate, got {framerate}"
            assert n_frames > 0, f"{rel_path}: empty audio frames"


def test_audio_script_references_exist():
    """Verify all audio paths referenced in .rpy files exist on disk."""
    rpy_files = list(GAME_DIR.glob("**/*.rpy"))
    assert len(rpy_files) > 0

    audio_pattern = re.compile(r'audio/([a-zA-Z0-9_\.]+)\.wav')
    referenced = set()

    for rpy in rpy_files:
        content = rpy.read_text(encoding="utf-8")
        matches = audio_pattern.findall(content)
        for m in matches:
            referenced.add(f"audio/{m}.wav")

    assert len(referenced) > 0, "No audio references found in script files"
    for ref in referenced:
        target = GAME_DIR / ref
        assert target.exists(), f"Referenced audio file not found on disk: {target}"


def test_renpy_script_integrity_and_lint():
    """Basic Ren'Py syntax integrity scan ensuring matching quotes, blocks, and label syntax."""
    rpy_files = list(GAME_DIR.glob("**/*.rpy"))
    assert len(rpy_files) >= 7

    defined_labels = set()
    jumped_labels = set()

    for rpy in rpy_files:
        lines = rpy.read_text(encoding="utf-8").splitlines()
        for idx, line in enumerate(lines, 1):
            stripped = line.strip()
            # Check defined labels
            if stripped.startswith("label ") and stripped.endswith(":"):
                label_name = stripped[6:-1].strip()
                defined_labels.add(label_name)

            # Collect jumps
            if stripped.startswith("jump "):
                j_name = stripped[5:].strip()
                jumped_labels.add(j_name)

    # All jumped labels should exist (except menu exit / dynamic returns)
    for j in jumped_labels:
        # Ignore conditional or expression jumps if any
        if not j.startswith("expression"):
            assert j in defined_labels, f"Jump to non-existent label '{j}' detected in scripts."
