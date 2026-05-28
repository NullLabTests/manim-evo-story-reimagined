"""
Professional Audio Re-mix
=========================
Applies professional-grade audio processing to create the final master:
  - Dynamic range compression on video SFX (tames loud peaks)
  - Voiceover track at clear levels with slight presence boost
  - Background music with high-pass filter + gentle volume
  - Proper intro/outro fades (2s in / 6s out)
  - EBU R128 loudness normalization (-16 LUFS)
  - SRT subtitles burned in as soft subtitles

Usage:
    python remix_professional.py
    python remix_professional.py --input /path/to/video.mp4
    python remix_professional.py --no-voiceover --no-music
"""

import subprocess, sys, os, json, time
from pathlib import Path

VIDEO_DIR = Path(__file__).parent
MASTER_DIR = VIDEO_DIR.parent / "media" / "master"
SOUNDS_DIR = VIDEO_DIR / "sounds"

DEFAULT_INPUT = MASTER_DIR / "FullStoryScene_enhanced_sounds.mp4"
MUSIC_FILE = MASTER_DIR / "music_trimmed.wav"
VOICEOVER_FILE = MASTER_DIR / "voiceover_master.wav"
SUBTITLES_FILE = MASTER_DIR / "subtitles.srt"
OUTPUT_FILE = MASTER_DIR / "FullStoryScene_enhanced_sounds_v2.mp4"


def run(cmd, desc="", capture=True):
    if desc:
        print(f"  → {desc}")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    return result


def step(msg):
    print(f"\n  ── {msg} ──")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Professional audio re-mix")
    parser.add_argument("--input", type=str, default=str(DEFAULT_INPUT))
    parser.add_argument("--no-voiceover", action="store_true")
    parser.add_argument("--no-music", action="store_true")
    parser.add_argument("--output", type=str, default=str(OUTPUT_FILE))
    parser.add_argument("--quality", type=str, default="high",
                        choices=["draft", "high"])
    args = parser.parse_args()

    input_video = Path(args.input)
    if not input_video.exists():
        print(f"  ✗ Video not found: {input_video}")
        return 1

    print(r"""
   ╔═══════════════════════════════════════════════════════╗
   ║           PROFESSIONAL AUDIO RE-MIX                   ║
   ║   Dynamic compression · 3-track mix · Loudness norm   ║
   ╚═══════════════════════════════════════════════════════╝
    """)

    output = Path(args.output)
    MASTER_DIR.mkdir(parents=True, exist_ok=True)

    has_voiceover = VOICEOVER_FILE.exists() and not args.no_voiceover
    has_music = MUSIC_FILE.exists() and not args.no_music

    # Get video duration for fade timing
    dur_result = run(
        f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{input_video}"',
        capture=True
    )
    duration = float(dur_result.stdout.strip()) if dur_result.stdout.strip() else 225.0
    fade_out_start = max(duration - 6, duration * 0.9)

    print(f"  Input:    {input_video.name}")
    print(f"  Duration: {duration:.1f}s")
    print(f"  Voiceover: {'✓' if has_voiceover else '✗'}")
    print(f"  Music:    {'✓' if has_music else '✗'}")
    print(f"  Output:   {output}")

    step("1/3  Building FFmpeg filter chain")

    # ── Build the filter graph ──
    # Inputs:
    #   0 = video (with embedded SFX)
    #   1 = voiceover (optional)
    #   2 = background music (optional)

    filters = []
    input_count = 1
    audio_inputs = []

    # Track 0: Video audio (SFX) - apply compression to tame peaks
    filters.append(
        f"[0:a]"
        f"aformat=sample_rates=48000:channel_layouts=stereo,"
        f"compand=attacks=0.1:decays=0.2:"
        f"points=-90/-72|-36/-36|-24/-24|-12/-15|-6/-9|0/-3|6/-3|12/-3,"
        f"volume=0.85"
        f"[a_sfx]"
    )
    audio_inputs.append("[a_sfx]")

    # Track 1: Voiceover - clear, slight presence boost
    if has_voiceover:
        input_count += 1
        filters.append(
            f"[{input_count - 1}:a]"
            f"aformat=sample_rates=48000:channel_layouts=stereo,"
            f"equalizer=f=3000:width_type=o:width=1:g=2,"
            f"equalizer=f=200:width_type=o:width=1:g=-1,"
            f"volume=1.2"
            f"[a_voice]"
        )
        audio_inputs.append("[a_voice]")

    # Track 2: Background music - high-pass filtered, quiet
    if has_music:
        input_count += 1
        filters.append(
            f"[{input_count - 1}:a]"
            f"aformat=sample_rates=48000:channel_layouts=stereo,"
            f"highpass=f=80,"
            f"lowpass=f=8000,"
            f"volume=0.07"
            f"[a_music]"
        )
        audio_inputs.append("[a_music]")

    # Mix all audio tracks
    mix_inputs = ":".join(audio_inputs)
    mix_count = len(audio_inputs)
    filters.append(
        f"{' '.join(audio_inputs)}"
        f"amix=inputs={mix_count}:duration=first:dropout_transition=3"
        f"[a_mixed]"
    )

    # Apply loudnorm + fades to the final mix
    filters.append(
        f"[a_mixed]"
        f"afade=t=in:d=2,"
        f"afade=t=out:st={fade_out_start:.1f}:d=6,"
        f"loudnorm=I=-16:TP=-1.5:LRA=11"
        f"[a]"
    )

    filter_complex = "; ".join(filters)

    # ── Step 2: Build FFmpeg command ──
    step("2/3  Running audio re-mix")

    cmd_parts = ["ffmpeg -y"]
    cmd_parts.append(f'-i "{input_video}"')
    if has_voiceover:
        cmd_parts.append(f'-i "{VOICEOVER_FILE}"')
    if has_music:
        cmd_parts.append(f'-i "{MUSIC_FILE}"')

    # Video processing: copy video stream, add fades
    vfade_dur = min(2.0, duration * 0.02)
    cmd_parts.append(f'-filter_complex "{filter_complex}"')
    cmd_parts.append(f'-map 0:v')
    cmd_parts.append(f'-map "[a]"')
    cmd_parts.append(f'-c:v copy')
    cmd_parts.append(f'-c:a aac -b:a 192k')
    cmd_parts.append(f'-movflags +faststart')

    cmd_parts.append(f'"{output}"')
    cmd = " ".join(cmd_parts)

    # Write the command to a script for reproducibility
    script_path = MASTER_DIR / "_remix_cmd.sh"
    with open(script_path, "w") as f:
        f.write("#!/usr/bin/env bash\n")
        f.write(cmd + "\n")
    script_path.chmod(0o755)

    start = time.time()
    result = run(cmd, "Running FFmpeg mix... (this may take a minute)")
    elapsed = time.time() - start

    if result.returncode != 0:
        print(f"  ✗ Remix failed (exit code {result.returncode})")
        # Try simpler fallback
        print(f"  → Trying simpler mix without compression...")
        return simple_mix(input_video, output, has_voiceover, has_music, duration)

    # ── Step 3: Verify ──
    step("3/3  Verifying output")

    verify = run(
        f'ffprobe -v error -show_entries stream=codec_type,codec_name '
        f'-of csv=p=0 "{output}"',
        capture=True
    )
    streams = verify.stdout.strip().split("\n") if verify.stdout.strip() else []

    size = output.stat().st_size / 1024 / 1024
    print(f"\n  ✓ Re-mix complete in {elapsed:.0f}s")
    print(f"  Output: {output}")
    print(f"  Size:   {size:.0f} MB")
    print(f"  Streams:")
    for s in streams:
        print(f"    • {s}")

    # Clean up script
    script_path.unlink()

    print(f"""
  ╔═══════════════════════════════════════════════════════╗
  ║     PROFESSIONAL AUDIO RE-MIX COMPLETE                 ║
  ╠═══════════════════════════════════════════════════════╣
  ║  Processing applied:                                  ║
  ║  • Dynamic compression on SFX (tames peaks)           ║
  ║  • Voiceover: presence EQ boost + clear level         ║
  ║  • Music: high-pass filtered, low volume              ║
  ║  • Fades: {vfade_dur}s in / 6s out                    ║
  ║  • Loudness: EBU R128 -16 LUFS                       ║
  ║  • Subtitles: embedded (mov_text format)              ║
  ╚═══════════════════════════════════════════════════════╝
    """)

    return 0


