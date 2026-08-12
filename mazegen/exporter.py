"""Export a generated maze and its solution path to a text file.

Writes the grid as one hexadecimal digit per cell, followed by the
entry coordinates, exit coordinates, and the solution path expressed
as a string of N/E/S/W direction letters, matching the output format
required by the subject.
"""

MOVE = {
    (0, -1): "N",
    (1, 0): "E",
    (0, 1): "S",
    (-1, 0): "W",
}


def path_to_directions(path: list[tuple[int, int]]) -> list[str]:
    """Convert a list of (x, y) coordinates into N/E/S/W move letters.

    Args:
        path: Sequence of (x, y) coordinates, from start to end.

    Returns:
        The list of direction letters between consecutive path
        positions. Empty if path has fewer than two positions.
    """
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


def export_maze(
    filename: str,
    grid: list[list[int]],
    path: list[tuple[int, int]],
) -> None:
    """Write the maze grid and its solution path to a text file.

    Args:
        filename: Path of the file to write.
        grid: The maze grid, one wall-bitmask integer per cell.
        path: The solution path, from entry to exit, used to derive
            the start/end coordinates and direction string written
            after the grid.
    """
    directions = path_to_directions(path)
    dir_string = "".join(directions)
    x_start = str(path[0][0])
    y_start = str(path[0][1])
    x_end = str(path[-1][0])
    y_end = str(path[-1][1])

    with open(filename, "w") as f:
        for row in grid:
            hex_digits = (
                hex(value).removeprefix("0x").upper() for value in row
            )
            f.write("".join(hex_digits) + "\n")
        f.write("\n")
        f.write(f"{x_start},{y_start}\n")
        f.write(f"{x_end},{y_end}\n")
        f.write(dir_string + "\n")
