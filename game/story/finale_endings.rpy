## finale_endings.rpy - Grand Finale ("The Unbroken Concord") & All 8 Endings & Epilogues
## Complies with Section 4.3 of the Master Build Bible (v3.2)

## ============================================================================
## GRAND FINALE: THE UNBROKEN CONCORD (800 ELO CORRUPTED ARBITER BOSS)
## ============================================================================

label grand_finale_unbroken_concord:
    scene bg_thronefield_eclipse with fade
    show image "characters/dawn_queen/state_a_battle.png" at left
    show image "characters/dusk_queen/state_a_battle.png" at right
    with dissolve

    narrator "Grand Finale — The Unbroken Concord."
    narrator "At your command, the blades of Dawn and Dusk halt in unison! Across the sixty-four monoliths, radiant solar gold and twilight umbral violet weave together into a single resonant harmonic."
    lysandra "Arbiter of the Monoliths! Your corrupted directive ends today! House Aurelis refuses to sacrifice another soul to The Hollow!"
    nyssara "And The Umbrenholt Dominion severs your strings! Step down from the chasm, automaton, or be unmade by both courts at once!"

    with vpunch
    arbiter "ERROR. TREATY VIOLATION DETECTED. INITIATING TOTAL PURGE OF BOTH SOVEREIGN COURTS."

    hide image "characters/dawn_queen/state_a_battle.png"
    hide image "characters/dusk_queen/state_a_battle.png"
    show image "characters/dawn_bishop/state_a_battle.png" at left
    show image "characters/dusk_bishop/state_a_battle.png" at right
    with dissolve

    ilyara "Commander! Veyra and I have linked our prism and moon-lantern leylines! You now command 5 full Aether Charges!"
    veyra "And both Queens stand at your war table alongside us—projecting 4 Allied Advisor Vectors each turn! Lead us to victory!"

    hide image "characters/dawn_bishop/state_a_battle.png"
    hide image "characters/dusk_bishop/state_a_battle.png"

    $ chapters_db = load_campaign_json()
    $ gf_data = chapters_db["grand_finale"]

    $ current_session = MatchSession(
        player_faction=current_faction,
        boss_profile_id="grand_command",
        initial_fen=gf_data["initial_fen"],
        starting_aether=5,
        max_aether=5
    )
    $ current_session.concord_points = persistent.concord_points
    $ p_lead = "dawn_queen" if current_faction == "dawn" else "dusk_queen"
    $ b_lead = "dusk_king" if current_faction == "dawn" else "dawn_king"
    $ current_detector = EventDetector(
        player_char_id=p_lead,
        boss_char_id=b_lead,
        player_faction=current_faction
    )

    $ tf_ui = ThronefieldUI(current_session, current_detector, gf_data)
    call screen thronefield(tf_ui)
    $ finale_outcome = _return

    if finale_outcome and finale_outcome.get("winner") == "player":
        jump ending_true_concord
    else:
        jump ending_abyssal_breach

## ============================================================================
## ENDINGS 1 - 4: CORE NARRATIVE CONCLUSIONS
## ============================================================================

label ending_true_concord:
    $ unlock_cg("cgs/cg_10_true_concord_finale.png")
    scene expression "cgs/cg_10_true_concord_finale.png" with flash

    narrator "ENDING 1 OF 8: THE TRUE CONCORD (GOLDEN ENDING)"
    narrator "With a final, cataclysmic checkmate, the Corrupted Arbiter shatters into harmless motes of ancient quartz!"
    narrator "Standing shoulder-to-shoulder on the central throne monolith, Lysandra, Nyssara, Ilyara, and Veyra channel the combined Aether of Lumen and Umbra deep into the chasm."
    narrator "Beneath the sixty-four stones, the chambers of The Quiet open like blooming stars—releasing every single Unthroned champion unharmed while sealing The Hollow forever!"

    show image "characters/dawn_king/state_a_battle.png" at left
    show image "characters/dusk_king/state_a_battle.png" at right
    with dissolve
    aurelian "Six hundred years of fear and bloodshed... ended in a single night of unity."
    malachar "And a new Second Concord begins—written not by machines, but by the living."
    hide image "characters/dawn_king/state_a_battle.png"
    hide image "characters/dusk_king/state_a_battle.png"

    # Route to Character-Specific Fellowship Epilogue (Endings 5 - 8)
    jump select_fellowship_epilogue

label ending_solar_dominance:
    scene bg_thronefield_dawn with fade
    show image "characters/dawn_queen/state_a_battle.png" at left
    show image "characters/dawn_king/state_a_battle.png" at right
    with dissolve

    narrator "ENDING 2 OF 8: SOLAR DOMINANCE"
    narrator "House Aurelis claims total military victory across the sixty-four monoliths. The banners of Solhaven fly uncontested over the central gorge as Umbrenholt's forces withdraw into the northern mountains."
    lysandra "The field is ours, Commander... yet look at the fractures still pulsing beneath the Duskstone."
    aurelian "We have won the Rite, my Strategist, but the seal beneath the chasm remains unstable. Until the next generation is called to the stone, our watch never truly ends."
    return

