"""
xAI Grok Imagine Video Generation Client
=========================================
Core module for generating videos using the xAI Grok Imagine API.

Provides:
  - GrokClient: API client with auth, generation, and polling
  - Prompt library with curated prompts for all 13 chapters
  - Utilities for downloading and organizing generated videos

Usage:
    from grok_video import GrokClient
    client = GrokClient()
    video_path = client.generate_chapter("big_bang")
"""

import json
import os
import time
from pathlib import Path

import httpx


BASE_URL = "https://api.x.ai/v1"
DEFAULT_KEY_PATH = Path(__file__).parent.parent / "x_key.txt"
MEDIA_DIR = Path(__file__).parent.parent / "media" / "scenes"


def load_api_key(path=None):
    """Load xAI API key from multiple supported locations.

    Priority:
    1. XAI_API_KEY environment variable
    2. X_KEY file (one-line, project root) - preferred documented method
    3. x_key.txt file (legacy location)
    """
    # 1. Environment variable (most secure for CI / production)
    env_key = os.environ.get("XAI_API_KEY")
    if env_key and env_key.strip():
        return env_key.strip()

    # 2. X_KEY (one-line file) - the documented user-friendly method
    x_key_path = Path(__file__).parent.parent / "X_KEY"
    if x_key_path.exists():
        key = x_key_path.read_text().strip()
        if key:
            return key

    # 3. Fallback to x_key.txt for compatibility
    path = Path(path or DEFAULT_KEY_PATH)
    if path.exists():
        key = path.read_text().strip()
        if key:
            return key

    raise FileNotFoundError(
        "No xAI API key found.\n"
        "Set XAI_API_KEY env var, or place your key (one line) in a file named X_KEY "
        "or x_key.txt in the project root.\n"
        "See x_key.example for the expected format."
    )


