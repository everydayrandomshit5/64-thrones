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



## Audio Track Definitions

define audio.bgm_ashgate = "audio/bgm_ashgate_theme.wav"

define audio.bgm_dawn = "audio/bgm_dawn_march.wav"

define audio.bgm_dusk = "audio/bgm_dusk_requiem.wav"

define audio.bgm_war_tent = "audio/bgm_war_tent.wav"

define audio.bgm_parley = "audio/bgm_parley.wav"

define audio.bgm_climax = "audio/bgm_monolith_climax.wav"

define audio.bgm_epilogue = "audio/bgm_epilogue.wav"



define audio.sfx_move = "audio/sfx_piece_move.wav"

define audio.sfx_capture = "audio/sfx_piece_capture.wav"

define audio.sfx_check = "audio/sfx_check.wav"

define audio.sfx_checkmate = "audio/sfx_checkmate.wav"

define audio.sfx_spell = "audio/sfx_spell_cast.wav"

define audio.sfx_chrono = "audio/sfx_chrono_pulse.wav"

define audio.sfx_armor_break = "audio/sfx_armor_break.wav"

define audio.sfx_click = "audio/sfx_button_click.wav"

## Custom Transitions
define flash = Fade(0.1, 0.0, 0.3, color="#ffffff")



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



## Runtime Session State (Primitives persisted per Section 0 Guardrail)

default current_session = None

default current_detector = None

default current_camp = None

default session_snapshot = None

default camp_snapshot = None

default current_chapter_idx = 1

default current_faction = "dawn"

default last_match_outcome = None

default chapter_obj_met = False

default banter_db = {}



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



    def load_banter_json():

        p = renpy.loader.transfn("data/banter.json")

        with open(p, "r", encoding="utf-8") as f:

            return json.load(f)



## ============================================================================

## MAIN ENTRY POINT

## ============================================================================



label start:

    play music audio.bgm_ashgate fadein 1.0

    scene bg_ashgate_hall

    with dissolve



    $ chapters_db = load_campaign_json()

    $ roster_db = load_roster_json()

    $ banter_db = load_banter_json()



    menu:

        "Begin The Summit of Ashgate (Shared Prologue)":

            jump prologue_start



        "Command House Aurelis (Dawn / White Campaign)":

            $ current_faction = "dawn"

            $ current_camp = CampManager(faction="dawn")

            jump campaign_dawn_start



        "Command The Umbrenholt Dominion (Dusk / Black Campaign)":

            $ current_faction = "dusk"

            $ current_camp = CampManager(faction="dusk")

            jump campaign_dusk_start



        "Open Codex Archive & CG Gallery":

            call screen codex_gallery

            jump start



## ============================================================================

## CAMPAIGN ENTRY LABELS (Routed to game/story/campaign_dawn.rpy & campaign_dusk.rpy)

## ============================================================================



label campaign_dawn_start:

    jump dawn_ch1_start



label campaign_dusk_start:

    jump dusk_ch1_start

