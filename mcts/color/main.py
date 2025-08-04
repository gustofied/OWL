"""
main.py – Color‑Game with MCTS + Rerun visualisation
-----------------------------------------------------

Run this file to play a full game between two MCTS agents while
streaming the board state live to the Rerun viewer.

Prerequisites
-------------
pip install rerun-sdk           # visualisation
pip install color‑game‑package # whatever name you used
"""
from color_game import GameState, LETTER, Color
from mcts         import mcts
import visual                          # <‑‑ our helper module (visual.py)


# ---------------------------------------------------------------------
# Console helpers
# ---------------------------------------------------------------------
def print_board(gs: GameState) -> None:
    """Pretty‑print the current position with player info."""
    print(f"\nPlayer {gs.player} to move   (G wins if score>0, R wins if <0)")
    print(gs.board)
    print()


# ---------------------------------------------------------------------
# Main program
# ---------------------------------------------------------------------
def main() -> None:
    """Play until the board is full, logging every step to Rerun."""
    gs = GameState()               # fresh empty position

    # ─── Visual initialisation ───────────────────────────────────────
    visual.init_view(gs.board)     # draw static grid sized to Board(cols, rows)
    visual.log_board(gs.board)     # log the empty board once
    # ─────────────────────────────────────────────────────────────────

    print_board(gs)

    while not gs.is_terminal():
        # Let MCTS choose a move for the current player
        best = mcts(gs, iterations=100)    # tweak iterations for speed/strength
        print(f"MCTS chose column {best.col}  color {LETTER[best.piece.color]}")
        
        # Show the three-phase debug output for the actual game move
        print("=== Executing move ===")
        gs, _, _, _ = gs.step(best, show_steps=True)

        visual.log_board(gs.board)         # live update in the Rerun viewer
        print_board(gs)

    # ─── Final result ────────────────────────────────────────────────
    red_count   = 0
    green_count = 0
    blue_count  = 0

    for row in gs.board.grid:
        for cell in row:
            if cell.color == Color.R:
                red_count   += 1
            elif cell.color == Color.G:
                green_count += 1
            elif cell.color == Color.B:
                blue_count  += 1

    print(f"\nFinal counts →  R:{red_count}  G:{green_count}  B:{blue_count}")

    highest = max(red_count, green_count, blue_count)
    leaders = [c for c, n in
            (("Green", green_count),
                ("Red",   red_count),
                ("Blue",  blue_count))
            if n == highest]

    if len(leaders) == 1 and leaders[0] != "Blue":
        print(f"Game over – {leaders[0]} wins ✔")
    else:
        print("Game over – Draw ✔")


if __name__ == "__main__":
    main()