## thronefield.rpy - 1920x1080 Interactive Tactical Chessboard & HUD
## Complies with Section 5 & Section 6 of the Master Build Bible (v3.2)

init python:
    import math
    import chess
    from core.story_ai import (
        get_war_council_advice,
        predict_boss_move,
        square_to_center_coords,
        get_vector_arrow_transform,
    )

## ============================================================================
## ATL TRANSFORMS (Section 6.2)
## ============================================================================

transform advisor_vector_arrow(x1, y1, length_px, angle_deg):
    xpos x1
    ypos y1
    anchor (0.0, 0.5)
    transform_anchor True
    xsize int(length_px)
    ysize 28
    rotate angle_deg
    rotate_pad False
    alpha 0.88
    linear 0.6 alpha 0.55
    linear 0.6 alpha 0.88
    repeat

transform pulse_glow:
    alpha 0.7
    linear 0.8 alpha 1.0
    linear 0.8 alpha 0.7
    repeat

transform cutin_banner_anim:
    xalign 0.5
    yalign 0.35
    alpha 0.0
    xoffset -200
    easein 0.25 alpha 1.0 xoffset 0
    pause 1.8
    easeout 0.25 alpha 0.0 xoffset 200

## ============================================================================
## THRONEFIELD SCREEN CONTROLLER FUNCTIONS
## ============================================================================

init python:
    class ThronefieldUI:
        def __init__(self, session, detector, chapter_data=None, camp=None, banter=None):
            self.session = session
            self.detector = detector
            self.chapter_data = chapter_data or {}
            self.camp = camp
            self.banter = banter or {}

            self.selected_sq = None
            self.legal_moves_for_selected = []
            self.spell_mode = None  # None, "aegis", "advance"
            self.selected_advisor_idx = None
            self.active_advisors = []
            self.cutin_active = None
            self.battle_log_msg = None

            # If match starts on Boss turn (e.g., Dusk faction vs White-first FEN), execute boss opening move
            if not self.session.board.is_game_over() and not self.session.is_player_turn:
                self.execute_boss_reply()
            else:
                self.refresh_advisors()

        def refresh_advisors(self):
            if not self.session.board.is_game_over() and self.session.is_player_turn:
                is_finale = (self.chapter_data.get("id") == "grand_finale")
                enhanced_ids = []
                if self.camp is not None and hasattr(self.camp, "fellowship_ranks"):
                    enhanced_ids = [
                        cid for cid, rk in self.camp.fellowship_ranks.items() if rk >= 2
                    ]
                self.active_advisors = get_war_council_advice(
                    self.session.board,
                    player_faction=self.session.player_faction,
                    legal_moves=self.session.get_filtered_legal_moves(),
                    include_allied_fourth=is_finale,
                    enhanced_char_ids=enhanced_ids,
                )
            else:
                self.active_advisors = []

        def _get_spell_callout(self, spell_key):
            spells_dict = self.banter.get("spells", {}).get(spell_key, {})
            return spells_dict.get(self.session.player_faction, "")

        def on_square_clicked(self, sq):
            if not self.session.is_player_turn or self.session.board.is_game_over():
                return

            # Spell Mode: Aegis Ward target selection
            if self.spell_mode == "aegis":
                if self.session.can_cast_aegis_ward(sq):
                    self.session.cast_aegis_ward(sq)
                    self.spell_mode = None
                    self.battle_log_msg = self._get_spell_callout("aegis_ward")
                    self.refresh_advisors()
                else:
                    self.spell_mode = None
                return

            # Spell Mode: Marshal's Advance pawn selection
            if self.spell_mode == "advance":
                if self.session.can_cast_marshals_advance(sq):
                    res = self.session.cast_marshals_advance(sq)
                    self.spell_mode = None
                    self.battle_log_msg = self._get_spell_callout("marshals_advance")
                    self._after_player_move(chess.Move.from_uci(f"{res['moved_pawn']}{res['dest_square']}"))
                    self.refresh_advisors()
                else:
                    self.spell_mode = None
                return

            # Normal Piece Selection & Move Execution
            if self.selected_sq is not None:
                # Check if clicking a legal destination
                dest_move = None
                for m in self.legal_moves_for_selected:
                    if m.to_square == sq:
                        dest_move = m
                        break

                if dest_move is not None:
                    # Execute move
                    self.session.push_player_move(dest_move)
                    self._after_player_move(dest_move)
                    self.selected_sq = None
                    self.legal_moves_for_selected = []
                    self.refresh_advisors()

                    # Trigger boss reply if match is ongoing
                    if not self.session.board.is_game_over() and not self.session.is_player_turn:
                        self.execute_boss_reply()
                    return

            # Select piece on square
            piece = self.session.board.piece_at(sq)
            if piece and piece.color == self.session.player_color:
                self.selected_sq = sq
                all_legal = self.session.get_filtered_legal_moves()
                self.legal_moves_for_selected = [m for m in all_legal if m.from_square == sq]
            else:
                self.selected_sq = None
                self.legal_moves_for_selected = []

        def execute_advisor_move(self, advisor_entry):
            if not self.session.is_player_turn or self.session.board.is_game_over():
                return
            move = advisor_entry["move"]
            self.session.push_player_move(move)
            self._after_player_move(move)
            self.selected_sq = None
            self.legal_moves_for_selected = []
            self.refresh_advisors()

            if not self.session.board.is_game_over() and not self.session.is_player_turn:
                self.execute_boss_reply()

        def execute_boss_reply(self):
            boss_prof = self.chapter_data.get("boss_profile", "grand_command")
            res = self.session.push_boss_move(profile_id=boss_prof)
            if res["success"]:
                last_m = chess.Move.from_uci(res["move"])
                self._after_boss_move(last_m)
            self.refresh_advisors()

        def _after_player_move(self, move):
            self.detector.update(self.session.board, last_move=move)
            self._check_cutins()

        def _after_boss_move(self, move):
            self.detector.update(self.session.board, last_move=move)
            self._check_cutins()

        def _check_cutins(self):
            pending = self.detector.pop_pending_cutins()
            if pending:
                self.cutin_active = pending[0]
            else:
                self.cutin_active = None

        def dismiss_cutin(self):
            self.cutin_active = None

        # Spell Activators
        def trigger_chrono_pulse(self):
            if self.session.can_cast_chrono_pulse():
                self.session.cast_chrono_pulse()
                self.selected_sq = None
                self.legal_moves_for_selected = []
                self.battle_log_msg = self._get_spell_callout("chrono_pulse")
                self.refresh_advisors()

        def trigger_oracle_gaze(self):
            if self.session.can_cast_oracle_gaze():
                boss_prof = self.chapter_data.get("boss_profile", "grand_command")
                self.session.cast_oracle_gaze(boss_profile_id=boss_prof)
                self.battle_log_msg = self._get_spell_callout("oracle_gaze")

        def trigger_aegis_ward_mode(self):
            if self.session.aether >= 2 and self.session.is_player_turn:
                self.spell_mode = "aegis" if self.spell_mode != "aegis" else None

        def trigger_marshals_advance_mode(self):
            if self.session.aether >= 2 and self.session.is_player_turn:
                self.spell_mode = "advance" if self.spell_mode != "advance" else None

