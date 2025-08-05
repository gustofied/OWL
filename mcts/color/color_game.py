from dataclasses import dataclass
from copy import deepcopy
from enum import IntEnum
from typing import TypeAlias, List, Tuple

class Color(IntEnum):
    EMPTY = 0
    R = 1; G = 2; B = 3
    Y = 4; M = 5; C = 6


@dataclass()
class Cell:
    color: Color = Color.EMPTY
    locked: bool = False  # becomes True after a trio‑mix


@dataclass(frozen=True)
class Piece:

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

CellPos = Tuple[int, int]

# The board, we do 6x5 in this example to keep it simple ;), and you play the board like from the top, and the piece drops, just as connect four. Same game "map"

class Board:
    def __init__(self, rows: int = 6, cols: int = 5):
        self.rows = rows
        self.cols = cols
        self.grid: List[List[Cell]] = [[Cell() for _ in range(cols)] for _ in range(rows)]
        self.events: List[dict] = []  # cleared each move

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
        if piece.color not in PRIMARY:
            raise ValueError("Only R, G or B can be dropped")
        if not (0 <= col < self.cols):
            raise IndexError("Column out of range")

        self.events.clear()

        for row in range(self.rows):
            if self.grid[row][col].color == Color.EMPTY:
                self.grid[row][col].color = piece.color
                self._log("drop", (row, col))
                secondary_cells = self._pair_mix(row, col)  # pass 1
                self._trio_mix(secondary_cells)             # pass 2
                return
        raise ValueError("Column is full")

    def drop_with_trace(self, col: int, piece: Piece) -> None:        
        if piece.color not in PRIMARY:
            raise ValueError("Only R, G or B can be dropped")
        if not (0 <= col < self.cols):
            raise IndexError("Column out of range")

        self.events.clear()

        for row in range(self.rows):
            if self.grid[row][col].color == Color.EMPTY:
                self.grid[row][col].color = piece.color
                self._log("drop", (row, col))
                print("\n— after drop —\n" + str(self))

                secondary_cells = self._pair_mix(row, col)
                print("\n— after pair —\n" + str(self))

                self._trio_mix(secondary_cells)
                print("\n— after trio —\n" + str(self))
                return
        raise ValueError("Column is full")

    # ── internal mixing phases ──
    def _pair_mix(self, row: int, col: int) -> List[CellPos]:
        """If a neighbouring primary can mix, turn the pair into a secondary.
        Returns the coordinates of the (0–2) secondary cells produced."""
        base_color = self.grid[row][col].color
        for d_row, d_col in ((0, 1), (-1, 0), (0, -1)):
            nbr_row, nbr_col = row + d_row, col + d_col
            if self._in_bounds(nbr_row, nbr_col):
                neighbour = self.grid[nbr_row][nbr_col]
                if neighbour.locked:
                    continue
                neighbour_color = neighbour.color
                if neighbour_color in PRIMARY and neighbour_color != base_color:
                    secondary = PAIR_TO_SECONDARY[(base_color, neighbour_color)]
                    self.grid[row][col].color = secondary
                    self.grid[nbr_row][nbr_col].color = secondary
                    secondary_cells = [(row, col), (nbr_row, nbr_col)]
                    self._log("pair", *secondary_cells)
                    return secondary_cells
        return []

    def _trio_mix(self, secondary_cells: List[CellPos]) -> None:
        """Attempt the trio‑mix around any secondary cells created this move."""
        for sec_row, sec_col in secondary_cells:
            secondary_color = self.grid[sec_row][sec_col].color
            for d_row, d_col in ((0, 1), (-1, 0), (0, -1), (1, 0)):
                nbr_row, nbr_col = sec_row + d_row, sec_col + d_col
                if not self._in_bounds(nbr_row, nbr_col):
                    continue
                neighbour = self.grid[nbr_row][nbr_col]
                if neighbour.locked:
                    continue
                complement_color = neighbour.color
                primary_color = LOCK.get((secondary_color, complement_color))
                if primary_color:
                    trio_positions = set(secondary_cells + [(nbr_row, nbr_col)])
                    for r, c in trio_positions:
                        cell = self.grid[r][c]
                        cell.color = primary_color
                        cell.locked = True
                    self._log("trio", *trio_positions)
                    return

# ──────────────────────────────────────────────────────────────────────────────
#  Turn / game‑state logic
# ──────────────────────────────────────────────────────────────────────────────

@dataclass(frozen=True, eq=True)
class Action:
    col: int
    piece: Piece


class GameState:
    def __init__(self, board=None, player=1, last_action=None):
        self.board = board or Board()
        self.player = player
        self.last_action = last_action

    def copy(self):
        return GameState(
            board=deepcopy(self.board),
            player=self.player,
            last_action=self.last_action,
        )

    def get_legal_actions(self):
        actions: List[Action] = []
        top_row = self.board.rows - 1
        for col in range(self.board.cols):
            if self.board.grid[top_row][col].color == Color.EMPTY:
                for color in (R, G, B):
                    actions.append(Action(col, Piece(color)))
        return actions

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
    def is_terminal(self):
        """
        The game ends when there are no empty cells (0) left on the board.
        Returns True if the board is full, otherwise False.
        """
        for row in self.board.grid:
            for cell in row:
                if cell.color == Color.EMPTY:           
                    return False
        return True                 


    def get_result(self) -> int:
        """
        Score from the perspective of the player who JUST moved.

            +1  → last mover wins
            -1  → last mover loses
            0  → draw (tie or blue majority)

        Rule: whichever primary colour (R, G, B) occupies the most cells wins.
        """
        red_count   = 0
        green_count = 0
        blue_count  = 0

        for row in self.board.grid:
            for cell in row:
                if cell.color == Color.R:
                    red_count   += 1
                elif cell.color == Color.G:
                    green_count += 1
                elif cell.color == Color.B:
                    blue_count  += 1

        highest_count = max(red_count, green_count, blue_count)
        leading_colours = [
            colour for colour, count in (
                (Color.R, red_count),
                (Color.G, green_count),
                (Color.B, blue_count),
            )
            if count == highest_count
        ]

        # Draw if more than one colour ties for first OR blue leads on its own
        if len(leading_colours) > 1 or leading_colours[0] == Color.B:
            return 0

        winning_colour = leading_colours[0]
        winning_player = 1 if winning_colour == Color.G else 2     # G ↔ player 1, R ↔ player 2
        last_mover     = 3 - self.player                           # invert 1↔2

        return 1 if winning_player == last_mover else -1