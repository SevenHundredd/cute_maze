from .generator import MazeGenerator
import subprocess
import sys
from time import sleep

RESET = "\033[0m"

RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
PURPLE = "\033[35m"

THEMES={
    "1": {
        "wall": f"{PURPLE}██{RESET}",
        "space": "  ",
        "entry": f"{GREEN}██{RESET}",
        "exit": f"{RED}██{RESET}",
        "path": f"{YELLOW}██{RESET}",
        "pattern_42": f"{CYAN}██{RESET}"
    },
    "2": {
        "wall": f"{CYAN}██{RESET}",
        "space": "  ",
        "entry": f"{GREEN}██{RESET}",
        "exit": f"{RED}██{RESET}",
        "path": f"{YELLOW}██{RESET}",
        "pattern_42": f"{RED}██{RESET}"
    },
    "3": {
        "wall": "🧱",
        "space": "  ",
        "entry": f"{GREEN}██{RESET}",
        "exit": f"{RED}██{RESET}",
        "path": f"{YELLOW}██{RESET}",
        "pattern_42": "🟦"
    },
    "4": {
        "wall": "██",
        "space": "  ",
        "entry": f"{GREEN}██{RESET}",
        "exit": f"{RED}██{RESET}",
        "path": f"{YELLOW}██{RESET}",
        "pattern_42": "  "
    }
}

def clear_screen() -> None:
    """Clears the terminal screen."""
    if sys.platform.startswith('win'):
        subprocess.run(['cls'], check=True, shell=True)
    else:
        subprocess.run(['clear'], check=True, shell=True)

def maze_frame(generator: MazeGenerator, grid: list[list[int]], path: list[tuple[int, int]], theme_name: str) -> None:
    print(f"Entry: {generator.entry}, Exit: {generator.exit}, Perfect: {generator.config.perfect}, Seed: {generator.config.seed}")
    theme = THEMES[theme_name]
    path_set = set(path)

    width = generator.width
    height = generator.height
    entry = generator.entry
    exit = generator.exit
    pattern_42 = set() if generator.entry in generator.ignore or generator.exit in generator.ignore else generator.ignore

    print(theme["wall"] * (width * 2 + 1))
    for y in range(height):
        row = theme["wall"]
        for x in range(width):
            pos = (x, y)
            if pos == entry:
                row += theme['entry']
            elif pos == exit:
                row += theme['exit']
            elif pos in path_set:
                row += theme['path']
            elif pos in pattern_42:
                row += theme['pattern_42']
            else:
                row += theme['space']
            row += theme["wall"] if grid[y][x] & 2 or (x == width - 1) else theme["space"]
        print(row)

        bottom_row = theme["wall"]
        for x in range(width):
            bottom_row += theme["wall"] if grid[y][x] & 4 or (y == height - 1) else theme["space"]
            bottom_row += theme["wall"]

        print(bottom_row)

def animated_frame(generator: MazeGenerator, grid: list[list[int]], path: list[tuple[int, int]], theme_name: str) -> None:
    start_grid = [[15 for _ in range(generator.width)] for _ in range(generator.height)]
    for y in range(generator.height):
        for x in range(generator.width):
            start_grid[y][x] = grid[y][x]
            maze_frame(generator, start_grid, path, theme_name)
            sleep(0.05)
            clear_screen()

