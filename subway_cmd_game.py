#!/usr/bin/env python3
"""Pseudo-3D Subway runner with Tkinter, 3 lives and hit animation."""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass

WINDOW_W = 440
WINDOW_H = 760
FPS_MS = 16
SPAWN_MS = 520
START_LIVES = 3

ROAD_TOP_Y = 120
ROAD_BOTTOM_Y = 730
ROAD_TOP_HALF = 70
ROAD_BOTTOM_HALF = 185

GROUND_SPEED = 0.020
JUMP_HEIGHT = 140
JUMP_DURATION_MS = 460

LANES = [-1, 0, 1]


@dataclass
class WorldObject:
    lane: int
    z: float  # 0.0 far -> 1.0 near
    kind: str  # obstacle | coin


class Subway3DGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Subway 3D Runner")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WINDOW_W, height=WINDOW_H, bg="#0a0f17", highlightthickness=0)
        self.canvas.pack()

        self.score = 0
        self.best = 0
        self.lives = START_LIVES
        self.running = True

        self.player_lane = 0
        self.player_jump_ms = 0

        self.objects: list[WorldObject] = []
        self.road_offset = 0.0

        # hit animation timers
        self.hit_flash_ms = 0
        self.hit_shake_ms = 0

        self.spawn_after_id: str | None = None
        self.loop_after_id: str | None = None

        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)
        self.root.bind("<a>", self.move_left)
        self.root.bind("<d>", self.move_right)
        self.root.bind("<space>", self.jump)
        self.root.bind("<Up>", self.jump)
        self.root.bind("<w>", self.jump)
        self.root.bind("<r>", self.restart)

        self.start_round()

    def start_round(self) -> None:
        self.score = 0
        self.lives = START_LIVES
        self.running = True
        self.player_lane = 0
        self.player_jump_ms = 0
        self.objects.clear()
        self.hit_flash_ms = 0
        self.hit_shake_ms = 0
        self.road_offset = 0.0

        self.schedule_spawn()
        self.game_loop()

    def restart(self, _event: tk.Event | None = None) -> None:
        if self.running:
            return
        if self.spawn_after_id:
            self.root.after_cancel(self.spawn_after_id)
        if self.loop_after_id:
            self.root.after_cancel(self.loop_after_id)
        self.start_round()

    def move_left(self, _event: tk.Event | None = None) -> None:
        if self.running:
            self.player_lane = max(-1, self.player_lane - 1)

    def move_right(self, _event: tk.Event | None = None) -> None:
        if self.running:
            self.player_lane = min(1, self.player_lane + 1)

    def jump(self, _event: tk.Event | None = None) -> None:
        if self.running and self.player_jump_ms <= 0:
            self.player_jump_ms = JUMP_DURATION_MS

    def schedule_spawn(self) -> None:
        if not self.running:
            return

        lane = random.choice(LANES)
        if random.random() < 0.75:
            self.objects.append(WorldObject(lane=lane, z=0.02, kind="obstacle"))
        if random.random() < 0.45:
            self.objects.append(WorldObject(lane=random.choice(LANES), z=0.0, kind="coin"))

        self.spawn_after_id = self.root.after(SPAWN_MS, self.schedule_spawn)

    def lane_x_at_z(self, lane: int, z: float) -> float:
        cx = WINDOW_W / 2
        half = ROAD_TOP_HALF + (ROAD_BOTTOM_HALF - ROAD_TOP_HALF) * z
        lane_width = (half * 2) / 3
        return cx + lane * lane_width

    def y_at_z(self, z: float) -> float:
        return ROAD_TOP_Y + (ROAD_BOTTOM_Y - ROAD_TOP_Y) * z

    def player_jump_offset(self) -> float:
        if self.player_jump_ms <= 0:
            return 0.0
        t = 1.0 - (self.player_jump_ms / JUMP_DURATION_MS)
        arc = 4 * t * (1 - t)
        return JUMP_HEIGHT * arc

    def player_rect(self) -> tuple[float, float, float, float]:
        z = 0.92
        px = self.lane_x_at_z(self.player_lane, z)
        py = self.y_at_z(z) - self.player_jump_offset()

        w = 40
        h = 62
        if self.hit_shake_ms > 0:
            px += random.randint(-6, 6)

        return px - w / 2, py - h, px + w / 2, py

    @staticmethod
    def intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
        return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

    def update_world(self) -> None:
        self.road_offset = (self.road_offset + GROUND_SPEED * 2.1) % 0.13

        for obj in self.objects:
            obj.z += GROUND_SPEED

        self.objects = [o for o in self.objects if o.z <= 1.08]

        self.score += 2
        self.best = max(self.best, self.score)

        if self.player_jump_ms > 0:
            self.player_jump_ms = max(0, self.player_jump_ms - FPS_MS)

        if self.hit_flash_ms > 0:
            self.hit_flash_ms = max(0, self.hit_flash_ms - FPS_MS)
        if self.hit_shake_ms > 0:
            self.hit_shake_ms = max(0, self.hit_shake_ms - FPS_MS)

    def handle_collisions(self) -> None:
        p = self.player_rect()
        kept: list[WorldObject] = []
        hit_this_frame = False

        for obj in self.objects:
            if obj.kind == "coin":
                if obj.z > 0.86 and obj.lane == self.player_lane and self.player_jump_offset() < 40:
                    self.score += 60
                    continue
                kept.append(obj)
                continue

            # obstacle
            if obj.z > 0.88 and obj.z < 1.03 and obj.lane == self.player_lane:
                if self.player_jump_offset() < 55 and not hit_this_frame:
                    self.lives -= 1
                    self.hit_flash_ms = 180
                    self.hit_shake_ms = 220
                    hit_this_frame = True
                continue

            kept.append(obj)

        self.objects = kept

        if self.lives <= 0:
            self.running = False
            self.best = max(self.best, self.score)

    def draw_background(self) -> None:
        c = self.canvas
        c.delete("all")

        # sky gradient bands
        c.create_rectangle(0, 0, WINDOW_W, ROAD_TOP_Y + 40, fill="#112236", outline="")
        c.create_rectangle(0, ROAD_TOP_Y + 40, WINDOW_W, ROAD_TOP_Y + 130, fill="#0f1a2d", outline="")

        cx = WINDOW_W / 2
        left_top = cx - ROAD_TOP_HALF
        right_top = cx + ROAD_TOP_HALF
        left_bottom = cx - ROAD_BOTTOM_HALF
        right_bottom = cx + ROAD_BOTTOM_HALF

        # road trapezoid
        c.create_polygon(
            left_top,
            ROAD_TOP_Y,
            right_top,
            ROAD_TOP_Y,
            right_bottom,
            ROAD_BOTTOM_Y,
            left_bottom,
            ROAD_BOTTOM_Y,
            fill="#222",
            outline="#666",
            width=2,
        )

        # lane lines with perspective movement
        for lane_edge in [-0.5, 0.5]:
            x1 = cx + lane_edge * ((ROAD_TOP_HALF * 2) / 3)
            x2 = cx + lane_edge * ((ROAD_BOTTOM_HALF * 2) / 3)
            c.create_line(x1, ROAD_TOP_Y, x2, ROAD_BOTTOM_Y, fill="#7d7d7d", width=2)

        z = self.road_offset
        while z < 1.0:
            y = self.y_at_z(z)
            half = ROAD_TOP_HALF + (ROAD_BOTTOM_HALF - ROAD_TOP_HALF) * z
            seg_half = max(12, 34 * z)
            c.create_line(cx - seg_half, y, cx + seg_half, y, fill="#bfbfbf", width=max(1, int(1 + z * 2)))
            z += 0.13

    def draw_objects(self) -> None:
        c = self.canvas

        # far to near for depth effect
        for obj in sorted(self.objects, key=lambda o: o.z):
            x = self.lane_x_at_z(obj.lane, obj.z)
            y = self.y_at_z(obj.z)
            scale = 0.35 + obj.z * 1.05

            if obj.kind == "obstacle":
                w = 26 * scale
                h = 34 * scale
                c.create_rectangle(
                    x - w,
                    y - h,
                    x + w,
                    y,
                    fill="#df403b",
                    outline="#7f1916",
                    width=max(1, int(scale * 2)),
                )
            else:
                r = 9 * scale
                c.create_oval(
                    x - r,
                    y - r,
                    x + r,
                    y + r,
                    fill="#ffd347",
                    outline="#9a7d1d",
                    width=max(1, int(scale * 2)),
                )

    def draw_player(self) -> None:
        c = self.canvas
        l, t, r, b = self.player_rect()
        c.create_rectangle(l, t, r, b, fill="#4da7ff", outline="#1f5e9d", width=3)
        c.create_rectangle(l + 6, t + 8, r - 6, t + 20, fill="#b9ddff", outline="")

    def draw_hud(self) -> None:
        c = self.canvas
        c.create_text(12, 14, text=f"Skor: {self.score}", anchor="w", fill="white", font=("Arial", 14, "bold"))
        c.create_text(12, 38, text=f"En iyi: {self.best}", anchor="w", fill="#d6d6d6", font=("Arial", 12))
        c.create_text(WINDOW_W - 12, 14, text=f"Can: {self.lives}", anchor="e", fill="#ff8a8a", font=("Arial", 14, "bold"))
        c.create_text(WINDOW_W / 2, 20, text="A/D veya ←/→ | W/Space zıpla", anchor="n", fill="#d2d2d2", font=("Arial", 10))

        if self.hit_flash_ms > 0:
            alpha = max(40, int(120 * (self.hit_flash_ms / 180)))
            color = f"#ff{max(0, 255 - alpha):02x}{max(0, 255 - alpha):02x}"
            c.create_rectangle(0, 0, WINDOW_W, WINDOW_H, fill=color, outline="")

        if not self.running:
            c.create_rectangle(70, 250, WINDOW_W - 70, 445, fill="#000", outline="#888", width=2)
            c.create_text(WINDOW_W / 2, 300, text="OYUN BİTTİ", fill="white", font=("Arial", 26, "bold"))
            c.create_text(WINDOW_W / 2, 338, text=f"Skor: {self.score}", fill="#ddd", font=("Arial", 16))
            c.create_text(WINDOW_W / 2, 366, text=f"En iyi: {self.best}", fill="#ddd", font=("Arial", 14))
            c.create_text(WINDOW_W / 2, 405, text="Tekrar başlamak için R", fill="#91cbff", font=("Arial", 14, "bold"))

    def draw(self) -> None:
        self.draw_background()
        self.draw_objects()
        self.draw_player()
        self.draw_hud()

    def game_loop(self) -> None:
        if self.running:
            self.update_world()
            self.handle_collisions()

        self.draw()
        self.loop_after_id = self.root.after(FPS_MS, self.game_loop)


def main() -> None:
    root = tk.Tk()
    Subway3DGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
