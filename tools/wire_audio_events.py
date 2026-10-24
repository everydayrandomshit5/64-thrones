"""
wire_audio_events.py - Wires BGM and SFX triggers into Ren'Py story and UI scripts.
"""

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

def update_thronefield():
    path = ROOT_DIR / "game" / "ui" / "thronefield.rpy"
    content = path.read_text(encoding="utf-8")

    # Replace methods
    old_block = """        def _after_player_move(self, move):
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
                self.spell_mode = "advance" if self.spell_mode != "advance" else None"""

    new_block = """        def _after_player_move(self, move):
            self.detector.update(self.session.board, last_move=move)
            self._check_cutins()
            self._play_move_sfx(move)

        def _after_boss_move(self, move):
            self.detector.update(self.session.board, last_move=move)
            self._check_cutins()
            self._play_move_sfx(move)

        def _play_move_sfx(self, move):
            try:
                if self.session.board.is_checkmate():
                    renpy.sound.play("audio/sfx_checkmate.wav")
                elif self.session.board.is_check():
                    renpy.sound.play("audio/sfx_check.wav")
                elif self.session.board.is_capture(move):
                    renpy.sound.play("audio/sfx_piece_capture.wav")
                else:
                    renpy.sound.play("audio/sfx_piece_move.wav")
            except Exception:
                pass

        def _check_cutins(self):
            pending = self.detector.pop_pending_cutins()
            if pending:
                self.cutin_active = pending[0]
                try:
                    renpy.sound.play("audio/sfx_armor_break.wav")
                except Exception:
                    pass
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
                try:
                    renpy.sound.play("audio/sfx_chrono_pulse.wav")
                except Exception:
                    pass

        def trigger_oracle_gaze(self):
            if self.session.can_cast_oracle_gaze():
                boss_prof = self.chapter_data.get("boss_profile", "grand_command")
                self.session.cast_oracle_gaze(boss_profile_id=boss_prof)
                self.battle_log_msg = self._get_spell_callout("oracle_gaze")
                try:
                    renpy.sound.play("audio/sfx_spell_cast.wav")
                except Exception:
                    pass

        def trigger_aegis_ward_mode(self):
            if self.session.aether >= 2 and self.session.is_player_turn:
                self.spell_mode = "aegis" if self.spell_mode != "aegis" else None
                try:
                    renpy.sound.play("audio/sfx_button_click.wav")
                except Exception:
                    pass

        def trigger_marshals_advance_mode(self):
            if self.session.aether >= 2 and self.session.is_player_turn:
                self.spell_mode = "advance" if self.spell_mode != "advance" else None
                try:
                    renpy.sound.play("audio/sfx_button_click.wav")
                except Exception:
                    pass"""

    # Normalize line endings for replacement
    content_norm = content.replace("\r\n", "\n")
    old_norm = old_block.replace("\r\n", "\n")
    new_norm = new_block.replace("\r\n", "\n")

    if old_norm in content_norm:
        content_norm = content_norm.replace(old_norm, new_norm, 1)
        path.write_text(content_norm.replace("\n", "\r\n"), encoding="utf-8")
        print("Updated game/ui/thronefield.rpy with SFX triggers.")
    else:
        print("thronefield.rpy target block not found!")


def update_script_rpy():
    path = ROOT_DIR / "game" / "script.rpy"
    content = path.read_text(encoding="utf-8").replace("\r\n", "\n")

    # Add audio defines
    audio_defines = """## Audio Track Definitions
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
"""

    if "define audio.bgm_ashgate" not in content:
        content = content.replace("## Character Dialogue Definitions", f"{audio_defines}\n## Character Dialogue Definitions", 1)

    # Add play music to label start
    if "play music audio.bgm_ashgate" not in content:
        content = content.replace(
            "label start:\n    scene bg_ashgate_hall fit cover\n    with dissolve",
            "label start:\n    play music audio.bgm_ashgate fadein 1.0\n    scene bg_ashgate_hall fit cover\n    with dissolve"
        )

    path.write_text(content.replace("\n", "\r\n"), encoding="utf-8")
    print("Updated game/script.rpy with audio defines and title music.")


