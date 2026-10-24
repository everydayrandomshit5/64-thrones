"""
generate_audio.py - Synthesizes orchestral BGM and combat SFX for 64-Thrones: High-Glamour Edition.
Complies with Section 7.1 & 8.2 of the Master Build Bible.
"""

import json
import math
import struct
import wave
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT_DIR / "tools" / "audio_manifest.json"
AUDIO_DIR = ROOT_DIR / "game" / "audio"

SAMPLE_RATE = 44100


def clamp_pcm(val: float) -> int:
    """Clamps float sample (-1.0 to 1.0) into 16-bit signed integer (-32768 to 32767)."""
    return max(-32768, min(32767, int(val * 32767.0)))


def write_wav(path: Path, samples: list[float], channels: int = 2):
    """Writes a list of normalized float audio samples to a 16-bit PCM WAV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)
        wav.setframerate(SAMPLE_RATE)
        frames = bytearray()
        if channels == 1:
            for s in samples:
                frames.extend(struct.pack("<h", clamp_pcm(s)))
        else:
            # Stereo: samples is list of (left, right) or float mono duplicated
            for s in samples:
                if isinstance(s, (tuple, list)):
                    l, r = s[0], s[1]
                else:
                    l = r = s
                frames.extend(struct.pack("<hh", clamp_pcm(l), clamp_pcm(r)))
        wav.writeframes(frames)


def osc_sine(freq: float, t: float) -> float:
    return math.sin(2.0 * math.pi * freq * t)


def osc_triangle(freq: float, t: float) -> float:
    phase = (freq * t) % 1.0
    return 4.0 * abs(phase - 0.5) - 1.0


def osc_organ(freq: float, t: float) -> float:
    """Multi-harmonic warm tone (fundamental + 2nd, 3rd, 4th harmonics)."""
    return (
        0.55 * osc_sine(freq, t)
        + 0.25 * osc_sine(freq * 2.0, t)
        + 0.15 * osc_sine(freq * 3.0, t)
        + 0.05 * osc_sine(freq * 4.0, t)
    )


def osc_brass(freq: float, t: float) -> float:
    """Rich brass timbre with odd & even harmonics."""
    return (
        0.50 * osc_sine(freq, t)
        + 0.30 * osc_triangle(freq * 2.0, t)
        + 0.15 * osc_sine(freq * 3.0, t)
        + 0.05 * osc_sine(freq * 5.0, t)
    )


def osc_harp(freq: float, t: float, duration: float) -> float:
    """Plucked string with rapid transient and warm decay."""
    decay = math.exp(-6.0 * (t % duration))
    return decay * (0.7 * osc_sine(freq, t) + 0.3 * osc_triangle(freq * 2.0, t))


# --- BGM Generators ---

def gen_bgm_ashgate_theme(duration: float = 12.0) -> list[tuple[float, float]]:
    """Summit of Ashgate: Regal minor-key brass, sweeping chords, and harp arpeggios."""
    n_samples = int(SAMPLE_RATE * duration)
    # Chord progression: Dm -> Bb -> F -> C / Am (3 seconds per bar)
    chords = [
        ([146.83, 220.0, 293.66, 349.23], [73.42, 110.0]),  # Dm (D3, A3, D4, F4), bass D2, A2
        ([116.54, 233.08, 293.66, 349.23], [58.27, 116.54]), # Bb
        ([174.61, 261.63, 349.23, 440.0], [87.31, 130.81]),  # F
        ([130.81, 196.0, 261.63, 329.63], [65.41, 98.0]),    # C
    ]
    bar_dur = duration / len(chords)
    samples = []

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        bar_idx = min(int(t / bar_dur), len(chords) - 1)
        bar_t = t % bar_dur
        chord_notes, bass_notes = chords[bar_idx]

        # Chord pad
        pad_l, pad_r = 0.0, 0.0
        for idx, freq in enumerate(chord_notes):
            v = osc_organ(freq, t) * 0.12
            if idx % 2 == 0:
                pad_l += v * 0.9
                pad_r += v * 0.5
            else:
                pad_l += v * 0.5
                pad_r += v * 0.9

        # Brass Bass
        bass = sum(osc_brass(bf, t) for bf in bass_notes) * 0.15

        # Arpeggiated Harp Motif (8 notes per bar)
        arp_step = int((bar_t / bar_dur) * 8) % len(chord_notes)
        arp_freq = chord_notes[arp_step] * 2.0  # Octave higher
        harp_t = bar_t % (bar_dur / 8.0)
        harp_env = math.exp(-12.0 * harp_t)
        harp = osc_sine(arp_freq, t) * harp_env * 0.18

        # Subtle stereo pan
        l = pad_l + bass * 0.5 + harp * 0.7
        r = pad_r + bass * 0.5 + harp * 0.3

        # Fade in and loop-tail fade out
        fade_env = 1.0
        if t < 0.5:
            fade_env = t / 0.5
        elif t > duration - 0.5:
            fade_env = (duration - t) / 0.5

        samples.append((l * fade_env * 0.85, r * fade_env * 0.85))

    return samples


def gen_bgm_dawn_march(duration: float = 10.0) -> list[tuple[float, float]]:
    """Sunblade Vanguard: Heroic G-major brass march with galloping pulse."""
    n_samples = int(SAMPLE_RATE * duration)
    # G -> D -> Em -> C
    chords = [
        ([196.0, 246.94, 293.66, 392.0], 98.0),   # G
        ([146.83, 220.0, 293.66, 369.99], 73.42), # D
        ([164.81, 196.0, 246.94, 329.63], 82.41), # Em
        ([130.81, 164.81, 196.0, 261.63], 65.41), # C
    ]
    bar_dur = duration / len(chords)
    samples = []

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        bar_idx = min(int(t / bar_dur), len(chords) - 1)
        bar_t = t % bar_dur
        chord, bass_freq = chords[bar_idx]

        # Galloping March Pulse (dotted rhythm: 1, 2.5, 3.5)
        beat_t = bar_t % 0.625
        pulse = math.exp(-18.0 * beat_t) * osc_brass(bass_freq, t) * 0.22

        # Triumphant Horn Harmony
        horn = sum(osc_brass(cf, t) for cf in chord[:3]) * 0.10

        # High trumpet lead
        melody_notes = [392.0, 440.0, 493.88, 587.33]
        m_idx = int((t * 2.0)) % len(melody_notes)
        m_freq = melody_notes[m_idx]
        lead = osc_sine(m_freq, t) * 0.12 * (0.8 + 0.2 * math.sin(6 * math.pi * t))

        out = pulse + horn + lead
        fade = min(1.0, t / 0.4) * min(1.0, (duration - t) / 0.4)
        samples.append((out * fade * 0.8, out * fade * 0.8))

    return samples


def gen_bgm_dusk_requiem(duration: float = 10.0) -> list[tuple[float, float]]:
    """Velvet Dominion: Deep gothic brooding strings in C-minor with bell chimes."""
    n_samples = int(SAMPLE_RATE * duration)
    # Cm -> Ab -> Fm -> G
    chords = [
        ([130.81, 155.56, 196.0, 261.63], 65.41),  # Cm
        ([103.83, 130.81, 164.81, 207.65], 51.91), # Ab
        ([87.31, 103.83, 130.81, 174.61], 43.65),  # Fm
        ([98.0, 123.47, 146.83, 196.0], 49.0),     # G
    ]
    bar_dur = duration / len(chords)
    samples = []

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        bar_idx = min(int(t / bar_dur), len(chords) - 1)
        bar_t = t % bar_dur
        chord, bass_freq = chords[bar_idx]

        # Dark Cello Pad with slow vibrato
        vibrato = 1.0 + 0.015 * math.sin(5.0 * 2.0 * math.pi * t)
        cello = sum(osc_triangle(cf * vibrato, t) for cf in chord) * 0.08
        sub_bass = osc_sine(bass_freq, t) * 0.20

        # Amethyst Moon-Bell Chime every 2.5 seconds
        bell_t = bar_t
        bell_env = math.exp(-3.5 * bell_t)
        bell = (osc_sine(523.25 * 2, t) + 0.5 * osc_sine(784.0 * 2, t)) * bell_env * 0.15

        l = (cello * 0.8 + sub_bass * 0.6 + bell * 0.7)
        r = (cello * 0.8 + sub_bass * 0.6 + bell * 0.3)
        fade = min(1.0, t / 0.5) * min(1.0, (duration - t) / 0.5)
        samples.append((l * fade * 0.85, r * fade * 0.85))

    return samples


def gen_bgm_war_tent(duration: float = 12.0) -> list[tuple[float, float]]:
    """Campfire Fellowship: Warm acoustic lute and flute pastoral harmony."""
    n_samples = int(SAMPLE_RATE * duration)
    # A major / F#m / D / E (Warm campfire acoustic progression)
    roots = [220.0, 185.0, 146.83, 164.81]
    bar_dur = duration / len(roots)
    samples = []

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        bar_idx = min(int(t / bar_dur), len(roots) - 1)
        bar_t = t % bar_dur
        root = roots[bar_idx]

        # Fingerpicked Lute arpeggiation (6 notes per bar)
        step = int((bar_t / bar_dur) * 6)
        offsets = [1.0, 1.25, 1.5, 2.0, 1.5, 1.25]
        note_freq = root * offsets[step]
        step_t = bar_t % (bar_dur / 6.0)
        lute_env = math.exp(-8.0 * step_t)
        lute = (osc_triangle(note_freq, t) + 0.3 * osc_sine(note_freq * 2, t)) * lute_env * 0.25

        # Warm Wooden Flute melodic overlay
        flute_freq = root * 2.0
        flute = osc_sine(flute_freq, t) * 0.08 * (0.8 + 0.2 * math.sin(4 * math.pi * t))

        l = (lute * 0.7 + flute * 0.5)
        r = (lute * 0.5 + flute * 0.7)
        fade = min(1.0, t / 0.5) * min(1.0, (duration - t) / 0.5)
        samples.append((l * fade * 0.85, r * fade * 0.85))

    return samples


def gen_bgm_parley(duration: float = 8.0) -> list[tuple[float, float]]:
    """Parley: Tense diplomatic suspense, rhythmic pizzicato pulse."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    base_freq = 110.0  # A2

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        # Steady tense pizzicato ticking at 120 bpm (every 0.5 sec)
        tick_t = t % 0.5
        tick_env = math.exp(-25.0 * tick_t)
        pizz = osc_triangle(base_freq * 2.0, t) * tick_env * 0.35

        # Swelling dissonance
        swell = math.sin(math.pi * t / duration) * (osc_sine(220.0, t) + osc_sine(233.08, t)) * 0.12

        s = pizz + swell
        fade = min(1.0, t / 0.3) * min(1.0, (duration - t) / 0.3)
        samples.append((s * fade * 0.85, s * fade * 0.85))

    return samples


