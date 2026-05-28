# Prompt Engineering Philosophy

High-quality Grok Imagine video output depends heavily on prompt craft.

## Core Principles

1. **Cinematic Language First**
   - Always include shot type, lens feel, lighting, and motion direction
   - Examples: "slow push-in macro lens", "wide establishing shot with gentle crane up", "intimate eye-level tracking shot"

2. **Scientific Accuracy + Artistic Beauty**
   - The goal is educational impact, not pure photorealism or pure abstraction
   - Ground the visual in real science while allowing the model creative freedom for emotional resonance

3. **Temporal & Stylistic Consistency Across Chapters**
   - Maintain a coherent visual language from the Big Bang through human evolution
   - Color temperature arc: cold cosmic → warm primordial → rich biological → golden human era

4. **Specificity Over Vagueness**
   - Bad: "beautiful space scene"
   - Good: "A brilliant point of white light exploding outward into cosmic inflation, vibrant purple and blue energy waves expanding through dark space, cinematic volumetric lighting, ultra-detailed, 4K, slow motion, awe-inspiring, shot on 35mm anamorphic"

## Recommended Prompt Structure

`[SUBJECT], [VISUAL STYLE / CINEMATIC TECHNIQUE], [LIGHTING & COLOR], [COMPOSITION & MOTION], [MOOD / ERA], [TECHNICAL QUALITY]`

## Iteration Process

- Generate a clip
- Note what worked and what failed (coherence, lighting, subject clarity, pacing)
- Adjust only one major variable per iteration
- Keep a prompt journal per chapter

## Current Best Practices (May 2026)

- Favor 8–12 second clips during early exploration (faster iteration)
- Use consistent aspect ratio (16:9 or 9:16 depending on target)
- When possible, include era/period descriptors ("Cambrian sea floor, 540 million years ago")
- For microscopic or cosmic scales, explicitly call out the visual scale ("macro lens on primordial cell" or "vast cosmic scale, single point of light in infinite darkness")

The prompts currently living in `video_project/grok_video.py` represent the accumulated best practices from multiple generations.

---

*Great prompts turn a generative model into a reliable cinematic collaborator.*