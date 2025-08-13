import math
import numpy as np
EPSILON = 1e-6

class Vector2:
    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

    def __iter__(self): # now I can do list(Vector2()), and have iterable behavior on our Vector2
        yield self.x
        yield self.y

    def __array__(self, dtype=None, copy=None): # but we will just do Vector2() mostly as we implement this thing here
        return np.asarray((self.x, self.y), dtype=dtype)

    def magnitude(self) -> float:
        """Return the vector's length."""
        return math.hypot(self.x, self.y) # returns the hypotenuse

    def normalize(self) -> "Vector2":
        """Return a new normalized vector (unit length)."""
        m = self.magnitude()
        if m < 0: # If a vector has a magnitude of 0, it has no direction:) 
            return Vector2(0.0, 0.0)
        return Vector2(self.x / m, self.y / m)

    def normalize_me(self) -> None:
        """Scale this vector so it has a length of 1 (modifies in place)."""
        m = self.magnitude()
        if m >= 0:
            self.x /= m
            self.y /= m
            
    def is_normalized(self, tol: float = EPSILON) -> bool:
        """Quickly check if the vector is unit-length (within tolerance of EPSI)."""
        length_sq = self.x * self.x + self.y * self.y 
        return abs(length_sq - 1.0) <= tol
    
    def dot(self, other: "Vector2") -> float: # Algebraic dot product
        """Return the dot product with another vector."""
        return self.x * other.x + self.y * other.y

    def cross(self, other: "Vector2") -> float: # The determinant of the 2x2 matrix, cross is for 3D but z input is 0 here
        """Return the cross product (scalar), positive if 'other' is to the left."""
        return self.x * other.y - self.y * other.x

    def angle(self, other: "Vector2", degrees: bool = False) -> float:
        """Return the unsigned angle between this vector and another."""
        magnitude_self = self.magnitude()
        magnitude_other = other.magnitude()
        if magnitude_self == 0 or magnitude_other == 0:
            return 0.0
        cosine_of_angle = self.dot(other) / (magnitude_self * magnitude_other)
        cosine_of_angle = max(-1.0, min(1.0, cosine_of_angle))  # Clamper here for precision safety
        angle_radians = math.acos(cosine_of_angle)
        return math.degrees(angle_radians) if degrees else angle_radians

    def angle_with_direction(self, other: "Vector2", degrees: bool = False) -> float: # i like the right facing vecotr as refereence method better havent grasped this one fully yet
        """Return signed angle to 'other'. Positive = turn left, Negative = turn right."""
        dot_value = self.dot(other)
        cross_value = self.cross(other)
        angle_radians = math.atan2(cross_value, dot_value)
        return math.degrees(angle_radians) if degrees else angle_radians
    
    def rotate(self, angle_radians: float, degrees: bool = False, pivot: "Vector2" = None) -> "Vector2": # we use rotation matrix here yeh
        """Return a new vector rotated by the given angle around a pivot (default: origin)."""
        if degrees:
            angle_radians = math.radians(angle_radians)
        cosine_angle = math.cos(angle_radians)
        sine_angle = math.sin(angle_radians)

        if pivot:
            # Translate so pivot becomes origin
            delta_x = self.x - pivot.x
            delta_y = self.y - pivot.y
            rotated_x = delta_x * cosine_angle - delta_y * sine_angle
            rotated_y = delta_x * sine_angle + delta_y * cosine_angle
            # Translate back to world space
            return Vector2(pivot.x + rotated_x, pivot.y + rotated_y)
        else:
            # Rotate around origin
            rotated_x = self.x * cosine_angle - self.y * sine_angle
            rotated_y = self.x * sine_angle + self.y * cosine_angle
            return Vector2(rotated_x, rotated_y)

    def rotate_me(self, angle_radians: float, degrees: bool = False, pivot: "Vector2" = None) -> "Vector2":
        """Rotate this vector in place by the given angle around a pivot (default: origin)."""
        rotated = self.rotate(angle_radians, degrees=degrees, pivot=pivot)
        self.x, self.y = rotated.x, rotated.y
        return self