label ending_umbral_ascendancy:
    scene bg_thronefield_dusk with fade
    show image "characters/dusk_queen/state_a_battle.png" at left
    show image "characters/dusk_king/state_a_battle.png" at right
    with dissolve

    narrator "ENDING 3 OF 8: UMBRAL ASCENDANCY"
    narrator "The Umbrenholt Dominion triumphs upon the Thronefield. Twilight banners drape the monoliths as Solhaven's legions retreat beyond the eastern ridge."
    nyssara "A masterstroke of conquest, Commander. The Aether Wellsprings answer solely to Umbral Peak now."
    malachar "Yet the whispers from The Hollow have only grown quieter, not ceased. Guard our borders well, Arch-Strategist—the abyss remembers."
    return

label ending_abyssal_breach:
    scene bg_thronefield_eclipse with fade
    with vpunch

    narrator "ENDING 4 OF 8: THE ABYSSAL BREACH (DEFEAT)"
    narrator "Overwhelmed by the Corrupted Arbiter's relentless barrage, the defensive leylines shatter. One by one, the sixty-four monoliths crumble into the yawning chasm of The Hollow."
    narrator "Only by a desperate final Aether ward do your surviving officers pull you back to the canyon rim as eternal twilight swallows the valley below."
    return

## ============================================================================
## ENDINGS 5 - 8: CHARACTER-SPECIFIC FELLOWSHIP EPILOGUES
## ============================================================================

label select_fellowship_epilogue:
    menu:
        "Choose which sworn champion's Fellowship Epilogue to experience:"
        "Epilogue 5: The Sunblade's Vow (Grand Marshal Lysandra)":
            jump epilogue_lysandra
        "Epilogue 6: The Velvet Shadow (Regent Nyssara)":
            jump epilogue_nyssara
        "Epilogue 7: Starlight & Moonweave (Ilyara & Veyra)":
            jump epilogue_seers
        "Epilogue 8: Wings & Fangs of the Border (Kestrel, Kaelen & Vanguards)":
            jump epilogue_vanguard

label epilogue_lysandra:
    scene bg_quarters_dawn with fade
    $ unlock_cg("cgs/cg_04_lysandra_oath.png")
    show expression "cgs/cg_04_lysandra_oath.png" with dissolve

    narrator "ENDING 5 OF 8: EPILOGUE — THE SUNBLADE'S VOW"
    narrator "Months after the sealing of The Hollow, the royal citadel of Solhaven rings with music and celebration. Away from the grand ballroom, Grand Marshal Lysandra draws you into the warm balcony pavilion overlooking the golden valley."
    narrator "Arrayed in her crimson velvet evening attire, she sets her rapier Sunburst aside on the table and steps into your embrace."
    lysandra "For the first time in my life, there is no tournament to fight and no war on the horizon."
    lysandra "You gave Eltheris its peace, Commander... and you gave me a reason to lay down my armor. Stay by my side—tonight, and for all the dawns to come."
    return

label epilogue_nyssara:
    scene bg_quarters_dusk with fade
    $ unlock_cg("cgs/cg_05_nyssara_oath.png")
    show expression "cgs/cg_05_nyssara_oath.png" with dissolve

    narrator "ENDING 6 OF 8: EPILOGUE — THE VELVET SHADOW"
    narrator "High in the starlit spire of Umbral Peak, Regent Nyssara hosts a private twilight banquet in her candlelit quarters. Wearing her sheer plum-and-black lace corset, she raises two crystal goblets of spiced wine."
    nyssara "The courts of Dawn and Dusk now trade openly across the sixty-four monoliths, all because a certain brilliant Strategist refused to play by the Arbiter's rules."
    nyssara "The realm is secure, my love. Now... we have all the time in the world to explore our own private maneuvers."
    return

label epilogue_seers:
    scene bg_prism_observatory with fade
    $ unlock_cg("cgs/cg_06_ilyara_astrolabe.png")
    $ unlock_cg("cgs/cg_07_veyra_lantern.png")
    show image "characters/dawn_bishop/state_c_camp.png" at left
    show image "characters/dusk_bishop/state_c_camp.png" at right
    with dissolve

    narrator "ENDING 7 OF 8: EPILOGUE — STARLIGHT & MOONWEAVE"
    narrator "Above the peaceful Thronefield, the Prism Observatory and the Obsidian Sanctum are joined into the Unified Astral Academy. High Seeress Ilyara and Moonweaver Veyra stand on either side of your desk as starlight and lantern-glow fill the chamber."
    ilyara "Without the corruption of The Hollow, the leylines sing with gentle warmth across our skin, Commander."
    veyra "And together with you as our High Chancellor, we shall chart the heavens for centuries to come."
    return

label epilogue_vanguard:
    scene bg_river_parley with fade
    $ unlock_cg("cgs/cg_08_kestrel_skyfall.png")
    $ unlock_cg("cgs/cg_09_kaelen_nightwatch.png")
    show image "characters/dawn_knight/state_c_camp.png" at left
    show image "characters/dusk_knight/state_c_camp.png" at right
    with dissolve

    narrator "ENDING 8 OF 8: EPILOGUE — WINGS & FANGS OF THE BORDER"
    narrator "Along the newly united frontier of Eltheris, sky-griffins and shadow-wolves patrol side by side. Kestrel, Kaelen, Tamsin, and Sorrel gather around your command fire under a clear, unbroken sky."
    kestrel "From the highest updraft to the deepest gorge, the border belongs to our joint squadron now, Commander!"
    kaelen "And wherever the trail leads next, our pack rides with you!"
    return
