## codex_gallery.rpy - Codex Dossier, Wardrobe State Switcher & CG Gallery
## Complies with Section 2.1 & Part 3 of the Master Build Bible (v3.2)

init python:
    class CodexUI:
        def __init__(self, roster_data, manifest_data):
            self.roster = roster_data
            self.manifest = manifest_data
            self.active_subtab = "dossier"  # "dossier", "cgs", "lore"
            self.selected_char_id = "dawn_queen"
            self.selected_outfit_state = "state_a_battle"
            self.fullscreen_cg = None

        def select_character(self, char_id):
            self.selected_char_id = char_id
            self.selected_outfit_state = "state_a_battle"
            try:
                renpy.restart_interaction()
            except Exception:
                pass

        def set_outfit_state(self, state):
            self.selected_outfit_state = state
            try:
                renpy.restart_interaction()
            except Exception:
                pass

        def view_cg(self, cg_path):
            self.fullscreen_cg = cg_path
            try:
                renpy.restart_interaction()
            except Exception:
                pass

        def close_cg(self):
            self.fullscreen_cg = None
            try:
                renpy.restart_interaction()
            except Exception:
                pass

default codex_state = None

init python:
    import json
    from pathlib import Path

    def load_codex_data():
        global codex_state
        if codex_state is not None:
            return
        roster_path = renpy.loader.transfn("data/characters.json")
        try:
            manifest_path = renpy.loader.transfn("data/art_manifest.json")
        except Exception:
            manifest_path = renpy.loader.transfn("../tools/art_manifest.json")
        with open(roster_path, "r", encoding="utf-8") as f:
            r_data = json.load(f).get("characters", [])
        with open(manifest_path, "r", encoding="utf-8") as f:
            m_data = json.load(f)
        codex_state = CodexUI(r_data, m_data)

## ============================================================================
## MAIN CODEX GALLERY SCREEN
## ============================================================================

