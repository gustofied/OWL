from __future__ import annotations

# =========================
# games_math_game.py (full)
# =========================

from dataclasses import dataclass
from enum import Enum
import math
import os
import sys
import threading
import time
from typing import Optional, Annotated

import numpy as np
import rerun as rr
import typer
from rich.console import Console
from rich.panel import Panel

from games_math import Vector2, EPSILON  # your Vector2 class

# -------------------------
# App / UI (Typer + Rich)
# -------------------------
app = typer.Typer(help="games_math steering demo")
console = Console()

# -------------------------
# Reduce Rerun startup noise
# -------------------------
os.environ.setdefault("RUST_LOG", "warn")

# -------------------------
# Rerun init
# -------------------------
rr.init("games_math_game", spawn=True)

description = """

Game mechanics, a user can move the "main arrow"
left arrow on keyboard to rotate to the left
right arrow on keyboard to go right
So we need an update function that changes the pos when we hold one of they keys..
This game is heavy into visuals, setting up nicely for future games.

We also introduce our LLM agent, what can he do here in this game, env?
We make a simple driver, loop,

All is logged first as setup run to wandb ofc to capture it all if we want
Then for live we have rerun visuals and log.
After run we could use rerun or wandb, we are experimenting here getting to know the two
as well as the logging module of python.
As a result we have a simple MVP with the three.

So, games math game, shows us
games math and mechanics, we use it to have an arrow and make a small steering game
We make the translation into LLM digestable so it can interact here
and we play around with logging and visuals both for game wise , but also LLM agent and learning wise
next up is more steering behaviours.

"""

# Make the description visible in the viewer (markdown)
rr.log(
    "docs",
    rr.TextDocument(description, media_type=rr.MediaType.MARKDOWN),
    static=True,
)

# -------------------------
# STATIC BACKGROUND (log once)
# -------------------------
CIRCLE_RADIUS = 1.0
VIEW_PADDING = 0.25
GRID_SPACING = 0.25

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
            radii=0.01,
            draw_order=0
        ),
        static=True,
    )

make_background()

# -------------------------
# Controls
# -------------------------
class KeyBackend(str, Enum):
    global_keys = "global"  # system-wide keyboard hooks (pynput)
    stdin = "stdin"         # read from terminal only

@dataclass
class Controls:
    turn_dir: int = 0          # -1=left, 0=none, +1=right
    last_event: float = 0.0    # when we last saw a keypress

controls = Controls()
_running = True
HOLD_TIMEOUT = 0.25  # only used by stdin backend

def _stdin_keyboard_thread():
    """
    Minimal non-blocking arrow-key listener via stdin.
    Terminal must have focus. Press 'q' to quit.
    """
    global _running
    try:
        import msvcrt  # type: ignore[attr-defined]
        # Windows branch
        while _running:
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                now = time.time()
                if ch in (b"\x00", b"\xe0"):
                    ch2 = msvcrt.getch()
                    if ch2 == b"K":
                        controls.turn_dir = -1; controls.last_event = now
                    elif ch2 == b"M":
                        controls.turn_dir = +1; controls.last_event = now
                elif ch in (b"q", b"Q"):
                    _running = False
            else:
                time.sleep(0.01)
        return
    except Exception:
        pass

    # POSIX branch
    import termios, tty, select  # type: ignore
    fd = sys.stdin.fileno()
    if not sys.stdin.isatty():
        return
    old = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        while _running:
            r, _, _ = select.select([sys.stdin], [], [], 0.05)
            if not r:
                continue
            ch = sys.stdin.read(1)
            now = time.time()
            if ch == "\x1b":  # ESC
                seq = sys.stdin.read(2)  # likely '[' + code
                if len(seq) == 2 and seq[0] == "[":
                    if seq[1] == "D":  # left
                        controls.turn_dir = -1; controls.last_event = now
                    elif seq[1] == "C":  # right
                        controls.turn_dir = +1; controls.last_event = now
            elif ch in ("q", "Q"):
                _running = False
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def start_keyboard_listener(mode: KeyBackend) -> KeyBackend:
    """
    Start the chosen keyboard backend. Returns the actual backend used.
    """
    if mode == KeyBackend.global_keys:
        try:
            from pynput import keyboard  # type: ignore

            def on_press(key):
                global _running
                now = time.time()
                try:
                    if key == keyboard.Key.left:
                        controls.turn_dir = -1; controls.last_event = now
                    elif key == keyboard.Key.right:
                        controls.turn_dir = +1; controls.last_event = now
                    elif getattr(key, "char", "").lower() == "q":
                        _running = False
                except Exception:
                    pass

            def on_release(key):
                # Reset on arrow release; continuous press keeps it set.
                if str(key) in ("Key.left", "Key.right"):
                    controls.turn_dir = 0

            listener = keyboard.Listener(on_press=on_press, on_release=on_release)
            listener.daemon = True
            listener.start()
            return KeyBackend.global_keys
        except Exception as e:
            console.print(
                Panel(
                    f"[yellow]Global key listener not available ({e}). Falling back to stdin.[/yellow]\n"
                    "Tip (macOS): grant Accessibility permission to your terminal/IDE.",
                    title="Input backend",
                    border_style="yellow",
                )
            )
            mode = KeyBackend.stdin

    # stdin backend
    t = threading.Thread(target=_stdin_keyboard_thread, daemon=True)
    t.start()
    return KeyBackend.stdin

