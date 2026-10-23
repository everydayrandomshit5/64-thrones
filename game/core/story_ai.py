"""
story_ai.py - Heuristic Chess Engine, 3-Advisor War Council, and Boss AI Profiles.

Part of 64-Thrones: High-Glamour Edition (v3.2).
Complies with Section 5.1 & 5.2 of the Master Build Bible.
"""

from __future__ import annotations

import math
import random
from typing import Any, Callable, Dict, List, Optional, Tuple

import chess

# Centipawn piece values according to Section 5.1
PIECE_VALUES: Dict[chess.PieceType, int] = {
    chess.PAWN: 100,
    chess.KNIGHT: 310,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

# Central board squares (0-indexed files 2..5 and ranks 2..5 => c3 to f6)
CENTER_FILES = {2, 3, 4, 5}
CENTER_RANKS = {2, 3, 4, 5}


def chebyshev_distance(sq1: int, sq2: int) -> int:
    """Computes Chebyshev (chessboard) distance between two squares."""
    return max(
        abs(chess.square_file(sq1) - chess.square_file(sq2)),
        abs(chess.square_rank(sq1) - chess.square_rank(sq2)),
    )


# =============================================================================
# 5.1 HEURISTIC EVALUATION COMPONENTS
# =============================================================================


def evaluate_c(board: chess.Board, move: chess.Move) -> float:
    """C(m): Centipawn value of captured target (or 100 if en passant, else 0)."""
    if board.is_en_passant(move):
        return 100.0
    captured = board.piece_at(move.to_square)
    if captured is not None:
        return float(PIECE_VALUES.get(captured.piece_type, 0))
    return 0.0


def evaluate_k(board: chess.Board, move: chess.Move) -> float:
    """K(m): +150 if move m delivers Check, else 0."""
    return 150.0 if board.gives_check(move) else 0.0


def evaluate_d(board: chess.Board, move: chess.Move) -> float:
    """D(m): Central board control (+30 if to_square in files 2..5 and ranks 2..5, else 0)."""
    f = chess.square_file(move.to_square)
    r = chess.square_rank(move.to_square)
    if f in CENTER_FILES and r in CENTER_RANKS:
        return 30.0
    return 0.0


def evaluate_r(board: chess.Board, move: chess.Move) -> float:
    """
    R(m): Risk penalty (-0.8 * V(moving_piece) if after push,
    to_square is attacked by enemy and NOT defended by friendly, else 0).
    """
    friendly_color = board.turn
    enemy_color = not friendly_color
    moving_piece = board.piece_at(move.from_square)
    moving_val = PIECE_VALUES.get(moving_piece.piece_type, 0) if moving_piece else 0

    board.push(move)
    try:
        is_attacked = board.is_attacked_by(enemy_color, move.to_square)
        is_defended = board.is_attacked_by(friendly_color, move.to_square)
        if is_attacked and not is_defended:
            return -0.8 * float(moving_val)
        return 0.0
    finally:
        board.pop()


def evaluate_f(board: chess.Board, move: chess.Move) -> float:
    """
    F(m): Tactical fork/pin bonus (+180 if after push, the moved piece
    attacks >= 2 enemy pieces of value >= 310 or King; else 0).
    """
    friendly_color = board.turn
    enemy_color = not friendly_color

    board.push(move)
    try:
        attacked_sqs = board.attacks(move.to_square)
        high_value_targets = 0
        for sq in attacked_sqs:
            piece = board.piece_at(sq)
            if piece is not None and piece.color == enemy_color:
                if piece.piece_type == chess.KING or PIECE_VALUES.get(piece.piece_type, 0) >= 310:
                    high_value_targets += 1
        return 180.0 if high_value_targets >= 2 else 0.0
    finally:
        board.pop()


def evaluate_g(board: chess.Board, move: chess.Move) -> float:
    """
    G(m): King safety score (+120 if castling, or Chebyshev distance <= 2
    from friendly King, or captures an attacker of the King zone; else 0).
    """
    friendly_color = board.turn
    king_sq = board.king(friendly_color)

    # 1. Castling
    if board.is_castling(move):
        return 120.0

    if king_sq is not None:
        # 2. Within Chebyshev distance <= 2 from friendly king
        if chebyshev_distance(move.to_square, king_sq) <= 2:
            return 120.0

        # 3. Friendly piece captures an attacker of the King zone (dist <= 1 of King)
        if board.is_capture(move):
            target_piece = board.piece_at(move.to_square)
            if target_piece is not None:
                for attacked_sq in board.attacks(move.to_square):
                    if chebyshev_distance(attacked_sq, king_sq) <= 1:
                        return 120.0

    return 0.0


def evaluate_move_components(board: chess.Board, move: chess.Move) -> Dict[str, float]:
    """Computes all deterministic heuristic components for a move."""
    return {
        "C": evaluate_c(board, move),
        "K": evaluate_k(board, move),
        "D": evaluate_d(board, move),
        "R": evaluate_r(board, move),
        "F": evaluate_f(board, move),
        "G": evaluate_g(board, move),
    }


# =============================================================================
# 3 DISTINCT WAR COUNCIL ADVISOR FORMULAS
# =============================================================================


def score_queen(comps: Dict[str, float]) -> float:
    """
    The Marshal's Strike (Lysandra / Nyssara - Tactical Offense, Red Vector):
    S_Queen(m) = 1.8 * C(m) + 2.0 * K(m) + 1.2 * D(m) + 0.4 * R(m)
    """
    return (
        1.8 * comps["C"]
        + 2.0 * comps["K"]
        + 1.2 * comps["D"]
        + 0.4 * comps["R"]
    )


def score_warden(comps: Dict[str, float]) -> float:
    """
    The Bastion's Guard (Brannoch / Dravok - Defense & Fortification, Blue Vector):
    S_Warden(m) = 1.5 * G(m) + 1.0 * D(m) + 0.8 * C(m) + 2.5 * R(m)
    """
    return (
        1.5 * comps["G"]
        + 1.0 * comps["D"]
        + 0.8 * comps["C"]
        + 2.5 * comps["R"]
    )


def score_seer(comps: Dict[str, float]) -> float:
    """
    The Seer's Path (Ilyara / Veyra - Tactical Geometry & Forks, Violet Vector):
    S_Seer(m) = 2.2 * F(m) + 1.4 * D(m) + 1.1 * C(m) + 1.2 * R(m)
    """
    return (
        2.2 * comps["F"]
        + 1.4 * comps["D"]
        + 1.1 * comps["C"]
        + 1.2 * comps["R"]
    )


def score_ally(comps: Dict[str, float]) -> float:
    """
    Allied Sovereign Advisor (Grand Finale 4th Vector, Gold Vector):
    Harmonious blend of offensive pressure and central coordination.
    """
    return (
        1.4 * comps["C"]
        + 1.5 * comps["K"]
        + 1.5 * comps["D"]
        + 1.5 * comps["F"]
        + 1.0 * comps["R"]
    )


# =============================================================================
# UI COORDINATE & ATL VECTOR CALCULATIONS (Section 6.2)
# =============================================================================


def square_to_center_coords(sq: int, orientation_white: bool = True) -> Tuple[float, float]:
    """
    Calculates center pixel coordinates (X, Y) for a chessboard square on a 1920x1080 display.
    Board Origin: (640, 120), Square Width: 80px, Centered at +40px.
    """
    f = chess.square_file(sq)
    r = chess.square_rank(sq)
    if orientation_white:
        x = 640.0 + f * 80.0 + 40.0
        y = 120.0 + (7 - r) * 80.0 + 40.0
    else:
        x = 640.0 + (7 - f) * 80.0 + 40.0
        y = 120.0 + r * 80.0 + 40.0
    return (x, y)


def get_vector_arrow_transform(
    from_sq: int, to_sq: int, orientation_white: bool = True
) -> Tuple[float, float, float, float]:
    """
    Returns (x1, y1, length_px, angle_deg) for Ren'Py ATL transform advisor_vector_arrow.
    Exact trigonometry matching Section 6.2.
    """
    x1, y1 = square_to_center_coords(from_sq, orientation_white)
    x2, y2 = square_to_center_coords(to_sq, orientation_white)
    dx = x2 - x1
    dy = y2 - y1
    length_px = math.hypot(dx, dy)
    angle_deg = math.degrees(math.atan2(dy, dx))
    return (round(x1, 1), round(y1, 1), round(length_px, 1), round(angle_deg, 2))


# =============================================================================
# WAR COUNCIL ADVICE GENERATOR (Strict Uniqueness Filter)
# =============================================================================


def generate_advisor_rationale(
    advisor_type: str, move: chess.Move, comps: Dict[str, float], enhanced: bool = False
) -> str:
    """Generates tactical rationale dialogue for an advisor's recommended move."""
    piece_names = {
        chess.PAWN: "Vanguard Sworn",
        chess.KNIGHT: "Cavalier",
        chess.BISHOP: "Seer",
        chess.ROOK: "Bastion Warden",
        chess.QUEEN: "Grand Marshal",
        chess.KING: "Sovereign",
    }
    from_str = chess.square_name(move.from_square)
    to_str = chess.square_name(move.to_square)

    if advisor_type == "queen":
        if comps["K"] > 0:
            base = f"Drive the strike to {to_str}! Force their Sovereign into retreat."
        elif comps["C"] >= 500:
            base = f"Shatter their heavy line at {to_str}—seize the material advantage."
        elif comps["C"] > 0:
            base = f"Cut down the enemy at {to_str} to clear our advance."
        elif comps["D"] > 0:
            base = f"Claim the central nexus at {to_str} to dominate the field."
        else:
            base = f"Advance from {from_str} to {to_str} to sustain offensive tempo."
        if enhanced:
            base += f" [Offense: +{comps['C'] + comps['K']:.0f} tactical pressure]"
        return base

    elif advisor_type == "warden":
        if comps["G"] > 0 and comps["R"] >= 0:
            base = f"Anchor our defenses around {to_str}. Protect the Sovereign at all costs."
        elif comps["R"] < 0:
            base = f"Take caution at {to_str}; ensure our shields overlap before advancing."
        elif comps["C"] > 0:
            base = f"Neutralize the threat at {to_str} with solid defensive footing."
        elif comps["D"] > 0:
            base = f"Establish an unbreakable bulwark at {to_str}."
        else:
            base = f"Reposition safely to {to_str} to reinforce our formation."
        if enhanced:
            base += f" [Fortification: King safety +{comps['G']:.0f}, Risk factor {comps['R']:.1f}]"
        return base

    elif advisor_type == "seer":
        if comps["F"] > 0:
            base = f"Align the celestial leylines through {to_str}! A dual threat opens before us."
        elif comps["D"] > 0:
            base = f"Channel diagonal resonance into {to_str} to bind their pathways."
        elif comps["C"] > 0:
            base = f"Harvest the astral fracture at {to_str}."
        else:
            base = f"Geometric convergence points toward {to_str}. Pressure bends in our favor."
        if enhanced:
            base += f" [Aether Geometry: Fork bonus +{comps['F']:.0f}]"
        return base

    elif advisor_type == "ally":
        if comps["K"] > 0 or comps["C"] > 0:
            base = f"Combined Concord strike at {to_str}! Dawn and Dusk converge as one."
        elif comps["F"] > 0:
            base = f"Twin-court pincer at {to_str}—bind the Arbiter's flanks!"
        else:
            base = f"Synchronize allied leylines from {from_str} to {to_str}."
        if enhanced:
            base += f" [Concord Synergy: +{comps['C'] + comps['K'] + comps['F']:.0f}]"
        return base

    return f"Advance to {to_str}."


def get_war_council_advice(
    board: chess.Board,
    player_faction: str = "dawn",
    enhanced_analysis: bool = False,
    legal_moves: Optional[List[chess.Move]] = None,
    include_allied_fourth: bool = False,
    enhanced_char_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    Computes recommendations for the 3 War Council Advisors with strict uniqueness.
    Section 5.1 & Section 4.3 (Allied 4th Advisor for Grand Finale).
    """
    moves = legal_moves if legal_moves is not None else list(board.legal_moves)
    if not moves:
        return []

    orientation_white = (player_faction.lower() == "dawn")

    # Precompute move components
    move_comps: Dict[chess.Move, Dict[str, float]] = {}
    for m in moves:
        move_comps[m] = evaluate_move_components(board, m)

    # 1. Marshal (Queen) selection
    m_queen = max(moves, key=lambda m: score_queen(move_comps[m]))

    # 2. Bastion (Warden) selection with uniqueness
    remaining_for_warden = [m for m in moves if m != m_queen]
    m_warden = max(remaining_for_warden, key=lambda m: score_warden(move_comps[m])) if remaining_for_warden else m_queen

    # 3. Seer selection with uniqueness
    remaining_for_seer = [m for m in moves if m != m_queen and m != m_warden]
    if remaining_for_seer:
        m_seer = max(remaining_for_seer, key=lambda m: score_seer(move_comps[m]))
    elif remaining_for_warden:
        m_seer = remaining_for_warden[0]
    else:
        m_seer = m_queen

    # Faction-specific character names and IDs
    if player_faction.lower() == "dawn":
        queen_char = ("dawn_queen", "Lysandra", "The Sunblade", "ui/arrow_queen_red.png", "red")
        warden_char = ("dawn_rook", "Brannoch", "The Alabaster Bastion", "ui/arrow_warden_blue.png", "blue")
        seer_char = ("dawn_bishop", "Ilyara", "The Prism Oracle", "ui/arrow_seer_violet.png", "violet")
        ally_char = ("dusk_queen", "Nyssara", "The Velvet Blade", "ui/arrow_ally_gold.png", "gold")
    else:
        queen_char = ("dusk_queen", "Nyssara", "The Velvet Blade", "ui/arrow_queen_red.png", "red")
        warden_char = ("dusk_rook", "Dravok", "The Iron Citadel", "ui/arrow_warden_blue.png", "blue")
        seer_char = ("dusk_bishop", "Veyra", "The Lantern Arcanist", "ui/arrow_seer_violet.png", "violet")
        ally_char = ("dawn_queen", "Lysandra", "The Sunblade", "ui/arrow_ally_gold.png", "gold")

    advice_list: List[Dict[str, Any]] = []

    def make_entry(
        advisor_role: str,
        char_info: Tuple[str, str, str, str, str],
        move: chess.Move,
        score_val: float,
    ) -> Dict[str, Any]:
        char_id, name, title, arrow_texture, color_name = char_info
        x1, y1, length_px, angle_deg = get_vector_arrow_transform(
            move.from_square, move.to_square, orientation_white
        )
        is_char_enhanced = enhanced_analysis or (
            enhanced_char_ids is not None and char_id in enhanced_char_ids
        )
        rationale = generate_advisor_rationale(
            advisor_role, move, move_comps[move], enhanced=is_char_enhanced
        )
        return {
            "role": advisor_role,
            "char_id": char_id,
            "name": name,
            "title": title,
            "move": move,
            "uci": move.uci(),
            "from_square": move.from_square,
            "to_square": move.to_square,
            "score": round(score_val, 2),
            "arrow_texture": arrow_texture,
            "color": color_name,
            "vector": {
                "x1": x1,
                "y1": y1,
                "length": length_px,
                "angle": angle_deg,
            },
            "rationale": rationale,
        }

    advice_list.append(make_entry("queen", queen_char, m_queen, score_queen(move_comps[m_queen])))
    advice_list.append(make_entry("warden", warden_char, m_warden, score_warden(move_comps[m_warden])))
    advice_list.append(make_entry("seer", seer_char, m_seer, score_seer(move_comps[m_seer])))

    if include_allied_fourth:
        remaining_for_ally = [m for m in moves if m not in (m_queen, m_warden, m_seer)]
        if remaining_for_ally:
            m_ally = max(remaining_for_ally, key=lambda m: score_ally(move_comps[m]))
        else:
            m_ally = m_queen
        advice_list.append(make_entry("ally", ally_char, m_ally, score_ally(move_comps[m_ally])))

    return advice_list


# =============================================================================
# 5.2 BOSS AI PROFILES (350 - 800 ELO)
# =============================================================================


class BossProfile:
    def __init__(
        self,
        profile_id: str,
        elo: int,
        depth: int,
        sigma: float,
        description: str,
        move_modifier: Callable[[chess.Board, chess.Move, Dict[str, float]], float],
    ):
        self.profile_id = profile_id
        self.elo = elo
        self.depth = depth
        self.sigma = sigma
        self.description = description
        self.move_modifier = move_modifier


def _mod_reckless_vanguard(board: chess.Board, m: chess.Move, c: Dict[str, float]) -> float:
    # 350 ELO: Pushes pawns aggressively (2.0x), sets R(m) = 0.1 * R(m)
    moving = board.piece_at(m.from_square)
    pawn_mult = 2.0 if moving and moving.piece_type == chess.PAWN else 1.0
    return (
        pawn_mult * (c["C"] + 0.5 * c["K"] + 0.5 * c["D"])
        + 0.1 * c["R"]
        + (50.0 if moving and moving.piece_type == chess.PAWN else 0.0)
    )


def _mod_flank_hunter(board: chess.Board, m: chess.Move, c: Dict[str, float]) -> float:
    # 420 ELO: Favors Knight maneuvers (2.2x)
    moving = board.piece_at(m.from_square)
    knight_mult = 2.2 if moving and moving.piece_type == chess.KNIGHT else 1.0
    return knight_mult * (c["C"] + 0.5 * c["K"] + 0.4 * c["D"] + 0.6 * c["R"])


def _mod_iron_warden(board: chess.Board, m: chess.Move, c: Dict[str, float]) -> float:
    # 480 ELO: Prefers defensive Rook moves (1.8x)
    moving = board.piece_at(m.from_square)
    rook_mult = 1.8 if moving and moving.piece_type == chess.ROOK else 1.0
    return rook_mult * (1.2 * c["G"] + 0.8 * c["D"] + 0.7 * c["C"] + 1.2 * c["R"])


def _mod_diagonal_sniper(board: chess.Board, m: chess.Move, c: Dict[str, float]) -> float:
    # 540 ELO: Fixated on Bishop lines (1.8x)
    moving = board.piece_at(m.from_square)
    bishop_mult = 1.8 if moving and moving.piece_type == chess.BISHOP else 1.0
    return bishop_mult * (c["C"] + 0.8 * c["D"] + 0.8 * c["F"] + 0.7 * c["R"])


def _mod_hollow_raider(board: chess.Board, m: chess.Move, c: Dict[str, float]) -> float:
    # 600 ELO: Highly aggressive on captures (1.6 * C(m))
    return 1.6 * c["C"] + 0.8 * c["K"] + 0.6 * c["D"] + 0.8 * c["R"]


def _mod_regicide_assassin(board: chess.Board, m: chess.Move, c: Dict[str, float]) -> float:
    # 650 ELO: Pursues checks relentlessly (3.0 * K(m))
    return 3.0 * c["K"] + 1.1 * c["C"] + 0.5 * c["D"] + 0.5 * c["R"]


def _mod_rival_queen(board: chess.Board, m: chess.Move, c: Dict[str, float]) -> float:
    # 700 ELO: Active early Queen sorties (1.8x)
    moving = board.piece_at(m.from_square)
    queen_mult = 1.8 if moving and moving.piece_type == chess.QUEEN else 1.0
    return queen_mult * (1.3 * c["C"] + 1.4 * c["K"] + 1.0 * c["D"] + 0.8 * c["R"])


def _mod_grand_command(board: chess.Board, m: chess.Move, c: Dict[str, float]) -> float:
    # 750-800 ELO: Balanced play
    return 1.4 * c["C"] + 1.5 * c["K"] + 1.2 * c["D"] + 1.4 * c["F"] + 1.2 * c["G"] + 1.0 * c["R"]


BOSS_PROFILES: Dict[str, BossProfile] = {
    "reckless_vanguard": BossProfile(
        "reckless_vanguard", 350, 1, 140.0, "Aggressive pawn thrusts with low risk awareness", _mod_reckless_vanguard
    ),
    "flank_hunter": BossProfile(
        "flank_hunter", 420, 1, 110.0, "Flank maneuvers favoring Knight thrusts", _mod_flank_hunter
    ),
    "iron_warden": BossProfile(
        "iron_warden", 480, 1, 90.0, "Defensive Rook alignment and King fortification", _mod_iron_warden
    ),
    "diagonal_sniper": BossProfile(
        "diagonal_sniper", 540, 1, 75.0, "Long-range Bishop diagonal pressure", _mod_diagonal_sniper
    ),
    "hollow_raider": BossProfile(
        "hollow_raider", 600, 2, 65.0, "Aggressive captures and predatory material trades", _mod_hollow_raider
    ),
    "regicide_assassin": BossProfile(
        "regicide_assassin", 650, 2, 50.0, "Obsessive pursuit of checks against the Sovereign", _mod_regicide_assassin
    ),
    "rival_queen": BossProfile(
        "rival_queen", 700, 2, 35.0, "Early Grand Marshal sorties and high-tempo queen pressure", _mod_rival_queen
    ),
    "grand_command": BossProfile(
        "grand_command", 750, 2, 20.0, "Balanced grandmaster coordination and foresight", _mod_grand_command
    ),
}


def _minimax_eval_depth2(
    board: chess.Board,
    profile: BossProfile,
    root_move: chess.Move,
    root_score: float,
) -> float:
    """
    Evaluates depth-2 reply for Boss AI profiles that use Depth 2 (600 - 800 ELO).
    Minimizes the opponent's best response to test if root_move leaves Boss vulnerable.
    """
    board.push(root_move)
    try:
        if board.is_checkmate():
            return 99999.0
        if board.is_stalemate() or board.is_insufficient_material():
            return 0.0

        replies = list(board.legal_moves)
        if not replies:
            return root_score

        # Opponent minimizes Boss advantage (or maximizes opponent counter-capture/check)
        worst_response_penalty = 0.0
        for reply in replies:
            c = evaluate_move_components(board, reply)
            # High opponent captures or checks penalize root move
            reply_harm = c["C"] + 1.2 * c["K"]
            if reply_harm > worst_response_penalty:
                worst_response_penalty = reply_harm

        return root_score - 0.7 * worst_response_penalty
    finally:
        board.pop()


def select_boss_move(
    board: chess.Board,
    profile_id: str,
    legal_moves: Optional[List[chess.Move]] = None,
    apply_noise: bool = True,
    rng: Optional[random.Random] = None,
) -> Optional[chess.Move]:
    """
    Selects a move for the Boss AI according to its personality profile and noise sigma.
    Section 5.2 of the Master Build Bible.
    """
    moves = legal_moves if legal_moves is not None else list(board.legal_moves)
    if not moves:
        return None

    profile = BOSS_PROFILES.get(profile_id, BOSS_PROFILES["grand_command"])
    r = rng if rng is not None else random.Random()

    scored_moves: List[Tuple[chess.Move, float]] = []
    for m in moves:
        comps = evaluate_move_components(board, m)
        base_score = profile.move_modifier(board, m, comps)

        if profile.depth >= 2:
            final_score = _minimax_eval_depth2(board, profile, m, base_score)
        else:
            final_score = base_score

        if apply_noise and profile.sigma > 0:
            noise = r.gauss(0.0, profile.sigma)
            final_score += noise

        scored_moves.append((m, final_score))

    scored_moves.sort(key=lambda item: item[1], reverse=True)
    return scored_moves[0][0]


def predict_boss_move(
    board: chess.Board,
    profile_id: str,
    legal_moves: Optional[List[chess.Move]] = None,
) -> Optional[chess.Move]:
    """
    Predicts opponent move deterministically (sigma = 0) for Oracle's Gaze spell.
    Section 5.3 of the Master Build Bible.
    """
    return select_boss_move(
        board,
        profile_id=profile_id,
        legal_moves=legal_moves,
        apply_noise=False,
    )
