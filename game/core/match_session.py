"""
match_session.py - Match Controller, Sanitized Sovereign Spells & State Tracker.

Part of 64-Thrones: High-Glamour Edition (v3.2).
Complies with Section 0 & Section 5.3 of the Master Build Bible.
"""

from __future__ import annotations

import copy
import random
from typing import Any, Dict, List, Optional, Tuple

import chess

from .story_ai import (
    BOSS_PROFILES,
    get_war_council_advice,
    predict_boss_move,
    select_boss_move,
    square_to_center_coords,
)


class MatchSession:
    """
    Encapsulates a full Thronefield chess match, managing:
    - python-chess Board state and sanitized move filters
    - The 4 Sovereign Spells (Chrono-Pulse, Oracle's Gaze, Aegis Ward, Marshal's Advance)
    - Primitive FEN/History stack serialization for Ren'Py save/load/rollback
    - Material balance & event tracking
    """

    def __init__(
        self,
        player_faction: str = "dawn",
        boss_profile_id: str = "reckless_vanguard",
        initial_fen: Optional[str] = None,
        starting_aether: int = 3,
        max_aether: int = 3,
    ) -> None:
        self.player_faction = player_faction.lower()
        self.player_color: chess.Color = (
            chess.WHITE if self.player_faction == "dawn" else chess.BLACK
        )
        self.boss_color: chess.Color = not self.player_color
        self.boss_profile_id = boss_profile_id

        # Board initialization
        self.board = chess.Board(initial_fen) if initial_fen else chess.Board()
        self.current_fen: str = self.board.fen()

        # Aether & Spell States
        self.max_aether: int = max(1, max_aether)
        self.aether: int = min(starting_aether, self.max_aether)
        self.warded_square: Optional[int] = None
        self.oracle_active: bool = False
        self.oracle_prediction: Optional[Dict[str, Any]] = None

        # FEN + History stack serialization (Section 0)
        # Stores list of (fen_str, spell_state_snapshot)
        self.fen_history_list: List[Tuple[str, Dict[str, Any]]] = [
            (self.current_fen, self._snapshot_spell_state())
        ]

        # Match statistics
        self.move_count: int = 0
        self.captured_pieces_by_player: List[chess.PieceType] = []
        self.captured_pieces_by_boss: List[chess.PieceType] = []
        self.concord_points: int = 0

    def _snapshot_spell_state(self) -> Dict[str, Any]:
        """Returns a JSON-serializable snapshot of spell variables."""
        return {
            "aether": self.aether,
            "max_aether": self.max_aether,
            "warded_square": self.warded_square,
            "oracle_active": self.oracle_active,
            "oracle_prediction": copy.deepcopy(self.oracle_prediction),
        }

    @property
    def is_player_turn(self) -> bool:
        """Returns True if it is currently the player's turn to move."""
        return self.board.turn == self.player_color

    @property
    def is_game_over(self) -> bool:
        """Checks if the match has concluded."""
        return self.board.is_game_over()

    def get_outcome(self) -> Optional[Dict[str, Any]]:
        """Returns outcome summary if game is over, else None."""
        if not self.board.is_game_over():
            return None

        if self.board.is_checkmate():
            # The side whose turn it is has been checkmated
            winner = "player" if self.board.turn == self.boss_color else "boss"
            termination = "checkmate"
        elif self.board.is_stalemate():
            winner = "draw"
            termination = "stalemate"
        elif self.board.is_insufficient_material():
            winner = "draw"
            termination = "insufficient_material"
        elif self.board.can_claim_threefold_repetition():
            winner = "draw"
            termination = "threefold_repetition"
        elif self.board.can_claim_fifty_moves():
            winner = "draw"
            termination = "fifty_moves"
        else:
            winner = "draw"
            termination = "draw"

        return {
            "is_game_over": True,
            "winner": winner,
            "termination": termination,
            "turns_played": self.move_count,
        }

    # =========================================================================
    # SANITIZED MOVE FILTER (AEGIS WARD GUARD - Section 5.3)
    # =========================================================================

    def get_filtered_legal_moves(self) -> List[chess.Move]:
        """
        Sanitized legal move generator wrapper.
        Section 5.3:
        If warded_square is active and board.turn != player_color:
          1) If piece on warded_square delivers check OR enemy is in check:
             Aegis immunity is bypassed so python-chess evasion rules stay valid.
          2) Otherwise, filter out moves where m.to_square == warded_square.
          3) If filtered list is empty, fall back to unfiltered to prevent false stalemate.
        """
        all_legal = list(self.board.legal_moves)
        if not all_legal:
            return []

        # Aegis Ward only affects the opponent's moves
        if self.warded_square is None or self.board.turn == self.player_color:
            return all_legal

        # Check safety bypass: If opponent is in check, bypass immunity
        if self.board.is_check():
            return all_legal

        # Also verify if warded piece is delivering check (already covered by board.is_check(),
        # but check explicitly for safety)
        if self.warded_square in self.board.checkers():
            return all_legal

        # Filter out moves capturing the warded piece
        filtered = [m for m in all_legal if m.to_square != self.warded_square]

        # Prevent false stalemate
        return filtered if filtered else all_legal

    # =========================================================================
    # SOVEREIGN SPELL 1: CHRONO-PULSE (Tactical Rewind - Cost 1 Aether)
    # =========================================================================

    def can_cast_chrono_pulse(self) -> bool:
        """
        Guard clause:
        - len(fen_history_list) >= 3 (at least 1 full round of 2 half-moves has elapsed)
        - It is the player's turn
        - Player has at least 1 Aether
        """
        return (
            self.aether >= 1
            and self.is_player_turn
            and len(self.fen_history_list) >= 3
        )

    def cast_chrono_pulse(self) -> Dict[str, Any]:
        """
        Executes Chrono-Pulse:
        Pops the last 2 half-move snapshots and restores the prior full-turn state.
        Deducts 1 Aether for the cast.
        """
        if not self.can_cast_chrono_pulse():
            return {
                "success": False,
                "error": "Chrono-Pulse requirement not met (Aether >= 1, Player turn, >= 1 full round played)",
            }

        # Deduct aether cost
        self.aether -= 1
        current_aether = self.aether

        # Pop 2 half-moves (enemy move + player's previous move)
        self.fen_history_list.pop()
        self.fen_history_list.pop()

        # Restore from the new top of the history stack
        restored_fen, restored_spells = self.fen_history_list[-1]
        self.board = chess.Board(restored_fen)
        self.current_fen = restored_fen

        # Restore spell parameters (maintaining the newly deducted aether)
        self.warded_square = restored_spells.get("warded_square")
        self.oracle_active = False
        self.oracle_prediction = None
        self.aether = current_aether

        if self.move_count > 0:
            self.move_count -= 1

        return {
            "success": True,
            "restored_fen": self.current_fen,
            "remaining_aether": self.aether,
        }

    # =========================================================================
    # SOVEREIGN SPELL 2: ORACLE'S GAZE (Foresight - Cost 1 Aether)
    # =========================================================================

    def can_cast_oracle_gaze(self) -> bool:
        """
        Guard clause:
        - Player's turn
        - oracle_active == False
        - Player has at least 1 Aether
        """
        return (
            self.aether >= 1
            and self.is_player_turn
            and not self.oracle_active
            and not self.board.is_game_over()
        )

    def cast_oracle_gaze(self, boss_profile_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Executes Oracle's Gaze:
        Clones board, evaluates opponent's deterministic response (sigma = 0),
        and highlights predicted origin and destination squares.
        """
        if not self.can_cast_oracle_gaze():
            return {"success": False, "error": "Oracle's Gaze cannot be cast."}

        self.aether -= 1
        self.oracle_active = True
        profile = boss_profile_id if boss_profile_id else self.boss_profile_id

        # Predict opponent's threat:
        # Simulate position from opponent's perspective.
        # If we simulate opponent's next turn right now (or after top advisor move):
        cloned_board = self.board.copy()
        predicted_move: Optional[chess.Move] = None

        # If not in check, push null move to see what boss would play immediately
        if not cloned_board.is_check():
            cloned_board.push(chess.Move.null())
            predicted_move = predict_boss_move(cloned_board, profile)
            cloned_board.pop()

        # If null move wasn't possible or yielded nothing, evaluate after top Queen advisor move
        if predicted_move is None:
            advices = get_war_council_advice(self.board, player_faction=self.player_faction)
            if advices:
                top_m = advices[0]["move"]
                cloned_board.push(top_m)
                predicted_move = predict_boss_move(cloned_board, profile)
                cloned_board.pop()

        if predicted_move is None:
            # Fallback to any legal move in current board
            legal = list(self.board.legal_moves)
            predicted_move = legal[0] if legal else None

        if predicted_move is not None:
            from_sq = predicted_move.from_square
            to_sq = predicted_move.to_square
            orientation_white = (self.player_faction == "dawn")
            x1, y1 = square_to_center_coords(from_sq, orientation_white)
            x2, y2 = square_to_center_coords(to_sq, orientation_white)

            self.oracle_prediction = {
                "uci": predicted_move.uci(),
                "from_square": from_sq,
                "to_square": to_sq,
                "from_name": chess.square_name(from_sq),
                "to_name": chess.square_name(to_sq),
                "from_center": (x1, y1),
                "to_center": (x2, y2),
            }
        else:
            self.oracle_prediction = None

        return {
            "success": True,
            "prediction": self.oracle_prediction,
            "remaining_aether": self.aether,
        }

    # =========================================================================
    # SOVEREIGN SPELL 3: AEGIS WARD (Bastion Shield - Cost 2 Aether)
    # =========================================================================

    def can_cast_aegis_ward(self, target_sq: int) -> bool:
        """
        Guard clause:
        - Player's turn
        - Player has at least 2 Aether
        - target_sq contains a friendly non-King piece
        """
        if self.aether < 2 or not self.is_player_turn or self.board.is_game_over():
            return False

        piece = self.board.piece_at(target_sq)
        if piece is None:
            return False
        if piece.color != self.player_color or piece.piece_type == chess.KING:
            return False

        return True

    def cast_aegis_ward(self, target_sq: int) -> Dict[str, Any]:
        """
        Executes Aegis Ward:
        Protects target_sq for 1 enemy turn.
        """
        if not self.can_cast_aegis_ward(target_sq):
            return {"success": False, "error": "Invalid target for Aegis Ward."}

        self.aether -= 2
        self.warded_square = target_sq

        return {
            "success": True,
            "warded_square": target_sq,
            "square_name": chess.square_name(target_sq),
            "remaining_aether": self.aether,
        }

    # =========================================================================
    # SOVEREIGN SPELL 4: MARSHAL'S ADVANCE (Rapid Deployment - Cost 2 Aether)
    # =========================================================================

    def can_cast_marshals_advance(self, target_sq: int) -> bool:
        """
        Guard clause:
        1) Player's turn, aether >= 2
        2) Player's King is NOT in check
        3) target_sq is a friendly Pawn
        4) 0-indexed rank condition: 1-step move does not promote (dest rank not 0 or 7)
        5) The 1-step forward move is in board.legal_moves, is a non-capture,
           and does not deliver check.
        """
        if self.aether < 2 or not self.is_player_turn or self.board.is_game_over():
            return False

        if self.board.is_check():
            return False

        piece = self.board.piece_at(target_sq)
        if piece is None or piece.color != self.player_color or piece.piece_type != chess.PAWN:
            return False

        # Compute 1-step forward move
        step_offset = 8 if self.player_color == chess.WHITE else -8
        dest_sq = target_sq + step_offset

        if not (0 <= dest_sq <= 63):
            return False

        dest_rank = chess.square_rank(dest_sq)
        if dest_rank in (0, 7):
            return False

        step_move = chess.Move(target_sq, dest_sq)

        # Must be in legal_moves
        if step_move not in self.board.legal_moves:
            return False

        # Non-capture
        if self.board.piece_at(dest_sq) is not None:
            return False

        # Must not deliver check
        if self.board.gives_check(step_move):
            return False

        return True

    def cast_marshals_advance(self, target_sq: int) -> Dict[str, Any]:
        """
        Executes Marshal's Advance:
        Pushes the 1-step pawn advance, then immediately pushes chess.Move.null().
        Turn is returned to player!
        """
        if not self.can_cast_marshals_advance(target_sq):
            return {"success": False, "error": "Marshal's Advance conditions not met."}

        self.aether -= 2
        step_offset = 8 if self.player_color == chess.WHITE else -8
        dest_sq = target_sq + step_offset
        step_move = chess.Move(target_sq, dest_sq)

        # 1. Push pawn advance
        self.board.push(step_move)

        # 2. Immediately push null move to return turn to player
        self.board.push(chess.Move.null())

        # Update FEN and record snapshot
        self.current_fen = self.board.fen()
        self.fen_history_list.append((self.current_fen, self._snapshot_spell_state()))

        return {
            "success": True,
            "moved_pawn": chess.square_name(target_sq),
            "dest_square": chess.square_name(dest_sq),
            "remaining_aether": self.aether,
        }

    # =========================================================================
    # MOVE EXECUTION (PLAYER & OPPONENT)
    # =========================================================================

    def push_player_move(self, move: chess.Move) -> Dict[str, Any]:
        """
        Executes a player move, updates board state, and registers history snapshot.
        """
        if not self.is_player_turn:
            return {"success": False, "error": "Not player's turn"}

        legal_moves = self.get_filtered_legal_moves()
        if move not in legal_moves:
            return {"success": False, "error": f"Illegal move: {move.uci()}"}

        # Clear warded square if player moves the warded piece
        if self.warded_square == move.from_square:
            self.warded_square = None

        # Capture tracking
        captured_piece = self.board.piece_at(move.to_square)
        if captured_piece is not None:
            self.captured_pieces_by_player.append(captured_piece.piece_type)
        elif self.board.is_en_passant(move):
            self.captured_pieces_by_player.append(chess.PAWN)

        # Push move
        self.board.push(move)
        self.oracle_active = False
        self.oracle_prediction = None
        self.current_fen = self.board.fen()

        # Record history snapshot
        self.fen_history_list.append((self.current_fen, self._snapshot_spell_state()))

        return {
            "success": True,
            "move": move.uci(),
            "fen": self.current_fen,
            "is_game_over": self.board.is_game_over(),
        }

    def push_boss_move(
        self,
        profile_id: Optional[str] = None,
        apply_noise: bool = True,
        rng: Optional[random.Random] = None,
    ) -> Dict[str, Any]:
        """
        Calculates and executes the Boss AI move using sanitized legal move filters.
        Section 5.2 & Section 5.3.
        """
        if self.is_player_turn:
            return {"success": False, "error": "Currently player's turn"}

        if self.board.is_game_over():
            return {"success": False, "error": "Match already concluded"}

        prof = profile_id if profile_id else self.boss_profile_id
        filtered_moves = self.get_filtered_legal_moves()
        if not filtered_moves:
            return {"success": False, "error": "No legal moves available"}

        boss_move = select_boss_move(
            self.board,
            profile_id=prof,
            legal_moves=filtered_moves,
            apply_noise=apply_noise,
            rng=rng,
        )

        if boss_move is None:
            return {"success": False, "error": "Boss AI could not select a move"}

        # Capture tracking
        captured_piece = self.board.piece_at(boss_move.to_square)
        if captured_piece is not None:
            self.captured_pieces_by_boss.append(captured_piece.piece_type)
        elif self.board.is_en_passant(boss_move):
            self.captured_pieces_by_boss.append(chess.PAWN)

        # Push boss move
        self.board.push(boss_move)

        # Aegis Ward expires after 1 enemy turn
        self.warded_square = None

        self.move_count += 1
        self.current_fen = self.board.fen()

        # Record history snapshot
        self.fen_history_list.append((self.current_fen, self._snapshot_spell_state()))

        return {
            "success": True,
            "move": boss_move.uci(),
            "fen": self.current_fen,
            "is_game_over": self.board.is_game_over(),
        }

    # =========================================================================
    # REN'PY SERIALIZATION / ROLLBACK RECONSTRUCTION (Section 0)
    # =========================================================================

    def to_dict(self) -> Dict[str, Any]:
        """Serializes match state to primitive Python dict for Ren'Py store persistence."""
        return {
            "player_faction": self.player_faction,
            "boss_profile_id": self.boss_profile_id,
            "current_fen": self.board.fen(),
            "fen_history_list": copy.deepcopy(self.fen_history_list),
            "max_aether": self.max_aether,
            "aether": self.aether,
            "warded_square": self.warded_square,
            "oracle_active": self.oracle_active,
            "oracle_prediction": copy.deepcopy(self.oracle_prediction),
            "move_count": self.move_count,
            "captured_pieces_by_player": [int(p) for p in self.captured_pieces_by_player],
            "captured_pieces_by_boss": [int(p) for p in self.captured_pieces_by_boss],
            "concord_points": self.concord_points,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MatchSession:
        """Reconstructs a clean MatchSession from primitive store data."""
        session = cls(
            player_faction=data["player_faction"],
            boss_profile_id=data["boss_profile_id"],
            initial_fen=data["current_fen"],
            starting_aether=data.get("aether", 3),
            max_aether=data.get("max_aether", 3),
        )
        session.current_fen = data["current_fen"]
        session.fen_history_list = copy.deepcopy(data.get("fen_history_list", []))
        session.warded_square = data.get("warded_square")
        session.oracle_active = data.get("oracle_active", False)
        session.oracle_prediction = copy.deepcopy(data.get("oracle_prediction"))
        session.move_count = data.get("move_count", 0)
        session.captured_pieces_by_player = [
            chess.PieceType(p) for p in data.get("captured_pieces_by_player", [])
        ]
        session.captured_pieces_by_boss = [
            chess.PieceType(p) for p in data.get("captured_pieces_by_boss", [])
        ]
        session.concord_points = data.get("concord_points", 0)
        return session
