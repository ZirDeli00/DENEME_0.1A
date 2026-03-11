#!/usr/bin/env python3
"""Simple Subway Surfers-style endless runner for terminal/CMD."""

from __future__ import annotations

import os
import random
import sys
import time
from dataclasses import dataclass

LANES = 3
WIDTH = 21
HEIGHT = 18
FRAME_TIME = 0.11
OBSTACLE_SPAWN_RATE = 0.36
COIN_SPAWN_RATE = 0.28


@dataclass
class Runner:
    lane: int = 1
    jump_timer: int = 0

    @property
    def is_jumping(self) -> bool:
        return self.jump_timer > 0


@dataclass
class Item:
    lane: int
    y: int
    kind: str  # "obstacle" | "coin"


class Keyboard:
    """Cross-platform non-blocking key reader."""

    def __init__(self) -> None:
        self._impl = None
        if os.name == "nt":
            import msvcrt  # type: ignore

            self._impl = ("win", msvcrt)
        else:
            if not sys.stdin.isatty():
                self._impl = None
                return

            import select
            import termios
            import tty

            self._impl = ("unix", select, termios, tty)
            self.fd = sys.stdin.fileno()
            self.old = termios.tcgetattr(self.fd)
            tty.setcbreak(self.fd)

    def close(self) -> None:
        if self._impl and self._impl[0] == "unix":
            _, _, termios, _ = self._impl
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def get_key(self) -> str | None:
        if not self._impl:
            return None
        if self._impl[0] == "win":
            _, msvcrt = self._impl
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch in (b"\xe0", b"\x00"):
                    extra = msvcrt.getch()
                    arrows = {b"K": "left", b"M": "right", b"H": "up"}
                    return arrows.get(extra, "")
                mapping = {b"a": "left", b"d": "right", b"w": "up", b"q": "quit", b" ": "up"}
                return mapping.get(ch.lower(), "")
            return None

        _, select, *_ = self._impl
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        if ready:
            ch = sys.stdin.read(1)
            mapping = {"a": "left", "d": "right", "w": "up", "q": "quit", " ": "up"}
            return mapping.get(ch.lower(), "")
        return None


def clear() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def lane_to_x(lane: int) -> int:
    return 2 + lane * 6


def draw(runner: Runner, items: list[Item], score: int, best: int) -> None:
    canvas = [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for y in range(HEIGHT):
        for lane in range(LANES):
            x = lane_to_x(lane)
            canvas[y][x] = "|"

    for item in items:
        if 0 <= item.y < HEIGHT:
            x = lane_to_x(item.lane)
            canvas[item.y][x] = "X" if item.kind == "obstacle" else "$"

    player_y = HEIGHT - 2 if not runner.is_jumping else HEIGHT - 4
    canvas[player_y][lane_to_x(runner.lane)] = "A" if not runner.is_jumping else "^"

    lines = ["Subway CMD Runner (A/D: lane, W/Space: jump, Q: quit)"]
    lines.append(f"Score: {score}   Best: {best}")
    lines.append("+" + "-" * WIDTH + "+")
    for row in canvas:
        lines.append("|" + "".join(row) + "|")
    lines.append("+" + "-" * WIDTH + "+")
    print("\n".join(lines))


def update_items(items: list[Item]) -> None:
    for item in items:
        item.y += 1
    items[:] = [i for i in items if i.y < HEIGHT]


def spawn(items: list[Item]) -> None:
    if random.random() < OBSTACLE_SPAWN_RATE:
        items.append(Item(lane=random.randint(0, LANES - 1), y=0, kind="obstacle"))
    if random.random() < COIN_SPAWN_RATE:
        items.append(Item(lane=random.randint(0, LANES - 1), y=0, kind="coin"))


def collisions(runner: Runner, items: list[Item]) -> tuple[bool, int]:
    gain = 0
    danger_y = HEIGHT - 2
    kept: list[Item] = []

    for item in items:
        if item.lane == runner.lane and item.y == danger_y:
            if item.kind == "coin":
                gain += 25
                continue
            if not runner.is_jumping:
                return True, gain
        kept.append(item)

    items[:] = kept
    return False, gain


def play(best_score: int) -> int:
    runner = Runner()
    items: list[Item] = []
    score = 0
    keyboard = Keyboard()

    try:
        while True:
            key = keyboard.get_key()
            if key == "left":
                runner.lane = max(0, runner.lane - 1)
            elif key == "right":
                runner.lane = min(LANES - 1, runner.lane + 1)
            elif key == "up" and not runner.is_jumping:
                runner.jump_timer = 2
            elif key == "quit":
                return best_score

            update_items(items)
            spawn(items)

            dead, gain = collisions(runner, items)
            if dead:
                clear()
                draw(runner, items, score, max(best_score, score))
                print("\nGAME OVER! Devam etmek için Enter, çıkmak için Q.")
                choice = input().strip().lower()
                if choice == "q":
                    return max(best_score, score)
                return max(best_score, score)

            if runner.jump_timer > 0:
                runner.jump_timer -= 1

            score += 10 + gain
            best_score = max(best_score, score)

            clear()
            draw(runner, items, score, best_score)
            time.sleep(FRAME_TIME)
    finally:
        keyboard.close()


def main() -> None:
    random.seed()

    if not sys.stdin.isatty():
        print("Bu oyun interaktif terminal/CMD gerektirir.")
        return

    best = 0
    while True:
        best = play(best)
        print("\nTekrar oynamak için Enter, tamamen çıkmak için Q.")
        if input().strip().lower() == "q":
            break


if __name__ == "__main__":
    main()
