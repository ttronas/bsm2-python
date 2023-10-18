"""
test primclar_bsm2.py
"""

import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')

import numpy as np
import csv
import time
from bsm2 import primclarinit_bsm2
from bsm2.primclar_bsm2 import PrimaryClarifier
from bsm2.settler1d_bsm2 import Settler
import bsm2.asm1init_bsm2 as asm1init
import bsm2.settler1dinit_bsm2 as settler1dinit
from asm1.asm1 import ASM1reactor

from asm1.plantperformance import PlantPerformance


tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated


# definition of the tested clarifier:
primclar = PrimaryClarifier(primclarinit_bsm2.VOL_P, primclarinit_bsm2.yinit1, primclarinit_bsm2.PAR_P, asm1init.PAR1, primclarinit_bsm2.XVECTOR_P, tempmodel, activate)

# CONSTINFLUENT from BSM1:
y_in = np.array([2.7226191e1, 5.8176186e1, 9.2499001e1, 3.6394347e2, 5.0683288e1, 0, 0, 0, 0, 2.3859466e1, 5.6516060e0, 1.6129816e1, 7.0000000e0, 3.8034432e2, 2.0648361e4, 1.4858080e1, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

yp_out = np.zeros(21)
yp_eff = np.zeros(25)


start = time.perf_counter()

for step in simtime:

    yp_out, yp_eff = primclar.output(timestep, step, y_in)


stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Effluent at t = 200 d: \n', yp_eff)

print('Sludge at t = 200 d: \n', yp_out)

yp_eff_matlab = np.array([2.72261910e+01, 5.81761860e+01, 4.81526527e+01, 1.89459814e+02, 2.63844446e+01, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 2.38594660e+01, 5.65160600e+00, 8.39677640e+00, 7.00000000e+00, 1.97997683e+02, 2.05038225e+04, 1.48580800e+01, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 4.29077631e+01, 4.29077631e+01, 3.49399288e+02, 6.79774222e+01])
yp_out_matlab = np.array([2.72261910e+01, 5.81761860e+01, 6.38334526e+03, 2.51156964e+04, 3.49764779e+03, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 2.38594660e+01, 5.65160600e+00, 1.11311672e+03, 7.00000000e+00, 2.62475171e+04, 1.44538527e+02, 1.48580800e+01, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00])

assert np.allclose(yp_eff, yp_eff_matlab, rtol=1e-5, atol=1e-5)
assert np.allclose(yp_out, yp_out_matlab, rtol=1e-5, atol=1e-5)