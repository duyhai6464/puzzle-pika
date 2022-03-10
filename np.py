import numpy as np

a = np.random.randint(-1, 8, size=64).reshape((8, -1))

print(a)


def sr(x):
    for i in range(len(x)):
        x[:, i] = sorted(x[:, i], key=lambda v: v != -1)


sr(a)
print(a)
