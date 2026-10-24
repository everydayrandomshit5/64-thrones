## campaign_dusk.rpy - The Umbrenholt Dominion (Dusk / Black) 8-Chapter Campaign & Fellowship Dialogues
## Complies with Section 2.1, Part 3 & Part 4.2 of the Master Build Bible (v3.2)

## ============================================================================
## DUSK CAMPAIGN HELPER: WAR TENT + THRONEFIELD MATCH RUNNER
## ============================================================================

label run_dusk_chapter_battle(chap_idx):
    $ chapters_db = load_campaign_json()
    $ roster_db = load_roster_json()
    $ banter_db = load_banter_json()
    $ chap_data = chapters_db["dusk_campaign"][chap_idx - 1]

    # 1. War Tent Tactical Hub (2 AP) with Pavilion Fellowship Scene Loop
    $ current_camp.start_camp_session(chap_idx)
    $ tent_state = WarTentUI(current_camp, chap_data, roster_db)
    label .dusk_camp_loop:
        call screen war_tent_hub(tent_state)
        $ camp_ret = _return
        if camp_ret == "counsel_scene" and tent_state.last_counseled_char:
            call dusk_camp_fellowship_dialogue(tent_state.last_counseled_char, tent_state.last_counseled_rank)
            jump .dusk_camp_loop

    # Eve of Chapter 8: Check for Fellowship Rank 4 Champion's Oath CG after Camp!
    if chap_idx == 8:
        call dusk_check_rank4_oath

    # 2. Thronefield Chess Match (with Defeat / Regroup Retry Guard)
    $ aether_bonuses = current_camp.get_battle_aether_bonuses()
    $ current_camp.consume_recon_buff()
    $ init_ward = chess.A8 if chap_idx == 6 else None

    label .dusk_battle_attempt:
        $ current_session = MatchSession(
            player_faction="dusk",
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
            player_faction="dusk"
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
            scene bg_thronefield_dusk with dissolve
            show expression "characters/dusk_queen/state_b_worn.png" as dusk_queen at center with dissolve
            nyssara "The monoliths fall silent... Pull back to my pavilion before The Quiet claims our vanguard. Regroup and strike again, Commander!"
            hide dusk_queen
            menu:
                "The Thronefield clash ended without victory:"
                "Regroup and Retry This Thronefield Match":
                    jump .dusk_battle_attempt
    return

## ============================================================================
## DUSK CHAPTERS 1 - 4
## ============================================================================

label dusk_ch1_start:
    play music audio.bgm_dusk fadein 1.0
    $ current_chapter_idx = 1
    scene bg_thronefield_dusk with fade
    show expression "characters/dusk_queen/state_a_battle.png" as dusk_queen at left
    show expression "characters/dusk_pawn_lead/state_a_battle.png" as dusk_pawn_lead at right
    with dissolve

    narrator "Chapter 1: Lanterns in the Gorge — The Western Obsidian Ridge."
    nyssara "Look how eagerly Solhaven's vanguard marches onto the Duskstone, Commander. They mistake our shadow for weakness."
    sorrel "Regent Nyssara! I've finished charting the leyline elevations along the first rank. If we lure their reckless pawns forward, our files will slice right through them!"
    nyssara "Clever girl, Sorrel. Come, Commander—let us prepare in my pavilion before teaching House Aurelis the price of haste."

    hide dusk_queen
    hide dusk_pawn_lead
    call run_dusk_chapter_battle(1)

    scene bg_thronefield_dusk with dissolve
    show expression "characters/dusk_queen/state_a_battle.png" as dusk_queen at center with dissolve
    nyssara "Their forward line has collapsed into our trap. Several young Solhaven squires stand disarmed at the edge of the monolith."
    menu:
        "What is your command regarding the disarmed Solhaven squires?"
        "Stay the whip-blade and allow them to retreat before The Quiet takes them (+1 Concord)":
            $ persistent.concord_points += 1
            nyssara "Mercy from the shadows? Mmm... a calculated kindness, Commander. Lysandra will take note."
        "Bind their positions and claim full dominion of the gorge":
            nyssara "Cold and decisive. The first monolith is ours."
    jump dusk_ch2_start

label dusk_ch2_start:
    $ current_chapter_idx = 2
    scene bg_thronefield_dusk with fade
    show expression "characters/dusk_knight/state_a_battle.png" as dusk_knight at left
    show expression "characters/dusk_queen/state_a_battle.png" as dusk_queen at right
    with dissolve

    narrator "Chapter 2: Shadows in the Basin — Midnight Perimeter Watch."
    kaelen "Gloam caught the scent an hour ago, Commander. Solhaven's griffin riders are circling the flank—and the chasm below is leaking a strange, hollow frost."
    nyssara "Captain Kestrel thinks her aerial leaps can outmaneuver our Nightrunners. Show her how sharper fangs hunt in the dark, Kaelen."

    hide dusk_knight
    hide dusk_queen
    call run_dusk_chapter_battle(2)

    scene bg_thronefield_dusk with dissolve
    show expression "characters/dusk_knight/state_a_battle.png" as dusk_knight at center with dissolve
    kaelen "The sky-knights are grounded! My wolves also uncovered a fractured Aether resonator near the fissure—it's draining life force straight down into the abyss."
    menu:
        "How do you handle the anomalous rift resonator and grounded scouts?"
        "Log the rift energy signature and let Kestrel's downed scouts withdraw (+1 Concord)":
            $ persistent.concord_points += 1
            kaelen "Smart move. Real hunters don't kill when a bigger predator is lurking beneath the ice."
        "Shatter the beacon and lock down the basin":
            kaelen "Done. The night belongs to our pack."
    jump dusk_ch3_start

label dusk_ch3_start:
    $ current_chapter_idx = 3
    scene bg_thronefield_dusk with fade
    show expression "characters/dusk_rook/state_a_battle.png" as dusk_rook at left
    show expression "characters/dusk_pawn_lead/state_a_battle.png" as dusk_pawn_lead at right
    with dissolve

    narrator "Chapter 3: The Iron Wall — The Narrow Chasm Defile."
    dravok "Thirty border skirmishes I've fought, Commander, and none hit harder than Sir Brannoch's kinetic charges. Good thing my dark-iron plate doesn't know how to bend!"
    sorrel "Warden Dravok, if you anchor the central files with your gravity warhammer, our diagonal casters can pin their advance!"

    hide dusk_rook
    hide dusk_pawn_lead
    call run_dusk_chapter_battle(3)

    scene bg_thronefield_dusk with dissolve
    show expression "characters/dusk_rook/state_a_battle.png" as dusk_rook at center with dissolve
    dravok "Hah! Even the Alabaster Bastion couldn't crack Umbrenholt iron today! Brannoch held his shield over his wounded niece as they pulled back."
    menu:
        "How do you direct Warden Dravok as Brannoch's squad withdraws?"
        "Halt the gravity bombardment and honor the old knight's retreat (+1 Concord)":
            $ persistent.concord_points += 1
            dravok "Aye, Commander. Brannoch is a man of iron honor—no need to crush young levies when the field is won."
        "Press the siege hammers forward to fortify the defile":
            dravok "The Iron Wall stands unchallenged!"
    jump dusk_ch4_start

label dusk_ch4_start:
    $ current_chapter_idx = 4
    scene bg_obsidian_archive with fade
    show expression "characters/dusk_bishop/state_a_battle.png" as dusk_bishop at left
    show expression "characters/dusk_queen/state_a_battle.png" as dusk_queen at right
    with dissolve

    narrator "Chapter 4: Echoes in the Stone — The Lower Sanctum of the Monoliths."
    veyra "Listen closely to the violet mist, Commander... My moon-lantern detects the heartbeats of those taken into The Quiet. They are not preserved in stasis—The Hollow is drinking their memories!"
    nyssara "High Seeress Ilyara is projecting solar beams across the sanctuary diagonals. Secure the sanctum so Veyra can trace the leak!"

    hide dusk_bishop
    hide dusk_queen
    call run_dusk_chapter_battle(4)

    scene bg_obsidian_archive with dissolve
    show expression "characters/dusk_bishop/state_a_battle.png" as dusk_bishop at center with dissolve
    veyra "The diagonal leylines are ours. Commander, I can project a shadow-astronomy echo across the chasm so Ilyara sees the truth of The Quiet as well."
    menu:
        "Do you allow Moonweaver Veyra to share the resonance echo?"
        "Transmit the lantern resonance to warn Solhaven's Seeress (+1 Concord)":
            $ persistent.concord_points += 1
            veyra "The starlight and the moonweave now share the same secret, Commander."
        "Conceal our findings within the Umbrenholt sanctum":
            veyra "The shadows will keep our knowledge safe until you command otherwise."
    jump dusk_ch5_start

## ============================================================================
## DUSK CHAPTERS 5 - 8
## ============================================================================

label dusk_ch5_start:
    $ current_chapter_idx = 5
    scene bg_obsidian_archive with fade
    show expression "characters/dusk_pawn_lead/state_a_battle.png" as dusk_pawn_lead at left
    show expression "characters/dusk_queen/state_a_battle.png" as dusk_queen at right
    with dissolve

    narrator "Chapter 5: The Obsidian Archive — The Forbidden Treaty Vaults."
    sorrel "Commander, Regent Nyssara—look at these gravity-preserved stone tablets! The original First Concord never decreed eternal stasis in The Quiet. Someone rewrote the Arbiter's core runes!"
    nyssara "And Tamsin Haldane's vanguard raiders have just breached the outer vault door. Guide Sorrel to the first rank, Commander—let her claim her Umbral Coronation!"

    hide dusk_pawn_lead
    hide dusk_queen
    call run_dusk_chapter_battle(5)

    scene bg_obsidian_archive with dissolve
    show expression "characters/dusk_pawn_lead/state_a_battle.png" as dusk_pawn_lead at center with dissolve
    sorrel "We held the archive within twenty-five moves! And Tamsin's vanguard detachment is cornered in the lower corridor."
    menu:
        "How do you handle the cornered Solhaven vanguard and the treaty proof?"
        "Spare Tamsin's detachment and pass them a rubbing of the original treaty (+1 Concord)":
            $ persistent.concord_points += 1
            sorrel "I slipped the rubbing right into Tamsin's buckler strap! Now both vanguards know the truth!"
        "Lock the obsidian vaults and keep the unredacted tablets for Umbrenholt alone":
            sorrel "Vaults sealed tight, Commander. Every tablet is cataloged in my map case."
    jump dusk_ch6_start

label dusk_ch6_start:
    $ current_chapter_idx = 6
    scene bg_quarters_dusk with fade
    show expression "characters/dusk_king/state_c_camp.png" as dusk_king at left
    show expression "characters/dusk_queen/state_c_camp.png" as dusk_queen at right
    with dissolve

    narrator "Chapter 6: The Emperor's Burden — The Imperial Pavilion at Umbral Peak."
    malachar "Do you see this runic brand across my sternum, Strategist? Every generation, the Emperor of Umbrenholt binds his own life force to anchor the northern half of the seal."
    malachar "Aurelian thinks our shadow-forges caused the breach, and his regicide strike force marches on my position. Protect the Ashen Crown so we may end this madness."
    nyssara "Warden Dravok's Aegis Ward encircles our line. No solar blade shall reach the Emperor."

    hide dusk_king
    hide dusk_queen
    call run_dusk_chapter_battle(6)

    scene bg_thronefield_dusk with dissolve
    show expression "characters/dusk_king/state_a_battle.png" as dusk_king at center with dissolve
    malachar "Aurelian's assault is broken. Across the field, the Lion of Solhaven lowers his greatsword—he sees the runic brand burning through my cracked breastplate."
    menu:
        "How do you counsel Emperor Malachar after repelling the assault?"
        "Dispatch an imperial missive sharing our findings on the failing seal (+1 Concord)":
            $ persistent.concord_points += 1
            malachar "Aurelian and I have borne this silence too long. Let the truth be spoken between kings."
        "Consolidate the imperial guard for the final reckoning":
            malachar "So be it. Umbrenholt marches to the end."
    jump dusk_ch7_start

label dusk_ch7_start:
    $ current_chapter_idx = 7
    scene bg_river_parley with fade
    $ unlock_cg("cgs/cg_03_river_parley.png")
    show expression "cgs/cg_03_river_parley.png" with dissolve

    narrator "Chapter 7: Parley at the River — A Secret Midnight Armistice."
    narrator "By the mist-shrouded riverbank, Regent Nyssara and Grand Marshal Lysandra compare the unredacted Obsidian tablets with the Prism Observatory ciphers."
    nyssara "So the Arbiter Automaton itself detonated the Ashgate conduits. It needed a war to harvest thirty-two champions into The Quiet."
    lysandra "And if either of us refuses to take the field tomorrow, the automaton will trigger a total leyline collapse across both capitals."
    nyssara "Then we put on a show worthy of two queens, Lysandra. Try not to let your Commander's eyes wander while we cross blades."
    lysandra "Focus on your own defense, Nyssara—our Strategist knows every feint in your repertoire."

    hide expression "cgs/cg_03_river_parley.png"
    call run_dusk_chapter_battle(7)

    scene bg_river_parley with dissolve
    show expression "characters/dusk_queen/state_a_battle.png" as dusk_queen at left
    show expression "characters/dawn_queen/state_a_battle.png" as dawn_queen at right
    with dissolve
    lysandra "Well fought, Commander. You kept Nyssara unscathed through twenty turns of steel and fire."
    menu:
        "As the midnight parley concludes, what do you offer Grand Marshal Lysandra?"
        "Deliver the complete shadow-key to synchronize our Aether for the final stone (+1 Concord)":
            $ persistent.concord_points += 1
            lysandra "I accept your trust, Strategist. When the eighth monolith rises, Solhaven will answer your call."
        "Retain the shadow-key for Umbrenholt's sole advantage":
            lysandra "Then may the strongest court survive what comes tomorrow."
    jump dusk_ch8_start

label dusk_ch8_start:
    $ current_chapter_idx = 8
    scene bg_thronefield_eclipse with fade
    show expression "characters/dusk_queen/state_a_battle.png" as dusk_queen at left
    show expression "characters/dusk_bishop/state_a_battle.png" as dusk_bishop at right
    with dissolve

    narrator "Chapter 8: The Final Duskstone — Beneath the Eclipsed Chasm."
    veyra "The seal beneath the sixty-four stones is fracturing! Violet and golden lightning are tearing through the void!"
    nyssara "The final match is upon us, Commander. Bring Solhaven's King to checkmate—and if our Concord is strong enough, we will turn our blades upon the true enemy!"

    hide dusk_queen
    hide dusk_bishop
    call run_dusk_chapter_battle(8)

    scene bg_thronefield_eclipse with dissolve
    show expression "characters/dusk_queen/state_a_battle.png" as dusk_queen at left
    show expression "characters/dawn_queen/state_b_worn.png" as dawn_queen at right
    with dissolve

    narrator "House Aurelis is locked in final checkmate! Above the trembling monoliths, the Arbiter Automaton commands you to cast the defeated court into The Quiet forever."

    if persistent.concord_points >= 3:
        nyssara "Commander! Our Concord Rating is [persistent.concord_points]! Lysandra and Ilyara are awaiting your command—we can defy the Arbiter and unite both realms right now!"
        menu:
            "The fate of Eltheris hangs on your command:"
            "Cease Hostilities — Unite Dusk and Dawn against the Corrupted Arbiter! (Grand Finale)":
                jump grand_finale_unbroken_concord
            "Deliver the final blow and claim absolute Umbral Ascendancy for Umbrenholt":
                jump ending_umbral_ascendancy
    else:
        nyssara "Without sufficient trust between the courts (Concord: [persistent.concord_points]/3), only Umbrenholt's dominion can impose order upon the rift!"
        jump ending_umbral_ascendancy

## ============================================================================
## DUSK RANK 4 CHAMPION'S OATH SCENES & CAMP FELLOWSHIP DIALOGUES
## ============================================================================

label dusk_check_rank4_oath:
    if current_camp and current_camp.fellowship_ranks.get("dusk_queen", 0) >= 4:
        scene bg_quarters_dusk with dissolve
        $ unlock_cg("cgs/cg_05_nyssara_oath.png")
        show expression "cgs/cg_05_nyssara_oath.png" with dissolve
        narrator "In the velvet hush of her private pavilion, Regent Nyssara stands beside the candlelit war map in her sheer plum-and-black lace negligee corset and cropped velvet bolero. Her warm fingers brush yours over the obsidian pieces."
        nyssara "In the intelligence courts of Umbral Peak, trust is a fatal luxury. I kept everyone at whip's length... until you walked into my tent."
        nyssara "Few understand the burden of holding a realm together from the shadows. With you, Commander, I never stand alone."
        hide expression "cgs/cg_05_nyssara_oath.png" with dissolve

    if current_camp and current_camp.fellowship_ranks.get("dusk_bishop", 0) >= 4:
        scene bg_quarters_dusk with dissolve
        $ unlock_cg("cgs/cg_07_veyra_lantern.png")
        show expression "cgs/cg_07_veyra_lantern.png" with dissolve
        narrator "Under the warm amethyst glow of her floating moon-lantern, Moonweaver Veyra leans close in her cropped lavender silk tie-front top and ruffled black lace micro-skirt, tracing the rift's true resonance frequency against your palm."
        veyra "I have peered into a thousand dimensional folds, Commander, yet none ever held the warmth I find in your gaze. My lantern—and my soul—burn for you."
        hide expression "cgs/cg_07_veyra_lantern.png" with dissolve

    if current_camp and current_camp.fellowship_ranks.get("dusk_knight", 0) >= 4:
        scene bg_thronefield_dusk with dissolve
        $ unlock_cg("cgs/cg_09_kaelen_nightwatch.png")
        show expression "cgs/cg_09_kaelen_nightwatch.png" with dissolve
        narrator "Out on a moonlit rock outcrop overlooking the gorge, Huntress-Captain Kaelen Ashfang sits pressed against your shoulder in her fur-trimmed cropped leather vest, her shadow-wolf Gloam curled peacefully at your feet."
        kaelen "Northern border wolves mate and hunt for life, Commander. Whatever storms break over the monoliths tomorrow, my fangs and my heart belong to you."
        hide expression "cgs/cg_09_kaelen_nightwatch.png" with dissolve
    return

label dusk_camp_fellowship_dialogue(char_id, rank):
    scene bg_quarters_dusk with dissolve
    show expression f"characters/{char_id}/state_c_camp.png" at center with dissolve

    if char_id == "dusk_queen":
        if rank == 1:
            nyssara "Come in, Commander. Leave the formalities outside—I just unhooked my scale-corset for the evening. Care for a cup of spiced black tea while we decode these intercepts?"
        elif rank == 2:
            nyssara "Every noble in Umbrenholt feared my whip-blade, yet none ever asked what it cost to guard the realm from the dark. You see past the velvet mask, don't you?"
        elif rank == 3:
            nyssara "Sit closer by the brazier, Strategist. Your pulse quickens whenever I lean over your map... and I find I rather enjoy it. (+1 Max Aether Unlocked!)"
        else:
            nyssara "Command me as you wish, my Strategist. In light or shadow, I am yours."
    elif char_id == "dusk_bishop":
        if rank == 1:
            veyra "Welcome into the lantern-light, Commander. This cropped lavender silk lets the night breeze soothe my Aether burns."
        elif rank == 2:
            veyra "When I first heard the whispers leaking from The Quiet, the High Court thought I was dreaming. Only you listened to my star-charts."
        elif rank == 3:
            veyra "Watch how the violet mist curls around both our hands... our astral resonance is completely intertwined now. (+1 Max Aether Unlocked!)"
        else:
            veyra "Every shadow and star in my sanctum belongs to you, Commander."
    elif char_id == "dusk_knight":
        if rank == 1:
            kaelen "Ha, caught me brushing Gloam's coat! Don't mind the open vest, Commander—campfires run hot after a night patrol."
        elif rank == 2:
            kaelen "High court politics make my skin crawl. Out here on the border, a leader's word is measured by whether they bleed with their pack—and you've proven yourself ten times over."
        elif rank == 3:
            kaelen "Here, share my fur cloak by the embers. Even a Nightrunner needs someone watching her back. (+1 Max Aether Unlocked!)"
        else:
            kaelen "Lead the hunt, Commander. My blades and I are right beside you!"
    elif char_id == "dusk_pawn_lead":
        if rank == 1:
            sorrel "Oh! Commander! Let me adjust my spectacles—I tied my dress shirt up because the ink-lamps make the tent so warm!"
        elif rank == 2:
            sorrel "When I stole the duplicate First Concord scrolls from the lower archive, I knew my life was forfeit if caught. Thank you for believing in a humble scribe."
        elif rank == 3:
            sorrel "Look at these new flanking diagrams I drew for us! With your guidance, I'm not afraid of the front line anymore! (+1 Max Aether Unlocked!)"
        else:
            sorrel "Whether with quill or command blade, I'm devoted to your strategy forever!"
    elif char_id == "dusk_rook":
        if rank == 1:
            dravok "Pull up an anvil-stool, Commander. Nothing clears a warrior's head like the ring of a whetstone on dark iron."
        elif rank == 2:
            dravok "These glowing violet brands on my chest mark thirty battles where I carried young levies home on my shield. We won't leave any behind in The Quiet."
        elif rank == 3:
            dravok "By the Iron Crags, your fortification tactics are masterwork! (+1 Max Aether Unlocked!)"
        else:
            dravok "My warhammer and my life are sworn to your banner, Commander."
    elif char_id == "dusk_king":
        if rank == 1:
            malachar "Step inside, Strategist. In this pavilion, you may speak freely without the weight of imperial protocol."
        elif rank == 2:
            malachar "For centuries, my ancestors watched champions vanish into the monoliths, bound by a treaty they dared not question. Together, we shall break that cycle."
        elif rank == 3:
            malachar "You have become the sharpest mind in the history of the Dominion. (+1 Max Aether Unlocked!)"
        else:
            malachar "Stand beside the throne as Arch-Strategist of Umbrenholt, now and always."

    hide expression f"characters/{char_id}/state_c_camp.png" with dissolve
    return
