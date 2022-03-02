
import pygame
import time
import random
import numpy as np
import sys

# Sub class for the maze generating algoirthms
class Algorithm:
    def __init__(self, maze_gen):
        self.maze = maze_gen
        self.WINDOW = self.maze.WINDOW

        self.wait_time = self.maze.wait_time
        self.cell_size = self.maze.cell_size
        self.half_c_size = self.cell_size//2
        # Line for the path through the maze
        self.line_width = self.cell_size - (2*((self.cell_size//2)-1))

        self.grid = self.maze.grid
        # The line through the maze is drawn from the exit to the entry
        self.entry = self.grid[0, 0]
        self.exit = self.grid[-1, -1]
        # current is the cell currently being considered
        self.current = self.entry
        self.current.been_visited()
        # Keeps track of which cell each cell came from
        self.solution = {}

    def display_and_wait(self):
        pygame.display.update()
        time.sleep(self.wait_time)

    # Sees if the window has been closed
    def check_closed(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

    # Draws a path through the whole maze
    def path_through(self):
        def path_line_up(x, y, colour):
            pygame.draw.rect(self.WINDOW, colour, (x+self.half_c_size, y+self.half_c_size-self.cell_size, self.line_width, self.cell_size), 0)
            pygame.display.update()
        
        def path_line_down(x, y, colour):
            pygame.draw.rect(self.WINDOW, colour, (x+self.half_c_size, y+self.half_c_size, self.line_width, self.cell_size), 0)
            pygame.display.update()

        def path_line_left(x, y, colour):
            pygame.draw.rect(self.WINDOW, colour, (x+self.half_c_size-self.cell_size, y+self.half_c_size, self.cell_size+self.line_width, self.line_width), 0)
            pygame.display.update()

        def path_line_right(x, y, colour):
            pygame.draw.rect(self.WINDOW, colour, (x+self.half_c_size, y+self.half_c_size, self.cell_size+self.line_width, self.line_width), 0)
            pygame.display.update()

        x = self.exit.x
        y = self.exit.y
        i = 0

        # Originally goes through the path to check the length
        while (x, y) != (self.entry.x, self.entry.y):
            self.check_closed()
            i += 1
            x, y = self.solution[x,y]

        x = self.exit.x
        y = self.exit.y

        # Starts red and fades into yellow
        colour = (255, 0, 0)
        green_value = 0

        counter = 0
        gradient_quotient = 0

        # Creates a gradiented line from red to yellow, with the gradient dependent on the length of the path
        if i <= 255:
            gradient_quotient = 255//i
            while (x, y) != (self.entry.x, self.entry.y):
                self.check_closed()

                if self.solution[x, y][0] > x:
                    path_line_right(x, y, colour)
                if self.solution[x, y][0] < x:
                    path_line_left(x, y, colour)
                if self.solution[x, y][1] < y:
                    path_line_up(x, y, colour)
                if self.solution[x, y][1] > y:
                    path_line_down(x, y, colour)

                x, y = self.solution[x, y]
                time.sleep(self.wait_time)
                green_value += gradient_quotient
                colour = (255, green_value, 0)

        else:
            gradient_quotient = 1
            colour_change_const = ((i//255)+1)
            while (x, y) != (self.entry.x, self.entry.y):
                self.check_closed()

                counter += 1
                if self.solution[x, y][0] > x:
                    path_line_right(x, y, colour)
                if self.solution[x, y][0] < x:
                    path_line_left(x, y, colour)
                if self.solution[x, y][1] < y:
                    path_line_up(x, y, colour)
                if self.solution[x, y][1] > y:
                    path_line_down(x, y, colour)               

                x, y = self.solution[x, y] 
                time.sleep(self.wait_time)
                if counter % colour_change_const == 0:
                    green_value += gradient_quotient
                    colour = (255, green_value, 0)


# The algoirthm finds a random walk from a starting point, and once the walk has no where to go, you backtrack until
# you find a cell in which you can do another walk from.
class DepthFirst(Algorithm):
    def __init__(self, maze_gen):
        Algorithm.__init__(self, maze_gen)

        # Stack needed for backtracking
        self.stack = np.empty((0,1))
        self.stack = np.append(self.stack, self.current)  

    def run(self):
        pygame.display.set_caption("Python Maze Generator (Depth First Search)")
        while self.stack.size > 0:
            self.check_closed()

            time.sleep(self.wait_time)
            unvisited_neighbours = self.current.grab_unvisited_neighbours()

            # Chooses random direction to walk in if viable
            if len(unvisited_neighbours) > 0:
                chosen_neighbour = random.choice(unvisited_neighbours)

                if chosen_neighbour.row > self.current.row:
                    self.current.open_down()

                if chosen_neighbour.row < self.current.row:
                    self.current.open_up()

                if chosen_neighbour.col > self.current.col:
                    self.current.open_right()

                if chosen_neighbour.col < self.current.col:
                    self.current.open_left()

                pygame.display.update()
                self.solution[(chosen_neighbour.x, chosen_neighbour.y)] = self.current.x, self.current.y
                self.current = chosen_neighbour
                self.current.been_visited()
                self.stack = np.append(self.stack, self.current)

            # If there's nowhere to walk, the cell flashes red and there's a backtrack
            else:
                self.current = self.stack[-1]
                self.stack = self.stack[:-1]

                self.current.show_cell()
                pygame.display.update()
                time.sleep(self.wait_time)
                self.current.cover_cell()
                pygame.display.update()

        # Shows path through the maze once it's created
        self.path_through()

# Adds a cell to a maze and then randomly joins an adjacent cell to the maze. Another cell adjacent to the current
# maze is then joined to the maze, and this is repeated until the maze is complete.
class Primms(Algorithm):
    def __init__(self, maze_gen):
        Algorithm.__init__(self, maze_gen)

        # Array of cells which are adjacent to already visited cells
        self.considering = np.empty((0,1))    

    def run(self):
        pygame.display.set_caption("Pyhton Maze Generator (Primm's Algorithm)")
        self.current.show_cell()

        # Finds all adjacent cells and adds them to the 'considering' array
        self.considering = np.array(self.current.grab_unvisited_neighbours())
        for cell in self.considering:
            cell.show_cell()
        pygame.display.update()

        while self.considering.size > 0:
            self.check_closed()

            time.sleep(self.wait_time)

            # Picks a random cell from 'considering', and joins it to a visited cell
            self.current = random.choice(self.considering)
            self.current.been_visited()
            visited_neighbours = self.current.grab_visited_neighbours()

            chosen_neighbour = random.choice(visited_neighbours)

            if chosen_neighbour.row > self.current.row:
                self.current.open_down()

            if chosen_neighbour.row < self.current.row:
                self.current.open_up()

            if chosen_neighbour.col > self.current.col:
                self.current.open_right()

            if chosen_neighbour.col < self.current.col:
                self.current.open_left()

            self.solution[(self.current.x, self.current.y)] = chosen_neighbour.x, chosen_neighbour.y
            # Adds neighbours of the newly joined cell to the 'considering' array if the cell is not being currently considered
            unvisited_neighbours = self.current.grab_unvisited_neighbours()
            for neighbour in unvisited_neighbours:
                if neighbour not in self.considering:
                    neighbour.show_cell()
                    self.considering = np.append(self.considering, neighbour)

            # Deletes the newly added cell from 'considering'
            delete_array = np.where(self.current == self.considering)
            delete_index = delete_array[0]
            self.considering = np.delete(self.considering, delete_index)

            pygame.display.update()

        self.path_through()


# Goes from the uppermost furthest left cell and adds a cell to the right to complete the top row
# Afterward, each cell added, going from left to right, top to bottom, either carves a path upwards
# or to the left, until the maze is complete.
class BinaryTree(Algorithm):
    def __init__(self, maze_gen):
        Algorithm.__init__(self, maze_gen)

    def run(self):
        pygame.display.set_caption("Python Maze Generator (Binary Tree Algorithm)")

        # Fills the first cell
        self.current.show_cell()
        self.display_and_wait()
        self.current.cover_cell()

        # Fills the remaining section of the top row 
        for cell in self.grid[0, 1:]:
            self.check_closed()

            self.current = cell
            self.current.show_cell()
            self.display_and_wait()
            self.current.open_left()

            self.solution[(self.current.x, self.current.y)] = self.current.x - self.cell_size, self.current.y

        # Fills the remaining rows  
        for row in self.grid[1:]:
            self.current = row[0]

            # First cell of each row can only carve upwards
            self.current.show_cell()
            self.display_and_wait()
            self.current.open_up()
            self.display_and_wait()    

            self.solution[(self.current.x, self.current.y)] = self.current.x, self.current.y - self.cell_size

            for cell in row[1:]:
                self.check_closed()

                self.current = cell

                self.current.show_cell()
                self.display_and_wait()

                direction = random.randrange(2)

                if direction == 0:
                    self.current.open_up()
                    self.solution[(self.current.x, self.current.y)] = self.current.x, self.current.y - self.cell_size
                else:
                    self.current.open_left()
                    self.solution[(self.current.x, self.current.y)] = self.current.x - self.cell_size, self.current.y
        pygame.display.update()

        self.path_through()


# Creates a random walk from the top left cell and when the walk comes to an end, another walk is started from the first 
# cell possible, when looking from left to right, top to bottom on the maze.
class HuntAndKill(Algorithm):
    def __init__(self, maze_gen):
        Algorithm.__init__(self, maze_gen)

        # A generator and its initial position
        self.h = self.hunt()
        self.hunt_pos = next(self.h)

    # The generator goes through positions left to right, top to bottom on the maze
    def hunt(self):
        for i in range(self.grid.shape[0]):
            for j in range(self.grid.shape[1]):
                yield (i, j)
        # Yields an invalid position once the maze is complete
        yield -1

    def run(self):
        pygame.display.set_caption("Python Maze Generator (Hunt and Kill Algorithm)")

        # Until the generator is on its final value
        while self.hunt_pos != -1:
            self.check_closed()

            # Performs random walk
            time.sleep(self.wait_time)
            unvisited_neighbours = self.current.grab_unvisited_neighbours()

            if len(unvisited_neighbours) > 0:
                chosen_neighbour = random.choice(unvisited_neighbours)

                if chosen_neighbour.row > self.current.row:
                    self.current.open_down()

                if chosen_neighbour.row < self.current.row:
                    self.current.open_up()

                if chosen_neighbour.col > self.current.col:
                    self.current.open_right()

                if chosen_neighbour.col < self.current.col:
                    self.current.open_left()

                pygame.display.update()
                self.solution[(chosen_neighbour.x, chosen_neighbour.y)] = self.current.x, self.current.y
                self.current = chosen_neighbour
                self.current.been_visited()

            # If no available position, walk from the last 'hunting' position
            else:
                self.current = self.grid[self.hunt_pos]
                self.current.show_cell()
                self.display_and_wait()

                self.current.cover_cell()
                pygame.display.update()

                unvisited_neighbours = self.current.grab_unvisited_neighbours()
                # If the hunting position isn't available, use the next one
                if len(unvisited_neighbours) == 0:
                    self.hunt_pos = next(self.h)

        self.path_through()


# Connects cells horizontally into a 'run set'. Randomly chooses whether to continue the run set or to carve upwards
# on a random cell in the run set, which creates a new set, which becomes the current runnning set.
class Sidewinder(Algorithm):
    def __init__(self, maze_gen):
        Algorithm.__init__(self, maze_gen)

        self.run_set = np.empty((0,1))

    # Chooses random cell in the run set and carves upwards
    def carve_north(self):
        chosen_cell = random.choice(self.run_set)
        chosen_cell.show_cell()
        self.display_and_wait()
        chosen_cell.open_up()
        self.solution[(chosen_cell.x, chosen_cell.y)] = chosen_cell.x, chosen_cell.y - self.cell_size

        for cell in self.run_set:
            self.check_closed()

            # Redirects the 'solution' of the cells in the run set towards the cell which carved upwards
            if cell.col < chosen_cell.col:
                self.solution[(cell.x, cell.y)] = cell.x + self.cell_size, cell.y

    def run(self):
        pygame.display.set_caption("Python Maze Generator (Sidewinder Algorithm)")

        # Carves to the right along the entire top row
        for cell in self.grid[0, :-1]:
            self.check_closed()

            self.current = cell
            self.current.show_cell()
            self.display_and_wait()
            self.current.open_right()

            self.solution[(self.current.x + self.cell_size, self.current.y)] = self.current.x, self.current.y

        self.current = self.grid[0, -1]
        self.current.show_cell()
        self.display_and_wait()
        self.current.cover_cell()

        # Fills the remaining rows of the maze
        for row in self.grid[1:]:
            self.check_closed()

            for cell in row[:-1]:
                self.check_closed()
                self.current = cell

                carve_east = random.choice([True, True, False])

                self.current.show_cell()
                self.display_and_wait()
                self.current.cover_cell()

                self.run_set = np.append(self.run_set, self.current)

                if carve_east:
                    self.current.open_right()
                    self.solution[(self.current.x + self.cell_size, self.current.y)] = self.current.x, self.current.y
                else:
                    self.carve_north()
                    self.run_set = np.empty((0,1))

            # Always carves north on the last cell of each row
            self.current = row[-1]    

            self.current.show_cell()
            self.display_and_wait()
            self.current.cover_cell()

            self.run_set = np.append(self.run_set, self.current)

            self.carve_north()
            self.run_set = np.empty((0,1))
            self.display_and_wait()

        self.path_through()


# Creates cells from left to right, top to bottom. Initialises each cell in its own set and chooses random whether 
# or not to merge with the cell to the left of it, so long as they are in different sets. After completing a row
# each cell from the row randomly carves downwards, with at least one cell from each set carving downwards. 
# The final row of the maze merges all of the sets together into one.
class Ellers(Algorithm):
    def __init__(self, maze_gen):
        Algorithm.__init__(self, maze_gen)

        # Eller's itertes over each row twice so this exists to speed up the process
        self.wait_time_multiplier = 1.5

        self.set_dict = {}
        self.rolling_set_no = 1
        self.current_row = 0

        self.create_new_set()

    # For when each new cell is created
    def create_new_set(self):
        self.current.set = self.rolling_set_no
        self.set_dict[self.current.set] = {self.current}
        self.rolling_set_no += 1

    # Merges the newer sets to the older sets instead of the other way around for efficiency 
    def merge_sets(self, set_num, neighbour_set_num):
        self.set_dict[neighbour_set_num].update(self.set_dict[set_num])

        for cell in self.set_dict[set_num]:
            self.check_closed()
            cell.set = neighbour_set_num
        del self.set_dict[set_num]

    # Creates downwards connections in the row, ensuring each set has at least one
    def extend_down(self):
        row = self.grid[self.current_row]
        # Counts the number of cells of each set in the row
        counter = {}
        # Tracks if the set has a downwards connection
        extended = {}

        for cell in row:
            self.check_closed()

            try:
                counter[cell.set] += 1
            except:
                counter[cell.set] = 1
                extended[cell.set] = False

        for cell in row:
            self.check_closed()

            cell.show_cell()
            self.display_and_wait()

            carve_down = random.choice([True, False])
            if carve_down:
                cell.open_down()

                extended[cell.set] = True
                self.grid[cell.row + 1, cell.col].been_visited()
                self.grid[cell.row + 1, cell.col].set = cell.set
                self.set_dict[cell.set].add(self.grid[cell.row + 1, cell.col])

            # if the cell is the last in the set of the row and no cells in the set connected downwards
            elif counter[cell.set] == 1 and not extended[cell.set] == True:
                cell.open_down()
                self.grid[cell.row + 1, cell.col].been_visited()
                self.grid[cell.row + 1, cell.col].set = cell.set
                self.set_dict[cell.set].add(self.grid[cell.row + 1, cell.col])

            else:
                cell.cover_cell()

            counter[cell.set] -= 1
            self.display_and_wait()    

        self.current_row += 1            

    def run(self):
        pygame.display.set_caption("Python Maze Generator (Eller's Algorithm)")

        self.wait_time /= self.wait_time_multiplier

        # First cell
        self.current.show_cell()
        self.display_and_wait()
        self.current.cover_cell()
        self.display_and_wait()

        previous = self.current

        # First row, after the first cell
        for cell in self.grid[0, 1:]:
            self.check_closed()

            self.current = cell
            self.create_new_set()

            self.current.show_cell()
            self.display_and_wait()

            merge = random.choice([True, False])
            if merge:
                self.current.open_left()
                self.merge_sets(self.current.set, previous.set)
            else:
                self.current.cover_cell()

            self.display_and_wait()
            previous = self.current

        self.extend_down()

        # Remaining rows up to the final row
        for row in self.grid[1:-1]:
            self.check_closed()

            # First cell of row
            self.current = row[0]
            self.current.show_cell()
            self.display_and_wait()

            # If the cell isn't where a downwards connection was made
            if not self.current.visited:
                self.create_new_set()
            
            self.current.cover_cell()
            self.display_and_wait()

            previous = self.current

            # Remaining cells of rows
            for cell in row[1:]:
                self.check_closed()
                self.current = cell

                self.current.show_cell()
                self.display_and_wait()

                if not self.current.visited:
                    self.create_new_set()

                if previous.set != self.current.set:
                    merge = random.choice([True, False])
                    if merge:
                        self.current.open_left()
                        self.merge_sets(self.current.set, previous.set)
                    else:
                        self.current.cover_cell()
                else:
                    self.current.cover_cell()

                self.display_and_wait()

                previous = self.current
            
            self.extend_down()

        # Final row
        self.current = self.grid[-1, 0]
        self.current.show_cell()
        self.display_and_wait()

        if not self.current.visited:
            self.create_new_set()

        self.current.cover_cell()
        self.display_and_wait()

        previous = self.current

        # Remaining cells of the final row
        for cell in self.grid[-1, 1:]:
            self.check_closed()
            self.current = cell

            self.current.show_cell()
            self.display_and_wait()

            if not self.current.visited:
                self.create_new_set()

            if previous.set != self.current.set:
                self.current.open_left()
                self.merge_sets(self.current.set, previous.set)
            else:
                self.current.cover_cell()

            self.display_and_wait()

        self.wait_time *= self.wait_time_multiplier