class GrokClient:
    """Client for xAI Grok Imagine video generation."""

    def __init__(self, api_key=None, base_url=BASE_URL):
        self.api_key = api_key or load_api_key()
        self.base_url = base_url
        self.client = httpx.Client(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=120.0,
        )

    def generate_video(self, prompt, size="1920x1080", duration=15, **kwargs):
        """Submit a video generation request and return the generation ID."""
        payload = {
            "model": "grok-video-latest",
            "prompt": prompt,
            "size": size,
            "duration": duration,
            **kwargs,
        }
        response = self.client.post("/video/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("id")

    def poll_generation(self, generation_id, poll_interval=5, timeout=300):
        """Poll until generation is complete. Returns the result data."""
        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed > timeout:
                raise TimeoutError(
                    f"Generation {generation_id} did not complete within {timeout}s"
                )

            response = self.client.get(f"/video/generations/{generation_id}")
            response.raise_for_status()
            data = response.json()

            status = data.get("status")
            if status == "completed":
                return data
            elif status == "failed":
                error = data.get("error", "Unknown error")
                raise RuntimeError(f"Generation failed: {error}")

            time.sleep(poll_interval)

    def download_video(self, generation_id, output_path=None):
        """Download the generated video file."""
        data = self.poll_generation(generation_id)

        video_url = data.get("video_url") or data.get("output", {}).get("video_url")
        if not video_url:
            raise ValueError(f"No video URL in response: {data}")

        if output_path is None:
            output_path = MEDIA_DIR / f"{generation_id}.mp4"

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        response = httpx.get(video_url, timeout=300)
        response.raise_for_status()

        output_path.write_bytes(response.content)
        return output_path

    def generate_chapter(self, chapter_key, prompt=None, output_path=None, **kwargs):
        """Generate a full chapter video: prompt, submit, poll, download."""
        if prompt is None:
            prompt = PROMPTS.get(chapter_key)
            if not prompt:
                raise ValueError(
                    f"No default prompt for '{chapter_key}'. "
                    f"Provide one or add it to PROMPTS."
                )

        if output_path is None:
            output_path = MEDIA_DIR / f"{chapter_key}.mp4"

        print(f"  Generating '{chapter_key}'...")
        gen_id = self.generate_video(prompt, **kwargs)
        print(f"  Generation ID: {gen_id}")
        result = self.download_video(gen_id, output_path)
        print(f"  Downloaded: {output_path}")
        return result


# ─── Prompt Library ─────────────────────────────────────────────────────
# Curated prompts for xAI Grok Imagine video generation.
# Each prompt is optimized for cinematic, educational output.

PROMPTS = {
    "title": (
        "A stunning view of the Milky Way galaxy slowly rotating in deep space, "
        "countless stars twinkling against pure black, cinematic wide shot, "
        "ultra-detailed, 4K resolution, awe-inspiring, smooth motion"
    ),
    "big_bang": (
        "A brilliant point of white light exploding outward into cosmic inflation, "
        "vibrant purple and blue energy waves expanding through dark space, "
        "cinematic lighting, ultra-detailed, slow motion, awe-inspiring, "
        "scientific visualization style"
    ),
    "stars": (
        "A vast stellar nursery with glowing pink and purple nebula clouds, "
        "newborn stars igniting within, tendrils of gas and dust, "
        "deep space background, cinematic composition, ultra-detailed, "
        "Hubble Space Telescope aesthetic"
    ),
    "solar_system": (
        "A protoplanetary disk of swirling dust and gas around a young Sun-like star, "
        "planetesimals forming, warm orange and gold tones, "
        "cinematic wide shot, ultra-detailed, 4K, artistic scientific visualization"
    ),
    "origin_of_life": (
        "Primordial ocean under a stormy sky with volcanic islands in the distance, "
        "lightning striking the water, chemical-rich atmosphere, warm amber and green tones, "
        "cinematic wide shot, dramatic lighting, ultra-detailed, 4K"
    ),
    "great_oxidation": (
        "Microscopic view of cyanobacteria releasing streams of oxygen bubbles into "
        "ancient seawater, rusty iron formations on the seafloor, "
        "bi-directional lighting, macro lens aesthetic, scientific illustration style"
    ),
    "eukaryotes": (
        "Microscopic view of a primitive cell engulfing a smaller cell, "
        "endosymbiosis event, bioluminescent glow inside the cell membrane, "
        "detailed cellular texture, scientific accuracy meets artistic beauty, "
        "macro lens, soft lighting"
    ),
    "cambrian": (
        "Ancient Cambrian seafloor teeming with bizarre early life forms, "
        "trilobites and anomalocaris swimming through clear prehistoric waters, "
        "sunlight filtering from above, vibrant coral and green tones, "
        "cinematic underwater shot, ultra-detailed, paleoart style"
    ),
    "sea_to_land": (
        "A Tiktaalik-like creature emerging from shallow water onto a muddy riverbank, "
        "lush Devonian vegetation in the background, warm sunset lighting, "
        "cinematic medium shot, ultra-detailed, paleontological reconstruction style"
    ),
    "rise_of_mammals": (
        "A massive asteroid impact in the distance, fiery debris cloud rising, "
        "small mammalian creatures scurrying through ferns in the foreground, "
        "dramatic orange and red sky, cinematic composition, ultra-detailed, 4K"
    ),
    "primates": (
        "A family of early primates moving through a dense Eocene forest canopy, "
        "dappled sunlight filtering through leaves, green and golden tones, "
        "cinematic tracking shot, ultra-detailed, National Geographic documentary style"
    ),
    "human_evolution": (
        "A progression of hominin figures silhouetted against a savanna sunrise, "
        "from Australopithecus to Homo sapiens, warm golden hour lighting, "
        "cinematic wide shot, ultra-detailed, 4K, evolutionary timeline aesthetic"
    ),
    "conclusion": (
        "A single human figure standing on a hill under a star-filled night sky, "
        "the Milky Way arcing overhead, warm firelight, contemplative mood, "
        "cinematic wide shot, ultra-detailed, 4K, profound and inspiring"
    ),
}


CHAPTER_NAMES = {
    "title": "From the Big Bang to You",
    "big_bang": "The Big Bang",
    "stars": "Star Formation & Galaxies",
    "solar_system": "The Solar System",
    "origin_of_life": "Origin of Life",
    "great_oxidation": "The Great Oxidation",
    "eukaryotes": "Eukaryotes & Endosymbiosis",
    "cambrian": "The Cambrian Explosion",
    "sea_to_land": "From Sea to Land",
    "rise_of_mammals": "Rise of the Mammals",
    "primates": "The Primate Lineage",
    "human_evolution": "Human Evolution",
    "conclusion": "Conclusion",
}


def list_chapters():
    """Print all available chapters with their descriptions."""
    print(f"\n  {'Chapter':<20} {'Title':<40}")
    print(f"  {'-'*20} {'-'*40}")
    for key, title in CHAPTER_NAMES.items():
        print(f"  {key:<20} {title:<40}")
    print()


def test_connection():
    """Test API connectivity."""
    client = GrokClient()
    try:
        response = client.client.get("/models")
        response.raise_for_status()
        models = response.json().get("data", [])
        print("  ✓ Connected to xAI API")
        for m in models:
            print(f"    - {m.get('id')}")
        return True
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return False


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_connection()
    elif len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_chapters()
    else:
        print("Usage: python grok_video.py --test | --list")
