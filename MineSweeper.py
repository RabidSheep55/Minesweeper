'''
SOLVER LOGIC:
 - Open all cells around '0' cells
 - Mark mine positions using first level logic
 - Open all cells around those which have the right amount of mines tagged
 - Select and open safe cells using second level logic (1-1 pattern):
    - Find and store lists of codes on a temp map at unknowns susceptible of being solved using 1-1,
      (while doing so, mark effective 2 cells to use for 1-2 checking later)
    - Go through those locs, checking if 1-1 or 1-2 is present, and open cells accordingly
 - If number of unknowns equals remainder of mines - tag them
 - If there's only one mine left, mark position which satisfies all unresolved cells
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
    HIGHLIGHT = '\x1b[1;35;40m'
    END = '\x1b[0m'

### Kata Solution code
import numpy as np
from collections import Counter

DEBUG = True

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

    if DEBUG: fancyPrint(board, resolved)

    MAX_LOOPS = 20
    didSomething = True

    i = 0
    # Iterate while more mines to find or board not fully revelead, and not stuck in infinite loop
    while (foundMines != n) & (i < MAX_LOOPS) & didSomething:
        didSomething = False

        ## Reveal cells around '0' cells
        for cell in set(tuple(pos) for pos in np.argwhere(board == "0")) - resolved:
            resolved.add(tuple(cell))
            for adjacent in near(cell, ALL_LOCS) - resolved - opened:
                board[adjacent] = open(*adjacent)
                opened.add(adjacent)
                if DEBUG: print(f"[{i}] Opened {adjacent} thanks to 0 cell")
                didSomething = True

        if DEBUG: fancyPrint(board, resolved)

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
                foundMines += len(unknown - resolved)
                mines |= unknown - resolved
                resolved.add(cell) # Satisfied cells are resolved
                resolved |= unknown  # Marked mines are resolved
                if DEBUG: print(f"[{i}] Marking {unknown} thanks to 1st level logic from {cell}")
                didSomething = True

            # FOR DEBUGGING
            # elif (int(board[cell]) < len(marked)):
            #     print(f"[{i}] CELL {cell} OVERLOADED")
            #     fancyPrint(board, resolved, [cell])
            #     quit()

        # Apply mine positions
        while mines:
            board[mines.pop()] = "*"

        if DEBUG: fancyPrint(board, resolved)

        ## Open all cells around those which have the right amount of mines tagged
        for cell in set(tuple(pos) for pos in np.argwhere(board != "?")) - resolved:
            adjacent = near(cell, ALL_LOCS)
            tagged = len([pos for pos in adjacent if board[pos] == "*"])

            # Number of adjacent tagged mines matches cell value
            if int(board[cell]) == tagged:
                for pos in [pos for pos in adjacent if board[pos] == "?"]:
                    board[pos] = open(*pos)
                    if DEBUG: print(f"[{i}] Opened {pos} thanks to satifed cell {cell}")
                    didSomething = True

        if DEBUG: fancyPrint(board, resolved)

        ## Select and open/mark cells using second level logic (1-1 and 1-2 patterns)
        # 1-1 Pattern: If a current cell's mine count will be satisfied by all
        # mine placement options from another cell - then we can safely open the rest
        # Also selecting all effective 2 cells to use for 1-2 logic later
        temp = np.copy(board).astype(np.dtype(list)) # Temporary board to mark cells
        effectiveOnes = set() # Cells on which the 1-1 is going to be checked
        effectiveTwos = set() # Cells on which the 1-2 is going to be checked
        placed = {} # Dict tracks how many of each code was placed
        for cell in set(tuple(pos) for pos in np.argwhere(board != "?")) - resolved:
            adjacent = near(cell, ALL_LOCS)
            mines = [pos for pos in adjacent if board[pos] == "*"]
            unknowns = [pos for pos in adjacent if board[pos] == "?"]

            # Effective value of cell is 1 and can not be solved using first level
            # NOTE: could technically open cell - come back here when needing more speed
            if (int(board[cell]) - len(mines) == 1) & (len(unknowns) != 1):
                effectiveOnes.add(cell)
                # Add unique codes to unknowns around cell to perform logic later
                code = str(cell[0]) + str(cell[1])
                placed[code] = len(unknowns) # To compare with Counter later
                for pos in unknowns:
                    if type(temp[pos]) == str:
                        temp[pos] = [code]
                    else:
                        temp[pos] += [code]
            # Effective value of cell is 2 and can not be solved using first level
            if (int(board[cell]) - len(mines) == 2) & (len(unknowns) == 3):
                effectiveTwos.add(cell)


        # Process the effectiveOnes cells - open valid 1-1 patterns
        opened = set()
        for cell in effectiveOnes:
            adjacent = near(cell, ALL_LOCS)
            curr = str(cell[0]) + str(cell[1]) # Current cell code

            # Fetch code lists surrounding the current cell
            codes = [(temp[pos], pos) for pos in adjacent if type(temp[pos]) == list]
            # Flatten and warp with Counter
            count = Counter([code for pos in codes for code in pos[0]])
            # (cell sees all placed codes from a cell) (that isnt itself) (that would lead to opening unknowns)
            matches = [code for code in count.keys() if (count[code] == placed[code]) & (code != curr) & (count[code] < len(codes))]
            # Open all cells which don't contain the matched codes
            for match in matches:
                for code in codes:
                    if (not match in code[0]) & (not code[1] in opened):
                        if DEBUG: print(f"[{i}] Opening {code[1]} thanks to 1-1 logic from {cell}")
                        opened.add(code[1])
                        board[code[1]] = open(*code[1])
                        didSomething = True

        if DEBUG: fancyPrint(board, resolved)

        # Tag effectiveTwo cells which match the 1-2 pattern
        for cell in effectiveTwos:
            adjacent = near(cell, ALL_LOCS)
            curr = str(cell[0]) + str(cell[1]) # Current cell code

            # Fetch unknown that might have not been tagged in temp
            unknown = [pos for pos in adjacent if temp[pos] == "?"]
            # Fetch code lists surrounding the current cell
            codes = [(temp[pos], pos) for pos in adjacent if type(temp[pos]) == list]
            # Flatten and warp with Counter
            count = Counter([code for pos in codes for code in pos[0]])
            # (cell sees all placed codes from a cell) (that isnt itself) (that would lead to marking unknowns (num of unknowns is len(codes)))
            matches = [code for code in count.keys() if (count[code] == placed[code]) & (code != curr)]

            # Mark all cells which don't contain the matched codes
            for match in matches:
                for code in codes:
                    if (not match in code[0]) & (not code[1] in resolved):
                        foundMines += 1
                        resolved.add(code[1])
                        board[code[1]] = "*"
                        if DEBUG: print(f"[{i}] Marking {code[1]} thanks to 1-2 logic from {cell}")
                        didSomething = True

                # There's a match - the cell to mark has to be the only unknown
                if len(unknown):
                    if not unknown[0] in resolved:
                        foundMines += 1
                        resolved.add(unknown[0])
                        board[unknown[0]] = "*"
                        if DEBUG: print(f"[{i}] Marking {unknown[0]} thanks to 1-2 logic from {cell}")
                        didSomething = True
                        break


        # If number of unknowns equals remainder of mines - tag them
        # NOTE: Using np.where here instead of argwhere will cause the count of '?' to be one less than reality for some reason...
        unknowns = np.argwhere(board == "?")
        if (len(unknowns) == n - foundMines) & bool(len(unknowns)):
            foundMines += len(unknowns)
            for cell in unknowns:
                board[tuple(cell)] = "*"
                resolved.add(tuple(cell))
            if DEBUG: print(f"[{i}] Marked all remaining unknowns as they have to be mines")

        # If there's only one mine left, mark position which satisfies all unresolved cells
        elif n - foundMines == 1:
            unresolved = set(tuple(pos) for pos in np.argwhere(board != "?")) - resolved
            codes = set([str(pos[0]) + str(pos[1]) for pos in unresolved])

            # If a cell contains all codes from unresolved cells, its the final mine
            for cell in unknowns:
                if set(temp[tuple(cell)]) == codes:
                    foundMines += 1
                    resolved.add(tuple(cell))
                    board[tuple(cell)] = "*"
                    if DEBUG: print(f"[{i}] Marked last mine as it satifies all unresolved cells")

        # TODO: Implement a guessing algorithm - makes initial mine guess and tests if branching decisions
        #       make sense based on number of mines remaining

        fancyPrint(board, resolved)
        i += 1

    # Game is over, just need to reveal remaining unknowns
    if (foundMines == n):
        unknowns = np.argwhere(board == "?")
        for cell in unknowns:
            cell = tuple(cell)
            board[cell] = open(*cell)
            resolved.add(cell)
        if DEBUG: print(f"[{i}] Opened all remaining cells, all mines found")

    # Handle exit condtions
    if foundMines == n:
        print(f"SUCCESS! Found {foundMines}/{n} mines after {i} iterations")
        return "\n".join([' '.join(line) for line in board]).replace('*', "x")

    if i == MAX_LOOPS:
        print("Max Loops exceeded")
        return "MAX LOOPS EXCEEDED"

    if not didSomething:
        print(f"NoActionPerformed: Start of infinite looping caught - Aborted at {i} iterations")
        print(f"{foundMines}/{n} mines were marked")
        return "?"

### Cached function in the kata (have to recode for testing here)
def open(row, column, board=None, resolved=None, highlight=[]):
    val = result[row][column]
    if val == 'x':
        print(f"Game over, exploded mine at {(row, column)}")
        # board[row, column] = "#"
        # fancyPrint(board, resolved, highlight + [(row, column)])
        quit()
    else:
        return val

### For Debugging
# Simple print board
def pr(A):
    for line in A:
        print(*line, sep=" ")
    print()

# Print board with colors
def fancyPrint(board, resolved, highlight=[]):
    i = 0
    for row in board:
        j = 0
        for item in row:
            if (i, j) in highlight:
                print(f"{colors.HIGHLIGHT}{item}{colors.END}", end=" ")
            elif item == "*" or item == "x":
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
from tests import tests
import re

# 2, 3 are 50%, should return "?"
# FAILS: 12, 14 <- need trial and error logic here (relies on knowldge of number of mines remaining)
testID = 12
gamemap, result = (tests[testID]["gamemap"], tests[testID]["result"])

# Find number of mines
n = re.split('\s|\n', result).count('x')

# Format result in a usable way for the open function
result = [row.split(' ') for row in result.split("\n")]
# Solve the game
ans = solve_mine(gamemap, n)
print(ans)
# fancyPrint(result, set())
