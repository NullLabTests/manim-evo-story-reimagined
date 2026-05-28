# Contributing

Thanks for your interest in improving this project! Contributions of all kinds are welcome.

## How to Contribute

### Prompts & AI Video Generation

The most impactful contribution is improving the Grok Imagine prompts. Each chapter's prompt lives in `video_project/grok_video.py` (`PROMPTS` dict). To contribute:

1. Generate a chapter with the current prompt
2. Tweak the prompt and regenerate
3. Compare results
4. Submit a PR with your improved prompt and example output

**Tips for prompt engineering:**
- Be specific about visual elements, lighting, and composition
- Use cinematic vocabulary (close-up, wide shot, macro lens)
- Include mood descriptors (awe-inspiring, dramatic, gentle)
- Note aspect ratio and framing for chapter transitions

### Manim Overlays

The Manim scripts in `scripts/` can be enhanced with:
- Better data visualizations (timelines, charts, trees)
- Chapter title cards and transitions
- Information graphics that overlay on AI footage

See the original Manim Evolution Story documentation for Manim API references.

### Audio

Enhancements to `video_project/generate_sounds.py`, `generate_music.py`, and `generate_voiceover.py` are valuable:
- New sound effects for existing chapters
- Better procedural music generation
- Improved voiceover timing and subtitle generation

### Documentation

Improvements to README, this file, prompt engineering guides, and tutorials are always appreciated.

## Development Setup

```bash
git clone https://github.com/NullLabTests/manim-evo-story-reimagined.git
cd manim-evo-story-reimagined
pip install manim numpy httpx Pillow edge-tts scipy
cp x_key.example x_key.txt
# Add your xAI API key to x_key.txt
```

## Pull Request Process

1. Create a feature branch from `main`
2. Make focused, well-described commits
3. Test your changes (generate a chapter, run the assembly, etc.)
4. Update documentation if needed
5. Open a PR with a clear description of what and why

## Code Style

- Python: Follow PEP 8, 120 character line limit
- Prompts: One line per chapter, descriptive and specific
- Commits: Use conventional commits (`feat:`, `fix:`, `docs:`, `chore:`)
- No secrets: Never commit API keys or tokens

## Code of Conduct

Be respectful, constructive, and inclusive. This is an educational open-source project — everyone is here to learn.
