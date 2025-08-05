from dataclasses import dataclass
from copy import deepcopy
from enum import IntEnum
from typing import TypeAlias, List, Tuple


class Color(IntEnum):
    EMPTY = 0
    R = 1; G = 2; B = 3
    Y = 4; M = 5; C = 6


@dataclass
class Cell:
    """A single grid/board square."""
    color: Color = Color.EMPTY
    locked: bool = False      # becomes True after a triomix


@dataclass(frozen=True)
class Piece:
    """Just a colour of the piece choses by the player that is going to be dropped."""
    color: Color



R, G, B, Y, M, C = Color.R, Color.G, Color.B, Color.Y, Color.M, Color.C
PRIMARY = {R, G, B}

LETTER = {
    Color.EMPTY: ".",
    R: "R", G: "G", B: "B",
    Y: "Y", M: "M", C: "C",
}

HEX = {
    R: "#FF0000", G: "#00FF00", B: "#0000FF",
    Y: "#FFFF00", M: "#FF00FF", C: "#00FFFF",
}

# Chemistry, true mixing of primaries into secondaries, RGB

PAIR_TO_SECONDARY = {
    (R, G): Y, (G, R): Y,
    (R, B): M, (B, R): M,
    (G, B): C, (B, G): C,
}

# Chemistry Substractive
LOCK = {
    (Y, M): R, (M, Y): R,
    (C, Y): G, (Y, C): G,
    (M, C): B, (C, M): B,
}


CellPos: TypeAlias = Tuple[int, int]

class Board:
    def __init__(self, rows: int = 6, cols: int = 5):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[Cell]] = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self.events: List[dict] = []  

    # ── helpers ──
    def _in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def _log(self, event_type: str, *positions: CellPos) -> None:
        self.events.append({"event_type": event_type, "positions": positions})

    def __str__(self) -> str:
        lines = [
            " ".join(
                (LETTER[cell.color].lower() if cell.locked else LETTER[cell.color])
                for cell in row
            )
            for row in reversed(self.grid)
        ]
        return "\n".join(lines)


    def drop(self, col: int, piece: Piece) -> None:
        """
        Drop *piece* into column *col*, then run we a pairmix and triomix.
        """
        if piece.color not in PRIMARY:
            raise ValueError("Only R, G or B can be dropped")
        if not (0 <= col < self.cols):
            raise IndexError("Column out of range")

        self.events.clear()

        for row in range(self.rows):
            if self.grid[row][col].color == Color.EMPTY:
                self.grid[row][col].color = piece.color
                drop_pos: CellPos = (row, col)
                self._log("drop", drop_pos)

                pair_positions = self._pair_mix(drop_pos)
                self._trio_mix(pair_positions)
                return
        raise ValueError("Column is full")

    def drop_with_trace(self, col: int, piece: Piece) -> None:
        """Same as :py:meth:`drop` but prints the board after each phase."""
        if piece.color not in PRIMARY:
            raise ValueError("Only R, G or B can be dropped")
        if not (0 <= col < self.cols):
            raise IndexError("Column out of range")

        self.events.clear()

        for row in range(self.rows):
            if self.grid[row][col].color == Color.EMPTY:
                self.grid[row][col].color = piece.color
                drop_pos: CellPos = (row, col)
                self._log("drop", drop_pos)
                print("\n— after drop —\n" + str(self))

                pair_positions = self._pair_mix(drop_pos)
                print("\n— after pair —\n" + str(self))

                self._trio_mix(pair_positions)
                print("\n— after trio —\n" + str(self))
                return
        raise ValueError("Column is full")

    # Chemistry
    # PASS 1 : le mixing of pairs
    def _pair_mix(self, drop_pos: CellPos) -> List[CellPos]:
        """
         Look at the cell of the peice we just dropped. If one of its orthogonal
        neighbours is a *different* primary, convert that pair to the
        appropriate secondary.  Only ONE mix can happen per move. Retrun the list 
        of the pair mixing with their positions
        """
        row, col = drop_pos
        drop_colour = self.grid[row][col].color

        for d_row, d_col in ((0, 1), (-1, 0), (0, -1)):   # right, below, left , Scan neighbours clockwise (270): Right, Down, Left (no Up - just dropped!)
            nbr_row, nbr_col = row + d_row, col + d_col
            if not self._in_bounds(nbr_row, nbr_col):
                continue

            neighbour = self.grid[nbr_row][nbr_col]
            if neighbour.locked:
                continue

            neighbour_colour = neighbour.color
            if neighbour_colour in PRIMARY and neighbour_colour != drop_colour:
                pair_colour = PAIR_TO_SECONDARY[(drop_colour, neighbour_colour)]
                self.grid[row][col].color        = pair_colour
                self.grid[nbr_row][nbr_col].color = pair_colour

                pair_positions = [drop_pos, (nbr_row, nbr_col)]
                self._log("pair", *pair_positions)
                return pair_positions

        return []

    # Pass 2, le mixing of triples/trios
    def _trio_mix(self, pair_positions: List[CellPos]) -> None:
        """Attempt the trio-mix around the two *pair* squares produced this turn."""
        for pair_row, pair_col in pair_positions:
            pair_colour = self.grid[pair_row][pair_col].color

            for d_row, d_col in ((0, 1), (-1, 0), (0, -1), (1, 0)):
                nbr_row, nbr_col = pair_row + d_row, pair_col + d_col
                if not self._in_bounds(nbr_row, nbr_col):
                    continue

                neighbour = self.grid[nbr_row][nbr_col]
                if neighbour.locked:
                    continue

                complement_colour = neighbour.color
                result_colour = LOCK.get((pair_colour, complement_colour))
                if result_colour:
                    trio_positions = set(pair_positions + [(nbr_row, nbr_col)])
                    for row_idx, col_idx in trio_positions:
                        cell = self.grid[row_idx][col_idx]
                        cell.color  = result_colour
                        cell.locked = True

                    self._log("trio", *trio_positions)
                    return



