"""
Post-Production Master
======================
Professional audio mixing, normalization, and final assembly using FFmpeg.
Handles: background music, voiceover, sound effects leveling, crossfades.

Usage:
    python post_production.py --help
    python post_production.py --video final_video.mp4 --music background.mp3
    python post_production.py --video final_video.mp4 --voiceover narration.mp3
    python post_production.py --all --music bg.mp3 --voiceover voice.mp3
"""

import subprocess, sys, json, os
from pathlib import Path

VIDEO_DIR = Path(__file__).parent


def run(cmd, desc=""):
    if desc:
        print(f"  → {desc}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ✗ ERROR: {result.stderr[-500:]}")
        return None
    return result


def get_duration(filepath):
    """Get media duration in seconds using ffprobe."""
    cmd = f'ffprobe -v error -show_entries format=duration -of json "{filepath}"'
    result = run(cmd, capture=True)
    if result:
        data = json.loads(result.stdout)
        return float(data["format"]["duration"])
    return 0


def analyze_loudness(filepath):
    """Get integrated loudness (LUFS) and true peak."""
    cmd = f'ffmpeg -i "{filepath}" -af loudnorm=I=-16:print_format=json -f null NUL 2>&1' if os.name == 'nt' else \
          f'ffmpeg -i "{filepath}" -af loudnorm=I=-16:print_format=json -f null - 2>&1'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # Parse JSON from the stderr output
    output = result.stderr or result.stdout
    try:
        # Find JSON block between { and }
        start = output.find("{")
        end = output.rfind("}") + 1
        if start >= 0 and end > start:
            data = json.loads(output[start:end])
            return data
    except (json.JSONDecodeError, ValueError):
        pass
    return {"input_i": "?", "input_tp": "?"}


def normalize_audio(input_file, output_file, loudness_target=-16, true_peak=-1.5):
    """Normalize audio to target loudness using EBU R128."""
    cmd = (
        f'ffmpeg -y -i "{input_file}" '
        f'-af loudnorm=I={loudness_target}:TP={true_peak}:LRA=11:print_format=summary '
        f'-c:v copy "{output_file}" 2>/dev/null'
    )
    result = run(cmd, desc=f"Normalizing audio to {loudness_target} LUFS")
    return result is not None


def mix_audio_tracks(
    video_path,
    output_path,
    music_path=None,
    voiceover_path=None,
    music_volume=0.08,
    voiceover_volume=1.0,
    fade_in=0.5,
    fade_out=2.0,
):
    """
    Professional 3-track mix: video audio + background music + voiceover.
    
    Audio layering:
      Track 1: Video sound effects (from Manim) — kept at original level
      Track 2: Background music — ducked under voiceover, faded
      Track 3: Voiceover narration — centered, slightly compressed
    """
    if not video_path:
        print("  ✗ No video specified")
        return False

    if not Path(video_path).exists():
        print(f"  ✗ Video not found: {video_path}")
        return False

    duration = get_duration(video_path)
    if duration == 0:
        print(f"  ✗ Could not determine video duration")
        return False

    print(f"\n  Audio Mix: {Path(video_path).name} ({duration:.1f}s)")
    print(f"    Music: {Path(music_path).name if music_path else 'None'}")
    print(f"    Voiceover: {Path(voiceover_path).name if voiceover_path else 'None'}")

    # Build the FFmpeg filter graph
    filter_parts = []

    # Input 0: Video (with its audio track = sound effects)
    inputs = [f'-i "{video_path}"']
    stream_idx = 0

    # Input 1: Music (optional)
    music_stream = None
    if music_path and Path(music_path).exists():
        inputs.append(f'-i "{music_path}"')
        music_stream = len(inputs) - 1
        # Apply volume, fade in/out
        filter_parts.append(
            f"[{music_stream}:a]"
            f"volume={music_volume},"
            f"afade=t=in:d={fade_in},"
            f"afade=t=out:st={duration - fade_out}:d={fade_out}"
            f"[music]"
        )

    # Input 2: Voiceover (optional)
    voice_stream = None
    if voiceover_path and Path(voiceover_path).exists():
        inputs.append(f'-i "{voiceover_path}"')
        voice_stream = len(inputs) - 1
        # Apply compression + volume
        filter_parts.append(
            f"[{voice_stream}:a]"
            f"volume={voiceover_volume},"
            f"compand=attacks=0.01:decays=0.05:points=-80/-80|-30/-15|-10/-3|0/0:gain=2:volume=1"
            f"[voice]"
        )

    # Mix all audio streams
    mix_inputs = ["[0:a]"]  # Original SFX audio
    if music_stream is not None:
        mix_inputs.append("[music]")
    if voice_stream is not None:
        mix_inputs.append("[voice]")

    mix_str = "".join(mix_inputs)
    num_inputs = len(mix_inputs)

    # Use amix for multi-track mixing
    filter_parts.append(
        f"{mix_str}amix=inputs={num_inputs}:duration=first:dropout_transition=2"
        f",loudnorm=I=-16:TP=-1.5:LRA=11"
        f"[a]"
    )

    filter_graph = ";".join(filter_parts)
    cmd_inputs = " ".join(inputs)
    
    cmd = (
        f'ffmpeg -y {cmd_inputs} '
        f'-filter_complex "{filter_graph}" '
        f'-map 0:v -map "[a]" '
        f'-c:v copy -c:a aac -b:a 192k '
        f'-shortest '
        f'"{output_path}" 2>/dev/null'
    )

    result = run(cmd, desc="Mixing audio tracks...")
    if result and result.returncode == 0:
        size_mb = Path(output_path).stat().st_size / 1024 / 1024
        print(f"  ✓ Master mixed: {output_path} ({size_mb:.0f} MB)")
        # Show audio stats
        print(f"  ✓ Audio: AAC 192kbps, normalized to -16 LUFS")
        return True
    return False


