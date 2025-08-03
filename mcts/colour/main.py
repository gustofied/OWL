"""
main.py – Colour‑Game with MCTS + Rerun visualisation
-----------------------------------------------------

Run this file to play a full game between two MCTS agents while
streaming the board state live to the Rerun viewer.

Prerequisites
-------------
pip install rerun-sdk           # visualisation
pip install colour‑game‑package # whatever name you used
"""
from colour_game import GameState, LETTER, Color
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
        
        # Show the three-phase debug output for the actual game move
        print("=== Executing move ===")
        gs = gs.perform_action(best, show_steps=True)

        visual.log_board(gs.board)         # live update in the Rerun viewer
        print_board(gs)

    # ─── Final result ────────────────────────────────────────────────
    # Count all green and red pieces (both locked and unlocked)
    green_count = 0
    red_count = 0
    
    for row in gs.board.grid:
        for cell in row:
            if cell.color == Color.G:
                green_count += 1
            elif cell.color == Color.R:
                red_count += 1
    
    if green_count > red_count:
        print(f"Game over – Green wins ✔ (Green: {green_count}, Red: {red_count})")
    elif red_count > green_count:
        print(f"Game over – Red wins ✔ (Red: {red_count}, Green: {green_count})")
    else:
        print(f"Game over – Draw ✔ (Green: {green_count}, Red: {red_count})")
    # ─────────────────────────────────────────────────────────────────


if __name__ == "__main__":
    main()