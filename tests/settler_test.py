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
from bsm2.asm1_bsm2 import ASM1reactor

from asm1.plantperformance import PlantPerformance


tempmodel = True   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
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

y_in_r = np.zeros(21)
ys_was = np.zeros(21)
ys_ret = np.zeros(21)
ys_eff = np.zeros(25)


start = time.perf_counter()

for step in simtime:
    y_in_r = (y_in*y_in[14]+ys_ret*ys_ret[14])/(y_in[14]+ys_ret[14])
    y_in_r[14] = y_in[14] + ys_ret[14]

    ys_ret, ys_was, ys_eff = settler.outputs(timestep, step, y_in)


stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Effluent at t =', endtime, 'd: \n', ys_eff)

print('Return sludge at t =', endtime, 'd: \n', ys_ret)
print('Waste sludge at t =', endtime, 'd: \n', ys_was)

ys_eff_matlab = np.array([27.2261906234849, 58.1761856778940, 57.6331639834608, 226.761517652130, 31.5791330041318, -1.66421414831116e-192, -1.16601864259075e-191, -8.11672191131637e-49, -5.42862363860910e-48, 23.8594656340447, 5.65160603095694, 10.0499716031479, 7.00000000000000, 236.980360979792, 20348.03612112084, 14.8580800598190, 0, 0, 0, 0, 0])
ys_ret_matlab = np.array([27.2261906234849, 58.1761856778940, 2457.35553685526, 9668.62883162335, 1346.46706814607, -7.09585517990803e-191, -4.97165550076186e-190, -4.79462592055835e-49, -3.20675803848598e-48, 23.8594656340447, 5.65160603095694, 428.509414671749, 7.00000000000000, 10104.3385774685, 20648, 14.8580800598190, 0, 0, 0, 0, 0])
ys_was_matlab = np.array([27.2261906234849, 58.1761856778940, 2457.35553685526, 9668.62883162335, 1346.46706814607, -7.09585517990803e-191, -4.97165550076186e-190, -4.79462592055835e-49, -3.20675803848598e-48, 23.8594656340447, 5.65160603095694, 428.509414671749, 7.00000000000000, 10104.3385774685, 300, 14.8580800598190, 0, 0, 0, 0, 0])

print('Effluent difference to MatLab solution: \n', ys_eff_matlab - ys_eff[:21])
print('Return sludge difference to MatLab solution: \n', ys_ret_matlab - ys_ret)
print('Waste sludge difference to MatLab solution: \n', ys_was_matlab - ys_was)

# assert np.allclose(ys_eff[:21], ys_eff_matlab, rtol=1e-5, atol=1e-5)
# assert np.allclose(ys_ret, ys_ret_matlab, rtol=1e-5, atol=1e-5)
# assert np.allclose(ys_was, ys_was_matlab, rtol=1e-5, atol=1e-5)