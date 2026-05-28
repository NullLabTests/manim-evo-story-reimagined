# Audio Design Guidelines

Professional audio is one of the highest-leverage ways to elevate the final Grok Imagine video from "interesting AI experiment" to "high-quality educational film."

## Three-Layer Audio Strategy

We use three distinct, independently controllable layers:

| Layer | Tool | Purpose | Characteristics |
|-------|------|---------|-----------------|
| **Voiceover Narration** | `edge-tts` (or higher quality TTS) | Clear educational storytelling | Natural pacing, consistent voice, subtle emotional arc |
| **Sound Effects (SFX)** | `generate_sounds.py` (NumPy/SciPy synthesis) | Grounding & immersion | Chapter-specific, non-distracting, scientifically evocative |
| **Ambient Score** | `generate_music.py` | Emotional through-line | Evolving, minimal, 15-minute continuous bed |

## Design Principles

1. **Support the visuals, never compete**
   - The Grok footage is the star. Audio should enhance mood and clarity.

2. **Scientific but cinematic**
   - Sounds should feel plausible (e.g., low-frequency rumble for Big Bang, organic bubbling for early life) while serving dramatic purpose.

3. **Evolving Soundscape**
   - The audio should mirror the narrative arc:
     - Cold, vast, sparse in the cosmic chapters
     - Warmer, more organic and rhythmic in the biological chapters
     - Intimate and reflective in the human chapters

4. **Technical Quality Targets**
   - Final mix: EBU R128 loudness normalization
   - Clear voice at -18 to -22 LUFS integrated
   - Music/SFX bed at -28 to -32 LUFS
   - Proper use of fades, ducking, and spatial positioning where relevant

## Current Tooling

- `video_project/generate_voiceover.py` — Generates per-chapter narration + SRT subtitles
- `video_project/generate_sounds.py` — Synthesizes chapter-specific effects
- `video_project/generate_music.py` — Creates the long-form evolving ambient score
- `video_project/sound_design.py` + `remix_professional.py` — Timing and final mixing

## Future Enhancements (High Priority)

- More sophisticated procedural music with actual chord progressions and motif development
- Layered, multi-stem SFX with better variation per chapter
- Optional high-quality neural voice (when available via xAI or other)
- Full 5.1 / binaural options for premium release

## Workflow Recommendation

1. Lock picture (final video edit)
2. Spot the voiceover script
3. Generate and time the narration
4. Design and place SFX against picture
5. Compose / adapt the ambient score to picture
6. Final mix + loudness pass

---

*In an educational film about 13.8 billion years of evolution, sound is not decoration — it is part of the storytelling.*