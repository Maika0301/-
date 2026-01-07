"""
NiuTube 3D PC Builder & Video Sim

- GUI: pyglet window with on-screen HUD instead of CLI
- 3D: Simple spinning rig cubes to represent the PC and monitors
- Play loop:
    * Press 1 to toggle OS (Windows/Ubuntu) and start a build
    * Press 2 to buy the next part (if you have funds)
    * Press 3 to create a channel (enter name in prompt)
    * Press 4 to publish a video in the next category
    * Press TAB to toggle the in-game site feed view
    * Press R to reset the session

No external assets or movie.py usage.
"""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Sequence

import pyglet
from pyglet import gl


AI_MODELS: Sequence[str] = ("ChatGPT", "Gemini", "Claude")
CATEGORIES: Sequence[str] = ("VM/PC Builds", "AI Battles", "Tools & Sites")


@dataclass
class Part:
    name: str
    cost: int


@dataclass
class PC:
    os: str
    parts: List[Part] = field(default_factory=list)

    def total_cost(self) -> int:
        return sum(p.cost for p in self.parts)


@dataclass
class Video:
    title: str
    category: str
    views: int
    likes: int
    ad_revenue: float


@dataclass
class Channel:
    name: str
    videos: List[Video] = field(default_factory=list)

    def upload(self, video: Video) -> None:
        self.videos.append(video)


@dataclass
class NiuTubeSim:
    bank: float = 2500.0
    pc: PC | None = None
    channel: Channel | None = None
    logs: List[str] = field(default_factory=list)
    _generators: Dict[str, Callable[[], Video]] = field(init=False)
    _parts_catalog: Sequence[Part] = field(
        default_factory=lambda: (
            Part("Ryzen 7 CPU", 320),
            Part("Core i7 CPU", 350),
            Part("RTX 4070 GPU", 600),
            Part("RX 7800 XT GPU", 520),
            Part("32GB DDR5 RAM", 180),
            Part("2TB NVMe SSD", 190),
            Part("Platinum PSU", 170),
            Part("Mesh Case", 130),
            Part("240mm AIO", 140),
        )
    )
    _part_index: int = 0
    _category_index: int = 0
    _os_index: int = 0

    def __post_init__(self) -> None:
        self._generators = {
            "VM/PC Builds": self._gen_vm_pc_video,
            "AI Battles": self._gen_ai_battle_video,
            "Tools & Sites": self._gen_tool_site_video,
        }

    def log(self, message: str) -> None:
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        self.logs = self.logs[-12:]

    def toggle_os(self) -> None:
        oses = ("Windows", "Ubuntu")
        self._os_index = (self._os_index + 1) % len(oses)
        choice = oses[self._os_index]
        self.pc = PC(os=choice, parts=[])
        self.log(f"OS selected: {choice}")

    def buy_next_part(self) -> None:
        if self.pc is None:
            self.log("Choose an OS first (press 1).")
            return
        part = self._parts_catalog[self._part_index]
        if self.bank < part.cost:
            self.log("Not enough funds.")
            return
        self.bank -= part.cost
        self.pc.parts.append(part)
        self._part_index = (self._part_index + 1) % len(self._parts_catalog)
        self.log(f"Purchased {part.name} for ${part.cost}. Balance ${self.bank:.2f}")

    def create_channel(self, name: str) -> None:
        if not name:
            self.log("Channel name required.")
            return
        self.channel = Channel(name=name.strip())
        self.log(f"Channel created: {self.channel.name}")

    def publish_next_video(self) -> None:
        if self.channel is None:
            self.log("Create a channel first (press 3).")
            return
        category = CATEGORIES[self._category_index]
        self._category_index = (self._category_index + 1) % len(CATEGORIES)
        video = self._generators[category]()
        self.channel.upload(video)
        self.bank += video.ad_revenue
        self.log(
            f"Uploaded '{video.title}' | {video.views} views | +${video.ad_revenue:.2f}"
        )

    def reset(self) -> None:
        self.bank = 2500.0
        self.pc = None
        self.channel = None
        self.logs.clear()
        self._part_index = 0
        self._category_index = 0
        self._os_index = 0
        self.log("Session reset.")

    # ---- video generators ----
    def _gen_vm_pc_video(self) -> Video:
        config = ", ".join(p.name for p in (self.pc.parts if self.pc else [])) or "budget build"
        views = random.randint(8_000, 140_000)
        likes = int(views * random.uniform(0.06, 0.12))
        revenue = views * 0.0015
        return Video(
            title=f"{self.pc.os if self.pc else 'DIY'} Rig: {config}",
            category="VM/PC Builds",
            views=views,
            likes=likes,
            ad_revenue=revenue,
        )

    def _gen_ai_battle_video(self) -> Video:
        p1, p2 = random.sample(AI_MODELS, 2)
        topic = random.choice(("code review", "math duel", "story face-off"))
        views = random.randint(30_000, 320_000)
        likes = int(views * random.uniform(0.08, 0.15))
        revenue = views * 0.002
        return Video(
            title=f"{p1} vs {p2}: {topic}!",
            category="AI Battles",
            views=views,
            likes=likes,
            ad_revenue=revenue,
        )

    def _gen_tool_site_video(self) -> Video:
        concept = random.choice(
            (
                "auto-texture lab",
                "VM snapshotter",
                "AI overlay IDE",
                "NiuTube video site builder",
            )
        )
        views = random.randint(10_000, 180_000)
        likes = int(views * random.uniform(0.07, 0.13))
        revenue = views * 0.0017
        return Video(
            title=f"Built a {concept} for creators",
            category="Tools & Sites",
            views=views,
            likes=likes,
            ad_revenue=revenue,
        )


