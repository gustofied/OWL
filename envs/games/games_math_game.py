from rich import print as rprint
import rerun as rr
import numpy as np
from games_math import Vector2
rr.init("games_math_game")
rr.spawn()

v1 = Vector2(1, 2)
v2 = Vector2(1,4)
length = v1.magnitude()
print(v1.angle(v2, degrees=True))


rr.log(
    "map/arrows",
    rr.Arrows2D(
        vectors=[v1,v2],
        colors=[[255, 0, 0]],
        labels=["vector2"],
        radii=0.025,
    ),
)

rprint("[italic red]Hello[/italic red] World!")

