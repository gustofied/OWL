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



# DOT Product


# Have this at the end, maybe we have like this at each chapter end classes we could use:)
class Vector2:
    def __init__(self, x, y):
        self.x: float = x
        self.y: float = y

    def magnitude(self):
        length = Vector2().linlag.norm(Vector2) # lol?
        # Hmm how would we do this?


