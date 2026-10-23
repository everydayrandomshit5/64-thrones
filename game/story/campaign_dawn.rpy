## campaign_dawn.rpy - House Aurelis (Dawn / White) 8-Chapter Campaign & Fellowship Dialogues
## Complies with Section 2.1, Part 3 & Part 4.2 of the Master Build Bible (v3.2)

## ============================================================================
## DAWN CAMPAIGN HELPER: WAR TENT + THRONEFIELD MATCH RUNNER
## ============================================================================

label run_dawn_chapter_battle(chap_idx):
    $ chapters_db = load_campaign_json()
    $ roster_db = load_roster_json()
    $ banter_db = load_banter_json()
    $ chap_data = chapters_db["dawn_campaign"][chap_idx - 1]

    # 1. War Tent Tactical Hub (2 AP) with Pavilion Fellowship Scene Loop
    $ current_camp.start_camp_session(chap_idx)
    $ tent_state = WarTentUI(current_camp, chap_data, roster_db)
    label .dawn_camp_loop:
        call screen war_tent_hub(tent_state)
        $ camp_ret = _return
        if camp_ret == "counsel_scene" and tent_state.last_counseled_char:
            call dawn_camp_fellowship_dialogue(tent_state.last_counseled_char, tent_state.last_counseled_rank)
            jump .dawn_camp_loop

    # Eve of Chapter 8: Check for Fellowship Rank 4 Champion's Oath CG after Camp!
    if chap_idx == 8:
        call dawn_check_rank4_oath

    # 2. Thronefield Chess Match (with Defeat / Regroup Retry Guard)
    $ aether_bonuses = current_camp.get_battle_aether_bonuses()
    $ current_camp.consume_recon_buff()
    $ init_ward = chess.A1 if chap_idx == 6 else None

    label .dawn_battle_attempt:
        $ current_session = MatchSession(
            player_faction="dawn",
            boss_profile_id=chap_data["boss_profile"],
            initial_fen=chap_data["initial_fen"],
            starting_aether=aether_bonuses[1],
            max_aether=aether_bonuses[0],
            initial_warded_square=init_ward
        )
        $ current_session.concord_points = persistent.concord_points
        $ current_detector = EventDetector(
            player_char_id=chap_data["player_char"],
            boss_char_id=chap_data["boss_char"],
            player_faction="dawn"
        )

        $ tf_ui = ThronefieldUI(current_session, current_detector, chap_data, camp=current_camp, banter=banter_db)
        call screen thronefield(tf_ui)
        $ last_match_outcome = _return
        $ chapter_obj_met = current_session.evaluate_chapter_objective(chap_idx)
        $ session_snapshot = current_session.to_dict()
        $ camp_snapshot = current_camp.to_dict()
        $ current_session = None
        $ current_detector = None

        $ match_won = (last_match_outcome and last_match_outcome.get("winner") == "player")
        $ draw_obj_ok = (chap_idx in (3, 7) and last_match_outcome and last_match_outcome.get("winner") == "draw" and chapter_obj_met)
        if not (match_won or draw_obj_ok):
            scene bg_thronefield_dawn with dissolve
            show expression "characters/dawn_queen/state_b_worn.png" as dawn_queen at center with dissolve
            lysandra "Our line has fractured... Sound the retreat to camp before The Quiet takes us all! Regroup and strike again, Commander!"
            hide dawn_queen
            menu:
                "The Thronefield clash ended without victory:"
                "Regroup and Retry This Thronefield Match":
                    jump .dawn_battle_attempt
    return

## ============================================================================
## DAWN CHAPTERS 1 - 4
## ============================================================================

