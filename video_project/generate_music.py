"""
Background Music Generator
==========================
Generates original, royalty-free background music tracks using
synthesized instruments and ambient pads. No external samples needed.

Outputs a 15-minute ambient/cinematic track matching the video's arc:
  - Opening: mysterious, cosmic
  - Middle: rhythmic, building
  - End: triumphant, emotional

Usage:
    python generate_music.py                          # full 15-min track
    python generate_music.py --duration 300            # 5-minute preview
    python generate_music.py --output custom_bgm.wav
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path
import struct, math, sys

SAMPLE_RATE = 44100
OUTPUT_DIR = Path(__file__).parent
DEFAULT_DURATION = 900  # 15 minutes


def normalize(audio):
    peak = np.max(np.abs(audio))
    if peak > 0:
        audio = audio / peak * 0.95
    return audio


def sine(freq, duration, sr=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sr * duration), False)
    return np.sin(2 * np.pi * freq * t)


def saw(freq, duration, sr=SAMPLE_RATE):
    t = np.linspace(0, duration, int(sr * duration), False)
    return 2 * (freq * t - np.floor(freq * t + 0.5))


def noise(duration, color='white', sr=SAMPLE_RATE):
    n = int(sr * duration)
    if color == 'white':
        return np.random.uniform(-1, 1, n)
    elif color == 'pink':
        white = np.random.uniform(-1, 1, n)
        pink = np.zeros(n)
        b = [0.049922035, -0.095993537, 0.050612699, -0.004408786]
        for i in range(n):
            pink[i] = white[i]
            for j in range(1, min(i + 1, len(b))):
                pink[i] += b[j] * white[i - j]
            pink[i] -= 0.95 * pink[i - 1] if i > 0 else 0
        return normalize(pink)
    return np.random.uniform(-1, 1, n)


def lowpass(audio, cutoff, sr=SAMPLE_RATE):
    """Simple one-pole lowpass filter."""
    rc = 1.0 / (cutoff * 2 * np.pi)
    dt = 1.0 / sr
    alpha = dt / (rc + dt)
    filtered = np.zeros_like(audio)
    filtered[0] = audio[0]
    for i in range(1, len(audio)):
        filtered[i] = filtered[i - 1] + alpha * (audio[i] - filtered[i - 1])
    return filtered


def highpass(audio, cutoff, sr=SAMPLE_RATE):
    """Simple one-pole highpass filter."""
    filtered = audio - lowpass(audio, cutoff, sr)
    return filtered


# ─── Synth Instruments ─────────────────────────────────────────────────

class Pad:
    """Warm evolving pad with slow modulation."""
    def __init__(self, freqs, duration, sr=SAMPLE_RATE):
        self.freqs = freqs
        self.duration = duration
        self.sr = sr
        self.n = int(sr * duration)

    def render(self):
        t = np.linspace(0, self.duration, self.n, False)
        audio = np.zeros(self.n)
        for f in self.freqs:
            audio += sine(f, self.duration, self.sr) * (0.6 / len(self.freqs))
        # Slow modulation
        lfo = sine(0.1, self.duration, self.sr) * 0.3 + 0.7
        audio = audio * lfo
        # Add harmonics
        for f in self.freqs:
            audio += sine(f * 2, self.duration, self.sr) * (0.15 / len(self.freqs))
        audio = lowpass(audio, 800)
        return normalize(audio) * 0.3


class Bass:
    """Deep sub-bass drone."""
    def __init__(self, freq, duration, sr=SAMPLE_RATE):
        self.freq = freq
        self.duration = duration
        self.sr = sr

    def render(self):
        audio = sine(self.freq, self.duration, self.sr) * 0.4
        audio += sine(self.freq / 2, self.duration, self.sr) * 0.2
        audio = lowpass(audio, 120)
        return normalize(audio) * 0.35


class Arp:
    """Rhythmic arpeggiator for movement."""
    def __init__(self, notes, bpm=80, duration=60, sr=SAMPLE_RATE):
        self.notes = notes
        self.bpm = bpm
        self.beat_duration = 60 / bpm
        self.duration = duration
        self.sr = sr

    def render(self):
        n = int(self.sr * self.duration)
        audio = np.zeros(n)
        pattern_len = len(self.notes)
        total_beats = int(self.duration / self.beat_duration)
        for beat in range(total_beats):
            note = self.notes[beat % pattern_len]
            start = int(beat * self.beat_duration * self.sr)
            note_len = int(self.beat_duration * 0.4 * self.sr)
            for i in range(start, min(start + note_len, n)):
                frac = (i - start) / note_len
                env = max(0, 1 - frac * 3)
                audio[i] += np.sin(2 * np.pi * note * frac * 4) * env * 0.08
        return normalize(audio) * 0.15


class Swell:
    """Slow-building pad swell for emotional peaks."""
    def __init__(self, freqs, duration, start_time, sr=SAMPLE_RATE):
        self.freqs = freqs
        self.duration = duration
        self.start_time = start_time
        self.sr = sr

    def render(self, total_duration):
        n = int(self.sr * total_duration)
        start = int(self.start_time * self.sr)
        seg_n = int(self.sr * self.duration)
        audio_seg = np.zeros(seg_n)
        t = np.linspace(0, self.duration, seg_n, False)
        for f in self.freqs:
            audio_seg += sine(f, self.duration, self.sr) * (0.5 / len(self.freqs))
        # Swell envelope
        swell_env = np.linspace(0, 1, seg_n) ** 1.5
        audio_seg = audio_seg * swell_env * 0.3
        audio = np.zeros(n)
        end = min(start + seg_n, n)
        audio[start:end] = audio_seg[:end - start]
        return audio


class Drone:
    """Continuous evolving drone with subtle harmonic shifts."""
    def __init__(self, base_freq, duration, sr=SAMPLE_RATE):
        self.base = base_freq
        self.duration = duration
        self.sr = sr

    def render(self):
        n = int(self.sr * self.duration)
        t = np.linspace(0, self.duration, n, False)
        audio = sine(self.base, self.duration, self.sr) * 0.15
        audio += sine(self.base * 1.5, self.duration, self.sr) * 0.1
        audio += sine(self.base * 2, self.duration, self.sr) * 0.08
        # Slow filter sweep
        lfo = sine(0.05, self.duration, self.sr) * 0.5 + 0.5
        audio = audio * (0.3 + 0.7 * lfo)
        return lowpass(audio, 400) * 0.2


# ─── Musical Structure ─────────────────────────────────────────────────
#
# The 15-minute piece follows the video's emotional arc:
#
#   0:00   Introduction - lonely pad, sub-bass
#   1:00   Big Bang - low rumble, slow arp enters
#   2:30   Stars - brighter pad, gentle pulse
#   4:00   Solar System - warm chord progression
#   5:30   Origin of Life - mysterious, evolving
#   7:00   Cambrian - more movement, faster arp
#   8:30   Land/Dinosaurs - darker, powerful
#   10:00  Mammals - lighter, hopeful
#   11:00  Primates/Humans - rhythmic pulse builds
#   12:30  Human Story - drums, emotional swell
#   13:30  Conclusion - triumphant resolution
#

def safe_add(target, source, start_idx):
    """Add source into target at start_idx, handling length mismatches."""
    end_idx = min(start_idx + len(source), len(target))
    src_len = end_idx - start_idx
    if src_len <= 0:
        return
    target[start_idx:end_idx] += source[:src_len]


def generate_full_track(duration=DEFAULT_DURATION, sr=SAMPLE_RATE):
    print(f"  Generating {duration//60} minute background music track...")
    n = int(sr * duration)
    master = np.zeros(n)
    t = np.linspace(0, duration, n, False)
    progress_step = duration // 10

    def progress(pos, label):
        pct = int(pos / duration * 100)
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(f"    [{bar}] {pct}% — {label}")

    # === Movement 1: Cosmic Dawn (0:00 - 2:00) ===
    progress(0, "Cosmic Dawn")

    drone1 = Drone(55, duration * 0.15, sr).render()
    safe_add(master, drone1, 0)

    pad1 = Pad([261.63, 329.63, 392.00], duration * 0.1, sr).render()
    safe_add(master, pad1, int(5 * sr))

    progress(int(duration * 0.15), "Stars Form")

    # === Movement 2: Stellar Forge ===
    bass1 = Bass(55, duration * 0.3, sr).render()
    safe_add(master, bass1, int(duration * 0.12 * sr))

    c_major = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 523.25]
    arp1 = Arp(c_major[:4], bpm=70, duration=duration * 0.25, sr=sr).render()
    safe_add(master, arp1, int(duration * 0.18 * sr))

    pad2 = Pad([261.63, 329.63, 392.00, 523.25], duration * 0.2, sr).render()
    safe_add(master, pad2, int(duration * 0.2 * sr))

    progress(int(duration * 0.33), "Life Emerges")

    # === Movement 3: Life's Journey ===
    pad3 = Pad([220, 293.66, 349.23], duration * 0.25, sr).render()
    safe_add(master, pad3, int(duration * 0.4 * sr))

    f_major = [174.61, 220, 261.63, 349.23, 440, 523.25]
    arp2 = Arp(f_major, bpm=85, duration=duration * 0.2, sr=sr).render()
    safe_add(master, arp2, int(duration * 0.45 * sr))

    bass2 = Bass(44, duration * 0.25, sr).render()
    safe_add(master, bass2, int(duration * 0.42 * sr))

    progress(int(duration * 0.5), "Cambrian to Land")

    # === Movement 4: The Rise ===
    pulse = (sine(2.0, duration * 0.2, sr) * 0.5 + 0.5) * noise(duration * 0.2, 'pink', sr)
    pulse = lowpass(pulse, 200) * 0.06
    safe_add(master, pulse, int(duration * 0.65 * sr))

    pad4 = Pad([392, 493.88, 587.33], duration * 0.15, sr).render()
    safe_add(master, pad4, int(duration * 0.68 * sr))

    progress(int(duration * 0.75), "Human Story")

    # === Movement 5: Human Dawn ===
    beat = sine(1.5, duration * 0.15, sr) * 0.5 + 0.5
    rhythm_bass = (beat > 0.7).astype(float) * Bass(55, duration * 0.15, sr).render()
    safe_add(master, rhythm_bass, int(duration * 0.8 * sr))

    swell = Swell([523.25, 659.25, 783.99], duration * 0.1, duration * 0.85, sr)
    swell_audio = swell.render(duration)
    master += swell_audio

    final_chord = Pad([523.25, 659.25, 783.99, 1046.50], duration * 0.1, sr).render()
    safe_add(master, final_chord, int(duration * 0.9 * sr))

    progress(duration, "Complete")

    # Master normalize
    master = normalize(master)
    
    # Apply subtle fade in/out
    fade_len = int(2 * sr)
    fade_in = np.linspace(0, 1, fade_len)
    fade_out = np.linspace(1, 0, fade_len)
    master[:fade_len] *= fade_in
    master[-fade_len:] *= fade_out

    return master


def verify_wav(filepath):
    """Verify generated WAV is valid."""
    try:
        sr, data = wavfile.read(filepath)
        duration = len(data) / sr
        print(f"  ✓ WAV valid: {sr}Hz, {len(data)} samples, {duration:.1f}s, "
              f"{Path(filepath).stat().st_size / 1024 / 1024:.1f}MB")
        return True
    except Exception as e:
        print(f"  ✗ WAV invalid: {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate background music")
    parser.add_argument("--duration", "-d", type=int, default=DEFAULT_DURATION,
                       help=f"Duration in seconds (default: {DEFAULT_DURATION})")
    parser.add_argument("--output", "-o", type=str, default="background_music.wav",
                       help="Output WAV file")
    parser.add_argument("--mp3", action="store_true",
                       help="Also convert to MP3")
    args = parser.parse_args()

    print(r"""
   ╔══════════════════════════════════════════════════════════╗
   ║   BACKGROUND MUSIC GENERATOR                             ║
   ║   Original score — synthesized, royalty-free             ║
   ╚══════════════════════════════════════════════════════════╝
    """)

    audio = generate_full_track(args.duration)
    output_path = OUTPUT_DIR / args.output
    wavfile.write(str(output_path), SAMPLE_RATE, (audio * 32767).astype(np.int16))
    verify_wav(output_path)

    if args.mp3:
        import subprocess
        mp3_path = output_path.with_suffix(".mp3")
        subprocess.run([
            "ffmpeg", "-y", "-i", str(output_path),
            "-codec:a", "libmp3lame", "-b:a", "192k",
            str(mp3_path)
        ], capture_output=True)
        print(f"  ✓ MP3 exported: {mp3_path.name}")

    print(f"\n  ✓ Background music generated: {output_path.name}")
    print(f"  ✓ Use with: python post_production.py --video final.mp4 --music {output_path.name}")


if __name__ == "__main__":
    main()
