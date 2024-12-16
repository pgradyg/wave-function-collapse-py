import pygame
import random
import heapq

tile_colors = {
    "trees": (29, 108, 29),
    "grass": (34, 139, 34),
    "shore": (238, 214, 175),
    "water": (65, 105, 225),
    "ocean": (38, 69, 132)
}

# sample pattern
pattern = [
    ["trees", "trees", "grass"],
    ["grass", "grass", "shore"],
    ["grass", "shore", "water"],
    ["shore", "shore", "water"],
    ["water", "water", "ocean"],
    ["ocean", "ocean", "ocean"]
]

def get_constraints(pattern):
    constraints = {}
    for row in range(len(pattern)):
        for col in range(len(pattern[0])):
            tile = pattern[row][col]
            if tile not in constraints:
                constraints[tile] = set()
            if row > 0:
                constraints[tile].add(pattern[row - 1][col])
            if row < len(pattern) - 1:
                constraints[tile].add(pattern[row + 1][col])
            if col > 0:
                constraints[tile].add(pattern[row][col - 1])
            if col < len(pattern[0]) - 1:
                constraints[tile].add(pattern[row][col + 1])
    return constraints

constraints = get_constraints(pattern)
print(constraints)

class Tile:
    def __init__(self, row, col, actual_tile=None):
        self.row = row
        self.col = col
        self.actual_tile = actual_tile
        if actual_tile:
            self.possible_tiles = set([actual_tile])
            self.constraints = constraints[actual_tile]
        else:
            self.possible_tiles = set(list(tile_colors.keys()))
            self.constraints = set(list(tile_colors.keys()))
    
    # Dunder methods for comparing entropy
    def __lt__(self, other):
        return len(self.possible_tiles) < len(other.possible_tiles)
    
    def __le__(self, other):
        return len(self.possible_tiles) <= len(other.possible_tiles)
    
    def __eq__(self, other):
        return len(self.possible_tiles) == len(other.possible_tiles)
    
    def __ne__(self, other):
        return len(self.possible_tiles) != len(other.possible_tiles)

    def __gt__(self, other):
        return len(self.possible_tiles) > len(other.possible_tiles)
    
    def __ge__(self, other):
        return len(self.possible_tiles) >= len(other.possible_tiles)



# Set constants
ROWS = 40
COLS = 40
TILE_SIZE = 20

# Set screen
screen = pygame.display.set_mode((COLS * TILE_SIZE, ROWS * TILE_SIZE))


# Define initial frequencies
frequencies = {
    "grass": 3,
    "shore": 2,
    "water": 2,
    "ocean": 4,
    "trees": 3
}


# Initialize the grid with superposition (all possible tiles)
grid = [[Tile(i, j) for i in range(COLS)] for j in range(ROWS)]

def draw_grid(grid):
    surface = pygame.Surface((COLS * TILE_SIZE, ROWS * TILE_SIZE))
    pixel_array = pygame.surfarray.pixels3d(surface)
    for row in range(ROWS):
        for col in range(COLS):
            tile = grid[row][col]
            if tile.actual_tile:
                pixel_array[row * TILE_SIZE:(row + 1) * TILE_SIZE, col * TILE_SIZE:(col + 1) * TILE_SIZE] = tile_colors[tile.actual_tile]
            else:
                possible_tiles = tile.possible_tiles
                num_tiles = len(possible_tiles)

                if num_tiles > 0:
                    avg_color = [0, 0, 0]
                    for possible_tile in possible_tiles:
                        avg_color[0] += tile_colors[possible_tile][0]
                        avg_color[1] += tile_colors[possible_tile][1]
                        avg_color[2] += tile_colors[possible_tile][2]
                    avg_color = tuple([(c // num_tiles) for c in avg_color])
                    pixel_array[row * TILE_SIZE:(row + 1) * TILE_SIZE, col * TILE_SIZE:(col + 1) * TILE_SIZE] = avg_color
    del pixel_array
    screen.blit(surface, (0, 0))

# collapse a cell into a value
def collapse_cell(row, col):
    tile = grid[row][col]

    # return if tile already collapsed
    if tile.actual_tile:
        return
    else:
        # collapse the tile based on possiblities and their weights
        possible_tiles = tile.possible_tiles
        if possible_tiles:
            weights = [frequencies[tile] for tile in possible_tiles]
            tile.actual_tile = random.choices(list(possible_tiles), weights=weights)[0]
            tile.possible_tiles = set([tile.actual_tile])
            tile.constraints = constraints[tile.actual_tile]
        # propagate constraints
        propagate_constraints(row, col)
    

def propagate_constraints(row, col):
    # need to update possible tiles and constraints for neighbors
    stack = [(row, col)]
    visited = set()
    while stack:
        row, col = stack.pop()
        tile = grid[row][col]
        visited.add((row, col))

        if row > 0:
            up_tile = grid[row - 1][col]
            up_tile.possible_tiles = set([t for t in up_tile.possible_tiles if t in tile.constraints])
            up_tile.constraints = set()
            for t in up_tile.possible_tiles:
                up_tile.constraints.update(constraints[t])
            if (row - 1, col) not in visited:
                stack.append((row - 1, col))

        if row < ROWS - 1:
            down_tile = grid[row + 1][col]
            down_tile.possible_tiles = set([t for t in down_tile.possible_tiles if t in tile.constraints])
            down_tile.constraints = set()
            for t in down_tile.possible_tiles:
                down_tile.constraints.update(constraints[t])
            if (row + 1, col) not in visited:
                stack.append((row + 1, col))

        if col > 0:
            left_tile = grid[row][col - 1]
            left_tile.possible_tiles = set([t for t in left_tile.possible_tiles if t in tile.constraints])
            left_tile.constraints = set()
            for t in left_tile.possible_tiles:
                left_tile.constraints.update(constraints[t])
            if (row, col - 1) not in visited:
                stack.append((row, col - 1))

        if col < COLS - 1:
            right_tile = grid[row][col + 1]
            right_tile.possible_tiles = set([t for t in right_tile.possible_tiles if t in tile.constraints])
            right_tile.constraints = set()
            for t in right_tile.possible_tiles:
                right_tile.constraints.update(constraints[t])
            if (row, col + 1) not in visited:
                stack.append((row, col + 1))
    return

def generate_map():
    priority_queue = []
    for row in range(ROWS):
        for col in range(COLS):
            heapq.heappush(priority_queue, grid[row][col])
    x = 0
    while priority_queue:
        tile = heapq.heappop(priority_queue)
        collapse_cell(tile.row, tile.col)
        if x % 10 == 0:
            draw_grid(grid)
            pygame.display.flip()
        x += 1

 


draw_grid(grid)
pygame.display.flip()

# Main Game Loop
running = True
ran = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if not ran:
        generate_map()
        draw_grid(grid)
        pygame.display.flip()
        print('done')
        ran = True


pygame.quit()