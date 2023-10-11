"""Execution file for bsm2 model with primary clarifier, 5 asm1-reactors and a second clarifier in steady state simulation

This script will run the plant (ams1 model + settling model) to steady state. The results are saved as csv file and
are necessary for further dynamic simulations.

This script requires that the following packages are installed within the Python environment you are running this script
in: 'numpy', 'csv', 'time', 'scipy.integrate', 'numba'.

The parameters 'tempmodel' and 'activate' can be set to 'True' if you want to activate them.
"""
import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')

import numpy as np
import csv
import time
import primclarinit_bsm2
from primclar_bsm2 import PrimaryClarifier
from settler1d_bsm2 import Settler
import asm1init_bsm2 as asm1init
import settler1dinit_bsm2 as settler1dinit
from asm1.asm1 import ASM1reactor

from asm1.plantperformance import PlantPerformance


tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated


# definition of the reactors:
primclar = PrimaryClarifier(primclarinit_bsm2.VOL_P, primclarinit_bsm2.yinit1, primclarinit_bsm2.PAR_P, asm1init.PAR1, primclarinit_bsm2.XVECTOR_P, tempmodel, activate)

plantperformance = PlantPerformance()

# CONSTINFLUENT from BSM1:
y_in = np.array([2.7226191e1, 5.8176186e1, 9.2499001e1, 3.6394347e2, 5.0683288e1, 0, 0, 0, 0, 2.3859466e1, 5.6516060e0, 1.6129816e1, 7.0000000e0, 3.8034432e2, 2.0648361e4, 1.4858080e1, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

yp_out = np.zeros(21)
yp_eff = np.zeros(25)
y_out1 = np.zeros(21)
y_out2 = np.zeros(21)
y_out3 = np.zeros(21)
y_out4 = np.zeros(21)
y_out5 = np.zeros(21)
ys_out = np.zeros(21)
ys_eff = np.zeros(25)
ys_in = np.zeros(21)
Qintr = 0


start = time.perf_counter()

for step in simtime:
    y_in_r = (y_in*y_in[14]+ys_out*ys_out[14])/(y_in[14]+ys_out[14])
    y_in_r[14] = y_in[14] + ys_out[14]
    y_in1 = (y_in_r*y_in_r[14]+y_out5*Qintr)/(y_in_r[14]+Qintr)
    y_in1[14] = y_in_r[14]+Qintr

    yp_out, yp_eff = primclar.output(timestep, step, y_in1)


stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Effluent at t = 200 d: ', yp_eff)

print('Sludge at t = 200 d: ', yp_out)