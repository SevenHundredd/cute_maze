import sys
import random
from time import sleep

from mazegen import *
# import * not autorized by PEP8, but used here for simplicity
# all files need mypy and flake8 check
# command during program need precision
def main():
    config_file = sys.argv[1]
    try:
        config = load_config(config_file)
    except Exception as e:
        raise SystemExit(f"Error loading config: {e}")

    theme = list(THEMES.keys())
    current_theme = "3"
    generator = MazeGenerator(config)
    generator.generate()
    show_solution = False
    solution_path = []

    try:
        while True:
            clear_screen()
            if show_solution:
                print(f"Entry: {config.entry}, Exit: {config.exit}, Perfect: {config.perfect}, Seed: {config.seed}")
                head = [solution_path[0]]
                for pos in solution_path:
                    print(f"Entry: {config.entry}, Exit: {config.exit}, Perfect: {config.perfect}, Seed: {config.seed}")
                    maze_frame(generator, head, current_theme)
                    sleep(0.05)
                    head.append(pos)
                    if pos != solution_path[-1]:
                        clear_screen()
            else:
                maze_frame(generator, [], current_theme) 
            solve_label = "Hide Solution" if show_solution else "Show Solution"
            if generator.height < 7 or generator.width < 9:
                print("\nMaze dimensions are too small to print the 42 pattern. (Minimum 7*5)")
            if generator.entry in generator.ignore or generator.exit in generator.ignore:
                print("\nEntry or exit point is in the 42 pattern. The maze will be generated without the pattern.")
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
                    solution_path = solver.bidirectional_solve() if show_solution else []

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