"""
test dewatering_bsm2.py
"""

import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')

import numpy as np
import time
from bsm2 import adm1init_bsm2 as adm1init
from bsm2.adm1_bsm2 import ADM1Reactor


# definition of the tested dewatering:
adm1Reactor = ADM1Reactor(adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, adm1init.DIM_D)

# CONSTINFLUENT from BSM2:
y_in = np.array([30, 69.5000000000000, 51.2000000000000, 202.320000000000, 28.1700000000000, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 10.5900000000000, 7, 211.267500000000, 18446, 15, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

y_out2 = np.zeros(21)
yd_out = np.zeros(51)
y_out1 = np.zeros(33)


start = time.perf_counter()

for step in simtime:

    y_out2, yd_out, y_out1 = adm1Reactor.outputs(timestep, step, y_in, adm1init.T_op)


stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('ASM1 output at t = 200 d: \n', y_out2)
print('Digester output at t = 200 d: \n', yd_out)
print('ADM1 output at t = 200 d: \n', y_out1)

y_out2_matlab = np.array([30, 69.5000000000000, 67857.1005952170, 268141.574070787, 37334.6586673293, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 14035.2870176435, 7, 280000, 13.6396410675000, 15, 0, 0, 0, 0, 0])
yd_out_matlab = np.array([30, 69.5000000000000, 1.02475774302266, 4.04939426891298, 0.563816906659147, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 0.211956728488476, 7, 4.22847668894609, 18432.3603589325, 15, 0, 0, 0, 0, 0])
y_out1_matlab = np.array([30, 69.5000000000000, 1.02475774302266, 4.04939426891298, 0.563816906659147, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 0.211956728488476, 7, 4.22847668894609, 18432.3603589325, 15, 0, 0, 0, 0, 0])

print('ASM1 output difference to MatLab solution: \n', y_out2_matlab - y_out2)
print('Digester output difference to MatLab solution: \n', yd_out_matlab - yd_out)
print('ADM1 output difference to MatLab solution: \n', y_out1_matlab - y_out1)

assert np.allclose(y_out2, y_out2_matlab, rtol=1e-5, atol=1e-5)
assert np.allclose(yd_out, yd_out_matlab, rtol=1e-5, atol=1e-5)
assert np.allclose(y_out1, y_out1_matlab, rtol=1e-5, atol=1e-5)