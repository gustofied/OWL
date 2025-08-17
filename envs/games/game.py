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
    "/docs",
    rr.TextDocument(description, media_type=rr.MediaType.MARKDOWN),
    static=True,
)


# Let's begin with drawing the static elements kinda the map we could say

def make_background():
    circle_radius = 1.0     # unit circle..
    view_padding  = 0.25    # extend axes/grid slightly beyond the circle
    grid_spacing  = 0.25    # distance between neighboring grid lines


    # a bit opaque what this is
    limit_extent = circle_radius + view_padding

    # --- Circle (closed by construction) --------------------------------
    # Use N+1 samples with endpoint=True so we include both 0 and 2π,
    # which gives us a closed polyline directly.
    sample_count = 256
    angles = np.linspace(0.0, 2.0 * math.pi, sample_count + 1, endpoint=True)
    circle_points = [
        Vector2(math.cos(angle) * circle_radius, math.sin(angle) * circle_radius).to_rr2d()
        for angle in angles
    ]
    rr.log(
        "/map/unit_circle",
        rr.LineStrips2D([circle_points], colors=[240, 240, 245, 140], radii=0.025, draw_order=50),
        static=True,
    )

    # --- Axes ------------------------------------------------------------
    axes = [
        [Vector2(-limit_extent, 0.0).to_rr2d(), Vector2(limit_extent, 0.0).to_rr2d()],   # X axis
        [Vector2(0.0, -limit_extent).to_rr2d(), Vector2(0.0, limit_extent).to_rr2d()],   # Y axis
    ]
    rr.log(
        "/map/axes",
        rr.LineStrips2D(axes, colors=[210, 210, 220, 180], radii=0.02, draw_order=60),
        static=True,
    )

    # --- Grid ------------------------------------------------------------
    ticks = np.arange(-limit_extent, limit_extent + grid_spacing / 2.0, grid_spacing)

    vertical_lines = [
        [Vector2(float(x), -limit_extent).to_rr2d(), Vector2(float(x), limit_extent).to_rr2d()]
        for x in ticks
    ]
    horizontal_lines = [
        [Vector2(-limit_extent, float(y)).to_rr2d(), Vector2(limit_extent, float(y)).to_rr2d()]
        for y in ticks
    ]
    grid_lines = vertical_lines + horizontal_lines

    rr.log(
        "/map/grid",
        rr.LineStrips2D(grid_lines, colors=[225, 228, 233, 100], radii=0.01, draw_order=0),
        static=True,
    )
# Need to learn more about blueprints :) 
# What we do here is make the the grid,axes and unit circle non interactive, so we cant interact with them in rerun, we disable
# nice becasue annoying when hovering in rerun when everything just pops of
# when we enable static=True is just that they are not part of the updating/time set time part of our code, its needed

rr.send_blueprint(
    rrb.Blueprint(
        rrb.Grid(
        rrb.Spatial2DView(
            name="map",
            origin="/",
            overrides={
                "map/grid":        rrb.EntityBehavior(interactive=False),
                "map/axes":        rrb.EntityBehavior(interactive=False),
                "map/unit_circle": rrb.EntityBehavior(interactive=False),
            },
        ),
        rrb.TextLogView(origin="logs", name="Logs"),
    rrb.TextDocumentView(origin="docs", name="Game Docs"),
    grid_columns=2,
    column_shares=[3,2],
    row_shares=[1,1],
))
)

make_background()


# -----------------------------------------------------------------------------
# Simulation parameters
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# Rendering (all logging lives here)
# -----------------------------------------------------------------------------

def render(state: GameState, sim_time_seconds: float):
    rr.set_time("sim_time", duration=sim_time_seconds)

    vector_1 = state.v1
    vector_2 = state.v2

    normalized_v1 = vector_1.normalize()
    normalized_v2 = vector_2.normalize()

    # Vectors
    rr.log("map/vectors", rr.Arrows2D(
        vectors=[vector_1.to_rr2d(), vector_2.to_rr2d()],
        colors=[[200, 20, 20], [100, 20, 20]], radii=0.05, draw_order=100,
    ))

    # Shortest arc from normalized_v1 to normalized_v2 (in screen space)
    normalized_v1_screen = normalized_v1.to_rr2d()
    normalized_v2_screen = normalized_v2.to_rr2d()

    start_angle_screen = math.atan2(normalized_v1_screen.y, normalized_v1_screen.x)
    end_angle_screen   = math.atan2(normalized_v2_screen.y, normalized_v2_screen.x)

    def shortest_delta(start: float, end: float) -> float:
        return (end - start + math.pi) % (2.0 * math.pi) - math.pi

    delta_angle_screen = shortest_delta(start_angle_screen, end_angle_screen)

    arc_radius = 0.8
    samples_per_radian = 48
    sample_count = max(8, int(abs(delta_angle_screen) * samples_per_radian))
    angle_samples = np.linspace(start_angle_screen, start_angle_screen + delta_angle_screen, sample_count, endpoint=True)

    arc_points = [[math.cos(theta) * arc_radius, math.sin(theta) * arc_radius] for theta in angle_samples]

    rr.log("map/angle_arc", rr.LineStrips2D([arc_points], colors=[120, 120, 220, 220], radii=0.02, draw_order=90))

    middle_angle = start_angle_screen + 0.5 * delta_angle_screen
    label_position = [math.cos(middle_angle) * (arc_radius + 0.08), math.sin(middle_angle) * (arc_radius + 0.08)]
    theta_deg = abs(delta_angle_screen) * 180.0 / math.pi
    rr.log("map/angle_label", rr.Points2D(positions=[label_position], labels=[[f"θ = {theta_deg:.1f}°"]], radii=0.0, draw_order=95))


# -----------------------------------------------------------------------------
# Main loop
# -----------------------------------------------------------------------------

def main_loop():
    # initial state
    state = GameState(v1=Vector2(1, 5), v2=Vector2(2, 1))

    logger.info("Started game.")

    start_time = time.perf_counter()
    previous_time = start_time
    last_direction_log_time = -1e9

    # initial frame
    render(state, sim_time_seconds=0.0)

    while True:
        now = time.perf_counter()
        dt = now - previous_time
        sim_time_seconds = now - start_time
        previous_time = now

        # stop condition
        if sim_time_seconds >= RUN_DURATION_S:
            break

        # update
        state = step(state, dt)

        # render
        render(state, sim_time_seconds)

        # Direction message using math_utils only (no new helpers)
        n1 = state.v1.normalize()
        n2 = state.v2.normalize()
        cross_value = n1.cross(n2)
        dot_value   = n1.dot(n2)
        if sim_time_seconds - last_direction_log_time >= 0.5:  # log at most twice per second
            if   cross_value >  EPSILON: direction_label = "LEFT (CCW)"
            elif cross_value < -EPSILON: direction_label = "RIGHT (CW)"
            else:                         direction_label = ("ALIGNED" if dot_value >= 0.0 else "OPPOSITE")
            logger.info(f"relative direction: {direction_label}")
            last_direction_log_time = sim_time_seconds

        # simple frame pacing
        time.sleep(max(0.0, (1 / TARGET_FPS) - (time.perf_counter() - now)))

    logger.info("Quit.")


if __name__ == "__main__":
    make_background()
    main_loop()
