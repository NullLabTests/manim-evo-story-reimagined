"""
Render Pipeline
===============
One-command pipeline to render all scenes, with progress tracking,
multiple quality presets, and parallel scene rendering.

Usage:
    python render_pipeline.py --help
    python render_pipeline.py --quality low         # 480p15 quick preview
    python render_pipeline.py --quality high        # 1080p60 final render
    python render_pipeline.py --quality high --parallel  # all 13 scenes in parallel
    python render_pipeline.py --master --quality low     # render combined master
    python render_pipeline.py --master --sound           # render with sound
    python render_pipeline.py --concat                   # concat all individual scenes
    python render_pipeline.py --full                     # full pipeline: render + concat + music
"""

import subprocess, sys, os, time, json, threading, glob, shutil
from pathlib import Path
from datetime import timedelta

VIDEO_DIR = Path(__file__).parent
MEDIA_DIR = VIDEO_DIR / ".." / "media"
MANIM_BIN = shutil.which("manim") or "manim"

SCENES = [
    "TitleScene",
    "BigBangScene",
    "StarFormationScene",
    "SolarSystemScene",
    "OriginOfLifeScene",
    "GreatOxidationScene",
    "EukaryotesScene",
    "CambrianExplosionScene",
    "SeaToLandScene",
    "RiseOfMammalsScene",
    "PrimateLineageScene",
    "HumanEvolutionScene",
    "ConclusionScene",
]

SOUND_FILE = "full_video_sound.py"
SILENT_FILE = "full_video.py"
MODULAR_FILE = "create_longform_video.py"

QUALITY_PRESETS = {
    "low":    {"quality": "l", "resolution": "480p15",   "label": "Low (480p15)"},
    "medium": {"quality": "m", "resolution": "720p30",   "label": "Medium (720p30)"},
    "high":   {"quality": "h", "resolution": "1080p60",  "label": "High (1080p60)"},
    "4k":     {"quality": "k", "resolution": "2160p60",  "label": "4K (2160p60)"},
}


def print_banner():
    print(r"""
   ╔══════════════════════════════════════════════════════════╗
   ║   FROM THE BIG BANG TO YOU — Render Pipeline            ║
   ║   The Epic 13.8-Billion-Year Story of Evolution         ║
   ╚══════════════════════════════════════════════════════════╝
    """)


def run(cmd, desc="", capture=False):
    if desc:
        print(f"  → {desc}")
    result = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    if result.returncode != 0 and not capture:
        print(f"  ✗ ERROR: {result.stderr[-500:] if result.stderr else result.stdout[-500:]}")
    return result


class ProgressTracker:
    def __init__(self, total):
        self.total = total
        self.done = 0
        self.lock = threading.Lock()
        self.start_time = time.time()

    def tick(self, name=""):
        with self.lock:
            self.done += 1
            elapsed = time.time() - self.start_time
            pct = self.done / self.total * 100
            eta = timedelta(seconds=int(elapsed / self.done * (self.total - self.done))) if self.done > 0 else "?"
            print(f"  [{self.done}/{self.total}] {pct:.0f}% — {name or ''} — ETA: {eta}")


def render_modular_scene(scene_name, quality="high", progress=None):
    """Render a single modular scene."""
    q = QUALITY_PRESETS[quality]
    flag = q["quality"]
    source = VIDEO_DIR / MODULAR_FILE
    out_dir = MEDIA_DIR / "videos" / MODULAR_FILE.replace(".py", "") / q["resolution"]

    cmd = f'python "{MANIM_BIN}" -q{flag} "{source}" {scene_name} --progress_bar=none'
    result = run(cmd, capture=True)
    
    if result.returncode == 0:
        # Find the output file
        mp4s = list(out_dir.glob(f"{scene_name}.mp4"))
        if mp4s:
            if progress:
                progress.tick(scene_name)
            return str(mp4s[0])
    if progress:
        progress.tick(f"{scene_name} (FAILED)")
    return None


