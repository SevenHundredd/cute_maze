from inspect import stack
import random
from mazegen.config import MazeConfig
from time import sleep
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
    [1, 0, 1, 0, 1, 1, 1],
    [1, 0, 1, 0, 0, 0, 1],
    [1, 1, 1, 0, 1, 1, 1],
    [0, 0, 1, 0, 1, 0, 0],
    [0, 0, 1, 0, 1, 1, 1],
]

class MazeGenerator:
    def __init__(self, config: MazeConfig):
        self.config = config
        self.width = config.width
        self.height = config.height
        self.entry = config.entry
        self.exit = config.exit
        self.grid = [[15 for _ in range(self.width)] for _ in range(self.height)]
        self.ignore = set()


    def add_pattern_42(self) -> None:
        pattern_height = len(PATTERN_42)
        pattern_width = len(PATTERN_42[0])

        if pattern_height-1 >= self.height or pattern_width-1 >= self.width:
            print("Pattern 42 is too large to fit in the maze.")
            return
        start_x = (self.width - pattern_width) // 2
        start_y = (self.height - pattern_height) // 2
        for y in range(pattern_height):
            from a_maze_ing import maze_frame, clear_screen
            for x in range(pattern_width):
                if (start_x + x, start_y + y) == self.entry or (start_x + x, start_y + y) == self.exit:
                    print(f"Entry or exit found at ({start_x + x}, {start_y + y})")
                    self.grid = [[15 for _ in range(self.width)] for _ in range(self.height)]    
                    return
                if PATTERN_42[y][x] == 1:
                    self.grid[start_y + y][start_x + x] = 15
                    self.ignore.add((start_x + x, start_y + y))
                else:
                    self.grid[start_y + y][start_x + x] = 15
                try:
                    print(f"Entry: {self.entry}, Exit: {self.exit}, Perfect: {self.config.perfect}, Seed: {self.config.seed}")
                    maze_frame(self, [], "3")
                    sleep(0.05)
                    clear_screen()
                except KeyboardInterrupt:
                    raise SystemExit("\nProgram terminated due to user interruption.")
    
    def generate_maze(self) -> None:
        from a_maze_ing import maze_frame, clear_screen
        seen = set()
        start_cell = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        while start_cell in self.ignore:
            start_cell = (random.randint(0, self.width - 1), random.randint(0, self.height - 1))
        seen.update(self.ignore)
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
                self.grid[current_y][current_x] &= ~direction
                self.grid[new_y][new_x] &= ~OPPOSITE_WALL[direction]
                seen.add((new_x, new_y))
                stack.append((new_x, new_y))
            else:
                stack.pop()
            try:
                print(f"Entry: {self.entry}, Exit: {self.exit}, Perfect: {self.config.perfect}, Seed: {self.config.seed}")
                maze_frame(self, [], "3")
                sleep(0.005)
                clear_screen()
            except KeyboardInterrupt:
                raise SystemExit("\nProgram terminated due to user interruption.")

    def imperfect_maze(self) -> None:
        from a_maze_ing import maze_frame, clear_screen
        for y in range(self.height):
            for x in range(self.width):
                if random.randint(0,1):
                    if (x, y) in self.ignore:
                        continue
                    direction = random.choice([NORTH, EAST, SOUTH, WEST])
                    move_x, move_y = MOVES[direction]
                    new_x, new_y = x + move_x, y + move_y
                    if 0 <= new_x < self.width and 0 <= new_y < self.height:
                        if (new_x, new_y) not in self.ignore:
                            if self.grid[y][x] & direction:
                                self.grid[y][x] &= ~direction
                                self.grid[new_y][new_x] &= ~OPPOSITE_WALL[direction]
            try:
                print(f"Entry: {self.entry}, Exit: {self.exit}, Perfect: {self.config.perfect}, Seed: {self.config.seed}")
                maze_frame(self, [], "3")
                sleep(0.05)
                clear_screen()
            except KeyboardInterrupt:
                raise SystemExit("\nProgram terminated due to user interruption.")

    def generate(self) -> None:
        if self.config.seed is not None:
            random.seed(self.config.seed)
        self.add_pattern_42()
        self.generate_maze()
        if self.config.perfect is False:
            self.imperfect_maze()