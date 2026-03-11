import os
import random
from typing import List, Tuple

GRID_SIZE = 10
DIRECTIONS = {
    "w": (-1, 0),
    "s": (1, 0),
    "a": (0, -1),
    "d": (0, 1),
}


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def spawn_apple(snake: List[Tuple[int, int]]) -> Tuple[int, int]:
    while True:
        apple = (random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1))
        if apple not in snake:
            return apple


def draw_board(snake: List[Tuple[int, int]], apple: Tuple[int, int], score: int) -> None:
    print(f"Skor: {score}")
    print("+" + "--" * GRID_SIZE + "+")

    for row in range(GRID_SIZE):
        line = "|"
        for col in range(GRID_SIZE):
            cell = (row, col)
            if cell == snake[0]:
                line += "🟩"
            elif cell in snake:
                line += "🟢"
            elif cell == apple:
                line += "🍎"
            else:
                line += "⬛"
        line += "|"
        print(line)

    print("+" + "--" * GRID_SIZE + "+")
    print("Hareket: W/A/S/D (çıkış: Q)")


def next_head(head: Tuple[int, int], move: str) -> Tuple[int, int]:
    dr, dc = DIRECTIONS[move]
    return head[0] + dr, head[1] + dc


def main() -> None:
    snake: List[Tuple[int, int]] = [(5, 5), (5, 4), (5, 3)]
    apple = spawn_apple(snake)
    direction = "d"
    score = 0

    while True:
        clear_screen()
        draw_board(snake, apple, score)

        move = input("> ").strip().lower()
        if move == "q":
            print("Oyun kapatıldı.")
            break
        if move in DIRECTIONS:
            if (direction, move) not in {("w", "s"), ("s", "w"), ("a", "d"), ("d", "a")}:
                direction = move

        new_head = next_head(snake[0], direction)

        # Duvara çarpma
        if not (0 <= new_head[0] < GRID_SIZE and 0 <= new_head[1] < GRID_SIZE):
            clear_screen()
            print(f"Duvara çarptın! Oyun bitti. Skor: {score}")
            break

        # Kendine çarpma
        if new_head in snake:
            clear_screen()
            print(f"Kendine çarptın! Oyun bitti. Skor: {score}")
            break

        snake.insert(0, new_head)

        if new_head == apple:
            score += 1
            apple = spawn_apple(snake)
        else:
            snake.pop()


if __name__ == "__main__":
    main()
