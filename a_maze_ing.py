import sys
import random
from time import sleep
import traceback
from mazegen import MazeGenerator, MazeSolver, load_config, THEMES, maze_frame, clear_screen, animated_frame, export_maze

def main():
    config_file = sys.argv[1]
    try:
        config = load_config(config_file)
    except Exception as e:
        raise SystemExit(f"Error loading config: {e}")

    theme = list(THEMES.keys())
    current_theme = "3"
    generator = MazeGenerator(config)
    pattern = generator.ignore
    generator.generate()
    show_solution = False
    inside = False

    try:
        while True:
            if not inside:
                try:
                    clear_screen()
                    animated_frame(generator, generator.grid, [], current_theme)
                except KeyboardInterrupt:
                    for i in range(4):
                        clear_screen()
                        print("Skipping animation"+"."*i)
                        sleep(0.5)
                    maze_frame(generator, generator.grid, [], current_theme)
                        
            clear_screen()
            if show_solution:
                try:
                    head = [solution_path[0]]
                    for pos in solution_path:
                        maze_frame(generator, generator.grid, head, current_theme)
                        sleep(0.05)
                        head.append(pos)
                        if pos != solution_path[-1]:
                            clear_screen()
                except KeyboardInterrupt:
                    for i in range(4):
                        clear_screen()
                        print("Skipping animation"+"."*i)
                        sleep(0.5)
                    maze_frame(generator, generator.grid, solution_path, current_theme)
            else:
                maze_frame(generator, generator.grid, [], current_theme) 
            solve_label = "Hide Solution" if show_solution else "Show Solution"
            if generator.height < 7 or generator.width < 9:
                print("\n⚠️  Maze dimensions are too small to print the 42 pattern. (Minimum 9*7)")
            if generator.entry in pattern or generator.exit in pattern:
                print("\n⚠️  Entry or exit point is in the 42 pattern. The 42 pattern is excluded from the maze.")
            inside = True
            print(f"\n[1] {solve_label}")
            print("[2] Regenerate Maze")
            print("[3] Change Theme")
            print("[4] Export Maze")
            print("[5] Change maze configuration")
            print("[6] Quit")

            choice = input("Choose an option: ").strip()

            match choice:
                case "1":
                    show_solution = not show_solution
                    solver = MazeSolver(generator.grid, config.entry, config.exit)
                    solution_path = solver.solve() if show_solution else []

                case "2":
                    if config.seed is not None:
                        choice = input(" Found a seed, Choose an option:\n  [1] Next seed\n  [2] Previous seed\n> ").strip()
                        match choice:
                            case "2":
                                config.seed -= 1
                            case "1":
                                config.seed += 1
                            case _:
                                input("Keeping current seed.")
                    generator = MazeGenerator(config)
                    generator.generate()
                    solution_path = []
                    show_solution = False
                    inside = False

                case "3":
                    current_theme = random.choice(theme)

                case "4":
                    if not solution_path:
                        solver = MazeSolver(generator.grid, config.entry, config.exit)
                        solution_path = solver.solve()
                    export_maze("maze_output.txt", generator.grid, solution_path)
                    input("\nExported to 'maze_output.txt'! Press any key to continue...")

                case "5":
                    new_entry = input("Enter new entry point (x,y): ")
                    new_exit = input("Enter new exit point (x,y): ")
                    new_width = input("Enter new width: ")
                    new_height = input("Enter new height: ")
                    new_perfect = input("Should the maze be perfect? (True/False): ")
                    new_seed = input("Choose an option for the seed:\n [1] Keep current seed\n [2] Enter new seed\n [3] Remove/add seed\n> ")
                    match new_seed:
                        case "1":
                            new_seed_value = input("Enter new seed value (integer): ")
                            config.seed = int(new_seed_value) if new_seed_value else config.seed
                        case "2":
                            if config.seed is not None:
                                config.seed = None
                            else:
                                new_seed_value = input("Enter new seed value (integer): ")
                                config.seed = int(new_seed_value) if new_seed_value else config.seed
                        case _:
                            input("Keeping current seed.")
                    try:
                        old_config = config.copy()
                        config.entry = tuple(map(int, new_entry.split(','))) if new_entry else config.entry
                        config.exit = tuple(map(int, new_exit.split(','))) if new_exit else config.exit
                        config.width = int(new_width) if new_width else config.width
                        config.height = int(new_height) if new_height else config.height
                        config.perfect = new_perfect
                        generator.generate()
                    except Exception as e:
                        print(f"\nError in new configuration: {e}")
                        print("Reverting to previous configuration.")
                        generator = MazeGenerator(old_config)
                        generator.generate()
                        solution_path = []
                        show_solution = False
                        input("Press Enter to continue...")
                        

                case "6":
                    print("\nGoodbye!")
                    break

                case _:
                    input("\nInvalid option! Press entry to try again...")
    except KeyboardInterrupt:
        clear_screen()
        print("Program terminated by user. Goodbye!")
    except Exception as e:
        traceback.print_exc()
        raise SystemExit(f"\n\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()       