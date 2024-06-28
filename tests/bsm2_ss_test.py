"""Execution file for the BSM2 Open Loop Test Case.
The test case is based on the BSM2 Benchmark Simulation Model No. 2 (BSM2)
and does not contain any controllers. It runs the BSM2 model with steady state influent data.
"""

import csv
import os
import time

import numpy as np
from tqdm import tqdm

from bsm2_python.bsm2_ol import BSM2OL
from bsm2_python.log import logger

path_name = os.path.dirname(__file__)


def test_bsm2_ss():
    with open(path_name + '/../src/bsm2_python/data/constinfluent_bsm2.csv', encoding='utf-8-sig') as f:
        data_in = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)

    bsm2_ol = BSM2OL(endtime=200, timestep=15 / 60 / 24, data_in=data_in, tempmodel=False, activate=False)
    start = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm2_ol.simtime)):
        bsm2_ol.step(idx)
    stop = time.perf_counter()

    logger.info('Steady state simulation for %s days completed after: %s seconds', bsm2_ol.endtime, stop - start)
    logger.info('Effluent at t = %s d: \n %s', bsm2_ol.endtime, bsm2_ol.y_eff_all[-1, :])

    # Values from steady state simulation in Matlab (bsm2_ss_test.slx):
    y_eff_matlab = np.array(
        [
            28.0642887119962,
            0.673364475815250,
            5.91913835971477,
            0.123285601784297,
            8.66136144290520,
            0.648399156210382,
            3.74853796399266,
            1.37475295428356,
            9.19481822135851,
            0.158452042351794,
            0.559426467987976,
            0.00924276243835767,
            4.56455955711027,
            14.3255418934555,
            20640.7790857910,
            14.8580800597899,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    logger.info('Effluent difference to MatLab solution: %s\n', y_eff_matlab - bsm2_ol.y_eff_all[-1, :])

    assert np.allclose(bsm2_ol.y_eff_all[-1, :], y_eff_matlab, rtol=3e-1, atol=1e0)


test_bsm2_ss()
