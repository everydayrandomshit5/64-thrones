"""
Unit tests for game/core/story_ai.py.
Verifies centipawn evaluation, 3-Advisor War Council calculations,
strict uniqueness filter, and Boss AI personality profiles (Section 5.1 & 5.2).
"""

import math
import random
import pytest
import chess

from game.core.story_ai import (
    PIECE_VALUES,
    BOSS_PROFILES,
    chebyshev_distance,
    evaluate_c,
    evaluate_k,
    evaluate_d,
    evaluate_r,
    evaluate_f,
    evaluate_g,
    evaluate_move_components,
    score_queen,
    score_warden,
    score_seer,
    score_ally,
    get_war_council_advice,
    select_boss_move,
    predict_boss_move,
    square_to_center_coords,
    get_vector_arrow_transform,
)


def test_piece_values():
    """Verify piece values defined in centipawns."""
    assert PIECE_VALUES[chess.PAWN] == 100
    assert PIECE_VALUES[chess.KNIGHT] == 310
    assert PIECE_VALUES[chess.BISHOP] == 330
    assert PIECE_VALUES[chess.ROOK] == 500
    assert PIECE_VALUES[chess.QUEEN] == 900
    assert PIECE_VALUES[chess.KING] == 0


def test_chebyshev_distance():
    """Verify Chebyshev distance calculation."""
    # e4 to e5: distance 1
    assert chebyshev_distance(chess.E4, chess.E5) == 1
    # a1 to h8: distance 7
    assert chebyshev_distance(chess.A1, chess.H8) == 7
    # c3 to e5: distance 2
    assert chebyshev_distance(chess.C3, chess.E5) == 2


