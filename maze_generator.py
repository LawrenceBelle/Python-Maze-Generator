import pygame
import numpy as np
#
from algorithms import *


class MazeGenerator:
    def __init__(self, rows, cols, cell_size, algorithm):
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size

        # Decides how long to pause based on the size of the maze, the larger the maze, the shorter the pause
        if (self.rows + self.cols)//2 > 150:
            self.wait_time = 0
        else:
            self.wait_time = 1 / (((self.rows+self.cols)//2) ** (1 + ((divmod((self.rows+self.cols)//2, 25)[0] + 1) / 20)))

        # Define colours
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.LIGHT_GREY = (180, 180, 180)
        self.DARK_GREY = (50, 50, 50)
        self.COBALT = (64, 130, 255)
        self.YELLOW = (255, 255, 0)
        self.RED = (255, 30, 30)
        self.BLACK = (0, 0, 0)        

        # Select colours
        self.maze_colour = self.COBALT
        self.wall_colour = self.DARK_GREY
        self.backtrack_colour = self.RED
        self.bg_colour = self.BLACK

        # set up pygame window
        self.WINDOW_WIDTH = (self.cols+2)*self.cell_size
        self.WINDOW_HEIGHT = (self.rows+2)*self.cell_size
        self.FPS = 60
        pygame.init()
        self.clock = pygame.time.Clock()
        self.WINDOW = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Python Maze Generator")
        self.running = True
        
        # A map of all the cells in the maze
        self.grid = self.make_grid()
        self.add_cell_neighbours()

        # A collection of the maze creating algorithms
        self.depth_first = DepthFirst(self)
        self.primms = Primms(self)
        self.binary_tree = BinaryTree(self)
        self.hunt_and_kill = HuntAndKill(self)
        self.sidewinder = Sidewinder(self)
        self.ellers = Ellers(self)

        # Dictionary to convert the output of the tkinter spinbox to an algorithm
        self.algorithms = {
            "Depth First" : self.depth_first,
            "Primm's" : self.primms,
            "Binary Tree" : self.binary_tree,
            "Hunt and Kill" : self.hunt_and_kill,
            "Sidewinder" : self.sidewinder,
            "Eller's" : self.ellers,            
        }
        self.algorithm = self.algorithms[algorithm]


    # clasee for each tile in the maze
    class Cell:
        def __init__(self, row, col, cell_size, no_rows, no_cols, window, m_colour, bt_colour):
            self.window = window

            self.row = row
            self.col = col

            self.no_rows = no_rows
            self.no_cols = no_cols
            self.cell_size = cell_size
            # converts the coordinates one cell width and height from the the top left corner
            self.x = (self.col+1) * self.cell_size
            self.y = (self.row+1) * self.cell_size
            self.visited = False
            self.neighbours = []
            # used for Eller's Algorithm
            self.set = None
            
            self.maze_colour = m_colour
            self.backtrack_colour = bt_colour

        def been_visited(self):
            self.visited = True

        # Collects all adjacent cells 
        def add_neighbours(self, grid):
            self.neighbours = []
            if self.row < self.no_rows-1:
                self.neighbours.append(grid[self.row+1, self.col])

            if self.row > 0:
                self.neighbours.append(grid[self.row-1, self.col])

            if self.col < self.no_cols-1:
                self.neighbours.append(grid[self.row, self.col+1])

            if self.col > 0:
                self.neighbours.append(grid[self.row, self.col-1])

        def grab_unvisited_neighbours(self):
            unvisited_neighbours = []
            for neighbour in self.neighbours:
                if not neighbour.visited:
                    unvisited_neighbours.append(neighbour)
            return unvisited_neighbours

        # Needed for Primm's
        def grab_visited_neighbours(self):
            visited_neighbours = []
            for neighbour in self.neighbours:
                if neighbour.visited:
                    visited_neighbours.append(neighbour)
            return visited_neighbours

        # Removes wall between current and adjacent cell
        def open_up(self):
            pygame.draw.rect(self.window, self.maze_colour, (self.x+1, self.y+1-self.cell_size, self.cell_size-1, (2*self.cell_size)-1), 0)

        def open_down(self):
            pygame.draw.rect(self.window, self.maze_colour, (self.x+1, self.y+1, self.cell_size-1, (2*self.cell_size)-1), 0)

        def open_left(self):
            pygame.draw.rect(self.window, self.maze_colour, (self.x+1-self.cell_size, self.y+1, (2*self.cell_size)-1, self.cell_size-1), 0)

        def open_right(self):
            pygame.draw.rect(self.window, self.maze_colour, (self.x+1, self.y+1, (2*self.cell_size)-1, self.cell_size-1), 0)


        # Flashes the cell which is considered
        def show_cell(self):
            pygame.draw.rect(self.window, self.backtrack_colour, (self.x+1, self.y+1, self.cell_size-1, self.cell_size-1), 0)         

        def cover_cell(self):
            pygame.draw.rect(self.window, self.maze_colour, (self.x+1, self.y+1, self.cell_size-1, self.cell_size-1), 0)   

    # Draws all the walls for the maze
    def draw_grid(self):
        self.WINDOW.fill(self.bg_colour)
        for i in range(self.rows+1):
            pygame.draw.line(self.WINDOW, self.wall_colour, (self.cell_size, (i+1)*self.cell_size), (self.cell_size*(self.cols+1), (i+1)*self.cell_size))
        for j in range(self.cols+1):
            pygame.draw.line(self.WINDOW, self.wall_colour, ((j+1)*self.cell_size, self.cell_size), ((j+1)*self.cell_size, self.cell_size*(self.rows+1)))
        pygame.display.update()

    # Creates the map of all the cells
    def make_grid(self):
        grid = np.empty((0, self.cols))
        for i in range(self.rows):
            grid_row = np.empty((0,1))
            for j in range(self.cols):
                cell = self.Cell(i, j, self.cell_size, self.rows, self.cols, self.WINDOW, self.maze_colour, self.backtrack_colour)
                grid_row = np.append(grid_row, cell)
            grid = np.append(grid, np.array([grid_row]), axis=0)

        return grid

    def add_cell_neighbours(self):
        for row in self.grid:
            for cell in row:
                cell.add_neighbours(self.grid)

    # Starts the maze creations algorithm
    def generate(self):
        
        self.draw_grid()

        self.algorithm.run()

        while self.running:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    


if __name__ == '__main__':
    mg = MazeGenerator(20, 20, 20, "Depth First")
    mg.generate()
