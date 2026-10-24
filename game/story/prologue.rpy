## prologue.rpy - Shared Prologue: "The Night Ashgate Burned"

## Complies with Section 4.1 of the Master Build Bible (v3.2)



init python:

    def unlock_cg(cg_path):

        if cg_path not in persistent.unlocked_cgs:

            persistent.unlocked_cgs.append(cg_path)

        if store.current_camp is not None and cg_path not in store.current_camp.unlocked_cgs:

            store.current_camp.unlocked_cgs.append(cg_path)



## ============================================================================

## SHARED PROLOGUE: THE NIGHT ASHGATE BURNED

## ============================================================================



label prologue_start:

    play music audio.bgm_parley fadein 1.0

    $ persistent.concord_points = 0

    $ current_chapter_idx = 1

    $ banter_db = load_banter_json()



    # -------------------------------------------------------------------------

    # SCENE 1: THE DIPLOMATIC SUMMIT

    # -------------------------------------------------------------------------

    scene bg_ashgate_hall

    with fade



    narrator "Six centuries after the Cataclysm of Falling Stars, the neutral border citadel of Ashgate gleams beneath a fragile twilight."

    narrator "High above the central chasm of Eltheris, banners of radiant solar gold and midnight velvet hang side by side along the vaulted stone arches."

    narrator "Tonight, the two great powers of the continent have convened to renegotiate the Aether Wellspring treaties—and you have been summoned as Chief Arbiter-Strategist to witness the accord."



    show expression "characters/dawn_king/state_a_battle.png" as dawn_king at left

    show expression "characters/dusk_king/state_a_battle.png" as dusk_king at right

    with dissolve



    aurelian "Six hundred years of cold peace have strained the leylines of Solhaven, Emperor Malachar. The southern wells run dry while your shadow-forges draw deeper from the crust."

    malachar "Our forges sustain the northern wards against the frost-wastes, Sovereign Aurelian. Umbrenholt takes only what the First Concord permits—no more, no less."



    hide dawn_king

    hide dusk_king

    with dissolve



    narrator "Before the monarchs' dispute can harden, their apex military commanders step forward to the marble drafting table."



    show expression "characters/dawn_queen/state_a_battle.png" as dawn_queen at left

    show expression "characters/dusk_queen/state_a_battle.png" as dusk_queen at right

    with dissolve



    narrator "On the left stands Grand Marshal Lysandra Verel—'The Sunblade' of House Aurelis—arrayed in her sculpted ivory-and-gold half-cuirass and pearl battle micro-skirt, the radiant rapier Sunburst resting at her hip."

    narrator "Across from her leans Regent Nyssara Vael—'The Velvet Blade' of Umbrenholt—her articulated obsidian scale-corset and sheer spider-lily gartered stockings catching the brazier light as she traces a gloved finger along the border map."



    lysandra "We did not ride to Ashgate to trade veiled accusations, Regent Nyssara. My scouts recorded three seismic Aether surges beneath the central gorge this month alone."

    nyssara "And my Moonweavers recorded the exact same tremors originating from the solar conduits, Grand Marshal. Perhaps if Solhaven's steel were as sharp as your posture, you would look beneath the stone rather than across the border."

    lysandra "Careful, Nyssara. Sunburst answers provocations faster than diplomats do."

    nyssara "Mmm. A tempting promise, Lysandra. Yet look at the Strategist's charts—both our readings converge on the sealed fault line directly below this citadel."



    # -------------------------------------------------------------------------

    # SCENE 2: THE SABOTAGE

    # -------------------------------------------------------------------------

    narrator "Before you can speak to confirm Nyssara's deduction, the runic chandeliers overhead flare a violent, corrupted crimson."



    play sound audio.sfx_armor_break

    play music audio.bgm_ashgate fadein 0.5

    with vpunch

    narrator "A deafening roar shatters the marble floor! Ancient Aether conduits beneath Ashgate detonate in a cascade of fractured prism-light and gravitational shadow."



    $ unlock_cg("cgs/cg_01_ashgate_climax.png")

    scene expression "cgs/cg_01_ashgate_climax.png"

    with flash



    narrator "From the ruptured floor rise faceless, hollow-forged constructs bearing neither the crest of Solhaven nor the sigil of Umbrenholt!"

    narrator "Pillars crash across the dais. Without hesitation, Lysandra and Nyssara leap into the breach—fighting back-to-back in a dazzling storm of golden kinetic slashes and lethal dusk-steel whip arcs!"



    lysandra "Treachery! Someone rigged the foundational leylines to blow! Guard the Sovereigns—keep them clear of the chasm!"

    nyssara "These constructs are bound by ancient pre-Cataclysm ciphers! Strategist, clear the southern archway—Lysandra and I will hold the center!"



    with vpunch

    narrator "Lysandra's rapier pierces the core of a towering construct while Nyssara's whip-blade severs the limbs of two more, their Aether-weave regalia glowing with resonant heat as the great hall collapses around them."

    narrator "Under your tactical direction, both delegations fight their way through the burning courtyard and retreat to opposite ridges of the central valley."



    # -------------------------------------------------------------------------

    # SCENE 3: THE MONOLITHS RISE

    # -------------------------------------------------------------------------

    $ unlock_cg("cgs/cg_02_monoliths_rise.png")

    scene expression "cgs/cg_02_monoliths_rise.png"

    with dissolve



    narrator "As the dust of Ashgate settles into the yawning abyss of The Hollow, the earth trembles a second time."

    narrator "Sixty-four colossal monolith slabs—alternating between radiant white Dawnstone and starlit black Duskstone—rise from the chasm on pillars of ancient Aether, locking into an immense eight-by-eight grid over the void."

    narrator "At the center of the stone sky-bridge materializes the towering masked figure of the Arbiter Automaton."



    arbiter "HEAR THE LAW OF THE FIRST CONCORD. THE SEAL OF ASHGATE IS BROKEN. TOTAL CONTINENTAL WAR IS FORBIDDEN BY ANCIENT GEAS."

    arbiter "LET THE SIXTEEN CHAMPIONS OF DAWN AND THE SIXTEEN CHAMPIONS OF DUSK ASCEND THE SIXTY-FOUR THRONES. ONLY BY THE RITE OF THRONES SHALL SOVEREIGNTY BE DECIDED."



    scene bg_ashgate_hall

    with dissolve



    show expression "characters/dawn_queen/state_a_battle.png" as dawn_queen at left

    show expression "characters/dusk_queen/state_a_battle.png" as dusk_queen at right

    with dissolve



    lysandra "The Rite of Thrones... invoked automatically by the sabotage. Whoever orchestrated tonight's attack wants our courts to bleed each other dry into The Quiet."

    nyssara "And until the Rite is resolved, the ancient Geas binds every warrior's stride to the leylines of the board. Only a master tactician who understands both the sixty-four stones and the truth beneath them can lead us out of this trap."



    lysandra "Strategist! Stand with House Aurelis. Take command of our War Tent, guide the Sunblade, and bring the light of Solhaven to the monoliths!"

    nyssara "Or walk with The Umbrenholt Dominion, Commander. Command my shadow court, unravel the conspiracy from the dark, and claim the Duskstone!"



    # -------------------------------------------------------------------------

    # FACTION CHOICE

    # -------------------------------------------------------------------------

    menu:

        "Choose which realm's grand campaign you will command:"



        "Take Command of House Aurelis (Dawn / White) alongside Grand Marshal Lysandra":

            $ current_faction = "dawn"

            $ current_camp = CampManager(faction="dawn")

            hide dusk_queen with dissolve

            lysandra "Your wisdom honors Solhaven, Commander. Come—our War Tent awaits on the eastern ridge. Let us prepare the Vanguard for First Light!"

            jump campaign_dawn_start



        "Take Command of The Umbrenholt Dominion (Dusk / Black) alongside Regent Nyssara":

            $ current_faction = "dusk"

            $ current_camp = CampManager(faction="dusk")

            hide dawn_queen with dissolve

            nyssara "A deliciously perceptive choice, Commander. Come into the velvet dark of my pavilion—let us show Solhaven how shadows conquer."

            jump campaign_dusk_start

