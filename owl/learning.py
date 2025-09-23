import math
import rerun as rr
import rerun.blueprint as rrb
from observability import setup_logging
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("learning")
logging.getLogger().addHandler(rr.LoggingHandler("logs/handler"))
rr.init("learning", spawn=True)


logger.info("hey")
print(math.pi)






rr.log(
    "circle",
    rr.LineStrips2D(
        strips=[
            [[0, 0], [2, 1], [4, -1], [6, 0]],
            [[0, 3], [1, 4], [2, 2], [3, 4], [4, 2], [5, 4], [6, 3]],
        ],
        colors=[0,123,0],
        radii=0.2
    )
)

# mys = rrb(


# )¨

# rr.send_blueprint(mys)

a = np.arange(1,10,4)
print(a)

logger.info(([x for x in range(0,10) if x>4]))


for x in range(0,10):
    print(x)
np1 = np.array([1,2,3])
logger.info(np1)

print("hey")