def update_prologue_rpy():
    path = ROOT_DIR / "game" / "story" / "prologue.rpy"
    content = path.read_text(encoding="utf-8").replace("\r\n", "\n")

    if "play music audio.bgm_parley" not in content:
        content = content.replace(
            "label prologue_start:\n    $ persistent.concord_points = 0",
            "label prologue_start:\n    play music audio.bgm_parley fadein 1.0\n    $ persistent.concord_points = 0"
        )
    if "play sound audio.sfx_armor_break" not in content:
        content = content.replace(
            '    narrator "Before you can speak to confirm Nyssara\'s deduction, the runic chandeliers overhead flare a violent, corrupted crimson."\n\n    with vpunch',
            '    narrator "Before you can speak to confirm Nyssara\'s deduction, the runic chandeliers overhead flare a violent, corrupted crimson."\n\n    play sound audio.sfx_armor_break\n    play music audio.bgm_ashgate fadein 0.5\n    with vpunch'
        )

    path.write_text(content.replace("\n", "\r\n"), encoding="utf-8")
    print("Updated game/story/prologue.rpy with BGM & SFX.")


def update_campaign_dawn_rpy():
    path = ROOT_DIR / "game" / "story" / "campaign_dawn.rpy"
    content = path.read_text(encoding="utf-8").replace("\r\n", "\n")

    if "play music audio.bgm_dawn" not in content:
        content = content.replace(
            "label dawn_ch1_start:\n    $ current_chapter_idx = 1",
            "label dawn_ch1_start:\n    play music audio.bgm_dawn fadein 1.0\n    $ current_chapter_idx = 1"
        )
    if "play music audio.bgm_war_tent" not in content:
        content = content.replace(
            "label dawn_camp_fellowship:\n    scene bg_war_tent_dawn",
            "label dawn_camp_fellowship:\n    play music audio.bgm_war_tent fadein 1.0\n    scene bg_war_tent_dawn"
        )

    path.write_text(content.replace("\n", "\r\n"), encoding="utf-8")
    print("Updated game/story/campaign_dawn.rpy with BGM.")


def update_campaign_dusk_rpy():
    path = ROOT_DIR / "game" / "story" / "campaign_dusk.rpy"
    content = path.read_text(encoding="utf-8").replace("\r\n", "\n")

    if "play music audio.bgm_dusk" not in content:
        content = content.replace(
            "label dusk_ch1_start:\n    $ current_chapter_idx = 1",
            "label dusk_ch1_start:\n    play music audio.bgm_dusk fadein 1.0\n    $ current_chapter_idx = 1"
        )
    if "play music audio.bgm_war_tent" not in content:
        content = content.replace(
            "label dusk_camp_fellowship:\n    scene bg_war_tent_dusk",
            "label dusk_camp_fellowship:\n    play music audio.bgm_war_tent fadein 1.0\n    scene bg_war_tent_dusk"
        )

    path.write_text(content.replace("\n", "\r\n"), encoding="utf-8")
    print("Updated game/story/campaign_dusk.rpy with BGM.")


def update_finale_endings_rpy():
    path = ROOT_DIR / "game" / "story" / "finale_endings.rpy"
    content = path.read_text(encoding="utf-8").replace("\r\n", "\n")

    if "play music audio.bgm_climax" not in content:
        content = content.replace(
            "label finale_concord_start:\n    $ persistent.completed_campaigns.append(current_faction)",
            "label finale_concord_start:\n    play music audio.bgm_climax fadein 1.0\n    $ persistent.completed_campaigns.append(current_faction)"
        )
    if "play music audio.bgm_epilogue" not in content:
        content = content.replace(
            "label epilogue_sunblade_vow:\n    scene bg_quarters_dawn",
            "label epilogue_sunblade_vow:\n    play music audio.bgm_epilogue fadein 1.0\n    scene bg_quarters_dawn"
        )

    path.write_text(content.replace("\n", "\r\n"), encoding="utf-8")
    print("Updated game/story/finale_endings.rpy with BGM.")


if __name__ == "__main__":
    update_thronefield()
    update_script_rpy()
    update_prologue_rpy()
    update_campaign_dawn_rpy()
    update_campaign_dusk_rpy()
    update_finale_endings_rpy()
