"""
Unit tests for Phase 4 Narrative & Campaign Implementation (game/story/*.rpy).
Verifies Prologue, Dawn Campaign (Ch 1-8), Dusk Campaign (Ch 1-8),
Camp Fellowship scenes, Concord branching, and all 8 Endings & Epilogues.
"""

from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
STORY_DIR = ROOT_DIR / "game" / "story"


def test_all_story_files_exist():
    """Verify all 4 required narrative script files exist in game/story/."""
    required = [
        "prologue.rpy",
        "campaign_dawn.rpy",
        "campaign_dusk.rpy",
        "finale_endings.rpy",
    ]
    for filename in required:
        p = STORY_DIR / filename
        assert p.exists(), f"Missing story script: {p}"
        assert p.stat().st_size > 2000, f"Story script {filename} is unexpectedly small"


def test_prologue_scenes_and_faction_branch():
    """Verify prologue.rpy includes all 3 Ashgate scenes, CGs 1 & 2, and faction choice."""
    text = (STORY_DIR / "prologue.rpy").read_text(encoding="utf-8")
    assert "label prologue_start:" in text
    assert "cgs/cg_01_ashgate_climax.png" in text
    assert "cgs/cg_02_monoliths_rise.png" in text
    assert "jump campaign_dawn_start" in text
    assert "jump campaign_dusk_start" in text


def test_dawn_campaign_chapters_and_fellowship():
    """Verify campaign_dawn.rpy contains Chapters 1-8, Concord triggers, and Fellowship dialogues."""
    text = (STORY_DIR / "campaign_dawn.rpy").read_text(encoding="utf-8")
    for ch in range(1, 9):
        assert f"label dawn_ch{ch}_start:" in text, f"Missing dawn_ch{ch}_start label"

    assert "persistent.concord_points += 1" in text
    assert "persistent.concord_points >= 3" in text
    assert "jump grand_finale_unbroken_concord" in text
    assert "jump ending_solar_dominance" in text
    assert "label dawn_camp_fellowship_dialogue(" in text
    assert "call dawn_camp_fellowship_dialogue(" in text
    assert "initial_warded_square=init_ward" in text
    assert "evaluate_chapter_objective(" in text
    assert "session_snapshot = current_session.to_dict()" in text
    assert "show image " not in text

    for cid in ["dawn_queen", "dawn_bishop", "dawn_knight", "dawn_pawn_lead", "dawn_rook", "dawn_king"]:
        assert cid in text


def test_dusk_campaign_chapters_and_fellowship():
    """Verify campaign_dusk.rpy contains Chapters 1-8, Concord triggers, and Fellowship dialogues."""
    text = (STORY_DIR / "campaign_dusk.rpy").read_text(encoding="utf-8")
    for ch in range(1, 9):
        assert f"label dusk_ch{ch}_start:" in text, f"Missing dusk_ch{ch}_start label"

    assert "persistent.concord_points += 1" in text
    assert "persistent.concord_points >= 3" in text
    assert "jump grand_finale_unbroken_concord" in text
    assert "jump ending_umbral_ascendancy" in text
    assert "label dusk_camp_fellowship_dialogue(" in text
    assert "call dusk_camp_fellowship_dialogue(" in text
    assert "initial_warded_square=init_ward" in text
    assert "evaluate_chapter_objective(" in text
    assert "session_snapshot = current_session.to_dict()" in text
    assert "show image " not in text

    for cid in ["dusk_queen", "dusk_bishop", "dusk_knight", "dusk_pawn_lead", "dusk_rook", "dusk_king"]:
        assert cid in text


def test_finale_and_all_eight_endings():
    """Verify finale_endings.rpy implements The Unbroken Concord and all 8 endings."""
    text = (STORY_DIR / "finale_endings.rpy").read_text(encoding="utf-8")
    required_labels = [
        "label grand_finale_unbroken_concord:",
        "label ending_true_concord:",
        "label ending_solar_dominance:",
        "label ending_umbral_ascendancy:",
        "label ending_abyssal_breach:",
        "label epilogue_lysandra:",
        "label epilogue_nyssara:",
        "label epilogue_seers:",
        "label epilogue_vanguard:",
    ]
    for lbl in required_labels:
        assert lbl in text, f"Missing finale/ending label: {lbl}"

    assert "cgs/cg_10_true_concord_finale.png" in text
    assert "starting_aether=5" in text
    assert "max_aether=5" in text
    assert "mark_ending_completed(" in text
    assert "show image " not in text


def test_dusk_finale_and_chapter_objectives_logic():
    """Verify Dusk Grand Finale turn-1 playability, Ch 6 Rook Aegis Ward, and Ch 1-8 objectives."""
    import chess
    from game.core.match_session import MatchSession
    from game.core.story_ai import get_war_council_advice

    # 1. Dusk Grand Finale session must allow player moves without softlocking
    dusk_gf_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR b KQkq - 0 1"
    session_dusk_gf = MatchSession(
        player_faction="dusk",
        boss_profile_id="grand_command",
        initial_fen=dusk_gf_fen,
        starting_aether=5,
        max_aether=5,
    )
    assert session_dusk_gf.is_player_turn is True
    assert session_dusk_gf.aether == 5
    advisors = get_war_council_advice(
        session_dusk_gf.board,
        player_faction="dusk",
        legal_moves=session_dusk_gf.get_filtered_legal_moves(),
        include_allied_fourth=True,
        enhanced_char_ids=["dusk_queen"],
    )
    assert len(advisors) == 4
    assert "[Offense:" in advisors[0]["rationale"]

    # 2. Chapter 6 Rook Aegis Ward initialization
    ch6_dawn = MatchSession(player_faction="dawn", initial_warded_square=chess.A1)
    assert ch6_dawn.warded_square == chess.A1
    ch6_dusk = MatchSession(
        player_faction="dusk",
        initial_fen=dusk_gf_fen,
        initial_warded_square=chess.A8,
    )
    assert ch6_dusk.warded_square == chess.A8

    # 3. Chapter 1 midline pawn advance objective
    ch1_session = MatchSession(player_faction="dawn")
    ch1_session.push_player_move(chess.Move.from_uci("e2e4"))
    ch1_session.push_boss_move(apply_noise=False)
    # Advance e4 to e5 (rank 4 in 0-indexed -> past midline)
    if chess.Move.from_uci("e4e5") in ch1_session.get_filtered_legal_moves():
        ch1_session.push_player_move(chess.Move.from_uci("e4e5"))
        assert ch1_session.midline_pawn_advanced is True
        assert ch1_session.evaluate_chapter_objective(1) is True
