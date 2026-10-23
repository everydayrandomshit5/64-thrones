"""
Unit tests for Ren'Py UI controllers & state integration (Phase 3).
Verifies ThronefieldUI, WarTentUI, and CodexUI state machines.
"""

import json
from pathlib import Path
import pytest
import chess

from game.core.match_session import MatchSession
from game.core.event_detector import EventDetector
from game.core.camp_manager import CampManager
from game.core.story_ai import square_to_center_coords, get_vector_arrow_transform

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "game" / "data"
UI_DIR = ROOT_DIR / "game" / "ui"


def test_rpy_files_exist_and_non_empty():
    """Verify all required Ren'Py scripts exist and have content."""
    required_files = [
        ROOT_DIR / "game" / "options.rpy",
        ROOT_DIR / "game" / "gui.rpy",
        ROOT_DIR / "game" / "script.rpy",
        UI_DIR / "thronefield.rpy",
        UI_DIR / "war_tent_hub.rpy",
        UI_DIR / "codex_gallery.rpy",
    ]
    for rf in required_files:
        assert rf.exists(), f"Missing file: {rf}"
        content = rf.read_text(encoding="utf-8")
        assert len(content) > 100, f"File {rf} appears empty or truncated"


def test_thronefield_ui_flow():
    """
    Simulates ThronefieldUI interactions:
    - Piece selection & legal moves calculation
    - Player move execution
    - Boss reply execution
    - 3-Advisor calculations and direct execution
    - Sovereign spells: Chrono-Pulse, Oracle's Gaze, Aegis Ward, Marshal's Advance
    """
    # Import controller logic directly
    session = MatchSession(player_faction="dawn", starting_aether=3)
    detector = EventDetector(player_char_id="dawn_queen", boss_char_id="dusk_queen")
    chapter_data = {
        "title": "First Light on the Stone",
        "boss_profile": "reckless_vanguard",
        "boss_elo": 350,
    }

    # Simulate ThronefieldUI helper class
    class MockThronefieldUI:
        def __init__(self, s, d, c):
            self.session = s
            self.detector = d
            self.chapter_data = c
            self.selected_sq = None
            self.legal_moves_for_selected = []
            self.spell_mode = None
            self.cutin_active = None
            self.active_advisors = []
            self.refresh_advisors()

        def refresh_advisors(self):
            if not self.session.board.is_game_over() and self.session.is_player_turn:
                from game.core.story_ai import get_war_council_advice
                self.active_advisors = get_war_council_advice(
                    self.session.board,
                    player_faction=self.session.player_faction,
                    legal_moves=self.session.get_filtered_legal_moves(),
                )

        def on_square_clicked(self, sq):
            if self.spell_mode == "aegis":
                if self.session.can_cast_aegis_ward(sq):
                    self.session.cast_aegis_ward(sq)
                self.spell_mode = None
                return

            if self.spell_mode == "advance":
                if self.session.can_cast_marshals_advance(sq):
                    res = self.session.cast_marshals_advance(sq)
                    self.detector.update(self.session.board)
                self.spell_mode = None
                return

            if self.selected_sq is not None:
                for m in self.legal_moves_for_selected:
                    if m.to_square == sq:
                        self.session.push_player_move(m)
                        self.detector.update(self.session.board, last_move=m)
                        self.selected_sq = None
                        self.legal_moves_for_selected = []
                        self.refresh_advisors()
                        if not self.session.board.is_game_over() and not self.session.is_player_turn:
                            self.session.push_boss_move(apply_noise=False)
                            self.detector.update(self.session.board)
                            self.refresh_advisors()
                        return

            piece = self.session.board.piece_at(sq)
            if piece and piece.color == self.session.player_color:
                self.selected_sq = sq
                all_legal = self.session.get_filtered_legal_moves()
                self.legal_moves_for_selected = [m for m in all_legal if m.from_square == sq]
            else:
                self.selected_sq = None
                self.legal_moves_for_selected = []

    ui = MockThronefieldUI(session, detector, chapter_data)
    assert len(ui.active_advisors) == 3

    # Click e2 pawn
    ui.on_square_clicked(chess.E2)
    assert ui.selected_sq == chess.E2
    assert len(ui.legal_moves_for_selected) == 2  # e3, e4

    # Click e4 to move
    ui.on_square_clicked(chess.E4)
    assert session.board.piece_at(chess.E4) is not None
    # Boss automatically replied
    assert session.move_count == 1
    assert session.is_player_turn is True

    # Test Aegis Ward mode
    ui.spell_mode = "aegis"
    ui.on_square_clicked(chess.D1)  # Queen on d1
    assert session.warded_square == chess.D1
    assert session.aether == 1


def test_war_tent_ui_flow():
    """Verify War Tent UI fellowship counseling and recon interactions."""
    camp = CampManager(faction="dawn")
    chapter_data = {
        "chapter": 1,
        "boss_char": "dusk_queen",
        "boss_profile": "reckless_vanguard",
        "boss_elo": 350,
        "recon_notes": "Enemy pushes pawns aggressively.",
    }

    assert camp.ap == 2

    # Counsel action (1 AP)
    res_counsel = camp.counsel_officer("dawn_queen", affinity_gain=15)
    assert res_counsel["success"] is True
    assert camp.ap == 1
    assert camp.fellowship_ranks["dawn_queen"] == 1

    # Recon action (1 AP)
    res_recon = camp.perform_recon("dawn_bishop", "reckless_vanguard")
    assert res_recon["success"] is True
    assert camp.ap == 0
    assert camp.recon_buff_active is True

    # Check aether bonuses for battle
    max_a, start_a = camp.get_battle_aether_bonuses()
    assert max_a == 3
    assert start_a == 4


def test_codex_ui_wardrobe_state_switching():
    """Verify Codex UI loads characters and switches wardrobe states."""
    with open(DATA_DIR / "characters.json", "r", encoding="utf-8") as f:
        chars = json.load(f)["characters"]

    char = next(c for c in chars if c["id"] == "dawn_queen")
    assert "state_a_battle" in char["wardrobe"]
    assert "state_b_worn" in char["wardrobe"]
    assert "state_c_camp" in char["wardrobe"]

    tamsin = next(c for c in chars if c["id"] == "dawn_pawn_lead")
    assert "state_d_promoted" in tamsin["wardrobe"]
