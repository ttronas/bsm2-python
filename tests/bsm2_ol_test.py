"""Execution file for the BSM2 Open Loop Test Case.
The test case is based on the BSM2 Benchmark Simulation Model No. 2 (BSM2) and does not contain any controllers.
But it runs the BSM2 model with dynamic influent data.
"""

import time

import numpy as np
from tqdm import tqdm

from bsm2_python.bsm2_ol import BSM2OL
from bsm2_python.log import logger


def test_bsm2_ol():
    bsm2_ol = BSM2OL(endtime=50, timestep=15 / 60 / 24, tempmodel=False, activate=False)
    start = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm2_ol.simtime)):
        bsm2_ol.step(idx)
    stop = time.perf_counter()

    logger.info('Dynamic open loop simulation completed after: %s seconds', stop - start)
    logger.info('Effluent at t = %s d: \n%s', bsm2_ol.endtime, bsm2_ol.y_eff_all[-1, :])

    # Values from 50 days dynamic simulation in Matlab (bsm2_ol_test.slx):
    y_eff_matlab = np.array(
        [
            30.3048073995454,
            0.727115825514541,
            5.71425178672745,
            0.149476159082923,
            10.2011468520338,
            0.675741381093006,
            3.11565239524537,
            0.685855321678047,
            8.90977381477780,
            0.611796164282852,
            0.551749126735591,
            0.0109090777954400,
            4.70515110754296,
            14.8922014306369,
            20959.8789197157,
            11.4654727685328,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    logger.info('Effluent difference to MatLab solution: \n%s', y_eff_matlab - bsm2_ol.y_eff_all[-1, :])

    assert np.allclose(bsm2_ol.y_eff_all[-1, :], y_eff_matlab, rtol=3e-1, atol=1e0)


test_bsm2_ol()
