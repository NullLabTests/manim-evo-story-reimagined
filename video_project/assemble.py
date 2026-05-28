"""
Final Assembly Pipeline
=======================
Assembles the complete master video from AI-generated chapters, Manim overlays,
voiceover narration, sound effects, and background music.

Usage:
    python assemble.py                         # Full assembly
    python assemble.py --quick                 # 480p preview
    python assemble.py --skip-narration         # Skip voiceover
    python assemble.py --scratch               # Regenerate everything
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

VIDEO_DIR = Path(__file__).parent
PROJECT_DIR = VIDEO_DIR.parent
MEDIA_DIR = PROJECT_DIR / "media"
MASTER_DIR = MEDIA_DIR / "master"
SCENES_DIR = MEDIA_DIR / "scenes"
OVERLAYS_DIR = MEDIA_DIR / "overlays"
SOUNDS_DIR = VIDEO_DIR / "sounds"
VOICEOVER_DIR = VIDEO_DIR / "voiceover"

CHAPTERS = [
    "title", "big_bang", "stars", "solar_system",
    "origin_of_life", "great_oxidation", "eukaryotes",
    "cambrian", "sea_to_land", "rise_of_mammals",
    "primates", "human_evolution", "conclusion",
]


def run(cmd, desc="", capture=True):
    if desc:
        print(f"  → {desc}")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0 and capture:
        err = result.stderr.strip()[-300:] if result.stderr.strip() else ""
        if err:
            print(f"  ⚠ {err}")
    return result


def step(msg):
    print(f"\n  ── {msg} ──")


def get_duration(file_path):
    result = run(
        f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{file_path}"',
    )
    try:
        return float(result.stdout.strip())
    except (ValueError, TypeError):
        return 0


def find_chapter_videos():
    """Find available chapter videos in scenes directory."""
    found = []
    for ch in CHAPTERS:
        candidates = [
            SCENES_DIR / f"{ch}.mp4",
            SCENES_DIR / f"{ch}.mov",
            MEDIA_DIR / f"{ch}.mp4",
        ]
        for c in candidates:
            if c.exists():
                found.append((ch, c))
                break
        else:
            print(f"  ⚠ Missing chapter: {ch}")
    return found


def concat_chapters(chapter_videos, output_path):
    """Concatenate chapter videos using FFmpeg concat demuxer."""
    concat_file = MASTER_DIR / "_chapters.txt"
    MASTER_DIR.mkdir(parents=True, exist_ok=True)

    with open(concat_file, "w") as f:
        for key, path in chapter_videos:
            f.write(f"file '{path.absolute()}'\n")

    result = run(
        f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c copy "{output_path}"',
        desc="Concatenating chapter videos",
    )
    concat_file.unlink(missing_ok=True)
    return result.returncode == 0 if result else False


def add_audio(video_path, narration_path, music_path, output_path):
    """Mix video with narration and background music."""
    inputs = f'-i "{video_path}"'
    filter_parts = []
    map_parts = ["-map 0:v"]
    input_idx = 1

    if narration_path and narration_path.exists():
        inputs += f' -i "{narration_path}"'
        filter_parts.append(f"[{input_idx}:a]volume=1.0[a_voice]")
        input_idx += 1

    if music_path and music_path.exists():
        inputs += f' -i "{music_path}"'
        filter_parts.append(f"[{input_idx}:a]volume=0.08[a_music]")
        input_idx += 1

    if not filter_parts:
        filter_complex = "[0:a]loudnorm=I=-16:TP=-1.5:LRA=11[a]"
    else:
        voice_ref = "a_voice" if narration_path and narration_path.exists() else None
        music_ref = "a_music" if music_path and music_path.exists() else None
        mix_inputs = []
        if voice_ref:
            mix_inputs.append(f"[{voice_ref}]")
        if music_ref:
            mix_inputs.append(f"[{music_ref}]")
        mix_inputs.append("[0:a]")
        mix_str = "+".join(mix_inputs)
        filter_complex = ";".join(filter_parts)
        filter_complex += f";{mix_str}amix=inputs={len(mix_inputs)}:duration=first:dropout_transition=2,loudnorm=I=-16:TP=-1.5:LRA=11[a]"

    cmd = (
        f'ffmpeg -y {inputs} '
        f'-filter_complex "{filter_complex}" '
        f'{" ".join(map_parts)} -map "[a]" '
        f'-c:v copy -c:a aac -b:a 192k '
        f'"{output_path}" 2>/dev/null'
    )
    result = run(cmd, desc="Mixing audio tracks")
    return result.returncode == 0 if result else False


def add_fades(input_path, output_path):
    """Add video and audio fades."""
    duration = get_duration(input_path)
    fade_d = min(2.0, duration * 0.05)

    cmd = (
        f'ffmpeg -y -i "{input_path}" '
        f'-vf "fade=t=in:st=0:d={fade_d},fade=t=out:st={duration - fade_d}:d={fade_d}" '
        f'-af "afade=t=in:d={fade_d},afade=t=out:st={duration - fade_d}:d={fade_d}" '
        f'-c:v libx264 -crf 18 -preset slow '
        f'-c:a copy '
        f'"{output_path}" 2>/dev/null'
    )
    result = run(cmd, desc="Applying fades")
    return result.returncode == 0 if result else False


def assemble(quick=False, skip_narration=False):
    """Run the full assembly pipeline."""
    start_time = time.time()
    MASTER_DIR.mkdir(parents=True, exist_ok=True)

    quality_suffix = "_preview" if quick else ""
    output_name = f"EvolutionStory_Reimagined{quality_suffix}.mp4"
    output_path = MASTER_DIR / output_name

    step("1/4  Finding chapter videos")
    chapter_videos = find_chapter_videos()
    if not chapter_videos:
        print("  ✗ No chapter videos found. Run generate_chapter.py first.")
        return False
    print(f"  Found {len(chapter_videos)}/{len(CHAPTERS)} chapters")

    step("2/4  Concatenating chapters")
    concat_video = MASTER_DIR / f"_concat{quality_suffix}.mp4"
    if not concat_chapters(chapter_videos, concat_video):
        print("  ✗ Concatenation failed")
        return False
    concat_dur = get_duration(concat_video)
    print(f"  Duration: {concat_dur:.1f}s ({concat_dur/60:.1f} min)")

    step("3/4  Mixing audio")
    narration = None if skip_narration else (MASTER_DIR / "voiceover_master.wav")
    music = VIDEO_DIR / "background_music_15min.wav"
    mixed = MASTER_DIR / f"_mixed{quality_suffix}.mp4"
    if not add_audio(concat_video, narration, music, mixed):
        print("  ⚠ Audio mix issue, continuing with video only")
        mixed = concat_video

    step("4/4  Finalizing with fades")
    if not add_fades(mixed, output_path):
        print("  ✗ Finalization failed")
        return False

    # Cleanup temp files
    for tmp in [concat_video, mixed]:
        if tmp.exists() and tmp != concat_video:
            tmp.unlink()

    elapsed = time.time() - start_time
    size_mb = output_path.stat().st_size / 1024 / 1024 if output_path.exists() else 0

    print(f"""
  ════════════════════════════════════════════════════════
  ✓ ASSEMBLY COMPLETE
  ════════════════════════════════════════════════════════
  File:     {output_path}
  Size:     {size_mb:.0f} MB
  Length:   {concat_dur:.1f}s ({concat_dur/60:.1f} min)
  Chapters: {len(chapter_videos)}/{len(CHAPTERS)}
  Time:     {elapsed:.1f}s
  Audio:    {'SFX + Narration + Music' if not skip_narration else 'SFX only'}
  ════════════════════════════════════════════════════════
    """)
    return True


def main():
    parser = argparse.ArgumentParser(description="Assemble the master video")
    parser.add_argument("--quick", "-q", action="store_true", help="Preview quality")
    parser.add_argument("--skip-narration", action="store_true", help="Skip voiceover")
    parser.add_argument("--scratch", action="store_true", help="Regenerate everything")
    args = parser.parse_args()

    print(r"""
   ╔══════════════════════════════════════════════════════════╗
   ║   MANIM EVOLUTION STORY — REIMAGINED                      ║
   ║   Final Assembly Pipeline                                ║
   ╚══════════════════════════════════════════════════════════╝
    """)

    success = assemble(quick=args.quick, skip_narration=args.skip_narration)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
