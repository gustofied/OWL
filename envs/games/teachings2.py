from observability import setup_logging
import logging
import rerun as rr
import rerun.blueprint as rrb
import time 

setup_logging(app_name="teachings2")
my_log = logging.getLogger("log")
x = 0
dt = 4



rr.log("poinsta",
       rr.Points2D(
    positions=[[1,1],[1,2]],
    radii=5,
    colors=[233,33,33],
       ),
 static=True)




def step(y):
    return y + 1



hans = 9
dt = 5
start = time.perf_counter()
while x < 11:
    now = time.perf_counter()
    elapsed = now - start
    rr.set_time("timer", duration=elapsed)
    hans = step(hans)
    my_log.info(hans)
    x += 2
    time.sleep(dt)

min_urr = rrb.Blueprint(
    rrb.Vertical(
        contents=[
            rrb.TextLogView(origin="logs/handler"),
            rrb.Spatial2DView(origin="poinsta")
        ]
    ),
    collapse_panels=True,
)


rr.send_blueprint(min_urr)
