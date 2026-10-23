## war_tent_hub.rpy - War Tent Tactical Camp Hub (Between Battles)
## Complies with Section 2.1 of the Master Build Bible (v3.2)

init python:
    class WarTentUI:
        def __init__(self, camp_manager, chapter_data, roster_data):
            self.camp = camp_manager
            self.chapter_data = chapter_data
            self.roster = roster_data
            self.active_tab = "counsel"  # "counsel", "recon", "archive"
            self.selected_officer_id = None
            self.dialogue_msg = None

        def select_officer(self, char_id):
            self.selected_officer_id = char_id
            self.dialogue_msg = None

        def perform_counsel(self, char_id):
            if self.camp.ap >= 1:
                res = self.camp.counsel_officer(char_id, affinity_gain=15)
                if res["success"]:
                    if res["rank_up"]:
                        self.dialogue_msg = f"Fellowship Rank increased to Rank {res['current_rank']}! New tactical insight unlocked."
                    else:
                        self.dialogue_msg = f"Spent the evening counseling with {char_id.replace('_', ' ').title()}. (+15 Affinity)"

        def perform_recon(self):
            if self.camp.ap >= 1 and not self.camp.recon_buff_active:
                seer_id = "dawn_bishop" if self.camp.faction == "dawn" else "dusk_bishop"
                boss_prof = self.chapter_data.get("boss_profile", "reckless_vanguard")
                notes = self.chapter_data.get("recon_notes", "Enemy exposes their vanguard early.")
                res = self.camp.perform_recon(seer_id, boss_prof, notes=notes)
                if res["success"]:
                    self.dialogue_msg = "Reconnaissance complete! +1 Bonus Starting Aether granted for the upcoming battle."

## ============================================================================
## WAR TENT SCREEN
## ============================================================================

