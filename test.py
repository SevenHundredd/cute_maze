from mazegen import MazeGenerator, load_config 

config = load_config("config.txt")
generator = MazeGenerator(config)
generator.generate()
print(bin(generator.grid[0][0]).removeprefix('0b'))