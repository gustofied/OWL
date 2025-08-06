from color_game import GameState, LETTER, Color
from mcts        import mcts
import visual


def print_board(gs: GameState) -> None:
    print(f"\nPlayer {gs.player} to move   (G wins if score>0, R wins if <0)")
    print(gs.board)
    print()

def main() -> None:
    gs = GameState()                   
    visual.init_view(gs.board)
    visual.log_board(gs.board)
    print_board(gs)

    while True:
        best = mcts(gs, iterations=100)
        print(f"MCTS chose column {best.col}  color {LETTER[best.piece.color]}")

        print("=== Executing move ===")
        gs, reward, done, _ = gs.step(best, show_steps=True)

        visual.log_board(gs.board)
        
        print_board(gs)

        if done:
            print("episode reward:", reward)
            break

    red_count = green_count = blue_count = 0
    for row in gs.board.grid:
        for cell in row:
            if cell.color == Color.R:
                red_count += 1
            elif cell.color == Color.G:
                green_count += 1
            elif cell.color == Color.B:
                blue_count += 1

    print(f"\nFinal counts →  R:{red_count}  G:{green_count}  B:{blue_count}")
    highest = max(red_count, green_count, blue_count)
    leaders = [c for c, n in (("Green", green_count),
                              ("Red", red_count),
                              ("Blue", blue_count)) if n == highest]
    if len(leaders) == 1 and leaders[0] != "Blue":
        print(f"Game over – {leaders[0]} wins ✔")
    else:
        print("Game over – Draw ✔")


if __name__ == "__main__":
    main()
