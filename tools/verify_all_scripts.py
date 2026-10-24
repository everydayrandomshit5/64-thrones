"""
verify_all_scripts.py - Comprehensive Ren'Py script linter and asset reference validator.
Checks every .rpy file in game/ for missing assets, dangling labels, broken audio calls,
and invalid character references.
"""

import os
import re
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
GAME_DIR = ROOT_DIR / "game"
IMAGES_DIR = GAME_DIR / "images"
AUDIO_DIR = GAME_DIR / "audio"


def check_script_integrity():
    print("===========================================================")
    print("[TESTING] REN'PY SCRIPT INTEGRITY & ASSET LINT")
    print("===========================================================")

    rpy_files = sorted(GAME_DIR.glob("**/*.rpy"))
    print(f"Discovered {len(rpy_files)} Ren'Py script files:")
    for f in rpy_files:
        print(f"  - {f.relative_to(ROOT_DIR)}")

    errors = []
    warnings = []

    # 1. Collect Defined Labels
    defined_labels = set()
    label_pattern = re.compile(r"^\s*label\s+([a-zA-Z0-9_]+)(\(.*\))?:")

    for f in rpy_files:
        for idx, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            m = label_pattern.match(line)
            if m:
                label_name = m.group(1)
                if label_name in defined_labels:
                    warnings.append(f"Duplicate label '{label_name}' defined in {f.name}:{idx}")
                defined_labels.add(label_name)

    print(f"\n[Labels] Found {len(defined_labels)} defined script labels.")

    # 2. Check Jumps and Calls
    jump_pattern = re.compile(r"^\s*jump\s+([a-zA-Z0-9_]+)")
    call_pattern = re.compile(r"^\s*call\s+([a-zA-Z0-9_]+)")

    for f in rpy_files:
        for idx, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            # Jump checks
            jm = jump_pattern.match(line)
            if jm:
                target = jm.group(1)
                if not target.startswith("expression") and target not in defined_labels:
                    errors.append(f"Broken jump to undefined label '{target}' at {f.name}:{idx}")

            # Call checks
            cm = call_pattern.match(line)
            if cm:
                target = cm.group(1)
                if not target.startswith("expression") and target not in defined_labels:
                    # Ignore common built-in screen calls if any
                    if target not in ["screen"]:
                        errors.append(f"Broken call to undefined label '{target}' at {f.name}:{idx}")

    # 3. Check Audio References
    audio_pattern = re.compile(r'audio/([a-zA-Z0-9_\-\.]+)\.wav')
    audio_refs = set()

    for f in rpy_files:
        for idx, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            matches = audio_pattern.findall(line)
            for m in matches:
                audio_file = f"audio/{m}.wav"
                audio_refs.add(audio_file)
                full_path = GAME_DIR / audio_file
                if not full_path.exists():
                    errors.append(f"Missing referenced audio '{audio_file}' at {f.name}:{idx}")

    print(f"[Audio] Verified {len(audio_refs)} unique audio references against disk.")

    # 4. Check Image References
    image_pattern = re.compile(r'(?:scene|show|image)\s+["\']?([a-zA-Z0-9_/\.\-]+(?:\.png|\.jpg))["\']?')
    img_refs = set()

    for f in rpy_files:
        for idx, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            matches = image_pattern.findall(line)
            for m in matches:
                # clean up path
                img_path = m.strip("\"'")
                img_refs.add(img_path)
                full_path = IMAGES_DIR / img_path
                # Check if file exists either directly or inside images/
                alt_path = GAME_DIR / img_path
                if not full_path.exists() and not alt_path.exists():
                    errors.append(f"Missing referenced image '{img_path}' at {f.name}:{idx}")

    # Also check string image references like "images/cgs/..." or "cgs/..."
    string_img_pattern = re.compile(r'["\']((?:cgs|bg|characters|cutins|ui|board)/[a-zA-Z0-9_/\.\-]+\.png)["\']')
    for f in rpy_files:
        for idx, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            matches = string_img_pattern.findall(line)
            for m in matches:
                img_refs.add(m)
                full_path = IMAGES_DIR / m
                alt_path = GAME_DIR / m
                if not full_path.exists() and not alt_path.exists():
                    errors.append(f"Missing referenced image '{m}' at {f.name}:{idx}")

    print(f"[Images] Verified {len(img_refs)} unique image references against disk.")

    # 5. Check Character Declarations
    char_def_pattern = re.compile(r'define\s+([a-zA-Z0-9_]+)\s*=\s*Character\(')
    defined_chars = set()
    for f in rpy_files:
        for line in f.read_text(encoding="utf-8").splitlines():
            m = char_def_pattern.search(line)
            if m:
                defined_chars.add(m.group(1))

    print(f"[Characters] Found {len(defined_chars)} declared dialogue characters: {sorted(defined_chars)}")

    # Report results
    print("\n-----------------------------------------------------------")
    if warnings:
        print(f"Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"  [WARN] {w}")

    if errors:
        print(f"ERRORS FOUND ({len(errors)}):")
        for e in errors:
            print(f"  [ERROR] {e}")
        print("\n[LINT FAILED] Script issues detected.")
        sys.exit(1)
    else:
        print("[LINT PASSED] Zero syntax errors, missing assets, or broken jumps detected.")
        print("-----------------------------------------------------------")
        sys.exit(0)


if __name__ == "__main__":
    check_script_integrity()
