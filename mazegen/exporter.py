

MOVE = {
    (0, -1): "N",
    (1, 0): "E",
    (0, 1): "S",
    (-1, 0): "W",
}


def path_to_directions(path: list[tuple[int, int]]) -> list[str]:
    if not path or len(path) < 2:
        return []

    directions = []
    for i in range(len(path) - 1):
        curr_x, curr_y = path[i]
        next_x, next_y = path[i + 1]
        move = (next_x - curr_x, next_y - curr_y)

        if move in MOVE:
            directions.append(MOVE[move])

    return directions


def export_maze(filename: str, grid: list[list[int]], path: list[tuple[int, int]]) -> None:
    directions = path_to_directions(path)
    dir_string = "".join(directions)
    x_start = str(path[0][0])
    y_start = str(path[0][1])
    x_end = str(path[-1][0])
    y_end = str(path[-1][1])

    with open(filename, "w") as f:
        for row in grid:
            f.write("".join(hex(value).removeprefix("0x").upper() for value in row) + "\n")
        f.write("\n")
        f.write(f"{x_start},{y_start}\n")
        f.write(f"{x_end},{y_end}\n")
        f.write(dir_string + "\n")
