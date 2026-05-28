"""
Sound Design Engine
===================
Professional layered audio for the 13.8-billion-year story.

Two audio layers per chapter:
  - BACKGROUND:  continuous ambiance (drone, hum, wind, water) that plays
                 throughout the entire chapter
  - SPOT FX:     precisely-timed sound effects (explosions, twinkles,
                 splashes, impacts) that sync with specific visuals

Usage in Manim scene:
    from sound_design import SoundDesign
    sd = SoundDesign(self)
    sd.play_chapter("big_bang")   # schedules all sounds for that chapter
"""

import os
from pathlib import Path

SOUNDS_DIR = Path(__file__).parent / "sounds"


# ─── Sound Design Database ──────────────────────────────────────────────
#
# Each chapter has:
#   background: (filename, gain) — loops continuously
#   spot_fx:    list of (filename, delay_seconds, gain) — one-shot
#
# delay_seconds is relative to the start of the chapter.

DESIGN = {
    "title": {
        "background": ("galaxy_hum.wav", 0.12),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.3),
            ("star_twinkle.wav", 2.5, 0.12),
            ("inspirational_swell.wav", 5.0, 0.15),
        ],
    },
    "big_bang": {
        "background": ("galaxy_hum.wav", 0.10),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.3),
            ("big_bang_boom.wav", 2.0, 0.80),
            ("inflation_whoosh.wav", 4.0, 0.50),
            ("star_twinkle.wav", 8.0, 0.10),
        ],
    },
    "stars": {
        "background": ("galaxy_hum.wav", 0.10),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.25),
            ("star_twinkle.wav", 2.0, 0.25),
            ("star_twinkle.wav", 3.5, 0.20),
            ("star_twinkle.wav", 5.0, 0.18),
            ("star_twinkle.wav", 7.5, 0.15),
            ("star_twinkle.wav", 10.0, 0.12),
        ],
    },
    "solar_system": {
        "background": ("solar_hum.wav", 0.15),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.25),
            ("star_twinkle.wav", 4.0, 0.10),
            ("star_twinkle.wav", 6.0, 0.08),
        ],
    },
    "origin_of_life": {
        "background": ("ocean_ambient.wav", 0.12),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.25),
            ("life_spark.wav", 5.0, 0.50),
            ("dna_twinkle.wav", 8.0, 0.20),
            ("cell_division.wav", 12.0, 0.30),
            ("star_twinkle.wav", 14.0, 0.08),
        ],
    },
    "great_oxidation": {
        "background": ("ocean_ambient.wav", 0.10),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.25),
            ("bubble_pop.wav", 3.0, 0.12),
            ("bubble_pop.wav", 4.0, 0.10),
            ("bubble_pop.wav", 5.0, 0.15),
            ("bubble_pop.wav", 6.5, 0.10),
            ("bubble_pop.wav", 8.0, 0.12),
            ("bubble_pop.wav", 9.5, 0.08),
        ],
    },
    "eukaryotes": {
        "background": ("ocean_ambient.wav", 0.08),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.25),
            ("dna_twinkle.wav", 3.0, 0.18),
            ("cell_division.wav", 6.5, 0.30),
            ("star_twinkle.wav", 9.0, 0.10),
        ],
    },
    "cambrian": {
        "background": ("ocean_ambient.wav", 0.10),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.25),
            ("cambrian_chirp.wav", 2.0, 0.22),
            ("cambrian_chirp.wav", 3.5, 0.18),
            ("cambrian_chirp.wav", 5.0, 0.20),
            ("cambrian_chirp.wav", 6.5, 0.15),
            ("cambrian_chirp.wav", 8.0, 0.10),
        ],
    },
    "sea_to_land": {
        "background": ("forest_ambient.wav", 0.10),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.25),
            ("splash_water.wav", 4.0, 0.50),
            ("dino_stomp.wav", 9.0, 0.40),
            ("dino_stomp.wav", 10.5, 0.35),
            ("cambrian_chirp.wav", 12.0, 0.08),
        ],
    },
    "rise_of_mammals": {
        "background": ("forest_ambient.wav", 0.08),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.25),
            ("asteroid_impact.wav", 1.5, 0.70),
            ("mammal_scamper.wav", 6.0, 0.12),
            ("mammal_scamper.wav", 7.0, 0.10),
            ("mammal_scamper.wav", 8.0, 0.10),
            ("mammal_scamper.wav", 9.0, 0.08),
            ("star_twinkle.wav", 11.0, 0.08),
        ],
    },
    "primates": {
        "background": ("forest_ambient.wav", 0.10),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.25),
            ("dna_twinkle.wav", 3.0, 0.12),
            ("human_drum.wav", 4.0, 0.20),
            ("star_twinkle.wav", 7.0, 0.08),
        ],
    },
    "human_evolution": {
        "background": ("human_drum.wav", 0.12),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.25),
            ("dna_twinkle.wav", 4.0, 0.10),
            ("star_twinkle.wav", 6.0, 0.08),
            ("star_twinkle.wav", 9.0, 0.12),
            ("inspirational_swell.wav", 12.0, 0.15),
        ],
    },
    "conclusion": {
        "background": ("galaxy_hum.wav", 0.08),
        "spot_fx": [
            ("transition_swipe.wav", 0.0, 0.20),
            ("inspirational_swell.wav", 1.0, 0.40),
            ("star_twinkle.wav", 6.0, 0.10),
            ("star_twinkle.wav", 10.0, 0.08),
            ("inspirational_swell.wav", 14.0, 0.25),
        ],
    },
}