def gen_bgm_monolith_climax(duration: float = 12.0) -> list[tuple[float, float]]:
    """The Unbroken Concord: Grand unified climax, thundering orchestral chords."""
    n_samples = int(SAMPLE_RATE * duration)
    # D -> G -> A -> D (majestic cadence)
    prog = [
        ([146.83, 220.0, 293.66, 369.99, 440.0], 73.42),
        ([196.0, 246.94, 293.66, 392.0, 493.88], 98.0),
        ([220.0, 277.18, 329.63, 440.0, 554.37], 110.0),
        ([293.66, 369.99, 440.0, 587.33, 739.99], 146.83),
    ]
    bar_dur = duration / len(prog)
    samples = []

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        bar_idx = min(int(t / bar_dur), len(prog) - 1)
        chord, bass_freq = prog[bar_idx]

        # Full Symphonic Brass Chords
        symphony = sum(osc_brass(cf, t) for cf in chord) * 0.09
        timpani_t = t % 1.5
        timpani = math.exp(-8.0 * timpani_t) * osc_sine(bass_freq * 0.75, t) * 0.35

        val = symphony + timpani
        fade = min(1.0, t / 0.5) * min(1.0, (duration - t) / 0.5)
        samples.append((val * fade * 0.85, val * fade * 0.85))

    return samples


