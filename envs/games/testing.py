import numpy as np
from games_logger import logger, setup_logging


setup_logging() # can also just have it outside main
a = np.zeros(3)
logger.info(type((a)))