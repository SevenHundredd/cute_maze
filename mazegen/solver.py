NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

MOVES = {
    SOUTH: (0, 1, SOUTH),
    NORTH: (0, -1, NORTH),
    EAST: (1, 0, EAST),
    WEST: (-1, 0, WEST)
}


class MazeSolver:
    def __init__(self, grid: list[list[int]], entry: tuple[int, int], exit: tuple[int, int]):
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.height = len(grid)
        self.width = len(grid[0])

    def solve(self) -> list[tuple[int, int]]:
        queue = [(self.entry[0], self.entry[1], [self.entry])]
        seen = {self.entry}

        while queue:
            x, y , path = queue.pop(0)
            if (x, y) == self.exit:
                return path

            for direction in MOVES:
                move_x, move_y, wall = MOVES[direction]
                new_x, new_y = x + move_x, y + move_y
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    if not (self.grid[y][x] & wall) and (new_x, new_y) not in seen:
                        seen.add((new_x, new_y))
                        queue.append((new_x, new_y, path + [(new_x, new_y)]))


    def bidirectional_solve(self) -> list[tuple[int, int]]:
        queue_start = [(self.entry[0], self.entry[1], [self.entry])]
        queue_end = [(self.exit[0], self.exit[1], [self.exit])]
        seen_start = {self.entry: [self.entry]}
        seen_end = {self.exit: [self.exit]}

        while queue_start and queue_end:
            x, y, path = queue_start.pop(0)
            if (x, y) in seen_end:
                return path + seen_end[(x, y)][::-1][1:]

            for direction in MOVES:
                move_x, move_y, wall = MOVES[direction]
                new_x, new_y = x + move_x, y + move_y
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    if not (self.grid[y][x] & wall) and (new_x, new_y) not in seen_start:
                        seen_start[(new_x, new_y)] = path + [(new_x, new_y)]
                        queue_start.append((new_x, new_y, path + [(new_x, new_y)]))

            x, y, path = queue_end.pop(0)
            if (x, y) in seen_start:
                return seen_start[(x, y)] + path[::-1][1:]

            for direction in MOVES:
                move_x, move_y, wall = MOVES[direction]
                new_x, new_y = x + move_x, y + move_y
                if 0 <= new_x < self.width and 0 <= new_y < self.height:
                    if not (self.grid[y][x] & wall) and (new_x, new_y) not in seen_end:
                        seen_end[(new_x, new_y)] = path + [(new_x, new_y)]
                        queue_end.append((new_x, new_y, path + [(new_x, new_y)]))