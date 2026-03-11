#!/usr/bin/env python3
"""2D Subway Surfers-style mini game with Tkinter and 3 lives."""

from __future__ import annotations

import random
import tkinter as tk
from dataclasses import dataclass

WINDOW_W = 420
WINDOW_H = 700
LANES_X = [105, 210, 315]
PLAYER_Y = 590
GROUND_SPEED = 8
SPAWN_MS = 650
TICK_MS = 16
JUMP_HEIGHT = 170
JUMP_DURATION = 460
START_LIVES = 3


@dataclass
class Obstacle:
    lane: int
    x: float
    y: float
    w: int = 56
    h: int = 70


@dataclass
class Coin:
    lane: int
    x: float
    y: float
    r: int = 14


class Subway2DGame:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Subway 2D Runner")
        self.root.resizable(False, False)

        self.canvas = tk.Canvas(root, width=WINDOW_W, height=WINDOW_H, bg="#111")
        self.canvas.pack()

        self.score = 0
        self.best = 0
        self.lives = START_LIVES
        self.running = True

        self.player_lane = 1
        self.player_x = LANES_X[self.player_lane]
        self.player_y = PLAYER_Y
        self.player_w = 48
        self.player_h = 66

        self.is_jumping = False
        self.jump_start_y = PLAYER_Y
        self.jump_elapsed = 0

        self.road_offset = 0
        self.obstacles: list[Obstacle] = []
        self.coins: list[Coin] = []

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
        self.running = True
        self.score = 0
        self.lives = START_LIVES
        self.player_lane = 1
        self.player_x = LANES_X[self.player_lane]
        self.player_y = PLAYER_Y
        self.is_jumping = False
        self.jump_elapsed = 0
        self.obstacles.clear()
        self.coins.clear()

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
        if not self.running:
            return
        self.player_lane = max(0, self.player_lane - 1)
        self.player_x = LANES_X[self.player_lane]

    def move_right(self, _event: tk.Event | None = None) -> None:
        if not self.running:
            return
        self.player_lane = min(2, self.player_lane + 1)
        self.player_x = LANES_X[self.player_lane]

    def jump(self, _event: tk.Event | None = None) -> None:
        if not self.running or self.is_jumping:
            return
        self.is_jumping = True
        self.jump_elapsed = 0

    def schedule_spawn(self) -> None:
        if not self.running:
            return

        lane = random.randint(0, 2)
        if random.random() < 0.72:
            self.obstacles.append(Obstacle(lane=lane, x=LANES_X[lane], y=-80))
        if random.random() < 0.45:
            coin_lane = random.randint(0, 2)
            self.coins.append(Coin(lane=coin_lane, x=LANES_X[coin_lane], y=-40))

        self.spawn_after_id = self.root.after(SPAWN_MS, self.schedule_spawn)

    def update_jump(self) -> None:
        if not self.is_jumping:
            self.player_y = PLAYER_Y
            return

        self.jump_elapsed += TICK_MS
        t = self.jump_elapsed / JUMP_DURATION

        if t >= 1:
            self.is_jumping = False
            self.player_y = PLAYER_Y
            return

        # Parabolic jump arc
        arc = 4 * t * (1 - t)
        self.player_y = PLAYER_Y - int(JUMP_HEIGHT * arc)

    def player_rect(self) -> tuple[float, float, float, float]:
        left = self.player_x - self.player_w / 2
        right = self.player_x + self.player_w / 2
        top = self.player_y - self.player_h / 2
        bottom = self.player_y + self.player_h / 2
        return left, top, right, bottom

    @staticmethod
    def intersects(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> bool:
        return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])

    def handle_collisions(self) -> None:
        p = self.player_rect()

        remaining_obstacles: list[Obstacle] = []
        took_hit = False

        for ob in self.obstacles:
            ob_rect = (
                ob.x - ob.w / 2,
                ob.y - ob.h / 2,
                ob.x + ob.w / 2,
                ob.y + ob.h / 2,
            )
            if self.intersects(p, ob_rect):
                if not took_hit:
                    self.lives -= 1
                    took_hit = True
                continue
            remaining_obstacles.append(ob)

        self.obstacles = remaining_obstacles

        remaining_coins: list[Coin] = []
        for coin in self.coins:
            c_rect = (coin.x - coin.r, coin.y - coin.r, coin.x + coin.r, coin.y + coin.r)
            if self.intersects(p, c_rect):
                self.score += 50
                continue
            remaining_coins.append(coin)

        self.coins = remaining_coins

        if self.lives <= 0:
            self.running = False
            self.best = max(self.best, self.score)

    def update_world(self) -> None:
        self.road_offset = (self.road_offset + GROUND_SPEED) % 60

        for ob in self.obstacles:
            ob.y += GROUND_SPEED
        for coin in self.coins:
            coin.y += GROUND_SPEED

        self.obstacles = [ob for ob in self.obstacles if ob.y < WINDOW_H + 100]
        self.coins = [coin for coin in self.coins if coin.y < WINDOW_H + 40]

        self.score += 2
        self.best = max(self.best, self.score)

    def draw(self) -> None:
        c = self.canvas
        c.delete("all")

        # Road
        c.create_rectangle(35, 0, WINDOW_W - 35, WINDOW_H, fill="#1d1d1d", outline="")
        c.create_line(35, 0, 35, WINDOW_H, fill="#666", width=3)
        c.create_line(WINDOW_W - 35, 0, WINDOW_W - 35, WINDOW_H, fill="#666", width=3)

        # Lane separators with scrolling effect
        for x in [157, 262]:
            y = -60 + self.road_offset
            while y < WINDOW_H + 60:
                c.create_line(x, y, x, y + 36, fill="#bbb", width=4)
                y += 60

        # Obstacles
        for ob in self.obstacles:
            c.create_rectangle(
                ob.x - ob.w / 2,
                ob.y - ob.h / 2,
                ob.x + ob.w / 2,
                ob.y + ob.h / 2,
                fill="#d63a3a",
                outline="#7b1d1d",
                width=3,
            )

        # Coins
        for coin in self.coins:
            c.create_oval(
                coin.x - coin.r,
                coin.y - coin.r,
                coin.x + coin.r,
                coin.y + coin.r,
                fill="#ffd447",
                outline="#9f7f18",
                width=2,
            )

        # Player
        c.create_rectangle(
            self.player_x - self.player_w / 2,
            self.player_y - self.player_h / 2,
            self.player_x + self.player_w / 2,
            self.player_y + self.player_h / 2,
            fill="#49a8ff",
            outline="#1f5f99",
            width=3,
        )

        # HUD
        c.create_text(12, 16, text=f"Score: {self.score}", anchor="w", fill="white", font=("Arial", 14, "bold"))
        c.create_text(12, 40, text=f"Best: {self.best}", anchor="w", fill="#ddd", font=("Arial", 12))
        c.create_text(WINDOW_W - 12, 16, text=f"Can: {self.lives}", anchor="e", fill="#ff7f7f", font=("Arial", 14, "bold"))
        c.create_text(WINDOW_W / 2, 16, text="A/D veya ←/→ | W/Space zıpla", anchor="n", fill="#cfcfcf", font=("Arial", 10))

        if not self.running:
            c.create_rectangle(70, 250, WINDOW_W - 70, 430, fill="#000", outline="#888", width=2)
            c.create_text(WINDOW_W / 2, 295, text="OYUN BİTTİ", fill="white", font=("Arial", 24, "bold"))
            c.create_text(WINDOW_W / 2, 336, text=f"Skor: {self.score}", fill="#ddd", font=("Arial", 16))
            c.create_text(WINDOW_W / 2, 365, text=f"En iyi: {self.best}", fill="#ddd", font=("Arial", 14))
            c.create_text(WINDOW_W / 2, 402, text="Tekrar başlamak için R", fill="#8ecbff", font=("Arial", 14, "bold"))

    def game_loop(self) -> None:
        if self.running:
            self.update_jump()
            self.update_world()
            self.handle_collisions()

        self.draw()
        self.loop_after_id = self.root.after(TICK_MS, self.game_loop)


def main() -> None:
    root = tk.Tk()
    Subway2DGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
