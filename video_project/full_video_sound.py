"""
From the Big Bang to You: The Epic 13.8-Billion-Year Story of Evolution
=========================================================================
MASTER FILE — All 13 chapters in one continuous Scene.

Render the full video:
  manim -pqh full_video.py FullStoryScene

Render with section markers (FFmpeg seeks easily):
  manim -pqh --save_sections full_video.py FullStoryScene

Render low-quality quick preview:
  manim -pql full_video.py FullStoryScene

Extract audio for voiceover:
  ffmpeg -i FullStoryScene.mp4 -q:a 0 -map a audio.mp3

Add voiceover back:
  ffmpeg -i FullStoryScene.mp4 -i audio.mp3 -c:v copy -c:a aac final.mp4
"""

from manim import *
import numpy as np
from sound_design import add_chapter_sounds, add_between_chapter_sound

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
    dot = Dot(radius=0.06, color=color).move_to([x_pos, -3.2, 0])
    year = Text(year_text, font_size=14, color=color).next_to(dot, DOWN, buff=0.08)
    label = Text(label_text, font_size=10, color=color).next_to(year, DOWN, buff=0.04)
    return VGroup(dot, year, label)


def create_star_field(num=120, width=14, height=8):
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
    glow = Circle(radius=radius, color=color, stroke_opacity=0)
    glow.set_fill(color=color, opacity=opacity)
    return glow


# ═══════════════════════════════════════════════════════════════════════════════
# MASTER SCENE — All 13 chapters in sequence
# ═══════════════════════════════════════════════════════════════════════════════

