"""
Shared color palette, constants, and helper functions used by all scripts.

Import with:
  from shared import COSMIC_BG, create_star_field, create_glow_circle, ...
"""

from manim import *
import numpy as np


# ─── Colour Palette ──────────────────────────────────────────────────────────
COSMIC_BG = ManimColor("#0a0a1a")
C_WARM_GOLD = ManimColor("#FFD700")
C_DEEP_BLUE = ManimColor("#1a237e")
C_LIFE_GREEN = ManimColor("#4CAF50")
C_OXYGEN_BLUE = ManimColor("#42A5F5")
C_FIRE_RED = ManimColor("#FF5722")
C_PRIMORDIAL = ManimColor("#FF8A65")
C_HUMAN_TONE = ManimColor("#FFCC80")
C_NEBULA_PINK = ManimColor("#E040FB")
C_NEBULA_PURPLE = ManimColor("#7C4DFF")
C_GALAXY_BLUE = ManimColor("#448AFF")


# ─── Helper Functions ────────────────────────────────────────────────────────

def make_timeline_label(scene, year_text, x_pos, label_text="", color=WHITE):
    """Place a year label on a horizontal timeline. Returns the label group."""
    dot = Dot(radius=0.06, color=color).move_to([x_pos, -3.2, 0])
    year = Text(year_text, font_size=14, color=color).next_to(dot, DOWN, buff=0.08)
    label = Text(label_text, font_size=10, color=color).next_to(year, DOWN, buff=0.04)
    return VGroup(dot, year, label)


def create_star_field(num=120, width=14, height=8):
    """Create a field of small dots with varying opacity for starry backgrounds."""
    stars = VGroup()
    for _ in range(num):
        x = np.random.uniform(-width / 2, width / 2)
        y = np.random.uniform(-height / 2, height / 2)
        r = np.random.uniform(0.008, 0.025)
        opacity = np.random.uniform(0.3, 1.0)
        star = Dot(radius=r, color=WHITE, stroke_opacity=0).set_opacity(opacity)
        star.move_to([x, y, 0])
        stars.add(star)
    return stars


def create_glow_circle(radius=1.0, color=BLUE, opacity=0.15):
    """Create a glowing circle with a soft halo."""
    glow = Circle(radius=radius, color=color, stroke_opacity=0)
    glow.set_fill(color=color, opacity=opacity)
    return glow
