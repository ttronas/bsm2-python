"""testing numba functions"""

import logging

import numpy as np
from numba import jit

logging.basicConfig(level=logging.INFO)


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
    logging.info(a)


def test_numba_example():
    a = numba_example()
    logging.info(a)


test_numba_example()
test_numba_numpy_example()