label dawn_ch1_start:
    $ current_chapter_idx = 1
    scene bg_thronefield_dawn with fade
    show expression "characters/dawn_queen/state_a_battle.png" as dawn_queen at left
    show expression "characters/dawn_pawn_lead/state_a_battle.png" as dawn_pawn_lead at right
    with dissolve

    narrator "Chapter 1: First Light on the Stone — The Eastern Ridge of the Thronefield."
    lysandra "Eyes front, Vanguard! The morning sun strikes the Dawnstone monoliths, and Umbrenholt's forward scouts are already testing the first file."
    tamsin "General Lysandra, Commander! The First File is formed and ready. My buckler is strapped tight—we won't yield a single slab!"
    lysandra "Well spoken, Tamsin. Commander, let us convene in the War Tent before taking the field against Nyssara's vanguard."

    hide dawn_queen
    hide dawn_pawn_lead
    call run_dawn_chapter_battle(1)

    scene bg_thronefield_dawn with dissolve
    show expression "characters/dawn_queen/state_a_battle.png" as dawn_queen at center with dissolve
    lysandra "Their reckless vanguard line is broken! Several young Umbrenholt conscripts are trapped along the fourth rank before The Quiet claims them."
    menu:
        "How do you handle the routed Umbrenholt vanguard?"
        "Lower blades and allow their conscripts safe passage off the monolith (+1 Concord)":
            $ persistent.concord_points += 1
            lysandra "Honor above bloodlust. A true strategist conquers the field without needless slaughter."
        "Press the advance and secure every stone without quarter":
            lysandra "A stern decree, Commander. The front line is unconditionally ours."
    jump dawn_ch2_start

label dawn_ch2_start:
    $ current_chapter_idx = 2
    scene bg_thronefield_dawn with fade
    show expression "characters/dawn_knight/state_a_battle.png" as dawn_knight at left
    show expression "characters/dawn_queen/state_a_battle.png" as dawn_queen at right
    with dissolve

    narrator "Chapter 2: Wings in the Updraft — High Aerie Recon Post."
    kestrel "Pennant caught a strange updraft over the chasm, Commander! Huntress Kaelen and her shadow-wolves are prowl-leaping along the flank monoliths."
    kestrel "More than that... I spotted an old Solhaven sky-knight beacon wedged in the fissure—just like the one my sibling carried before vanishing."
    lysandra "Keep your heart steady, Captain Rowan. We will break Kaelen's cavalry forks and recover that beacon together."

    hide dawn_knight
    hide dawn_queen
    call run_dawn_chapter_battle(2)

    scene bg_thronefield_dawn with dissolve
    show expression "characters/dawn_knight/state_a_battle.png" as dawn_knight at center with dissolve
    kestrel "Ha! Skyfall takes the skies! And look—we recovered the scout cipher from the chasm rim, alongside one of Kaelen's wounded outriders."
    menu:
        "How do you proceed with the border cipher and outrider?"
        "Log the anomalous rift cipher and release the wounded wolf-scout (+1 Concord)":
            $ persistent.concord_points += 1
            kestrel "Good call, Commander. These rift readings prove the chasm itself is destabilizing."
        "Seize the relay and fortify the aerial flank":
            kestrel "Copy that! No shadow-wolf leaps past our watch tonight."
    jump dawn_ch3_start

label dawn_ch3_start:
    $ current_chapter_idx = 3
    scene bg_thronefield_dawn with fade
    show expression "characters/dawn_rook/state_a_battle.png" as dawn_rook at left
    show expression "characters/dawn_pawn_lead/state_a_battle.png" as dawn_pawn_lead at right
    with dissolve

    narrator "Chapter 3: The Bastion of Dawn — The Central Monolith Defile."
    brannoch "Plant your tower shields deep! Warden Dravok Kell brings the Iron Wall of Umbrenholt down the central file."
    tamsin "Uncle Brannoch, the kinetic tremors from his gravity warhammer are shaking the stone!"
    brannoch "Let the mountain fall if it must, Tamsin—the Alabaster Bastion does not move! Commander, direct our defensive vectors."

    hide dawn_rook
    hide dawn_pawn_lead
    call run_dawn_chapter_battle(3)

    scene bg_thronefield_dawn with dissolve
    show expression "characters/dawn_rook/state_a_battle.png" as dawn_rook at center with dissolve
    brannoch "Dravok's iron line is repelled! The old veteran saluted our shield-wall before withdrawing his battered levies."
    menu:
        "How do you answer Warden Dravok's withdrawal?"
        "Return the knightly salute and refrain from striking the retreating guards (+1 Concord)":
            $ persistent.concord_points += 1
            brannoch "A worthy soldier knows when steel has spoken enough. Dravok will remember this honor."
        "Dismantle their forward barricades to cement our file control":
            brannoch "Done. The central rampart belongs to House Aurelis."
    jump dawn_ch4_start