def add_video_fades(input_path, output_path, fade_in=0.5, fade_out=1.0):
    """Add video fade-in/fade-out."""
    duration = get_duration(input_path)
    if duration == 0:
        return False
    cmd = (
        f'ffmpeg -y -i "{input_path}" '
        f'-vf "fade=t=in:st=0:d={fade_in},fade=t=out:st={duration - fade_out}:d={fade_out}" '
        f'-af "afade=t=in:d={fade_in},afade=t=out:st={duration - fade_out}:d={fade_out}" '
        f'-c:v libx264 -crf 18 -preset slow '
        f'"{output_path}" 2>/dev/null'
    )
    result = run(cmd, desc="Adding video fade effects...")
    return result is not None


def create_title_card(text, output_path, duration=3.0, bg_color="#0a0a1a"):
    """Create a simple title card using FFmpeg."""
    # Use drawtext filter to create a title card
    cmd = (
        f'ffmpeg -y -f lavfi -i color=c={bg_color}:s=1920x1080:d={duration} '
        f'-vf "drawtext=text=\'{text}\':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2" '
        f'-c:v libx264 -crf 18 "{output_path}" 2>/dev/null'
    )
    result = run(cmd, desc=f"Creating title card: {text}")
    return result is not None


def print_report(video_path):
    """Print detailed audio/video info for quality check."""
    if not Path(video_path).exists():
        print(f"  ✗ File not found: {video_path}")
        return
    
    duration = get_duration(video_path)
    size_mb = Path(video_path).stat().st_size / 1024 / 1024
    
    print(f"\n  ════════════ QUALITY REPORT ════════════")
    print(f"  File:    {Path(video_path).name}")
    print(f"  Size:    {size_mb:.1f} MB")
    print(f"  Length:  {duration:.1f}s ({duration/60:.1f} min)")
    print(f"  Bitrate: {size_mb * 8 / duration * 1000:.0f} kbps (total)")
    
    # Get codec info
    cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,bit_rate -of json "{video_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        stream = data["streams"][0]
        print(f"  Video:   {stream['codec_name']} {stream['width']}x{stream['height']}")
        if stream.get('bit_rate'):
            print(f"  VBR:     {int(stream['bit_rate'])/1000:.0f} kbps")
    except:
        pass
    
    cmd = f'ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,bit_rate,sample_rate -of json "{video_path}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    try:
        data = json.loads(result.stdout)
        if data["streams"]:
            stream = data["streams"][0]
            print(f"  Audio:   {stream['codec_name']} {int(stream.get('sample_rate',0))/1000:.0f}kHz")
            if stream.get('bit_rate'):
                print(f"  ABR:     {int(stream['bit_rate'])/1000:.0f} kbps")
    except:
        pass
    
    print(f"  ════════════════════════════════════════")


def main():
    import argparse
    print(r"""
   ╔══════════════════════════════════════════════════════════╗
   ║   POST-PRODUCTION MASTER — Audio Mix & Final Assembly    ║
   ╚══════════════════════════════════════════════════════════╝
    """)

    parser = argparse.ArgumentParser(description="Post-production audio/video master")
    parser.add_argument("--video", "-v", type=str, help="Input video file")
    parser.add_argument("--music", "-m", type=str, help="Background music file")
    parser.add_argument("--voiceover", "-vo", type=str, help="Voiceover narration file")
    parser.add_argument("--output", "-o", type=str, default="final_master.mp4", help="Output file")
    parser.add_argument("--music-volume", type=float, default=0.08, help="Music volume (0-1)")
    parser.add_argument("--voice-volume", type=float, default=1.0, help="Voiceover volume")
    parser.add_argument("--fade-in", type=float, default=0.5, help="Fade in duration (s)")
    parser.add_argument("--fade-out", type=float, default=2.0, help="Fade out duration (s)")
    parser.add_argument("--report", "-r", type=str, nargs="?", const="final_master.mp4", help="Print quality report")
    parser.add_argument("--all", "-a", action="store_true", help="Full post-pro: mix + fades + report")
    parser.add_argument("--fades", action="store_true", help="Add video/audio fades only")
    parser.add_argument("--normalize", action="store_true", help="Normalize audio only")

    args = parser.parse_args()

    if args.report:
        print_report(args.report)
        return

    if args.all:
        # Step 1: Mix audio tracks
        output_mixed = str(VIDEO_DIR / "_mixed_temp.mp4")
        ok = mix_audio_tracks(
            video_path=args.video,
            output_path=output_mixed,
            music_path=args.music,
            voiceover_path=args.voiceover,
            music_volume=args.music_volume,
            voiceover_volume=args.voice_volume,
            fade_in=args.fade_in,
            fade_out=args.fade_out,
        )
        if not ok:
            print("  ✗ Audio mix failed")
            return

        # Step 2: Add fades
        ok = add_video_fades(output_mixed, args.output, args.fade_in, args.fade_out)
        Path(output_mixed).unlink(missing_ok=True)
        if ok:
            print_report(args.output)
        return

    if args.music or args.voiceover:
        mix_audio_tracks(
            video_path=args.video,
            output_path=args.output,
            music_path=args.music,
            voiceover_path=args.voiceover,
            music_volume=args.music_volume,
            voiceover_volume=args.voice_volume,
            fade_in=args.fade_in,
            fade_out=args.fade_out,
        )
        return

    if args.fades and args.video:
        add_video_fades(args.video, args.output or "faded_" + Path(args.video).name, args.fade_in, args.fade_out)
        return

    if args.normalize and args.video:
        normalize_audio(args.video, args.output or "normalized_" + Path(args.video).name)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