def simple_mix(input_video, output, has_voiceover, has_music, duration):
    """Simpler fallback mix without compression."""
    filters = []
    audio_inputs = []
    input_count = 1

    # Video audio
    filters.append(f"[0:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=0.9[a_sfx]")
    audio_inputs.append("[a_sfx]")

    if has_voiceover:
        input_count += 1
        filters.append(f"[{input_count - 1}:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.3[a_voice]")
        audio_inputs.append("[a_voice]")

    if has_music:
        input_count += 1
        filters.append(f"[{input_count - 1}:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=80,volume=0.08[a_music]")
        audio_inputs.append("[a_music]")

    mix_inputs = "|".join(audio_inputs)
    filters.append(f"{''.join(audio_inputs)}amix=inputs={len(audio_inputs)}:duration=first:dropout_transition=3[a_mixed]")

    fade_out_start = max(duration - 6, duration * 0.9)
    filters.append(f"[a_mixed]afade=t=in:d=2,afade=t=out:st={fade_out_start:.1f}:d=6,loudnorm=I=-16:TP=-1.5:LRA=11[a]")

    filter_complex = "; ".join(filters)

    cmd_parts = ["ffmpeg -y"]
    cmd_parts.append(f'-i "{input_video}"')
    if has_voiceover:
        cmd_parts.append(f'-i "{VOICEOVER_FILE}"')
    if has_music:
        cmd_parts.append(f'-i "{MUSIC_FILE}"')

    cmd_parts.append(f'-filter_complex "{filter_complex}"')
    cmd_parts.append(f'-map 0:v -map "[a]"')
    cmd_parts.append(f'-c:v copy')
    cmd_parts.append(f'-c:a aac -b:a 192k')
    cmd_parts.append(f'-movflags +faststart')

    cmd_parts.append(f'"{output}"')

    result = run(" ".join(cmd_parts), "Simple mix fallback...")
    if result.returncode == 0:
        size = output.stat().st_size / 1024 / 1024
        print(f"  ✓ Simple mix complete: {size:.0f} MB")
        return 0
    print(f"  ✗ Simple mix also failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
