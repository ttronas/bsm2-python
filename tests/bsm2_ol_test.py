"""Execution file for the BSM2 Open Loop Test Case.
The test case is based on the BSM2 Benchmark Simulation Model No. 2 (BSM2) and does not contain any controllers. But it runs the BSM2 model with dynamic influent data.
"""


def test_bsm2_ol():
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

    bsm2_ol = BSM2_OL(endtime=50, timestep=15/60/24)
    start = time.perf_counter()
    for idx, stime in enumerate(tqdm(bsm2_ol.simtime)):
        bsm2_ol.step(idx)
    stop = time.perf_counter()

    print('Dynamic open loop simulation completed after: ', stop - start, 'seconds')
    print('Effluent at t =', bsm2_ol.endtime, 'd:  \n', bsm2_ol.y_eff_all[-1, :])

    # Values from 50 days dynamic simulation in Matlab (bsm2_ol_test.slx):
    y_eff_matlab = np.array([30.3048073995454, 0.727115825514541, 5.71425178672745, 0.149476159082923, 10.2011468520338, 0.675741381093006, 3.11565239524537, 0.685855321678047, 8.90977381477780, 0.611796164282852, 0.551749126735591, 0.0109090777954400, 4.70515110754296, 14.8922014306369, 20959.8789197157, 11.4654727685328, 0, 0, 0, 0, 0])

    print('Effluent difference to MatLab solution: \n', y_eff_matlab - bsm2_ol.y_eff_all[-1, :])


    assert np.allclose(bsm2_ol.y_eff_all[-1, :], y_eff_matlab, rtol=3e-1, atol=1e0)


test_bsm2_ol()
