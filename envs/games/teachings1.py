from observability import setup_logging
import logging
import numpy as np
import rerun as rr
import rerun.blueprint as rrb
import time
setup_logging(app_name="testing")

my_logger = logging.getLogger("my_logger")
my_logger.info("hey")

listen = np.array([1, 20, 10])
my_logger.warning(listen)

listen2 = np.asarray([1,2,2])
my_logger.warning(listen2)

listen3 = np.arange(1,10,2.5)
my_logger.warning(listen3)

listen4 = np.linspace(1,10) # step size becomes auto 50
my_logger.warning(listen4)


rr.log("tesksten",
       rr.TextDocument(
           text="""
Hello 
There

"""

))


# so im interested in making arrays of points like this
# so this is a point [[1.2,1,3],[1.2,1.4]]
# this is two points in if we use Points2D we get two points
# if we use linestripes we get the two points and a line between them

# then how could we genreate like large networks of these points what is the common way
# and what about longer lines with more points etc
# also what theory python or whatever could i learn more about this

dt = 0.1
start = time.perf_counter()
for x in range(10):
    now = time.perf_counter()
    elapsed = now - start
    positions=[[1+x,0],[0,1+x]]
    rr.set_time("timer", duration=elapsed)
    rr.log("mine_points", rr.Points2D(positions,radii=1,colors=[140,30,200]))
    my_logger.info("one cyle")
    time.sleep(dt)


time.sleep(10)
elapsed = time.perf_counter() - start 
my_logger.info("hey")
    

my_blueprint = rrb.Blueprint(
    rrb.Horizontal(
        contents=[
        rrb.Spatial2DView(origin="mine_points"),
        rrb.TextDocumentView(origin="tesksten"),
        rrb.TextLogView(origin="logs/handler")]
    ),
    auto_layout=True
)

rr.send_blueprint(my_blueprint)

# https://q-viper.github.io/2020/08/10/drawing-simple-geometrical-shapes-on-python-using-numpy-and-visualize-it-with-matplotlib/ 
# https://www.youtube.com/watch?v=CHd4QRGPQ6s&list=PLTd6ceoshprfZs1VIzGHDt-MYgVewC5tc&index=5
# Virkerlig gå inn i numpy