screen war_tent_hub(tent_state):
    modal True

    $ camp = tent_state.camp
    $ faction = camp.faction
    $ bg_camp = "bg/bg_war_tent_dawn.png" if faction == "dawn" else "bg/bg_war_tent_dusk.png"
    add bg_camp fit "cover"

    # -------------------------------------------------------------------------
    # TOP HEADER: Chapter & AP Status
    # -------------------------------------------------------------------------
    frame:
        xpos 0 ypos 0 xsize 1920 ysize 80
        background "#140F22EE"
        hbox:
            align (0.5, 0.5)
            spacing 60
            text "WAR TENT TACTICAL HUB — CHAPTER [camp.chapter]" size 28 color "#EBC364" bold True
            text "EVENING AP: [camp.ap] / [camp.max_ap]" size 24 color ("#80FF80" if camp.ap > 0 else "#FF8080") bold True
            text "CONCORD RATING: [persistent.concord_points]" size 24 color "#AF78E6"

    # -------------------------------------------------------------------------
    # TAB BUTTONS (x=80..600, y=100)
    # -------------------------------------------------------------------------
    hbox:
        xpos 80 ypos 100
        spacing 20
        button:
            xsize 260 ysize 50
            background ("#4A2E68" if tent_state.active_tab == "counsel" else "#201830")
            hover_background "#603A85"
            action [SetVariable("tent_state.active_tab", "counsel"), SetVariable("tent_state.dialogue_msg", None)]
            text "Counsel Quarters (1 AP)" size 20 color "#FBF8F0" align (0.5, 0.5)

        button:
            xsize 280 ysize 50
            background ("#4A2E68" if tent_state.active_tab == "recon" else "#201830")
            hover_background "#603A85"
            action [SetVariable("tent_state.active_tab", "recon"), SetVariable("tent_state.dialogue_msg", None)]
            text "War Table Recon (1 AP)" size 20 color "#FBF8F0" align (0.5, 0.5)

        button:
            xsize 240 ysize 50
            background ("#4A2E68" if tent_state.active_tab == "archive" else "#201830")
            hover_background "#603A85"
            action [SetVariable("tent_state.active_tab", "archive")]
            text "Codex Archive (0 AP)" size 20 color "#FBF8F0" align (0.5, 0.5)

    # -------------------------------------------------------------------------
    # TAB 1: COUNSEL QUARTERS
    # -------------------------------------------------------------------------
    if tent_state.active_tab == "counsel":
        # Officer list
        frame:
            xpos 80 ypos 170 xsize 480 ysize 840
            background "#181224EE"
            vbox:
                spacing 10
                text "CAMP OFFICERS (LOUNGEWEAR)" size 22 color "#EBC364" bold True
                $ faction_chars = [c for c in tent_state.roster if c["faction"] == faction]
                for c in faction_chars:
                    $ cid = c["id"]
                    $ aff = camp.affinity.get(cid, 0)
                    $ rk = camp.fellowship_ranks.get(cid, 0)
                    button:
                        xsize 440 ysize 70
                        background ("#352445" if tent_state.selected_officer_id == cid else "#221A30")
                        hover_background "#452F5A"
                        action Function(tent_state.select_officer, cid)
                        hbox:
                            align (0.5, 0.5)
                            spacing 15
                            add f"ui/advisors/{cid}_bust.png" xsize 50 ysize 50
                            vbox:
                                text "[c['name']]" size 18 color "#FBF8F0" bold True
                                text "Rank [rk] | Affinity [aff]" size 14 color "#C8C0D8"

        # Selected Officer Pavilion Display
        if tent_state.selected_officer_id:
            $ oc = next((c for c in tent_state.roster if c["id"] == tent_state.selected_officer_id), None)
            if oc:
                frame:
                    xpos 580 ypos 170 xsize 1260 ysize 840
                    background "#181224EE"

                    # Officer Camp Sprite (State C)
                    $ camp_sprite = f"characters/{oc['id']}/state_c_camp.png"
                    add camp_sprite:
                        xpos 40 ypos 40
                        xsize 560 ysize 672
                        crop (120, 0, 660, 792)

                    # Info & Fellowship Arc
                    vbox:
                        xpos 640 ypos 60
                        xsize 580
                        spacing 16
                        text "[oc['name'].upper()]" size 32 color "#EBC364" bold True
                        text "[oc['title']]" size 20 color "#AF78E6"
                        text "[oc['wardrobe']['state_c_camp']]" size 16 color "#C8C0D8"

                        $ cur_rk = camp.fellowship_ranks.get(oc['id'], 0)
                        $ cur_aff = camp.affinity.get(oc['id'], 0)
                        text "Fellowship Rank: [cur_rk] / 4  (Affinity: [cur_aff])" size 20 color "#FFE899"

                        # Rank Benefits
                        text "Rank 1 (10): Unlocks Codex Dossier & Lore" size 16 color ("#80FF80" if cur_rk >= 1 else "#808080")
                        text "Rank 2 (25): Enhanced Advisor Tactical Analysis" size 16 color ("#80FF80" if cur_rk >= 2 else "#808080")
                        text "Rank 3 (45): +1 Max Aether Charge in Battles" size 16 color ("#80FF80" if cur_rk >= 3 else "#808080")
                        text "Rank 4 (70): Champion's Oath CG & Epilogue" size 16 color ("#80FF80" if cur_rk >= 4 else "#808080")

                        null height 20

                        if camp.ap >= 1:
                            textbutton "Spend 1 AP to Counsel in Pavilion":
                                text_size 22
                                action Function(tent_state.perform_counsel, oc['id'])
                        else:
                            text "NO ACTION POINTS REMAINING THIS EVENING" size 18 color "#FF8080"

                        if tent_state.dialogue_msg:
                            null height 10
                            text "[tent_state.dialogue_msg]" size 18 color "#80FF80" italic True

    # -------------------------------------------------------------------------
    # TAB 2: WAR TABLE RECONNAISSANCE
    # -------------------------------------------------------------------------
    elif tent_state.active_tab == "recon":
        frame:
            xpos 80 ypos 170 xsize 1760 ysize 840
            background "#181224EE"

            $ seer_char = "dawn_bishop" if faction == "dawn" else "dusk_bishop"
            # Seer in Camp Loungewear
            add f"characters/{seer_char}/state_c_camp.png":
                xpos 60 ypos 40
                xsize 560 ysize 672
                crop (120, 0, 660, 792)

            vbox:
                xpos 660 ypos 60
                xsize 1020
                spacing 20
                text "WAR TABLE RECONNAISSANCE" size 32 color "#EBC364" bold True
                text "Consult with your High Seeress to study the enemy commander's opening vectors and flaws." size 20 color "#C8C0D8"

                frame:
                    background "#221A30"
                    xsize 980 ysize 220
                    vbox:
                        xalign 0.5 yalign 0.5
                        spacing 10
                        text "TARGET COMMANDER: [tent_state.chapter_data.get('boss_char', 'ENEMY BOSS').upper()]" size 24 color "#EBC364" bold True
                        text "AI PROFILE: [tent_state.chapter_data.get('boss_profile', 'reckless_vanguard')]  (ESTIMATED ELO: [tent_state.chapter_data.get('boss_elo', 400)])" size 20 color "#AF78E6"
                        text "TACTICAL RECON NOTES: [tent_state.chapter_data.get('recon_notes', 'Aggressive forward pushes.')]" size 18 color "#FBF8F0"

                if not camp.recon_buff_active:
                    if camp.ap >= 1:
                        textbutton "Consult Seer (1 AP) — Grant +1 Bonus Starting Aether":
                            text_size 24
                            action Function(tent_state.perform_recon)
                    else:
                        text "NO ACTION POINTS REMAINING THIS EVENING" size 18 color "#FF8080"
                else:
                    text "RECON BUFF ACTIVE: +1 Bonus Starting Aether applied for the upcoming match!" size 22 color "#80FF80" bold True

                if tent_state.dialogue_msg:
                    text "[tent_state.dialogue_msg]" size 18 color "#80FF80" italic True

    # -------------------------------------------------------------------------
    # TAB 3: CODEX ARCHIVE LINK
    # -------------------------------------------------------------------------
    elif tent_state.active_tab == "archive":
        frame:
            xpos 80 ypos 170 xsize 1760 ysize 840
            background "#181224EE"
            vbox:
                align (0.5, 0.5)
                spacing 30
                text "THE ARCHIVE OF RECORDS" size 36 color "#EBC364" bold True xalign 0.5
                text "Review character dossiers, unlocked wardrobe state views, and event CGs." size 22 color "#C8C0D8" xalign 0.5
                textbutton "Open Full Codex & CG Gallery":
                    text_size 28
                    xalign 0.5
                    action Show("codex_gallery", transition=dissolve)

    # -------------------------------------------------------------------------
    # BOTTOM ACTION: DEPLOY TO THRONEFIELD
    # -------------------------------------------------------------------------
    textbutton "DEPLOY TO THRONEFIELD":
        xalign 0.5 ypos 1020
        text_size 28
        action Return("battle")