def gen_bgm_epilogue(duration: float = 10.0) -> list[tuple[float, float]]:
    """Eltheris Reborn: Peaceful piano and violin resolution."""
    n_samples = int(SAMPLE_RATE * duration)
    chords = [
        [261.63, 329.63, 392.0],  # C
        [220.0, 261.63, 329.63],  # Am
        [174.61, 220.0, 261.63],  # F
        [196.0, 246.94, 293.66],  # G
    ]
    bar_dur = duration / len(chords)
    samples = []

    for i in range(n_samples):
        t = i / SAMPLE_RATE
        bar_idx = min(int(t / bar_dur), len(chords) - 1)
        chord = chords[bar_idx]

        # Gentle Piano Chord Decay
        piano_t = (t % bar_dur)
        piano_env = math.exp(-2.5 * piano_t)
        piano = sum(osc_sine(f, t) + 0.2 * osc_sine(f * 2, t) for f in chord) * piano_env * 0.14

        # Solo Violin
        v_freq = chord[-1] * 2.0
        violin = osc_organ(v_freq, t) * 0.12 * (0.85 + 0.15 * math.sin(6 * math.pi * t))

        out = piano + violin
        fade = min(1.0, t / 0.4) * min(1.0, (duration - t) / 0.4)
        samples.append((out * fade * 0.85, out * fade * 0.85))

    return samples


