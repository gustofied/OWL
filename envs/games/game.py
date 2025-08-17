from __future__ import annotations

from observability import setup_logging, logger

from dataclasses import dataclass
import math
import time
from typing import Optional

import numpy as np
import rerun as rr
import rerun.blueprint as rrb

from math_utils import Vector2, EPSILON  

setup_logging(app_name="game")


description = """

Ramble: oki for game mechanics behaviours, a user can move the "main arrow"
left arrow on keyboard to rotate to the left and right arrow on keyboard to go right
This would be cool to introduce but this human input layer might be out of scope for now
We would want an agent to do this, no need for a human player right now.
So if we wanted to we would need an update function that changes the pos when we hold one of they keys..
It does some force?

well game_1 is a basic game but leads heavy into basics and visuals (observability), which sets up nicley for game 2 - 3 - 4 etc, those games
adds on firstly more you could call game mechanics/things but then more gameplay, Game AI etc

In addition to the simple game, we ofc here introduce some way of the game to be played and interacted by a LLM agent
What we have implemented to do this is simple driver/loop, and some translation of action space into the observatoin for agent

The observabillty consits of wandb, rerun, and logging module, we explore this combo, we want wandb to capture the runs and all.
rerun makes it easier to tap into what happens in real time, and gives nice visuals to build our intution and debugging live
log for log yeh, and can be saved in wandb, and showcased in rerun live too. We explore this setup, try to build on it, and think this
is the future of observabillity for owl

Oki so at last, this is game 1, game 1 is basic, we have a unit circle, two arrows, some calucations like dot, cross, angle, 
we try to have the llm steer one of the arrows, and the other arrows become the goal, it needs to learn have to steer it best.
Learn maybe wrong word here, we just want to tailor our translation from the actionm space to the best possible observation for the agent.
That's our hoaning in here, in future games, look into more rewards machines, FSM, interaction stack, memory tools, etc

"""


rr.log(
    "docs",
    rr.TextDocument(description, media_type=rr.MediaType.MARKDOWN),
    static=True,
)

# Let's begin with drawing the static elements kinda the map we could say

def make_background():
    circle_radius = 1.0     # unit circle..
    view_padding  = 0.25    # extend axes/grid slightly beyond the circle
    grid_spacing  = 0.25    # distance between neighboring grid lines

    # a bit opaque what this is
    lim = circle_radius + view_padding

    # --- Circle ----------------------------------------------------------
    # Use N+1 samples with endpoint=True so we include both 0 and 2π,
    # which gives us a closed polyline directly.
    N = 256
    angles = np.linspace(0.0, 2.0 * math.pi, N + 1, endpoint=True)

    circle_pts = [
        Vector2(math.cos(a) * circle_radius, math.sin(a) * circle_radius).to_rr2d()
        for a in angles
    ]

    rr.log(
        "/map/unit_circle",
        rr.LineStrips2D([circle_pts], colors=[240, 240, 245, 140], radii=0.025, draw_order=50),
        static=True,
    )

    # --- Axes ------------------------------------------------------------
    axes = [
        [Vector2(-lim, 0.0).to_rr2d(), Vector2(lim, 0.0).to_rr2d()],   # X axis
        [Vector2(0.0, -lim).to_rr2d(), Vector2(0.0, lim).to_rr2d()],   # Y axis
    ]
    rr.log(
        "/map/axes",
        rr.LineStrips2D(axes, colors=[210, 210, 220, 180], radii=0.02, draw_order=60),
        static=True,
    )

    # --- Grid ------------------------------------------------------------
    # We want ticks at every multiple of grid_spacing from -lim to +lim, inclusive.
    ticks = np.arange(-lim, lim + grid_spacing / 2.0, grid_spacing)

    vertical_lines = [
        [Vector2(float(x), -lim).to_rr2d(), Vector2(float(x), lim).to_rr2d()]
        for x in ticks
    ]
    horizontal_lines = [
        [Vector2(-lim, float(y)).to_rr2d(), Vector2(lim, float(y)).to_rr2d()]
        for y in ticks
    ]
    grid = vertical_lines + horizontal_lines

    rr.log(
        "/map/grid",
        rr.LineStrips2D(grid, colors=[225, 228, 233, 100], radii=0.01, draw_order=0),
        static=True,
    )


# Need to learn more about blueprints :) 
# What we do here is make the the grid,axes and unit circle non interactive, so we cant interact with them in rerun, we disable
# nice becasue annoying when hovering in rerun when everything just pops of
# when we enable static=True is just that they are not part of the updating/time set time part of our code, its needed

