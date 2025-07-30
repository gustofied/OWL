import rerun as rr
import rerun.blueprint as rrb
import random

# Initialize Rerun Viewer
rr.init("connect_four_play", spawn=True)

# Draw the static board frame and grid
rr.log("board/frame", rr.Boxes2D(mins=[0, 0], sizes=[7, 6]))
horizontal = [[(0, y), (7, y)] for y in range(7)]
vertical   = [[(x, 0), (x, 6)] for x in range(8)]
rr.log("board/grid", rr.LineStrips2D(horizontal + vertical))

# Configure the 2D camera once
blueprint = rrb.Blueprint(
    rrb.Spatial2DView(
        origin="/",
        name="Connect Four Play",
        background=[30, 30, 60],
        visual_bounds=rrb.VisualBounds2D(x_range=[0, 7], y_range=[0, 6]),
    )
)
rr.send_blueprint(blueprint)

# Game state: 6 rows x 7 columns, 0=empty, 1=red, 2=yellow
board = [[0 for _ in range(7)] for _ in range(6)]
turn = 1  # start with player 1 (red)

# Function to log tokens in the current board state
def log_tokens():
    positions, colors, radii = [], [], []
    for y in range(6):
        for x in range(7):
            if board[y][x] != 0:
                positions.append((x + 0.5, y + 0.5))
                # Red for player 1, Yellow for player 2
                colors.append([255, 0, 0] if board[y][x] == 1 else [255, 255, 0])
                radii.append(0.45)
    rr.log("board/tokens", rr.Points2D(positions, colors=colors, radii=radii))

# Function to make a random valid move

def play_random_move():
    global turn
    # Check for any non-full columns
    valid_cols = [c for c in range(7) if board[5][c] == 0]
    if not valid_cols:
        print("Board is full: no more moves possible.")
        return False
    col = random.choice(valid_cols)
    # Drop piece to lowest empty slot in that column
    for y in range(6):
        if board[y][col] == 0:
            board[y][col] = turn
            break
    trace_player = "Red" if turn == 1 else "Yellow"
    print(f"{trace_player} played in column {col}.")
    turn = 3 - turn  # alternate player
    # Log updated tokens
    log_tokens()
    return True

# Main loop: type 'play' to make a random move, 'q' to quit
print("Type 'play' to make a random move. Type 'q' to quit.")
while True:
    cmd = input(">>> ").strip().lower()
    if cmd == 'q':
        print("Exiting Connect Four.")
        break
    elif cmd == 'play':
        if not play_random_move():
            break
    else:
        print("Unrecognized command. Type 'play' or 'q'.")
