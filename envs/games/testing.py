import rerun as rr
import time
from observability import setup_logging
import rerun.blueprint as rrb

setup_logging(app_name="testing")

rr.set_time("frame", sequence=0) # hmm need to learn abuot this aha
rr.log(
    "text_notes",
    rr.TextDocument("""
    "testing_logs",
    ## Hey, how are you?
    This is a markdown note logged into Rerun.
                    """)
)

dt = 0.05
for i in range(10):
    rr.set_time("frame", sequence=i*1000000)
    rr.set_time("sim_time", duration=i*dt)
    rr.log("logs/value", rr.Scalars(2*i))
    time.sleep(1)

my_blueprint = rrb.Blueprint(
     rrb.Horizontal(
         contents=[
             rrb.TextDocumentView(origin="text_notes", name="Notes"),
             rrb.TimeSeriesView(origin="/logs", name="Values"),
         ],
         name="Main row",
     ),
     collapse_panels=False, 
 )

rr.send_blueprint(my_blueprint) 