## ============================================================================
## MAIN THRONEFIELD SCREEN
## ============================================================================

screen thronefield(ui_state):
    modal True

    $ session = ui_state.session
    $ detector = ui_state.detector
    $ board = session.board
    $ is_white = (session.player_faction == "dawn")

    # Background Environment
    $ bg_img = ui_state.chapter_data.get("bg_battle", "bg/bg_thronefield_dawn.png")
    add bg_img fit "cover"

    # -------------------------------------------------------------------------
    # 1. TOP BAR (y=0..70)
    # -------------------------------------------------------------------------
    frame:
        xpos 0 ypos 0 xsize 1920 ysize 70
        background "#151020DD"
        hbox:
            align (0.5, 0.5)
            spacing 60
            text "[ui_state.chapter_data.get('title', 'THRONEFIELD DUEL')]" size 28 color "#EBC364" bold True
            text "TURN: [session.move_count + 1]" size 24 color "#FBF8F0"
            $ delta_val = (detector.player_sprite_state != "state_a_battle")
            text "MATERIAL: [calculate_material_delta(board, session.player_color):+.1f]" size 24 color ("#FF8080" if calculate_material_delta(board, session.player_color) < 0 else "#80FF80")
            text "CONCORD: [session.concord_points]" size 24 color "#AF78E6" bold True

    # -------------------------------------------------------------------------
    # 2. LEFT HUD: PLAYER COMMANDER & SOVEREIGN SPELLS (x=20..610)
    # -------------------------------------------------------------------------
    frame:
        xpos 20 ypos 90 xsize 590 ysize 960
        background "ui/frame_hud_panel.png"

        # Commander Portrait (State A, B, or D)
        $ p_char = detector.player_char_id
        $ p_state = detector.get_character_sprite_state(p_char)
        $ p_sprite = f"characters/{p_char}/{p_state}.png"
        add p_sprite:
            xalign 0.5 ypos 30
            xsize 480 ysize 576
            crop (160, 0, 580, 696)

        # Commander Label & Title
        vbox:
            xalign 0.5 ypos 590
            spacing 4
            text "[p_char.replace('_', ' ').upper()]" size 24 color "#EBC364" bold True xalign 0.5
            text "State: [p_state]" size 18 color "#C8C0D8" xalign 0.5

        # Aether Gauge
        vbox:
            xalign 0.5 ypos 650
            spacing 6
            text "AETHER CHARGES: [session.aether] / [session.max_aether]" size 20 color "#EBC364" xalign 0.5
            hbox:
                xalign 0.5
                spacing 12
                for i in range(session.max_aether):
                    if i < session.aether:
                        add "board/ward_aegis_overlay.png" xsize 24 ysize 24
                    else:
                        add "board/tile_duskstone.png" xsize 24 ysize 24 alpha 0.4

        # 4 Sovereign Spell Buttons
        hbox:
            xalign 0.5 ypos 720
            spacing 16

            # Spell 1: Chrono-Pulse (Cost 1)
            imagebutton:
                idle "ui/spells/spell_chrono.png"
                hover "ui/spells/spell_chrono.png"
                sensitive session.can_cast_chrono_pulse()
                action Function(ui_state.trigger_chrono_pulse)
                tooltip "Chrono-Pulse (1 Aether): Rewind 1 Full Turn"

            # Spell 2: Oracle's Gaze (Cost 1)
            imagebutton:
                idle "ui/spells/spell_oracle.png"
                hover "ui/spells/spell_oracle.png"
                sensitive session.can_cast_oracle_gaze()
                action Function(ui_state.trigger_oracle_gaze)
                tooltip "Oracle's Gaze (1 Aether): Foresee Enemy Move"

            # Spell 3: Aegis Ward (Cost 2)
            imagebutton:
                idle "ui/spells/spell_aegis.png"
                hover "ui/spells/spell_aegis.png"
                sensitive (session.aether >= 2 and session.is_player_turn)
                action Function(ui_state.trigger_aegis_ward_mode)
                tooltip "Aegis Ward (2 Aether): Shield friendly piece for 1 turn"

            # Spell 4: Marshal's Advance (Cost 2)
            imagebutton:
                idle "ui/spells/spell_advance.png"
                hover "ui/spells/spell_advance.png"
                sensitive (session.aether >= 2 and session.is_player_turn)
                action Function(ui_state.trigger_marshals_advance_mode)
                tooltip "Marshal's Advance (2 Aether): 1-Square Pawn Advance without losing turn"

        if ui_state.spell_mode:
            text "MODE: SELECT TARGET FOR [ui_state.spell_mode.upper()]" size 20 color "#FFE899" xalign 0.5 ypos 820 at pulse_glow
        elif ui_state.battle_log_msg:
            text "[ui_state.battle_log_msg]" size 16 color "#FFE899" italic True xalign 0.5 ypos 820 xsize 540 text_align 0.5

    # -------------------------------------------------------------------------
    # 3. CENTER: 640x640 THRONEFIELD CHESSBOARD (x=640..1280, y=120..760)
    # -------------------------------------------------------------------------
    fixed:
        xpos 640 ypos 120 xsize 640 ysize 640

        # Layer 1: 64 Board Tiles
        for sq in range(64):
            $ f = chess.square_file(sq)
            $ r = chess.square_rank(sq)
            $ px = (f if is_white else (7 - f)) * 80
            $ py = ((7 - r) if is_white else r) * 80
            $ is_light = ((f + r) % 2 == 1)

            add ("board/tile_dawnstone.png" if is_light else "board/tile_duskstone.png"):
                xpos px ypos py
                xsize 80 ysize 80

        # Layer 2: Highlight Overlays
        # Selected square
        if ui_state.selected_sq is not None:
            $ sf = chess.square_file(ui_state.selected_sq)
            $ sr = chess.square_rank(ui_state.selected_sq)
            $ spx = (sf if is_white else (7 - sf)) * 80
            $ spy = ((7 - sr) if is_white else sr) * 80
            add "board/highlight_move.png":
                xpos spx ypos spy
                xsize 80 ysize 80

        # Legal target squares
        for lm in ui_state.legal_moves_for_selected:
            $ tf = chess.square_file(lm.to_square)
            $ tr = chess.square_rank(lm.to_square)
            $ tpx = (tf if is_white else (7 - tf)) * 80
            $ tpy = ((7 - tr) if is_white else tr) * 80
            $ is_cap = (board.piece_at(lm.to_square) is not None or board.is_en_passant(lm))
            add ("board/highlight_capture.png" if is_cap else "board/highlight_move.png"):
                xpos tpx ypos tpy
                xsize 80 ysize 80 alpha 0.75

        # Oracle's Gaze Prediction Highlight
        if session.oracle_active and session.oracle_prediction:
            $ op_from = session.oracle_prediction["from_square"]
            $ op_to = session.oracle_prediction["to_square"]
            $ op_f_f = chess.square_file(op_from)
            $ op_f_r = chess.square_rank(op_from)
            $ op_t_f = chess.square_file(op_to)
            $ op_t_r = chess.square_rank(op_to)
            add "board/highlight_oracle.png":
                xpos ((op_f_f if is_white else (7 - op_f_f)) * 80) ypos (((7 - op_f_r) if is_white else op_f_r) * 80)
                xsize 80 ysize 80 at pulse_glow
            add "board/highlight_oracle.png":
                xpos ((op_t_f if is_white else (7 - op_t_f)) * 80) ypos (((7 - op_t_r) if is_white else op_t_r) * 80)
                xsize 80 ysize 80 at pulse_glow

        # Aegis Ward active shield overlay
        if session.warded_square is not None:
            $ wf = chess.square_file(session.warded_square)
            $ wr = chess.square_rank(session.warded_square)
            add "board/ward_aegis_overlay.png":
                xpos ((wf if is_white else (7 - wf)) * 80) ypos (((7 - wr) if is_white else wr) * 80)
                xsize 80 ysize 80 at pulse_glow

        # Check highlight
        if board.is_check():
            $ king_sq = board.king(board.turn)
            if king_sq is not None:
                $ kf = chess.square_file(king_sq)
                $ kr = chess.square_rank(king_sq)
                add "board/highlight_check.png":
                    xpos ((kf if is_white else (7 - kf)) * 80) ypos (((7 - kr) if is_white else kr) * 80)
                    xsize 80 ysize 80 at pulse_glow

        # Layer 3: Interactive Piece Tokens (80x80)
        for sq in range(64):
            $ piece = board.piece_at(sq)
            $ f = chess.square_file(sq)
            $ r = chess.square_rank(sq)
            $ px = (f if is_white else (7 - f)) * 80
            $ py = ((7 - r) if is_white else r) * 80

            if piece is not None:
                $ p_color = "dawn" if piece.color == chess.WHITE else "dusk"
                $ p_type = {chess.KING:"king", chess.QUEEN:"queen", chess.ROOK:"rook", chess.BISHOP:"bishop", chess.KNIGHT:"knight", chess.PAWN:"pawn"}[piece.piece_type]
                $ token_img = f"board/pieces/{p_color}_{p_type}.png"

                imagebutton:
                    xpos px ypos py
                    xsize 80 ysize 80
                    idle token_img
                    hover token_img
                    action Function(ui_state.on_square_clicked, sq)
            else:
                button:
                    xpos px ypos py
                    xsize 80 ysize 80
                    background None
                    action Function(ui_state.on_square_clicked, sq)

    # -------------------------------------------------------------------------
    # Layer 4: Advisor Vector Visuals (ATL Anchored Vectors - Section 6.2)
    # -------------------------------------------------------------------------
    for idx, adv in enumerate(ui_state.active_advisors):
        if ui_state.selected_advisor_idx is None or ui_state.selected_advisor_idx == idx:
            $ vec = adv["vector"]
            add adv["arrow_texture"] at advisor_vector_arrow(vec["x1"], vec["y1"], vec["length"], vec["angle"])

    # -------------------------------------------------------------------------
    # 4. RIGHT HUD: OPPONENT BOSS & STASIS RESERVE (x=1310..1900)
    # -------------------------------------------------------------------------
    frame:
        xpos 1310 ypos 90 xsize 590 ysize 960
        background "ui/frame_hud_panel.png"

        $ b_char = detector.boss_char_id
        $ b_state = detector.get_character_sprite_state(b_char)
        $ b_sprite = f"characters/{b_char}/{b_state}.png"
        add b_sprite:
            xalign 0.5 ypos 30
            xsize 480 ysize 576
            crop (160, 0, 580, 696)

        vbox:
            xalign 0.5 ypos 590
            spacing 4
            text "[b_char.replace('_', ' ').upper()]" size 24 color "#AF78E6" bold True xalign 0.5
            text "ELO: [ui_state.chapter_data.get('boss_elo', 500)] | State: [b_state]" size 18 color "#C8C0D8" xalign 0.5

        # Stasis Reserve: Captured pieces
        vbox:
            xalign 0.5 ypos 650
            spacing 6
            text "STASIS RESERVE (CAPTURED)" size 20 color "#EBC364" xalign 0.5
            hbox:
                xalign 0.5
                spacing 8
                for cap in session.captured_pieces_by_player[:8]:
                    $ cap_name = {chess.PAWN:"pawn", chess.KNIGHT:"knight", chess.BISHOP:"bishop", chess.ROOK:"rook", chess.QUEEN:"queen"}.get(cap, "pawn")
                    $ cap_img = f"board/pieces/{('dusk' if is_white else 'dawn')}_{cap_name}.png"
                    add cap_img xsize 36 ysize 36

    # -------------------------------------------------------------------------
    # 5. BOTTOM BAR: WAR COUNCIL ADVISORS (y=775..1065)
    # -------------------------------------------------------------------------
    frame:
        xpos 640 ypos 775 xsize 640 ysize 285
        background "#181224EE"

        $ num_adv = len(ui_state.active_advisors)
        $ card_w = 150 if num_adv >= 4 else 198
        $ card_spacing = 8 if num_adv >= 4 else 14

        hbox:
            align (0.5, 0.5)
            spacing card_spacing

            for idx, adv in enumerate(ui_state.active_advisors):
                button:
                    xsize card_w ysize 260
                    background ("#302040" if ui_state.selected_advisor_idx == idx else "#201830")
                    hover_background "#402850"
                    action [SetVariable("ui_state.selected_advisor_idx", (None if ui_state.selected_advisor_idx == idx else idx))]

                    vbox:
                        align (0.5, 0.5)
                        spacing 4
                        add f"ui/advisors/{adv['char_id']}_bust.png" xsize 56 ysize 56 xalign 0.5
                        text "[adv['name']]" size 16 color "#EBC364" bold True xalign 0.5
                        text "[adv['role'].upper()]" size 13 color adv['color'] xalign 0.5
                        text "[adv['uci'].upper()]" size 15 color "#FBF8F0" bold True xalign 0.5
                        text "[adv['rationale'][:96]]" size 11 color "#C8C0D8" xalign 0.5 text_align 0.5

                        textbutton "Execute":
                            xalign 0.5
                            text_size 14
                            action Function(ui_state.execute_advisor_move, adv)

    # -------------------------------------------------------------------------
    # 6. ACTION CUT-IN BANNER OVERLAY
    # -------------------------------------------------------------------------
    if ui_state.cutin_active:
        $ banner_file = ui_state.cutin_active["banner"]
        $ cutin_cid = ui_state.cutin_active.get("char_id", "")
        $ cutin_type = ui_state.cutin_active.get("type", "battle_damage")
        $ cutin_quote = (
            ui_state.banter.get("promotion_callouts", {}).get(cutin_cid, "")
            if cutin_type == "ascension"
            else ui_state.banter.get("worn_state_reactions", {}).get(cutin_cid, "")
        )
        button:
            xpos 0 ypos 0 xsize 1920 ysize 1080
            background "#00000088"
            action Function(ui_state.dismiss_cutin)

            add banner_file at cutin_banner_anim:
                xsize 1920 ysize 360

            if cutin_quote:
                frame:
                    xalign 0.5 ypos 620 xsize 1200 ysize 90
                    background "#140F22EE"
                    text "[cutin_quote]" size 22 color "#FFE899" italic True align (0.5, 0.5) text_align 0.5

    # -------------------------------------------------------------------------
    # 7. MATCH OUTCOME MODAL
    # -------------------------------------------------------------------------
    if session.is_game_over:
        $ outcome = session.get_outcome()
        frame:
            align (0.5, 0.5)
            xsize 600 ysize 300
            background "#1F1530F5"

            vbox:
                align (0.5, 0.5)
                spacing 20
                if outcome["winner"] == "player":
                    text "VICTORY ON THE THRONEFIELD" size 32 color "#80FF80" bold True xalign 0.5
                elif outcome["winner"] == "boss":
                    text "DEFEAT — ENTERING THE QUIET" size 32 color "#FF8080" bold True xalign 0.5
                else:
                    text "STALEMATE — THE MONOLITHS REST" size 32 color "#EBC364" bold True xalign 0.5

                text "Termination: [outcome['termination'].upper()]" size 20 color "#C8C0D8" xalign 0.5
                textbutton "Return to War Camp":
                    xalign 0.5
                    text_size 24
                    action Return(outcome)