label dawn_ch4_start:
    $ current_chapter_idx = 4
    scene bg_prism_observatory with fade
    show expression "characters/dawn_bishop/state_a_battle.png" as dawn_bishop at left
    show expression "characters/dawn_queen/state_a_battle.png" as dawn_queen at right
    with dissolve

    narrator "Chapter 4: The Prism Observatory — The Starlit Spire above the Rift."
    ilyara "Commander... feel the Aether currents here. My skin burns with their resonance. The Arbiter Automaton has no living soul-thread—it is running on a corrupted loop!"
    lysandra "Moonweaver Veyra's umbral lanterns are already refracting across the diagonal lenses. Protect High Seeress Ilyara while she records the glyph cipher!"

    hide dawn_bishop
    hide dawn_queen
    call run_dawn_chapter_battle(4)

    scene bg_prism_observatory with dissolve
    show expression "characters/dawn_bishop/state_a_battle.png" as dawn_bishop at center with dissolve
    ilyara "The prism lenses hold! Look at the refracted starlight, Commander—the Champions drawn into The Quiet aren't resting peacefully. Their vitality is draining into The Hollow!"
    menu:
        "What do you do with the Prism Observatory's astral optics?"
        "Preserve the optics intact and transmit the warning cipher across the valley (+1 Concord)":
            $ persistent.concord_points += 1
            ilyara "May Moonweaver Veyra read our starlight and realize the danger we all share."
        "Overcharge the prism to blind Umbrenholt's divinations":
            ilyara "The flare will shield our movements, though it pains me to scorch such ancient glass."
    jump dawn_ch5_start

## ============================================================================
## DAWN CHAPTERS 5 - 8
## ============================================================================

label dawn_ch5_start:
    $ current_chapter_idx = 5
    scene bg_sunken_foundry with fade
    show expression "characters/dawn_pawn_lead/state_a_battle.png" as dawn_pawn_lead at left
    show expression "characters/dawn_queen/state_a_battle.png" as dawn_queen at right
    with dissolve

    narrator "Chapter 5: The Sunken Foundry — The Submerged Mythril Vaults."
    tamsin "The water is ankle-deep over the runic tiles, Commander, and Vanguard Scribe Sorrel's raiders are scouring the drowned archive!"
    lysandra "They are searching for the original First Concord plates. Hold the line, Tamsin—if you reach the eighth rank, the Solar Ascension is yours!"

    hide dawn_pawn_lead
    hide dawn_queen
    call run_dawn_chapter_battle(5)

    scene bg_sunken_foundry with dissolve
    show expression "characters/dawn_pawn_lead/state_a_battle.png" as dawn_pawn_lead at center with dissolve
    tamsin "We secured the mythril tablet! And Sorrel dropped a waterproof scroll case during her retreat—it shows the Arbiter's clauses were altered centuries ago!"
    menu:
        "How do you handle the Sunken Foundry aftermath?"
        "Spare Sorrel's vanguard detachment and preserve the treaty fragment (+1 Concord)":
            $ persistent.concord_points += 1
            tamsin "They're sworn soldiers just like us. I'm glad we stayed our spears, Commander!"
        "Seal the foundry floodgates to lock out Umbrenholt's scribes":
            tamsin "Floodgates locked! The relics are safe in Solhaven's hands."
    jump dawn_ch6_start

