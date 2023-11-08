"""
test primclar_bsm2.py
"""

import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')

import numpy as np
import time
from bsm2 import asm1init_bsm2 as asm1init
from bsm2 import primclarinit_bsm2 as primclarinit
from bsm2.primclar_bsm2 import PrimaryClarifier


tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated


# definition of the tested clarifier:
primclar = PrimaryClarifier(primclarinit.VOL_P, primclarinit.yinit1, primclarinit.PAR_P, asm1init.PAR1, primclarinit.XVECTOR_P, tempmodel, activate)

# CONSTINFLUENT from BSM2:
y_in = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

yp_out = np.zeros(21)
yp_eff = np.zeros(25)


start = time.perf_counter()

for step in simtime:

    yp_out, yp_eff = primclar.outputs(timestep, step, y_in)


stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Effluent at t = 200 d: \n', yp_eff)
print('Sludge at t = 200 d: \n', yp_out)

yp_eff_matlab = np.array([30, 69.5000000000000, 26.0206415019475, 102.822191185039, 14.3164349826144, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 5.38200377940671, 7, 107.369450752201, 18316.8780000000, 15, 0, 0, 0, 0, 0])
yp_out_matlab = np.array([30, 69.5000000000000, 3623.07185550945, 14316.7948790366, 1993.39715175198, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 749.381463864162, 7, 14949.9479147235, 129.122000000000, 15, 0, 0, 0, 0, 0])

print('Effluent difference to MatLab solution: \n', yp_eff_matlab - yp_eff[:21])
print('Sludge difference to MatLab solution: \n', yp_out_matlab - yp_out)

assert np.allclose(yp_eff[:21], yp_eff_matlab, rtol=1e-5, atol=1e-5)
assert np.allclose(yp_out, yp_out_matlab, rtol=1e-5, atol=1e-5)