class FullStoryScene(Scene):
    def construct(self):
        self.camera.background_color = COSMIC_BG
        self.chapter_01_title()
        self.chapter_02_big_bang()
        self.chapter_03_stars_and_galaxies()
        self.chapter_04_solar_system()
        self.chapter_05_origin_of_life()
        self.chapter_06_great_oxidation()
        self.chapter_07_eukaryotes()
        self.chapter_08_cambrian_explosion()
        self.chapter_09_sea_to_land()
        self.chapter_10_rise_of_mammals()
        self.chapter_11_primate_lineage()
        self.chapter_12_human_evolution()
        self.chapter_13_conclusion()

    # ─── CHAPTER 1: Title ─────────────────────────────────────────────────

    def chapter_01_title(self):
        self.next_section("Title", skip_animations=False)
        add_chapter_sounds(self, "title")

        stars = create_star_field(200)
        for star in stars:
            star.set_opacity(np.random.uniform(0.2, 0.5))
        self.add(stars)
        self.play(*[FadeIn(star, scale=0.5) for star in stars[:30]], run_time=0.8)

        subtitle = Text(
            "THE EPIC 13.8-BILLION-YEAR STORY OF EVOLUTION",
            font_size=28, color=GREY_B,
        )
        subtitle.next_to(ORIGIN, DOWN, buff=0.8)

        title = Text(
            "From the Big Bang to You",
            font_size=54, color=C_WARM_GOLD, weight=BOLD,
        )
        title.move_to(ORIGIN)

        self.play(
            *[FadeIn(star, scale=0.5) for star in stars[:30]],
            run_time=0.5,
        )
        self.wait(0.3)
        self.play(Write(title, run_time=2.5))
        self.wait(0.5)
        self.play(FadeIn(subtitle, shift=UP * 0.3, run_time=1.5))
        self.wait(2.0)

        underline = Line(
            title.get_left() + DOWN * 0.3,
            title.get_right() + DOWN * 0.3,
            color=C_WARM_GOLD,
        )
        self.play(Create(underline), run_time=0.8)
        self.wait(1.5)

        for _ in range(2):
            self.play(stars.animate.set_opacity(0.6), run_time=1.5)
            self.play(stars.animate.set_opacity(1), run_time=1.5)

        self.play(
            FadeOut(title, shift=UP * 0.5),
            FadeOut(subtitle, shift=DOWN * 0.5),
            FadeOut(underline),
            *[FadeOut(s) for s in stars],
            run_time=1.5,
        )
        self.wait(0.3)

    # ─── CHAPTER 2: Big Bang ──────────────────────────────────────────────

    def chapter_02_big_bang(self):
        self.next_section("Big Bang & Cosmic Inflation", skip_animations=False)
        add_chapter_sounds(self, "big_bang")
        self.camera.background_color = "#000000"

        label = Text("The Big Bang", font_size=44, color=BLUE, weight=BOLD)
        label.to_edge(UP, buff=0.5)
        self.play(Write(label), run_time=1)
        self.wait(0.3)

        year_label = Text("13.8 billion years ago", font_size=22, color=GREY_B)
        year_label.next_to(label, DOWN, buff=0.3)
        self.play(FadeIn(year_label, shift=UP * 0.2), run_time=0.8)

        singularity = Dot(radius=0.15, color=WHITE)
        self.play(FadeIn(singularity, scale=0.1), run_time=1.0)

        flash = create_glow_circle(0.5, color=WHITE, opacity=0.8)
        flash.move_to(singularity.get_center())
        self.play(
            flash.animate.scale(30).set_opacity(0),
            run_time=1.5, rate_func=exponential_decay,
        )
        self.wait(0.2)

        grid = NumberPlane(
            x_range=[-20, 20, 1], y_range=[-12, 12, 1],
            background_line_style={
                "stroke_color": BLUE_D, "stroke_width": 0.5, "stroke_opacity": 0.3,
            },
            axis_config={"stroke_opacity": 0},
        )
        grid.scale(0.01)
        self.add(grid)
        self.play(
            grid.animate.scale(100),
            run_time=3.0, rate_func=rate_functions.ease_out_cubic,
        )

        particles = VGroup()
        for _ in range(80):
            angle = np.random.uniform(0, 2 * np.pi)
            dist = np.random.uniform(0.5, 6)
            p = Dot(
                radius=np.random.uniform(0.008, 0.025),
                color=interpolate_color(BLUE, PURPLE, np.random.random()),
            )
            p.move_to([np.cos(angle) * dist, np.sin(angle) * dist, 0])
            p.set_opacity(0)
            p.start_pos = p.get_center().copy()
            particles.add(p)

        self.play(
            *[p.animate(run_time=np.random.uniform(0.8, 2.0)).set_opacity(
                np.random.uniform(0.3, 1.0)) for p in particles],
            run_time=2.0,
        )
        self.wait(0.5)
        self.add(particles)
        self.play(FadeOut(particles, run_time=2.0))

        forces = [
            Text("Gravity", font_size=24, color=GOLD),
            Text("Strong Nuclear", font_size=24, color=RED),
            Text("Weak Nuclear", font_size=24, color=ORANGE),
            Text("Electromagnetism", font_size=24, color=BLUE),
        ]
        force_group = VGroup(*forces).arrange(RIGHT, buff=0.6)
        force_group.next_to(grid, DOWN, buff=0.8)

        for f in forces:
            self.play(FadeIn(f, scale=0.5, shift=UP * 0.3), run_time=0.6)
            self.wait(0.15)

        self.wait(1.0)
        self.play(
            FadeOut(force_group, shift=DOWN * 0.3),
            FadeOut(grid), FadeOut(label), FadeOut(year_label),
            run_time=1.5,
        )
        self.wait(0.3)

    # ─── CHAPTER 3: Stars & Galaxies ──────────────────────────────────────

    def chapter_03_stars_and_galaxies(self):
        self.next_section("Stars & Galaxies", skip_animations=False)
        add_chapter_sounds(self, "stars")
        self.camera.background_color = COSMIC_BG

        title = Text("Stars & Galaxies", font_size=40, color=C_GALAXY_BLUE, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        year_label = Text("First stars ~13.4 billion years ago", font_size=20, color=GREY_B)
        year_label.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(year_label, shift=UP * 0.2), run_time=0.6)
        self.wait(0.3)

        nebula_colors = [C_NEBULA_PINK, C_NEBULA_PURPLE, BLUE_D, C_PRIMORDIAL]
        nebulae = VGroup()
        for color in nebula_colors:
            n = Circle(
                radius=np.random.uniform(1.5, 3.0), color=color,
                stroke_opacity=0, fill_opacity=0.15,
            )
            n.move_to([np.random.uniform(-5, 5), np.random.uniform(-2, 2), 0])
            nebulae.add(n)
        self.play(*[GrowFromCenter(n, run_time=np.random.uniform(1, 2)) for n in nebulae], run_time=2.0)
        self.wait(0.5)

        stars_group = VGroup()
        for _ in range(30):
            s = Dot(
                radius=np.random.uniform(0.015, 0.04),
                color=interpolate_color(BLUE, C_WARM_GOLD, np.random.random()),
            )
            s.move_to([np.random.uniform(-6, 6), np.random.uniform(-3, 3), 0])
            s.set_opacity(0)
            stars_group.add(s)
        self.play(
            *[s.animate(run_time=np.random.uniform(0.3, 1.5)).set_opacity(np.random.uniform(0.5, 1.0))
              for s in stars_group],
            run_time=2.5,
        )
        self.wait(0.8)

        spiral_center = Dot(radius=0.08, color=WHITE).move_to([-2.5, 1.5, 0])
        spiral_group = VGroup(spiral_center)
        for i in range(50):
            angle = i * 0.5
            radius = 0.2 + i * 0.04
            x = -2.5 + radius * np.cos(angle)
            y = 1.5 + radius * np.sin(angle)
            d = Dot(
                radius=np.random.uniform(0.01, 0.025),
                color=interpolate_color(BLUE, C_WARM_GOLD, i / 50),
            )
            d.move_to([x, y, 0])
            d.set_opacity(0)
            spiral_group.add(d)
        self.play(
            *[d.animate(run_time=0.1 + i * 0.04).set_opacity(0.8)
              for i, d in enumerate(spiral_group[1:])],
            run_time=3.0,
        )
        spiral2 = spiral_group.copy()
        spiral2.move_to([3, -1.5, 0])
        self.play(
            *[d.animate(run_time=0.1 + i * 0.04).set_opacity(0.8)
              for i, d in enumerate(spiral2[1:])],
            run_time=2.5,
        )
        self.wait(0.5)

        elements_text = Text(
            "First elements: H, He  →  then stars forge C, O, Fe, Au...",
            font_size=24, color=GREY_B,
            t2c={"H, He": BLUE, "C, O, Fe, Au": C_WARM_GOLD},
        )
        elements_text.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(elements_text, shift=UP * 0.3), run_time=1.2)
        self.wait(2.0)

        self.play(FadeOut(VGroup(title, year_label, nebulae, stars_group, spiral_group, spiral2, elements_text)), run_time=1.5)
        self.wait(0.3)

    # ─── CHAPTER 4: Solar System ──────────────────────────────────────────

    def chapter_04_solar_system(self):
        self.next_section("Solar System", skip_animations=False)
        add_chapter_sounds(self, "solar_system")
        self.camera.background_color = COSMIC_BG

        title = Text("Our Solar System", font_size=40, color=C_WARM_GOLD, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        year_label = Text("~4.6 billion years ago", font_size=20, color=GREY_B)
        year_label.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(year_label, shift=UP * 0.2), run_time=0.6)
        self.wait(0.3)

        sun = Circle(radius=0.7, color=YELLOW, fill_opacity=0.9)
        sun.set_fill(YELLOW, opacity=0.9)
        sun_glow = create_glow_circle(1.0, YELLOW, opacity=0.2)
        sun_glow.move_to(sun.get_center())
        self.play(GrowFromCenter(sun), run_time=1.0)
        self.add(sun_glow)
        self.wait(0.3)

        orbit_data = [
            (0.35, 1.2, BLUE_D, "Mercury"), (0.45, 1.7, GREY, "Venus"),
            (0.5, 2.3, BLUE, "Earth"), (0.4, 3.0, RED, "Mars"),
            (0.6, 4.2, ORANGE, "Jupiter"), (0.55, 5.0, GOLD, "Saturn"),
            (0.5, 5.8, BLUE_C, "Uranus"), (0.48, 6.5, PURPLE_D, "Neptune"),
        ]
        planets = VGroup()
        orbits = VGroup()
        for radius, orbit_radius, color, name in orbit_data:
            orbit = Circle(radius=orbit_radius, color=GREY_D, stroke_width=0.5)
            orbit.move_to(sun.get_center())
            orbits.add(orbit)
            planet = Circle(radius=radius, color=color, fill_opacity=0.8)
            planet.move_to(sun.get_center() + [orbit_radius, 0, 0])
            planets.add(planet)
        self.play(*[Create(o, run_time=0.3) for o in orbits], run_time=1.5)
        self.play(*[GrowFromCenter(p, run_time=0.4) for p in planets], run_time=2.0)
        self.wait(0.5)

        self.play(*[
            UpdateFromAlphaFunc(
                planet,
                lambda m, a, idx=i: m.move_to(
                    sun.get_center() + [
                        orbit_data[idx][1] * np.cos(a * 2 * np.pi * np.random.uniform(0.3, 0.8)),
                        orbit_data[idx][1] * np.sin(a * 2 * np.pi * np.random.uniform(0.3, 0.8)),
                        0,
                    ]
                ),
            )
            for i, (_, planet) in enumerate(zip(orbit_data, planets))
        ], run_time=5.0)
        self.wait(0.5)

        earth = planets[2]
        earth_highlight = create_glow_circle(0.8, BLUE, opacity=0.3)
        earth_highlight.move_to(earth.get_center())
        earth_label = Text("Earth", font_size=20, color=BLUE)
        earth_label.next_to(earth, UP, buff=0.3)
        self.play(FadeIn(earth_highlight), Write(earth_label), run_time=1.0)

        earth_info = Text("Early Earth: molten, bombarded by asteroids", font_size=22, color=GREY_B)
        earth_info.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(earth_info, shift=UP * 0.3), run_time=1.0)
        self.wait(1.5)

        self.play(FadeOut(VGroup(title, year_label, sun, sun_glow, orbits, planets, earth_highlight, earth_label, earth_info)), run_time=1.5)
        self.wait(0.3)

    # ─── CHAPTER 5: Origin of Life ────────────────────────────────────────

    def chapter_05_origin_of_life(self):
        self.next_section("Origin of Life", skip_animations=False)
        add_chapter_sounds(self, "origin_of_life")
        self.camera.background_color = "#0D1117"

        title = Text("Origin of Life", font_size=40, color=C_LIFE_GREEN, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        year_label = Text("~3.8 billion years ago", font_size=20, color=GREY_B)
        year_label.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(year_label, shift=UP * 0.2), run_time=0.6)

        ocean = Rectangle(width=14, height=2.5, color=C_DEEP_BLUE, fill_opacity=0.6)
        ocean.set_fill(C_DEEP_BLUE, opacity=0.6)
        ocean.to_edge(DOWN, buff=0)
        self.play(FadeIn(ocean, shift=UP * 0.5), run_time=1.0)

        molecules_text = [
            ("H₂O", BLUE_D), ("CH₄", GREY_B), ("NH₃", PURPLE),
            ("CO₂", GREY), ("HCN", RED), ("H₂", BLUE_D),
        ]
        molecules = VGroup()
        for formula, color in molecules_text:
            t = Text(formula, font_size=18, color=color)
            t.move_to([np.random.uniform(-5, 5), np.random.uniform(-2.5, 0.5), 0])
            t.set_opacity(0)
            molecules.add(t)
        self.play(*[FadeIn(m, scale=0.3, run_time=np.random.uniform(0.5, 1.2)) for m in molecules], run_time=2.0)
        self.wait(0.5)

        center_point = np.array([0, -1, 0])
        self.play(*[
            m.animate.move_to(center_point + np.array([np.random.uniform(-0.3, 0.3), np.random.uniform(-0.3, 0.3), 0]))
            for m in molecules
        ], run_time=2.0)
        self.wait(0.3)

        flash = create_glow_circle(0.8, C_LIFE_GREEN, opacity=0.5)
        flash.move_to(center_point)
        self.play(flash.animate.scale(3).set_opacity(0), run_time=1.0)
        self.wait(0.3)

        membrane = Circle(radius=0.5, color=C_LIFE_GREEN, stroke_width=3)
        membrane.move_to(center_point)
        membrane.set_fill(C_LIFE_GREEN, opacity=0.1)
        inner = Circle(radius=0.4, color=C_LIFE_GREEN, fill_opacity=0.05)
        inner.set_fill(C_LIFE_GREEN, opacity=0.05)
        inner.move_to(center_point)
        self.play(DrawBorderThenFill(membrane), GrowFromCenter(inner), run_time=1.5)

        luca_label = Text("LUCA", font_size=22, color=C_LIFE_GREEN, weight=BOLD)
        luca_label.next_to(membrane, RIGHT, buff=0.5)
        luca_sub = Text("(Last Universal Common Ancestor)", font_size=14, color=GREY_B)
        luca_sub.next_to(luca_label, DOWN, buff=0.1)
        self.play(Write(luca_label), FadeIn(luca_sub, shift=UP * 0.2), run_time=1.2)
        self.wait(1.5)

        membrane2 = membrane.copy()
        self.play(membrane.animate.shift(LEFT * 0.5), membrane2.animate.shift(RIGHT * 0.5), run_time=2.0)
        self.wait(0.5)

        self.play(FadeOut(VGroup(title, year_label, ocean, molecules, membrane, membrane2, inner, luca_label, luca_sub)), run_time=1.5)
        self.wait(0.3)

    # ─── CHAPTER 6: Great Oxidation ────────────────────────────────────────

    def chapter_06_great_oxidation(self):
        self.next_section("Great Oxidation Event", skip_animations=False)
        add_chapter_sounds(self, "great_oxidation")
        self.camera.background_color = "#0D1117"

        title = Text("The Great Oxidation Event", font_size=38, color=C_OXYGEN_BLUE, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        year_label = Text("~2.4 billion years ago", font_size=20, color=GREY_B)
        year_label.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(year_label, shift=UP * 0.2), run_time=0.6)

        timeline = Line([-6, -3.2, 0], [6, -3.2, 0], color=GREY_D, stroke_width=2)
        self.play(Create(timeline), run_time=0.5)
        start_label = Text("3.8 bya", font_size=12, color=GREY_C)
        start_label.next_to(timeline.get_left(), DOWN, buff=0.1)
        end_label = Text("Today", font_size=12, color=GREY_C)
        end_label.next_to(timeline.get_right(), DOWN, buff=0.1)
        self.play(Write(start_label), Write(end_label), run_time=0.5)
        goe_dot = Dot(color=C_OXYGEN_BLUE).move_to([1.5, -3.2, 0])
        goe_label = Text("GOE", font_size=12, color=C_OXYGEN_BLUE)
        goe_label.next_to(goe_dot, UP, buff=0.05)
        self.play(FadeIn(goe_dot), Write(goe_label), run_time=0.5)

        cyano_group = VGroup()
        for _ in range(8):
            cyano = Circle(radius=0.12, color=C_LIFE_GREEN, fill_opacity=0.7)
            cyano.set_fill(C_LIFE_GREEN, opacity=0.7)
            cyano.move_to([np.random.uniform(-5, 5), np.random.uniform(-2.5, 0.5), 0])
            cyano_group.add(cyano)
        self.play(*[GrowFromCenter(c, run_time=np.random.uniform(0.3, 0.8)) for c in cyano_group], run_time=2.0)
        cyano_text = Text("Cyanobacteria: O₂-producing photosynthesis", font_size=18, color=C_LIFE_GREEN)
        cyano_text.to_edge(DOWN, buff=0.8)
        self.play(FadeIn(cyano_text, shift=UP * 0.3), run_time=0.8)
        self.wait(0.5)

        oxygen_bubbles = VGroup()
        for _ in range(25):
            bubble = Circle(radius=np.random.uniform(0.03, 0.07), color=C_OXYGEN_BLUE, fill_opacity=0.4)
            bubble.set_fill(C_OXYGEN_BLUE, opacity=0.4)
            bubble.move_to([np.random.uniform(-5, 5), np.random.uniform(-2.5, -1), 0])
            bubble.set_opacity(0)
            oxygen_bubbles.add(bubble)
        self.play(*[bubble.animate(run_time=np.random.uniform(0.5, 1.5)).set_opacity(0.6).shift(UP * np.random.uniform(1, 3))
                    for bubble in oxygen_bubbles], run_time=2.5)

        o2_text = Text("O₂ levels rise dramatically", font_size=22, color=C_OXYGEN_BLUE)
        o2_text.shift(UP * 1.5)
        self.play(Write(o2_text), run_time=0.8)
        self.wait(0.5)

        rust_info = Text("Iron in oceans rusts → Banded Iron Formations", font_size=18, color=C_FIRE_RED)
        rust_info.next_to(cyano_text, DOWN, buff=0.15)
        self.play(FadeIn(rust_info, shift=UP * 0.2), run_time=0.8)
        self.wait(0.8)

        extinction_text = Text("Catastrophic for early anaerobic life", font_size=18, color=RED)
        extinction_text.next_to(rust_info, DOWN, buff=0.15)
        self.play(FadeIn(extinction_text, shift=UP * 0.2), run_time=0.8)
        self.wait(1.5)

        self.play(FadeOut(VGroup(title, year_label, timeline, start_label, end_label, goe_dot, goe_label,
                                cyano_group, cyano_text, oxygen_bubbles, o2_text, rust_info, extinction_text)), run_time=1.5)
        self.wait(0.3)

    # ─── CHAPTER 7: Eukaryotes ────────────────────────────────────────────

    def chapter_07_eukaryotes(self):
        self.next_section("Eukaryotes & Complex Cells", skip_animations=False)
        add_chapter_sounds(self, "eukaryotes")
        self.camera.background_color = "#0D1117"

        title = Text("Eukaryotes: The Complex Cell", font_size=38, color=PURPLE, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        year_label = Text("~2.0 billion years ago", font_size=20, color=GREY_B)
        year_label.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(year_label, shift=UP * 0.2), run_time=0.6)

        prok = Circle(radius=0.5, color=C_LIFE_GREEN, stroke_width=3)
        prok.set_fill(C_LIFE_GREEN, opacity=0.08)
        prok.move_to(LEFT * 3)
        prok_label = Text("Prokaryote", font_size=16, color=C_LIFE_GREEN)
        prok_label.next_to(prok, DOWN, buff=0.3)
        dna_line = Line(prok.get_center() + LEFT * 0.2, prok.get_center() + RIGHT * 0.2, color=C_LIFE_GREEN)
        self.play(DrawBorderThenFill(prok), Create(dna_line), Write(prok_label), run_time=1.5)
        self.wait(0.5)

        prey = Circle(radius=0.25, color=BLUE_D, stroke_width=2)
        prey.set_fill(BLUE_D, opacity=0.1)
        prey.move_to(LEFT * 1.5 + DOWN * 0.3)
        self.play(GrowFromCenter(prey), run_time=0.8)
        self.play(prey.animate.move_to(prok.get_center() + RIGHT * 0.1), run_time=1.5)

        engulf_flash = create_glow_circle(0.8, PURPLE, opacity=0.4)
        engulf_flash.move_to(prok.get_center())
        self.play(engulf_flash.animate.scale(1.5).set_opacity(0), run_time=0.8)
        self.wait(0.3)

        euk = Circle(radius=0.7, color=PURPLE, stroke_width=3)
        euk.set_fill(PURPLE, opacity=0.08)
        euk.move_to(RIGHT * 3)
        nucleus = Circle(radius=0.25, color=PURPLE_A, fill_opacity=0.2)
        nucleus.set_fill(PURPLE_A, opacity=0.2)
        nucleus.move_to(euk.get_center() + LEFT * 0.1)
        mito = Circle(radius=0.15, color=BLUE_D, fill_opacity=0.2)
        mito.set_fill(BLUE_D, opacity=0.2)
        mito.move_to(euk.get_center() + RIGHT * 0.25 + UP * 0.15)
        euk_label = Text("Eukaryote", font_size=16, color=PURPLE)
        euk_label.next_to(euk, DOWN, buff=0.3)
        arrow = Arrow(prok.get_right(), euk.get_left(), color=GREY, stroke_width=2)

        self.play(ReplacementTransform(prok.copy(), euk), run_time=0.5)
        self.play(Create(arrow), FadeIn(nucleus, scale=0.5), FadeIn(mito, scale=0.5), FadeIn(euk_label), run_time=1.5)

        nucleus_label = Text("Nucleus", font_size=12, color=PURPLE_A)
        nucleus_label.next_to(nucleus, LEFT, buff=0.1)
        mito_label = Text("Mitochondria", font_size=12, color=BLUE_D)
        mito_label.next_to(mito, RIGHT, buff=0.1)
        self.play(Write(nucleus_label), Write(mito_label), run_time=0.8)
        self.wait(0.5)

        endo_text = Text("Endosymbiosis: one cell engulfs another,\ncreating organelles", font_size=18, color=GREY_B)
        endo_text.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(endo_text, shift=UP * 0.3), run_time=1.0)
        self.wait(2.0)

        self.play(FadeOut(VGroup(title, year_label, prok, prok_label, dna_line, prey, engulf_flash, arrow,
                                euk, nucleus, mito, euk_label, nucleus_label, mito_label, endo_text)), run_time=1.5)
        self.wait(0.3)

    # ─── CHAPTER 8: Cambrian Explosion ────────────────────────────────────

    def chapter_08_cambrian_explosion(self):
        self.next_section("Cambrian Explosion", skip_animations=False)
        add_chapter_sounds(self, "cambrian")
        self.camera.background_color = "#0a1628"

        title = Text("The Cambrian Explosion", font_size=38, color=C_PRIMORDIAL, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        year_label = Text("~541 million years ago", font_size=20, color=GREY_B)
        year_label.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(year_label, shift=UP * 0.2), run_time=0.6)

        seafloor = Rectangle(width=14, height=0.5, color="#2a1a0a", fill_opacity=1.0)
        seafloor.set_fill("#2a1a0a", opacity=1.0)
        seafloor.to_edge(DOWN, buff=0)
        self.play(FadeIn(seafloor, shift=UP * 0.3), run_time=0.5)
        water = Rectangle(width=14, height=3.5, color=BLUE_D, fill_opacity=0.2)
        water.set_fill(BLUE_D, opacity=0.2)
        water.next_to(seafloor, UP, buff=0)
        self.play(FadeIn(water, shift=UP * 0.3), run_time=0.5)

        creature_shapes = [
            (Circle(radius=0.15, color=C_PRIMORDIAL, fill_opacity=0.7), [-4, -2.2, 0]),
            (RegularPolygon(5, radius=0.12, color=C_WARM_GOLD, fill_opacity=0.7), [-2, -2.5, 0]),
            (Ellipse(width=0.3, height=0.12, color=C_LIFE_GREEN, fill_opacity=0.7), [0, -2.3, 0]),
            (Circle(radius=0.1, color=C_NEBULA_PINK, fill_opacity=0.7), [2, -2.6, 0]),
            (RegularPolygon(6, radius=0.12, color=C_OXYGEN_BLUE, fill_opacity=0.7), [4, -2.4, 0]),
            (Ellipse(width=0.4, height=0.1, color=C_FIRE_RED, fill_opacity=0.7), [-3, -1.8, 0]),
            (Circle(radius=0.08, color=GOLD, fill_opacity=0.7), [3.5, -2.0, 0]),
            (Square(side_length=0.2, color=PURPLE_D, fill_opacity=0.7), [-1, -1.7, 0]),
        ]
        creatures = VGroup()
        for shape, pos in creature_shapes:
            shape.move_to(pos)
            shape.set_opacity(0)
            creatures.add(shape)
        self.play(*[FadeIn(c, scale=0.3, run_time=np.random.uniform(0.4, 1.0)) for c in creatures], run_time=2.5)

        creature_names = [
            ("Trilobite", [-4, -3.0, 0]),
            ("Anomalocaris", [0.5, -3.0, 0]),
            ("Wiwaxia", [4, -3.2, 0]),
        ]
        name_labels = VGroup()
        for name, pos in creature_names:
            label = Text(name, font_size=12, color=GREY_C)
            label.move_to(pos)
            label.set_opacity(0)
            name_labels.add(label)
        self.play(*[FadeIn(l, run_time=0.5) for l in name_labels], run_time=1.0)
        self.wait(0.3)

        for i, c in enumerate(creatures):
            self.play(c.animate.shift(UP * np.random.uniform(0.1, 0.3) * (-1 if i % 2 == 0 else 1)), run_time=0.5)
        self.wait(0.5)

        tree_line = Line(DOWN * 1.0, UP * 1.5, color=GREY_D, stroke_width=2)
        tree_line.shift(RIGHT * 4.5)
        branch_labels_data = [
            ("Arthropods", RIGHT * 4.5 + UP * 1.2, C_PRIMORDIAL),
            ("Chordates", RIGHT * 4.5 + UP * 0.4, BLUE),
            ("Mollusks", RIGHT * 4.5 + DOWN * 0.2, C_WARM_GOLD),
            ("Annelids", RIGHT * 4.5 + DOWN * 0.8, C_LIFE_GREEN),
        ]
        tree_title = Text("Tree of Life", font_size=18, color=GREY_B)
        tree_title.next_to(tree_line, UP, buff=0.3)
        self.play(Create(tree_line), Write(tree_title), run_time=0.8)
        branch_lines = VGroup()
        branch_texts = VGroup()
        for name, pos, color in branch_labels_data:
            line = Line(tree_line.get_bottom(), pos, color=color, stroke_width=1.5)
            text = Text(name, font_size=12, color=color)
            text.next_to(pos, RIGHT, buff=0.1)
            branch_lines.add(line)
            branch_texts.add(text)
        self.play(*[Create(bl) for bl in branch_lines], *[Write(bt) for bt in branch_texts], run_time=1.5)

        diversity_text = Text("Most major animal body plans appear\nin just ~20 million years", font_size=18, color=GREY_B)
        diversity_text.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(diversity_text, shift=UP * 0.3), run_time=1.0)
        self.wait(2.0)

        self.play(FadeOut(VGroup(title, year_label, seafloor, water, creatures, name_labels, tree_line, tree_title, branch_lines, branch_texts, diversity_text)), run_time=1.5)
        self.wait(0.3)

    # ─── CHAPTER 9: Sea to Land ───────────────────────────────────────────

    def chapter_09_sea_to_land(self):
        self.next_section("Sea to Land", skip_animations=False)
        add_chapter_sounds(self, "sea_to_land")
        self.camera.background_color = "#0a1628"

        title = Text("From Sea to Land", font_size=40, color=C_LIFE_GREEN, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        year_label = Text("~400-200 million years ago", font_size=20, color=GREY_B)
        year_label.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(year_label, shift=UP * 0.2), run_time=0.6)

        water_rect = Rectangle(width=5, height=5, color=BLUE_D, fill_opacity=0.3)
        water_rect.set_fill(BLUE_D, opacity=0.3)
        water_rect.move_to(LEFT * 3.5)
        self.play(FadeIn(water_rect, shift=RIGHT * 0.3), run_time=0.5)

        land_area = Polygon(
            [0.5, -2.5, 0], [7, -2.5, 0], [7, 2.5, 0], [0.5, 2.5, 0],
            color="#1a3a1a", fill_opacity=0.6, stroke_opacity=0,
        )
        land_area.set_fill("#1a3a1a", opacity=0.6)
        land_points = [[0.5, -2.5, 0], [2, -2.0, 0], [3.5, -1.8, 0], [5.5, -2.2, 0], [7, -2.5, 0]]
        land = VGroup()
        for i in range(len(land_points) - 1):
            segment = Line(land_points[i], land_points[i + 1], color=C_LIFE_GREEN, stroke_width=3)
            land.add(segment)
        self.play(FadeIn(land_area, shift=LEFT * 0.5), *[Create(s) for s in land], run_time=1.0)

        water_label = Text("Water", font_size=18, color=BLUE_D)
        water_label.move_to(LEFT * 3.5 + UP * 2)
        land_label = Text("Land", font_size=18, color=C_LIFE_GREEN)
        land_label.move_to(RIGHT * 3.5 + UP * 2)
        self.play(Write(water_label), Write(land_label), run_time=0.5)

        fish_body = Ellipse(width=0.6, height=0.2, color=BLUE, fill_opacity=0.7)
        fish_body.set_fill(BLUE, opacity=0.7)
        fish_body.move_to(LEFT * 4 + DOWN * 0.5)
        fish_tail = Polygon([-0.3, 0, 0], [-0.5, -0.15, 0], [-0.5, 0.15, 0], color=BLUE, fill_opacity=0.7)
        fish_tail.move_to(fish_body.get_left())
        fish = VGroup(fish_body, fish_tail)
        self.play(GrowFromCenter(fish), run_time=0.8)

        tetrapod_body = Ellipse(width=0.5, height=0.25, color=C_LIFE_GREEN, fill_opacity=0.7)
        tetrapod_body.set_fill(C_LIFE_GREEN, opacity=0.7)
        tetrapod_body.move_to(RIGHT * 1 + DOWN * 0.8)
        leg1 = Line(ORIGIN, [0.2, -0.2, 0], color=C_LIFE_GREEN, stroke_width=3)
        leg1.move_to(tetrapod_body.get_bottom() + LEFT * 0.15)
        leg2 = Line(ORIGIN, [0.2, -0.2, 0], color=C_LIFE_GREEN, stroke_width=3)
        leg2.move_to(tetrapod_body.get_bottom() + RIGHT * 0.15)
        tetrapod = VGroup(tetrapod_body, leg1, leg2)
        transition_arrow = Arrow(fish.get_right(), tetrapod.get_left(), color=GREY, stroke_width=2)
        self.play(Create(transition_arrow), run_time=0.5)
        self.play(ReplacementTransform(fish.copy(), tetrapod), run_time=1.5)

        tiktaalik_label = Text("Tiktaalik (early tetrapod)", font_size=14, color=C_LIFE_GREEN)
        tiktaalik_label.next_to(tetrapod, DOWN, buff=0.3)
        self.play(Write(tiktaalik_label), run_time=0.5)
        self.wait(0.5)

        plants = VGroup()
        for x in [2.5, 4, 5.5]:
            stem = Line([x, -2.0, 0], [x, -1.0, 0], color=C_LIFE_GREEN, stroke_width=3)
            crown = Circle(radius=0.15, color=C_LIFE_GREEN, fill_opacity=0.5)
            crown.set_fill(C_LIFE_GREEN, opacity=0.5)
            crown.move_to([x, -0.8, 0])
            plants.add(stem, crown)
        self.play(*[Create(p, run_time=0.3) for p in plants], run_time=1.0)
        self.wait(0.3)

        dino_text = Text("Age of Dinosaurs begins ~230 mya", font_size=18, color=C_WARM_GOLD)
        dino_text.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(dino_text, shift=UP * 0.3), run_time=0.8)

        dino_body = Ellipse(width=0.8, height=0.4, color=C_WARM_GOLD, fill_opacity=0.7)
        dino_body.set_fill(C_WARM_GOLD, opacity=0.7)
        dino_body.move_to(RIGHT * 3.5 + UP * 0.5)
        dino_head = Circle(radius=0.15, color=C_WARM_GOLD, fill_opacity=0.7)
        dino_head.set_fill(C_WARM_GOLD, opacity=0.7)
        dino_head.move_to(RIGHT * 4.0 + UP * 0.7)
        dino_neck = Line(dino_body.get_right(), dino_head.get_bottom(), color=C_WARM_GOLD, stroke_width=4)
        dino_tail = Line(dino_body.get_left(), LEFT * 0.2 + RIGHT * 2.9 + UP * 0.3, color=C_WARM_GOLD, stroke_width=3)
        dino_leg = Line(dino_body.get_bottom() + LEFT * 0.1, RIGHT * 3.4 + DOWN * 0.2, color=C_WARM_GOLD, stroke_width=3)
        dino_group = VGroup(dino_body, dino_head, dino_neck, dino_tail, dino_leg)
        self.play(*[Create(d, run_time=0.3) for d in [dino_body, dino_head, dino_neck, dino_tail, dino_leg]], run_time=1.2)
        self.wait(2.0)

        self.play(FadeOut(VGroup(title, year_label, water_rect, land_area, land, water_label, land_label, fish,
                                transition_arrow, tetrapod, tiktaalik_label, plants, dino_text, dino_group)), run_time=1.5)
        self.wait(0.3)

    # ─── CHAPTER 10: Rise of Mammals ──────────────────────────────────────

    def chapter_10_rise_of_mammals(self):
        self.next_section("Rise of Mammals", skip_animations=False)
        add_chapter_sounds(self, "rise_of_mammals")
        self.camera.background_color = COSMIC_BG

        title = Text("Rise of Mammals", font_size=40, color=C_HUMAN_TONE, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        year_label = Text("~66 million years ago to present", font_size=20, color=GREY_B)
        year_label.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(year_label, shift=UP * 0.2), run_time=0.6)

        asteroid = Circle(radius=0.2, color=C_FIRE_RED, fill_opacity=0.9)
        asteroid.set_fill(C_FIRE_RED, opacity=0.9)
        asteroid.move_to(UP * 4 + RIGHT * 2)
        impact_point = DOWN * 2.5 + LEFT * 1
        self.play(asteroid.animate.move_to(impact_point), run_time=2.0, rate_func=rate_functions.ease_in_cubic)

        impact_glow = create_glow_circle(2.0, YELLOW, opacity=0.8)
        impact_glow.move_to(impact_point)
        self.play(impact_glow.animate.scale(4).set_opacity(0), run_time=1.0)
        self.wait(0.3)
        rings = VGroup()
        for r in [0.5, 1.0, 1.5, 2.0]:
            ring = Circle(radius=r, color=ORANGE, stroke_width=1)
            ring.move_to(impact_point)
            ring.set_opacity(0.6)
            rings.add(ring)
        self.play(*[ring.animate.scale(8).set_opacity(0) for ring in rings], run_time=1.5)

        dust = create_glow_circle(3.0, GREY, opacity=0.5)
        dust.move_to(impact_point)
        self.play(dust.animate.scale(2).set_opacity(0.8), run_time=0.8)
        self.wait(0.5)

        dino_fade_text = Text("Non-avian dinosaurs go extinct", font_size=20, color=GREY_B)
        dino_fade_text.to_edge(DOWN, buff=0.5)
        self.play(Write(dino_fade_text), run_time=0.8)
        self.wait(1.0)
        self.play(FadeOut(dust), FadeOut(dino_fade_text), run_time=0.8)

        mammal_text = Text("Small, nocturnal mammals survive", font_size=20, color=C_HUMAN_TONE)
        mammal_text.to_edge(DOWN, buff=0.5)
        self.play(FadeIn(mammal_text, shift=UP * 0.3), run_time=0.8)

        mammals = VGroup()
        for _ in range(6):
            body = Ellipse(width=0.25, height=0.15, color=C_HUMAN_TONE, fill_opacity=0.8)
            body.set_fill(C_HUMAN_TONE, opacity=0.8)
            body.move_to([np.random.uniform(-5, 5), np.random.uniform(-2, 1), 0])
            body.set_opacity(0)
            mammals.add(body)
        self.play(*[FadeIn(m, scale=0.5, run_time=np.random.uniform(0.3, 0.8)) for m in mammals], run_time=2.0)
        self.wait(0.8)

        radiation_text = Text("Mammals diversify into niches left vacant", font_size=18, color=GREY_B)
        radiation_text.next_to(mammal_text, DOWN, buff=0.25)
        self.play(FadeIn(radiation_text, shift=UP * 0.2), run_time=0.8)

        mammal_colors = [C_HUMAN_TONE, C_NEBULA_PINK, C_WARM_GOLD, C_LIFE_GREEN, C_OXYGEN_BLUE, C_PRIMORDIAL]
        self.play(*[mammals[i].animate.scale(np.random.uniform(1.5, 3.0)).set_color(mammal_colors[i])
                    for i in range(len(mammals))], run_time=2.0)

        examples = VGroup()
        example_texts = [
            ("Primates", LEFT * 4 + DOWN * 1, C_HUMAN_TONE),
            ("Carnivores", LEFT * 1.5 + UP * 1, C_FIRE_RED),
            ("Cetaceans", RIGHT * 2 + DOWN * 0.5, C_OXYGEN_BLUE),
            ("Bats", RIGHT * 4 + UP * 1, C_NEBULA_PURPLE),
        ]
        for name, pos, color in example_texts:
            t = Text(name, font_size=14, color=color)
            t.move_to(pos)
            t.set_opacity(0)
            examples.add(t)
        self.play(*[FadeIn(e, run_time=0.5) for e in examples], run_time=1.0)
        self.wait(2.0)

        self.play(FadeOut(VGroup(title, year_label, asteroid, impact_glow, rings, mammals, mammal_text, radiation_text, examples)), run_time=1.5)
        self.wait(0.3)

    # ─── CHAPTER 11: Primate Lineage ──────────────────────────────────────

    def chapter_11_primate_lineage(self):
        self.next_section("Primate Lineage", skip_animations=False)
        add_chapter_sounds(self, "primates")
        self.camera.background_color = COSMIC_BG

        title = Text("The Primate Lineage", font_size=38, color=C_HUMAN_TONE, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        year_label = Text("~65 million years ago → present", font_size=20, color=GREY_B)
        year_label.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(year_label, shift=UP * 0.2), run_time=0.6)

        tree_start = DOWN * 2 + LEFT * 4
        trunk = Line(tree_start, tree_start + UP * 3.5, color=GREY_D, stroke_width=3)
        self.play(Create(trunk), run_time=0.5)

        branch_data = [
            (0.7, "Strepsirrhines\n(lemurs, lorises)", C_NEBULA_PINK),
            (1.5, "Tarsiers", C_PRIMORDIAL),
            (2.3, "New World\nMonkeys", C_LIFE_GREEN),
            (2.8, "Old World\nMonkeys", C_OXYGEN_BLUE),
            (3.2, "Apes", C_HUMAN_TONE),
        ]
        branches = VGroup()
        branch_labels = VGroup()
        for y_frac, name, color in branch_data:
            y = tree_start[1] + y_frac * 3.0
            branch_line = Line([tree_start[0] + 0.5, y, 0], [tree_start[0] + 2.0, y, 0], color=color, stroke_width=2)
            label = Text(name, font_size=12, color=color)
            label.next_to(branch_line, RIGHT, buff=0.1)
            branches.add(branch_line)
            branch_labels.add(label)
        self.play(*[Create(b) for b in branches], *[Write(l) for l in branch_labels], run_time=2.0)
        self.wait(0.5)

        human_branch_start = tree_start[1] + 3.2 * 3.0 + 0.5
        human_line = Line([tree_start[0] + 0.5, human_branch_start, 0],
                          [tree_start[0] + 0.5, tree_start[1] + 3.8, 0],
                          color=C_WARM_GOLD, stroke_width=3)
        human_label = Text("Hominins", font_size=14, color=C_WARM_GOLD, weight=BOLD)
        human_label.next_to(human_line, LEFT, buff=0.3)
        self.play(Create(human_line), Write(human_label), run_time=1.0)
        self.wait(0.3)

        adaptations = VGroup()
        adapt_texts = ["Binocular vision", "Opposable thumbs", "Large brains relative to body", "Social learning"]
        for i, text in enumerate(adapt_texts):
            t = Text(f"✓ {text}", font_size=16, color=GREY_B)
            t.move_to(RIGHT * 2.5 + DOWN * 1 + DOWN * i * 0.4)
            t.set_opacity(0)
            adaptations.add(t)
        self.play(*[FadeIn(a, shift=LEFT * 0.3, run_time=0.5) for a in adaptations], run_time=2.0)

        bipedalism = Text("Bipedalism evolves ~6-7 mya", font_size=18, color=C_WARM_GOLD)
        bipedalism.next_to(human_label, DOWN, buff=0.5)
        self.play(FadeIn(bipedalism, shift=UP * 0.2), run_time=0.8)
        self.wait(2.0)

        self.play(FadeOut(VGroup(title, year_label, trunk, branches, branch_labels, human_line, human_label, adaptations, bipedalism)), run_time=1.5)
        self.wait(0.3)

    # ─── CHAPTER 12: Human Evolution ──────────────────────────────────────

    def chapter_12_human_evolution(self):
        self.next_section("Human Evolution", skip_animations=False)
        add_chapter_sounds(self, "human_evolution")
        self.camera.background_color = COSMIC_BG

        title = Text("The Human Journey", font_size=40, color=C_WARM_GOLD, weight=BOLD)
        title.to_edge(UP, buff=0.5)
        self.play(Write(title), run_time=0.8)
        year_label = Text("~7 million years ago → present", font_size=20, color=GREY_B)
        year_label.next_to(title, DOWN, buff=0.25)
        self.play(FadeIn(year_label, shift=UP * 0.2), run_time=0.6)

        timeline = Line(LEFT * 6, RIGHT * 6, color=GREY_D, stroke_width=2)
        timeline.shift(DOWN * 2.5)
        self.play(Create(timeline), run_time=0.5)

        species = [
            ("Sahelanthropus\ntchadensis", -5.5, C_HUMAN_TONE, "~7 mya"),
            ("Australopithecus\nafarensis", -3.5, C_PRIMORDIAL, "~4 mya"),
            ("Homo\nhabilis", -1.5, C_FIRE_RED, "~2.8 mya"),
            ("Homo\nerectus", 0.5, C_WARM_GOLD, "~2 mya"),
            ("Homo\nneanderthalensis", 2.5, C_NEBULA_PURPLE, "~400 kya"),
            ("Homo\nsapiens", 4.5, BLUE, "~300 kya"),
        ]
        species_labels = VGroup()
        for name, x_pos, color, date in species:
            dot = Dot(radius=0.08, color=color).move_to([x_pos, -2.5, 0])
            fig_circle = Circle(radius=0.12, color=color, fill_opacity=0.7)
            fig_circle.set_fill(color, opacity=0.7)
            fig_circle.move_to([x_pos, -1.0, 0])
            fig_body = Line([x_pos, -0.88, 0], [x_pos, -1.4, 0], color=color, stroke_width=2)
            fig = VGroup(fig_circle, fig_body)
            name_text = Text(name, font_size=10, color=color)
            name_text.next_to(fig, UP, buff=0.1)
            date_text = Text(date, font_size=9, color=GREY_C)
            date_text.next_to(dot, DOWN, buff=0.05)
            species_labels.add(VGroup(fig, name_text, dot, date_text))
        for s in species_labels:
            s.set_opacity(0)
        self.play(*[FadeIn(s, run_time=0.5) for s in species_labels], run_time=3.0)
        self.wait(0.5)

        brain_sizes = [
            (350, -4.5, BLUE_D), (450, -3.0, C_PRIMORDIAL), (600, -1.5, C_FIRE_RED),
            (900, 0.0, C_WARM_GOLD), (1400, 2.0, C_NEBULA_PURPLE), (1350, 3.5, BLUE),
        ]
        brain_bars = VGroup()
        for size, x_pos, color in brain_sizes:
            height = size / 1400 * 2.0
            bar = Rectangle(width=0.3, height=height, color=color, fill_opacity=0.6)
            bar.set_fill(color, opacity=0.6)
            bar.move_to([x_pos, -2.0 + height / 2, 0])
            bar.set_opacity(0)
            brain_bars.add(bar)
        self.play(*[FadeIn(b, shift=UP * 0.3, run_time=0.4) for b in brain_bars], run_time=2.0)
        brain_cc = Text("Brain size: ~350 cm³ → ~1350 cm³", font_size=14, color=GREY_B)
        brain_cc.next_to(brain_bars, DOWN, buff=0.3)
        self.play(FadeIn(brain_cc, shift=UP * 0.2), run_time=0.6)
        self.wait(0.8)

        tech_advances = [
            ("Oldowan tools\n(~2.6 mya)", 0.5, C_HUMAN_TONE),
            ("Fire control\n(~1.5 mya)", 1.5, C_FIRE_RED),
            ("Acheulean axes\n(~1.7 mya)", 2.5, C_WARM_GOLD),
            ("Symbolic art\n(~100 kya)", 3.5, C_NEBULA_PINK),
            ("Agriculture\n(~10 kya)", 4.5, C_LIFE_GREEN),
        ]
        tech_group = VGroup()
        for text, x_off, color in tech_advances:
            t = Text(text, font_size=12, color=color)
            t.move_to(RIGHT * x_off + UP * 0.5)
            t.set_opacity(0)
            tech_group.add(t)
        self.play(*[FadeIn(t, shift=UP * 0.2, run_time=0.5) for t in tech_group], run_time=2.5)
        self.wait(0.5)

        africa_text = Text("Homo sapiens migrates out of Africa ~70 kya", font_size=18, color=C_WARM_GOLD)
        africa_text.to_edge(DOWN, buff=0.3)
        self.play(FadeIn(africa_text, shift=UP * 0.3), run_time=0.8)
        self.wait(1.5)

        self.play(FadeOut(VGroup(title, year_label, timeline, species_labels, brain_bars, brain_cc, tech_group, africa_text)), run_time=1.5)
        self.wait(0.3)

    # ─── CHAPTER 13: Conclusion ───────────────────────────────────────────

    def chapter_13_conclusion(self):
        self.next_section("Conclusion", skip_animations=False)
        add_chapter_sounds(self, "conclusion")
        self.camera.background_color = COSMIC_BG

        stars = create_star_field(150)
        self.add(stars)
        for star in stars:
            star.set_opacity(np.random.uniform(0.2, 0.8))

        recap_title = Text("13.8 Billion Years in 15 Minutes", font_size=30, color=GREY_B)
        recap_title.to_edge(UP, buff=0.5)
        self.play(Write(recap_title), run_time=1.0)

        timeline = Line(LEFT * 6, RIGHT * 6, color=GREY_D, stroke_width=2)
        timeline.shift(DOWN * 1.5)
        self.play(Create(timeline), run_time=0.5)

        events = [
            (-5.5, "Big Bang", BLUE, 13.8),
            (-3.5, "First Stars", C_GALAXY_BLUE, 13.4),
            (-1.8, "Earth", C_LIFE_GREEN, 4.6),
            (-0.5, "First Life", C_LIFE_GREEN, 3.8),
            (0.5, "Cambrian Exp.", C_PRIMORDIAL, 0.541),
            (1.5, "Humans", C_WARM_GOLD, 0.003),
            (4.5, "You", YELLOW, 0.0),
        ]
        event_labels = VGroup()
        for x, name, color, bya in events:
            dot = Dot(radius=0.06, color=color).move_to([x, -1.5, 0])
            label = Text(name, font_size=11, color=color)
            label.next_to(dot, UP, buff=0.05)
            if bya > 0:
                year = Text(f"{bya} bya", font_size=9, color=GREY_C)
                year.next_to(dot, DOWN, buff=0.03)
                event_labels.add(VGroup(dot, label, year))
            else:
                event_labels.add(VGroup(dot, label))
        self.play(*[FadeIn(e, scale=0.5, run_time=0.3) for e in event_labels], run_time=2.0)
        self.wait(1.0)

        self.play(FadeOut(recap_title), FadeOut(timeline), FadeOut(event_labels), run_time=1.5)

        final_messages = [
            "You are made of stardust.",
            "The calcium in your bones",
            "the iron in your blood",
            "the oxygen you breathe",
            "were forged in ancient stars.",
            "You are the universe",
            "experiencing itself.",
        ]
        message_group = VGroup()
        for i, msg in enumerate(final_messages):
            if i >= 4:
                t = Text(msg, font_size=32, color=C_WARM_GOLD, weight=BOLD)
            else:
                t = Text(msg, font_size=28, color=GREY_B)
            t.move_to(UP * 1.5 - i * 0.7 * UP)
            t.set_opacity(0)
            message_group.add(t)

        self.play(*[FadeIn(m, shift=UP * 0.2, run_time=1.0) for m in message_group[:4]], run_time=4.0)
        self.wait(0.5)
        self.play(*[FadeIn(m, shift=UP * 0.2, run_time=1.2) for m in message_group[4:]], run_time=3.0)
        self.wait(2.0)

        final_title = Text("From the Big Bang to You", font_size=40, color=C_WARM_GOLD, weight=BOLD)
        final_title.to_edge(DOWN, buff=1.0)
        self.play(Write(final_title), run_time=1.5)
        self.wait(3.0)

        self.play(
            *[FadeOut(m, run_time=2.0) for m in message_group],
            FadeOut(final_title, run_time=2.0),
            FadeOut(stars, run_time=2.0),
            run_time=2.5,
        )
        self.wait(0.5)
