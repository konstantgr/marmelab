# from typing import List
import numpy as np
from time import time


def random_matmul(seed : int = 42) -> np.ndarray:
    M = 5_000
    X = np.random.rand(M, M)
    Y = np.random.rand(M, M)

    return X.dot(Y)


if __name__ == "__main__":
    start_time = time()
    random_matmul()[0, 0]
    print(time() - start_time)

