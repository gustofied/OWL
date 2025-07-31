from dataclasses import dataclass
from copy import deepcopy


# We start with our Color Pieces

R, G, B, Y, M, C = range(1, 7)  
          
PRIMARY   = {R, G, B}

SECONDARY = {Y, M, C}  

LETTER = {                             
    0: '.',
    R: 'R',  G: 'G',  B: 'B',
    Y: 'Y',  M: 'M',  C: 'C',
}


# Maybe 0 should be a color here? At the same time the board/map will be handled by rerun

HEX = {                                
    R: '#FF0000',  G: '#00FF00',  B: '#0000FF',
    Y: '#FFFF00',  M: '#FF00FF',  C: '#00FFFF',
}


PAIR_TO_SECONDARY = {
    (R, G): Y, (G, R): Y,   
    (R, B): M, (B, R): M,
    (G, B): C, (B, G): C,
}

LOCK = {
    (Y, M): R, (M, Y): R,  
    (C, Y): G, (Y, C): G,
    (M, C): B, (C, M): B,
}           



# The board, we do 6x5 in this example to keep it simple ;), and you play the board like from on top, just as connect four. Same game "map"

class Board:
    def __init__(self, cols = 5, rows = 6):
        self.cols = cols
        self.rows = rows
        self.grid = [[0] * cols for _ in range(rows)]
        # These store the coordinates of the two pieces that were last turned into secondary colors during the most recent mix. If no mix occurred, they remain None.
        self.colour_coords = self.nbr_colour_coords = None 
        # Tracks which cells are permanently locked after a trio-mix
        self.locked = [[False] * cols for _ in range(rows)]


    def __str__(self) -> str:
        lines = [
            " ".join(LETTER[cell] for cell in row)
            for row in reversed(self.grid)      
        ]
        return "\n".join(lines)
    
    def drop(self, col, colour) -> None:
        if colour not in PRIMARY:
            raise ValueError("Only R, G or B can be dropped")
        if not (0 <= col < self.cols):
            raise IndexError("Column out of range")
        for row in range(self.rows):          
            if self.grid[row][col] == 0:
                self.grid[row][col] = colour
                self.pair_mix(row, col)       
                self.trio_mix(row, col)
                return
        raise ValueError("Column is full")
    
    # Alchemy
    

    # ---------- PASS 1 : le mixing of pairs ----------
    def pair_mix(self, row, col):
        """
        Look at the token we just dropped.   If one of its orthogonal
        neighbours is a *different* primary, convert that pair to the
        appropriate secondary.  Only ONE mix can happen per move.
        """
        colour = self.grid[row][col]
        # Scan neighbours clockwise: Right, Down, Left
        for d_row, d_col in ((0, 1), (-1, 0), (0, -1)):
            nbr_row, nbr_col = row + d_row, col + d_col
            if 0 <= nbr_row < self.rows and 0 <= nbr_col < self.cols:
                # Skip already-locked neighbours
                if self.locked[nbr_row][nbr_col]:
                    continue
                nbr_colour = self.grid[nbr_row][nbr_col]
                if nbr_colour in PRIMARY and nbr_colour != colour:
                    secondary = PAIR_TO_SECONDARY[(colour, nbr_colour)]
                    self.grid[row][col]            = secondary
                    self.grid[nbr_row][nbr_col]    = secondary
                    self.colour_coords, self.nbr_colour_coords = (row, col), (nbr_row, nbr_col)
                    return                             
        self.colour_coords = self.nbr_colour_coords = None                

    # ---------- PASS 2 : le mixing of triples/trios ----------
    def trio_mix(self, row, col):
        """
        If a pair is created, there is a second possible phase, for each colour in
        the pair_mix (there are 0, 1, or 2),
        scan neighbours clockwise.  The first which will be the colour dropped
        colour, scans, then the "neighbour" of the pair gets scanned. If one of them finds
        a complementary secondary as neighbour, the three of the turn into the
        resulting primary we have then a trio mix, they are also locked colour and 
        cant change in the future, hence can't be part of future mixes.
        """
        for tertiary_pos in (self.colour_coords, self.nbr_colour_coords):
            if not tertiary_pos:
                continue

            tertiary_row, tertiary_col = tertiary_pos
            # Skip if this cell is already locked (safety check)
            if self.locked[tertiary_row][tertiary_col]:
                continue

            tertiary_colour = self.grid[tertiary_row][tertiary_col]   

            for d_row, d_col in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                nbr_row, nbr_col = tertiary_row + d_row, tertiary_col + d_col
                if 0 <= nbr_row < self.rows and 0 <= nbr_col < self.cols:
                    # Skip locked neighbours
                    if self.locked[nbr_row][nbr_col]:
                        continue
                    nbr_colour = self.grid[nbr_row][nbr_col]
                    primary = LOCK.get((tertiary_colour, nbr_colour))
                    if primary:
                        # Convert colours
                        self.grid[tertiary_row][tertiary_col] = primary
                        self.grid[nbr_row][nbr_col]           = primary
                        self.grid[row][col]                   = primary
                        # Lock the trio permanently
                        self.locked[tertiary_row][tertiary_col] = True
                        self.locked[nbr_row][nbr_col]           = True
                        self.locked[row][col]                   = True
                        return       
              
# The players move, the player decides which column to drop his piece and also which color it is, it could be red, green or blue
@dataclass(frozen=True, eq=True)
class Action:
    col: int
    colour: int  

class GameState:
    def __init__(self, board=None, player=1, last_action=None):
        self.board        = board or Board()
        self.player       = player
        self.last_action  = last_action

    
    def copy(self):
        return GameState(
            board       = deepcopy(self.board), # deepcopy change in future to something more optimal.. :)
            player      = self.player,
            last_action = self.last_action
        )
    

    # Here we check which columns are available (this is done by checking the top cell, so rows - 1 and column)
    # ofc we then fan out all colour choices on each aviablbel column too
    # this results in all legal actions
    def get_legal_actions(self):
        actions = []
        top_row = self.board.rows - 1
        for col in range(self.board.cols):
            if self.board.grid[top_row][col] == 0:         
                for colour in (R, G, B):
                    actions.append(Action(col, colour))
        return actions
    
    # Creates a new game state by applying the given action. This updates the board, switches the player, and records the last action.
    def perform_action(self, action: Action):
        new = self.copy()
        new.board.drop(action.col, action.colour)
        new.player = 3 - self.player                   
        new.last_action = action
        return new

    def is_terminal(self):
        """
        The game ends when there are no empty cells (0) left on the board.
        Returns True if the board is full, otherwise False.
        """
        for row in self.board.grid:
            for cell in row:
                if cell == 0:           
                    return False
        return True                 


    def get_result(self):
        """
        Score the finished game from the perspective of the *last* mover.
        +1  → last mover wins
        -1  → last mover loses
        0  → draw
        """
        green_cells = 0
        red_cells   = 0

        for row in self.board.grid:
            for cell in row:
                if cell == G:
                    green_cells += 1
                elif cell == R:
                    red_cells += 1

        if green_cells == red_cells:
            return 0
        
        winner      = 1 if green_cells > red_cells else 2
        last_mover  = 3 - self.player       

        return 1 if winner == last_mover else -1
