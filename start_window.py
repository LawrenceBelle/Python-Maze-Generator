import tkinter as tk

class Window:
    def __init__(self):
        # Only starts maze if 'launch' is pressed
        self.launch_maze = False

        # Set up window dimensions
        self.WIDTH = 500
        self.HEIGHT = 300

        # Maze dimensions
        self.maze_rows = 20
        self.maze_cols = 20
        self.maze_cell_size = 20
        self.min_rows = 5
        self.min_cols = 5
        self.min_cell_size = 4

        # Available maze creating algorithms
        self.algorithms = ("Depth First", "Primm's", "Binary Tree", "Hunt and Kill", "Sidewinder", "Eller's")
        self.chosen_algorithm = self.algorithms[0]

        self.maze_window_width = (self.maze_cols+2) * self.maze_cell_size        
        self.maze_window_height = (self.maze_rows+2) * self.maze_cell_size

        # Base for set up window
        self.root = tk.Tk()
        self.defaultbg = self.root.cget('bg')
        self.root.resizable(False, False)
        self.root.title('Maze Generator Set Up')

        self.canvas = tk.Canvas(self.root, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack()

        # String variables for the entries and labels
        self.rows_text = tk.StringVar()
        self.rows_text.set(str(self.maze_rows))
        self.cols_text = tk.StringVar()
        self.cols_text.set(str(self.maze_cols))
        self.cell_size_text = tk.StringVar()
        self.cell_size_text.set(str(self.maze_cell_size))

        self.dim_error_text = tk.StringVar()
        self.window_dim_text = tk.StringVar()
        self.window_dim_text.set(f'{self.maze_window_width} x {self.maze_window_height} pxls')

        # Amounts the buttons will affect the maze dimensions
        self.small_increment = 1
        self.large_increment = 10

        # Creating functions for the buttons
        self.add_rows = self.change_maze_dim(self.small_increment, 'rows')
        self.bulk_add_rows = self.change_maze_dim(self.large_increment, 'rows')
        self.take_rows = self.change_maze_dim(-self.small_increment, 'rows')
        self.bulk_take_rows = self.change_maze_dim(-self.large_increment, 'rows')

        self.add_cols = self.change_maze_dim(self.small_increment, 'cols')
        self.bulk_add_cols = self.change_maze_dim(self.large_increment, 'cols')
        self.take_cols = self.change_maze_dim(-self.small_increment, 'cols')
        self.bulk_take_cols = self.change_maze_dim(-self.large_increment, 'cols')

        self.add_cell_size = self.change_maze_dim(self.small_increment, 'cell_size')
        self.bulk_add_cell_size = self.change_maze_dim(self.large_increment, 'cell_size')
        self.take_cell_size = self.change_maze_dim(-self.small_increment, 'cell_size')
        self.bulk_take_cell_size = self.change_maze_dim(-self.large_increment, 'cell_size')

        # Relative sizing for the frames
        self.mid_ref = 0.5
        width_ref = 0.8
        current_y = 0
        y_buffer = 0.05
        current_y += y_buffer
        y_header_length = 0.2
        y_maze_dim_length = 0.3
        y_window_dim_length = 0.1
        y_method_length = 0.1
        y_launch_length = 0.15

        # Contains a Title and instructions
        self.header_frame = tk.Frame(self.root)
        self.header_frame.place(relx=self.mid_ref, rely=current_y, relwidth=width_ref, relheight=y_header_length, anchor='n')
        self.fill_header_frame(self.header_frame)

        current_y += (y_header_length + y_buffer)

        # Contains options for number of rows, columns, and cell size
        self.maze_dim_frame = tk.Frame(self.root)
        self.maze_dim_frame.place(relx=self.mid_ref, rely=current_y, relwidth=width_ref, relheight=y_maze_dim_length, anchor='n')
        self.row_entry, self.col_entry, self.cell_entry = self.fill_maze_dim_frame(self.maze_dim_frame)

        # Ensures only digits (up to 3) are inputted in the entries and updates the relative values
        def validate_entry(input, entry):
            if input.isdigit() and (len(input) < 4):
                if entry == '.!frame2.!frame.!entry': # self.row_entry
                    self.maze_rows = int(input)
                elif entry == '.!frame2.!frame2.!entry': # self.col_entry
                    self.maze_cols = int(input)
                elif entry == '.!frame2.!frame3.!entry': # self.cell_entry
                    self.maze_cell_size = int(input)

                self.maze_window_width = (self.maze_cols+2) * self.maze_cell_size        
                self.maze_window_height = (self.maze_rows+2) * self.maze_cell_size
                self.window_dim_text.set(f'{self.maze_window_width} x {self.maze_window_height} pxls')

                return True
            elif input == '':
                return True
            else:
                return False

        self.validcomm = self.root.register(validate_entry)

        for entry in (self.row_entry, self.col_entry, self.cell_entry):
            entry.config(validate='key', validatecommand=(self.validcomm,'%P','%W'))

        current_y += y_maze_dim_length

        # Displays current window size based on number of rows, columns, and cell size
        self.window_dim_frame = tk.Frame(self.root)
        self.window_dim_frame.place(relx=self.mid_ref, rely=current_y, relwidth=width_ref, relheight=y_window_dim_length, anchor='n')
        self.fill_window_dim_frame(self.window_dim_frame, 'The window will be of size:', self.window_dim_text)

        current_y += y_window_dim_length

        # Contains options for maze creation algorithm
        self.method_frame = tk.Frame(self.root)
        self.method_frame.place(relx=self.mid_ref, rely=current_y, relwidth=width_ref, relheight=y_method_length, anchor='n')
        self.algorithm_box = self.fill_method_frame(self.method_frame)

        current_y += (y_method_length + y_buffer)

        # Contrains button to launch the maze and message if the previous inputs aren't valid
        self.launch_frame = tk.Frame()
        self.launch_frame.place(relx=self.mid_ref, rely=current_y, relwidth=width_ref, relheight=y_launch_length, anchor='n')
        self.fill_launch_frame(self.launch_frame)

    def change_maze_dim(self, increment, maze_feature):
        # Refers to either rows, cols or cell_size
        mf = maze_feature        
        inc = increment
        def inner_function():
            if mf == 'rows':
                if (self.maze_rows + inc) >= self.min_rows:
                    self.maze_rows += inc
                else:
                    self.maze_rows = self.min_rows
            elif mf == 'cols':
                if (self.maze_cols + inc) >= self.min_cols:
                    self.maze_cols += inc
                else:
                    self.maze_cols = self.min_cols
            elif mf == 'cell_size':
                if (self.maze_cell_size + inc) >= self.min_cell_size:
                    self.maze_cell_size += inc
                else:
                    self.maze_cell_size = self.min_cell_size
            self.refresh_entries()
        return inner_function
    
    # Sets title for the window and gives instructions
    def fill_header_frame(self, frame):
        rel_title_height = 0.75
        rel_instruc_height = 1 - rel_title_height

        title_label = tk.Label(frame, text='Maze Generator Launcher', font=('', 20), bg=self.defaultbg)
        title_label.place(relwidth=1, relheight=rel_title_height)

        instructions_label = tk.Label(frame, text='Select the dimensions of the maze', bg=self.defaultbg)
        instructions_label.place(rely=rel_title_height, relwidth=1, relheight=rel_instruc_height)

    # Fills an area with a label an entry and 4 buttons, used for the number of maze rows, columns, and the cell size
    def fill_sizing_frame(self, frame, dimension, textvar, bulk_down, down, up, bulk_up):
        rel_label_height = 0
        rel_entry_height = 1 - rel_label_height

        rel_label_width = 0.3
        rel_entry_width = 0.3
        rel_button_width = (1 - (rel_label_width + rel_entry_width))/4
        current_x = 0

        side_label = tk.Label(frame, text=dimension)
        side_label.place(relheight=rel_entry_height, relwidth=rel_label_width)

        current_x += rel_label_width
        entry = tk.Entry(frame, textvariable=textvar, borderwidth=1, justify='center')
        entry.place(relx=current_x, rely=rel_label_height, relwidth=rel_entry_width, relheight=rel_entry_height)

        current_x += rel_entry_width
        bulk_down_button = tk.Button(frame, text='<<', command=bulk_down, borderwidth=1)
        bulk_down_button.place(relx=current_x, rely=rel_label_height, relwidth=rel_button_width, relheight=rel_entry_height)

        current_x += rel_button_width
        down_button = tk.Button(frame, text='<', command=down, borderwidth=1)
        down_button.place(relx=current_x, rely=rel_label_height, relwidth=rel_button_width, relheight=rel_entry_height)

        current_x += rel_button_width
        up_button = tk.Button(frame, text='>', command=up, borderwidth=1)
        up_button.place(relx=current_x, rely=rel_label_height, relwidth=rel_button_width, relheight=rel_entry_height)

        current_x += rel_button_width
        bulk_up_button = tk.Button(frame, text='>>', command=bulk_up, borderwidth=1) 
        bulk_up_button.place(relx=current_x, rely=rel_label_height, relwidth=rel_button_width, relheight=rel_entry_height)        

        return entry        

    # Creates the area where the maze rows, columns, and cell size are adjusted
    def fill_maze_dim_frame(self, base_frame):
        current_y = 0
        rel_frame_height = 1/4

        row_frame = tk.Frame(base_frame)
        row_frame.place(rely=current_y, relwidth=1, relheight=rel_frame_height)
        row_entry = self.fill_sizing_frame(row_frame, 'Rows:', self.rows_text, self.bulk_take_rows, self.take_rows, self.add_rows, self.bulk_add_rows)

        current_y += rel_frame_height
        col_frame = tk.Frame(base_frame)
        col_frame.place(rely=current_y, relwidth=1, relheight=rel_frame_height)
        col_entry = self.fill_sizing_frame(col_frame, 'Columns:', self.cols_text, self.bulk_take_cols, self.take_cols, self.add_cols, self.bulk_add_cols)

        current_y += rel_frame_height
        cell_frame = tk.Frame(base_frame)
        cell_frame.place(rely=current_y, relwidth=1, relheight=rel_frame_height)
        cell_entry = self.fill_sizing_frame(cell_frame, 'Cell Size (pxls):', self.cell_size_text, self.bulk_take_cell_size, self.take_cell_size, self.add_cell_size, self.bulk_add_cell_size)
        
        return row_entry, col_entry, cell_entry

    # Displays the current dimensions of the maze window
    def fill_window_dim_frame(self, frame, top_text, dim_text):
        rel_top_height = 0.3
        rel_dimensions_label_height = 1 - rel_top_height

        top_label = tk.Label(frame, text=top_text, bg=self.defaultbg)
        top_label.place(relheight=rel_top_height, relwidth=1)

        dimensions_label = tk.Label(frame, textvariable=dim_text, bg=self.defaultbg)
        dimensions_label.place(rely=rel_top_height, relheight=rel_dimensions_label_height, relwidth=1)

    # Ares for choosing the maze creation algorithm
    def fill_method_frame(self, frame):
        label = tk.Label(frame, text='Algorithm:')
        label.place(relheight=1)

        spin_box = tk.Spinbox(frame, values=self.algorithms, wrap=True, state='readonly', justify='center')
        spin_box.place(relx=self.mid_ref, relheight=1, relwidth=0.6, anchor='n')
        return spin_box

    # The button to create the maze and ensure there are enough rows, columns, and cell pixels
    def fill_launch_frame(self, frame):
        rel_button_height = 0.5
        rel_text_height = 1 - rel_button_height      
        button = tk.Button(frame, text='Launch', command=self.launch, bd=1)
        button.place(relx=self.mid_ref, relwidth=0.4, relheight=rel_button_height, anchor='n')

        label = tk.Label(frame, textvariable=self.dim_error_text, bg=self.defaultbg, fg='red')
        label.place(rely=rel_button_height, relheight=rel_text_height, relwidth=1)

    # Makes sure all the current info is on the screen
    def refresh_entries(self):
        self.rows_text.set(str(self.maze_rows))
        self.cols_text.set(str(self.maze_cols))
        self.cell_size_text.set(str(self.maze_cell_size))
        self.maze_window_width = (self.maze_cols+2) * self.maze_cell_size        
        self.maze_window_height = (self.maze_rows+2) * self.maze_cell_size
        self.window_dim_text.set(f'{self.maze_window_width} x {self.maze_window_height} pxls')

    # Starts the set up window
    def run(self):
        self.root.mainloop()

    # Starts the maze window if there are enough rows, columns, and cell pixels
    def launch(self):
        # check cell size is at least 4, and rows and cols are at least 5 first
        if self.maze_rows<5 or self.maze_cols<5 or self.maze_cell_size<4:
            base_msg = 'Invalid requirement(s): Not enough'
            error_msg = base_msg
            if self.maze_rows<5:
                error_msg += ' rows'
            if self.maze_cols<5:
                if error_msg != base_msg:
                    error_msg += ','
                error_msg += ' cols'
            if self.maze_cell_size<4:
                if error_msg != base_msg:
                    error_msg += ','
                error_msg += ' cell size'

            self.dim_error_text.set(error_msg)

        else:
            self.launch_maze = True
            self.chosen_algorithm = self.algorithm_box.get()
            self.root.destroy()



if __name__ == '__main__':
    w = Window()
    w.run()