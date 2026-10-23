"""
build_manifest.py - Generates tools/art_manifest.json containing all 110 production visual assets.
Complies with Section 7.1 & 7.2 of the Master Build Bible.
"""

import json
from pathlib import Path

MANIFEST_PATH = Path(__file__).parent / "art_manifest.json"

GLOBAL_FEMALE_PREFIX = (
    "masterpiece, best quality, ultra-detailed anime fantasy illustration, thigh-up 3/4 portrait, "
    "voluptuous hourglass figure, glossy skin highlights, alluring expression, ornate high-fantasy couture armor, "
    "deep plunging cleavage, cropped underboob cutout, ultra-short pleated miniskirt, tight sheer thigh-high stockings "
    "with ornate garter straps, zettai ryouiki"
)

GLOBAL_MALE_PREFIX = (
    "masterpiece, best quality, ultra-detailed anime fantasy illustration, waist-up portrait, "
    "powerful muscular physique, veteran warrior countenance, ornate high-fantasy plate armor, dynamic lighting"
)

STATE_B_MODIFIER = (
    "battle-damaged armor, cracked lower breastplate exposing pronounced underboob, loosened corset laces, "
    "deep cleavage, torn miniskirt hem showing garter strap, ripped thigh-high stockings, glistening sweat, "
    "blushing, fierce breathless combat expression, arcane sparks"
)

STATE_C_MODIFIER = (
    "off-duty evening camp loungewear, cropped silk top, exposed underboob and deep cleavage, "
    "short pleated skirt, tight stay-up thigh-high stockings, warm candlelight"
)

NEGATIVE_PROMPT = (
    "bad anatomy, extra limbs, deformed hands, blurry, lowres, text, watermark, signature, "
    "religious cross, christian bishop mitre"
)

CHARACTERS = [
    # Dawn (White)
    ("dawn_king", "male", "Aurelian Valdris", "lion-crested gilded plate armor, silver-streaked golden hair, amber eyes, short trimmed beard, royal ivory mantle"),
    ("dawn_queen", "female", "Lysandra Verel", "sculpted ivory-and-gold half-cuirass, deep sweetheart cleavage, cropped midriff, fiery auburn plait, pleated pearl micro-skirt, white garter stockings, Sunburst rapier"),
    ("dawn_rook", "male", "Brannoch Haldane", "massive alabaster tower shield, heavy white enamel plate, winged pauldrons, powerful muscular build"),
    ("dawn_bishop", "female", "Ilyara Quen", "celestial-blue halter silk bodice, diamond keyhole cleavage, bare underboob, silver navel chain, long silver hair, pearl-blue thigh-high stockings, floating prism staff"),
    ("dawn_knight", "female", "Kestrel Rowan", "aerodynamic cropped cavalry breastplate, plunging center cleavage, copper-red short hair, navy riding micro-skirt, white-and-gold striped stockings, winged helm"),
    ("dawn_pawn_lead", "female", "Tamsin Haldane", "polished steel half-cuirass over low-scoop linen corset-blouse, generous cleavage, pleated vanguard miniskirt, honey-blonde braid, short spear"),
    # Dusk (Black)
    ("dusk_king", "male", "Malachar Voss", "midnight-black plate armor, velvet open mantle, runic sternum brand, jet-black hair with silver temples, dusk-steel circlet"),
    ("dusk_queen", "female", "Nyssara Vael", "articulated obsidian scale-corset, plunging deep V-neckline, bare underboob, braided raven hair crown, bedroom violet eyes, high-slit black micro-skirt, lace garter stockings, whip-blade"),
    ("dusk_rook", "male", "Dravok Kell", "dark iron fortress-plate, bare-chested gladiator harness, glowing violet runic brands, two-handed warhammer"),
    ("dusk_bishop", "female", "Veyra Thorne", "dark violet cropped hood mantle, criss-cross silver ribbon bra, exposed underboob and deep cleavage, lavender-silver hair, tiered amethyst miniskirt, celestial moon-lantern"),
    ("dusk_knight", "female", "Kaelen Ashfang", "minimalist dark leather scout-harness, open-front cross-straps, deep cleavage and bare underboob, wild raven hair, wolf eyes, fishnet-leather stockings, shadow-wolf mount"),
    ("dusk_pawn_lead", "female", "Sorrel Nightwick", "enameled underbust corset, cropped unbuttoned charcoal blouse, deep cleavage, spectacles, dark-crimson braids, pleated plaid miniskirt, opaque stockings, short sword"),
]

