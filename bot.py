import random
    
class Cell():

    '''
    White = Empty
    Green, Red = Players
    '''

    def __init__(self, color, value):
        self.color = color
        self.value = value

config = {
        'columns': 6,
        'rows': 6,
        'players': 2,
        'mark': 'RED',
        'threshold': {
            'corner': 1,
            'edge': 2,
            'center': 3
        }
    }

board = [[Cell('WHITE', 0) for _ in range(config['columns'])] for __ in range(config['rows'])]
N_STEPS = 5


def position(config, cell):
    
    if cell in [(0, 0), (0, config['columns']), (config['rows'], 0), (config['rows'], config['columns'])]:
        return 'corner'
    
    if cell[0] in [0, config['rows']] or cell[1] in [0, config['colums']]:
        return 'edge'

    return 'center'


# returns a grid with a next move played
def drop_piece(board, cell, mark, config):
    
    next_grid = board.copy()
    pos = position(config, cell)
    if cell.value < config['threshold'][pos]:
        cell.value += 1
    else:
        cell.value = 0

        if pos == 'corner':
            if cell[0] == 0 and cell[1] == 0:
                next_cell = (cell[0], 1)
                drop_piece(next_grid, next_cell, mark, config)
                next_cell = (1, cell[1])
                drop_piece(next_grid, next_cell, mark, config)

            elif cell[0] == 0 and cell[1] == config['columns']-1:
                next_cell = (cell[0], config['columns']-2)
                drop_piece(next_grid, next_cell, mark, config)
                next_cell = (1, cell[1])
                drop_piece(next_grid, next_cell, mark, config)

            elif cell[0] == config['rows']-1 and cell[1] == 0:
                next_cell = (cell[0], 1)
                drop_piece(next_grid, next_cell, mark, config)
                next_cell = (1, cell[1])
                drop_piece(next_grid, next_cell, mark, config)

            elif cell[0] == config['rows']-1 and cell[1] == config['columns']-1:
                next_cell = (cell[0], config['columns']-2)
                drop_piece(next_grid, next_cell, mark, config)
                next_cell = (config['rows']-2, cell[1])
                drop_piece(next_grid, next_cell, mark, config)

        elif pos == 'edge':
            if cell[0] == 0:
                next_cells = [(cell[0], cell[1]+1),
                              (cell[0], cell[1]-1),
                              (cell[0]+1, cell[1])]
                for next_cell in next_cells:
                    drop_piece(next_grid, next_cell, mark, config)

            elif cell[0] == config['row'] - 1:
                next_cells = [(cell[0], cell[1]+1),
                              (cell[0], cell[1]-1),
                              (cell[0]-1, cell[1])]
                for next_cell in next_cells:
                    drop_piece(next_grid, next_cell, mark, config)
            elif cell[1] == 0:
                next_cells = [(cell[0]+1, cell[1]),
                              (cell[0]-1, cell[1]),
                              (cell[0], cell[1]+1)]
                for next_cell in next_cells:
                    drop_piece(next_grid, next_cell, mark, config)
            else:
                next_cells = [(cell[0]+1, cell[1]),
                              (cell[0]-1, cell[1]),
                              (cell[0], cell[1]-1)]
                for next_cell in next_cells:
                    drop_piece(next_grid, next_cell, mark, config)

        else:
            next_cell = [(cell[0]+1, cell[1]),
                         (cell[0]-1, cell[1]),
                         (cell[0], cell[1]+1),
                         (cell[0], cell[1]-1)]
            for next_cell in next_cells:
                drop_piece(next_grid, next_cell, mark, config)

    return next_grid


# check each critical condition for conditions
def check_window(window, num_discs, piece, config):
    return (window.count(piece) == num_discs and window.count(0) == config.inarow-num_discs)
    

# count critical conditions
def count_windows(grid, num_discs, piece, config):
    num_windows = 0
    # horizontal
    for row in range(config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[row, col:col+config.inarow])
            if check_window(window, num_discs, piece, config):
                num_windows += 1
    # vertical
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns):
            window = list(grid[row:row+config.inarow, col])
            if check_window(window, num_discs, piece, config):
                num_windows += 1
    # positive diagonal
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row+config.inarow), range(col, col+config.inarow)])
            if check_window(window, num_discs, piece, config):
                num_windows += 1
    # negative diagonal
    for row in range(config.inarow-1, config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row-config.inarow, -1), range(col, col+config.inarow)])
            if check_window(window, num_discs, piece, config):
                num_windows += 1
    return num_windows


# function to calculate the heuristics
def get_heuristic(grid, mark, config):
    num_threes = count_windows(grid, 3, mark, config)
    num_fours = count_windows(grid, 4, mark, config)
    num_threes_opp = count_windows(grid, 3, mark%2+1, config)
    num_fours_opp = count_windows(grid, 4, mark%2+1, config)
    score = num_threes - 1e2*num_threes_opp - 1e4*num_fours_opp + 1e6*num_fours
    return score


#initializes the mini-max tree
def score_move(board, cell, mark, config, nsteps):
    next_grid = drop_piece(board, cell, mark, config)
    score = minimax(next_grid, nsteps-1, False, mark, config)
    return score


# helper function for terminal node
def is_terminal_window(window, config):
    return window.count(1) == config.inarow or window.count(2) == config.inarow


# To check if this is a terminal node in the tree
def is_terminal_node(grid, config):
    # Check for draw 
    if list(grid[0, :]).count(0) == 0:
        return True
    # Check for win: horizontal, vertical, or diagonal
    # horizontal 
    for row in range(config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[row, col:col+config.inarow])
            if is_terminal_window(window, config):
                return True
    # vertical
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns):
            window = list(grid[row:row+config.inarow, col])
            if is_terminal_window(window, config):
                return True
    # positive diagonal
    for row in range(config.rows-(config.inarow-1)):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row+config.inarow), range(col, col+config.inarow)])
            if is_terminal_window(window, config):
                return True
    # negative diagonal
    for row in range(config.inarow-1, config.rows):
        for col in range(config.columns-(config.inarow-1)):
            window = list(grid[range(row, row-config.inarow, -1), range(col, col+config.inarow)])
            if is_terminal_window(window, config):
                return True
    return False


# Change this to alpha-beta pruning
def minimax(node, depth, maximizingPlayer, mark, config):
    is_terminal = is_terminal_node(node, config)
    valid_moves = [c for c in range(config.columns) if node[0][c] == 0]
    if depth == 0 or is_terminal:
        return get_heuristic(node, mark, config)
    if maximizingPlayer:
        value = -np.Inf
        for col in valid_moves:
            child = drop_piece(node, col, mark, config)
            value = max(value, minimax(child, depth-1, False, mark, config))
        return value
    else:
        value = np.Inf
        for col in valid_moves:
            child = drop_piece(node, col, mark%2+1, config)
            value = min(value, minimax(child, depth-1, True, mark, config))
        return value


# Will search for best moves and gives the final move
def my_agent(board, config):
    
    valid_moves = []
    
    for i in range(config.rows):
        for j in range(config.columns):
            cell = board[i][j]
            if cell.color == 'WHITE' or config['mark']:
                valid_moves.append((i, j))

    scores = dict(zip(valid_moves, [score_move(board, cell, config['mark'], config, N_STEPS) for cell in valid_moves]))
    
    max_cols = [key for key in scores.keys() if scores[key] == max(scores.values())]
    
    return random.choice(max_cols)
