from .generator import MazeGenerator
import subprocess
import sys

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

def maze_frame(generator: MazeGenerator, path: list[tuple[int, int]], theme_name: str) -> None:
    theme = THEMES[theme_name]
    path_set = set(path)

    grid = generator.grid
    width = generator.width
    height = generator.height
    entry = generator.entry
    exit = generator.exit
    pattern_42 = generator.ignore

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

