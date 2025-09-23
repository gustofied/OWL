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

np1 = np.array([1,2,3])
logger.info(np1)