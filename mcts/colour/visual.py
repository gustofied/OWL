# visual.py  (new file, keeps main.py tidy)
import rerun as rr
import rerun.blueprint as rrb
from colour_game import HEX          # reuse your colour map

def init_view(board, app_id="colour_game_mcts"):
    """Init Rerun and draw the static grid for the given board."""
    rr.init(app_id, spawn=True)

    # Configure 2‑D view to fit board exactly
    blueprint = rrb.Blueprint(
        rrb.Spatial2DView(
            origin="/",
            name="Colour Game",
            background=[20, 20, 30],
            visual_bounds=rrb.VisualBounds2D(
                x_range=[0, board.cols],
                y_range=[board.rows, 0]
            ),
        )
    )
    rr.send_blueprint(blueprint)

    # Static grid lines
    horizontal = [[(0, y), (board.cols, y)] for y in range(board.rows + 1)]
    vertical   = [[(x, 0), (x, board.rows)] for x in range(board.cols + 1)]
    rr.log("board/grid", rr.LineStrips2D(horizontal + vertical))


def log_board(board):
    """Log coloured discs for the current board state."""
    positions, colors, radii = [], [], []
    for y in range(board.rows):
        for x in range(board.cols):
            colour = board.grid[y][x]
            if colour != 0:
                positions.append((x + 0.5, y + 0.5))
                # Convert #RRGGBB → [R,G,B]
                rgb = [int(HEX[colour][i:i+2], 16) for i in (1, 3, 5)]
                colors.append(rgb)
                radii.append(0.45)
    rr.log("board/tokens", rr.Points2D(positions, colors=colors, radii=radii))
