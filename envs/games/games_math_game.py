from dataclasses import dataclass
import time, numpy as np, rerun as rr
from games_math import Vector2, EPSILON
import math

rr.init("games_math_game", spawn=True)

description = """

Game mechanics, a user can move the "main arrow"
left arrow on keyboard to rotate to the left
right arrow on keyboard to go right
So we need an update function that changes the pos when we hold one of they keys..
This game is heavy into visuals, setting up nicley for future games.

We also introduce our LLM agent, what can he do here in this game, env?
We make a simple driver, loop,

All is logged first as setup run to wandb ofc to capture it all if we want
Then for live we have rerun visuals and log.
After run we could use rerun or wandb, we are expiremnting here getting to know the two as well as the logging module of python.
As a result we have a simple mvp with the three

So, games math game, shows us
games math and mechanics, we use it to have an arrow and make a small steering game
We make the tranlsation into llm ddigebstale so it can interact here
and we play around with logging and visuals both for game wise , but also llm agent and learning wise
next up is more steering behaviours.

                    """

# Make the description visible in the viewer
rr.log(
    "docs",
    rr.TextDocument(description, media_type=rr.MediaType.MARKDOWN),
    static=True,
)

# -------------------------
# STATIC BACKGROUND (log once)
# -------------------------
CIRCLE_RADIUS = 1.0
VIEW_PADDING  = 0.25
GRID_SPACING  = 0.25

def make_background():
    # Unit circle (closed strip)
    angles = np.linspace(0.0, 2.0 * math.pi, 256, endpoint=False)
    circle_pts = [Vector2(math.cos(a) * CIRCLE_RADIUS, math.sin(a) * CIRCLE_RADIUS).to_rr2d() for a in angles]
    circle_pts.append(circle_pts[0])

    rr.log(
        "map/unit_circle",
        rr.LineStrips2D([circle_pts], colors=[240, 240, 245, 140], radii=0.025, draw_order=50),
        static=True,
    )

    # Axes
    lim = CIRCLE_RADIUS + VIEW_PADDING
    axes = [
        [Vector2(-lim, 0.0).to_rr2d(), Vector2(lim, 0.0).to_rr2d()],
        [Vector2(0.0, -lim).to_rr2d(), Vector2(0.0, lim).to_rr2d()],
    ]
    rr.log(
        "map/axes",
        rr.LineStrips2D(axes, colors=[210, 210, 220, 180], radii=0.02, draw_order=60),
        static=True,
    )

    # Grid
    ticks = np.arange(-lim, lim + GRID_SPACING / 2, GRID_SPACING)
    grid = (
        [[Vector2(x, -lim).to_rr2d(), Vector2(x,  lim).to_rr2d()] for x in ticks] +
        [[Vector2(-lim, y).to_rr2d(), Vector2(lim, y).to_rr2d()] for y in ticks]
    )
    rr.log(
        "map/grid",
        rr.LineStrips2D(
            grid,
            colors=[225, 228, 233, 100],
            radii=0.01,   # use rr.Radius.ui_points(1.0) if you want zoom-independent width
            draw_order=0
        ),
        static=True,
    )

make_background()

# --- state -------------------------------------------------
@dataclass
class GameState:
    v1: Vector2
    v2: Vector2

def step(state: GameState, dt: float) -> GameState:
    ANGULAR_SPEED_V1 = +0.8
    ANGULAR_SPEED_V2 = -1.2
    return GameState(
        v1=state.v1.rotate(ANGULAR_SPEED_V1 * dt),
        v2=state.v2.rotate(ANGULAR_SPEED_V2 * dt),
    )

# --- rendering (all logging lives here) --------------------
def render(state: GameState, t: float):
    rr.set_time_seconds("sim_time", t)  # stamp time here (render step)

    n1, n2 = state.v1.normalize(), state.v2.normalize()

    rr.log("map/vectors", rr.Arrows2D(
        vectors=[state.v1.to_rr2d(), state.v2.to_rr2d()],
        colors=[[200,20,20],[100,20,20]], radii=0.05, draw_order=100
    ))
    rr.log("map/normalized_vectors", rr.Arrows2D(
        vectors=[n1.to_rr2d(), n2.to_rr2d()],
        colors=[[0,0,200],[0,0,200]], radii=0.05, draw_order=150
    ))

    # --- Angle value in math space (for label text) ---
    theta_deg = abs(n1.angle_with_direction(n2, degrees=True))

    # --- Arc computed in SCREEN SPACE to match the flipped view ---
    n1_s = n1.to_rr2d()
    n2_s = n2.to_rr2d()

    a = math.atan2(n1_s.y, n1_s.x)
    b = math.atan2(n2_s.y, n2_s.x)

    def shortest_delta(a0, a1):
        d = (a1 - a0 + math.pi) % (2.0 * math.pi) - math.pi
        return d

    d_screen = shortest_delta(a, b)

    ARC_RADIUS = 0.8
    SAMPLES_PER_RAD = 48
    samples = max(8, int(abs(d_screen) * SAMPLES_PER_RAD))
    thetas = np.linspace(a, a + d_screen, samples, endpoint=True)

    # Points already in screen coords (do NOT .to_rr2d() again)
    arc_pts = [[math.cos(th) * ARC_RADIUS, math.sin(th) * ARC_RADIUS] for th in thetas]

    rr.log("map/angle_arc",
           rr.LineStrips2D([arc_pts], colors=[120,120,220,220], radii=0.02, draw_order=90))

    mid = a + 0.5 * d_screen
    label_pos = [math.cos(mid) * (ARC_RADIUS + 0.08), math.sin(mid) * (ARC_RADIUS + 0.08)]
    rr.log("map/angle_label", rr.Points2D(
        positions=[label_pos], labels=[[f"θ = {theta_deg:.1f}°"]],
        radii=0.0, draw_order=95
    ))

# --- program ------------------------------------------------

# initial state
state = GameState(v1=Vector2(1, 5), v2=Vector2(2, 1))

# render initial frame at t=0 (logic already initialized)
t = 0.0
render(state, t)

# main loop: input -> update -> render
target_fps = 60.0
t0 = time.perf_counter()
prev = t0
while True:
    now = time.perf_counter()
    dt = now - prev
    prev = now

    # (logic)
    state = step(state, dt)
    t = now - t0

    # (render/log)
    render(state, t)

    # simple pacing
    time.sleep(max(0.0, (1/target_fps) - (time.perf_counter() - now)))
