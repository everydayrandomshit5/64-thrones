"""
event_detector.py - Detects checks, material deltas, and triggers dynamic wardrobe states.

Part of 64-Thrones: High-Glamour Edition (v3.2).
Complies with Section 5.4 of the Master Build Bible.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import chess

from .story_ai import PIECE_VALUES


def calculate_side_material(board: chess.Board, color: chess.Color) -> int:
    """Calculates total centipawn material for a given color (excluding King)."""
    total = 0
    for pt, val in PIECE_VALUES.items():
        if pt == chess.KING:
            continue
        total += len(board.pieces(pt, color)) * val
    return total


def calculate_material_delta(board: chess.Board, side_color: chess.Color) -> float:
    """
    Computes net material balance in pawns:
    Delta M = (M_side - M_opponent) / 100.0
    """
    m_side = calculate_side_material(board, side_color)
    m_opp = calculate_side_material(board, not side_color)
    return (m_side - m_opp) / 100.0


def is_king_in_check(board: chess.Board, side_color: chess.Color) -> bool:
    """Checks whether the King of side_color is in check."""
    if board.turn == side_color:
        return board.is_check()
    king_sq = board.king(side_color)
    if king_sq is None:
        return False
    return board.is_attacked_by(not side_color, king_sq)


class EventDetector:
    """
    Manages dynamic sprite wardrobe state transitions (state_a_battle <-> state_b_worn),
    pawn promotion states (state_d_promoted), and cut-in banner triggers.
    Section 5.4 of the Master Build Bible.
    """

    def __init__(
        self,
        player_char_id: str = "dawn_queen",
        boss_char_id: str = "dusk_queen",
        player_faction: str = "dawn",
    ) -> None:
        self.player_char_id = player_char_id
        self.boss_char_id = boss_char_id
        self.player_faction = player_faction.lower()
        self.player_color: chess.Color = (
            chess.WHITE if self.player_faction == "dawn" else chess.BLACK
        )
        self.boss_color: chess.Color = not self.player_color

        # Wardrobe states
        self.player_sprite_state: str = "state_a_battle"
        self.boss_sprite_state: str = "state_a_battle"

        # Vanguard promotion flags
        self.dawn_pawn_promoted: bool = False
        self.dusk_pawn_promoted: bool = False

        # Queue of triggered cut-in events
        self.pending_cutins: List[Dict[str, Any]] = []

    def update(
        self, board: chess.Board, last_move: Optional[chess.Move] = None
    ) -> Dict[str, Any]:
        """
        Evaluates board state after each half-move and triggers state transitions.
        """
        # Check promotion if last_move was a pawn promotion
        if last_move and last_move.promotion is not None:
            # Check who promoted
            # If White pawn reached rank 8 (chess rank 7 in 0-indexed)
            if chess.square_rank(last_move.to_square) == 7 and not self.dawn_pawn_promoted:
                self.dawn_pawn_promoted = True
                self._trigger_promoted_cutin("dawn_pawn_lead")
            elif chess.square_rank(last_move.to_square) == 0 and not self.dusk_pawn_promoted:
                self.dusk_pawn_promoted = True
                self._trigger_promoted_cutin("dusk_pawn_lead")

        # Evaluate Player Side
        player_delta = calculate_material_delta(board, self.player_color)
        player_check = is_king_in_check(board, self.player_color)
        player_has_queen = len(board.pieces(chess.QUEEN, self.player_color)) > 0
        player_queen_lost = not player_has_queen

        self.player_sprite_state = self._evaluate_side_transition(
            current_state=self.player_sprite_state,
            char_id=self.player_char_id,
            delta_m=player_delta,
            in_check=player_check,
            queen_lost=player_queen_lost,
            is_player=True,
        )

        # Evaluate Boss Side
        boss_delta = calculate_material_delta(board, self.boss_color)
        boss_check = is_king_in_check(board, self.boss_color)
        boss_has_queen = len(board.pieces(chess.QUEEN, self.boss_color)) > 0
        boss_queen_lost = not boss_has_queen

        self.boss_sprite_state = self._evaluate_side_transition(
            current_state=self.boss_sprite_state,
            char_id=self.boss_char_id,
            delta_m=boss_delta,
            in_check=boss_check,
            queen_lost=boss_queen_lost,
            is_player=False,
        )

        return {
            "player_delta_m": round(player_delta, 2),
            "boss_delta_m": round(boss_delta, 2),
            "player_check": player_check,
            "boss_check": boss_check,
            "player_queen_lost": player_queen_lost,
            "boss_queen_lost": boss_queen_lost,
            "player_state": self.player_sprite_state,
            "boss_state": self.boss_sprite_state,
            "dawn_pawn_promoted": self.dawn_pawn_promoted,
            "dusk_pawn_promoted": self.dusk_pawn_promoted,
            "cutins_triggered": len(self.pending_cutins) > 0,
        }

    def _evaluate_side_transition(
        self,
        current_state: str,
        char_id: str,
        delta_m: float,
        in_check: bool,
        queen_lost: bool,
        is_player: bool,
    ) -> str:
        """
        Transition logic with hysteresis:
        - state_a -> state_b if delta_m <= -2.0 OR in_check OR queen_lost
        - state_b -> state_a only if NOT in_check AND NOT queen_lost AND delta_m >= 0.0
        """
        # If character is in state_a_battle:
        if current_state == "state_a_battle":
            if delta_m <= -2.0 or in_check or queen_lost:
                # Transition to worn / battle-damaged state
                self._trigger_worn_cutin(char_id, delta_m, in_check, queen_lost)
                return "state_b_worn"
            return "state_a_battle"

        # If character is in state_b_worn:
        elif current_state == "state_b_worn":
            if not in_check and not queen_lost and delta_m >= 0.0:
                # Hysteresis recovery to pristine state
                return "state_a_battle"
            return "state_b_worn"

        return current_state

    def _trigger_worn_cutin(
        self, char_id: str, delta_m: float, in_check: bool, queen_lost: bool
    ) -> None:
        """Queues an Action Cut-In Banner event when armor is compromised."""
        self.pending_cutins.append({
            "type": "battle_damage",
            "char_id": char_id,
            "banner": f"cutins/{char_id}_cutin.png",
            "sfx": "audio/sfx_armor_shatter.ogg",
            "vfx": "vpunch",
            "reason": (
                "check" if in_check else ("queen_loss" if queen_lost else "material_deficit")
            ),
            "delta_m": delta_m,
        })

    def _trigger_promoted_cutin(self, lead_id: str) -> None:
        """Queues a Grand Promotion Cut-In Banner event."""
        self.pending_cutins.append({
            "type": "ascension",
            "char_id": lead_id,
            "banner": f"cutins/{lead_id}_promoted_cutin.png",
            "sfx": "audio/sfx_ascension_fanfare.ogg",
            "vfx": "flash",
            "reason": "promotion",
        })

    def pop_pending_cutins(self) -> List[Dict[str, Any]]:
        """Consumes and returns all currently pending cut-in events."""
        events = list(self.pending_cutins)
        self.pending_cutins.clear()
        return events

    def get_character_sprite_state(self, char_id: str) -> str:
        """Returns the active wardrobe state for a specific character ID."""
        if char_id == "dawn_pawn_lead" and self.dawn_pawn_promoted:
            return "state_d_promoted"
        if char_id == "dusk_pawn_lead" and self.dusk_pawn_promoted:
            return "state_d_promoted"

        if char_id == self.player_char_id:
            return self.player_sprite_state
        if char_id == self.boss_char_id:
            return self.boss_sprite_state

        return "state_a_battle"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes event detector state for save/load."""
        return {
            "player_char_id": self.player_char_id,
            "boss_char_id": self.boss_char_id,
            "player_faction": self.player_faction,
            "player_sprite_state": self.player_sprite_state,
            "boss_sprite_state": self.boss_sprite_state,
            "dawn_pawn_promoted": self.dawn_pawn_promoted,
            "dusk_pawn_promoted": self.dusk_pawn_promoted,
            "pending_cutins": list(self.pending_cutins),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EventDetector:
        """Reconstructs EventDetector from saved state dict."""
        detector = cls(
            player_char_id=data.get("player_char_id", "dawn_queen"),
            boss_char_id=data.get("boss_char_id", "dusk_queen"),
            player_faction=data.get("player_faction", "dawn"),
        )
        detector.player_sprite_state = data.get("player_sprite_state", "state_a_battle")
        detector.boss_sprite_state = data.get("boss_sprite_state", "state_a_battle")
        detector.dawn_pawn_promoted = data.get("dawn_pawn_promoted", False)
        detector.dusk_pawn_promoted = data.get("dusk_pawn_promoted", False)
        detector.pending_cutins = list(data.get("pending_cutins", []))
        return detector
