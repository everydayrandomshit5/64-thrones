"""
Unit tests for game/core/match_session.py.
Verifies all 4 Sovereign Spells, python-chess null-move guards, Aegis Ward bypass rules,
and FEN rollback serialization (Section 5.3 of the Master Build Bible).
"""

import pytest
import chess

from game.core.match_session import MatchSession


def test_initial_match_session():
    """Verify MatchSession initialization with Dawn faction and default aether."""
    session = MatchSession(player_faction="dawn", boss_profile_id="reckless_vanguard")
    assert session.player_faction == "dawn"
    assert session.player_color == chess.WHITE
    assert session.boss_color == chess.BLACK
    assert session.aether == 3
    assert session.max_aether == 3
    assert session.is_player_turn is True
    assert len(session.fen_history_list) == 1
    assert session.warded_square is None
    assert session.oracle_active is False


def test_chrono_pulse_execution_and_rollback():
    """Verify Chrono-Pulse tactical rewind (Cost: 1 Aether)."""
    session = MatchSession(player_faction="dawn", starting_aether=3)
    initial_fen = session.current_fen

    # Round 1:
    # Player moves e2e4
    res_p1 = session.push_player_move(chess.Move.from_uci("e2e4"))
    assert res_p1["success"] is True

    # Boss moves e7e5
    res_b1 = session.push_boss_move(apply_noise=False)
    assert res_b1["success"] is True

    # It's player's turn again, history length is 3 (initial + 2 half-moves)
    assert session.is_player_turn is True
    assert len(session.fen_history_list) == 3
    assert session.can_cast_chrono_pulse() is True

    # Cast Chrono-Pulse
    pulse_res = session.cast_chrono_pulse()
    assert pulse_res["success"] is True
    assert pulse_res["remaining_aether"] == 2
    assert session.aether == 2
    # Board is restored back to initial position!
    assert session.current_fen == initial_fen
    assert session.board.fen() == initial_fen
    assert session.board.piece_at(chess.E2).piece_type == chess.PAWN
    assert session.board.piece_at(chess.E4) is None
    assert len(session.fen_history_list) == 1

    # Cannot cast Chrono-Pulse again because history is back to length 1
    assert session.can_cast_chrono_pulse() is False


def test_chrono_pulse_guards():
    """Verify Chrono-Pulse cannot be cast without sufficient history or aether."""
    # New game: cannot cast on Turn 1 (no moves made yet)
    session = MatchSession(starting_aether=3)
    assert session.can_cast_chrono_pulse() is False

    # Empty aether
    session_no_aether = MatchSession(starting_aether=0)
    assert session_no_aether.can_cast_chrono_pulse() is False


def test_oracle_gaze_execution():
    """Verify Oracle's Gaze foresight spell (Cost: 1 Aether)."""
    session = MatchSession(player_faction="dawn", starting_aether=3)
    assert session.can_cast_oracle_gaze() is True

    res = session.cast_oracle_gaze()
    assert res["success"] is True
    assert session.aether == 2
    assert session.oracle_active is True
    assert session.oracle_prediction is not None
    assert "from_square" in session.oracle_prediction
    assert "to_square" in session.oracle_prediction
    assert "uci" in session.oracle_prediction

    # Cannot cast while already active
    assert session.can_cast_oracle_gaze() is False

    # Making a player move clears oracle state
    session.push_player_move(chess.Move.from_uci("e2e4"))
    assert session.oracle_active is False
    assert session.oracle_prediction is None


def test_aegis_ward_protection():
    """Verify Aegis Ward (Cost: 2 Aether) filters enemy captures on warded piece."""
    # Setup board: White Queen on d4, Black Rook on d8.
    # Turn: White
    fen = "3r4/8/8/8/3Q4/8/8/4K2k w - - 0 1"
    session = MatchSession(player_faction="dawn", initial_fen=fen, starting_aether=3)

    # Ward the Queen on d4
    assert session.can_cast_aegis_ward(chess.D4) is True
    res = session.cast_aegis_ward(chess.D4)
    assert res["success"] is True
    assert session.aether == 1
    assert session.warded_square == chess.D4

    # Player makes quiet King move
    session.push_player_move(chess.Move.from_uci("e1f1"))

    # Now it is Black's turn. The Black Rook on d8 would normally be able to capture d8d4.
    # Verify that get_filtered_legal_moves() filters out d8d4!
    filtered_moves = session.get_filtered_legal_moves()
    capturing_move = chess.Move.from_uci("d8d4")
    assert capturing_move not in filtered_moves

    # Opponent makes their legal non-capturing move
    res_b = session.push_boss_move(apply_noise=False)
    assert res_b["success"] is True
    assert res_b["move"] != "d8d4"

    # Queen was saved! Queen is still on d4
    assert session.board.piece_at(chess.D4) is not None
    assert session.board.piece_at(chess.D4).piece_type == chess.QUEEN

    # Ward expires after 1 enemy turn
    assert session.warded_square is None


