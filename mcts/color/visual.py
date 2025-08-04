# visual.py  (updated with event log support)
import rerun as rr
import rerun.blueprint as rrb
from color_game import HEX          # reuse your color map

def init_view(board, app_id="color_game_mcts"):
    """Init Rerun and draw the static grid for the given board."""
    rr.init(app_id, spawn=True)

    # Configure 2‑D view to fit board exactly
    blueprint = rrb.Blueprint(
        rrb.Spatial2DView(
            origin="/",
            name="Color Game",
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


def translate(coords_list):
    """Convert board coordinates (row,col) → visual coordinates (x,y)."""
    return [(x + 0.5, y + 0.5) for y, x in coords_list]


# Event overlay colors for better visual distinction
KIND_COLOR = {
    "drop": [255, 255, 255],  # White arrows for drops
    "pair": [255, 50, 50],    # Red boxes for pair mixes
    "trio": [50, 255, 50]     # Green boxes for trio mixes (locks)
}


def log_board(board):
    """Log colored discs for the current board state."""
    positions, colors, radii = [], [], []
    for y in range(board.rows):
        for x in range(board.cols):
            cell = board.grid[y][x]
            color = cell.color
            if color != 0:
                positions.append((x + 0.5, y + 0.5))
                # Convert #RRGGBB → [R,G,B]
                rgb = [int(HEX[color][i:i+2], 16) for i in (1, 3, 5)]
                # Make locked pieces slightly transparent
                if cell.locked:
                    rgb.append(180)  # Add alpha channel for transparency
                colors.append(rgb)
                radii.append(0.45)
    rr.log("board/tokens", rr.Points2D(positions, colors=colors, radii=radii))
    
    # ── overlays ───────────────────────────────────
    for e in board.events:
        positions = translate(e["positions"])
        event_color = KIND_COLOR[e["event_type"]]
        
        if e["event_type"] == "drop":
            # Arrow pointing down at the dropped position
            rr.log("board/over/drop",
                   rr.Arrows2D(origins=positions, vectors=[[0, 0.3] for _ in positions], colors=[event_color]))
        elif e["event_type"] == "pair":
            # Red boxes around the pair-mixed cells
            rr.log("board/over/pair",
                   rr.Boxes2D(centers=positions, half_sizes=[[0.4, 0.4] for _ in positions], colors=[event_color for _ in positions]))
        elif e["event_type"] == "trio":
            # Green boxes around the trio-mixed (locked) cells
            rr.log("board/over/lock",
                   rr.Boxes2D(centers=positions, half_sizes=[[0.45, 0.45] for _ in positions], colors=[event_color for _ in positions]))
    
    # Permanent outline for all locked cells
    locked_positions = []
    for y in range(board.rows):
        for x in range(board.cols):
            cell = board.grid[y][x]
            if cell.locked and cell.color != 0:
                locked_positions.append((x + 0.5, y + 0.5))
    
    if locked_positions:
        rr.log("board/locked_outline",
               rr.Boxes2D(centers=locked_positions, 
                         half_sizes=[[0.47, 0.47] for _ in locked_positions], 
                         colors=[[100, 100, 100, 120] for _ in locked_positions]))  # Gray with transparency
    
    board.events.clear()