# --- SFX Generators ---

def gen_sfx_piece_move(duration: float = 0.25) -> list[float]:
    """Crisp polished marble piece tap with body resonance."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-32.0 * t)
        click = osc_triangle(320.0, t) * 0.6 + osc_sine(160.0, t) * 0.4
        samples.append(click * env * 0.9)
    return samples


def gen_sfx_piece_capture(duration: float = 0.45) -> list[float]:
    """Metallic sword clash and resonant capture impact."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        transient = math.exp(-40.0 * t) * (osc_sine(1200.0, t) + osc_triangle(2400.0, t)) * 0.5
        tail = math.exp(-12.0 * t) * (osc_sine(440.0, t) + osc_sine(660.0, t)) * 0.5
        samples.append((transient + tail) * 0.9)
    return samples


def gen_sfx_check(duration: float = 0.65) -> list[float]:
    """Urgent brass/stinger alarm warning the King is in check."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-6.0 * t)
        # Diminished 5th tension chord (C5 + F#5)
        chord = (osc_brass(523.25, t) + osc_brass(739.99, t) + osc_brass(1046.5, t)) * 0.33
        samples.append(chord * env * 0.95)
    return samples


def gen_sfx_checkmate(duration: float = 1.5) -> list[float]:
    """Triumphant multi-voice victory fanfare."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    notes = [523.25, 659.25, 783.99, 1046.5]  # C Major Arpeggio Fanfare
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        step = min(int(t * 4), len(notes) - 1)
        freq = notes[step]
        env = math.exp(-3.0 * (t % 0.25)) if t < 1.0 else math.exp(-2.5 * (t - 0.75))
        fanfare = osc_brass(freq, t) * env * 0.7
        samples.append(fanfare * 0.9)
    return samples