# -------------------------
# Simulation parameters
# -------------------------
ANGULAR_SPEED_V1 = +0.8   # base auto-spin (radians/sec) for v1
ANGULAR_SPEED_V2 = -1.2   # constant spin for v2
target_fps = 60.0

# --- state -------------------------------------------------
@dataclass
class GameState:
    v1: Vector2
    v2: Vector2

def _fresh_turn_dir(now: float) -> Optional[int]:
    """Return -1/0/+1 if a turn key is 'held' recently (stdin backend), else None."""
    if now - controls.last_event <= HOLD_TIMEOUT:
        return controls.turn_dir
    return None

def step(state: GameState, dt: float, use_stdin_backend: bool) -> GameState:
    """
    v1:
      - With stdin backend: treat recent keypress as 'held' for a short timeout.
      - With global backend: turn_dir is updated on press/release, no timeout needed.
      - Otherwise auto-spin at ANGULAR_SPEED_V1.
    v2: constant spin.
    """
    if use_stdin_backend:
        dir_override = _fresh_turn_dir(time.time())
    else:
        dir_override = controls.turn_dir if controls.turn_dir != 0 else None

    ang_v1 = (dir_override * abs(ANGULAR_SPEED_V1)) if dir_override is not None else ANGULAR_SPEED_V1
    return GameState(
        v1=state.v1.rotate(ang_v1 * dt),
        v2=state.v2.rotate(ANGULAR_SPEED_V2 * dt),
    )

# --- rendering (all logging lives here) --------------------
def render(state: GameState, t: float, fps_ema: float | None):
    # Rerun 0.23+: relative duration timeline
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
    # Timeseries metrics: use Scalar for compatibility across Rerun versions
    try:
        rr.log("metrics/fps", rr.Scalar(float(fps_ema) if fps_ema is not None else float("nan")))
        rr.log("metrics/theta_deg", rr.Scalar(float(theta_deg)))
    except Exception:
        pass

    rr.log("hud", rr.TextLog(
        f"t={t:6.2f}s  fps~={fps_ema:5.1f}  θ={theta_deg:5.1f}°  turn={controls.turn_dir:+d}"
        if fps_ema is not None else
        f"t={t:6.2f}s  θ={theta_deg:5.1f}°  turn={controls.turn_dir:+d}"
    ))

# --- main loop ---
def main_loop(backend_used: KeyBackend):
    global _running
    state = GameState(v1=Vector2(1, 5), v2=Vector2(2, 1))

    # initial HUD + one frame
    rr.log("hud", rr.TextLog(f"Started game. Backend: {backend_used}. ← / → to steer. Q to quit."))
    t = 0.0
    fps_ema: float | None = None
    render(state, t, fps_ema)

    # timings
    t0 = time.perf_counter()
    prev = t0

    use_stdin_backend = backend_used == KeyBackend.stdin

    while _running:
        now = time.perf_counter()
        dt = now - prev
        prev = now

        state = step(state, dt, use_stdin_backend)
        t = now - t0

        inst_fps = 1.0 / dt if dt > 1e-9 else float("inf")
        fps_ema = inst_fps if fps_ema is None else (0.9 * fps_ema + 0.1 * inst_fps)

        render(state, t, fps_ema)

        time.sleep(max(0.0, (1/target_fps) - (time.perf_counter() - now)))

    rr.log("hud", rr.TextLog("Quit."))

# -------------------------
# Typer command
# -------------------------
@app.command()
def play(
    fps: Annotated[float, typer.Option("--fps", help="Target frames per second")] = 60.0,
    speed: Annotated[float, typer.Option("--speed", help="Scale angular speeds")] = 1.0,
    verbose: Annotated[bool, typer.Option("--verbose/--quiet", help="Show startup panel")] = True,
    keys: Annotated[KeyBackend, typer.Option("--keys", case_sensitive=False, help="Keyboard input backend: global or stdin")] = KeyBackend.global_keys,
):
    """
    Run the demo; steer with ← / →. Press Q to quit.
    - keys=global: works even when the Rerun window has focus (requires 'pynput').
    - keys=stdin : terminal must keep focus; no extra deps.
    """
    global target_fps, ANGULAR_SPEED_V1, ANGULAR_SPEED_V2

    target_fps = max(1.0, float(fps))
    ANGULAR_SPEED_V1 = +0.8 * float(speed)
    ANGULAR_SPEED_V2 = -1.2 * float(speed)

    if verbose:
        console.print(Panel(
            f"FPS={target_fps}  speed×{speed}\nControls: ← / →   Quit: Q\nBackend: {keys}",
            title="games_math",
            border_style="cyan",
        ))

    backend_used = start_keyboard_listener(keys)
    if backend_used != keys and verbose:
        console.print(Panel(f"Using backend: {backend_used}", title="Input", border_style="yellow"))

    main_loop(backend_used)

# -------------------------
# Script entry
# -------------------------
if __name__ == "__main__":
    # If called without args, just run the game (show panel).
    if len(sys.argv) == 1:
        play()  # defaults work because we use Annotated, not Option() defaults
    else:
        app()

# https://chatgpt.com/share/689e4ef6-8da4-8008-8786-05968503263d