# ---- Rendering helpers ----


def set_3d(window: pyglet.window.Window) -> None:
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glClearColor(0.04, 0.05, 0.08, 1.0)
    width, height = window.get_size()
    aspect = width / float(height)
    gl.glViewport(0, 0, width, height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    glu_perspective(65.0, aspect, 0.1, 100.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()


def glu_perspective(fov: float, aspect: float, znear: float, zfar: float) -> None:
    f = 1.0 / math.tan(math.radians(fov) / 2.0)
    m = (gl.GLfloat * 16)(
        f / aspect,
        0,
        0,
        0,
        0,
        f,
        0,
        0,
        0,
        0,
        (zfar + znear) / (znear - zfar),
        -1,
        0,
        0,
        (2 * zfar * znear) / (znear - zfar),
        0,
    )
    gl.glMultMatrixf(m)


def draw_cube(size: float, color: Sequence[float]) -> None:
    hs = size / 2.0
    vertices = [
        -hs, -hs, -hs,
        hs, -hs, -hs,
        hs, hs, -hs,
        -hs, hs, -hs,
        -hs, -hs, hs,
        hs, -hs, hs,
        hs, hs, hs,
        -hs, hs, hs,
    ]
    indices = [
        0, 1, 2, 3,  # back
        4, 5, 6, 7,  # front
        3, 2, 6, 7,  # top
        0, 1, 5, 4,  # bottom
        1, 2, 6, 5,  # right
        0, 3, 7, 4,  # left
    ]
    colors = list(color) * 8
    vertex_list = pyglet.graphics.vertex_list_indexed(
        8,
        indices,
        ("v3f/static", vertices),
        ("c3f/static", colors),
    )
    vertex_list.draw(gl.GL_QUADS)


class NiuTubeApp(pyglet.window.Window):
    def __init__(self) -> None:
        super().__init__(1280, 720, "NiuTube 3D Sim", resizable=True)
        self.sim = NiuTubeSim()
        self.site_view = False
        self.hud_batch = pyglet.graphics.Batch()
        self.labels: List[pyglet.text.Label] = []
        self._setup_hud()
        pyglet.clock.schedule_interval(self.update, 1 / 60.0)
        self._log_gl_info()

    def _log_gl_info(self) -> None:
        gl.gl_info.set_active_context()
        version = gl.gl_info.get_version()
        renderer = gl.gl_info.get_renderer()
        vendor = gl.gl_info.get_vendor()
        self.sim.log(f"GL version: {version}")
        self.sim.log(f"GL renderer: {renderer}")
        self.sim.log(f"GL vendor: {vendor}")

    def _setup_hud(self) -> None:
        self.labels = []
        for i in range(20):
            label = pyglet.text.Label(
                "",
                x=20,
                y=self.height - 20 - i * 22,
                anchor_x="left",
                anchor_y="top",
                color=(230, 230, 240, 255),
                batch=self.hud_batch,
            )
            self.labels.append(label)

    def on_resize(self, width: int, height: int) -> None:
        super().on_resize(width, height)
        self._setup_hud()

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        if symbol == pyglet.window.key._1:
            self.sim.toggle_os()
        elif symbol == pyglet.window.key._2:
            self.sim.buy_next_part()
        elif symbol == pyglet.window.key._3:
            name = input("Enter channel name: ")
            self.sim.create_channel(name)
        elif symbol == pyglet.window.key._4:
            self.sim.publish_next_video()
        elif symbol == pyglet.window.key.TAB:
            self.site_view = not self.site_view
        elif symbol == pyglet.window.key.R:
            self.sim.reset()

    def update(self, dt: float) -> None:
        pass

    # ---- drawing ----
    def on_draw(self) -> None:
        self.clear()
        set_3d(self)
        self._draw_scene()
        self._draw_hud()

    def _draw_scene(self) -> None:
        gl.glLoadIdentity()
        t = time.time()
        radius = 6.0
        cam_x = math.cos(t * 0.5) * radius
        cam_z = math.sin(t * 0.5) * radius
        gl.gluLookAt(cam_x, 3.0, cam_z, 0.0, 0.5, 0.0, 0.0, 1.0, 0.0)

        gl.glRotatef(t * 20.0, 0, 1, 0)
        draw_cube(2.4, (0.1, 0.5, 0.8))
        gl.glPushMatrix()
        gl.glTranslatef(0.0, 1.8, 0.0)
        gl.glScalef(1.4, 0.8, 0.1)
        draw_cube(1.0, (0.9, 0.9, 0.9))
        gl.glPopMatrix()

        gl.glPushMatrix()
        gl.glTranslatef(-2.4, 1.0, 0.0)
        gl.glRotatef(t * 40.0, 0, 1, 0)
        draw_cube(1.2, (0.9, 0.6, 0.2))
        gl.glPopMatrix()

        gl.glPushMatrix()
        gl.glTranslatef(2.4, 0.8, 0.0)
        gl.glRotatef(t * 60.0, 0, 1, 0)
        draw_cube(0.9, (0.2, 0.9, 0.5))
        gl.glPopMatrix()

    def _draw_hud(self) -> None:
        gl.glDisable(gl.GL_DEPTH_TEST)
        info_lines = self._build_info_lines()
        for label, text in zip(self.labels, info_lines):
            label.text = text
        self.hud_batch.draw()

    def _build_info_lines(self) -> List[str]:
        lines: List[str] = []
        lines.append("NiuTube: PC Builder + Video Site (GUI/3D)")
        lines.append("Controls: 1 OS | 2 Buy part | 3 Channel | 4 Publish | TAB Site | R Reset")
        lines.append(f"Bank: ${self.sim.bank:.2f}")
        lines.append(
            f"PC: {self.sim.pc.os if self.sim.pc else 'None'} "
            f"(${self.sim.pc.total_cost() if self.sim.pc else 0})"
        )
        parts = ", ".join(p.name for p in (self.sim.pc.parts if self.sim.pc else []))
        lines.append(f"Parts: {parts if parts else '-'}")
        lines.append(f"Channel: {self.sim.channel.name if self.sim.channel else '-'}")

        if self.site_view and self.sim.channel:
            lines.append("--- NiuTube Site Feed ---")
            if not self.sim.channel.videos:
                lines.append("No uploads yet.")
            else:
                for v in reversed(self.sim.channel.videos[-6:]):
                    lines.append(
                        f"{v.category}: {v.title} | {v.views} views | {v.likes} likes | ${v.ad_revenue:.2f}"
                    )
        else:
            lines.append("--- Activity ---")
            lines.extend(reversed(self.sim.logs))
        return lines


if __name__ == "__main__":
    window = NiuTubeApp()
    pyglet.app.run()
