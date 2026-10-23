"""
Unit tests for game/core/camp_manager.py.
Verifies the War Tent Tactical Hub AP system, Counsel Quarters fellowship progression,
Seer reconnaissance, and battle aether bonuses (Section 2.1 of Master Build Bible).
"""

import pytest

from game.core.camp_manager import CampManager, AFFINITY_THRESHOLDS


def test_initial_camp_session():
    """Verify CampManager initializes with 2 AP per evening."""
    camp = CampManager(faction="dawn")
    assert camp.faction == "dawn"
    assert camp.ap == 2
    assert camp.max_ap == 2
    assert camp.chapter == 1
    assert camp.recon_buff_active is False


def test_counsel_quarters_fellowship_progression():
    """
    Verify Counsel Quarters advances affinity and fellowship ranks (1-4):
    Rank 1: 10, Rank 2: 25, Rank 3: 45, Rank 4: 70.
    """
    camp = CampManager(faction="dawn")

    # Counsel 1: 15 affinity -> Reaches Rank 1 (>= 10)
    res1 = camp.counsel_officer("dawn_queen", affinity_gain=15)
    assert res1["success"] is True
    assert res1["current_rank"] == 1
    assert res1["rank_up"] is True
    assert camp.ap == 1
    assert "dawn_queen" in camp.unlocked_codex

    # Counsel 2: +15 affinity -> Total 30 -> Reaches Rank 2 (>= 25)
    res2 = camp.counsel_officer("dawn_queen", affinity_gain=15)
    assert res2["success"] is True
    assert res2["current_rank"] == 2
    assert camp.has_enhanced_advisor("dawn_queen") is True
    assert camp.ap == 0

    # Cannot counsel again with 0 AP
    res3 = camp.counsel_officer("dawn_queen", affinity_gain=15)
    assert res3["success"] is False


def test_fellowship_rank_3_and_4_benefits():
    """Verify Rank 3 (+1 Max Aether) and Rank 4 Champion's Oath."""
    camp = CampManager(faction="dawn")
    camp.start_camp_session(chapter=3)

    # Bring Lysandra to Rank 3 (50 affinity >= 45)
    camp.counsel_officer("dawn_queen", affinity_gain=50)
    assert camp.fellowship_ranks["dawn_queen"] == 3

    # Check battle aether bonuses: Base max 3 + 1 (Rank 3) = 4
    max_aether, starting_aether = camp.get_battle_aether_bonuses()
    assert max_aether == 4
    assert starting_aether == 3

    # Advance to Rank 4 (75 affinity >= 70)
    camp.start_camp_session(chapter=7)
    res_rank4 = camp.counsel_officer("dawn_queen", affinity_gain=25)
    assert res_rank4["current_rank"] == 4


def test_war_table_recon():
    """
    Verify War Table Recon grants +1 Bonus Starting Aether in upcoming match.
    """
    camp = CampManager(faction="dawn")
    assert camp.ap == 2

    recon_res = camp.perform_recon(
        seer_id="dawn_bishop",
        boss_profile_id="flank_hunter",
        notes="Enemy relies heavily on Knight advances.",
    )
    assert recon_res["success"] is True
    assert camp.ap == 1
    assert camp.recon_buff_active is True

    # Aether bonus should now include the +1 starting charge
    max_aether, starting_aether = camp.get_battle_aether_bonuses()
    assert max_aether == 3
    assert starting_aether == 4 or starting_aether == min(max_aether, 4)

    # Entering battle consumes the recon buff
    assert camp.consume_recon_buff() is True
    assert camp.recon_buff_active is False
    assert camp.consume_recon_buff() is False


def test_camp_manager_serialization():
    """Verify CampManager state can be serialized to primitive dict and reconstructed."""
    camp = CampManager(faction="dawn")
    camp.counsel_officer("dawn_queen", affinity_gain=30)
    camp.perform_recon("dawn_bishop", "reckless_vanguard")

    data = camp.to_dict()
    assert data["affinity"]["dawn_queen"] == 30
    assert data["fellowship_ranks"]["dawn_queen"] == 2
    assert data["recon_buff_active"] is True

    restored = CampManager.from_dict(data)
    assert restored.affinity["dawn_queen"] == 30
    assert restored.fellowship_ranks["dawn_queen"] == 2
    assert restored.has_enhanced_advisor("dawn_queen") is True
    assert restored.recon_buff_active is True
