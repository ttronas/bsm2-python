"""
test settler1d_bsm2.py
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


# definition of the tested settler:
settler = Settler(settler1dinit.DIM, settler1dinit.LAYER, asm1init.Qr, asm1init.Qw, settler1dinit.settlerinit, settler1dinit.SETTLERPAR, asm1init.PAR1, tempmodel, settler1dinit.MODELTYPE)

# CONSTINFLUENT from BSM1:
y_in = np.array([27.2261906234849, 58.1761856778940, 92.4990010554089, 363.943473006786, 50.6832881484832, 0, 0, 0, 0, 23.8594656340447, 5.65160603095694, 16.1298160611318, 7, 380.344321658009, 20648.3612112084, 14.8580800598190, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

ys_was = np.zeros(21)
ys_ret = np.zeros(21)
ys_eff = np.zeros(25)
Qintr = 0


start = time.perf_counter()

for step in simtime:

    ys_ret, ys_was, ys_eff = settler.outputs(timestep, step, y_in)


stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Effluent at t =', endtime, 'd: \n', ys_eff)

print('Return sludge at t =', endtime, 'd: \n', ys_ret)
print('Waste sludge at t =', endtime, 'd: \n', ys_was)

yp_eff_matlab = np.array([2.72261910e+01, 5.81761860e+01, 4.81526527e+01, 1.89459814e+02, 2.63844446e+01, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 2.38594660e+01, 5.65160600e+00, 8.39677640e+00, 7.00000000e+00, 1.97997683e+02, 2.05038225e+04, 1.48580800e+01, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 0.00000000e+00, 4.29077631e+01, 4.29077631e+01, 3.49399288e+02, 6.79774222e+01])
ys_ret_matlab = np.array([27.2261906234849, 58.1761856778940, 91.4097458129578, 359.657725794326, 50.0864488670803, 0, 0, 0, 0, 23.8594656340447, 5.65160603095694, 15.9398736130632, 7, 375.865440355774, 20648, 14.8580800598190, 0, 0, 0, 0, 0])
ys_was_matlab = np.array([27.2261906234849, 58.1761856778940, 91.4097458129578, 359.657725794326, 50.0864488670803, 0, 0, 0, 0, 23.8594656340447, 5.65160603095694, 15.9398736130632, 7, 375.865440355774, 300, 14.8580800598190, 0, 0, 0, 0, 0])

# assert np.allclose(yp_eff[:21], yp_eff_matlab, rtol=1e-5, atol=1e-5)
# assert np.allclose(ys_ret, ys_ret_matlab, rtol=1e-5, atol=1e-5)