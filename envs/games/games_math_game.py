from rich import print as rprint
import rerun as rr
import numpy as np
from games_math import Vector2
import math
rr.init("games_math_game", spawn=True)


# left arrow on keyboard to rotate to the left
# right arrow on keyboard to go right
# top arrow to go forward (not yet needed)
# bottom arrow to go backwards (not yet needed)
# we need an update function that changes the pos when we hold one of they keys..
# or we don't want to update via keys, and instead just have some values adjust inputs via random input or time input or something

# Let's start with one vector

v1 = Vector2(1, 5) # This goes 1 in x and 5 in y
# we want a v2 which will be our kinda target point/vector
v2 = Vector2(2, 1)

normalized_v1 = v1.normalize()
normalized_v2 = v2.normalize()








## -- RERUN --


# Let's visualize this in rerun, since we have __array__ we can do

# Let's create the grid behind stuff

rr.log(
    "map/vectors",
    rr.Arrows2D(
        vectors=[v1.to_rr2d(),v2.to_rr2d()],
        colors=[[200,20,20],[100,20,20]],
        # labels=[["our vector"],["target vector"]],
        radii=0.05,
        draw_order=100,
    )
)

# you could in place normalize instead of creating the two unit vectors too, and maybe instead of normalized to just unit_v1? 

rr.log(
    "map/normalized_vectors",
    rr.Arrows2D(
        vectors=[normalized_v1.to_rr2d(),normalized_v2.to_rr2d()],
        colors=[[0,0,200],[0,0,200]],
        # labels=[["our vector"],["target vector"]],
        radii=0.05,
        draw_order=150,
    )
)

# Our unit circle

R = 1.0
N = 256                     # learn 
angles = np.linspace(0.0, 2.0 * math.pi, N, endpoint=False) # learn

# learn some math to understand
circle_pts = [Vector2(math.cos(a) * R, math.sin(a) * R).to_rr2d() for a in angles]
circle_pts.append(circle_pts[0])   

rr.log(
    "map/unit_circle",
    rr.LineStrips2D(
        [circle_pts],
        colors=[240, 240, 245, 140],          
        radii=0.025,  
        draw_order=50,              
    ),
)

PAD = 0.25
axes = [
    [Vector2(-R-PAD, 0).to_rr2d(), Vector2(R+PAD, 0).to_rr2d()],  # X
    [Vector2(0, -R-PAD).to_rr2d(), Vector2(0, R+PAD).to_rr2d()],  # Y
]
rr.log(
    "map/axes",
    rr.LineStrips2D(
        axes,
        colors=[210, 210, 220, 180],
        radii=0.02,       
        draw_order=25,      
    ),
)


STEP = 0.25
EXT  = R + PAD
grid = []

xs = np.arange(-EXT, EXT + 1e-9, STEP)
for x in xs:
    grid.append([Vector2(x, -EXT).to_rr2d(), Vector2(x, EXT).to_rr2d()])

ys = np.arange(-EXT, EXT + 1e-9, STEP)
for y in ys:
    grid.append([Vector2(-EXT, y).to_rr2d(), Vector2(EXT, y).to_rr2d()])

rr.log(
    "map/grid",
    rr.LineStrips2D(
        grid,
        colors=[225, 228, 233, 100],
        radii=0.01,      # world units
        draw_order=0,   # behind circle(50), axes(60), arrows(100)
    ),
)

# --- Angle arc & label using your Vector2 methods (no extra helpers) ---
# maybe we add a visual that say, go to right, go to left, in addition with the degree label?

# Signed shortest angle (radians) from normalized_v1 -> normalized_v2 in [-pi, pi]
delta = normalized_v1.angle_with_direction(normalized_v2)
theta_deg = abs(normalized_v1.angle_with_direction(normalized_v2, degrees=True))


ARC_R = 0.8
M = 96  # arc resolution

# Arc points: rotate normalized_v1 toward normalized_v2, then scale by ARC_R
arc_dirs = [normalized_v1.rotate(t) for t in np.linspace(0.0, delta, M, endpoint=True)]
arc_pts  = [Vector2(p.x * ARC_R, p.y * ARC_R).to_rr2d() for p in arc_dirs]

rr.log(
    "map/angle_arc",
    rr.LineStrips2D(
        [arc_pts],
        colors=[120, 120, 220, 220],
        radii=0.02,
        draw_order=90,
    ),
)

# Label at mid-arc
half = delta * 0.5
mid_dir   = normalized_v1.rotate(half)
label_pos = Vector2(mid_dir.x * (ARC_R + 0.08), mid_dir.y * (ARC_R + 0.08)).to_rr2d()

rr.log(
    "map/angle_label",
    rr.Points2D(
        positions=[label_pos],
        labels=[[f"θ = {theta_deg:.1f}°"]],
        radii=0.0,          # hide dot; show just text
        draw_order=95,
    ),
)