def test_evaluate_c_capture():
    """Verify C(m) capture evaluation."""
    # Board with White pawn on e4, Black pawn on d5
    board = chess.Board("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
    m_capture = chess.Move.from_uci("e4d5")
    m_quiet = chess.Move.from_uci("e4e5")

    assert evaluate_c(board, m_capture) == 100.0
    assert evaluate_c(board, m_quiet) == 0.0

    # Board with White pawn capturing Queen
    board_q = chess.Board("rnb1kbnr/ppp1pppp/8/3q4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
    m_cap_queen = chess.Move.from_uci("e4d5")
    assert evaluate_c(board_q, m_cap_queen) == 900.0


def test_evaluate_k_check():
    """Verify K(m) delivers check bonus (+150)."""
    # Scholar's mate attack: Qh5, Black plays Nc6, then Qxf7# delivers check
    board = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 2 3")
    m_check = chess.Move.from_uci("h5f7")
    m_non_check = chess.Move.from_uci("h5e5")

    assert evaluate_k(board, m_check) == 150.0
    assert evaluate_k(board, m_non_check) == 150.0  # Qxe5+ is also check!
    m_quiet = chess.Move.from_uci("h5h4")
    assert evaluate_k(board, m_quiet) == 0.0


def test_evaluate_d_central_control():
    """Verify D(m) central control (+30 if file in 2..5 and rank in 2..5)."""
    board = chess.Board()
    # e2e4 lands on e4 (file 4, rank 3): in center
    m_center = chess.Move.from_uci("e2e4")
    assert evaluate_d(board, m_center) == 30.0

    # a2a3 lands on a3 (file 0, rank 2): outside center files
    m_flank = chess.Move.from_uci("a2a3")
    assert evaluate_d(board, m_flank) == 0.0

    # e2e2 landing on e2 (rank 1): outside center ranks
    m_b1a3 = chess.Move.from_uci("b1a3")
    assert evaluate_d(board, m_b1a3) == 0.0


def test_evaluate_r_risk_penalty():
    """Verify R(m) risk penalty (-0.8 * moving_piece_value when undefended and attacked)."""
    # White Knight moves into d5 where Black pawn on c6 attacks it, undefended by White
    board = chess.Board("rnbqkbnr/pp2pppp/2p5/8/8/2N5/PPPPPPPP/R1BQKBNR w KQkq - 0 2")
    m_blunder = chess.Move.from_uci("c3d5")
    # Knight value = 310 -> -0.8 * 310 = -248.0
    assert evaluate_r(board, m_blunder) == -248.0

    # Safe move: e2e4 (defended by Queen and Bishop)
    m_safe = chess.Move.from_uci("e2e4")
    assert evaluate_r(board, m_safe) == 0.0


def test_evaluate_f_fork():
    """Verify F(m) tactical fork bonus (+180 for attacking >= 2 high-value pieces)."""
    # White Knight on e5 can jump to c6 or d7 forking Black King and Rook
    board = chess.Board("r3k2r/ppp2ppp/8/4N3/8/8/PPPP1PPP/RNBQK2R w KQkq - 0 1")
    # Move Knight to d7: attacks e8 (King) and c5 / b8 / f8 (Rook)
    # Let's create an explicit fork position:
    # White Knight on e4. Black King on e8, Black Rook on c8.
    board_fork = chess.Board("2r1k2r/2p2ppp/8/8/4N3/8/PPPP1PPP/RNBQK2R w KQkq - 0 1")
    # Knight moves to d6+: checks King on e8, attacks Rook on c8!
    m_fork = chess.Move.from_uci("e4d6")
    assert evaluate_f(board_fork, m_fork) == 180.0

    # Non-fork move
    m_non_fork = chess.Move.from_uci("e4c5")
    assert evaluate_f(board_fork, m_non_fork) == 0.0


def test_evaluate_g_king_safety():
    """Verify G(m) king safety (+120 for castling, move near king, or capturing attacker)."""
    # Castling position
    board_castle = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4")
    m_castle = chess.Move.from_uci("e1g1")
    assert evaluate_g(board_castle, m_castle) == 120.0

    # Move close to King (Chebyshev distance <= 2 from e1)
    # d2d3 ends at d3, King at e1. File dist = 1, rank dist = 2 -> Chebyshev = 2 <= 2
    m_near = chess.Move.from_uci("d2d3")
    assert evaluate_g(board_castle, m_near) == 120.0


def test_advisor_formulas():
    """Verify exact Advisor heuristic formulas."""
    comps = {"C": 100.0, "K": 150.0, "D": 30.0, "R": -80.0, "F": 180.0, "G": 120.0}

    # S_Queen = 1.8*C + 2.0*K + 1.2*D + 0.4*R
    expected_queen = 1.8 * 100 + 2.0 * 150 + 1.2 * 30 + 0.4 * (-80)
    assert score_queen(comps) == expected_queen

    # S_Warden = 1.5*G + 1.0*D + 0.8*C + 2.5*R
    expected_warden = 1.5 * 120 + 1.0 * 30 + 0.8 * 100 + 2.5 * (-80)
    assert score_warden(comps) == expected_warden

    # S_Seer = 2.2*F + 1.4*D + 1.1*C + 1.2*R
    expected_seer = 2.2 * 180 + 1.4 * 30 + 1.1 * 100 + 1.2 * (-80)
    assert score_seer(comps) == expected_seer


def test_war_council_uniqueness():
    """Verify that War Council advisors return 3 strictly unique moves when available."""
    board = chess.Board()
    advice = get_war_council_advice(board, player_faction="dawn")

    assert len(advice) == 3
    moves = [item["move"] for item in advice]
    # Check that all 3 moves are distinct
    assert len(set(moves)) == 3

    roles = [item["role"] for item in advice]
    assert roles == ["queen", "warden", "seer"]

    # Check colors and arrow assets
    assert advice[0]["color"] == "red"
    assert advice[1]["color"] == "blue"
    assert advice[2]["color"] == "violet"

    # Check names
    assert advice[0]["name"] == "Lysandra"
    assert advice[1]["name"] == "Brannoch"
    assert advice[2]["name"] == "Ilyara"


def test_war_council_dusk_faction():
    """Verify advisor naming and assets for Dusk faction (Black)."""
    board = chess.Board()
    # Flip turn to Black
    board.push(chess.Move.from_uci("e2e4"))
    advice = get_war_council_advice(board, player_faction="dusk")

    assert len(advice) == 3
    assert advice[0]["name"] == "Nyssara"
    assert advice[1]["name"] == "Dravok"
    assert advice[2]["name"] == "Veyra"


def test_grand_finale_fourth_advisor():
    """Verify Grand Finale 4th allied advisor arrow."""
    board = chess.Board()
    advice = get_war_council_advice(
        board, player_faction="dawn", include_allied_fourth=True
    )
    assert len(advice) == 4
    assert advice[3]["role"] == "ally"
    assert advice[3]["color"] == "gold"
    assert advice[3]["name"] == "Nyssara"


def test_vector_arrow_transform():
    """Verify Ren'Py ATL coordinate math from Section 6.2."""
    # From e2 (f=4, r=1) to e4 (f=4, r=3) in White orientation
    # Center X(sq) = 640 + f * 80 + 40 = 640 + 320 + 40 = 1000
    # Center Y(sq) = 120 + (7 - r) * 80 + 40
    # For e2 (r=1): 120 + 6 * 80 + 40 = 120 + 480 + 40 = 640
    # For e4 (r=3): 120 + 4 * 80 + 40 = 120 + 320 + 40 = 480
    # dx = 0, dy = -160, length = 160, angle = -90.0 deg
    x1, y1, length, angle = get_vector_arrow_transform(chess.E2, chess.E4, orientation_white=True)
    assert x1 == 1000.0
    assert y1 == 640.0
    assert length == 160.0
    assert angle == -90.0


def test_all_boss_profiles_exist():
    """Verify all 8 Boss AI profiles from Section 5.2 exist with correct parameters."""
    expected_profiles = [
        ("reckless_vanguard", 350, 1, 140.0),
        ("flank_hunter", 420, 1, 110.0),
        ("iron_warden", 480, 1, 90.0),
        ("diagonal_sniper", 540, 1, 75.0),
        ("hollow_raider", 600, 2, 65.0),
        ("regicide_assassin", 650, 2, 50.0),
        ("rival_queen", 700, 2, 35.0),
        ("grand_command", 750, 2, 20.0),
    ]

    for pid, elo, depth, sigma in expected_profiles:
        assert pid in BOSS_PROFILES
        prof = BOSS_PROFILES[pid]
        assert prof.elo == elo
        assert prof.depth == depth
        assert prof.sigma == sigma


def test_deterministic_predict_boss_move():
    """Verify predict_boss_move is deterministic (sigma = 0)."""
    board = chess.Board()
    # Predict multiple times with same position; must return identical move
    m1 = predict_boss_move(board, "reckless_vanguard")
    m2 = predict_boss_move(board, "reckless_vanguard")
    assert m1 is not None
    assert m1 == m2


def test_reckless_vanguard_prefers_pawns():
    """Verify reckless_vanguard aggressively prioritizes pawn pushes."""
    board = chess.Board()
    # At start, reckless vanguard with noise=0 should select a pawn push
    move = select_boss_move(board, "reckless_vanguard", apply_noise=False)
    assert move is not None
    piece = board.piece_at(move.from_square)
    assert piece is not None
    assert piece.piece_type == chess.PAWN
