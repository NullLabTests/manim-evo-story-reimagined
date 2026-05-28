"""
Voiceover Narration Generator
==============================
Generates TTS narration clips, builds timing table, creates SRT subtitles,
and re-mixes the final video with professional 3-track audio.

Pipeline:
  1. Generate chapter-by-chapter narration WAVs via edge-tts
  2. Build timing table with per-chapter timestamps
  3. Generate SRT subtitle file
  4. Re-mix: video (SFX) + voiceover + trimmed background music
  5. Output to media/master/

Usage:
    python generate_voiceover.py                   # Full pipeline
    python generate_voiceover.py --skip-tts        # Use existing WAVs
    python generate_voiceover.py --voice en-US-AriaNeural
"""

import asyncio, json, os, subprocess, sys, tempfile, time
import edge_tts
from pathlib import Path

VIDEO_DIR = Path(__file__).parent
MASTER_DIR = VIDEO_DIR.parent / "media" / "master"
VOICEOVER_DIR = VIDEO_DIR / "voiceover"
SOUNDS_DIR = VIDEO_DIR / "sounds"

VOICE = "en-US-AriaNeural"  # Female US English narrator

# ─── Chapter Narration Script ────────────────────────────────────────────
# Each entry: (chapter_key, narration_text, estimated_duration_sec)
# duration_sec is the expected length of the spoken narration (approximate).
# The actual timing will be measured from the generated audio.

CHAPTERS = [
    ("title", [
        "From the Big Bang to You.",
        "The epic 13.8 billion year story of evolution.",
    ]),
    ("big_bang", [
        "Everything began 13.8 billion years ago.",
        "From an infinitely dense point, space itself exploded outward.",
        "In the first fraction of a second, the universe expanded faster than light.",
    ]),
    ("stars", [
        "The first stars ignited, fusing hydrogen into helium.",
        "Heavier elements — carbon, oxygen, iron — were forged in their cores.",
        "When these stars died, they scattered these elements across the cosmos.",
    ]),
    ("solar_system", [
        "Our Sun formed from a collapsing nebula of gas and dust.",
        "Planets coalesced from the leftover debris.",
        "Earth was born — a molten rock world that would become our home.",
    ]),
    ("origin_of_life", [
        "In primordial oceans, simple molecules began to assemble.",
        "Then something extraordinary happened: the first self-replicating molecules formed.",
        "Life had begun. The Last Universal Common Ancestor — LUCA — gave rise to everything alive today.",
    ]),
    ("great_oxidation", [
        "Cyanobacteria learned to photosynthesize, releasing oxygen into the atmosphere.",
        "This Great Oxidation Event poisoned most anaerobic life.",
        "But it paved the way for complex, energy-hungry organisms to evolve.",
    ]),
    ("eukaryotes", [
        "One simple cell engulfed another, creating a symbiotic relationship.",
        "This fusion produced the first complex cell — the eukaryote.",
        "With a nucleus and mitochondria, life could now grow more intricate.",
    ]),
    ("cambrian", [
        "In just 20 million years — a blink of geological time — most major animal body plans appeared.",
        "The Cambrian Explosion filled the oceans with bizarre and wonderful creatures.",
    ]),
    ("sea_to_land", [
        "Life moved onto land. Plants came first, then arthropods.",
        "Tiktaalik grew limbs and became the first tetrapod.",
        "Dinosaurs dominated the Earth for 165 million years.",
    ]),
    ("rise_of_mammals", [
        "Then, 66 million years ago, an asteroid struck the Yucatán Peninsula.",
        "The impact wiped out the dinosaurs, but small mammals survived.",
        "With the dinosaurs gone, mammals diversified and grew larger.",
    ]),
    ("primates", [
        "Primates evolved in the trees, developing binocular vision and grasping hands.",
        "Our lineage split from other apes around 7 million years ago.",
    ]),
    ("human_evolution", [
        "Our hominin lineage began in Africa. Australopithecus walked upright.",
        "Homo habilis made tools. Homo erectus mastered fire.",
        "Homo sapiens — us — emerged 300,000 years ago, spreading across the globe.",
    ]),
    ("conclusion", [
        "You are made of stardust. Every atom in your body was forged in a star.",
        "The universe is not just outside you — it is inside you.",
        "You are the universe experiencing itself.",
    ]),
]


