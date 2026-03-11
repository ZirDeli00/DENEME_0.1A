#!/usr/bin/env python3
"""Subway pseudo-3D runner with menu, settings, and gameplay help."""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog

# Optional drag & drop support
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore
except Exception:
    DND_FILES = None
    TkinterDnD = None

# Optional mp3 playback support
try:
    import pygame  # type: ignore
except Exception:
    pygame = None

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
    z: float
    kind: str  # obstacle | coin


class Subway3DGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Subway 3D Runner")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WINDOW_W, height=WINDOW_H, bg="#0a0f17", highlightthickness=0)
        self.canvas.pack()

        self.state = "menu"  # menu | settings | help | game

        self.score = 0
        self.best = 0
        self.lives = START_LIVES
        self.running = False

        self.player_lane = 0
        self.player_jump_ms = 0

        self.objects: list[WorldObject] = []
        self.road_offset = 0.0

        self.hit_flash_ms = 0
        self.hit_shake_ms = 0

        self.music_path: str | None = None
        self.music_status = "Müzik seçilmedi"

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

        self.canvas.bind("<Button-1>", self.handle_click)

        if DND_FILES is not None:
            try:
                self.canvas.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
                self.canvas.dnd_bind("<<Drop>>", self.on_drop_file)  # type: ignore[attr-defined]
            except Exception:
                pass

        self.game_loop()

    # ---------- menu / ui ----------
    def handle_click(self, event: tk.Event) -> None:
        x, y = event.x, event.y

        if self.state == "menu":
            if self.in_rect(x, y, (120, 260, 320, 320)):
                self.start_game()
            elif self.in_rect(x, y, (120, 340, 320, 400)):
                self.state = "settings"
            elif self.in_rect(x, y, (120, 420, 320, 480)):
                self.state = "help"

        elif self.state == "settings":
            if self.in_rect(x, y, (85, 565, 355, 620)):
                self.select_music_file()
            elif self.in_rect(x, y, (160, 655, 280, 705)):
                self.state = "menu"

        elif self.state == "help":
            if self.in_rect(x, y, (160, 655, 280, 705)):
                self.state = "menu"

        elif self.state == "game" and not self.running:
            if self.in_rect(x, y, (140, 460, 300, 510)):
                self.state = "menu"

    @staticmethod
    def in_rect(x: int, y: int, rect: tuple[int, int, int, int]) -> bool:
        l, t, r, b = rect
        return l <= x <= r and t <= y <= b

    # ---------- audio ----------
    def select_music_file(self) -> None:
        file_path = filedialog.askopenfilename(
            title="MP3 seç",
            filetypes=[("MP3 files", "*.mp3"), ("All files", "*.*")],
        )
        if file_path:
            self.set_music(file_path)

    def on_drop_file(self, event: tk.Event) -> None:
        if self.state != "settings":
            return

        raw = str(event.data).strip()
        if raw.startswith("{") and raw.endswith("}"):
            raw = raw[1:-1]
        path = raw.split()[0] if raw else ""
        if path.lower().endswith(".mp3"):
            self.set_music(path)

    def set_music(self, path: str) -> None:
        if not Path(path).exists():
            self.music_status = "Dosya bulunamadı"
            return
        if not path.lower().endswith(".mp3"):
            self.music_status = "Lütfen .mp3 dosyası seç"
            return

        self.music_path = path
        self.music_status = f"Yüklendi: {Path(path).name}"
        self.play_music()

    def play_music(self) -> None:
        if self.music_path is None:
            return
        if pygame is None:
            self.music_status = "pygame yok: müzik oynatılamadı"
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.play(-1)
            self.music_status = f"Çalıyor: {Path(self.music_path).name}"
        except Exception:
            self.music_status = "MP3 oynatılamadı"

    # ---------- game ----------
    def start_game(self) -> None:
        self.state = "game"
        self.score = 0
        self.lives = START_LIVES
        self.running = True
        self.player_lane = 0
        self.player_jump_ms = 0
        self.objects.clear()
        self.hit_flash_ms = 0
        self.hit_shake_ms = 0
        self.road_offset = 0.0

        if self.spawn_after_id:
            self.root.after_cancel(self.spawn_after_id)
        self.schedule_spawn()

    def restart(self, _event: tk.Event | None = None) -> None:
        if self.state == "game" and not self.running:
            self.start_game()

    def move_left(self, _event: tk.Event | None = None) -> None:
        if self.state == "game" and self.running:
            self.player_lane = max(-1, self.player_lane - 1)

    def move_right(self, _event: tk.Event | None = None) -> None:
        if self.state == "game" and self.running:
            self.player_lane = min(1, self.player_lane + 1)

    def jump(self, _event: tk.Event | None = None) -> None:
        if self.state == "game" and self.running and self.player_jump_ms <= 0:
            self.player_jump_ms = JUMP_DURATION_MS

    def schedule_spawn(self) -> None:
        if not (self.state == "game" and self.running):
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
        return JUMP_HEIGHT * (4 * t * (1 - t))

    def player_rect(self) -> tuple[float, float, float, float]:
        z = 0.92
        px = self.lane_x_at_z(self.player_lane, z)
        py = self.y_at_z(z) - self.player_jump_offset()
        if self.hit_shake_ms > 0:
            px += random.randint(-6, 6)
        w, h = 40, 62
        return px - w / 2, py - h, px + w / 2, py

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
        kept: list[WorldObject] = []
        hit = False

        for obj in self.objects:
            if obj.kind == "coin":
                if obj.z > 0.86 and obj.lane == self.player_lane and self.player_jump_offset() < 40:
                    self.score += 60
                    continue
                kept.append(obj)
                continue

            if 0.88 < obj.z < 1.03 and obj.lane == self.player_lane:
                if self.player_jump_offset() < 55 and not hit:
                    self.lives -= 1
                    self.hit_flash_ms = 180
                    self.hit_shake_ms = 220
                    hit = True
                continue

            kept.append(obj)

        self.objects = kept
        if self.lives <= 0:
            self.running = False
            self.best = max(self.best, self.score)

    # ---------- draw ----------
    def draw_button(self, rect: tuple[int, int, int, int], text: str) -> None:
        l, t, r, b = rect
        self.canvas.create_rectangle(l, t, r, b, fill="#1f2f46", outline="#9ac5ff", width=2)
        self.canvas.create_text((l + r) / 2, (t + b) / 2, text=text, fill="white", font=("Arial", 14, "bold"))

    def draw_menu(self) -> None:
        c = self.canvas
        c.delete("all")
        c.create_rectangle(0, 0, WINDOW_W, WINDOW_H, fill="#091522", outline="")
        c.create_text(WINDOW_W / 2, 150, text="SUBWAY 3D RUNNER", fill="#cbe5ff", font=("Arial", 30, "bold"))
        c.create_text(WINDOW_W / 2, 195, text="Ana Menü", fill="#9ec9ff", font=("Arial", 16))

        self.draw_button((120, 260, 320, 320), "Oyna")
        self.draw_button((120, 340, 320, 400), "Ayarlar")
        self.draw_button((120, 420, 320, 480), "Oynanış")

    def draw_settings(self) -> None:
        c = self.canvas
        c.delete("all")
        c.create_rectangle(0, 0, WINDOW_W, WINDOW_H, fill="#101825", outline="")
        c.create_text(WINDOW_W / 2, 90, text="Ayarlar", fill="white", font=("Arial", 26, "bold"))
        c.create_text(
            WINDOW_W / 2,
            140,
            text="MP3 dosyanı alana sürükleyip bırakabilirsin\n(veya alana tıklayıp dosya seçebilirsin)",
            fill="#cfd8e3",
            font=("Arial", 11),
            justify="center",
        )

        drop_rect = (70, 230, 370, 420)
        l, t, r, b = drop_rect
        c.create_rectangle(l, t, r, b, fill="#1b2636", outline="#86b6ff", width=3)
        c.create_text(WINDOW_W / 2, 290, text="MP3 Sürükle & Bırak", fill="#d6e8ff", font=("Arial", 18, "bold"))
        c.create_text(WINDOW_W / 2, 330, text=".mp3 dosyasını bu kutuya bırak", fill="#b5cbe8", font=("Arial", 11))

        self.draw_button((85, 565, 355, 620), "Dosya Seç (Yedek)")

        c.create_text(WINDOW_W / 2, 470, text=self.music_status, fill="#ffe39b", font=("Arial", 12, "bold"))
        if DND_FILES is None:
            c.create_text(
                WINDOW_W / 2,
                510,
                text="Sürükle-bırak için tkinterdnd2 gerekli.\nŞu an Dosya Seç butonunu kullanabilirsin.",
                fill="#ffb3b3",
                font=("Arial", 10),
                justify="center",
            )

        self.draw_button((160, 655, 280, 705), "Geri")

    def draw_help(self) -> None:
        c = self.canvas
        c.delete("all")
        c.create_rectangle(0, 0, WINDOW_W, WINDOW_H, fill="#121a28", outline="")
        c.create_text(WINDOW_W / 2, 90, text="Oynanış", fill="white", font=("Arial", 26, "bold"))

        text = (
            "• A/D veya ←/→ ile şerit değiştir.\n"
            "• W / ↑ / Space ile zıpla.\n"
            "• Engellere çarparsan 1 can kaybedersin.\n"
            "• Toplam 3 canın var, bitince oyun biter.\n"
            "• Coin toplayarak daha yüksek skor yap.\n\n"
            "Bu oyun Python + Tkinter ile\n"
            "Subway tarzı koşu mantığında geliştirildi."
        )
        c.create_text(WINDOW_W / 2, 340, text=text, fill="#d7e4f5", font=("Arial", 13), justify="center")

        self.draw_button((160, 655, 280, 705), "Geri")

    def draw_game(self) -> None:
        c = self.canvas
        c.delete("all")
        c.create_rectangle(0, 0, WINDOW_W, ROAD_TOP_Y + 130, fill="#102138", outline="")

        cx = WINDOW_W / 2
        c.create_polygon(
            cx - ROAD_TOP_HALF,
            ROAD_TOP_Y,
            cx + ROAD_TOP_HALF,
            ROAD_TOP_Y,
            cx + ROAD_BOTTOM_HALF,
            ROAD_BOTTOM_Y,
            cx - ROAD_BOTTOM_HALF,
            ROAD_BOTTOM_Y,
            fill="#222",
            outline="#666",
            width=2,
        )

        for lane_edge in [-0.5, 0.5]:
            c.create_line(
                cx + lane_edge * ((ROAD_TOP_HALF * 2) / 3),
                ROAD_TOP_Y,
                cx + lane_edge * ((ROAD_BOTTOM_HALF * 2) / 3),
                ROAD_BOTTOM_Y,
                fill="#7d7d7d",
                width=2,
            )

        z = self.road_offset
        while z < 1.0:
            y = self.y_at_z(z)
            seg_half = max(12, 34 * z)
            c.create_line(cx - seg_half, y, cx + seg_half, y, fill="#bfbfbf", width=max(1, int(1 + z * 2)))
            z += 0.13

        for obj in sorted(self.objects, key=lambda o: o.z):
            x = self.lane_x_at_z(obj.lane, obj.z)
            y = self.y_at_z(obj.z)
            scale = 0.35 + obj.z * 1.05
            if obj.kind == "obstacle":
                w = 26 * scale
                h = 34 * scale
                c.create_rectangle(x - w, y - h, x + w, y, fill="#df403b", outline="#7f1916", width=max(1, int(scale * 2)))
            else:
                r = 9 * scale
                c.create_oval(x - r, y - r, x + r, y + r, fill="#ffd347", outline="#9a7d1d", width=max(1, int(scale * 2)))

        l, t, r, b = self.player_rect()
        c.create_rectangle(l, t, r, b, fill="#4da7ff", outline="#1f5e9d", width=3)

        c.create_text(12, 14, text=f"Skor: {self.score}", anchor="w", fill="white", font=("Arial", 14, "bold"))
        c.create_text(12, 38, text=f"En iyi: {self.best}", anchor="w", fill="#d6d6d6", font=("Arial", 12))
        c.create_text(WINDOW_W - 12, 14, text=f"Can: {self.lives}", anchor="e", fill="#ff8a8a", font=("Arial", 14, "bold"))

        if self.hit_flash_ms > 0:
            c.create_rectangle(0, 0, WINDOW_W, WINDOW_H, fill="#ffb3b3", outline="")

        if not self.running:
            c.create_rectangle(70, 250, WINDOW_W - 70, 530, fill="#000", outline="#888", width=2)
            c.create_text(WINDOW_W / 2, 305, text="OYUN BİTTİ", fill="white", font=("Arial", 26, "bold"))
            c.create_text(WINDOW_W / 2, 345, text=f"Skor: {self.score}", fill="#ddd", font=("Arial", 16))
            c.create_text(WINDOW_W / 2, 372, text=f"En iyi: {self.best}", fill="#ddd", font=("Arial", 14))
            c.create_text(WINDOW_W / 2, 405, text="R: tekrar başlat", fill="#91cbff", font=("Arial", 13, "bold"))
            self.draw_button((140, 460, 300, 510), "Ana Menü")

    def draw(self) -> None:
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "settings":
            self.draw_settings()
        elif self.state == "help":
            self.draw_help()
        else:
            self.draw_game()

    def game_loop(self) -> None:
        if self.state == "game" and self.running:
            self.update_world()
            self.handle_collisions()
        self.draw()
        self.loop_after_id = self.root.after(FPS_MS, self.game_loop)


def create_root() -> tk.Tk:
    if TkinterDnD is not None:
        return TkinterDnD.Tk()
    return tk.Tk()


def main() -> None:
    root = create_root()
    Subway3DGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
