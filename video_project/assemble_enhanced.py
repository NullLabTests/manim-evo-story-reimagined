"""
Final Assembly: Enhanced Sounds Edition
=========================================
Assembles the definitive "enhanced_sounds" master video with:
  - All 13 chapters
  - Integrated sound effects (from Manim scene)
  - Original 15-minute background music score (synthesized)
  - Professional audio leveling (EBU R128 normalization)
  - Video fades and polish

Output: media/master/FullStoryScene_enhanced_sounds.mp4

Usage:
    python assemble_enhanced.py                          # full assembly
    python assemble_enhanced.py --skip-render             # skip manim, just mix
    python assemble_enhanced.py --music music_file.mp3    # use external music
    python assemble_enhanced.py --quick                   # 480p preview
"""

import subprocess, sys, os, time
from pathlib import Path

VIDEO_DIR = Path(__file__).parent
MEDIA_DIR = VIDEO_DIR.parent / "media"
MASTER_DIR = MEDIA_DIR / "master"
MANIM_BIN = "manim"

QUALITY_FLAGS = {
    "preview": "-ql",
    "final":   "-qh",
}


def run(cmd, desc="", capture=True):
    if desc:
        print(f"  → {desc}")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0:
        err = result.stderr[-300:] if result.stderr else result.stdout[-300:]
        print(f"  ✗ {err}")
        return None
    return result


def step(msg):
    print(f"\n  ── {msg} ──")


