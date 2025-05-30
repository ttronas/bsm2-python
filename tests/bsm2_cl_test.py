"""Execution file for the BSM2 Closed Loop Test Case.
The test case is based on the BSM2 Benchmark Simulation Model No. 2 (BSM2) including the controllers.
But it runs the BSM2 model with dynamic influent data.
"""

import time

import numpy as np
from tqdm import tqdm

from bsm2_python.bsm2_cl import BSM2CL
from bsm2_python.log import logger


def test_bsm2_cl():
    bsm2_cl = BSM2CL(endtime=5, timestep=1 / 60 / 24, tempmodel=False, activate=False, use_noise=2)
    start = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm2_cl.simtime)):
        bsm2_cl.step(idx)

    stop = time.perf_counter()
    logger.info('Dynamic closed loop simulation completed after: %s seconds', stop - start)
    logger.info('Effluent at t = %s d: \n%s', bsm2_cl.endtime, bsm2_cl.y_eff_all[-1, :])
    y_eff_matlab = np.array(
        [
            30.325155279916,
            0.700246902106201,
            5.70368210115735,
            0.139538406214234,
            10.170734195434,
            0.694338562640143,
            3.10834182764915,
            1.65315755118803,
            10.8355276819539,
            0.280568276679927,
            0.552589025343316,
            0.0102191557618448,
            4.54640264730173,
            14.8624763198212,
            21027.7298540125,
            11.4418804233311,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    assert np.allclose(bsm2_cl.y_eff_all[-1, :], y_eff_matlab, rtol=3e-1, atol=1e0)


test_bsm2_cl()
