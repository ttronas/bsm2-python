"""
test primclar_bsm2.py
"""

import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')

import numpy as np
import time
from bsm2.helpers_bsm2 import combiner, splitter


tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated


# CONSTINFLUENT from BSM2:
y_in1 = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])

# Constant influent based on digester input from BSM2:
y_in2 = np.array([28.0665048629843, 48.9525780251450, 10361.7145189587, 20375.0163964256, 10210.0695779898, 553.280744847661, 3204.66026217631, 0.252251384955929, 1.68714307465010, 28.9098125063162, 4.68341082328394, 906.093288634802, 7.15490225533614, 33528.5561252986, 178.467454963180, 14.8580800598190, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

y_mix = np.zeros(21)



start = time.perf_counter()


y_mix = combiner(y_in1, y_in2)

y_split1, y_split2 = splitter(y_in1, np.array([0.5, 0.5]))


stop = time.perf_counter()

print('Simulation completed after: ', stop - start, 'seconds')
print('Mix: \n', y_mix)
print('Split flow 1: \n', y_split1)
print('Split flow 2: \n', y_split2)

# y_mix_ref = np.array([30, 69.5000000000000, 26.0206415019475, 102.822191185039, 14.3164349826144, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 5.38200377940671, 7, 107.369450752201, 18316.8780000000, 15, 0, 0, 0, 0, 0])
# y_split1_ref = np.array([30, 69.5000000000000, 3623.07185550945, 14316.7948790366, 1993.39715175198, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 749.381463864162, 7, 14949.9479147235, 129.122000000000, 15, 0, 0, 0, 0, 0])
# y_split2_ref = np.array([30, 69.5000000000000, 3623.07185550945, 14316.7948790366, 1993.39715175198, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 749.381463864162, 7, 14949.9479147235, 129.122000000000, 15, 0, 0, 0, 0, 0])

# print('Mix difference: \n', y_mix_ref - y_mix)
# print('Split flow 1 difference: \n', y_split1_ref - y_split1)
# print('Split flow 2 difference: \n', y_split2_ref - y_split2)


# assert np.allclose(y_mix, y_mix_ref, rtol=1e-5, atol=1e-5)
# assert np.allclose(y_split1, y_split1_ref, rtol=1e-5, atol=1e-5)
# assert np.allclose(y_split2, y_split2_ref, rtol=1e-5, atol=1e-5)