label dawn_ch6_start:
    $ current_chapter_idx = 6
    scene bg_quarters_dawn with fade
    show expression "characters/dawn_king/state_c_camp.png" as dawn_king at left
    show expression "characters/dawn_queen/state_c_camp.png" as dawn_queen at right
    with dissolve

    narrator "Chapter 6: The Sovereign's Oath — The Royal Pavilion at Midnight."
    aurelian "Twenty years ago, Commander, I stood above the chasm when the first hairline fracture opened. I poured my own royal lifeblood into the Dawnstone to seal it."
    aurelian "Now Emperor Malachar marches his regicide assassins toward my throne, believing Solhaven broke the seal at Ashgate. We must survive his onslaught and force him to see reason."
    lysandra "Sir Brannoch has placed an Aegis Ward upon our vanguard. None shall touch the Lion of Solhaven while I draw breath."

    hide dawn_king
    hide dawn_queen
    call run_dawn_chapter_battle(6)

    scene bg_thronefield_dawn with dissolve
    show expression "characters/dawn_king/state_a_battle.png" as dawn_king at center with dissolve
    aurelian "Malachar's regicide strike has been parried. Across the monoliths, I see the exhaustion in his eyes—he carries the same dread of The Hollow that I do."
    menu:
        "How do you address Emperor Malachar after the royal clash?"
        "Send a royal envoy bearing proof of the failing seal beneath the board (+1 Concord)":
            $ persistent.concord_points += 1
            aurelian "Let truth bridge the chasm where steel could not. Well advised, my Strategist."
        "Fortify the royal guard for the final push":
            aurelian "Then we prepare for the endgame with unyielding resolve."
    jump dawn_ch7_start

label dawn_ch7_start:
    $ current_chapter_idx = 7
    scene bg_river_parley with fade
    $ unlock_cg("cgs/cg_03_river_parley.png")
    show expression "cgs/cg_03_river_parley.png" with dissolve

    narrator "Chapter 7: Parley at the River — A Mist-Veiled Neutral Crossing at Midnight."
    narrator "Under cover of darkness, Grand Marshal Lysandra and Regent Nyssara meet beside the lantern-lit water, their blades sheathed as they lay their recovered scrolls side by side."
    lysandra "So your Obsidian Archive proved it too, Nyssara. The sabotage at Ashgate was triggered by a dormant fail-safe inside the Arbiter Automaton itself."
    nyssara "The automaton is harvesting the Aether of every champion cast into The Quiet to rebuild its ancient creator's core—while letting The Hollow devour what remains."
    lysandra "Yet the Geas watches us even now. If we do not cross blades tomorrow on the seventh monolith, the Arbiter will purge both camps immediately."
    nyssara "Then give me an honorable bout worthy of the Sunblade, Lysandra—and let us see if your Commander's nerves match your beauty."

    hide expression "cgs/cg_03_river_parley.png"
    call run_dawn_chapter_battle(7)

    scene bg_river_parley with dissolve
    show expression "characters/dawn_queen/state_a_battle.png" as dawn_queen at left
    show expression "characters/dusk_queen/state_a_battle.png" as dusk_queen at right
    with dissolve
    nyssara "A thrilling dance, Commander. You protected your Queen admirably."
    menu:
        "Before parting at the river, what do you offer Regent Nyssara?"
        "Share the final unredacted treaty clause to synchronize our spells (+1 Concord)":
            $ persistent.concord_points += 1
            nyssara "We have an accord, Strategist. When the eighth stone rises, watch for my signal."
        "Keep the final solar cipher closely guarded within House Aurelis":
            nyssara "Ever cautious. Then we shall see whose will prevails at the climax."
    jump dawn_ch8_start

