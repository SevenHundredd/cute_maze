import random
from typing import Optional, Any
try:
    from dotenv import dotenv_values
    from pydantic import BaseModel, Field, model_validator, ValidationError, field_validator, ConfigDict
except ImportError as e:
    raise SystemExit(f"Required module not found: {e.name}. Please install the required modules using 'make install'.")

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

    @field_validator('entry', 'exit', mode='before')
    @classmethod
    def validate_coordinates(cls, value: str) -> tuple[int, int]:
        if isinstance(value, tuple) and len(value) == 2:
            return value
        elif isinstance(value, str):
            return tuple(map(int, value.split(',')))
        else: 
            raise ValueError("Coordinates must be a tuple of two integers or a string in the format 'x,y'.")

    
    @model_validator(mode="after")
    def validate_entry_and_exit(self) -> "MazeGenerator":
        entry = self.entry
        exit = self.exit
        width = self.width
        height = self.height

        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            raise ValueError("Entry point is out of bounds.")
        if not (0 <= exit[0] < width and 0 <= exit[1] < height):
            raise ValueError("Exit point is out of bounds.")
        if entry == exit:
            raise ValueError("Entry and exit points cannot be the same.")

        return self


    def get_pattern_42(self) -> None:
        pattern_height = len(PATTERN_42)
        pattern_width = len(PATTERN_42[0])
        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2
        if self.entry in self._ignore or self.exit in self._ignore:
            self._allowed = False       
            self._ignore = set()
            return
        for y in range(pattern_height):
            for x in range(pattern_width):
                if PATTERN_42[y][x] == 1:
                    self._ignore.add((start_x + x, start_y + y))

    def is_allowed(self) -> bool:
        return self._allowed

    def add_pattern_42(self) -> None:
        self.get_pattern_42()
        for x, y in self._ignore:
            self._grid[y][x] = 15

    def generate_maze(self) -> None:
        seen = set()
        start_cell = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        while start_cell in self._ignore:
            start_cell = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        seen.update(self._ignore)
        stack = [start_cell]
        seen.add(start_cell)

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
                self._grid[current_y][current_x] &= ~direction
                self._grid[new_y][new_x] &= ~OPPOSITE_WALL[direction]
                seen.add((new_x, new_y))
                stack.append((new_x, new_y))
            else:
                stack.pop()

    def imperfect_maze(self) -> None:
        for y in range(self.height):
            for x in range(self.width):
                if bin(self._grid[y][x]).count('1') == 3:
                    if (x, y) in self._ignore:
                        continue
                    for direction in [NORTH, EAST, SOUTH, WEST]:
                        move_x, move_y = MOVES[direction]
                        new_x, new_y = x + move_x, y + move_y
                        if 0 <= new_x < self.width and 0 <= new_y < self.height:
                            if (new_x, new_y) not in self._ignore:
                                if self._grid[y][x] & direction:
                                    self._grid[y][x] &= ~direction
                                    self._grid[new_y][new_x] &= ~OPPOSITE_WALL[direction]
                                    break

    def generate(self) -> None:
        self._grid = [[15 for _ in range(self.width)] for _ in range(self.height)]
        self._ignore = set()
        if self.seed is not None:
            random.seed(self.seed)
        self.get_pattern_42()
        if (self.height >= 7 and self.width >= 9):
            self.add_pattern_42()
        self.generate_maze()
        if self.perfect is False:
            self.imperfect_maze()



def load_config(config_path: str) -> MazeGenerator:
    try:
        data = dict(dotenv_values(config_path))
        return MazeGenerator(**data)
    except ValidationError as e:
        for error in e.errors():
            if error['type'] == 'value_error':
                print(f"Invalid value in '{config_path}': {error['msg'].split(', ')[1]}")
            else:
                print(f"Invalid configuration in '{config_path}': '{error['loc'][0]}' {error['msg']}")
        raise SystemExit("Program terminated due to invalid configuration.")
    except FileNotFoundError:
        raise SystemExit(f"Configuration file '{config_path}' not found.",)
    except PermissionError:
        raise SystemExit(f"Permission denied when trying to read '{config_path}'.")