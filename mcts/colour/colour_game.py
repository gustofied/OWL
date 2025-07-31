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
        self._sec1 = self._sec2 = None 


    def __str__(self) -> str:
        lines = [
            " ".join(LETTER[value] for value in row)
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
                self.secondary_lock(row, col)
                return
        raise ValueError("Column is full")
    
    # Alchemy
    
    def pair_mix(self, drop_row, drop_col):
        """
        Look at the token we just dropped.   If one of its orthogonal
        neighbours is a *different* primary, convert that pair to the
        appropriate secondary.  Only ONE mix can happen per move.
        """
        centre_colour = self.grid[drop_row][drop_col]
        # Scan neighbours clockwise: Right, Down, Left
        for d_row, d_col in ((0, 1), (-1, 0), (0, -1)):
            nbr_row, nbr_col = drop_row + d_row, drop_col + d_col
            if 0 <= nbr_row < self.rows and 0 <= nbr_col < self.cols:
                nbr_colour = self.grid[nbr_row][nbr_col]
                if nbr_colour in PRIMARY and nbr_colour != centre_colour:
                    secondary = PAIR_TO_SECONDARY[(centre_colour, nbr_colour)]
                    self.grid[drop_row][drop_col] = secondary
                    self.grid[nbr_row][nbr_col]   = secondary
                    self._sec1, self._sec2 = (drop_row, drop_col), (nbr_row, nbr_col)
                    return                               # one mix max
        self._sec1 = self._sec2 = None                   # no mix

    # ---------- PASS 2 : secondary lock ----------
    def secondary_lock(self, drop_row, drop_col):
        """
        For each secondary created in pair_mix (there are 0, 1, or 2),
        scan neighbours clockwise.  The first complementary secondary
        encountered forms a lock: both secondaries **and** the original
        dropped square turn into the resulting primary.
        """
        for sec_pos in (self._sec1, self._sec2):
            if not sec_pos:
                continue

            sec_row, sec_col = sec_pos
            sec_colour = self.grid[sec_row][sec_col]      # Y / M / C

            for d_row, d_col in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                nbr_row, nbr_col = sec_row + d_row, sec_col + d_col
                if 0 <= nbr_row < self.rows and 0 <= nbr_col < self.cols:
                    nbr_colour = self.grid[nbr_row][nbr_col]
                    primary = LOCK.get((sec_colour, nbr_colour))
                    if primary:
                        # Lock the trio
                        self.grid[sec_row][sec_col] = primary
                        self.grid[nbr_row][nbr_col] = primary
                        self.grid[drop_row][drop_col] = primary
                        return       # one lock max per move
        # No lock this turn
        
@dataclass(frozen=True, eq=True)
class Action:
    col: int
    colour: int  

class GameState:
    """
    A snapshot of the full game:
        board       – immutable copy of the grid
        player      – 1 (P1, wants G) or 2 (P2, wants R)
        last_action – Action that led here (None for root)
    """
    def __init__(self, board=None, player=1, last_action=None):
        self.board        = board or Board()
        self.player       = player
        self.last_action  = last_action

    # ----- helpers the AI / CLI will use -----
    def copy(self):
        return GameState(
            board       = deepcopy(self.board),
            player      = self.player,
            last_action = self.last_action
        )

    def get_legal_actions(self):
        """Return a list, not a generator."""
        actions = []
        top_row = self.board.rows - 1
        for col in range(self.board.cols):
            if self.board.grid[top_row][col] == 0:          # column not full
                for colour in (R, G, B):
                    actions.append(Action(col, colour))
        return actions

    def perform_action(self, action: Action):
        """Return a NEW GameState after applying `action`."""
        new = self.copy()
        new.board.drop(action.col, action.colour)
        # when you implement reactions, call them here:
        # new.board.pair_mix(); new.board.trio_revert()
        new.player = 3 - self.player                      # switch sides
        new.last_action = action
        return new

    # ----- end‑conditions & scoring -----
    def is_terminal(self):
        return all(cell for row in self.board.grid for cell in row)

    def get_result(self):
        greens = sum(cell == G for row in self.board.grid for cell in row)
        reds   = sum(cell == R for row in self.board.grid for cell in row)

        if greens == reds:
            return 0                # draw

        winner = 1 if greens > reds else 2  # 1=P1/Green, 2=P2/Red
        leaf_player = 3 - self.player       # the player who just made the last move

        return 1 if winner == leaf_player else -1