label dawn_ch8_start:
    $ current_chapter_idx = 8
    scene bg_thronefield_eclipse with fade
    show expression "characters/dawn_queen/state_a_battle.png" as dawn_queen at left
    show expression "characters/dawn_bishop/state_a_battle.png" as dawn_bishop at right
    with dissolve

    narrator "Chapter 8: The Final Dawnstone — Beneath the Eclipsed Sky."
    ilyara "The sky above the Thronefield has fractured into solar and umbral vortices! The Arbiter's runes are glowing blood-red!"
    lysandra "This is the climax of the Rite, Commander. Deliver checkmate across the final monolith—and if our Concord holds true, we will shatter the Arbiter's chains together!"

    hide dawn_queen
    hide dawn_bishop
    call run_dawn_chapter_battle(8)

    scene bg_thronefield_eclipse with dissolve
    show expression "characters/dawn_queen/state_a_battle.png" as dawn_queen at left
    show expression "characters/dusk_queen/state_b_worn.png" as dusk_queen at right
    with dissolve

    narrator "Umbrenholt's formation is placed in final checkmate! As the monoliths shudder above the yawning abyss of The Hollow, the Arbiter Automaton commands you to deliver the final execution strike."

    if persistent.concord_points >= 3:
        lysandra "Commander! Our Concord Rating is [persistent.concord_points]! Nyssara and her Seers are aligned with our frequency—we can refuse the Arbiter's decree and unite our courts!"
        menu:
            "The fate of Eltheris hangs on your command:"
            "Cease Hostilities — Unite Dawn and Dusk against the Corrupted Arbiter! (Grand Finale)":
                jump grand_finale_unbroken_concord
            "Strike the final blow and claim absolute Solar Dominance for House Aurelis":
                jump ending_solar_dominance
    else:
        lysandra "The rift trembles, and without sufficient trust between the courts (Concord: [persistent.concord_points]/3), only military dominion remains!"
        jump ending_solar_dominance

## ============================================================================
## DAWN RANK 4 CHAMPION'S OATH SCENES & CAMP FELLOWSHIP DIALOGUES
## ============================================================================

label dawn_check_rank4_oath:
    if current_camp and current_camp.fellowship_ranks.get("dawn_queen", 0) >= 4:
        scene bg_quarters_dawn with dissolve
        $ unlock_cg("cgs/cg_04_lysandra_oath.png")
        show expression "cgs/cg_04_lysandra_oath.png" with dissolve
        narrator "On the eve of the final battle, Grand Marshal Lysandra invites you into her candlelit pavilion. Dressed in her cropped crimson velvet bolero and high-waisted black leather miniskirt, she leans close across the illuminated war table."
        lysandra "For years, I fought only to clear the Verel name and serve the Crown. Every scar, every duel was bound by duty alone."
        lysandra "My blade has answered to the Crown. Tonight, Commander, all that I am—heart, body, and steel—answers to our shared vision."
        hide expression "cgs/cg_04_lysandra_oath.png" with dissolve

    if current_camp and current_camp.fellowship_ranks.get("dawn_bishop", 0) >= 4:
        scene bg_quarters_dawn with dissolve
        $ unlock_cg("cgs/cg_06_ilyara_astrolabe.png")
        show expression "cgs/cg_06_ilyara_astrolabe.png" with dissolve
        narrator "Starlight streams into High Seeress Ilyara's tent, reflecting off her translucent sapphire silk night-wrap and cropped white lace bralette as she unveils the true ancient map of Eltheris."
        ilyara "Through my ley-attuned skin, I have felt the cold loneliness of the stars... until your hand steadied mine, Commander. Tonight, my soul resonates only with yours."
        hide expression "cgs/cg_06_ilyara_astrolabe.png" with dissolve

    if current_camp and current_camp.fellowship_ranks.get("dawn_knight", 0) >= 4:
        scene bg_thronefield_dawn with dissolve
        $ unlock_cg("cgs/cg_08_kestrel_skyfall.png")
        show expression "cgs/cg_08_kestrel_skyfall.png" with dissolve
        narrator "High on the windswept aerie overlooking the monoliths, Cavalier-Captain Kestrel Rowan stands beside her griffin Pennant, her unzipped cropped leather flight jacket fluttering open in the dawn updraft."
        kestrel "I used to fly reckless because I thought nothing on the ground was worth coming back to. You changed that, Commander. Wherever you lead tomorrow, Skyfall rides at your wing!"
        hide expression "cgs/cg_08_kestrel_skyfall.png" with dissolve
    return

