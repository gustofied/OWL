from __future__ import annotations
from observability import setup_logging, logger
from dataclasses import dataclass
import math
import time
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
    world_size = 10
    world_half = world_size / 2.0 # can't find a better word for this
    grid_spacing  = 0.5    # distance between neighboring grid lines


    # We dont really need to do Vector2 here, just for unformity and aesthetica
    axes = [
        [Vector2(-world_half, 0.0).to_rr2d(), Vector2(world_half, 0.0).to_rr2d()],   # X axis
        [Vector2(0.0, -world_half).to_rr2d(), Vector2(0.0, world_half).to_rr2d()],   # Y axis
    ]
    rr.log(
        "/map/axes",
        rr.LineStrips2D(axes, colors=[210, 210, 220, 180], radii=0.02, draw_order=60), # might change draw order where things lands on top of each other later
        static=True,
    )

    # Our grid
    # Ticks with a little hacky + grid_spacing / 2.0 since arange is exlusive
    ticks = np.arange(-world_half, world_half + grid_spacing / 2.0, grid_spacing)

    vertical_lines = [
        [Vector2(float(x), -world_half).to_rr2d(), Vector2(float(x), world_half).to_rr2d()]
        for x in ticks
    ]
    horizontal_lines = [
        [Vector2(-world_half, float(y)).to_rr2d(), Vector2(world_half, float(y)).to_rr2d()]
        for y in ticks
    ]
    grid_lines = vertical_lines + horizontal_lines

    rr.log(
        "/map/grid",
        rr.LineStrips2D(grid_lines, colors=[225, 228, 233, 100], radii=0.01, draw_order=0),
        static=True,
    )

    # Here we draw our unit circle
    # Use N+1 samples with endpoint=True so we include both 0 and 2π,
    # which gives us a closed polyline directly.
    sample_count = 256
    angles = np.linspace(0.0, 2.0 * math.pi, sample_count + 1, endpoint=True)
    circle_points = [
        Vector2(math.cos(angle), math.sin(angle)).to_rr2d()
        for angle in angles
    ]
    rr.log(
        "/map/unit_circle",
        rr.LineStrips2D([circle_points], colors=[240, 240, 245, 140], radii=0.025, draw_order=50),
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
        column_shares=[2,2],
        row_shares=[1,1],
))
)



@dataclass
class GameState:
    # Again we have GameState and we have map/world and its gamestate that traverses or wholds a copy of the world
    # so the arrows not the mao with regards to background since it's static, but that might change in future games..
    # this is just the correct intuition play?


    # which now is two vectors
    # v1 is the AGENT's arrow, v2 is the GOAL arrow.
    v1: Vector2  # Agent
    v2: Vector2  # Goal


def step(state: GameState, dt: float) -> GameState:
    """Auto-spin both vectors at fixed angular velocities."""
    return GameState(
        v1=state.v1.rotate(+0.5 * dt),  # Agent 
        v2=state.v2.rotate(-0.5 * dt),  # Goal
    )

# def apply_action(state: GameState, action: float, dt: float) -> GameState:

def render(state: GameState, sim_time_seconds: float):
    rr.set_time("sim_time", duration=sim_time_seconds)

    agent_vec = state.v1   # AGENT arrow
    goal_vec  = state.v2   # GOAL arrow

    # Arrows (distinct colors: Agent = blue-ish, Goal = orange)
    rr.log("map/vectors", rr.Arrows2D(
        vectors=[agent_vec.to_rr2d(), goal_vec.to_rr2d()],
        colors=[[50, 130, 255], [255, 150, 60]],
        radii=0.05,
        draw_order=100,
    ))

    # Labels at arrow tips ("Agent" and "Goal")
    rr.log("map/arrow_labels", rr.Points2D(
        positions=[agent_vec.to_rr2d(), goal_vec.to_rr2d()],
        labels=["Agent", "Goal"],
        radii=0.01,
        draw_order=110,
    ))


def main_loop():
    make_background()

    state = GameState(v1=Vector2(1, 5), v2=Vector2(2, 1))

    logger.info("Started game.")

    start_time = time.perf_counter()
    previous_time = start_time
    last_direction_log_time = -1e9 # hmm what 

    render(state, sim_time_seconds=0.0)

    while True:
        now = time.perf_counter()
        dt = now - previous_time
        sim_time_seconds = now - start_time
        previous_time = now

        if sim_time_seconds >= 20:
            break

        state = step(state, dt)
        render(state, sim_time_seconds)

        n1 = state.v1.normalize()
        n2 = state.v2.normalize()
        cross_value = n1.cross(n2)
        dot_value   = n1.dot(n2)
        if sim_time_seconds - last_direction_log_time >= 0.5: 
            if   cross_value >  EPSILON: direction_label = "LEFT (CCW)"
            elif cross_value < -EPSILON: direction_label = "RIGHT (CW)"
            else:                         direction_label = ("ALIGNED" if dot_value >= 0.0 else "OPPOSITE")
            logger.info(f"relative direction: {direction_label}")
            last_direction_log_time = sim_time_seconds
        time.sleep(max(0.0, (1 / 60) - (time.perf_counter() - now)))

    logger.info("Quit.")


if __name__ == "__main__":
    main_loop()

# https://chatgpt.com/share/68a9dd1d-8998-8008-a41d-274c42c15ac4
