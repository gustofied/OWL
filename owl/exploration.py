# just a file for learning testing, and making things
# put this in and oout of owl
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


# Blueprint

