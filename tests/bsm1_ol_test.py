"""Execution file for BSM1 model (5 ASM1 reactors in series + settler) test case"""

import time

import numpy as np
from tqdm import tqdm

from bsm2_python.bsm1_ol import BSM1OL
from bsm2_python.log import logger

tempmodel = False  # if False influent wastewater temperature is just passed through process reactors and settler
# if True mass balance for the wastewater temperature is used in process reactors and settler

activate = False  # if False dummy states are 0
# if True dummy states are activated


def test_bsm1():
    # CONSTINFLUENT from BSM2:
    y_in = np.array(
        [
            [0.0, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
            [
                200.1,
                30,
                69.5,
                51.2,
                202.32,
                28.17,
                0,
                0,
                0,
                0,
                31.56,
                6.95,
                10.59,
                7,
                211.2675,
                18446,
                15,
                0,
                0,
                0,
                0,
                0,
            ],
        ]
    )
    bsm1_ol = BSM1OL(data_in=y_in, timestep=15 / (60 * 24), endtime=200, tempmodel=tempmodel, activate=activate)

    start = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm1_ol.simtime)):
        bsm1_ol.step(idx)

    stop = time.perf_counter()

    logger.info('Steady state simulation completed after: %s seconds', stop - start)
    logger.info('Effluent at t = %s d: \n %s', bsm1_ol.endtime, bsm1_ol.ys_eff)
    logger.info('Sludge height at t = %s d: \n %s', bsm1_ol.endtime, bsm1_ol.sludge_height)
    logger.info('TSS in Settler at t = %s d: \n %s', bsm1_ol.endtime, bsm1_ol.ys_tss_internal)

    ys_eff_matlab = np.array(
        [
            30.0000000000000,
            0.889492799653682,
            4.39182747787874,
            0.188440413683379,
            9.78152406404732,
            0.572507856962265,
            1.72830016782928,
            0.490943515687561,
            10.4152201204309,
            1.73333146817512,
            0.688280004678034,
            0.0134804685779854,
            4.12557938198182,
            12.4969499853007,
            18061,
            15,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    sludge_height_matlab = 0.447178539974702

    ys_tss_internal_matlab = np.array(
        [
            12.4969498996665,
            18.1132132624131,
            29.5402273766893,
            68.9780506740299,
            356.074706190146,
            356.074706190149,
            356.074706190151,
            356.074706190154,
            356.074706190157,
            6393.98442118288,
        ]
    )

    logger.info('Effluent difference to MatLab solution: \n %s', ys_eff_matlab - bsm1_ol.ys_eff)
    logger.info('Sludge height difference to MatLab solution: \n %s', sludge_height_matlab - bsm1_ol.sludge_height)
    logger.info('TSS in Settler difference to MatLab solution: \n %s', ys_tss_internal_matlab - bsm1_ol.ys_tss_internal)

    assert np.allclose(bsm1_ol.ys_eff, ys_eff_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(bsm1_ol.sludge_height, sludge_height_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(bsm1_ol.ys_tss_internal, ys_tss_internal_matlab, rtol=1e-5, atol=1e-5)


test_bsm1()


def test_bsm1_ol():
    bsm1_ol = BSM1OL(timestep=1 / (60 * 24), endtime=50, tempmodel=tempmodel, activate=activate)

    start = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm1_ol.simtime)):
        bsm1_ol.step(idx)

    stop = time.perf_counter()

    # np.savetxt(path_name + '/../data/test_ys_eff_all.csv', ys_eff_all, delimiter=',')
    # np.savetxt(path_name + '/../data/test_sludge_height_all.csv', sludge_height_all, delimiter=',')

    logger.info('Dynamic open loop simulation completed after: %s seconds', stop - start)
    logger.info('Effluent at t = %s d: \n %s', bsm1_ol.endtime, bsm1_ol.ys_eff)
    logger.info('Sludge height at t = %s, d: %s \n', bsm1_ol.endtime, bsm1_ol.sludge_height)
    logger.info('TSS in Settler at t = %s d: \n %s', bsm1_ol.endtime, bsm1_ol.ys_tss_internal)

    # Values from 50 days dynamic simulation in Matlab (bsm1_test_ol.slx):
    ys_eff_matlab = np.array(
        [
            29.9041779036345,
            2.86336250854119,
            10.4985364014802,
            1.77550626455255,
            24.7216745020295,
            0.0113748400676772,
            2.29517384745407,
            0.244476849395549,
            0.00553950757372690,
            26.6011848861327,
            0.994115660400043,
            0.106244650636689,
            7.41009979441910,
            29.4766993916880,
            20650.7908684698,
            11.4415311578628,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    sludge_height_matlab = 2.83301562022632  # refers to settler[166] in MatLab

    ys_tss_internal_matlab = np.array(
        [
            29.4769209754725,
            71.2561822632383,
            333.123417723819,
            4970.61537819270,
            6014.34928753355,
            7214.70237125071,
            7962.44137776940,
            8579.03662608854,
            9245.26491106585,
            10288.6971730720,
        ]
    )

    logger.info('Effluent difference to MatLab solution: \n %s', ys_eff_matlab - bsm1_ol.ys_eff)
    logger.info('Sludge height difference to MatLab solution: \n %s', sludge_height_matlab - bsm1_ol.sludge_height)
    logger.info('TSS in Settler difference to MatLab solution: \n %s', ys_tss_internal_matlab - bsm1_ol.ys_tss_internal)

    # high tolerances to speed up testing.
    # If timestep is refined (e.g. up to 1 minute), smaller tolerances are achieved.
    assert np.allclose(bsm1_ol.ys_eff, ys_eff_matlab, rtol=1e-1, atol=7e-1)
    assert np.allclose(bsm1_ol.sludge_height, sludge_height_matlab, rtol=1e-1)
    assert np.allclose(bsm1_ol.ys_tss_internal, ys_tss_internal_matlab, rtol=1e-1, atol=1e-1)


test_bsm1_ol()
