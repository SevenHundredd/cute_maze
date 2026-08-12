"""Terminal display helpers: themes, static frames and animation.

Renders a MazeGenerator's grid as coloured ASCII art in the terminal,
including the entry, exit, "42" pattern and an optional solution path.
"""
import random
import subprocess
import sys
from time import sleep

from .generator import MazeGenerator, OPPOSITE_WALL, MOVES

RESET = "\033[0m"

RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
PURPLE = "\033[35m"

THEMES = {
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


def maze_frame(
    generator: MazeGenerator,
    grid: list[list[int]],
    path: list[tuple[int, int]],
    theme_name: str,
) -> None:
    """Print one static frame of the maze to the terminal.

    Args:
        generator: The MazeGenerator holding the maze configuration
            (entry, exit, "42" pattern cells, dimensions).
        grid: The grid to render (may differ from grid,
            e.g. a partially revealed grid during animation).
        path: Cells to highlight as the current solution path.
        theme_name: Key into THEMES selecting the colours/symbols
            used to draw walls, spaces, entry, exit and path.
    """
    print(
        f"Size: {generator.width}x{generator.height}, "
        f"Entry: {generator.entry}, Exit: {generator.exit}, "
        f"Perfect: {generator.perfect}, Seed: {generator.seed}"
    )
    theme = THEMES[theme_name]
    path_set = set(path)
    path_set.add(generator.exit)

    width = generator.width
    height = generator.height
    entry = generator.entry
    exit = generator.exit
    entry_or_exit_ignored = (
        generator.entry in generator._ignore
        or generator.exit in generator._ignore
    )
    pattern_42 = set() if entry_or_exit_ignored else generator._ignore

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
                row += theme["space"]
            if grid[y][x] & 2 or (x == width - 1):
                row += theme["wall"]
            elif (x, y) in path_set and (x + 1, y) in path_set:
                row += theme["path"]
            else:
                row += theme["space"]
        print(row)

        bottom_row = theme["wall"]
        for x in range(width):
            if grid[y][x] & 4 or (y == height - 1):
                bottom_row += theme["wall"]
            elif (x, y) in path_set and (x, y + 1) in path_set:
                bottom_row += theme["path"]
            else:
                bottom_row += theme["space"]
            bottom_row += theme["wall"]

        print(bottom_row)


def animated_frame(
    generator: MazeGenerator,
    grid: list[list[int]],
    path: list[tuple[int, int]],
    theme_name: str, delay: float = 0.05
) -> None:
    """Reveal the maze cell by cell, in random order, as an animation.

    Starts from a fully-walled grid and, for each unseen cell in
    random order, copies its real walls from grid and redraws the
    whole frame, producing a "maze appearing" animation effect.

    Args:
        generator: The MazeGenerator holding the maze configuration.
        grid: The fully generated grid to reveal.
        path: Cells to highlight as the current solution path.
        theme_name: Key into THEMES selecting the colours/symbols
            used to draw the maze.
    """
    start_grid = [
        [15 for _ in range(generator.width)]
        for _ in range(generator.height)
    ]
    seen: set[tuple[int, int]] = set()
    while len(seen) < generator.height * generator.width:
        x = random.randint(0, generator.width - 1)
        y = random.randint(0, generator.height - 1)
        if (x, y) not in seen:
            seen.add((x, y))
            start_grid[y][x] = grid[y][x]
            maze_frame(generator, start_grid, path, theme_name)
            sleep(delay)
            clear_screen()
        else:
            continue


def animate_dfs_generation(
    generator: MazeGenerator,
    theme_name: str = "1",
    delay: float = 0.05,
) -> None:
    """
    Visualizes DFS (Recursive Backtracker) maze generation step-by-step:
    1. Starts with all walls up (15).
    2. Highlights the recursion stack in real-time as it carves passages.
    3. Backtracks by shrinking the stack when it hits a dead end.
    """
    grid = [[15 for _ in range(generator.width)]
            for _ in range(generator.height)]
    ignore_set = generator.get_ignore()

    start_cell = generator.get_start_cell()
    seen = set(ignore_set)
    seen.add(start_cell)
    stack = [start_cell]
    path = generator.get_generation_path().copy()

    while stack:
        clear_screen()
        maze_frame(generator, grid, stack, theme_name)
        sleep(delay)
        current_x, current_y = stack[-1]
        adjacent_cells = []
        for direction in MOVES:
            move_x, move_y = MOVES[direction]
            new_x, new_y = current_x + move_x, current_y + move_y
            if 0 <= new_x < generator.width and 0 <= new_y < generator.height:
                if (new_x, new_y) not in seen:
                    adjacent_cells.append((new_x, new_y, direction))

        if adjacent_cells:
            new_x, new_y, direction = path.pop(0)
            grid[current_y][current_x] &= ~direction
            grid[new_y][new_x] &= ~OPPOSITE_WALL[direction]
            seen.add((new_x, new_y))
            stack.append((new_x, new_y))
        else:
            stack.pop()

    clear_screen()
    maze_frame(generator, grid, [], theme_name)


def animate_path(
    generator: MazeGenerator,
    path: list[tuple[int, int]],
    theme_name: str = "1",
    delay: float = 0.05,
) -> None:
    """Animates a pre-calculated solution path step-by-step."""
    head = [path[0]]
    for pos in path:
        maze_frame(
            generator, generator.get_grid(), head, theme_name
        )
        sleep(delay)
        head.append(pos)
        if pos != path[-1]:
            clear_screen()


def animate_bfs(
    generator: MazeGenerator,
    theme_name: str = "1",
    delay: float = 0.05,
) -> None:
    """
    Visualizes BFS step-by-step:
    1. Shows the expanding search wave (level-by-level) using visited cells.
    2. Renders the final shortest path once the exit is hit.
    """
    grid = generator.get_grid()
    entry = generator.entry
    exit_pos = generator.exit

    queue = [(entry, [entry])]
    visited = {entry}
    final_path = []

    while queue:
        (x, y), path = queue.pop(0)

        clear_screen()
        maze_frame(generator, grid, list(visited), theme_name)
        sleep(delay)

        if (x, y) == exit_pos:
            final_path = path
            break

        for direction, (moves_x, moves_y) in MOVES.items():
            if not (grid[y][x] & direction):
                new_x, new_y = x + moves_x, y + moves_y
                if (0 <= new_x < generator.width and
                   0 <= new_y < generator.height):
                    if ((new_x, new_y) not in visited and
                       (new_x, new_y) not in generator.get_ignore()):
                        visited.add((new_x, new_y))
                        queue.append(((new_x, new_y), path + [(new_x, new_y)]))
    if final_path:
        sleep(delay)
        clear_screen()
        maze_frame(generator, grid, final_path, theme_name)
