# Agent Instructions for Manim Evolution Story — Reimagined

This file provides context and coordination instructions for all agents working on this project.

## Project Overview

We are reimagining the classic Manim Evolution Story — a 13-chapter animated journey through 13.8 billion years of cosmic and biological evolution — by replacing traditional Manim-rendered scenes with cinematic AI-generated video from xAI's Grok Imagine API.

## Repository

- **GitHub:** https://github.com/NullLabTests/manim-evo-story-reimagined
- **Remote origin:** https://github.com/NullLabTests/manim-evo-story-reimagined.git

## Available Agents

1. **Manager Agent** (me) — Coordinates work, maintains repo health, monitors processes
2. **Video Creator** — Generates Grok Imagine video chapters
3. **Audio Designer** — Generates procedural audio (voiceover, SFX, music)

## Important Files

| File | Purpose |
|------|---------|
| `x_key.txt` | xAI API key (DO NOT COMMIT - in .gitignore) |
| `x_key.example` | API key template |
| `video_project/` | All video/audio generation scripts |
| `scripts/` | Manim overlay scenes |
| `assets/` | README images, SVGs, previews |
| `media/` | Generated output (gitignored) |

## Key Commands

```bash
# Generate a chapter video
python video_project/generate_chapter.py --chapter N --output media/scenes/chapter_N.mp4

# Generate voiceover
python video_project/generate_voiceover.py

# Generate sound effects
python video_project/generate_sounds.py

# Generate music
python video_project/generate_music.py

# Full assembly
python video_project/assemble.py

# Full pipeline
python video_project/render_pipeline.py --full
```

## Coordination Rules

1. **Never commit x_key.txt or .env files**
2. **Commit frequently** with clear messages
3. **Push to main** when stable
4. **Log results** of generation runs so other agents know what's been done
5. **Respect .gitignore** — generated media stays local

## API Key

The xAI API key is in `x_key.txt` at the project root. It's gitignored for security.