def test_aegis_ward_bypass_on_check():
    """
    Verify Wrapper Safety Rule (Section 5.3):
    If opponent is in check, Aegis immunity is bypassed so python-chess evasion rules stay 100% valid.
    """
    # Setup: White Queen on d4 checks Black King on d8!
    # Black King has only one move: capture Queen on d4!
    # If Aegis Ward didn't bypass, Black would have 0 moves (false stalemate/illegal check evasion).
    fen = "3k4/8/8/8/3Q4/8/8/4K3 w - - 0 1"
    session = MatchSession(player_faction="dawn", initial_fen=fen, starting_aether=3)

    # Ward the Queen
    session.cast_aegis_ward(chess.D4)

    # Player delivers check with Queen to d7
    session.push_player_move(chess.Move.from_uci("d4d7"))

    # Now it's Black's turn. Black King on d8 is in check by Queen on d7.
    # Even if d7 was warded, because Black is in check, get_filtered_legal_moves bypasses immunity!
    filtered = session.get_filtered_legal_moves()
    assert len(filtered) > 0
    # King must be able to evade check (e.g. kxd7)
    assert chess.Move.from_uci("d8d7") in filtered


def test_aegis_ward_king_guard():
    """Verify King cannot be targeted with Aegis Ward."""
    session = MatchSession(player_faction="dawn", starting_aether=3)
    # White King is on e1
    assert session.can_cast_aegis_ward(chess.E1) is False


def test_marshals_advance_execution():
    """
    Verify Marshal's Advance (Cost: 2 Aether - Section 5.3):
    Pushes 1-step pawn advance, then pushes Move.null(), returning turn to player!
    """
    session = MatchSession(player_faction="dawn", starting_aether=3)

    # Friendly pawn on e2
    assert session.can_cast_marshals_advance(chess.E2) is True

    advance_res = session.cast_marshals_advance(chess.E2)
    assert advance_res["success"] is True
    assert advance_res["remaining_aether"] == 1
    assert session.aether == 1

    # Pawn moved to e3
    assert session.board.piece_at(chess.E2) is None
    assert session.board.piece_at(chess.E3).piece_type == chess.PAWN

    # Turn is STILL player's turn! (Because Move.null() passed the turn back)
    assert session.is_player_turn is True
    assert session.board.turn == chess.WHITE

    # Player can immediately make another move!
    res_move = session.push_player_move(chess.Move.from_uci("d2d4"))
    assert res_move["success"] is True


def test_marshals_advance_guards():
    """Verify Marshal's Advance guard clauses."""
    # 1. Blocked pawn cannot advance
    # White pawn on e4, Black pawn on e5
    fen_blocked = "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
    session_blocked = MatchSession(initial_fen=fen_blocked, starting_aether=3)
    assert session_blocked.can_cast_marshals_advance(chess.E4) is False

    # 2. Cannot cast while in check
    # White King on e1 in check by Black Queen on e2
    fen_check = "rnb1kbnr/pppp1ppp/8/8/8/8/PPPPqPPP/RNB1KBNR w KQkq - 0 1"
    session_check = MatchSession(initial_fen=fen_check, starting_aether=3)
    assert session_check.can_cast_marshals_advance(chess.A2) is False

    # 3. Cannot advance to promotion rank (rank 7 for White)
    fen_pawn7 = "8/4P3/8/8/8/8/8/4K2k w - - 0 1"
    session_pawn7 = MatchSession(initial_fen=fen_pawn7, starting_aether=3)
    assert session_pawn7.can_cast_marshals_advance(chess.E7) is False


def test_session_serialization_and_reconstruction():
    """
    Verify FEN + History stack serialization for Ren'Py save / rollback (Section 0).
    Reconstructs cleanly without corrupting Board or spell states.
    """
    session = MatchSession(player_faction="dawn", starting_aether=3)
    session.push_player_move(chess.Move.from_uci("e2e4"))
    session.push_boss_move(apply_noise=False)

    # Cast Oracle's Gaze
    session.cast_oracle_gaze()

    # Serialize to primitive dictionary
    data = session.to_dict()
    assert isinstance(data, dict)
    assert isinstance(data["current_fen"], str)
    assert isinstance(data["fen_history_list"], list)
    assert data["aether"] == 2
    assert data["oracle_active"] is True

    # Reconstruct new MatchSession from dictionary
    loaded_session = MatchSession.from_dict(data)
    assert loaded_session.player_faction == "dawn"
    assert loaded_session.current_fen == session.current_fen
    assert loaded_session.board.fen() == session.board.fen()
    assert loaded_session.aether == 2
    assert loaded_session.oracle_active is True
    assert len(loaded_session.fen_history_list) == len(session.fen_history_list)

    # Verify gameplay continues seamlessly on reconstructed session
    res = loaded_session.push_player_move(chess.Move.from_uci("g1f3"))
    assert res["success"] is True
