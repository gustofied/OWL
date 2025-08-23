import numpy as np

np1 = np.array([1,2,3,4])
print(np1)

np2 = np1.view()
print(np2)
np2[0] = 2
print(np1,np2)
