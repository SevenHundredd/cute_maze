*This project has been created as part of the 42 curriculum by sterandr, ramandri.*


# A-Maze-ing

![A-Maze-ing](https://github.com/SevenHundredd/deway/blob/main/26vjo9.jpg?raw=true)

## Description

A-Maze-ing is a Python maze generator and solver. Given a small text
configuration file, it procedurally generates a grid-based maze, makes
sure it is fully connected, embeds a hidden "42" pattern when the maze
is large enough, and displays the result live in the terminal with an
animated reveal.

From the interactive menu you can:

- Show or hide the shortest path between the entry and the exit.
- Regenerate the maze (optionally stepping through seeds).
- Change the colour theme.
- Export the maze and its solution to a text file.
- Change the configuration of the maze
- Edit the current configuration (size, entry/exit, seed, perfect flag)
  without restarting the program.

The maze generation, solving and export logic lives in a standalone,
pip-installable package (`mazegen`) so it can be reused in other
projects independently of the terminal interface.

## Instructions

### Requirements

- Python 3.10+
- `make`

### Install

```sh
make install
```

Installs the dependencies listed in `requirements.txt`
(`pydantic`, `python-dotenv`, `flake8`, `mypy`, `build`).

### Run

```sh
make run
```

Equivalent to:

```sh
python3 a_maze_ing.py config.txt
```

`config.txt` is the default configuration file provided at the root of
this repository. You can pass any other configuration file as the
argument instead.

### Other Makefile targets

| Target        | Description                                                |
|---------------|--------------------------------------------------------------|
| `debug`       | Runs the program under `pdb`.                                |
| `clean`       | Removes caches and build artifacts (`__pycache__`, etc).     |
| `lint`        | Runs `flake8 .` and `mypy .` with the mandatory subject flags. |
| `lint-strict` | Runs `flake8 .` and `mypy --strict .`.                       |
| `build`       | Builds a wheel and sdist for the `mazegen` package.          |
## Configuration file format

One `KEY=VALUE` pair per line. Lines starting with `#` are ignored.

| Key           | Description                          | Example        |
|---------------|---------------------------------------|-----------------|
| `WIDTH`       | Maze width, in cells (>= 3)           | `WIDTH=10`      |
| `HEIGHT`      | Maze height, in cells (>= 3)          | `HEIGHT=10`     |
| `ENTRY`       | Entry coordinates `x,y`               | `ENTRY=0,0`     |
| `EXIT`        | Exit coordinates `x,y`                | `EXIT=8,6`      |
| `OUTPUT_FILE` | Output filename                       | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | Whether the maze has a single unique path between any two cells | `PERFECT=True` |
| `SEED`        | *(optional)* Integer seed for reproducible generation | `SEED=45` |

Example (`config.txt`):

```
WIDTH=10
HEIGHT=10
ENTRY=0,0
EXIT=8,6
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=45
```

## Maze generation algorithm

The maze is carved with an **iterative recursive backtracker**
(randomized depth-first search using an explicit stack instead of
Python recursion): from a random starting cell, the algorithm
repeatedly moves to a random unvisited neighbour, knocking down the
wall between the two cells, and backtracks through the stack whenever
a cell has no unvisited neighbour left.

When `PERFECT=False`, an extra pass (`imperfect_maze`) opens one
additional wall on every dead-end cell, introducing loops and multiple
possible paths between some cells.

The shortest path (used for the "Show Solution" feature and for the
output file) is computed separately with a **breadth-first search**
(`MazeSolver.solve`), which guarantees the shortest path in an
unweighted grid.

### Why I chose this algorithm?
We chose the recursive backtracker because it is simple to implement, and it produces mazes with long, winding passages and few dead ends, which is desirable for a maze.
As for the imperfect maze generation, we chose to open one additional wall on every dead-end cell because it is a simple and effective way to introduce loops and multiple possible paths between some cells, it also prevents the case of open wide 3*3 areas and the maze have more aesthetic appeal.

## Reusable part

The `mazegen` package (`mazegen/`) is entirely independent from the
interactive terminal program (`a_maze_ing.py`) and can be installed
and reused in other projects.

### Building and installing the package

```sh
pip install build
python3 -m build --wheel --sdist -o dist
pip install dist/mazegen-1.0.0-py3-none-any.whl
```

A pre-built wheel, `mazegen-1.0.0-py3-none-any.whl`, is also provided
at the root of this repository.

### Basic usage

```python
from mazegen import MazeGenerator, load_config, MazeSolver, export_maze

# Build a generator directly...
generator = MazeGenerator(WIDTH=10, HEIGHT=10, ENTRY="0,0", EXIT="8,6")
# ...or load one from a KEY=VALUE configuration file
generator = load_config("config.txt")

generator.generate()

# Access the generated structure: one wall-bitmask integer per cell
# (bit 0=North, 1=East, 2=South, 3=West; 1 = wall closed)
grid = generator._grid

# Access a solution: shortest path from entry to exit
solver = MazeSolver(grid, generator.entry, generator.exit)
path = solver.solve()  # list[tuple[int, int]]

# Export the maze and its solution using the subject's text format
export_maze(generator.output_file, grid, path)
```

### What's reusable

- `MazeGenerator` (in `mazegen/generator.py`) — the maze generation
  class itself, plus `load_config` to build one from a config file.
- `MazeSolver` (in `mazegen/solver.py`) — BFS/bidirectional-BFS
  pathfinding over any compatible wall-bitmask grid.
- `export_maze` (in `mazegen/exporter.py`) — writes a grid and a path
  to the subject's text output format.
- `maze_frame`, `animated_frame`, `clear_screen`, `THEMES` (in
  `mazegen/custom_tools.py`) — optional terminal rendering helpers.

Only `a_maze_ing.py` (the interactive menu) is specific to this
project and not part of the reusable package.

## Bonuses implemented

- **Animation during maze generation**: `animated_frame` reveals the
  maze cell by cell in random order before the interactive menu
  appears (see `mazegen/custom_tools.py`).
- A second solving strategy, `MazeSolver.bidirectional_solve`, is
  available in the reusable package alongside the standard BFS
  `solve`, though the terminal program currently only calls `solve`.

## Team and project management
- **Team members and roles**: sterandr and ramandri
- **Planning**: 
  - **Initial design**: sterandr
  - **Maze generation and solving logic**: sterandr
  - **Terminal interface**: ramandri
  - **Configuration file parsing**: sterandr
  - **Export feature**: ramandri
  - **Testing and debugging**: both
- **What worked well / what could be improved**
  - **What worked well**: the maze generation and solving logic was
    implemented and tested in isolation from the terminal interface,
    which made it easier to reason about and debug.
  - **What could be improved**: the terminal interface was written
    in a single file, which made it harder to test and debug. It could
    be split into multiple modules to improve maintainability.
- **Specific tools used**: `pydantic`, `python-dotenv`

## Resources

- [Maze generation algorithm — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm) — overview of recursive backtracker, Prim's and Kruskal's algorithms.
- [Pydantic documentation](https://docs.pydantic.dev/) — used for configuration validation (`MazeGenerator` is a `pydantic.BaseModel`).
- [python-dotenv documentation](https://saurabh-kumar.com/python-dotenv/) — used to parse the `KEY=VALUE` configuration file.

### AI usage

AI was used to generate DOCSTRING comments for all functions and classes, and to suggest some refactoring of the terminal interface code. It was also used to help generate this README file
