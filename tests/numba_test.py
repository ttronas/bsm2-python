"""testing numba functions"""

import numpy as np
from numba import jit

from logger import log


@jit(nopython=True)
def numba_numpy_example():
    a = np.arange(10)
    b = 0
    for i in range(10):
        b += a[i]
    return b


@jit(nopython=True)
def numba_example():
    a = 0
    for i in range(10):
        a += i
    return a


def test_numba_numpy_example():
    a = numba_numpy_example()
    log.info(a)


def test_numba_example():
    a = numba_example()
    log.info(a)


test_numba_example()
test_numba_numpy_example()
