"""
test thickener_bsm2.py
"""

import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')

import numpy as np
import time
from bsm2 import asm1init_bsm2 as asm1init
from bsm2 import thickenerinit_bsm2 as thickenerinit
from bsm2.thickener_bsm2 import Thickener


# definition of the tested thickener:
thickener = Thickener(thickenerinit.THICKENERPAR, asm1init.PAR1)

# CONSTINFLUENT from BSM2:
y_in = np.array([30, 69.5000000000000, 51.2000000000000, 202.320000000000, 28.1700000000000, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 10.5900000000000, 7, 211.267500000000, 18446, 15, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

yt_uf = np.zeros(21)
yt_of = np.zeros(25)


start = time.perf_counter()

for step in simtime:

    yt_uf, yt_of = thickener.outputs(y_in)


stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Underflow at t = 200 d: \n', yt_uf)
print('Overflow at t = 200 d: \n', yt_of)

yt_uf_matlab = np.array([30, 69.5000000000000, 16964.2751488042, 67035.3935176968, 9333.66466683233, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 3508.82175441088, 7, 70000, 54.5585642700000, 15, 0, 0, 0, 0, 0])
yt_of_matlab = np.array([30, 69.5000000000000, 1.02703771566833, 4.05840372332064, 0.565071336921423, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 0.212428308768118, 7, 4.23788458193279, 18391.4414357300, 15, 0, 0, 0, 0, 0])

print('Underflow difference to MatLab solution: \n', yt_uf_matlab - yt_uf)
print('Overflow difference to MatLab solution: \n', yt_of_matlab - yt_of[:21])

assert np.allclose(yt_uf, yt_uf_matlab, rtol=1e-5, atol=1e-5)
assert np.allclose(yt_of[:21], yt_of_matlab, rtol=1e-5, atol=1e-5)