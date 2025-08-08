# Vectors
# Give me a vector, it tells me a direction, and for how long. Length can  also be called magnitude.
# Vector consits of a magnitude and a direction
# https://www.geeksforgeeks.org/python/how-to-create-a-vector-in-python-using-numpy/ 
# B = (0, -4) We are moving from 0 to -4, the arrow is towards -4 :)

import numpy as np

# 1)

# 2D vector
v2 = np.array([1.213123, 3.123213])

# 3D vector
v3 = np.array([1.2, -5.0, 6.6])

# 2) Constant / zero / ones
zeros2 = np.zeros(2)           # [0., 0.]
ones3  = np.ones(3) * 7        # [7., 7., 7.]
full4  = np.full(4, 2.5)       # [2.5,2.5,2.5,2.5]

# 3) Evenly or log spaced
ar   = np.arange(0, 1, 0.25)   # [0.,0.25,0.5,0.75]
lin  = np.linspace(0, 1, 5)    # [0.,0.25,0.5,0.75,1.]
log  = np.logspace(0, 2, 5)    # [1.,3.16,10.,31.6,100.]

# 4) Random vectors
u1 = np.random.rand(2)         # uniform [0,1)
u2 = np.random.randn(2)        # normal(0,1)
u3 = np.random.uniform(-1,1,2) # uniform [-1,1)
i2 = np.random.randint(0, 10, 2)

# 5) Basis / unit vectors
e1 = np.eye(3)[0]              # [1.,0.,0.]
e2 = np.eye(3)[1]              # [0.,1.,0.]

# Magnitude/length/distance

# Magnitude as we said is the length, it has other terms as length and also distance. We use them all
# How is this calculated, fundemental stuff, https://www.youtube.com/watch?v=5ptH2Xw4DZc 
v2 = np.array([3.0, 4.0]) # change our first one here lol
# 1) squares:     [9.0, 16.0] 
# 2) sum:         25.0
# 3) sqrt of sum: 5.0
length = np.linalg.norm(v2)   # 5.0

# Unit vector

# In the games we are sometimes interested in the pure direction, we then have the unit vector which
# is capped at the length of 1, it's our vector but with a length of 1. https://www.youtube.com/watch?v=f5DHYCKyVRo The OG guy
# To calculate it we do normalisation
# A unit vector is often depicted by a little dash or ^above the vector name.
# Unit vecotr are useful for a variety of reasons, such as multiplying our speed by it to get a character to moce in a particular direction at a particular speed, or when 
# calculating the angle of rotation between two points.


# 2) divide v2 by length to get unit vector

unit_v2 = v2/ length               # [0.6, 0.8]



# DOT Product https://www.youtube.com/watch?v=2PrSUK1VrKA, some intuition, and calculate via https://www.youtube.com/watch?v=dYPRYO8QhxU&t=84s (finding angle between to vectors)
vector1 = np.asarray([1,2])
vector2 = np.asarray([2,3])

dot_product = np.dot(vector1, vector2)
print(dot_product)




# But what we are interested in is the Angle ofthen between two objects, so what we do is use DOT product

# Lengths/magnitudes of the vectors, normalaized..
norm1 = np.linalg.norm(vector1)
norm2 = np.linalg.norm(vector2)

# Calculate the cosine of the angle

cosine_angle = dot_product / (norm1 * norm2)
cosine_angle = np.clip(cosine_angle, -1.0, 1.0) # np.clip is a safety-net that keeps a value (or every element of an array) inside the interval you specify.


# And the angle is then

angle_radians = np.arccos(cosine_angle) # in radians

angle_degrees = np.degrees(angle_radians) # in degrees

print(angle_degrees)

# Often we work with unit vectors when calcultating for dots and angles

u1 = vector1 / norm1
u2 = vector2 / norm2

angle_deg_units = np.degrees(
    np.arccos(
        np.clip(np.dot(u1, u2), -1.0, 1.0)   # dot product of the two unit vectors
    )
)
print("angle (unit vecs, deg) =", angle_deg_units)

# Knowing then angle, the theta θ tells us how much to turn in order to be same as the other one, but it does not say in which way to turn.
# In numpy we have np.arctan2

dot_product = dot_product
cross_product = vector1[0]*vector2[1] - vector1[1]*vector2[0]
signed_angle = np.arctan2(cross_product, dot_product)


# But in our games we use the idea, of storing “storing the right-facing vector for our agents.”

# The right-facing vector is always perpendicular to the forward-facing vector.
# In 2D, if forward = [x, y], then right = [y, -x] (a 90-degree clockwise rotation).
forward = np.array([1.0, 0.0])                  # Agent is facing right
right   = np.array([forward[1], -forward[0]])  # So right is pointing down

# Example target direction
target = np.array([0.0, 1.0])   # Target is above the agent

# Simple left/right decision based on the dot product with the right vector
side = np.dot(right, target)

if side > 0:
    print("Target is to the RIGHT → turn right")
elif side < 0:
    print("Target is to the LEFT → turn left")
else:
    print("Target is straight ahead or behind")

# Rotation

# At times you will want to rotate around a point. This may be around the origin or some arbitrary point in the world. 
# Rotation around origin , rotation around a point -> https://www.youtube.com/watch?v=FqiGuTtjmMg&t https://www.youtube.com/watch?v=LSq3JlS9LcY 
# Maybe a vid or two about transition matrix?



# 1) Create a 2×2 rotation matrix for a given angle (in radians)
def create_rotation_matrix_2d(angle_radians: float) -> np.ndarray:
    """
    Returns the 2×2 rotation matrix that rotates vectors
    by 'angle_radians' counter-clockwise about the origin.
    """
    cosine_of_angle = np.cos(angle_radians)
    sine_of_angle   = np.sin(angle_radians)

    rotation_matrix_2d = np.array([
        [ cosine_of_angle, -sine_of_angle ],
        [ sine_of_angle,    cosine_of_angle ]
    ])
    return rotation_matrix_2d

# 2) Example inputs
vector_to_rotate = np.array([3.0, 4.0])
pivot_point      = np.array([1.0, 2.0])
angle_degrees    = 30.0

# Convert degrees → radians
angle_radians = np.deg2rad(angle_degrees)

# 3) Rotate about the ORIGIN
rotation_matrix = create_rotation_matrix_2d(angle_radians)
rotated_about_origin = rotation_matrix.dot(vector_to_rotate)
print("Rotated about origin:", rotated_about_origin)
# → array([2.59807621, 5.09807621])

# 4) Rotate about an ARBITRARY PIVOT
#  4a) Translate vector so pivot is at the origin
translated_vector = vector_to_rotate - pivot_point

#  4b) Rotate in local space
rotated_translated_vector = rotation_matrix.dot(translated_vector)

#  4c) Translate back into world space
rotated_about_pivot = rotated_translated_vector + pivot_point
print("Rotated about pivot:", rotated_about_pivot)
# → array([2.36602540, 3.73205081])

# Note: NumPy does not include a built-in vector-rotation function,
# so this is the standard, efficient pattern—build your rotation matrix once,
# then apply it via dot() or the @ operator.

# Have this at the end, maybe we have like this at each chapter end classes we could use:)


class Vector2:
    def __init__(self, x, y):
        self.x: float = x
        self.y: float = y

    def magnitude(self):
        length = Vector2().linlag.norm(Vector2) # lol?
        # Hmm how would we do this?


