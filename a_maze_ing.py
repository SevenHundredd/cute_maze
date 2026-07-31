import sys
import random

from mazegen import *

def main():
    config_file = sys.argv[1]
    try:
        config = load_config(config_file)
    except Exception as e:
        print(f"Error loading config: {e}")

    theme = list(THEMES.keys())
    current_theme = "3"
    generator = MazeGenerator(config)
    generator.generate()
    show_solution = False
    solution_path = []

    try:
        while True:
            clear_screen()
            print(f"Entry: {config.entry}, Exit: {config.exit}, Perfect: {config.perfect}, Seed: {config.seed}")
            maze_frame(generator, solution_path if show_solution else [], current_theme)
            solve_label = "Hide Solution" if show_solution else "Show Solution"
            print(f"\n[1] {solve_label}")
            print("[2] Regenerate Maze")
            print("[3] Change Theme")
            print("[4] Export Maze")
            print("[5] Quit")

            choice = input("Choose an option: ").strip()

            match choice:
                case "1":
                    show_solution = not show_solution
                    solver = MazeSolver(generator.grid, config.entry, config.exit)
                    solution_path = solver.solve() if show_solution else []

                case "2":
                    if config.seed is not None:
                        choice = input(" Found a seed, Choose an option:\n  [1] Next seed\n  [2] Previous seed\n> ").strip()
                        if choice == "2":
                            config.seed -= 1
                        elif choice == "1":
                            config.seed += 1
                    generator = MazeGenerator(config)
                    generator.generate()
                    solution_path = []
                    show_solution = False

                case "3":
                    current_theme = random.choice(theme)

                case "4":
                    if not solution_path:
                        solver = MazeSolver(generator.grid, config.entry, config.exit)
                        solution_path = solver.solve()
                    export_maze("maze_output.txt", generator.grid, solution_path)
                    input("\nExported to 'maze_output.txt'! Press any key to continue...")

                case "5":
                    print("\nGoodbye!")
                    break

                case _:
                    input("\nInvalid option! Press any key to try again...")
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        raise SystemExit(f"\n\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()       