def build_manifest():
    assets = []

    # 1. Character Sprites (38: 12x3 + 2 promoted)
    for char_id, gender, name, desc in CHARACTERS:
        prefix = GLOBAL_FEMALE_PREFIX if gender == "female" else GLOBAL_MALE_PREFIX

        # state_a_battle
        assets.append({
            "path": f"characters/{char_id}/state_a_battle.png",
            "category": "character_sprite",
            "char_id": char_id,
            "state": "state_a_battle",
            "width": 900,
            "height": 1080,
            "format": "RGBA",
            "prompt": f"{prefix}, {name}, {desc}, pristine ceremonial battle regalia, weapons drawn, dynamic heroic stance",
            "negative_prompt": NEGATIVE_PROMPT,
            "seed_ref": f"{char_id}_master_seed",
        })

        # state_b_worn
        assets.append({
            "path": f"characters/{char_id}/state_b_worn.png",
            "category": "character_sprite",
            "char_id": char_id,
            "state": "state_b_worn",
            "width": 900,
            "height": 1080,
            "format": "RGBA",
            "prompt": f"{prefix}, {name}, {desc}, {STATE_B_MODIFIER}",
            "negative_prompt": NEGATIVE_PROMPT,
            "seed_ref": f"{char_id}_master_seed",
        })

        # state_c_camp
        assets.append({
            "path": f"characters/{char_id}/state_c_camp.png",
            "category": "character_sprite",
            "char_id": char_id,
            "state": "state_c_camp",
            "width": 900,
            "height": 1080,
            "format": "RGBA",
            "prompt": f"{prefix}, {name}, {desc}, {STATE_C_MODIFIER}",
            "negative_prompt": NEGATIVE_PROMPT,
            "seed_ref": f"{char_id}_master_seed",
        })

    # Promoted Forms (2)
    assets.append({
        "path": "characters/dawn_pawn_lead/state_d_promoted.png",
        "category": "character_sprite",
        "char_id": "dawn_pawn_lead",
        "state": "state_d_promoted",
        "width": 900,
        "height": 1080,
        "format": "RGBA",
        "prompt": f"{GLOBAL_FEMALE_PREFIX}, Tamsin Haldane, Solar Ascension Radiant Paladin form, golden wing-cupped bikini-cuirass, deep cleavage, bare underboob, sheer golden hip-sash, micro-skirt, white-and-gold lace stockings, runic winged spear, celestial aura",
        "negative_prompt": NEGATIVE_PROMPT,
        "seed_ref": "dawn_pawn_lead_master_seed",
    })
    assets.append({
        "path": "characters/dusk_pawn_lead/state_d_promoted.png",
        "category": "character_sprite",
        "char_id": "dusk_pawn_lead",
        "state": "state_d_promoted",
        "width": 900,
        "height": 1080,
        "format": "RGBA",
        "prompt": f"{GLOBAL_FEMALE_PREFIX}, Sorrel Nightwick, Umbral Coronation Grand Field Strategist form, obsidian-and-silver bikini breastplate, deep cleavage, bare underboob, high-slit velvet marshal cape-skirt, dual-garter sheer stockings, runic command blade, dark violet aura",
        "negative_prompt": NEGATIVE_PROMPT,
        "seed_ref": "dusk_pawn_lead_master_seed",
    })

    # 2. Action Cut-In Banners (14)
    for char_id, _, name, _ in CHARACTERS:
        assets.append({
            "path": f"cutins/{char_id}_cutin.png",
            "category": "action_cutin",
            "char_id": char_id,
            "width": 1920,
            "height": 360,
            "format": "RGBA",
            "prompt": f"dynamic cinematic anime combat action cut-in banner, 1920x360 horizontal, close-up intense focused eyes and bust/cleavage of {name}, radiant elemental Aether ribbons, fierce combat determination, widescreen slash composition",
            "negative_prompt": NEGATIVE_PROMPT,
            "seed_ref": f"{char_id}_master_seed",
        })
    assets.append({
        "path": "cutins/dawn_pawn_lead_promoted_cutin.png",
        "category": "action_cutin",
        "char_id": "dawn_pawn_lead",
        "width": 1920,
        "height": 360,
        "format": "RGBA",
        "prompt": "dynamic cinematic anime promotion cut-in banner, 1920x360 horizontal, Tamsin Haldane Solar Ascension, radiant golden wings, incandescent eyes, glowing winged spear, glorious victory fanfare energy",
        "negative_prompt": NEGATIVE_PROMPT,
        "seed_ref": "dawn_pawn_lead_master_seed",
    })
    assets.append({
        "path": "cutins/dusk_pawn_lead_promoted_cutin.png",
        "category": "action_cutin",
        "char_id": "dusk_pawn_lead",
        "width": 1920,
        "height": 360,
        "format": "RGBA",
        "prompt": "dynamic cinematic anime promotion cut-in banner, 1920x360 horizontal, Sorrel Nightwick Umbral Coronation, glowing violet eyes, obsidian blade, tactical diagrams in dark flame, grand coronation fanfare energy",
        "negative_prompt": NEGATIVE_PROMPT,
        "seed_ref": "dusk_pawn_lead_master_seed",
    })

    # 3. Advisor Medallion Busts (8)
    bust_chars = [
        "dawn_king", "dawn_queen", "dawn_rook", "dawn_bishop",
        "dusk_king", "dusk_queen", "dusk_rook", "dusk_bishop",
    ]
    for cid in bust_chars:
        faction = "dawn" if cid.startswith("dawn") else "dusk"
        frame_color = "ornate gilded sun-filigree frame" if faction == "dawn" else "ornate obsidian violet-filigree frame"
        assets.append({
            "path": f"ui/advisors/{cid}_bust.png",
            "category": "advisor_bust",
            "char_id": cid,
            "width": 160,
            "height": 160,
            "format": "RGBA",
            "prompt": f"circular UI medallion character icon, 160x160 portrait bust of {cid}, {frame_color}, transparent outer ring",
            "negative_prompt": NEGATIVE_PROMPT,
            "seed_ref": f"{cid}_master_seed",
        })

    # 4. Board Piece Tokens (12)
    for faction in ["dawn", "dusk"]:
        theme = "radiant white marble with gold filigree engraving" if faction == "dawn" else "polished dark obsidian with violet amethyst engraving"
        for piece in ["king", "queen", "rook", "bishop", "knight", "pawn"]:
            assets.append({
                "path": f"board/pieces/{faction}_{piece}.png",
                "category": "piece_token",
                "faction": faction,
                "piece_type": piece,
                "width": 80,
                "height": 80,
                "format": "RGBA",
                "prompt": f"heraldic fantasy chess token icon, 80x80 px, {piece} silhouette, {theme}, clean transparent background, clear role readability",
                "negative_prompt": "blurry, low resolution, extra pieces, noisy background",
            })

    # 5. Story & Fellowship CGs (10)
    cgs = [
        ("cgs/cg_01_ashgate_climax.png", "The Summit of Ashgate Climax", "Grand Marshal Lysandra and Regent Nyssara fighting back-to-back in collapsing burning citadel hall, swords crossed protecting sovereigns, dynamic high glamour lighting"),
        ("cgs/cg_02_monoliths_rise.png", "The Monoliths Rise", "Sixty-four colossal stone monoliths rising from the misty chasm between dawn and dusk armies, ancient glowing runes, epic wide scale"),
        ("cgs/cg_03_river_parley.png", "Parley at the River", "Secret night armistice meeting beside mist-veiled river; Lysandra in cropped battle regalia and Nyssara in velvet corset exchanging treaty scrolls"),
        ("cgs/cg_04_lysandra_oath.png", "The Sunblade's Oath", "Grand Marshal Lysandra leaning close across illuminated war table in cropped crimson top and black leather miniskirt, soft candlelit glow, solemn sensual oath"),
        ("cgs/cg_05_nyssara_oath.png", "The Velvet Blade's Oath", "Regent Nyssara in sheer plum corset standing shoulder-to-shoulder by candlelit map, fingers brushing over obsidian pieces with intimate seductive smile"),
        ("cgs/cg_06_ilyara_astrolabe.png", "The Prism Alignment", "High Seeress Ilyara Quen leaning over glowing ancient astrolabe, starlight illuminating sheer sapphire vestments and deep cleavage, awe-struck serene expression"),
        ("cgs/cg_07_veyra_lantern.png", "The Lantern Resonance", "Moonweaver Veyra Thorne holding floating moon-lantern in darkened tent, violet energy illuminating bare underboob and silver ribbon bra as ancient rift map appears"),
        ("cgs/cg_08_kestrel_skyfall.png", "Skyfall Salute", "Cavalier-Captain Kestrel Rowan perched beside war-griffin overlooking sunrise chasm, cropped riding jacket windswept open, playful triumphant salute"),
        ("cgs/cg_09_kaelen_nightwatch.png", "Nightrunner Vigil", "Huntress-Captain Kaelen Ashfang seated close beside you on cliff outcrop under twin moons, shadow-wolf resting at feet, open leather harness in moonlight"),
        ("cgs/cg_10_true_concord_finale.png", "The Unbroken Concord Finale", "Both Dawn and Dusk champions united on central throne monolith, radiant golden and violet leylines combining to seal the abyss, triumph, elegance, liberation"),
    ]
    for path, title, prompt_desc in cgs:
        assets.append({
            "path": path,
            "category": "story_cg",
            "title": title,
            "width": 1920,
            "height": 1080,
            "format": "RGB",
            "prompt": f"masterpiece, best quality, ultra-detailed widescreen visual novel event CG, 1920x1080, 16:9, {prompt_desc}, cinematic lighting, sensual high-fantasy anime pin-up aesthetic",
            "negative_prompt": NEGATIVE_PROMPT,
        })

    # 6. Environments & Camp Backgrounds (12)
    bgs = [
        ("bg/bg_ashgate_hall.png", "Ashgate Citadel Great Hall, massive vaulted stone arches, banners of sun and moon, burning braziers, grand diplomatic interior"),
        ("bg/bg_thronefield_dawn.png", "The Thronefield under golden morning sky, massive alternating white and black monoliths anchored over deep chasm, solar rays"),
        ("bg/bg_thronefield_dusk.png", "The Thronefield under twilight starry sky, violet aurora reflections on dark obsidian monoliths, glowing runes"),
        ("bg/bg_thronefield_eclipse.png", "The Thronefield under celestial eclipse, swirling solar and lunar twilight vortex in sky, glowing leyline fissures"),
        ("bg/bg_war_tent_dawn.png", "House Aurelis War Tent interior, ivory silk pavilions, illuminated tactical map table, gold-trimmed weapon racks, glowing lamps"),
        ("bg/bg_war_tent_dusk.png", "The Umbrenholt War Tent interior, midnight velvet drapery, shadow-lanterns, obsidian drafting table, crystal astrolabes"),
        ("bg/bg_quarters_dawn.png", "Officer Private Quarters Dawn, comfortable silk bedding, wooden writing desk, morning sunlight streaming through pavilion flap"),
        ("bg/bg_quarters_dusk.png", "Officer Private Quarters Dusk, plush fur throws, candlelit research desk with scrolls, celestial star charts on walls"),
        ("bg/bg_prism_observatory.png", "Ancient Prism Observatory, colossal floating crystal prisms refracting cosmic light, ancient runic dials overlooking mountain peaks"),
        ("bg/bg_sunken_foundry.png", "Submerged Ancient Foundry, mythril forge machinery half-covered in crystal clear water, glowing sunken ley conduits"),
        ("bg/bg_obsidian_archive.png", "The Obsidian Archive, towering shelves of dark stone tablets, ancient treaties preserved in gravity stasis, purple ethereal light"),
        ("bg/bg_river_parley.png", "Misty Riverbank Border at Midnight, willow trees trailing in dark water, neutral stone gazebo, lanterns reflecting on calm river"),
    ]
    for path, prompt_desc in bgs:
        assets.append({
            "path": path,
            "category": "environment_bg",
            "width": 1920,
            "height": 1080,
            "format": "RGB",
            "prompt": f"masterpiece, best quality, highly detailed anime fantasy visual novel background, 1920x1080, no characters, {prompt_desc}, cinematic atmosphere",
            "negative_prompt": "characters, people, blurry, lowres, text, watermark",
        })

    # 7. UI Components & Textures (16)
    ui_items = [
        ("board/tile_dawnstone.png", 80, 80, "tile", "radiant polished ivory-gold marble chess tile texture, subtle golden bevel border"),
        ("board/tile_duskstone.png", 80, 80, "tile", "polished midnight obsidian chess tile texture, subtle starlit purple bevel border"),
        ("board/highlight_move.png", 80, 80, "highlight", "tactical green neon destination square highlight ring, semi-transparent center"),
        ("board/highlight_capture.png", 80, 80, "highlight", "tactical crimson hostile capture square highlight with warning corner brackets"),
        ("board/highlight_check.png", 80, 80, "highlight", "flaming radiant amber check alert overlay with pulsating outer glow"),
        ("board/highlight_oracle.png", 80, 80, "highlight", "pulsing celestial violet and gold foresight prediction square outline"),
        ("board/ward_aegis_overlay.png", 80, 80, "overlay", "translucent golden solar hexagonal barrier shield overlay with runic edges"),
        ("ui/arrow_queen_red.png", 280, 28, "arrow", "tactical red energy vector arrow pointing right, glowing crimson trail, clean alpha"),
        ("ui/arrow_warden_blue.png", 280, 28, "arrow", "tactical sapphire blue defensive vector arrow pointing right, solid kinetic trail, clean alpha"),
        ("ui/arrow_seer_violet.png", 280, 28, "arrow", "tactical violet arcane vector arrow pointing right, shimmering starlight trail, clean alpha"),
        ("ui/arrow_ally_gold.png", 280, 28, "arrow", "tactical brilliant gold allied vector arrow pointing right, solar flare trail, clean alpha"),
        ("ui/spells/spell_chrono.png", 80, 80, "spell", "circular spell icon Chrono-Pulse, glowing hourglass reversing time with golden gears"),
        ("ui/spells/spell_oracle.png", 80, 80, "spell", "circular spell icon Oracle's Gaze, mystical glowing third eye with celestial star rays"),
        ("ui/spells/spell_aegis.png", 80, 80, "spell", "circular spell icon Aegis Ward, glowing mythril kite shield deflecting purple lightning"),
        ("ui/spells/spell_advance.png", 80, 80, "spell", "circular spell icon Marshal's Advance, crossed winged spears surging forward with light"),
        ("ui/frame_hud_panel.png", 600, 900, "frame", "ornate high-fantasy visual novel side HUD panel frame, polished dark slate, gilded trim, clean transparent center"),
    ]
    for path, w, h, uitype, desc in ui_items:
        assets.append({
            "path": path,
            "category": "ui_texture",
            "ui_type": uitype,
            "width": w,
            "height": h,
            "format": "RGBA",
            "prompt": f"game UI graphic, {w}x{h} px, {desc}, isolated on transparent background",
            "negative_prompt": "blurry, low quality, artifacting",
        })

    manifest_data = {
        "version": "3.2",
        "total_assets": len(assets),
        "categories": {
            "character_sprite": 38,
            "action_cutin": 14,
            "advisor_bust": 8,
            "piece_token": 12,
            "story_cg": 10,
            "environment_bg": 12,
            "ui_texture": 16,
        },
        "assets": assets,
    }

    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"Generated {MANIFEST_PATH} with {len(assets)} assets.")

if __name__ == "__main__":
    build_manifest()
