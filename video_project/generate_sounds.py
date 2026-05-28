"""
Sound Synthesis Engine
======================
Generates WAV files for all sound effects used in the video.
Uses numpy + scipy for additive/subtractive synthesis.

Run:  python generate_sounds.py
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path
import os

SAMPLE_RATE = 44100
SOUNDS_DIR = Path(__file__).parent / "sounds"
SOUNDS_DIR.mkdir(exist_ok=True)

def normalize(audio):
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.95
    return audio

def envelope(audio, attack=0.01, release=0.3):
    """Apply attack/release envelope."""
    n = len(audio)
    attack_s = int(attack * SAMPLE_RATE)
    release_s = int(release * SAMPLE_RATE)
    env = np.ones(n)
    env[:attack_s] = np.linspace(0, 1, attack_s)
    if release_s > 0:
        env[-release_s:] = np.linspace(1, 0, release_s)
    return audio * env

def sine(freq, duration, phase=0):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return np.sin(2 * np.pi * freq * t + phase)

def saw(freq, duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return 2 * (freq * t - np.floor(freq * t + 0.5))

def square(freq, duration, duty=0.5):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return np.where((freq * t % 1) < duty, 1.0, -1.0)

def noise(duration, color='white'):
    n = int(SAMPLE_RATE * duration)
    if color == 'white':
        return np.random.uniform(-1, 1, n)
    elif color == 'pink':
        white = np.random.uniform(-1, 1, n)
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        a = [1, -2.494956002, 2.017265875, -0.522189400]
        pink = np.zeros(n)
        for i in range(n):
            pink[i] = white[i]
            for j in range(1, min(i+1, len(b))):
                pink[i] += b[j] * white[i-j]
            for j in range(1, min(i+1, len(a))):
                pink[i] -= a[j] * pink[i-j]
        return normalize(pink)
    elif color == 'brown':
        white = np.random.uniform(-1, 1, n)
        brown = np.cumsum(white)
        return normalize(brown)

# ─── Sound Generators ────────────────────────────────────────────────────

def big_bang_boom(duration=3.0):
    """Massive low-end explosion with high-frequency crackle."""
    sr = SAMPLE_RATE
    t = np.linspace(0, duration, int(sr * duration), False)

    # Sub-bass rumble (20-60 Hz)
    sub = sine(30, duration) * 0.4 + sine(45, duration) * 0.3 + sine(60, duration) * 0.2
    sub_env = np.exp(-t * 2.5)  # fast decay
    sub = sub * sub_env

    # Mid boom (80-150 Hz)
    mid = sine(80, duration) * 0.3 + sine(120, duration) * 0.2
    mid_env = np.exp(-t * 1.8)
    mid = mid * mid_env

    # High crackle
    crackle = noise(duration, 'white') * 0.15
    crackle_env = np.exp(-t * 5.0)
    crackle = crackle * crackle_env

    audio = sub + mid + crackle
    audio = normalize(audio)
    audio = envelope(audio, attack=0.001, release=0.5)
    return audio


def whoosh(duration=2.0, pitch_start=100, pitch_end=600):
    """Rising frequency whoosh effect."""
    sr = SAMPLE_RATE
    n = int(sr * duration)
    t = np.linspace(0, duration, n, False)

    freq = np.linspace(pitch_start, pitch_end, n)
    phase = np.cumsum(2 * np.pi * freq / sr)
    tone = np.sin(phase) * 0.3

    noise_whoosh = noise(duration, 'pink') * 0.2
    noise_env = np.linspace(0, 1, n) * np.exp(-t * 1.5)
    noise_whoosh = noise_whoosh * noise_env

    audio = tone + noise_whoosh
    audio = normalize(audio)
    audio = envelope(audio, attack=0.05, release=0.3)
    return audio


def star_twinkle(duration=0.6):
    """Bright, short sparkling chime."""
    sr = SAMPLE_RATE
    t = np.linspace(0, duration, int(sr * duration), False)

    freqs = [880, 1320, 1760, 2200]
    tone = np.zeros_like(t)
    for i, f in enumerate(freqs):
        tone += sine(f, duration) * (0.25 / (i + 1))

    env = np.exp(-t * 4.0)
    tone = tone * env

    # Add a little shimmer
    shimmer = sine(4400, duration) * 0.05
    shimmer = shimmer * env * env

    audio = tone + shimmer
    audio = normalize(audio)
    return audio


def galaxy_hum(duration=5.0):
    """Deep ambient drone suggesting vast space."""
    sr = SAMPLE_RATE
    t = np.linspace(0, duration, int(sr * duration), False)

    # Deep drone with slow modulation
    base = sine(55, duration) * 0.3
    mod = sine(0.5, duration, phase=0) * 0.5 + 0.5  # LFO
    base = base * (0.5 + 0.5 * mod)

    fifth = sine(82.5, duration) * 0.2
    octave = sine(110, duration) * 0.15

    sub = sine(27.5, duration) * 0.2

    pad_noise = noise(duration, 'pink') * 0.05

    audio = base + fifth + octave + sub + pad_noise
    audio = normalize(audio)
    audio = envelope(audio, attack=0.5, release=1.0)
    return audio


def solar_hum(duration=4.0):
    """Warm, slow orbital hum suggesting planetary motion."""
    sr = SAMPLE_RATE
    t = np.linspace(0, duration, int(sr * duration), False)

    freqs = [110, 146.83, 196]  # A2, D3, G3 — warm chord
    chord = np.zeros_like(t)
    for f in freqs:
        chord += sine(f, duration) * (0.2 / len(freqs))

    mod = sine(0.3, duration, phase=0) * 0.3 + 0.7
    chord = chord * mod

    rhythm = sine(2.0, duration, phase=0) * 0.5 + 0.5
    pulse = (rhythm > 0.8).astype(float) * 0.1
    pulse = pulse * np.exp(-t * 2.0)  # fade out

    audio = chord + pulse
    audio = normalize(audio)
    audio = envelope(audio, attack=0.3, release=0.8)
    return audio


def ocean_ambient(duration=5.0):
    """Deep underwater wash — filtered noise with slow modulation."""
    n = int(SAMPLE_RATE * duration)
    t = np.linspace(0, duration, n, False)

    brown = noise(duration, 'brown') * 0.3
    pink = noise(duration, 'pink') * 0.2

    # Slow wave modulation
    wave_lfo = sine(0.15, duration, phase=0) * 0.3 + 0.5
    brown = brown * wave_lfo
    pink = pink * (1 - wave_lfo * 0.3)

    audio = brown + pink
    audio = normalize(audio)
    audio = envelope(audio, attack=1.0, release=1.0)
    return audio


def life_spark(duration=1.0):
    """Crackling chemical spark — short, bright."""
    sr = SAMPLE_RATE
    t = np.linspace(0, duration, int(sr * duration), False)

    # Bright crackle
    pop = noise(duration, 'white') * 0.4
    pop_env = np.exp(-t * 8.0)
    pop = pop * pop_env

    # Rising tone
    freq = np.linspace(200, 2000, len(t))
    phase = np.cumsum(2 * np.pi * freq / sr)
    tone = np.sin(phase) * 0.3
    tone_env = np.exp(-t * 4.0)
    tone = tone * tone_env

    audio = pop + tone
    audio = normalize(audio)
    return audio


def bubble_pop(duration=0.3):
    """Small oxygen bubble popping."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = np.linspace(400, 800, len(t))
    phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
    tone = np.sin(phase) * 0.5
    tone = tone * np.exp(-t * 10.0)

    pop = noise(duration, 'white') * 0.3
    pop = pop * np.exp(-t * 15.0)

    audio = tone + pop
    audio = normalize(audio)
    return audio


