#from utils import *

assignments = []

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values, assign_value = assign_value):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    # Eliminate the naked twins as possibilities for their peers
    
    for unit in unitlist:
        # set of pairs seen
        # given that the way possible values are
        # defined and eliminated is sorted
        # there was no need to hash "23" differently from
        # "32"
        seen = set()
        # i ended up needing this because downstream I ran the
        # risk of deleting the chars from the naked twins
        # themselves. so this set helps me remember them
        twins = set()
        # this was all I had initially and could probably have 
        # gotten rid of it and broken the string up into chars
        # downstream but the set would be fast to check for 
        # existence
        twinParts = set()

        # identify naked twins
        for pos in unit:
            cur = values[pos]
            if len(cur) == 2 and cur in seen:
                twins.add(cur)
                for char in cur:
                    twinParts.add(char)
                continue
            seen.add(cur)

        # zap the twin parts from all peers 
        # except the naked twins themselves
        if len(twinParts) > 0:
            for pos in unit:
                if values[pos] not in twins:
                    for x in twinParts:
                        assign_value(values, pos, values[pos].replace(x, ""))
    return values

def search(values, assign_value):
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values, naked_twins, assign_value)
    if values == False:
        return False
    
    # Choose one of the unfilled squares with the fewest possibilities
    MIN = 10
    MINPOS = "ZZ"
    for pos in values:
        if( len(values[pos]) > 1 and len(values[pos]) < MIN):
            MINPOS = pos
            MIN = len(values[pos])
            
    if MINPOS == "ZZ":
        return values
        
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    choices = values[MINPOS]
    for choice in choices:
        myValues = {pos:values[pos] if pos != MINPOS else choice for pos in values}
        found = search(myValues, assign_value)
        if found != False:
            return found
    return False

# *********************************
# Pasting this in here. Cannot submit because I guess
# we only send the source in this file and imports cannot
# be done. 
# *********************************
rows = 'ABCDEFGHI'
cols = '123456789'

def cross(a, b):
    return [s+t for s in a for t in b]

boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diagonal_units_1 = [[rows[i]+cols[i] for i in range(len(rows))]]
diagonal_units_2 = [[rows[i]+cols[len(cols)-1-i] for i in range(len(rows))]]
#diagonal_units = [list({k:True for pair in [[rows[i]+cols[i],rows[i]+cols[len(cols)-1-i]] for i in range(len(rows))] for k in pair }.keys())]
unitlist = row_units + column_units + square_units + diagonal_units_1 + diagonal_units_2
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Input: A grid in string form.
    Output: A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))
    
def eliminate(values, assignValue):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assignValue(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values, assignValue):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assignValue(values, dplaces[0], digit)
    return values

def reduce_puzzle(values, naked_twins, assignValue):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = naked_twins(values, assignValue)
        values = eliminate(values, assignValue)
        values = only_choice(values, assignValue)
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values
# *********************************
# End of Utils
# *********************************

def solve(grid, assign_value = assign_value):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid), assign_value)

if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid, assign_value))

    print(" ")
    diag_sudoku_grid2 = '.....6....59.....82....8....45........3........6..3.54...325..6..................'
    display(solve(diag_sudoku_grid2, assign_value))    

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