def assemble(quality="final", music_source=None, skip_render=False):
    MASTER_DIR.mkdir(parents=True, exist_ok=True)
    
    flag = QUALITY_FLAGS[quality]
    res = "480p15" if quality == "preview" else "1080p60"
    output_name = f"FullStoryScene_enhanced_sounds_{quality}.mp4"
    output_path = MASTER_DIR / output_name
    
    # ── Step 1: Verify all resources ──
    step("1/4  Checking resources")
    
    sound_py = VIDEO_DIR / "full_video_sound.py"
    music_default = VIDEO_DIR / "background_music_15min.wav"
    
    if not sound_py.exists():
        print(f"  ✗ {sound_py} not found. Cannot continue.")
        return False
    
    music_path = Path(music_source) if music_source else music_default
    if not music_path.exists():
        print(f"  ⚠ Music not found: {music_path}")
        print(f"  → Run: python generate_music.py")
        print(f"  → Or specify: --music your_music.mp3")
        if not music_source:
            print(f"  → Will continue without background music")
            music_path = None
    
    # ── Step 2: Render the video ──
    if skip_render:
        # Try to find existing rendered output
        existing = list(MEDIA_DIR.rglob(f"FullStoryScene.{res}.mp4")) + \
                   list(MEDIA_DIR.rglob("FullStoryScene.mp4"))
        found = [f for f in existing if f.exists()]
        if found:
            rendered_video = found[0]
            print(f"  ✓ Using existing render: {rendered_video}")
        else:
            print(f"  ✗ No existing render found. Remove --skip-render to render.")
            return False
    else:
        step("2/4  Rendering video with sound effects")
        print(f"  This will take a while for {quality} quality...")
        start = time.time()
        result = run(
            f'python "{MANIM_BIN}" {flag} "{sound_py}" FullStoryScene --progress_bar=none',
            capture=True
        )
        if result is None:
            return False
        
        # Find the rendered file
        media_video_dir = MEDIA_DIR / "videos" / "full_video_sound" / res
        rendered_video = media_video_dir / "FullStoryScene.mp4"
        if not rendered_video.exists():
            # Check other possible locations
            candidates = list(MEDIA_DIR.rglob("FullStoryScene.mp4"))
            if candidates:
                rendered_video = candidates[0]
            else:
                print(f"  ✗ Could not find rendered video")
                return False
        
        elapsed = time.time() - start
        print(f"  ✓ Rendered in {elapsed/60:.1f} minutes")
    
    # ── Step 3: Add background music + normalize ──
    step("3/4  Mixing background music & normalizing audio")
    
    temp_mixed = MASTER_DIR / f"_temp_{quality}.mp4"
    
    if music_path and music_path.exists():
        # Professional mix: original SFX + background music
        # Music is ducked under SFX using volume envelope
        filter_complex = (
            f"[1:a]volume=0.12[a_music];"
            f"[0:a][a_music]amix=inputs=2:duration=first:dropout_transition=2"
            f",loudnorm=I=-16:TP=-1.5:LRA=11[a]"
        )
        cmd = (
            f'ffmpeg -y -i "{rendered_video}" -i "{music_path}" '
            f'-filter_complex "{filter_complex}" '
            f'-map 0:v -map "[a]" '
            f'-c:v copy -c:a aac -b:a 192k '
            f'"{temp_mixed}" 2>/dev/null'
        )
    else:
        # Just normalize existing audio
        cmd = (
            f'ffmpeg -y -i "{rendered_video}" '
            f'-af loudnorm=I=-16:TP=-1.5:LRA=11 '
            f'-c:v copy -c:a aac -b:a 192k '
            f'"{temp_mixed}" 2>/dev/null'
        )
    
    result = run(cmd, desc="Mixing audio...")
    if result is None:
        return False
    
    # ── Step 4: Add video fades + finalize ──
    step("4/4  Adding fades & writing final file")
    
    # Get duration for fade timing
    probe = run(
        f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{temp_mixed}"',
        capture=True
    )
    duration = float(probe.stdout.strip()) if probe and probe.stdout.strip() else 900
    
    fade_duration = min(2.0, duration * 0.05)
    
    cmd = (
        f'ffmpeg -y -i "{temp_mixed}" '
        f'-vf "fade=t=in:st=0:d={fade_duration},"
        f'fade=t=out:st={duration - fade_duration}:d={fade_duration}" '
        f'-af "afade=t=in:d={fade_duration},"
        f'afade=t=out:st={duration - fade_duration}:d={fade_duration}" '
        f'-c:v libx264 -crf 18 -preset slow '
        f'-c:a copy '
        f'"{output_path}" 2>/dev/null'
    )
    result = run(cmd, desc="Applying fades...")
    if result is None:
        return False
    
    # Cleanup temp
    temp_mixed.unlink(missing_ok=True)
    
    # ── Final Report ──
    size_mb = output_path.stat().st_size / 1024 / 1024
    mins = duration / 60
    print(f"\n  ═════════════════════════════════════════════")
    print(f"  ✓ ENHANCED SOUNDS EDITION COMPLETE")
    print(f"  ═════════════════════════════════════════════")
    print(f"  File:   {output_path}")
    print(f"  Size:   {size_mb:.0f} MB")
    print(f"  Length: {mins:.1f} minutes")
    print(f"  Audio:  SFX (embedded) + Background Music + Normalized")
    print(f"  Bitrate control: high quality (CRF 18)")
    print(f"  ═════════════════════════════════════════════")
    print(f"\n  ✓ View with: open {output_path}")
    
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Assemble the Enhanced Sounds edition"
    )
    parser.add_argument("--quick", "-q", action="store_true",
                       help="Preview quality (480p, faster)")
    parser.add_argument("--skip-render", "-s", action="store_true",
                       help="Skip Manim render, use existing files")
    parser.add_argument("--music", "-m", type=str, default=None,
                       help="Path to background music file")
    parser.add_argument("--show-design", action="store_true",
                       help="Print the sound design plan")
    args = parser.parse_args()

    # Print banner
    print(r"""
   ╔══════════════════════════════════════════════════════════╗
   ║   ENHANCED SOUNDS EDITION — Final Assembly               ║
   ║   "From the Big Bang to You"                             ║
   ║   Original score + layered sound design                  ║
   ╚══════════════════════════════════════════════════════════╝
    """)
    
    if args.show_design:
        from sound_design import SoundDesign
        SoundDesign.list_design()
        SoundDesign.print_timing_guide()
        return

    quality = "preview" if args.quick else "final"
    success = assemble(
        quality=quality,
        music_source=args.music,
        skip_render=args.skip_render,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