def gen_sfx_spell_cast(duration: float = 0.8) -> list[float]:
    """Mystical celestial chime and swirling arcane resonance."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        sweep_freq = 400.0 + 1200.0 * (t / duration)
        shimmer = (osc_sine(sweep_freq, t) + 0.4 * osc_sine(sweep_freq * 1.5, t))
        env = math.sin(math.pi * t / duration) ** 0.8
        samples.append(shimmer * env * 0.85)
    return samples


def gen_sfx_chrono_pulse(duration: float = 0.7) -> list[float]:
    """Clockwork metronome tick + time-dilation reverse frequency sweep."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        # Reverse sweep
        sweep_freq = 1800.0 - 1400.0 * (t / duration)
        sweep = osc_sine(sweep_freq, t)
        tick = osc_triangle(880.0, t) * math.exp(-45.0 * (t % 0.15))
        env = math.exp(-4.0 * t)
        samples.append((sweep * 0.6 + tick * 0.4) * env * 0.85)
    return samples


def gen_sfx_armor_break(duration: float = 0.9) -> list[float]:
    """Heavy plate shatter crunch and deep bass impact (for state_b cut-in)."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        impact = math.exp(-15.0 * t) * osc_triangle(90.0, t) * 0.7
        # Glass/metal shatter high harmonics
        shatter = math.exp(-18.0 * t) * (osc_sine(2800.0, t) + osc_triangle(4200.0, t) + osc_sine(1600.0, t)) * 0.35
        samples.append((impact + shatter) * 0.9)
    return samples


def gen_sfx_button_click(duration: float = 0.15) -> list[float]:
    """Subtle parchment/crystal UI click."""
    n_samples = int(SAMPLE_RATE * duration)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        env = math.exp(-50.0 * t)
        click = osc_triangle(600.0, t) * 0.8
        samples.append(click * env * 0.75)
    return samples


# Dispatch Map
GENERATORS = {
    "audio/bgm_ashgate_theme.wav": gen_bgm_ashgate_theme,
    "audio/bgm_dawn_march.wav": gen_bgm_dawn_march,
    "audio/bgm_dusk_requiem.wav": gen_bgm_dusk_requiem,
    "audio/bgm_war_tent.wav": gen_bgm_war_tent,
    "audio/bgm_parley.wav": gen_bgm_parley,
    "audio/bgm_monolith_climax.wav": gen_bgm_monolith_climax,
    "audio/bgm_epilogue.wav": gen_bgm_epilogue,
    "audio/sfx_piece_move.wav": gen_sfx_piece_move,
    "audio/sfx_piece_capture.wav": gen_sfx_piece_capture,
    "audio/sfx_check.wav": gen_sfx_check,
    "audio/sfx_checkmate.wav": gen_sfx_checkmate,
    "audio/sfx_spell_cast.wav": gen_sfx_spell_cast,
    "audio/sfx_chrono_pulse.wav": gen_sfx_chrono_pulse,
    "audio/sfx_armor_break.wav": gen_sfx_armor_break,
    "audio/sfx_button_click.wav": gen_sfx_button_click,
}


def generate_all_audio():
    """Generates all 15 production audio assets defined in audio_manifest.json."""
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing {MANIFEST_PATH}")

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    audio_items = manifest.get("audio", [])
    print(f"===========================================================")
    print(f"[64-THRONES] AUDIO ASSET GENERATOR ({len(audio_items)} Tracks)")
    print(f"Target Directory: {AUDIO_DIR}")
    print(f"===========================================================\n")

    count = 0
    for item in audio_items:
        rel_path = item["path"]
        dur = item.get("duration_sec", 1.0)
        cat = item.get("category", "sfx")
        target_path = ROOT_DIR / "game" / rel_path

        gen_fn = GENERATORS.get(rel_path)
        if not gen_fn:
            print(f"[WARN] No generator for {rel_path}, skipping.")
            continue

        channels = 2 if cat == "bgm" else 1
        samples = gen_fn(duration=dur)
        write_wav(target_path, samples, channels=channels)
        count += 1
        print(f"  [OK] {rel_path} ({cat.upper()}, {dur:.1f}s, {channels}ch)")

    print(f"\n[DONE] Successfully generated {count} / {len(audio_items)} audio tracks.")


if __name__ == "__main__":
    generate_all_audio()