def render_modular_parallel(quality="high", max_workers=4):
    """Render all 13 scenes in parallel using thread pool."""
    print(f"\n  Rendering {len(SCENES)} scenes in parallel ({QUALITY_PRESETS[quality]['label']})...")
    results = {}
    threads = []
    progress = ProgressTracker(len(SCENES))

    def worker(name):
        result = render_modular_scene(name, quality, progress)
        results[name] = result

    for scene in SCENES:
        t = threading.Thread(target=worker, args=(scene,))
        threads.append(t)
        t.start()
        if len(threads) % max_workers == 0:
            for t in threads:
                t.join()
            threads = []

    for t in threads:
        t.join()

    success = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if not v)
    print(f"\n  ✓ {success} rendered, ✗ {failed} failed")
    return results


def render_master(quality="high", sound=False):
    """Render the combined master file."""
    q = QUALITY_PRESETS[quality]["quality"]
    source = SOUND_FILE if sound else SILENT_FILE
    source_path = VIDEO_DIR / source
    print(f"\n  Rendering master {'WITH' if sound else 'WITHOUT'} sound ({QUALITY_PRESETS[quality]['label']})")
    print(f"  This may take a while...")
    start = time.time()
    result = run(f'python "{MANIM_BIN}" -q{q} "{source_path}" FullStoryScene --progress_bar=none')
    elapsed = time.time() - start
    if result.returncode == 0:
        print(f"  ✓ Master rendered in {timedelta(seconds=int(elapsed))}")
        return True
    return False


def concat_modular(quality="high", output_name="final_video.mp4"):
    """Concatenate all individual scene videos using FFmpeg."""
    q = QUALITY_PRESETS[quality]["resolution"]
    out_dir = MEDIA_DIR / "videos" / MODULAR_FILE.replace(".py", "") / q
    output_path = VIDEO_DIR / output_name

    # Build concat file
    concat_file = VIDEO_DIR / "_concat_list.txt"
    with open(concat_file, "w") as f:
        for scene in SCENES:
            mp4 = out_dir / f"{scene}.mp4"
            if mp4.exists():
                f.write(f"file '{mp4.absolute()}'\n")

    if not concat_file.exists() or concat_file.stat().st_size == 0:
        print("  ✗ No rendered videos found to concatenate")
        return False

    print(f"\n  Concatenating {len(list(open(concat_file)))} videos...")
    cmd = f'ffmpeg -y -f concat -safe 0 -i "{concat_file}" -c copy "{output_path}" 2>/dev/null'
    result = run(cmd, capture=True)
    if result.returncode == 0:
        size = output_path.stat().st_size / 1024 / 1024
        print(f"  ✓ Concatenated: {output_name} ({size:.0f} MB)")
        concat_file.unlink()
        return True
    print(f"  ✗ Concatenation failed")
    return False


def add_music(video_path, music_path, output_path, music_volume=0.12):
    """Mix background music into the rendered video."""
    if not Path(video_path).exists():
        print(f"  ✗ Video not found: {video_path}")
        return False
    if not Path(music_path).exists():
        print(f"  ✗ Music not found: {music_path}")
        return False

    print(f"\n  Mixing background music (volume={music_volume})...")
    cmd = (
        f'ffmpeg -y -i "{video_path}" -i "{music_path}" '
        f'-filter_complex "[1:a]volume={music_volume}[a1];'
        f'[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2" '
        f'-c:v copy "{output_path}" 2>/dev/null'
    )
    result = run(cmd, capture=True)
    if result.returncode == 0:
        print(f"  ✓ Music mixed: {output_path}")
        return True
    return False


def extract_audio(video_path, output_path):
    """Extract audio track from a rendered video (for voiceover reference)."""
    if not Path(video_path).exists():
        print(f"  ✗ Video not found: {video_path}")
        return False
    result = run(f'ffmpeg -y -i "{video_path}" -q:a 0 -map a "{output_path}" 2>/dev/null', capture=True)
    if result.returncode == 0:
        print(f"  ✓ Audio extracted: {output_path}")
        return True
    return False


