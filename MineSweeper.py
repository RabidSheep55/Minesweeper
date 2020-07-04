'''
SOLVER LOGIC:
 - Open all cells around '0' cells
 - Mark mine positions using first level logic
 - Open all cells around those which have the right amount of mines tagged
'''


import re
import numpy as np

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
    pr(board)

    # Tools and constants
    H = len(board) # Height
    W = len(board[0]) # Width
    ALL_LOCS = set([(i, j) for i in range(H) for j in range(W)]) # All valid positions

    # Set stores positions which have been resolved and can be ignored
    resolved = set()

    i = 0
    while i < 5:

        ## Reveal cells around '0' cells
        for cell in set(tuple(pos) for pos in np.argwhere(board == "0")) - resolved:
            resolved.add(tuple(cell))
            for adjacent in near(cell, ALL_LOCS):
                board[adjacent] = open(*adjacent)

        ## Mark mine positions using first level logic
        mines = []
        for cell in set(tuple(pos) for pos in np.argwhere(board != "?")) - resolved:
            adjacent = near(cell, ALL_LOCS)
            possible = [pos for pos in adjacent if (board[pos] == "?" or board[pos] == "*")]

            # Number of possible adjacent mines corresponds to number on center
            if int(board[cell]) == len(possible):
                mines += possible
                resolved.add(cell)

        # Apply mine positions
        resolved |= set(mines)
        while mines:
            board[mines.pop()] = "*"

        ## Open all cells around those which have the right amount of mines tagged
        for cell in set(tuple(pos) for pos in np.argwhere(board != "?")) - resolved:
            adjacent = near(cell, ALL_LOCS)
            tagged = len([pos for pos in adjacent if board[pos] == "*"])

            # Number of adjacent tagged mines matches cell value
            if int(board[cell]) == tagged:
                for pos in [pos for pos in adjacent if board[pos] == "?"]:
                    board[pos] = open(*pos)

        i += 1

        pr(board)


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
