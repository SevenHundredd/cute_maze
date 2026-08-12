"""Maze generation logic based on a recursive backtracker algorithm.

This module defines the MazeGenerator class, a pydantic model that both
validates a maze configuration and generates the maze grid itself. Each
cell of the grid is stored as an integer bitmask of its closed walls
(NORTH=1, EAST=2, SOUTH=4, WEST=8).
"""
import random
from typing import Optional
try:
    from dotenv import dotenv_values
    from pydantic import (
        BaseModel, Field, model_validator, ValidationError,
        field_validator, ConfigDict,
    )
except ImportError as e:
    raise SystemExit(
        f"Required module not found: {e.name}. "
        "Please install the required modules using 'make install'."
    )

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

OPPOSITE_WALL = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST
}

MOVES = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0)
}

PATTERN_42 = [
    [1, 0, 0, 0, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 1, 1],
]


class MazeGenerator(BaseModel):
    """Pydantic model holding a maze configuration and its generated grid.

    Attributes:
        width: Number of cells on the horizontal axis (>= 3).
        height: Number of cells on the vertical axis (>= 3).
        entry: (x, y) coordinates of the maze entry point.
        exit: (x, y) coordinates of the maze exit point.
        output_file: Path of the file the maze will be exported to.
        perfect: If True, the maze has exactly one path between any
            two cells (no loops). If False, extra passages are opened.
        seed: Optional random seed for reproducible generation.
    """

    model_config = ConfigDict(validate_assignment=True)
    width: int = Field(..., ge=3, alias='WIDTH')
    height: int = Field(..., ge=3, alias='HEIGHT')
    entry: tuple[int, int] = Field(..., alias='ENTRY')
    exit: tuple[int, int] = Field(..., alias='EXIT')
    output_file: str = Field(default="maze.txt", alias='OUTPUT_FILE')
    perfect: bool = Field(default=True, alias='PERFECT')
    seed: Optional[int] = Field(default=None, alias='SEED')
    _grid: list[list[int]]
    _ignore: set[tuple[int, int]] = set()
    _allowed: bool = True
    _start_cell: tuple[int, int]
    _generation_path: list[tuple[int, int, int]] = []

    @field_validator('entry', 'exit', mode='before')
    @classmethod
    def validate_coordinates(cls, value: str) -> tuple[int, int]:
        """Parse entry/exit coordinates given as a tuple or a string.

        Args:
            value: Either a (x, y) tuple, or a string formatted as
                "x,y" (as read from the configuration file).

        Returns:
            The coordinates as a (x, y) tuple of integers.

        Raises:
            ValueError: If value is neither a valid tuple nor a
                parsable "x,y" string.
        """
        if isinstance(value, tuple) and len(value) == 2:
            return value
        elif isinstance(value, str):
            x_str, y_str = value.split(',')
            return (int(x_str), int(y_str))
        else:
            raise ValueError(
                "Coordinates must be a tuple of two integers "
                "or a string in the format 'x,y'."
            )

    @field_validator('output_file', mode='before')
    @classmethod
    def validate_output_file(cls, value: str) -> str:
        """Ensure the output file path is a non-empty string."""
        if isinstance(value, str) and value == '':
            return "maze.txt"
        elif isinstance(value, str):
            return value
        else:
            raise ValueError("Output file path must be a non-empty string.")

    @model_validator(mode="after")
    def validate_entry_and_exit(self) -> "MazeGenerator":
        """Check that entry and exit are in bounds and distinct.

        Returns:
            The validated MazeGenerator instance.

        Raises:
            ValueError: If entry or exit is out of bounds, or if they
                are equal.
        """
        entry = self.entry
        exit = self.exit
        width = self.width
        height = self.height

        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            input(f"Entry point {entry} is out of bounds for maze size" +
                  f" {width}x{height}.\n Entry point will be reset to (0, 0).")
            self.entry = (0, 0)
        if not (0 <= exit[0] < width and 0 <= exit[1] < height):
            input(f"Exit point {exit} is out of bounds for maze size " +
                  f"{width}x{height}.\n Exit point will" +
                  f" be reset to ({width - 1}, {height - 1}).")
            self.exit = (width - 1, height - 1)
        if entry == exit:
            input(f"Entry point {entry} and exit point {exit} " +
                  "are the same.\n Exit point will be reset " +
                  "to ({width - 1}, {height - 1}).")
            self.exit = (width - 1, height - 1)
        if self.output_file == '':
            input("Output file path is empty. It will be reset to 'maze.txt'.")
            self.output_file = "maze.txt"
        return self

    def get_pattern_42(self) -> None:
        """Compute which cells the centered "42" pattern occupies.

        Fills self._ignore with the coordinates of the cells forming
        the "42" pattern, centered on the grid. If the entry or exit
        point falls inside the pattern, the pattern is disabled for
        this generation (self._allowed is set to False and
        self._ignore is cleared).
        """
        pattern_height = len(PATTERN_42)
        pattern_width = len(PATTERN_42[0])
        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2
        if self.entry in self._ignore or self.exit in self._ignore:
            self._allowed = False
            self._ignore = set()
            return
        else:
            self._allowed = True
        for y in range(pattern_height):
            for x in range(pattern_width):
                if PATTERN_42[y][x] == 1:
                    self._ignore.add((start_x + x, start_y + y))

    def is_allowed(self) -> bool:
        """Return whether the "42" pattern was placed on the grid.

        Returns:
            False if the pattern was skipped because it overlapped
            the entry or exit point, True otherwise.
        """
        return self._allowed

    def get_grid(self) -> list[list[int]]:
        """Return the generated maze grid.

        Returns:
            A 2D list of integers, where each integer is a bitmask
            representing the closed walls of a cell.
        """
        return self._grid

    def get_ignore(self) -> set[tuple[int, int]]:
        """Return the set of coordinates occupied by the "42" pattern.

        Returns:
            A set of (x, y) tuples representing the cells that are
            part of the "42" pattern and should not be carved.
        """
        return self._ignore

    def get_generation_path(self) -> list[tuple[int, int, int]]:
        """Return the sequence of cells visited during maze generation.

        Returns:
            A list of (x, y) tuples representing the order in which
            cells were carved during the maze generation process.
        """
        return self._generation_path

    def set_generation_path(self, path: list[tuple[int, int, int]]) -> None:
        """Set the generation path to a new value.

        Args:
            path: A list of (x, y, direction) tuples representing
            the new generation path.
        """
        self._generation_path = path

    def get_start_cell(self) -> tuple[int, int]:
        """Return the starting cell used for maze generation.

        Returns:
            A tuple (x, y) representing the coordinates of the cell
            where the maze generation algorithm started carving.
        """
        return self._start_cell

    def add_pattern_42(self) -> None:
        """Carve the "42" pattern into the grid as fully closed cells."""
        self.get_pattern_42()
        if (self.height < 7 or self.width < 9):
            self._ignore = set()
            return
        for x, y in self._ignore:
            self._grid[y][x] = 15

    def generate_maze(self) -> None:
        """Carve a perfect maze using an iterative recursive backtracker.

        Starts from a random cell outside the "42" pattern and walks
        a randomized depth-first search over the grid, knocking down
        the wall between each cell and the next unvisited neighbour
        it moves to. Cells belonging to the "42" pattern are treated
        as already visited so the algorithm never carves through them.
        """
        seen = set()
        self._start_cell = (
            random.randint(0, self.width - 1),
            random.randint(0, self.height - 1),
        )
        while self._start_cell in self._ignore:
            self._start_cell = (
                random.randint(0, self.width - 1),
                random.randint(0, self.height - 1),
            )
        seen.update(self._ignore)
        stack = [self._start_cell]
        seen.add(self._start_cell)

        while stack:
            current_x, current_y = stack[-1]
            adjacent_cells = []
            for direction in (NORTH, EAST, SOUTH, WEST):
                move_x, move_y = MOVES[direction]
                new_x, new_y = current_x + move_x, current_y + move_y
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    if (new_x, new_y) not in seen:
                        adjacent_cells.append((new_x, new_y, direction))
            if adjacent_cells:
                new_x, new_y, direction = random.choice(adjacent_cells)
                self._generation_path.append((new_x, new_y, direction))
                self._grid[current_y][current_x] &= ~direction
                self._grid[new_y][new_x] &= ~OPPOSITE_WALL[direction]
                seen.add((new_x, new_y))
                stack.append((new_x, new_y))
            else:
                stack.pop()

    def imperfect_maze(self) -> None:
        """Open one extra wall on every dead-end cell to add loops.

        For each cell with exactly three closed walls (a dead end),
        knocks down one open-able wall shared with a neighbour that
        is not part of the "42" pattern, turning the perfect maze
        into one with multiple paths between some cells.
        """
        for y in range(self.height):
            for x in range(self.width):
                if bin(self._grid[y][x]).count('1') == 3:
                    if (x, y) in self._ignore:
                        continue
                    for direction in [NORTH, EAST, SOUTH, WEST]:
                        move_x, move_y = MOVES[direction]
                        new_x, new_y = x + move_x, y + move_y
                        in_bounds = (
                            0 <= new_x < self.width
                            and 0 <= new_y < self.height
                        )
                        if in_bounds and (new_x, new_y) not in self._ignore:
                            if self._grid[y][x] & direction:
                                self._grid[y][x] &= ~direction
                                opposite = OPPOSITE_WALL[direction]
                                self._grid[new_y][new_x] &= ~opposite
                                break

    def generate(self) -> None:
        """Generate (or regenerate) the maze grid for this configuration.

        Resets the grid to fully-walled cells, seeds the RNG if a
        seed is set, places the "42" pattern when the maze is large
        enough, carves the maze itself, and finally opens extra walls
        if the maze should not be perfect.
        """
        self._grid = [
            [15 for _ in range(self.width)] for _ in range(self.height)
        ]
        self._ignore = set()
        self._generation_path = []
        self._allowed = True
        if self.seed is not None:
            random.seed(self.seed)
        self.get_pattern_42()
        self.add_pattern_42()
        self.generate_maze()
        if self.perfect is False:
            self.imperfect_maze()


def load_config(config_path: str) -> MazeGenerator:
    """Load a maze configuration file and build a MazeGenerator from it.

    Args:
        config_path: Path to a "KEY=VALUE" configuration file (in the
            format accepted by python-dotenv).

    Returns:
        A validated MazeGenerator built from the file's content.

    Raises:
        SystemExit: If the file is missing, unreadable, or contains
            an invalid configuration.
    """
    try:
        data = dict(dotenv_values(config_path))
        return MazeGenerator.model_validate(data)
    except ValidationError as e:
        for error in e.errors():
            if error['type'] == 'value_error':
                msg = error['msg'].split(', ')[1]
                print(f"Invalid value in '{config_path}': {msg}")
            else:
                print(
                    f"Invalid configuration in '{config_path}': "
                    f"'{error['loc'][0]}' {error['msg']}"
                )
        raise SystemExit(
            "Program terminated due to invalid configuration."
        )
    except FileNotFoundError:
        raise SystemExit(f"Configuration file '{config_path}' not found.")
    except PermissionError:
        raise SystemExit(
            f"Permission denied when trying to read '{config_path}'."
        )