class SoundDesign:
    """Manages all audio for a scene. Call play_chapter() at chapter start."""

    def __init__(self, scene):
        self.scene = scene
        self._verify_sounds()

    def _verify_sounds(self):
        """Check all referenced sound files exist."""
        missing = []
        for chapter, design in DESIGN.items():
            bg_file = design["background"][0]
            if not (SOUNDS_DIR / bg_file).exists():
                missing.append(bg_file)
            for fx_file, _, _ in design["spot_fx"]:
                if not (SOUNDS_DIR / fx_file).exists():
                    missing.append(fx_file)
        if missing:
            unique = list(set(missing))
            print(f"  ⚠ Sound files missing: {unique}")
            print(f"  → Run: python generate_sounds.py")

    def play_chapter(self, chapter_key):
        """Schedule all sounds for a chapter. Call at chapter start."""
        if chapter_key not in DESIGN:
            print(f"  ⚠ Unknown chapter: {chapter_key}")
            return

        design = DESIGN[chapter_key]
        scene = self.scene

        # 1. Schedule background ambiance (plays at chapter start, repeats)
        bg_file, bg_gain = design["background"]
        bg_path = SOUNDS_DIR / bg_file
        if bg_path.exists():
            scene.add_sound(str(bg_path), time_offset=0, gain=bg_gain)

        # 2. Schedule all spot effects
        for fx_file, delay, gain in design["spot_fx"]:
            fx_path = SOUNDS_DIR / fx_file
            if fx_path.exists():
                scene.add_sound(str(fx_path), time_offset=delay, gain=gain)

    def play_between_chapters(self, delay=0):
        """Play a transition sound between chapters."""
        swipe = SOUNDS_DIR / "transition_swipe.wav"
        if swipe.exists():
            self.scene.add_sound(str(swipe), time_offset=delay, gain=0.12)

    @staticmethod
    def list_design():
        """Print the full sound design plan."""
        print("\n  ═══════════ SOUND DESIGN ═══════════")
        for chapter, design in DESIGN.items():
            bg = design["background"]
            fx_count = len(design["spot_fx"])
            fx_names = ", ".join(f[0].replace(".wav", "") for f in design["spot_fx"][:3])
            if fx_count > 3:
                fx_names += f" +{fx_count - 3} more"
            print(f"  {chapter:20s}  BG: {bg[0]:25s}  FX: {fx_names}")
        print()

    @staticmethod
    def print_timing_guide():
        """Print voiceover cue points."""
        print("""
   ╔══════════════════════════════════════════════════════════════╗
   ║               VOICEOVER & SOUND TIMING GUIDE                ║
   ╠══════════════════════════════════════════════════════════════╣
   ║  Ch. 1  TITLE                                               ║
   ║   0s  Swipe in     → "From the Big Bang to You..."          ║
   ║   5s  Swell begins → "The 13.8-billion-year story..."       ║
   ║                                                              ║
   ║  Ch. 2  BIG BANG                                            ║
   ║   0s  Swipe        → "Everything began 13.8 billion..."     ║
   ║   2s  BOOM!        → "...from an infinitely dense point"    ║
   ║   4s  Whoosh       → "Space itself expanded..."             ║
   ║                                                              ║
   ║  Ch. 3  STARS & GALAXIES                                    ║
   ║   0s  Swipe        → "The first stars ignited..."           ║
   ║   2s  Twinkle      → "...forging hydrogen into helium"      ║
   ║   7s  Twinkles     → "Heavier elements were born..."        ║
   ║                                                              ║
   ║  Ch. 4  SOLAR SYSTEM                                        ║
   ║   0s  Swipe        → "Our Sun formed from a nebula..."      ║
   ║   2s  Warm hum     → "Planets coalesced from debris..."     ║
   ║                                                              ║
   ║  Ch. 5  ORIGIN OF LIFE                                      ║
   ║   0s  Swipe        → "In primordial oceans..."              ║
   ║   1s  Ocean        → "...simple molecules assembled"        ║
   ║   5s  LIFE SPARK!  → "Then something extraordinary..."      ║
   ║   8s  DNA twinkle  → "The first self-replicating system"    ║
   ║  12s  Cell divide  → "LUCA — the Last Universal Common..."  ║
   ║                                                              ║
   ║  Ch. 6  GREAT OXIDATION                                     ║
   ║   0s  Swipe        → "Cyanobacteria transformed Earth"      ║
   ║   3s  Bubbles      → "Oxygen began to fill the oceans..."   ║
   ║                                                              ║
   ║  Ch. 7  EUKARYOTES                                          ║
   ║   0s  Swipe        → "One cell engulfed another..."         ║
   ║   3s  DNA twinkle  → "Creating the first complex cell"      ║
   ║   7s  Cell divide  → "The nucleus and mitochondria..."      ║
   ║                                                              ║
   ║  Ch. 8  CAMBRIAN EXPLOSION                                  ║
   ║   0s  Swipe        → "In just 20 million years..."          ║
   ║   2s  Alien chirps → "Most major animal body plans..."      ║
   ║                                                              ║
   ║  Ch. 9  SEA TO LAND                                         ║
   ║   0s  Swipe        → "Life moved onto land..."              ║
   ║   4s  SPLASH!      → "Tiktaalik grew limbs..."              ║
   ║   9s  STOMP!       → "Dinosaurs dominated for 165 my"       ║
   ║                                                              ║
   ║  Ch. 10 RISE OF MAMMALS                                     ║
   ║   0s  Swipe        → "Then, 66 million years ago..."        ║
   ║   2s  IMPACT!      → "An asteroid changed everything"       ║
   ║   6s  Scamper      → "Small mammals survived..."            ║
   ║                                                              ║
   ║  Ch. 11 PRIMATES                                            ║
   ║   0s  Swipe        → "Primates evolved in the trees..."     ║
   ║   4s  Drums        → "Binocular vision, opposable thumbs"   ║
   ║                                                              ║
   ║  Ch. 12 HUMAN EVOLUTION                                     ║
   ║   0s  Swipe        → "Our hominin lineage began..."         ║
   ║   1s  Drums        → "Australopithecus → Homo sapiens"      ║
   ║   6s  Twinkle      → "Tools, fire, art, agriculture"        ║
   ║  12s  Swell        → "We spread across the globe"           ║
   ║                                                              ║
   ║  Ch. 13 CONCLUSION                                          ║
   ║   0s  Swipe        → Timeline recap                         ║
   ║   1s  SWELL!       → "You are made of stardust"             ║
   ║  14s  Swell fades  → "You are the universe experiencing..." ║
   ╚══════════════════════════════════════════════════════════════╝
        """)


def add_chapter_sounds(scene, chapter_key):
    """Convenience function: creates SoundDesign and plays chapter."""
    sd = SoundDesign(scene)
    sd.play_chapter(chapter_key)


def add_between_chapter_sound(scene, delay=0):
    """Convenience function: plays transition between chapters."""
    sd = SoundDesign(scene)
    sd.play_between_chapters(delay)