rr.send_blueprint(
    rrb.Spatial2DView(
        name="map",
        origin="/", 
        overrides={
            "map/grid":        rrb.EntityBehavior(interactive=False),
            "map/axes":        rrb.EntityBehavior(interactive=False),
            "map/unit_circle": rrb.EntityBehavior(interactive=False),
        },
    )
)

make_background()



# -------------------------
# Simulation parameters
# -------------------------
ANGULAR_SPEED_V1 = +0.8   # radians/sec
ANGULAR_SPEED_V2 = -1.2   # radians/sec
TARGET_FPS = 60.0
RUN_DURATION_S = 20.0     # fixed run time since there are no inputs

# --- state -------------------------------------------------
@dataclass
class GameState:
    v1: Vector2
    v2: Vector2

def step(state: GameState, dt: float) -> GameState:
    """Auto-spin both vectors at fixed angular velocities."""
    return GameState(
        v1=state.v1.rotate(ANGULAR_SPEED_V1 * dt),
        v2=state.v2.rotate(ANGULAR_SPEED_V2 * dt),
    )

# --- rendering (all logging lives here) --------------------
def render(state: GameState, t: float, fps_ema: Optional[float]):
    # Rerun timeline
    rr.set_time("sim_time", duration=t)

    n1, n2 = state.v1.normalize(), state.v2.normalize()

    rr.log("map/vectors", rr.Arrows2D(
        vectors=[state.v1.to_rr2d(), state.v2.to_rr2d()],
        colors=[[200,20,20],[100,20,20]], radii=0.05, draw_order=100
    ))
    rr.log("map/normalized_vectors", rr.Arrows2D(
        vectors=[n1.to_rr2d(), n2.to_rr2d()],
        colors=[[0,0,200],[0,0,200]], radii=0.05, draw_order=150
    ))

    # Angle in math space (for label)
    theta_deg = abs(n1.angle_with_direction(n2, degrees=True))

    # Arc in screen space (flip-aware)
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

    # Points already in screen coords
    arc_pts = [[math.cos(th) * ARC_RADIUS, math.sin(th) * ARC_RADIUS] for th in thetas]

    rr.log("map/angle_arc",
           rr.LineStrips2D([arc_pts], colors=[120,120,220,220], radii=0.02, draw_order=90))

    mid = a + 0.5 * d_screen
    label_pos = [math.cos(mid) * (ARC_RADIUS + 0.08), math.sin(mid) * (ARC_RADIUS + 0.08)]
    rr.log("map/angle_label", rr.Points2D(
        positions=[label_pos], labels=[[f"θ = {theta_deg:.1f}°"]],
        radii=0.0, draw_order=95
    ))

    # ---- Metrics / HUD -------------------------------------------------
    try:
        rr.log("metrics/fps", rr.Scalar(float(fps_ema) if fps_ema is not None else float("nan")))
        rr.log("metrics/theta_deg", rr.Scalar(float(theta_deg)))
    except Exception:
        pass

    rr.log("hud", rr.TextLog(
        f"t={t:6.2f}s  fps~={fps_ema:5.1f}  θ={theta_deg:5.1f}°"
        if fps_ema is not None else
        f"t={t:6.2f}s  θ={theta_deg:5.1f}°"
    )) # I want logs to all fall under handler but name it observability but then we need to configure also the rerun I think so it's basic logs comes here?


# --- main loop ---
def main_loop():
    # initial state
    state = GameState(v1=Vector2(1, 5), v2=Vector2(2, 1))

    # startup message on sim_time = 0 for visibility
    rr.set_time("sim_time", duration=0.0)
    rr.log("hud", rr.TextLog("Started game."))
    logger.info("Started game.")

    t0 = time.perf_counter()
    prev = t0
    fps_ema: Optional[float] = None
    t = 0.0

    # initial frame
    render(state, t, fps_ema)

    # run for a fixed duration
    while t < RUN_DURATION_S:
        now = time.perf_counter()
        dt = now - prev
        prev = now

        state = step(state, dt)
        t = now - t0

        inst_fps = 1.0 / dt if dt > 1e-9 else float("inf")
        fps_ema = inst_fps if fps_ema is None else (0.9 * fps_ema + 0.1 * inst_fps)

        render(state, t, fps_ema)

        # simple frame pacing
        time.sleep(max(0.0, (1 / TARGET_FPS) - (time.perf_counter() - now)))

    rr.log("hud", rr.TextLog("Quit."))
    logger.info("Quit.")

# -------------------------
# Script entry
# -------------------------
if __name__ == "__main__":
    main_loop()

