"""
Chapter Video Generator
=======================
CLI tool for generating individual chapter videos using xAI Grok Imagine.

Usage:
    python generate_chapter.py --chapter big_bang         # Generate with default prompt
    python generate_chapter.py --chapter 2                 # By number (1-13)
    python generate_chapter.py --chapter big_bang --prompt "Custom prompt..."
    python generate_chapter.py --chapter big_bang --output my_video.mp4
    python generate_chapter.py --chapter big_bang --size 854x480  # Quick preview
    python generate_chapter.py --all                      # Generate all 13 chapters
    python generate_chapter.py --list                     # List chapters
"""

import argparse
import sys
from pathlib import Path

from grok_video import GrokClient, PROMPTS, CHAPTER_NAMES, list_chapters, MEDIA_DIR

CHAPTER_NUMBERS = {
    1: "title",
    2: "big_bang",
    3: "stars",
    4: "solar_system",
    5: "origin_of_life",
    6: "great_oxidation",
    7: "eukaryotes",
    8: "cambrian",
    9: "sea_to_land",
    10: "rise_of_mammals",
    11: "primates",
    12: "human_evolution",
    13: "conclusion",
}


def resolve_chapter(chapter_arg):
    """Convert a chapter argument to a key. Accepts name or number."""
    if chapter_arg.isdigit():
        num = int(chapter_arg)
        if num in CHAPTER_NUMBERS:
            return CHAPTER_NUMBERS[num]
        else:
            valid = list(CHAPTER_NUMBERS.keys())
            raise ValueError(f"Chapter number must be {min(valid)}-{max(valid)}, got {num}")
    key = chapter_arg.lower().replace(" ", "_")
    if key in PROMPTS:
        return key
    raise ValueError(
        f"Unknown chapter '{chapter_arg}'. Use --list to see available chapters."
    )


def main():
    parser = argparse.ArgumentParser(description="Generate chapter videos with Grok Imagine")
    parser.add_argument("--chapter", "-c", type=str, help="Chapter name or number (1-13)")
    parser.add_argument("--prompt", "-p", type=str, default=None, help="Custom prompt (overrides default)")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output path for video")
    parser.add_argument("--size", "-s", type=str, default="1920x1080", help="Video size (e.g. 1920x1080, 854x480)")
    parser.add_argument("--duration", "-d", type=int, default=15, help="Video duration in seconds")
    parser.add_argument("--all", "-a", action="store_true", help="Generate all 13 chapters")
    parser.add_argument("--list", "-l", action="store_true", help="List available chapters")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated without calling API")
    args = parser.parse_args()

    if args.list:
        list_chapters()
        return

    client = GrokClient()

    if args.all:
        print("\n  Generating all 13 chapters...\n")
        for key in PROMPTS:
            output_path = MEDIA_DIR / f"{key}.mp4"
            if output_path.exists():
                print(f"  ⚠ {key}.mp4 already exists, skipping (delete first)")
                continue
            if args.dry_run:
                print(f"  [dry-run] Would generate '{key}' → {output_path}")
                continue
            try:
                client.generate_chapter(
                    key,
                    output_path=output_path,
                    size=args.size,
                    duration=args.duration,
                )
            except Exception as e:
                print(f"  ✗ Failed '{key}': {e}")
        print("\n  Done!")
        return

    if not args.chapter:
        parser.print_help()
        return

    chapter_key = resolve_chapter(args.chapter)
    output_path = Path(args.output) if args.output else MEDIA_DIR / f"{chapter_key}.mp4"

    if output_path.exists():
        print(f"  ⚠ {output_path} already exists. Delete first or use a different --output.")
        return

    print(f"\n  Chapter:  {CHAPTER_NAMES.get(chapter_key, chapter_key)}")
    print(f"  Size:     {args.size}")
    print(f"  Duration: {args.duration}s")

    if args.dry_run:
        print(f"  [dry-run] Would generate → {output_path}")
        return

    try:
        client.generate_chapter(
            chapter_key,
            prompt=args.prompt,
            output_path=output_path,
            size=args.size,
            duration=args.duration,
        )
    except Exception as e:
        print(f"  ✗ Generation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