def cell_division(duration=0.8):
    """Soft double-pop suggesting cell splitting."""
    sr = SAMPLE_RATE
    n = int(sr * duration)
    t = np.linspace(0, duration, n, False)

    pop1 = np.zeros(n)
    pop2 = np.zeros(n)

    p1_idx = int(0.1 * sr)
    p2_idx = int(0.45 * sr)
    p_dur = int(0.15 * sr)

    for i in range(p1_idx, min(p1_idx + p_dur, n)):
        frac = (i - p1_idx) / p_dur
        pop1[i] = np.sin(2 * np.pi * 300 * frac * 5) * (1 - frac)
    pop1 = pop1 * 0.4

    for i in range(p2_idx, min(p2_idx + p_dur, n)):
        frac = (i - p2_idx) / p_dur
        pop2[i] = np.sin(2 * np.pi * 350 * frac * 5) * (1 - frac)
    pop2 = pop2 * 0.3

    audio = pop1 + pop2
    audio = normalize(audio)
    return audio


def cambrian_chirp(duration=0.5):
    """Alien-like chirp for Cambrian creatures."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    freq = np.linspace(600, 1200, len(t))
    phase = np.cumsum(2 * np.pi * freq / SAMPLE_RATE)
    tone = np.sin(phase) * 0.3

    freq2 = np.linspace(800, 1600, len(t))
    phase2 = np.cumsum(2 * np.pi * freq2 / SAMPLE_RATE)
    tone2 = np.sin(phase2) * 0.15

    audio = (tone + tone2) * np.exp(-t * 3.0)
    audio = normalize(audio)
    return audio


def splash_water(duration=1.2):
    """Water splashing — fish emerging."""
    sr = SAMPLE_RATE
    n = int(sr * duration)
    t = np.linspace(0, duration, n, False)

    # Short whoosh
    w = whoosh(duration * 0.4, 100, 800) * 0.3
    whoosh_up = np.zeros(n)
    copy_len = min(len(w), n)
    whoosh_up[:copy_len] = w[:copy_len]

    # Bubbles
    b_len = int(duration * 0.6 * sr)
    b_t = np.linspace(0, duration * 0.6, b_len)
    bubbles = noise(duration * 0.6, 'pink')[:b_len] * 0.2
    bubbles = bubbles * np.exp(-b_t * 4.0) * (b_t > 0.1).astype(float)
    bubbles_padded = np.zeros(n)
    copy_len = min(b_len, n)
    bubbles_padded[:copy_len] = bubbles[:copy_len]

    # Splat
    s_len = int(duration * 0.15 * sr)
    splat = noise(duration * 0.15, 'white')[:s_len] * 0.5
    splat_env = np.exp(-np.linspace(0, 10, s_len))
    splat = splat * splat_env
    splat_padded = np.zeros(n)
    start = int(0.1 * sr)
    copy_len = min(s_len, n - start)
    splat_padded[start:start + copy_len] = splat[:copy_len]

    audio = whoosh_up + bubbles_padded + splat_padded
    audio = normalize(audio)
    audio = envelope(audio, attack=0.01, release=0.2)
    return audio


def dino_stomp(duration=0.8):
    """Low, heavy stomp."""
    sr = SAMPLE_RATE
    n = int(sr * duration)
    t = np.linspace(0, duration, n, False)

    thud = sine(40, duration) * 0.6 + sine(60, duration) * 0.3
    thud_env = np.exp(-t * 6.0)
    thud = thud * thud_env

    c_len = int(duration * 0.3 * sr)
    c_t = np.linspace(0, duration * 0.3, c_len)
    crunch = noise(duration * 0.3, 'white')[:c_len] * 0.2
    crunch = crunch * np.exp(-np.linspace(0, 8, c_len))
    crunch_padded = np.zeros(n)
    copy_len = min(c_len, n)
    crunch_padded[:copy_len] = crunch[:copy_len]

    sub = sine(25, duration) * 0.3
    sub = sub * np.exp(-t * 3.0)

    audio = thud + crunch_padded + sub
    audio = normalize(audio)
    return audio


def asteroid_impact(duration=3.0):
    """Massive impact — bigger version of big_bang_boom with debris."""
    sr = SAMPLE_RATE
    n = int(sr * duration)
    t = np.linspace(0, duration, n, False)

    boom = big_bang_boom(duration)
    boom = boom[:n] if len(boom) > n else np.pad(boom, (0, n - len(boom)))

    debris_rattle = noise(duration, 'white')[:n] * 0.15
    debris_env = np.exp(-t * 6.0) * (np.sin(t * 40) * 0.5 + 0.5)
    debris = debris_rattle * debris_env

    r_len = int(duration * 0.5 * sr)
    ring = sine(180, duration * 0.5)[:r_len] * 0.2
    ring = ring * np.exp(-np.linspace(0, 2.0, r_len))
    ring_padded = np.zeros(n)
    copy_len = min(r_len, n)
    ring_padded[:copy_len] = ring[:copy_len]

    audio = boom * 0.7 + debris + ring_padded
    audio = normalize(audio)
    audio = envelope(audio, attack=0.001, release=0.8)
    return audio


def mammal_scamper(duration=0.3):
    """Quick light patter for small mammals."""
    sr = SAMPLE_RATE
    n = int(sr * duration)
    taps = np.zeros(n)
    num_taps = np.random.randint(2, 5)
    for _ in range(num_taps):
        pos = np.random.randint(0, n)
        tap_len = int(0.02 * sr)
        for i in range(pos, min(pos + tap_len, n)):
            frac = (i - pos) / tap_len
            taps[i] = np.sin(2 * np.pi * 1500 * frac) * (1 - frac) * 0.15
    audio = taps
    audio = normalize(audio)
    return audio


def human_drum(duration=4.0):
    """Low rhythmic drum pattern suggesting human innovation."""
    sr = SAMPLE_RATE
    n = int(sr * duration)
    t = np.linspace(0, duration, n, False)

    # Slow heartbeat-like rhythm
    bpm = 72
    beat_interval = 60 / bpm
    beats = np.zeros(n)

    for i in range(int(duration / beat_interval)):
        beat_pos = int(i * beat_interval * sr)
        beat_len = int(0.12 * sr)
        for j in range(beat_pos, min(beat_pos + beat_len, n)):
            frac = (j - beat_pos) / beat_len
            beats[j] = np.sin(2 * np.pi * 60 * frac) * (1 - frac) * 0.5

    # Occasional higher accent
    accents = np.zeros(n)
    for i in range(0, int(duration / beat_interval), 4):
        acc_pos = int(i * beat_interval * sr)
        acc_len = int(0.08 * sr)
        for j in range(acc_pos, min(acc_pos + acc_len, n)):
            frac = (j - acc_pos) / acc_len
            accents[j] = np.sin(2 * np.pi * 200 * frac) * (1 - frac) * 0.2

    audio = beats + accents
    audio = normalize(audio)
    audio = envelope(audio, attack=0.05, release=0.5)
    return audio


def inspirational_swell(duration=6.0):
    """Rising pad with emotional resonance for the conclusion."""
    sr = SAMPLE_RATE
    n = int(sr * duration)
    t = np.linspace(0, duration, n, False)

    # Slow chord progression: C major → F major → G major → C major
    chord_prog = [
        ([261.63, 329.63, 523.25], 0),
        ([349.23, 440.00, 698.46], 1.5),
        ([392.00, 493.88, 783.99], 3.0),
        ([523.25, 659.25, 1046.50], 4.5),
    ]

    pad = np.zeros(n)
    for freqs, start_time in chord_prog:
        start_idx = int(start_time * sr)
        for f in freqs:
            tone = sine(f, duration - start_time) * 0.15
            tone = np.pad(tone, (start_idx, 0))[:n]
            pad += tone

    # Rising swell
    swell_env = np.linspace(0, 1, n) ** 0.5
    pad = pad * swell_env

    # Add shimmer on top
    shimmer = noise(duration, 'pink') * 0.05
    shimmer_env = np.linspace(0, 1, n) ** 2
    shimmer = shimmer * shimmer_env

    audio = pad + shimmer
    audio = normalize(audio)
    audio = envelope(audio, attack=1.5, release=1.0)
    return audio


def transition_swipe(duration=0.5):
    """Quick whoosh for chapter transitions."""
    whoosh_snd = whoosh(duration, 200, 1200) * 0.4
    return normalize(whoosh_snd)


def dna_twinkle(duration=0.4):
    """Quick bright spark for DNA/molecular events."""
    return normalize(star_twinkle(duration) * 0.8)


def forest_ambient(duration=5.0):
    """Gentle nature ambient for land scenes."""
    sr = SAMPLE_RATE
    n = int(sr * duration)
    t = np.linspace(0, duration, n, False)

    wind = noise(duration, 'pink')[:n] * 0.15
    lfo = sine(0.3, duration, phase=0)[:n] * 0.3 + 0.5
    wind = wind * lfo

    chirps = np.zeros(n)
    for _ in range(4):
        pos = np.random.randint(int(0.5 * sr), n - int(0.5 * sr))
        chirp_len = int(0.15 * sr)
        freq = np.random.uniform(1000, 2000)
        for i in range(pos, min(pos + chirp_len, n)):
            frac = (i - pos) / chirp_len
            chirps[i] = np.sin(2 * np.pi * freq * frac) * (1 - frac) * 0.06

    audio = wind + chirps
    audio = normalize(audio)
    audio = envelope(audio, attack=0.5, release=0.5)
    return audio


# ─── Generate All Sounds ────────────────────────────────────────────────

SOUND_FUNCS = {
    "big_bang_boom.wav": (big_bang_boom, 3.0),
    "inflation_whoosh.wav": (whoosh, 2.5),
    "star_twinkle.wav": (star_twinkle, 0.6),
    "galaxy_hum.wav": (galaxy_hum, 5.0),
    "solar_hum.wav": (solar_hum, 4.0),
    "ocean_ambient.wav": (ocean_ambient, 5.0),
    "life_spark.wav": (life_spark, 1.0),
    "bubble_pop.wav": (bubble_pop, 0.3),
    "cell_division.wav": (cell_division, 0.8),
    "cambrian_chirp.wav": (cambrian_chirp, 0.5),
    "splash_water.wav": (splash_water, 1.2),
    "dino_stomp.wav": (dino_stomp, 0.8),
    "asteroid_impact.wav": (asteroid_impact, 3.0),
    "mammal_scamper.wav": (mammal_scamper, 0.3),
    "human_drum.wav": (human_drum, 4.0),
    "inspirational_swell.wav": (inspirational_swell, 6.0),
    "transition_swipe.wav": (transition_swipe, 0.5),
    "dna_twinkle.wav": (dna_twinkle, 0.4),
    "forest_ambient.wav": (forest_ambient, 5.0),
}

def generate_all():
    print("Generating sound effects...")
    for filename, (func, duration) in SOUND_FUNCS.items():
        filepath = SOUNDS_DIR / filename
        if filepath.exists():
            print(f"  ✓ {filename} — already exists")
            continue
        audio = func(duration)
        wavfile.write(str(filepath), SAMPLE_RATE, (audio * 32767).astype(np.int16))
        size_kb = os.path.getsize(filepath) / 1024
        print(f"  ✓ {filename} — {duration}s, {size_kb:.0f}KB")

    print(f"\nAll sounds generated in {SOUNDS_DIR}/")

if __name__ == "__main__":
    generate_all()
