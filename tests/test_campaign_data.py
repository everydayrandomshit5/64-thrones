"""
Unit tests for game data architecture and campaign integrity (Phase 2).
Validates characters.json, chapters.json, banter.json, art_manifest.json, and concord logic.
"""

import json
from pathlib import Path
import pytest
import chess
from PIL import Image

from game.core.story_ai import BOSS_PROFILES

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "game" / "data"
IMAGES_DIR = ROOT_DIR / "game" / "images"
MANIFEST_PATH = ROOT_DIR / "tools" / "art_manifest.json"


def test_characters_json_schema_and_completeness():
    """Verify characters.json structure, 12 characters, and asset links."""
    char_file = DATA_DIR / "characters.json"
    assert char_file.exists(), "characters.json does not exist"

    with open(char_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "factions" in data
    assert "dawn" in data["factions"]
    assert "dusk" in data["factions"]

    chars = data["characters"]
    assert len(chars) == 12, f"Expected 12 characters, found {len(chars)}"

    dawn_chars = [c for c in chars if c["faction"] == "dawn"]
    dusk_chars = [c for c in chars if c["faction"] == "dusk"]
    assert len(dawn_chars) == 6
    assert len(dusk_chars) == 6

    for c in chars:
        cid = c["id"]
        assert "name" in c and len(c["name"]) > 0
        assert "title" in c
        assert "role" in c
        assert "piece_type" in c
        assert "gender" in c
        assert "visuals" in c
        assert "wardrobe" in c
        assert "lore" in c and "secret" in c["lore"]
        assert "bond_arc" in c
        assert all(f"rank_{i}" in c["bond_arc"] for i in range(1, 5))

        # Wardrobe states A, B, C
        w = c["wardrobe"]
        assert "state_a_battle" in w
        assert "state_b_worn" in w
        assert "state_c_camp" in w

        # Sprite paths exist on disk
        sp = c["sprite_paths"]
        for s_key in ["state_a_battle", "state_b_worn", "state_c_camp"]:
            rel_path = sp[s_key]
            full_path = IMAGES_DIR / rel_path
            assert full_path.exists(), f"Sprite file missing: {full_path}"

    # Vanguard Leads must have state_d_promoted
    tamsin = next(c for c in chars if c["id"] == "dawn_pawn_lead")
    assert "state_d_promoted" in tamsin["wardrobe"]
    assert (IMAGES_DIR / tamsin["sprite_paths"]["state_d_promoted"]).exists()

    sorrel = next(c for c in chars if c["id"] == "dusk_pawn_lead")
    assert "state_d_promoted" in sorrel["wardrobe"]
    assert (IMAGES_DIR / sorrel["sprite_paths"]["state_d_promoted"]).exists()


def test_chapters_json_and_concord_logic():
    """Verify chapters.json, FEN validity, Boss AI mapping, and Concord logic."""
    chap_file = DATA_DIR / "chapters.json"
    assert chap_file.exists(), "chapters.json does not exist"

    with open(chap_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "prologue" in data
    assert len(data["prologue"]["scenes"]) == 3
    assert len(data["prologue"]["branch_choice"]["options"]) == 2

    dawn_chapters = data["dawn_campaign"]
    dusk_chapters = data["dusk_campaign"]
    assert len(dawn_chapters) == 8
    assert len(dusk_chapters) == 8

    # Validate each chapter in both campaigns
    for idx, chap in enumerate(dawn_chapters, 1):
        assert chap["chapter"] == idx
        # Validate FEN loads in python-chess
        board = chess.Board(chap["initial_fen"])
        assert board.is_valid()
        # Validate AI profile exists in story_ai.BOSS_PROFILES
        assert chap["boss_profile"] in BOSS_PROFILES
        assert "objective" in chap
        assert "concord_trigger" in chap
        assert chap.get("concord_points", 0) >= 1

    for idx, chap in enumerate(dusk_chapters, 1):
        assert chap["chapter"] == idx
        board = chess.Board(chap["initial_fen"])
        assert board.is_valid()
        assert chap["boss_profile"] in BOSS_PROFILES
        assert "objective" in chap
        assert "concord_trigger" in chap

    # Validate Grand Finale
    gf = data["grand_finale"]
    assert gf["boss_elo"] == 800
    assert gf["special_rules"]["allied_advisors"] == 4
    assert gf["special_rules"]["starting_aether"] == 5

    # Validate 8 Endings
    endings = data["endings"]
    assert len(endings) == 8
    ending_ids = [e["id"] for e in endings]
    assert "ending_true_concord" in ending_ids
    assert "ending_solar_dominance" in ending_ids
    assert "ending_umbral_ascendancy" in ending_ids
    assert "ending_abyssal_breach" in ending_ids


def test_banter_json_integrity():
    """Verify banter.json contains battle dialogue for all required roles."""
    banter_file = DATA_DIR / "banter.json"
    assert banter_file.exists(), "banter.json does not exist"

    with open(banter_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "advisor_callouts" in data
    adv = data["advisor_callouts"]
    for role in ["dawn_queen", "dusk_queen", "dawn_rook", "dusk_rook", "dawn_bishop", "dusk_bishop"]:
        assert role in adv

    # All 12 characters have worn state reactions
    worn = data["worn_state_reactions"]
    assert len(worn) == 12

    # Promotion callouts
    assert "dawn_pawn_lead" in data["promotion_callouts"]
    assert "dusk_pawn_lead" in data["promotion_callouts"]

    # All 4 spells
    spells = data["spells"]
    assert all(k in spells for k in ["chrono_pulse", "oracle_gaze", "aegis_ward", "marshals_advance"])


def test_art_manifest_and_placeholders_verification():
    """Verify art_manifest.json contains exactly 110 assets and all placeholders exist."""
    assert MANIFEST_PATH.exists()

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assets = manifest["assets"]
    assert len(assets) == 110, f"Expected 110 assets, got {len(assets)}"

    # Sample check metadata and image headers
    for item in assets:
        path = IMAGES_DIR / item["path"]
        assert path.exists(), f"Placeholder file not found: {path}"
        with Image.open(path) as im:
            assert im.size == (item["width"], item["height"]), f"Wrong size for {path}"
            assert im.text.get("ASSET_STATUS") == "DEV_PLACEHOLDER"
