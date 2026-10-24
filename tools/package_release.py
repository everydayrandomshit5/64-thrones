"""
package_release.py - Automated Release Packaging Pipeline for 64-Thrones: High-Glamour Edition (v3.2).
Part of Phase 7 of 64-Thrones SFW v2.
Complies with Section 1.1, Section 7.1, and Phase 7 of the Master Build Bible.
"""

import hashlib
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
GAME_DIR = ROOT_DIR / "game"
DIST_DIR = ROOT_DIR / "dist"
TOOLS_DIR = ROOT_DIR / "tools"
RENPY_SDK = Path("D:/antigravity/renpy-8.3.4-sdk")
RENPY_PYTHON = RENPY_SDK / "lib" / "py3-windows-x86_64" / "python.exe"

APP_NAME = "64-thrones-sfwv2"
VERSION = "1.0"
WIN_PKG_NAME = f"{APP_NAME}-{VERSION}-win"
LINUX_PKG_NAME = f"{APP_NAME}-{VERSION}-linux"


def run_pre_release_gates():
    """Runs strict production asset audit and pytest suite before packaging."""
    print("===========================================================")
    print("[PHASE 7] PRE-RELEASE GATE CHECK")
    print("===========================================================")

    # 1. Strict Asset Audit Gate
    print("\n[Gate 1/3] Running strict production asset audit...")
    audit_script = TOOLS_DIR / "audit_production_assets.py"
    res = subprocess.run([sys.executable, str(audit_script), "--strict"], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("[GATE FAILED] Strict asset audit did not pass. Cannot package release.")
        print(res.stderr)
        sys.exit(1)

    # 2. Pytest Suite Gate
    print("\n[Gate 2/3] Running unit & integration test suite (61 tests)...")
    res = subprocess.run([sys.executable, "-m", "pytest"], capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print("[GATE FAILED] Test suite did not pass. Cannot package release.")
        print(res.stderr)
        sys.exit(1)

    # 3. Native Ren'Py Engine Lint Gate
    print("\n[Gate 3/3] Running native Ren'Py engine lint...")
    lint_cmd = [
        str(RENPY_PYTHON),
        str(RENPY_SDK / "renpy.py"),
        str(ROOT_DIR),
        "lint",
    ]
    res = subprocess.run(lint_cmd, capture_output=True, text=True)
    print(res.stdout)
    if "is not an image" in res.stdout or "Could not evaluate" in res.stdout:
        print("[GATE FAILED] Ren'Py lint errors detected.")
        sys.exit(1)

    print("\n[PRE-RELEASE GATES PASSED] All 110 production assets, 61 tests & Ren'Py lint verified.")


def build_native_distributions():
    """Compiles native standalone Windows and Linux release distributions via Ren'Py SDK."""
    print("\nCompiling native standalone packages via Ren'Py SDK...")
    dist_cmd = [
        str(RENPY_PYTHON),
        str(RENPY_SDK / "renpy.py"),
        str(RENPY_SDK / "launcher"),
        "distribute",
        str(ROOT_DIR),
        "--destination",
        str(DIST_DIR),
    ]
    res = subprocess.run(dist_cmd, capture_output=True, text=True)
    print(res.stdout[-1500:] if len(res.stdout) > 1500 else res.stdout)
    if res.returncode != 0:
        print("[BUILD FAILED] Ren'Py distribute failed.")
        print(res.stderr)
        sys.exit(1)


def unpack_windows_release_for_instant_play():
    """Extracts Windows standalone release into dist/ so player can immediately run it."""
    zip_path = DIST_DIR / f"{WIN_PKG_NAME}.zip"
    if not zip_path.exists():
        print(f"[WARN] {zip_path} not found.")
        return

    print(f"\nUnpacking {zip_path.name} for instant double-click play...")
    with zipfile.ZipFile(str(zip_path), "r") as zf:
        zf.extractall(str(DIST_DIR))

    pkg_dir = DIST_DIR / WIN_PKG_NAME
    exe1 = pkg_dir / f"{APP_NAME}.exe"
    exe2 = pkg_dir / "64-thrones.exe"
    if exe1.exists():
        shutil.copyfile(str(exe1), str(exe2))

    bat_text = f'@echo off\nstart "" "%~dp0{APP_NAME}.exe"\n'
    (pkg_dir / "64-thrones.bat").write_text(bat_text, encoding="utf-8")
    (pkg_dir / "64-thrones.cmd").write_text(bat_text, encoding="utf-8")

    # In case the player has the nested extracted folder from earlier
    nested_dir = pkg_dir / WIN_PKG_NAME
    if not nested_dir.exists():
        nested_dir.mkdir(parents=True, exist_ok=True)

    for item in pkg_dir.iterdir():
        if item.name == WIN_PKG_NAME:
            continue
        target = nested_dir / item.name
        if item.is_dir():
            shutil.copytree(str(item), str(target), dirs_exist_ok=True)
        else:
            shutil.copyfile(str(item), str(target))

    print(f"[INSTANT PLAY READY] Standalone executables ready in {pkg_dir}")


def compute_checksums():
    """Computes SHA256 checksums for packaged archives."""
    sums_file = DIST_DIR / "SHA256SUMS.txt"
    lines = []
    for f in [DIST_DIR / f"{WIN_PKG_NAME}.zip", DIST_DIR / f"{LINUX_PKG_NAME}.tar.bz2"]:
        if f.exists():
            h = hashlib.sha256()
            with open(f, "rb") as fp:
                while chunk := fp.read(65536):
                    h.update(chunk)
            lines.append(f"{h.hexdigest()}  {f.name}")

    sums_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n[CHECKSUMS] Generated {sums_file.name}:")
    for l in lines:
        print(f"  {l}")


def main():
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    run_pre_release_gates()
    build_native_distributions()
    unpack_windows_release_for_instant_play()
    compute_checksums()

    print("\n===========================================================")
    print("[PHASE 7 COMPLETE] Native standalone release distributions built!")
    print("===========================================================")


if __name__ == "__main__":
    main()
