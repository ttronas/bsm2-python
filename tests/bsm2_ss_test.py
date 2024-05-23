"""Execution file for the BSM2 Open Loop Test Case.
The test case is based on the BSM2 Benchmark Simulation Model No. 2 (BSM2) and does not contain any controllers. It runs the BSM2 model with steady state influent data.
"""

def test_bsm2_ss():
    import sys
    import os
    import numpy as np
    import time
    import csv
    from tqdm import tqdm
    import os

    path_name = os.path.dirname(__file__)
    sys.path.append(path_name + '/..')

    from bsm2.bsm2_ol import BSM2_OL

    with open(path_name + '/../data/constinfluent_bsm2.csv', 'r', encoding='utf-8-sig') as f:
        data_in = np.array(list(csv.reader(f, delimiter=","))).astype(np.float64)

    bsm2_ol = BSM2_OL(endtime=200, timestep=15/60/24, data_in=data_in)
    start = time.perf_counter()
    for idx, stime in enumerate(tqdm(bsm2_ol.simtime)):
        bsm2_ol.step(idx)
    stop = time.perf_counter()

    print('Steady state simulation for 200 days completed after: ', stop - start, 'seconds')
    print('Effluent at t =', bsm2_ol.endtime, 'd:  \n', bsm2_ol.y_eff_all[-1, :])

    # Values from steady state simulation in Matlab (bsm2_ss_test.slx):
    y_eff_matlab = np.array([28.0642887119962,0.673364475815250,5.91913835971477,0.123285601784297,8.66136144290520,0.648399156210382,3.74853796399266,1.37475295428356,9.19481822135851,0.158452042351794,0.559426467987976,0.00924276243835767,4.56455955711027,14.3255418934555,20640.7790857910,14.8580800597899,0,0,0,0,0])

    print('Effluent difference to MatLab solution: \n', y_eff_matlab - bsm2_ol.y_eff_all[-1, :])

    assert np.allclose(bsm2_ol.y_eff_all[-1, :], y_eff_matlab, rtol=3e-1, atol=1e0)


test_bsm2_ss()
