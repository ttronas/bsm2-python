"""Execution file for BSM1 model (5 ASM1 reactors in series + settler) test case"""

import csv
import os
import time

import numpy as np
from tqdm import tqdm

import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init
import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit
from bsm2_python.bsm2.asm1_bsm2 import ASM1reactor
from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter
from bsm2_python.bsm2.settler1d_bsm2 import Settler
from bsm2_python.log import logger

path_name = os.path.dirname(__file__)

tempmodel = False  # if False influent wastewater temperature is just passed through process reactors and settler
# if True mass balance for the wastewater temperature is used in process reactors and settler

activate = False  # if False dummy states are 0
# if True dummy states are activated


def test_bsm1():
    # definition of the reactors:
    combiner = Combiner()
    reactor1 = ASM1reactor(
        asm1init.KLA1,
        asm1init.VOL1,
        asm1init.YINIT1,
        asm1init.PAR1,
        asm1init.CARB1,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    reactor2 = ASM1reactor(
        asm1init.KLA2,
        asm1init.VOL2,
        asm1init.YINIT2,
        asm1init.PAR2,
        asm1init.CARB2,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    reactor3 = ASM1reactor(
        asm1init.KLA3,
        asm1init.VOL3,
        asm1init.YINIT3,
        asm1init.PAR3,
        asm1init.CARB3,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    reactor4 = ASM1reactor(
        asm1init.KLA4,
        asm1init.VOL4,
        asm1init.YINIT4,
        asm1init.PAR4,
        asm1init.CARB4,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    reactor5 = ASM1reactor(
        asm1init.KLA5,
        asm1init.VOL5,
        asm1init.YINIT5,
        asm1init.PAR5,
        asm1init.CARB5,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    reactor5 = ASM1reactor(
        asm1init.KLA5,
        asm1init.VOL5,
        asm1init.YINIT5,
        asm1init.PAR5,
        asm1init.CARB5,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    splitter = Splitter()
    settler = Settler(
        settler1dinit.DIM,
        settler1dinit.LAYER,
        asm1init.QR,
        asm1init.QW,
        settler1dinit.settlerinit,
        settler1dinit.SETTLERPAR,
        asm1init.PAR1,
        tempmodel,
        settler1dinit.MODELTYPE,
    )

    # CONSTINFLUENT from BSM2:
    y_in = np.array(
        [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0]
    )

    timestep = 15 / (60 * 24)
    endtime = 200
    simtime = np.arange(0, endtime, timestep)

    y_out1 = np.zeros(21)
    y_out2 = np.zeros(21)
    y_out3 = np.zeros(21)
    y_out4 = np.zeros(21)
    y_out5 = np.zeros(21)
    y_out5_r = np.zeros(21)
    ys_in = np.zeros(21)
    ys_out = np.zeros(21)
    ys_eff = np.zeros(21)
    qintr = asm1init.QINTR
    sludge_height = 0

    start = time.perf_counter()

    for step in simtime:
        y_in1 = combiner.output(y_in, ys_out, y_out5_r)

        y_out1 = reactor1.output(timestep, step, y_in1)
        y_out2 = reactor2.output(timestep, step, y_out1)
        y_out3 = reactor3.output(timestep, step, y_out2)
        y_out4 = reactor4.output(timestep, step, y_out3)
        y_out5 = reactor5.output(timestep, step, y_out4)

        ys_in, y_out5_r = splitter.output(y_out5, (y_out5[14] - qintr, qintr))

        ys_out, _, ys_eff, sludge_height, ys_tss_internal = settler.output(timestep, step, ys_in)

    stop = time.perf_counter()

    logger.info('Steady state simulation completed after: %s seconds', stop - start)
    logger.info('Effluent at t = %s d: \n %s', endtime, ys_eff)
    logger.info('Sludge height at t = %s d: \n %s', endtime, sludge_height)
    logger.info('TSS in Settler at t = %s d: \n %s', endtime, ys_tss_internal)

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

    logger.info('Effluent difference to MatLab solution: \n %s', ys_eff_matlab - ys_eff)
    logger.info('Sludge height difference to MatLab solution: \n %s', sludge_height_matlab - sludge_height)
    logger.info('TSS in Settler difference to MatLab solution: \n %s', ys_tss_internal_matlab - ys_tss_internal)

    assert np.allclose(ys_eff, ys_eff_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(sludge_height, sludge_height_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(ys_tss_internal, ys_tss_internal_matlab, rtol=1e-5, atol=1e-5)


test_bsm1()


def test_bsm1_ol():
    # definition of the reactors:
    combiner = Combiner()
    reactor1 = ASM1reactor(
        asm1init.KLA1,
        asm1init.VOL1,
        asm1init.YINIT1,
        asm1init.PAR1,
        asm1init.CARB1,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    reactor2 = ASM1reactor(
        asm1init.KLA2,
        asm1init.VOL2,
        asm1init.YINIT2,
        asm1init.PAR2,
        asm1init.CARB2,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    reactor3 = ASM1reactor(
        asm1init.KLA3,
        asm1init.VOL3,
        asm1init.YINIT3,
        asm1init.PAR3,
        asm1init.CARB3,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    reactor4 = ASM1reactor(
        asm1init.KLA4,
        asm1init.VOL4,
        asm1init.YINIT4,
        asm1init.PAR4,
        asm1init.CARB4,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    reactor5 = ASM1reactor(
        asm1init.KLA5,
        asm1init.VOL5,
        asm1init.YINIT5,
        asm1init.PAR5,
        asm1init.CARB5,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    reactor5 = ASM1reactor(
        asm1init.KLA5,
        asm1init.VOL5,
        asm1init.YINIT5,
        asm1init.PAR5,
        asm1init.CARB5,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )
    splitter = Splitter()
    settler = Settler(
        settler1dinit.DIM,
        settler1dinit.LAYER,
        asm1init.QR,
        asm1init.QW,
        settler1dinit.settlerinit,
        settler1dinit.SETTLERPAR,
        asm1init.PAR1,
        tempmodel,
        settler1dinit.MODELTYPE,
    )

    # dyninfluent from BSM2:
    with open(path_name + '/../src/bsm2_python/data/dyninfluent_bsm2.csv', encoding='utf-8-sig') as f:
        data_in = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)

    timestep = 1 / 24 / 60  # 15 minutes in days
    endtime = 50  # only 50 days for testing
    data_time = data_in[:, 0]
    simtime = np.arange(0, endtime, timestep)
    y_in = data_in[:, 1:]
    del data_in

    y_out5_r = np.zeros(21)
    ys_in = np.zeros(21)
    ys_out = np.zeros(21)
    ys_eff = np.zeros(21)
    qintr = asm1init.QINTR
    sludge_height = 0

    ys_eff_all = np.zeros((len(simtime), 21))
    sludge_height_all = np.zeros((len(simtime), 1))
    ys_tss_internal_all = np.zeros((len(simtime), settler1dinit.LAYER[1]))

    start = time.perf_counter()

    for i, step in enumerate(tqdm(simtime)):
        # get influent data that is smaller than and closest to current time step
        y_in_timestep = y_in[np.where(data_time <= step)[0][-1], :]

        y_in1 = combiner.output(y_in_timestep, ys_out, y_out5_r)

        y_out1 = reactor1.output(timestep, step, y_in1)
        y_out2 = reactor2.output(timestep, step, y_out1)
        y_out3 = reactor3.output(timestep, step, y_out2)
        y_out4 = reactor4.output(timestep, step, y_out3)
        y_out5 = reactor5.output(timestep, step, y_out4)

        ys_in, y_out5_r = splitter.output(y_out5, (y_out5[14] - qintr, qintr))

        ys_out, _, ys_eff, sludge_height, ys_tss_internal = settler.output(timestep, step, ys_in)

        ys_eff_all[i] = ys_eff
        sludge_height_all[i] = sludge_height
        ys_tss_internal_all[i] = ys_tss_internal

    stop = time.perf_counter()

    # np.savetxt(path_name + '/../data/test_ys_eff_all.csv', ys_eff_all, delimiter=',')
    # np.savetxt(path_name + '/../data/test_sludge_height_all.csv', sludge_height_all, delimiter=',')

    logger.info('Dynamic open loop simulation completed after: %s seconds', stop - start)
    logger.info('Effluent at t = %s d: \n %s', endtime, ys_eff)
    logger.info('Sludge height at t = %s, d: %s \n', endtime, sludge_height)
    logger.info('TSS in Settler at t = %s d: \n %s', endtime, ys_tss_internal)

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

    logger.info('Effluent difference to MatLab solution: \n %s', ys_eff_matlab - ys_eff)
    logger.info('Sludge height difference to MatLab solution: \n %s', sludge_height_matlab - sludge_height)
    logger.info('TSS in Settler difference to MatLab solution: \n %s', ys_tss_internal_matlab - ys_tss_internal)

    # high tolerances to speed up testing.
    # If timestep is refined (e.g. up to 1 minute), smaller tolerances are achieved.
    assert np.allclose(ys_eff, ys_eff_matlab, rtol=1e-1, atol=7e-1)
    assert np.allclose(sludge_height, sludge_height_matlab, rtol=1e-1)
    assert np.allclose(ys_tss_internal, ys_tss_internal_matlab, rtol=1e-1, atol=1e-1)


test_bsm1_ol()
