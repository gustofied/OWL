from games_math import Vector2


v = Vector2(1,5)
print(v)
v.normalize_me()
print(v.is_normalized())
b = Vector2(3,7)
print(v.angle(b, degrees=True))
