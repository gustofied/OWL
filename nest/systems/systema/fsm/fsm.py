from enum import IntEnum

class States(IntEnum):
    A = 0
    B = 2
    C = 3

print((States.B.value  + 1))