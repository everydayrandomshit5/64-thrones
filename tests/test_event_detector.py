"""
Unit tests for game/core/event_detector.py.
Verifies dynamic wardrobe state transitions (state_a_battle <-> state_b_worn),
hysteresis recovery, pawn ascension (state_d_promoted), and cut-in banner triggers (Section 5.4).
"""

import pytest
import chess

from game.core.event_detector import (
    EventDetector,
    calculate_material_delta,
    calculate_side_material,
    is_king_in_check,
)


def test_initial_event_detector():
    """Verify EventDetector starts both commanders in state_a_battle."""
    detector = EventDetector(
        player_char_id="dawn_queen",
        boss_char_id="dusk_queen",
        player_faction="dawn",
    )
    assert detector.player_sprite_state == "state_a_battle"
    assert detector.boss_sprite_state == "state_a_battle"
    assert detector.dawn_pawn_promoted is False
    assert detector.dusk_pawn_promoted is False
    assert len(detector.pending_cutins) == 0


def test_material_delta_calculation():
    """Verify material delta in pawns."""
    # Standard initial board: material is identical, delta = 0.0
    board = chess.Board()
    assert calculate_material_delta(board, chess.WHITE) == 0.0
    assert calculate_material_delta(board, chess.BLACK) == 0.0

    # Remove White Rook (value 500)
    # White material is 500 less (-5.0 pawns)
    board.remove_piece_at(chess.A1)
    assert calculate_material_delta(board, chess.WHITE) == -5.0
    assert calculate_material_delta(board, chess.BLACK) == 5.0


def test_transition_to_worn_on_material_deficit():
    """
    Verify transition to state_b_worn when Delta M <= -2.0 (Section 5.4).
    Also verify cut-in event queueing.
    """
    detector = EventDetector(player_char_id="dawn_queen", boss_char_id="dusk_queen")
    board = chess.Board()

    # Remove 2 White pawns -> Delta M = -2.0
    board.remove_piece_at(chess.A2)
    board.remove_piece_at(chess.B2)

    status = detector.update(board)
    assert status["player_delta_m"] == -2.0
    assert detector.player_sprite_state == "state_b_worn"
    assert status["cutins_triggered"] is True

    cutins = detector.pop_pending_cutins()
    assert len(cutins) == 1
    assert cutins[0]["char_id"] == "dawn_queen"
    assert cutins[0]["banner"] == "cutins/dawn_queen_cutin.png"
    assert cutins[0]["sfx"] == "audio/sfx_armor_shatter.ogg"
    assert cutins[0]["vfx"] == "vpunch"


def test_transition_to_worn_on_check():
    """Verify transition to state_b_worn when King is in check."""
    detector = EventDetector(player_char_id="dawn_queen", boss_char_id="dusk_queen")
    # Scholar's mate attack with check delivered to Black King on e8
    board = chess.Board("rnbqkbnr/ppppp2p/5p2/6pQ/4P3/8/PPPP1PPP/RNB1KBNR b KQkq - 1 3")

    status = detector.update(board)
    assert status["boss_check"] is True
    assert detector.boss_sprite_state == "state_b_worn"

    cutins = detector.pop_pending_cutins()
    assert len(cutins) == 1
    assert cutins[0]["char_id"] == "dusk_queen"


def test_transition_to_worn_on_queen_capture():
    """Verify transition to state_b_worn when side's Queen is captured."""
    detector = EventDetector(player_char_id="dawn_queen", boss_char_id="dusk_queen")
    board = chess.Board()

    # Remove White Queen
    board.remove_piece_at(chess.D1)

    status = detector.update(board)
    assert status["player_queen_lost"] is True
    assert detector.player_sprite_state == "state_b_worn"


def test_hysteresis_recovery():
    """
    Verify Hysteresis Recovery (Section 5.4):
    Recovers to state_a_battle ONLY if not in check, queen intact,
    and material balance returns to Delta M >= 0.0 (does NOT recover at -1.0).
    """
    detector = EventDetector(player_char_id="dawn_queen", boss_char_id="dusk_queen")
    board = chess.Board()

    # Drop White material to -3.0
    board.remove_piece_at(chess.C1)  # Bishop (-3.3 pawns approx)
    detector.update(board)
    assert detector.player_sprite_state == "state_b_worn"
    detector.pop_pending_cutins()

    # Opponent now loses a pawn: Delta M is now -2.3 -> still worn
    board.remove_piece_at(chess.C7)
    detector.update(board)
    assert detector.player_sprite_state == "state_b_worn"

    # Opponent loses another pawn: Delta M is now -1.3 -> STILL worn (hysteresis prevents flicker)
    board.remove_piece_at(chess.D7)
    detector.update(board)
    assert detector.player_sprite_state == "state_b_worn"

    # Opponent loses their Bishop: Delta M returns to 0.0 -> RECOVERS to state_a_battle!
    board.remove_piece_at(chess.C8)
    detector.update(board)
    assert detector.player_sprite_state == "state_a_battle"


def test_vanguard_pawn_promotion():
    """
    Verify Vanguard Lead promotion to state_d_promoted (Solar Ascension / Umbral Coronation).
    """
    detector = EventDetector(player_char_id="dawn_queen", boss_char_id="dusk_queen")

    # Board where White pawn promotes on e8
    board = chess.Board("8/4P3/8/8/8/8/8/4K2k w - - 0 1")
    promo_move = chess.Move.from_uci("e7e8q")
    board.push(promo_move)

    status = detector.update(board, last_move=promo_move)
    assert status["dawn_pawn_promoted"] is True
    assert detector.dawn_pawn_promoted is True
    assert detector.get_character_sprite_state("dawn_pawn_lead") == "state_d_promoted"

    cutins = detector.pop_pending_cutins()
    promoted_events = [c for c in cutins if c["type"] == "ascension"]
    assert len(promoted_events) == 1
    assert promoted_events[0]["char_id"] == "dawn_pawn_lead"
    assert promoted_events[0]["banner"] == "cutins/dawn_pawn_lead_promoted_cutin.png"
    assert promoted_events[0]["sfx"] == "audio/sfx_ascension_fanfare.ogg"


def test_event_detector_serialization():
    """Verify EventDetector serializes and restores cleanly."""
    detector = EventDetector(player_char_id="dawn_queen", boss_char_id="dusk_queen")
    detector.player_sprite_state = "state_b_worn"
    detector.dawn_pawn_promoted = True

    data = detector.to_dict()
    assert data["player_sprite_state"] == "state_b_worn"
    assert data["dawn_pawn_promoted"] is True

    restored = EventDetector.from_dict(data)
    assert restored.player_sprite_state == "state_b_worn"
    assert restored.dawn_pawn_promoted is True
    assert restored.get_character_sprite_state("dawn_pawn_lead") == "state_d_promoted"
