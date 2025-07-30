"""
main.py – Colour‑Game with MCTS + Rerun visualisation
-----------------------------------------------------

Run this file to play a full game between two MCTS agents while
streaming the board state live to the Rerun viewer.

Prerequisites
-------------
pip install rerun-sdk           # visualisation
pip install colour‑game‑package # whatever name you used
"""
from colour_game import GameState, LETTER
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
        print(f"MCTS chose column {best.col}  colour {LETTER[best.colour]}")
        gs = gs.perform_action(best)

        visual.log_board(gs.board)         # live update in the Rerun viewer
        print_board(gs)

    # ─── Final result ────────────────────────────────────────────────
    final = gs.get_result()
    if final > 0:
        print("Game over – Player 1 (Green) wins  ✔")
    elif final < 0:
        print("Game over – Player 2 (Red) wins  ✔")
    else:
        print("Game over – Draw.")
    # ─────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    main()
