from .generator import MazeGenerator
import subprocess
import sys
#custom themes need more themes
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
    animated_grid = []

    animated_grid.append(theme["wall"] * (width * 2 + 1))
    for y in range(height):
        animated_grid.append(theme["wall"])
        for x in range(width):
            pos = (x, y)
            if pos == entry:
                animated_grid.append(theme['entry'])
            elif pos == exit:
                animated_grid.append(theme['exit'])
            elif pos in path_set:
                animated_grid.append(theme['path'])
            elif pos in pattern_42:
                animated_grid.append(theme['pattern_42'])
            else:
                animated_grid.append(theme['space'])
            animated_grid.append(theme["wall"] if grid[y][x] & 2 or (x == width - 1) else theme["space"])

        animated_grid.append(theme["wall"])
        for x in range(width):
            animated_grid.append(theme["wall"] if grid[y][x] & 4 or (y == height - 1) else theme["space"])
        animated_grid.append(theme["wall"])

    print('\n'.join(animated_grid))
