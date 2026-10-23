## script.rpy - Game Entry Point, System Initialization & Story Orchestrator
## 64-Thrones: High-Glamour Edition (v3.2)

init -10 python:
    import sys
    import os
    import json
    import random

    # Add embedded python-packages (python-chess) to sys.path
    game_dir = config.gamedir
    pkg_dir = os.path.join(game_dir, "python-packages")
    if pkg_dir not in sys.path:
        sys.path.insert(0, pkg_dir)

    import chess
    from core.story_ai import (
        get_war_council_advice,
        select_boss_move,
        predict_boss_move,
        square_to_center_coords,
        get_vector_arrow_transform,
        BOSS_PROFILES,
    )
    from core.match_session import MatchSession
    from core.event_detector import EventDetector, calculate_material_delta
    from core.camp_manager import CampManager

## Character Dialogue Definitions
define lysandra = Character("Lysandra", color="#EBC364", image="dawn_queen")
define nyssara = Character("Nyssara", color="#AF78E6", image="dusk_queen")
define aurelian = Character("Aurelian", color="#FFE899", image="dawn_king")
define malachar = Character("Malachar", color="#B8A8D0", image="dusk_king")
define brannoch = Character("Brannoch", color="#E0D8C8", image="dawn_rook")
define dravok = Character("Dravok", color="#9890A8", image="dusk_rook")
define ilyara = Character("Ilyara", color="#80D0FF", image="dawn_bishop")
define veyra = Character("Veyra", color="#C080FF", image="dusk_bishop")
define kestrel = Character("Kestrel", color="#FFA060", image="dawn_knight")
define kaelen = Character("Kaelen", color="#C07080", image="dusk_knight")
define tamsin = Character("Tamsin", color="#F0E0A0", image="dawn_pawn_lead")
define sorrel = Character("Sorrel", color="#D06070", image="dusk_pawn_lead")
define arbiter = Character("Arbiter Automaton", color="#88FFD0")
define narrator = Character(None, color="#FBF8F0")

## Persistent Game Progress
default persistent.concord_points = 0
default persistent.completed_campaigns = []
default persistent.unlocked_cgs = []

## Runtime Session State
default current_session = None
default current_detector = None
default current_camp = None
default current_chapter_idx = 1
default current_faction = "dawn"

## Helper function to load JSON chapter data
init python:
    def load_campaign_json():
        p = renpy.loader.transfn("data/chapters.json")
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_roster_json():
        p = renpy.loader.transfn("data/characters.json")
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)["characters"]

## ============================================================================
## MAIN ENTRY POINT
## ============================================================================

label start:
    scene bg_ashgate_hall fit cover
    with dissolve

    $ chapters_db = load_campaign_json()
    $ roster_db = load_roster_json()

    # Introduction & Faction Selection
    narrator "Six centuries after the Cataclysm of Falling Stars, the continent of Eltheris stands once more upon the precipice of ruin."
    narrator "Between the radiant realm of House Aurelis and the twilight empire of Umbrenholt, sixty-four colossal monoliths rise from the chasm of The Hollow."

    menu:
        "Select your path in the Rite of Sixty-Four Thrones:":
            "Command House Aurelis (Dawn / White)":
                $ current_faction = "dawn"
                $ current_camp = CampManager(faction="dawn")
                jump campaign_dawn_start

            "Command The Umbrenholt Dominion (Dusk / Black)":
                $ current_faction = "dusk"
                $ current_camp = CampManager(faction="dusk")
                jump campaign_dusk_start

            "Open Codex Archive & CG Gallery":
                call screen codex_gallery
                jump start

## ============================================================================
## CAMPAIGN LOOP (DAWN)
## ============================================================================

label campaign_dawn_start:
    $ chapters_db = load_campaign_json()
    $ roster_db = load_roster_json()
    $ dawn_list = chapters_db["dawn_campaign"]

    while current_chapter_idx <= len(dawn_list):
        $ chap_data = dawn_list[current_chapter_idx - 1]

        # 1. War Tent Tactical Hub
        $ current_camp.start_camp_session(current_chapter_idx)
        $ tent_state = WarTentUI(current_camp, chap_data, roster_db)
        call screen war_tent_hub(tent_state)

        # 2. Thronefield Chess Battle
        $ aether_bonuses = current_camp.get_battle_aether_bonuses()
        $ current_camp.consume_recon_buff()

        $ current_session = MatchSession(
            player_faction="dawn",
            boss_profile_id=chap_data["boss_profile"],
            initial_fen=chap_data["initial_fen"],
            starting_aether=aether_bonuses[1],
            max_aether=aether_bonuses[0]
        )
        $ current_detector = EventDetector(
            player_char_id=chap_data["player_char"],
            boss_char_id=chap_data["boss_char"],
            player_faction="dawn"
        )

        $ tf_ui = ThronefieldUI(current_session, current_detector, chap_data)
        call screen thronefield(tf_ui)

        # Aftermath
        $ current_chapter_idx += 1

    return

## ============================================================================
## CAMPAIGN LOOP (DUSK)
## ============================================================================

label campaign_dusk_start:
    $ chapters_db = load_campaign_json()
    $ roster_db = load_roster_json()
    $ dusk_list = chapters_db["dusk_campaign"]

    while current_chapter_idx <= len(dusk_list):
        $ chap_data = dusk_list[current_chapter_idx - 1]

        # 1. War Tent Tactical Hub
        $ current_camp.start_camp_session(current_chapter_idx)
        $ tent_state = WarTentUI(current_camp, chap_data, roster_db)
        call screen war_tent_hub(tent_state)

        # 2. Thronefield Chess Battle
        $ aether_bonuses = current_camp.get_battle_aether_bonuses()
        $ current_camp.consume_recon_buff()

        $ current_session = MatchSession(
            player_faction="dusk",
            boss_profile_id=chap_data["boss_profile"],
            initial_fen=chap_data["initial_fen"],
            starting_aether=aether_bonuses[1],
            max_aether=aether_bonuses[0]
        )
        $ current_detector = EventDetector(
            player_char_id=chap_data["player_char"],
            boss_char_id=chap_data["boss_char"],
            player_faction="dusk"
        )

        $ tf_ui = ThronefieldUI(current_session, current_detector, chap_data)
        call screen thronefield(tf_ui)

        # Aftermath
        $ current_chapter_idx += 1

    return
