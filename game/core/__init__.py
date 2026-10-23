"""
game.core package initialization.
"""

from .story_ai import (
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

from .match_session import MatchSession
from .event_detector import (
    EventDetector,
    calculate_side_material,
    calculate_material_delta,
    is_king_in_check,
)
from .camp_manager import CampManager, AFFINITY_THRESHOLDS

__all__ = [
    "PIECE_VALUES",
    "BOSS_PROFILES",
    "chebyshev_distance",
    "evaluate_c",
    "evaluate_k",
    "evaluate_d",
    "evaluate_r",
    "evaluate_f",
    "evaluate_g",
    "evaluate_move_components",
    "score_queen",
    "score_warden",
    "score_seer",
    "score_ally",
    "get_war_council_advice",
    "select_boss_move",
    "predict_boss_move",
    "square_to_center_coords",
    "get_vector_arrow_transform",
    "MatchSession",
    "EventDetector",
    "calculate_side_material",
    "calculate_material_delta",
    "is_king_in_check",
    "CampManager",
    "AFFINITY_THRESHOLDS",
]
