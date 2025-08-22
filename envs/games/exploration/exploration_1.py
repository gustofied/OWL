from ..observability import setup_logging
import rerun as rr
import rerun.blueprint as rrb
import numpy as np
import math
import logging
import time
from ..math_utils import Vector2

setup_logging(app_name="exploration_1")
logger = logging.getLogger("logger")

logger.info("yo")

x = [1,2,3]
y = [1,2,3]
pairs = list(zip(x,y))

np1 = np.array(x)
np2 = np.array(y)

# how could we make Vector2 ready for translation matrixes?
tall = Vector2(1,2)*2

print(tall.x, tall.y)
print(np1*2, x*2)
# angles = np.linspace(-math.pi,math.pi, endpoint=True, num=256)
# points = [[math.cos(angle), math.sin(angle)] for angle in angles]

# dt = 0.016
# for x in range(100):
#     rr.set_time("frames", sequence=x)
#     logger.info(x)
#     points = [[math.cos(angle + x), math.sin(angle)] for angle in angles]
#     rr.log("" \
#     "circle",
#     rr.LineStrips2D(
#         strips=points,
#         radii=0.02,
#         colors=[140,0,0]
#     ))
#     time.sleep(dt)