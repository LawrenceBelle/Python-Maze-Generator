from maze_generator import MazeGenerator
from start_window import Window

win = Window()
win.run()

if win.launch_maze:
    maze = MazeGenerator(win.maze_rows, win.maze_cols, win.maze_cell_size, win.chosen_algorithm)
    maze.generate()