label dawn_camp_fellowship_dialogue(char_id, rank):
    scene bg_quarters_dawn with dissolve
    show expression f"characters/{char_id}/state_c_camp.png" at center with dissolve

    if char_id == "dawn_queen":
        if rank == 1:
            lysandra "Ah, Commander. Come in—don't mind the crimson bolero, heavy plate grows stifling after a long march. Let us review our vanguard parries."
        elif rank == 2:
            lysandra "Every piece we move on that stone is a sworn life. When I cleared my family's name in the royal tourneys, I swore never to spend a soldier's blood lightly."
        elif rank == 3:
            lysandra "Pour yourself a glass of Solhaven reserve, Commander. Sitting beside you in the warm brazier light makes even this war feel bearable. (+1 Max Aether Unlocked!)"
        else:
            lysandra "Whatever awaits us on the eighth monolith, my rapier and my heart are yours."
    elif char_id == "dawn_bishop":
        if rank == 1:
            ilyara "Welcome to my pavilion, Commander. The silk night-wrap helps cool my skin after channeling prism vectors all afternoon."
        elif rank == 2:
            ilyara "Because my skin conducts Aether directly, every diagonal spell sends a feverish warmth through my chest. Your calm commands help anchor my focus."
        elif rank == 3:
            ilyara "Place your fingers on the astrolabe ring with mine... can you feel how our pulses synchronize the crystal? (+1 Max Aether Unlocked!)"
        else:
            ilyara "The stars have already written our concord, Commander."
    elif char_id == "dawn_knight":
        if rank == 1:
            kestrel "Hey there, Commander! Pennant just finished his evening rations. Like the flight jacket? Much easier to breathe without the breastplate!"
        elif rank == 2:
            kestrel "My older sibling vanished over the Thronefield rift three years ago. That's why I master every L-leap vector—to leave no blind spot unsearched."
        elif rank == 3:
            kestrel "Stay a while by the fire! With you calling the flanking leaps, I feel unstoppable. (+1 Max Aether Unlocked!)"
        else:
            kestrel "Sky and stone, Commander—I'm yours to the very end!"
    elif char_id == "dawn_pawn_lead":
        if rank == 1:
            tamsin "C-Commander! Sorry, I was just mending my squire's blouse... Please, sit! Let's go over the first-file shield drills!"
        elif rank == 2:
            tamsin "Sometimes looking at The Quiet terrifies me... but knowing Uncle Brannoch and you are watching over the vanguard gives me courage."
        elif rank == 3:
            tamsin "Look! I mastered the rapid advance step we practiced! I'll march all the way to the eighth rank for you! (+1 Max Aether Unlocked!)"
        else:
            tamsin "The Maiden of the First File pledges her spear to you forever, Commander!"
    elif char_id == "dawn_rook":
        if rank == 1:
            brannoch "Take a seat by the workbench, Commander. Carving these little cedar shields keeps my hands steady between battles."
        elif rank == 2:
            brannoch "Every fallen squire's name is etched inside my tower shield. Keep Tamsin and the young ones safe, and I'll stop an avalanche for you."
        elif rank == 3:
            brannoch "Our defensive coordination is the finest I've seen in forty winters. (+1 Max Aether Unlocked!)"
        else:
            brannoch "By the Alabaster Bastion, my shield is yours until my last breath."
    elif char_id == "dawn_king":
        if rank == 1:
            aurelian "Enter, Strategist. Even a King must unlace his mantle and study the raw topography when night falls."
        elif rank == 2:
            aurelian "Heavy is the crown that hides a dying seal from its own people. You carry half my burden with every victory."
        elif rank == 3:
            aurelian "Drink with me, my friend. House Aurelis has never had a finer mind at its helm. (+1 Max Aether Unlocked!)"
        else:
            aurelian "By royal decree, you are named Chief Marshal and Sworn Brother of Solhaven."

    hide expression f"characters/{char_id}/state_c_camp.png" with dissolve
    return
