"""Interactive command-line entry point for the A-Maze-ing project.

Loads a maze configuration from the file given as the first argument,
generates the maze, and displays an interactive terminal menu to
show/hide the solution, regenerate the maze, change theme, export it,
or edit the configuration on the fly.
"""
import sys
import random
from mazegen import MazeSolver, load_config
from mazegen.custom_tools import (animate_dfs_generation, animate_bfs,
                                  clear_screen, animate_path, maze_frame,
                                  animated_frame, THEMES)
from mazegen.exporter import export_maze


def main() -> None:
    """Run the interactive maze CLI.

    Reads the config path from sys.argv[1], generates the initial
    maze, then loops on a text menu until the user quits or an
    unhandled error/KeyboardInterrupt occurs.
    """
    config_file = sys.argv[1]
    try:
        generator = load_config(config_file)
        generator.generate()
        solver = MazeSolver(generator.get_grid(),
                            generator.entry,
                            generator.exit)
        solution_path = solver.solve()
        export_maze(generator.output_file, generator.get_grid(), solution_path)
        theme = list(THEMES.keys())
        current_theme = "3"
        show_solution = False
        inside = False
        solution_path = []
    except Exception as e:
        raise SystemExit(f"Error loading config: {e}")

    try:
        while True:
            if not inside:
                try:
                    clear_screen()
                    animated_frame(generator,
                                   generator.get_grid(),
                                   solution_path, current_theme)
                except KeyboardInterrupt:
                    clear_screen()
                    input("Animation interrupted. Press Enter to continue...")
                    maze_frame(
                        generator,
                        generator.get_grid(),
                        solution_path,
                        current_theme
                    )
            clear_screen()
            if show_solution:
                try:
                    animate_path(
                        generator, solution_path, current_theme
                    )
                except KeyboardInterrupt:
                    clear_screen()
                    input("Animation interrupted. Press Enter to continue...")
                    maze_frame(
                        generator, generator.get_grid(), solution_path,
                        current_theme,
                    )
            else:
                maze_frame(generator, generator.get_grid(), [], current_theme)
            solve_label = "Hide Solution" if show_solution else "Show Solution"
            if generator.height < 7 or generator.width < 9:
                print(
                    "\n⚠️  Maze dimensions are too small to print the "
                    "42 pattern. (Minimum 9*7)"
                )
            elif generator._allowed is False:
                print(
                    "\n⚠️  Entry or exit point is inside the '42' pattern. "
                    "The pattern will be skipped for this generation."
                )
            inside = True
            print(f"\n[1] {solve_label}")
            print("[2] Regenerate Maze")
            print("[3] Change Theme")
            print("[4] Export Maze")
            print("[5] Change maze configuration")
            print("[6] Visualize algorithms (DFS/BFS)")
            print("[7] Quit")

            choice = input("Choose an option: ").strip()

            match choice:
                case "1":
                    show_solution = not show_solution
                    solver = MazeSolver(
                        generator.get_grid(), generator.entry, generator.exit
                    )
                    solution_path = solver.solve() if show_solution else []

                case "2":
                    choice = input(
                        f" Found a seed ({generator.seed}), "
                        "Choose an option:\n"
                        "  [1] Choose a new seed\n  [2] Remove/add seed\n> "
                    ).strip()
                    match choice:
                        case "2":
                            if generator.seed is not None:
                                generator.seed = None
                            else:
                                new_seed_value = input(
                                    "Enter new seed value (integer): "
                                )
                                try:
                                    generator.seed = int(new_seed_value)
                                except ValueError:
                                    input("Invalid seed value! " +
                                          "Keeping current seed.")
                        case "1":
                            new_seed_value = input(
                                "Enter new seed value (integer): "
                            )
                            try:
                                generator.seed = int(new_seed_value)
                            except ValueError:
                                input("Invalid seed value! Keeping " +
                                      "current seed.")
                        case _:
                            input("Keeping current seed.")
                    generator.generate()
                    solution_path = []
                    show_solution = False
                    inside = False

                case "3":
                    current_theme = random.choice(theme)
                    solution_path = []
                    show_solution = False

                case "4":
                    if not solution_path:
                        solver = MazeSolver(
                            generator.get_grid(),
                            generator.entry,
                            generator.exit
                            )
                        solution_path = solver.solve()
                    output_file = input("Enter the solution path " +
                                        "to export the maze: ")
                    try:
                        export_maze(
                            output_file, generator.get_grid(), solution_path
                            )
                        input(
                            f"\nExported to '{output_file}'! "
                            "Press any key to continue..."
                        )
                    except FileNotFoundError:
                        clear_screen()
                        input("Empty input, setting output" +
                              f"file path to '{generator.output_file}'")
                    except PermissionError:
                        clear_screen()
                        input(f"Permission denied for '{output_file}'. " +
                              "Please check your permissions.")

                case "5":
                    try:
                        old_generator = generator.model_copy()
                        generator
                        new_width = input("Enter new width: ")
                        generator.width = (
                            int(new_width) if new_width else generator.width
                        )
                        new_height = input("Enter new height: ")
                        generator.height = (
                            int(new_height)
                            if new_height else generator.height
                        )
                        print(
                            "Make sure the new entry and exit points are "
                            f"within the maze size "
                            f"({generator.width}x{generator.height})."
                        )
                        new_entry = input("Enter new entry point (x,y): ")
                        if new_entry:
                            x_str, y_str = new_entry.split(',')
                            generator.entry = (int(x_str), int(y_str))
                        new_exit = input("Enter new exit point (x,y): ")
                        if new_exit:
                            x_str, y_str = new_exit.split(',')
                            generator.exit = (int(x_str), int(y_str))
                        new_perfect = input(
                            "Should the maze be perfect? (True/False): "
                        )
                        new_seed = input(
                            "Choose an option for the seed:\n"
                            " [1] Choose a new seed\n"
                            " [2] Remove/add seed\n> "
                        )
                        match new_seed:
                            case "1":
                                new_seed_value = input(
                                    "Enter new seed value (integer): "
                                )
                                try:
                                    generator.seed = int(new_seed_value)
                                except ValueError:
                                    input("Invalid seed" +
                                          " value! Keeping current seed.")
                            case "2":
                                if generator.seed is not None:
                                    generator.seed = None
                                else:
                                    new_seed_value = input(
                                        "Enter new seed value (integer): "
                                    )
                                    try:
                                        generator.seed = int(new_seed_value)
                                    except ValueError:
                                        input("Invalid seed" +
                                              " value! Keeping current seed.")
                            case _:
                                input("Keeping current seed.")
                        generator.perfect = (bool(new_perfect) if new_perfect
                                             else generator.perfect)
                        generator.generate()
                        show_solution = False
                        solution_path = []
                    except Exception as e:
                        clear_screen()
                        print(f"\nError in new configuration: {e}")
                        print("Reverting to previous configuration.")
                        generator = old_generator.model_copy()
                        generator.generate()
                        solution_path = []
                        show_solution = False
                        input("Press Enter to continue...")
                case "6":
                    algo_choice = input(
                        "Choose an algorithm to visualize:\n"
                        " [1] Depth-First Search (DFS generation)\n"
                        " [2] Breadth-First Search (BFS solving)\n> "
                    )
                    match algo_choice:
                        case "1":
                            try:
                                animate_dfs_generation(generator,
                                                       current_theme)
                                input("DFS visualization complete" +
                                      ". Press Enter to continue...")
                            except KeyboardInterrupt:
                                clear_screen()
                                input("DFS visualization interrupted" +
                                      ". Press Enter to continue...")
                            finally:
                                show_solution = False
                                solution_path = []
                        case "2":
                            try:
                                animate_bfs(generator, current_theme)
                                input("BFS visualization complete." +
                                      " Press Enter to continue...")
                            except KeyboardInterrupt:
                                clear_screen()
                                input("BFS visualization interrupted." +
                                      " Press Enter to continue...")
                            finally:
                                show_solution = False
                                solution_path = []
                        case _:
                            input("Invalid choice! Press Enter to continue...")
                            show_solution = False
                            solution_path = []
                case "7":
                    print("\nGoodbye!")
                    break

                case _:
                    input("\nInvalid option! Press entry to try again...")
    except KeyboardInterrupt:
        clear_screen()
        print("Program terminated by user. Goodbye!")
    except Exception as e:
        raise SystemExit(f"\n\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
