import pygame
import random

"""
10 x 20 square grid
shapes: S, Z, I, O, J, L, T
represented in order by 0 - 6
"""

pygame.font.init()

# GLOBAL VARIABLES
s_width = 800  # Width of the entire game window
s_height = 700  # Height of the entire game window
play_width = 300  # Width of the play area (10 blocks * 30 pixels per block)
play_height = 600  # Height of the play area (20 blocks * 30 pixels per block)
block_size = 30  # Size of each block

top_left_x = (s_width - play_width) // 2  # Top left x-coordinate of the play area
top_left_y = s_height - play_height  # Top left y-coordinate of the play area

# SHAPE FORMATS
# Define the different shapes and their rotations
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

# List of all shapes and their corresponding colors
shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]
# index 0 - 6 represent shape

# Piece class to represent each Tetris piece
class Piece(object):
    rows = 20  # Number of rows in the play area (y-axis)
    columns = 10  # Number of columns in the play area (x-axis)

    def __init__(self, column, row, shape):
        self.x = column  # Initial x-position
        self.y = row  # Initial y-position
        self.shape = shape  # Shape of the piece
        self.color = shape_colors[shapes.index(shape)]  # Color of the piece based on its shape
        self.rotation = 0  # Initial rotation state (0-3)

# Function to create the grid
# The grid contains the current state of the play area, including locked positions
def create_grid(locked_positions={}):
    grid = [[(0,0,0) for x in range(10)] for x in range(20)]  # Create a 20x10 grid filled with black (0,0,0)

    # Update the grid with locked positions
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            if (j,i) in locked_positions:
                c = locked_positions[(j,i)]
                grid[i][j] = c
    return grid

# Function to convert the shape format based on its current rotation
def convert_shape_format(shape):
    positions = []
    format = shape.shape[shape.rotation % len(shape.shape)]  # Get the correct rotation format

    # Iterate through the shape's format and determine the positions
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((shape.x + j, shape.y + i))

    # Adjust the positions to align with the play area
    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions

# Function to check if the current position of a piece is valid
def valid_space(shape, grid):
    accepted_positions = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)]
    accepted_positions = [j for sub in accepted_positions for j in sub]  # Flatten the list
    formatted = convert_shape_format(shape)

    # Check if each position of the piece is in the list of accepted positions
    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] > -1:
                return False

    return True

# Function to check if the player has lost
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:  # If any block is above the top of the play area
            return True
    return False

# Function to get a random shape
def get_shape():
    global shapes, shape_colors
    return Piece(5, 0, random.choice(shapes))  # Create a new piece at the top of the play area

# Function to draw text in the middle of the screen
def draw_text_middle(text, size, color, surface):
    font = pygame.font.SysFont('comicsans', size, bold=True)
    label = font.render(text, 1, color)

    # Center the text on the screen
    surface.blit(label, (top_left_x + play_width/2 - (label.get_width() / 2), top_left_y + play_height/2 - label.get_height()/2))

# Function to draw the grid lines (for visual reference)
def draw_grid(surface, row, col):
    sx = top_left_x
    sy = top_left_y
    for i in range(row):
        # Draw horizontal lines
        pygame.draw.line(surface, (128,128,128), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
        for j in range(col):
            # Draw vertical lines
            pygame.draw.line(surface, (128,128,128), (sx + j * block_size, sy), (sx + j * block_size, sy + play_height))

# Function to clear completed rows and shift everything above down
def clear_rows(grid, locked):
    inc = 0  # Number of rows to clear
    for i in range(len(grid)-1,-1,-1):  # Start from the bottom of the grid
        row = grid[i]
        if (0, 0, 0) not in row:  # If the row is completely filled
            inc += 1
            # Remove the locked positions for the cleared row
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue
    # Shift all rows above cleared rows down
    if inc > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + inc)
                locked[newKey] = locked.pop(key)

# Function to draw the next shape on the screen
def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('comicsans', 30)
    label = font.render('Next Shape', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)]

    # Draw the blocks of the next shape
    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                pygame.draw.rect(surface, shape.color, (sx + j * block_size, sy + i * block_size, block_size, block_size), 0)

    surface.blit(label, (sx + 10, sy - 30))

# Function to draw the main game window
def draw_window(surface):
    surface.fill((0, 0, 0))  # Fill the background with black
    # Draw the title
    font = pygame.font.SysFont('comicsans', 60)
    label = font.render('TETRIS', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    # Draw each block in the grid
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    # Draw grid and border
    draw_grid(surface, 20, 10)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

# Main game loop
def main():
    global grid

    locked_positions = {}  # Dictionary to store locked positions (x, y): (color)
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()  # Get the current piece
    next_piece = get_shape()  # Get the next piece
    clock = pygame.time.Clock()
    fall_time = 0
    level_time = 0
    fall_speed = 0.27  # Speed at which the pieces fall
    score = 0
    
    while run:
        grid = create_grid(locked_positions)  # Update the grid with locked positions
        fall_time += clock.get_rawtime()
        level_time += clock.get_rawtime()
        clock.tick()

        # Increase speed as time progresses
        if level_time / 1000 > 4:
            level_time = 0
            if fall_speed > 0.15:
                fall_speed -= 0.005
        
        # PIECE FALLING CODE
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # Event handling (keyboard input)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1

                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_UP:
                    # Rotate shape
                    current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
                    if not valid_space(current_piece, grid):
                        current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)

                if event.key == pygame.K_DOWN:
                    # Move shape down
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1

        shape_pos = convert_shape_format(current_piece)

        # Add piece to the grid for drawing
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                grid[y][x] = current_piece.color

        # If the piece hit the ground, lock it in place
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False

            # Check for cleared rows
            clear_rows(grid, locked_positions)
            score += 10

        draw_window(win)  # Draw the game window
        draw_next_shape(next_piece, win)  # Draw the next piece
        pygame.display.update()

        # Check if the player has lost
        if check_lost(locked_positions):
            run = False

    draw_text_middle("You Lost", 40, (255, 255, 255), win)
    pygame.display.update()
    pygame.time.delay(2000)

# Function to display the main menu
def main_menu():
    run = True
    while run:
        win.fill((0, 0, 0))
        draw_text_middle('Press any key to begin.', 60, (255, 255, 255), win)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.KEYDOWN:
                main()  # Start the game
    pygame.quit()

# Initialize the game window
win = pygame.display.set_mode((s_width, s_height))
pygame.display.set_caption('Tetris')

main_menu()  # Start the game