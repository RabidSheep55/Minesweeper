'''
SOLVER LOGIC:
 - Open all cells around '0' cells
 - Mark mine positions using first level logic
 - Open all cells around those which have the right amount of mines tagged
 - Mark mine positions using second level logic (1-1 and 1-2 patterns):
    - Find and store lists of codes on a temp map at unknowns susceptible of being solved using 1-1
    - Go through those locs, checking if 1-1 is present, and open cells
'''

# For colouring in commandline
class colors:
    # HEADER = '\033[95m'
    # OKBLUE = '\033[94m'
    # OKGREEN = '\033[92m'
    # WARNING = '\033[93m'
    # FAIL = '\033[91m'
    # ENDC = '\033[0m'
    # BOLD = '\033[1m'
    # UNDERLINE = '\033[4m'
    MINE = '\x1b[1;31;40m'
    RESOLVED = '\x1b[1;32;40m'
    UNKNOWN = "\x1b[1;34;40m"
    END = '\x1b[0m'

import re
import numpy as np
from collections import Counter

### Kata Solution code
# Utility function returns positions of valid adjacent cells
def near(pos, ALL_LOCS):
    # Create a set all cell positions around center (not including it)
    around = set([(i, j) for i in range(pos[0]-1, pos[0]+2) for j in range(pos[1]-1, pos[1]+2)]) - {tuple(pos)}
    # Only return the positions which intersect with valid positions
    return around & ALL_LOCS

# Solve minesweeper game
def solve_mine(map, n):
    # Store board data in a list
    board = np.array([row.split(' ') for row in map.split("\n")])

    # Tools and constants
    H = len(board) # Height
    W = len(board[0]) # Width
    ALL_LOCS = set([(i, j) for i in range(H) for j in range(W)]) # All valid positions

    # Variables
    resolved = set() # Positions which have been resolved and can be ignored
    opened = set() # Opened positions
    foundMines = 0

    fancyPrint(board, resolved)

    i = 0
    while foundMines < n:
        ## Reveal cells around '0' cells
        for cell in set(tuple(pos) for pos in np.argwhere(board == "0")) - resolved:
            resolved.add(tuple(cell))
            for adjacent in near(cell, ALL_LOCS) - resolved - opened:
                board[adjacent] = open(*adjacent)
                opened.add(adjacent)
                print(f"[{i}] Opened {adjacent} thanks to 0 cell")

        fancyPrint(board, resolved)

        ## Mark mine positions using first level logic
        mines = set()
        for cell in set(tuple(pos) for pos in np.argwhere(board != "?")) - resolved:
            adjacent = near(cell, ALL_LOCS)
            marked = set([pos for pos in adjacent if board[pos] == "*"])
            unknown = set([pos for pos in adjacent if board[pos] == "?"])

            # No unknown cells around, the cell is resolved
            if not len(unknown):
                resolved.add(cell)
            # Number of possible adjacent mines corresponds to number on center
            elif (int(board[cell]) == len(marked | unknown)) & len(unknown - resolved):
                foundMines += 1
                mines |= unknown
                resolved.add(cell) # Satisfied cells are resolved
                resolved |= unknown # Marked mines are resolved
                print(f"[{i}] Marking {unknown} thanks to 1st level logic from {cell}")

        # Apply mine positions
        while mines:
            board[mines.pop()] = "*"

        fancyPrint(board, resolved)

        ## Open all cells around those which have the right amount of mines tagged
        for cell in set(tuple(pos) for pos in np.argwhere(board != "?")) - resolved:
            adjacent = near(cell, ALL_LOCS)
            tagged = len([pos for pos in adjacent if board[pos] == "*"])

            # Number of adjacent tagged mines matches cell value
            if int(board[cell]) == tagged:
                for pos in [pos for pos in adjacent if board[pos] == "?"]:
                    board[pos] = open(*pos)
                    print(f"[{i}] Opened {pos} thanks to satifed cell {cell}")

        fancyPrint(board, resolved)

        ## Mark mine positions using second level logic (1-1 and 1-2 patterns)
        # 1-1 Pattern: If a current cell's mine count will be satisfied by all
        # mine placement options from another cell - then we can safely open the rest
        temp = np.copy(board).astype(np.dtype(list)) # Temporary board to mark cells
        highlighted = set() # Cells on which the 1-1 is going to be checked
        placed = {} # Dict tracks how many of each code was placed
        for cell in set(tuple(pos) for pos in np.argwhere(board != "?")) - resolved:
            adjacent = near(cell, ALL_LOCS)
            mines = [pos for pos in adjacent if board[pos] == "*"]
            unknowns = [pos for pos in adjacent if board[pos] == "?"]

            # Effective value of cell is 1?
            if int(board[cell]) - len(mines) == 1:
                highlighted.add(cell)
                # Add unique codes to unknowns around cell to perform logic later
                code = str(cell[0]*10 + cell[1])
                placed[code] = len(unknowns) # To compare with Counter later
                for pos in unknowns:
                    if type(temp[pos]) == str:
                        temp[pos] = [code]
                    else:
                        temp[pos] += [code]

        # Process the highlighted cells
        for cell in highlighted:
            adjacent = near(cell, ALL_LOCS)
            curr = str(cell[0]*10 + cell[1]) # Current cell code

            # Fetch code lists surrounding the current cell
            codes = [(temp[pos], pos) for pos in adjacent if type(temp[pos]) == list]
            # Flatten and warp with Counter
            count = Counter([code for pos in codes for code in pos[0]])
            # (cell sees all placed codes from a cell) (that isnt itself) (that would lead to opening unknowns)
            matches = [code for code in count.keys() if (count[code] == placed[code]) & (code != curr) & (count[code] < len(codes))]
            # Open all cells which don't contain the matched codes
            for match in matches:
                for code in codes:
                    if not match in code[0]:
                        board[code[1]] = open(*code[1])
                        print(f"[{i}] Opened {code[1]} thanks to 1-1 logic")

        fancyPrint(board, resolved)
        i += 1


### Cached function in the kata (have to recode for testing here)
def open(row, column):
    val = result[row][column]
    if val == 'x':
        print(f"Game over, exploded mine at {(column, row)}")
        quit()
    else:
        return val

### For Debugging
def pr(A):
    for line in A:
        print(*line, sep=" ")
    print()

def fancyPrint(board, resolved):
    i = 0
    for row in board:
        j = 0
        for item in row:
            if item == "*":
                print(f"{colors.MINE}*{colors.END}", end=" ")
            elif item == "?":
                print(f"{colors.UNKNOWN}?{colors.END}", end=" ")
            elif (i, j) in resolved:
                print(f"{colors.RESOLVED}{item}{colors.END}", end=" ")
            else:
                print(item, end=" ")
            j += 1
        i += 1
        print()
    print()

### Testing
gamemap = """
? ? ? ? ? ?
? ? ? ? ? ?
? ? ? 0 ? ?
? ? ? ? ? ?
? ? ? ? ? ?
0 0 0 ? ? ?
""".strip()

result = """
1 x 1 1 x 1
2 2 2 1 2 2
2 x 2 0 1 x
2 x 2 1 2 2
1 1 1 1 x 1
0 0 0 1 1 1
""".strip()

# Find number of mines
n = re.split('\s|\n', result).count('x')

# Format result in a usable way for the open function
result = [row.split(' ') for row in result.split("\n")]
# Solve the game
solve_mine(gamemap, n)
