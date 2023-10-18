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


# definition of the tested reactor:
reactor1 = ASM1reactor(asm1init.KLa1, asm1init.VOL1, asm1init.yinit1, asm1init.PAR1, asm1init.carb1, asm1init.carbonsourceconc, tempmodel, activate)

# CONSTINFLUENT from BSM1:
y_in = np.array([27.2235537504205, 96.9107937289381, 92.4900424710908, 364.891422877989, 49.6096859443932, 0, 0.0854954797530000, -3.80274069948699e-19, 0, 24.7152802660417, 4.79293323378183, 16.2086196296374, 7.06061671973609, 380.307485079920, 20650.3612112084, 14.8580800598190, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

y_out1 = np.zeros(21)


start = time.perf_counter()

for step in simtime:

    y_out1 = reactor1.output(timestep, step, y_in)


stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Out at t =', endtime, 'd: \n', y_out1)

y_out1_matlab = np.array([27.2235537504205, 96.9107937289381, 92.4900424710908, 364.891422877989, 49.6096859443932, -5.19160777634808e-32, 0.0854954797530000, -4.22798843246833e-26, -7.22247608684661e-38, 24.7152802660417, 4.79293323378183, 16.2086196296374, 7.06061671973609, 380.307485079920, 20650.3612112084, 14.8580800598190, 0, 0, 0, 0, 0])

print('Difference to MatLab solution: \n', y_out1_matlab - y_out1)
assert np.allclose(y_out1, y_out1_matlab, rtol=10e-1, atol=2)