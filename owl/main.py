import numpy as np
import rerun as rr
import rerun.blueprint as rrb
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger().addHandler(rr.LoggingHandler("logs/handler"))

my_logger = logging.getLogger("main")


rr.init("main", spawn=True)




my_logger.info("hello wolrd")
rr.log(
    "file_descriptor",
    rr.TextDocument(
        """
        This is my text
        """,
        media_type = rr.MediaType.MARKDOWN,

    ),
    static=True
    )

v = np.array([0,11])


rr.log(
    "worlds/arrow",
    rr.Arrows2D(
        vectors=[v],
        radii=0.5,
        colors=[0,0,200]
    )
)
v2 =  np.array([2,21], dtype=np.float32)

rr.log(
    "worlds/arrow2",
    rr.Arrows2D(
        vectors=[v2],
        radii=0.5,
        colors=[0,100,200]
    )
)

points = np.linspace(-np.pi,np.pi, 256, endpoint=True, dtype=np.float32)
angles = [[(np.cos(x)), (np.sin(x))] for x in points]
my_logger.info(angles)

rr.log(
    "worlds/circle",
    rr.LineStrips2D(
        strips=angles,
        radii=0.2,
        colors=(0,200,2),
    )
)



my_blueprint = rrb.Blueprint(
    rrb.Grid(
        contents=[
            rrb.TextDocumentView(origin="file_descriptor"),
            rrb.TextLogView(origin="logs/handler"),
            rrb.Spatial2DView(origin="worlds")
        ]
    )
)
rr.send_blueprint(my_blueprint)