def run(cmd, desc="", capture=True):
    if desc:
        print(f"  → {desc}")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0 and capture and result.stderr:
        print(f"  ⚠ {result.stderr[-200:]}")
    return result


def step(msg):
    print(f"\n  ── {msg} ──")


def format_srt_time(seconds):
    """Convert seconds to SRT time format: HH:MM:SS,mmm"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


async def generate_tts(text, output_path, voice=VOICE):
    """Generate TTS audio file using edge-tts."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, voice)
    with open(output_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
    return output_path


def get_duration(file_path):
    """Get audio duration in seconds using ffprobe."""
    result = subprocess.run(
        f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{file_path}"',
        shell=True, capture_output=True, text=True,
    )
    return float(result.stdout.strip()) if result.stdout.strip() else 0


def build_timing_table():
    """Build a timing table for all narration segments.

    Returns list of (chapter_key, sentence_index, text, start_time, end_time)
    """
    segments = []
    current_time = 0.0

    for key, sentences in CHAPTERS:
        chapter_start = current_time
        for i, sentence in enumerate(sentences):
            segments.append({
                "chapter": key,
                "sentence": i,
                "text": sentence,
                "start": current_time,
                "end": current_time + 0.1,  # placeholder, updated after measurement
                "file": VOICEOVER_DIR / f"{key}_{i:02d}.wav",
            })
            current_time += 0.1  # placeholder
        # Add chapter padding (silence between chapters)
        current_time += 2.0

    return segments


def measure_and_update(segments):
    """Measure actual duration from generated WAVs and update timing table.
    Adds 1.5s padding between chapters."""
    current_time = 0.0
    last_chapter = None
    for seg in segments:
        # Add padding between chapters
        if last_chapter is not None and seg["chapter"] != last_chapter:
            current_time += 1.5
        last_chapter = seg["chapter"]

        if seg["file"].exists():
            duration = get_duration(seg["file"])
        else:
            duration = 2.0  # fallback
        seg["start"] = current_time
        seg["end"] = current_time + duration
        current_time += duration
    return segments


def generate_srt(segments, output_path):
    """Generate SRT subtitle file from timed segments."""
    with open(output_path, "w") as f:
        idx = 1
        for i, seg in enumerate(segments):
            # Check if next segment is in same chapter (different sentence)
            is_new_chapter = (
                i == 0
                or seg["chapter"] != segments[i - 1]["chapter"]
            )

            # Add chapter title subtitle
            if is_new_chapter:
                chapter_titles = {
                    "title": "From the Big Bang to You",
                    "big_bang": "The Big Bang",
                    "stars": "Stars & Galaxies",
                    "solar_system": "The Solar System",
                    "origin_of_life": "Origin of Life",
                    "great_oxidation": "The Great Oxidation",
                    "eukaryotes": "Eukaryotes",
                    "cambrian": "The Cambrian Explosion",
                    "sea_to_land": "From Sea to Land",
                    "rise_of_mammals": "Rise of the Mammals",
                    "primates": "The Primate Lineage",
                    "human_evolution": "Human Evolution",
                    "conclusion": "Conclusion",
                }
                title = chapter_titles.get(seg["chapter"], seg["chapter"])
                # Chapter title overlay (1 second)
                f.write(f"{idx}\n")
                f.write(f"{format_srt_time(max(0, seg['start'] - 0.2))} --> {format_srt_time(seg['start'] + 1.0)}\n")
                f.write(f"{title}\n\n")
                idx += 1

            # Narration subtitle
            f.write(f"{idx}\n")
            f.write(f"{format_srt_time(seg['start'])} --> {format_srt_time(seg['end'])}\n")
            f.write(f"{seg['text']}\n\n")
            idx += 1


def get_chapter_boundaries(segments):
    """Get start/end times for each chapter based on segment timing."""
    boundaries = {}
    for seg in segments:
        key = seg["chapter"]
        if key not in boundaries:
            boundaries[key] = {"start": seg["start"], "end": seg["end"]}
        else:
            boundaries[key]["end"] = seg["end"]
    return boundaries


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate voiceover narration")
    parser.add_argument("--skip-tts", action="store_true", help="Skip TTS generation")
    parser.add_argument("--voice", type=str, default=VOICE, help="TTS voice name")
    parser.add_argument("--dry-run", action="store_true", help="Show plan only")
    args = parser.parse_args()

    print(r"""
   ╔══════════════════════════════════════════════════════════╗
   ║   VOICEOVER NARRATION + SUBTITLES + RE-MIX               ║
   ║   From the Big Bang to You                              ║
   ╚══════════════════════════════════════════════════════════╝
    """)

    VOICEOVER_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Generate TTS narration clips ──
    step("1/5  Generating TTS narration clips")

    if args.dry_run:
        print(f"  Would generate {sum(len(c[1]) for c in CHAPTERS)} clips")
        print(f"  Voice: {args.voice}")
        return

    if not args.skip_tts:
        total_clips = 0
        for key, sentences in CHAPTERS:
            for i, text in enumerate(sentences):
                output = VOICEOVER_DIR / f"{key}_{i:02d}.wav"
                if output.exists():
                    continue
                print(f"  [{key}] Generating: \"{text[:50]}...\"")
                asyncio.run(generate_tts(text, output, args.voice))
                total_clips += 1
        print(f"  ✓ Generated {total_clips} new clips (or all existed)")

    # ── Step 2: Build timing table ──
    step("2/5  Building timing table")

    segments = build_timing_table()
    segments = measure_and_update(segments)
    total_narration_duration = segments[-1]["end"] if segments else 0

    # Print chapter timing summary
    boundaries = get_chapter_boundaries(segments)
    print(f"\n  Chapter Timing:")
    for key, bounds in boundaries.items():
        dur = bounds["end"] - bounds["start"]
        print(f"    {key:20s}  {bounds['start']:6.1f}s - {bounds['end']:6.1f}s  ({dur:.1f}s)")

    print(f"\n  Total narration: {total_narration_duration:.1f}s")

    # Save timing table as JSON
    timing_json = MASTER_DIR / "voiceover_timing.json"
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    with open(timing_json, "w") as f:
        json.dump([{
            "chapter": s["chapter"],
            "text": s["text"],
            "start": round(s["start"], 2),
            "end": round(s["end"], 2),
        } for s in segments], f, indent=2)
    print(f"  ✓ Saved: {timing_json}")

    # ── Step 3: Generate SRT subtitles ──
    step("3/5  Generating SRT subtitles")

    srt_path = MASTER_DIR / "subtitles.srt"
    generate_srt(segments, srt_path)
    print(f"  ✓ Saved: {srt_path}")

    # ── Step 4: Find rendered video and trim/fade music ──
    step("4/5  Preparing audio tracks")

    # Find the rendered video
    rendered = (
        MASTER_DIR / "FullStoryScene_enhanced_sounds.mp4"
    )
    if not rendered.exists():
        # Fall back to the Manim output
        candidates = [
            VIDEO_DIR.parent / "media" / "videos" / "full_video_sound" / "1080p60" / "FullStoryScene.mp4",
            MASTER_DIR / "FullStoryScene_enhanced_sounds_preview.mp4",
        ]
        for c in candidates:
            if c.exists():
                rendered = c
                break

    if not rendered.exists():
        print(f"  ⚠ No rendered video found. Run render first.")
        return

    # Get video duration
    video_duration = get_duration(str(rendered))
    print(f"  Video: {rendered.name} ({video_duration:.1f}s)")

    # Trim the background music to match video length
    music_src = VIDEO_DIR / "background_music_15min.wav"
    music_trimmed = MASTER_DIR / "music_trimmed.wav"
    if music_src.exists():
        run(
            f'ffmpeg -y -i "{music_src}" -t {video_duration} -c copy "{music_trimmed}" 2>/dev/null',
            desc=f"Trimming music to {video_duration:.0f}s"
        )

    # Voiceover master: concatenate all chapter narration with appropriate gaps
    voiceover_master = MASTER_DIR / "voiceover_master.wav"

    # Build a concat file for FFmpeg
    concat_lines = []
    for seg in segments:
        if seg["file"].exists():
            concat_lines.append(f"file '{seg['file'].absolute()}'")

    if concat_lines:
        concat_file = MASTER_DIR / "_voiceover_concat.txt"
        with open(concat_file, "w") as f:
            for line in concat_lines:
                f.write(line + "\n")
        run(
            f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c copy "{voiceover_master}" 2>/dev/null',
            desc="Joining voiceover clips"
        )
        concat_file.unlink()

    # ── Step 5: Final re-mix ──
    step("5/5  Re-mixing 3-track audio: SFX + Voiceover + Music")

    final_output = MASTER_DIR / "FullStoryScene_enhanced_sounds_v2.mp4"

    if music_trimmed.exists() and voiceover_master.exists():
        # 3-track mix: SFX (from video, with embedded fades) + voiceover + music
        # Voiceover is centered, music is ducked
        filter_complex = (
            "[1:a]volume=1.0[a_voice];"
            "[2:a]volume=0.08[a_music];"
            "[0:a][a_voice][a_music]amix=inputs=3:duration=first:dropout_transition=2"
            ",loudnorm=I=-16:TP=-1.5:LRA=11[a]"
        )
        cmd = (
            f'ffmpeg -y -i "{rendered}" -i "{voiceover_master}" -i "{music_trimmed}" '
            f'-filter_complex "{filter_complex}" '
            f'-map 0:v -map "[a]" '
            f'-c:v copy -c:a aac -b:a 192k '
            f'"{final_output}" 2>/dev/null'
        )
    elif voiceover_master.exists():
        # 2-track mix: video SFX + voiceover
        filter_complex = (
            "[1:a]volume=1.0[a_voice];"
            "[0:a][a_voice]amix=inputs=2:duration=first:dropout_transition=2"
            ",loudnorm=I=-16:TP=-1.5:LRA=11[a]"
        )
        cmd = (
            f'ffmpeg -y -i "{rendered}" -i "{voiceover_master}" '
            f'-filter_complex "{filter_complex}" '
            f'-map 0:v -map "[a]" '
            f'-c:v copy -c:a aac -b:a 192k '
            f'"{final_output}" 2>/dev/null'
        )
    else:
        print("  ⚠ No voiceover to mix. Copying video as-is.")
        final_output = rendered

    if cmd:
        result = run(cmd, desc="Mixing 3-track audio...")
        if result and result.returncode == 0:
            print(f"  ✓ Mixed successfully")
        else:
            print(f"  ⚠ Mix failed, keeping original")

    # ── Final Report ──
    step("Complete")
    final_size = "N/A"
    if final_output.exists():
        final_size = f"{final_output.stat().st_size / 1024 / 1024:.0f} MB"

    print(f"""
  ╔═══════════════════════════════════════════════════════╗
  ║          VOICEOVER + SUBTITLES COMPLETE                ║
  ╚═══════════════════════════════════════════════════════╝

  Video:          {final_output.relative_to(VIDEO_DIR.parent) if final_output.exists() else 'N/A'}
  Size:           {final_size}
  Duration:       {video_duration:.0f}s ({video_duration/60:.1f} min)

  Audio tracks:
    • Chapter SFX          (embedded in video)
    • Voiceover narration  ({len(segments)} clips, {total_narration_duration:.0f}s)
    • Background music     (trimmed to match)

  Subtitles:      {srt_path.relative_to(VIDEO_DIR.parent) if srt_path.exists() else 'N/A'}
  Timing data:    {timing_json.relative_to(VIDEO_DIR.parent) if timing_json.exists() else 'N/A'}
  """.replace("Parent", ".."))


if __name__ == "__main__":
    main()
