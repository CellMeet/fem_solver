import numpy as np

data = np.loadtxt("result.txt", skiprows=1)

z = data[:,3]
u = data[:,4]

print(np.max(np.abs(u - z)))