screen codex_gallery():
    modal True

    on "show" action Function(load_codex_data)

    if codex_state is None:
        $ load_codex_data()

    add "bg/bg_obsidian_archive.png" fit "cover"

    # Top Header & Navigation
    frame:
        xpos 0 ypos 0 xsize 1920 ysize 80
        background "#100C1CEE"
        hbox:
            align (0.5, 0.5)
            spacing 40
            text "THE CODEX ARCHIVE & MEMORIAL" size 28 color "#EBC364" bold True

            button:
                action [SetField(codex_state, "active_subtab", "dossier"), Function(renpy.restart_interaction)]
                text "Character Dossiers & Wardrobe" size 20 color ("#FFE899" if codex_state.active_subtab == "dossier" else "#C8C0D8")

            button:
                action [SetField(codex_state, "active_subtab", "cgs"), Function(renpy.restart_interaction)]
                text "Fellowship CG Gallery" size 20 color ("#FFE899" if codex_state.active_subtab == "cgs" else "#C8C0D8")

            button:
                action [SetField(codex_state, "active_subtab", "lore"), Function(renpy.restart_interaction)]
                text "Chronicles of Eltheris" size 20 color ("#FFE899" if codex_state.active_subtab == "lore" else "#C8C0D8")

        textbutton "Return":
            xalign 0.98 yalign 0.5
            text_size 22
            action Hide("codex_gallery", transition=dissolve)

    # -------------------------------------------------------------------------
    # SUBTAB 1: CHARACTER DOSSIER & WARDROBE VIEWER
    # -------------------------------------------------------------------------
    if codex_state.active_subtab == "dossier":
        # Character Selector Rail
        frame:
            xpos 40 ypos 100 xsize 380 ysize 940
            background "#181224EE"
            vbox:
                spacing 8
                text "ROSTER OF CHOSEN" size 20 color "#EBC364" bold True
                for c in codex_state.roster:
                    $ cid = c["id"]
                    button:
                        xsize 340 ysize 60
                        background ("#4A2E68" if codex_state.selected_char_id == cid else "#221A30")
                        hover_background "#58387C"
                        action [SetField(codex_state, "selected_char_id", cid), SetField(codex_state, "selected_outfit_state", "state_a_battle"), Function(renpy.restart_interaction)]
                        hbox:
                            align (0.5, 0.5)
                            spacing 10
                            add f"ui/advisors/{cid}_bust.png" xsize 44 ysize 44
                            text "[c['name']]" size 16 color "#FBF8F0"

        # Character Display & Wardrobe Switcher
        $ active_char = next((c for c in codex_state.roster if c["id"] == codex_state.selected_char_id), None)
        if active_char:
            # Full Height Character Sprite
            $ sprite_file = f"characters/{active_char['id']}/{codex_state.selected_outfit_state}.png"
            add sprite_file:
                xpos 440 ypos 100
                xsize 720 ysize 864
                fit "contain"

            # Wardrobe Switcher Buttons
            frame:
                xpos 1180 ypos 100 xsize 700 ysize 940
                background "#181224EE"
                vbox:
                    spacing 16
                    text "[active_char['name'].upper()]" size 32 color "#EBC364" bold True
                    text "[active_char['title']] — [active_char['role'].upper()] ([active_char['faction'].upper()])" size 18 color "#AF78E6"
                    text "[active_char['visuals']]" size 16 color "#C8C0D8"

                    null height 10
                    text "INTERACTIVE WARDROBE STATES" size 20 color "#FFE899" bold True

                    hbox:
                        spacing 10
                        button:
                            xsize 150 ysize 45
                            background ("#4A2E68" if codex_state.selected_outfit_state == "state_a_battle" else "#201830")
                            action [SetField(codex_state, "selected_outfit_state", "state_a_battle"), Function(renpy.restart_interaction)]
                            text "State A: Battle" size 14 color "#FBF8F0" align (0.5, 0.5)

                        button:
                            xsize 150 ysize 45
                            background ("#4A2E68" if codex_state.selected_outfit_state == "state_b_worn" else "#201830")
                            action [SetField(codex_state, "selected_outfit_state", "state_b_worn"), Function(renpy.restart_interaction)]
                            text "State B: Worn" size 14 color "#FBF8F0" align (0.5, 0.5)

                        button:
                            xsize 150 ysize 45
                            background ("#4A2E68" if codex_state.selected_outfit_state == "state_c_camp" else "#201830")
                            action [SetField(codex_state, "selected_outfit_state", "state_c_camp"), Function(renpy.restart_interaction)]
                            text "State C: Camp" size 14 color "#FBF8F0" align (0.5, 0.5)

                        if "state_d_promoted" in active_char.get("wardrobe", {}):
                            button:
                                xsize 160 ysize 45
                                background ("#4A2E68" if codex_state.selected_outfit_state == "state_d_promoted" else "#201830")
                                action [SetField(codex_state, "selected_outfit_state", "state_d_promoted"), Function(renpy.restart_interaction)]
                                text "State D: Ascension" size 14 color "#FFE899" align (0.5, 0.5)

                    $ cur_desc = active_char['wardrobe'].get(codex_state.selected_outfit_state, "")
                    text "[cur_desc]" size 16 color "#E6E0F0"

                    null height 15
                    text "DOSSIER SECRET & LORE" size 20 color "#FFE899" bold True
                    text "[active_char['lore']['secret']]" size 16 color "#C8C0D8" italic True

    # -------------------------------------------------------------------------
    # SUBTAB 2: FELLOWSHIP CG GALLERY
    # -------------------------------------------------------------------------
    elif codex_state.active_subtab == "cgs":
        frame:
            xpos 80 ypos 100 xsize 1760 ysize 940
            background "#181224EE"
            grid 5 2:
                spacing 24
                align (0.5, 0.5)
                $ cg_list = [item for item in codex_state.manifest["assets"] if item["category"] == "story_cg"]
                for cg in cg_list:
                    button:
                        xsize 320 ysize 180
                        background "#221A30"
                        action [SetField(codex_state, "fullscreen_cg", cg["path"]), Function(renpy.restart_interaction)]
                        add cg["path"] xsize 320 ysize 180 fit "cover"

    # -------------------------------------------------------------------------
    # SUBTAB 3: CHRONICLES OF ELTHERIS (WORLD LORE)
    # -------------------------------------------------------------------------
    elif codex_state.active_subtab == "lore":
        frame:
            xpos 140 ypos 120 xsize 1640 ysize 900
            background "#181224EE"
            viewport:
                scrollbars "vertical"
                mousewheel True
                vbox:
                    spacing 20
                    text "THE CHRONICLES OF ELTHERIS" size 32 color "#EBC364" bold True
                    text "The Shattered Sky & The Wellsprings of Aether" size 24 color "#AF78E6" bold True
                    text "Six centuries ago, Eltheris was nearly unmade during the Cataclysm of Falling Stars. Sorcerer-kings tore open the leylines of the world to harvest Aether. Living skin attuned to runic silk conducts celestial energy most potently, leading champions to wear form-fitting Aether-Weave regalia." size 18 color "#C8C0D8"

                    text "The Law of the Sixty-Four Thrones" size 24 color "#AF78E6" bold True
                    text "Over the yawning chasm of The Hollow, sixty-four colossal monolith slabs of Dawnstone and Duskstone were anchored. Total continental war was bound by ancient treaty into the Rite of Thrones: sixteen champions deployed per realm under geometric Geas movement rules." size 18 color "#C8C0D8"

                    text "The Quiet & The Hollow" size 24 color "#AF78E6" bold True
                    text "When a piece is defeated, arcane overload shatters their outer barrier, drawing them into temporal suspended animation beneath the stone. But the ancient seal has degraded; vital life essence is leaking into the abyss beneath." size 18 color "#C8C0D8"

    # Fullscreen CG Lightbox View
    if codex_state.fullscreen_cg:
        button:
            xpos 0 ypos 0 xsize 1920 ysize 1080
            background "#000000FA"
            action [SetField(codex_state, "fullscreen_cg", None), Function(renpy.restart_interaction)]
            add codex_state.fullscreen_cg xalign 0.5 yalign 0.5 xsize 1920 ysize 1080 fit "contain"
