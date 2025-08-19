import rerun as rr
import time
from observability import setup_logging
import rerun.blueprint as rrb
from math_utils import Vector2
from datetime import datetime
import numpy as np
import logging
import time
import rerun.blueprint as rbb
setup_logging(app_name="testing")

my_logger = logging.getLogger("my_logger")
# my_logger.info("testing my logger")


listen = [x+0.25 for x in range(0,100)]


#
nplisten = np.array(listen)
nprangen = np.arange(0,10,1.23)
nplinspacen = np.linspace(0,10,50)

# my_logger.info(nplisten)
# my_logger.info(nprangen)
# my_logger.info(nplinspacen)
combined = []

for number in range(5):
    combined.append([float(nplinspacen[number]), float(nprangen[number])])

my_logger.info(combined)

rr.log(
     "world/lines",
     rr.LineStrips2D(
        strips=combined,
        radii=0.1,
        colors=[180,23,20]  
     )
 )



zeros = np.zeros(32)
asarr = np.asarray([1,2,2])

my_logger.info(zeros)
my_logger.info(asarr)

# Simulation

dt = 0.1
for i in range(0,100):
    rr.log("points/point", rr.Points2D((i,i),  radii= 0.5, colors=[0,222,0]))
    time.sleep(dt)





my_blueprint = rrb.Blueprint(
    rrb.Horizontal(
        rrb.Spatial2DView(origin="points/point"),
        rrb.Spatial2DView(origin="world/lines")
    ),
    collapse_panels=True,
)

rr.send_blueprint(my_blueprint)