def print_timing_guide():
    """Print approximate timing for each chapter (for voiceover planning)."""
    print("""
   ┌──────────────────────────────────────────────────────────────────────┐
   │                     VOICEOVER TIMING GUIDE                          │
   ├──────────────────────────────────────────────────────────────────────┤
   │ Ch.  Title                  Est. Duration  Narration Cue            │
   ├──────────────────────────────────────────────────────────────────────┤
   │  1   Title / Opening            ~8s        After subtitle fades in  │
   │  2   Big Bang                  ~12s        After flash fades        │
   │  3   Stars & Galaxies          ~15s        After spiral forms       │
   │  4   Solar System              ~12s        After Earth highlights   │
   │  5   Origin of Life            ~15s        After molecules combine  │
   │  6   Great Oxidation           ~14s        After O2 text appears    │
   │  7   Eukaryotes                ~12s        After nucleus forms      │
   │  8   Cambrian Explosion        ~14s        After creatures appear   │
   │  9   Sea to Land               ~16s        After tetrapod forms     │
   │ 10   Rise of Mammals           ~12s        After mammals emerge     │
   │ 11   Primate Lineage           ~10s        After tree grows         │
   │ 12   Human Evolution           ~14s        After timeline appears   │
   │ 13   Conclusion                ~16s        After timeline recap     │
   └──────────────────────────────────────────────────────────────────────┘
    """)


def main():
    import argparse
    print_banner()

    parser = argparse.ArgumentParser(
        description="Full render pipeline for Big Bang to You video"
    )
    parser.add_argument("--quality", "-q", default="low",
                       choices=list(QUALITY_PRESETS.keys()),
                       help="Render quality preset (default: low)")
    parser.add_argument("--parallel", "-p", action="store_true",
                       help="Render modular scenes in parallel")
    parser.add_argument("--master", "-m", action="store_true",
                       help="Render the combined master scene")
    parser.add_argument("--sound", "-s", action="store_true",
                       help="Render with sound effects")
    parser.add_argument("--concat", "-c", action="store_true",
                       help="Concatenate all rendered modular scenes")
    parser.add_argument("--music", "-M", type=str, nargs="?",
                       const="background_music.mp3",
                       help="Path to background music file to mix in")
    parser.add_argument("--full", "-f", action="store_true",
                       help="Run full pipeline: render all + concat + music")
    parser.add_argument("--timing", "-t", action="store_true",
                       help="Show voiceover timing guide")
    parser.add_argument("--extract-audio", "-ea", type=str, nargs="?",
                       const="voiceover_audio.mp3",
                       help="Extract audio from rendered master")
    parser.add_argument("--all-scenes", action="store_true",
                       help="Render all 13 modular scenes sequentially")
    args = parser.parse_args()

    if args.timing:
        print_timing_guide()
        return

    # Full pipeline
    if args.full:
        args.parallel = True
        args.concat = True
        if args.music:
            pass  # music handling below

    # Render modular scenes
    if args.all_scenes or args.parallel or args.full:
        results = render_modular_parallel(
            quality=args.quality,
            max_workers=4 if args.parallel else 1,
        )
        if args.parallel or args.full:
            pass  # already done above

    # Render master scene
    if args.master:
        render_master(quality=args.quality, sound=args.sound)

    # Concatenate
    if args.concat:
        master_video = concat_modular(quality=args.quality)

    # Extract audio (for voiceover recording)
    if args.extract_audio:
        # Find the master video
        q = QUALITY_PRESETS[args.quality]["resolution"]
        master_path = VIDEO_DIR / ".." / "media" / "videos" / SOUND_FILE.replace(".py", "") / q / "FullStoryScene.mp4"
        if master_path.exists():
            extract_audio(master_path, VIDEO_DIR / args.extract_audio)
        else:
            print(f"  ✗ No master video found at {master_path}")

    # Mix music
    if args.music:
        music_path = Path(args.music)
        if not music_path.is_absolute():
            music_path = VIDEO_DIR / args.music
        # Find the rendered master or concated video
        candidates = [
            VIDEO_DIR / "final_video.mp4",
            VIDEO_DIR / ".." / "media" / "videos" / SOUND_FILE.replace(".py", "") / QUALITY_PRESETS[args.quality]["resolution"] / "FullStoryScene.mp4",
            VIDEO_DIR / ".." / "media" / "videos" / SILENT_FILE.replace(".py", "") / QUALITY_PRESETS[args.quality]["resolution"] / "FullStoryScene.mp4",
        ]
        video_source = None
        for c in candidates:
            if c.exists():
                video_source = c
                break
        if video_source:
            output = VIDEO_DIR / "final_with_music.mp4"
            add_music(video_source, music_path, output)

    if not any([args.all_scenes, args.parallel, args.master, args.concat, args.music, args.extract_audio, args.timing, args.full]):
        parser.print_help()


if __name__ == "__main__":
    main()