@dataclass(frozen=True, eq=True)
class Action:
    col: int
    piece: Piece


class GameState:
    def __init__(self, board=None, player=1, last_action=None):
        self.board = board or Board()
        self.player = player
        self.last_action = last_action

    # basic utilities --------------------------------------------------
    def copy(self):
        return GameState(
            board=deepcopy(self.board),
            player=self.player,
            last_action=self.last_action,
        )

    def get_legal_actions(self):
        """All (column, primary colour) pairs that can currently be dropped."""
        actions: List[Action] = []
        top_row = self.board.rows - 1
        for col in range(self.board.cols):
            if self.board.grid[top_row][col].color == Color.EMPTY:
                for color in (R, G, B):
                    actions.append(Action(col, Piece(color)))
        return actions

    # single-step transition ------------------------------------------
    def step(self, action: Action, show_steps: bool = False):
        next_state = self.copy()
        if show_steps:
            next_state.board.drop_with_trace(action.col, action.piece)
        else:
            next_state.board.drop(action.col, action.piece)

        next_state.player = 3 - self.player
        next_state.last_action = action

        done = next_state.is_terminal()
        reward = next_state.get_result() if done else 0.0
        info = {}
        return next_state, reward, done, info

    # game-over logic --------------------------------------------------
    def is_terminal(self) -> bool:
        """The game ends when there are no empty cells left on the board."""
        for row in self.board.grid:
            for cell in row:
                if cell.color == Color.EMPTY:
                    return False
        return True

    def get_result(self) -> int:
        """
        Score from the perspective of the player who JUST moved:

            +1 → last mover wins
            -1 → last mover loses
             0 → draw (tie or blue majority)

        Rule: whichever primary colour (R, G, B) occupies the most cells wins.
        """
        red_count   = 0
        green_count = 0
        blue_count  = 0
        for row in self.board.grid:
            for cell in row:
                if cell.color == Color.R:
                    red_count += 1
                elif cell.color == Color.G:
                    green_count += 1
                elif cell.color == Color.B:
                    blue_count += 1

        highest_count = max(red_count, green_count, blue_count)
        leading_colors = [
            color for color, count in (
                (Color.R, red_count),
                (Color.G, green_count),
                (Color.B, blue_count),
            )
            if count == highest_count
        ]

        # Draw if more than one colour ties for first OR blue leads on its own
        if len(leading_colors) > 1 or leading_colors[0] == Color.B:
            return 0

        winning_color = leading_colors[0]
        winning_player = 1 if winning_color == Color.G else 2     # G ↔ player 1, R ↔ player 2
        last_mover = 3 - self.player                               # invert 1↔2
        return 1 if winning_player == last_mover else -1
