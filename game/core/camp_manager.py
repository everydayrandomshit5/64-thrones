"""
camp_manager.py - War Tent Hub AP System, Tactical Recon, and Fellowship Ranks.

Part of 64-Thrones: High-Glamour Edition (v3.2).
Complies with Section 2.1 of the Master Build Bible.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

AFFINITY_THRESHOLDS = {
    1: 10,  # Rank 1: Acquaintance (Codex Dossier & Background Lore)
    2: 25,  # Rank 2: Trusted Confidant (Enhanced Advisor Analysis)
    3: 45,  # Rank 3: Sworn Comrade (+1 Max Aether Charge in Matches)
    4: 70,  # Rank 4: Champion's Oath (Oath CG & Campaign Epilogue)
}


class CampManager:
    """
    Manages the War Tent Tactical Hub between matches:
    - 2 AP per evening camp
    - Counsel Quarters (1 AP): Builds affinity, advances Fellowship Ranks (1-4)
    - War Table Recon (1 AP): Seer analysis, +1 Bonus Aether Charge next battle
    - Archive of Records (0 AP): Free action
    """

    def __init__(self, faction: str = "dawn") -> None:
        self.faction = faction.lower()
        self.ap: int = 2
        self.max_ap: int = 2
        self.chapter: int = 1

        # Character affinity scores and rank progression
        self.affinity: Dict[str, int] = {}
        self.fellowship_ranks: Dict[str, int] = {}

        # Reconnaissance status for next battle
        self.recon_buff_active: bool = False
        self.recon_target_boss: Optional[str] = None
        self.recon_notes: Optional[str] = None

        # Archive unlocked records
        self.unlocked_codex: List[str] = []
        self.unlocked_cgs: List[str] = []

    def start_camp_session(self, chapter: int) -> None:
        """Resets AP to 2 for a new inter-chapter War Tent session."""
        self.chapter = chapter
        self.ap = self.max_ap

    def spend_ap(self, cost: int = 1) -> bool:
        """Attempts to spend action points."""
        if self.ap >= cost:
            self.ap -= cost
            return True
        return False

    def counsel_officer(self, char_id: str, affinity_gain: int = 15) -> Dict[str, Any]:
        """
        Spends 1 AP to counsel with an officer in their private pavilion.
        Updates affinity and computes rank advancements.
        """
        if not self.spend_ap(1):
            return {"success": False, "error": "Insufficient Action Points (AP)."}

        current_aff = self.affinity.get(char_id, 0)
        new_aff = current_aff + affinity_gain
        self.affinity[char_id] = new_aff

        old_rank = self.fellowship_ranks.get(char_id, 0)
        new_rank = old_rank

        for rank, req in sorted(AFFINITY_THRESHOLDS.items()):
            if new_aff >= req and rank > new_rank:
                new_rank = rank

        rank_up = new_rank > old_rank
        if rank_up:
            self.fellowship_ranks[char_id] = new_rank
            if char_id not in self.unlocked_codex and new_rank >= 1:
                self.unlocked_codex.append(char_id)

        return {
            "success": True,
            "char_id": char_id,
            "affinity_gain": affinity_gain,
            "total_affinity": new_aff,
            "old_rank": old_rank,
            "current_rank": new_rank,
            "rank_up": rank_up,
            "remaining_ap": self.ap,
        }

    def perform_recon(
        self, seer_id: str, boss_profile_id: str, notes: str = ""
    ) -> Dict[str, Any]:
        """
        Spends 1 AP to consult with the Seer at the illuminated war table.
        Grants +1 Bonus Aether Charge in the upcoming match.
        """
        if not self.spend_ap(1):
            return {"success": False, "error": "Insufficient Action Points (AP)."}

        self.recon_buff_active = True
        self.recon_target_boss = boss_profile_id
        self.recon_notes = notes

        # Slight affinity gain for the Seer
        seer_aff = self.affinity.get(seer_id, 0) + 5
        self.affinity[seer_id] = seer_aff

        return {
            "success": True,
            "seer_id": seer_id,
            "target_boss": boss_profile_id,
            "bonus_aether": 1,
            "notes": notes,
            "remaining_ap": self.ap,
        }

    def consume_recon_buff(self) -> bool:
        """Consumes the active recon buff when entering battle."""
        was_active = self.recon_buff_active
        self.recon_buff_active = False
        self.recon_target_boss = None
        self.recon_notes = None
        return was_active

    def get_battle_aether_bonuses(self) -> Tuple[int, int]:
        """
        Computes (max_aether, starting_aether) for an upcoming match:
        - Base max: 3
        - Any officer at Fellowship Rank 3+: +1 Max Aether
        - Recon buff active: +1 Starting Aether (up to max)
        """
        base_max = 3
        has_rank_3 = any(r >= 3 for r in self.fellowship_ranks.values())
        max_aether = base_max + (1 if has_rank_3 else 0)

        starting_aether = 3 + (1 if self.recon_buff_active else 0)
        return (max_aether, starting_aether)

    def has_enhanced_advisor(self, char_id: str) -> bool:
        """Returns True if the character is at least Fellowship Rank 2 (Enhanced Analysis)."""
        return self.fellowship_ranks.get(char_id, 0) >= 2

    def to_dict(self) -> Dict[str, Any]:
        """Serializes CampManager state for Ren'Py persistent/store persistence."""
        return {
            "faction": self.faction,
            "ap": self.ap,
            "max_ap": self.max_ap,
            "chapter": self.chapter,
            "affinity": dict(self.affinity),
            "fellowship_ranks": dict(self.fellowship_ranks),
            "recon_buff_active": self.recon_buff_active,
            "recon_target_boss": self.recon_target_boss,
            "recon_notes": self.recon_notes,
            "unlocked_codex": list(self.unlocked_codex),
            "unlocked_cgs": list(self.unlocked_cgs),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CampManager:
        """Reconstructs CampManager from serialized dict."""
        manager = cls(faction=data.get("faction", "dawn"))
        manager.ap = data.get("ap", 2)
        manager.max_ap = data.get("max_ap", 2)
        manager.chapter = data.get("chapter", 1)
        manager.affinity = dict(data.get("affinity", {}))
        manager.fellowship_ranks = dict(data.get("fellowship_ranks", {}))
        manager.recon_buff_active = data.get("recon_buff_active", False)
        manager.recon_target_boss = data.get("recon_target_boss")
        manager.recon_notes = data.get("recon_notes")
        manager.unlocked_codex = list(data.get("unlocked_codex", []))
        manager.unlocked_cgs = list(data.get("unlocked_cgs", []))
        return manager
