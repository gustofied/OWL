# just a file for learning testing, and making things

import rerun as rr
import rerun.blueprint as rrb
import numpy as np
import logging


# Observability setup

logging.basicConfig(level=logging.INFO)
my_logger = logging.getLogger("hey")
logging.getLogger().addHandler(rr.LoggingHandler("logs/handler"))
rr.init("main", spawn=True)
my_logger.info("Hello World")


# Numpy

np1 = np.array([[10,1,2,3,4,5,6,7,],[8,9,10,11,12,13,14,15]])
x = np.where(np1 != 2)
print(x)
print(np1[x])
print(np.sort(np1[x]))

for x in np.nditer(x):
    print(x)


np1 = np.array([[10,1,2,3,4,5,6,7,],[8,9,10,11,12,13,14,15]])
np2 = np.array([0,1,2])


np3 = np.array([10,20,11,21])
np4 = np.array([True,False,True,True])
print(np3[np4])
# Blueprint

