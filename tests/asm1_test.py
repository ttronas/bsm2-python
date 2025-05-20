"""Execution file for BSM1 model (5 ASM1 reactors in series + settler) test case"""

import csv
import os
import time

import numpy as np
from tqdm import tqdm

import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init
from bsm2_python.bsm2.asm1_bsm2 import ASM1Reactor
from bsm2_python.log import logger

path_name = os.path.dirname(__file__)

tempmodel = False  # if False influent wastewater temperature is just passed through process reactors and settler
# if True mass balance for the wastewater temperature is used in process reactors and settler

activate = False  # if False dummy states are 0
# if True dummy states are activated


def test_asm1():
    # definition of the reactors:
    reactor3 = ASM1Reactor(
        asm1init.KLA3,
        asm1init.VOL3,
        asm1init.YINIT3,
        asm1init.PAR3,
        asm1init.CARB3,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
    )

    # CONSTINFLUENT from BSM2:
    y_in = np.array(
        [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0]
    )

    timestep = 15 / (60 * 24)
    endtime = 50
    simtime = np.arange(0, endtime, timestep)

    y_out3 = np.zeros(21)

    start = time.perf_counter()

    for step in simtime:
        y_out3 = reactor3.output(timestep, step, y_in)

    stop = time.perf_counter()

    logger.info('Steady state simulation completed after: %s seconds', stop - start)
    logger.info('ASM1Reactor Output at t = %s d: \n %s', endtime, y_out3)

    y_out3_matlab = np.array(
        [
            30,
            63.8577381952497,
            51.2,
            195.543287548103,
            36.1897495656497,
            0,
            0.0627660451102823,
            7.32747877688682,
            0,
            31.7048384340176,
            6.49409298588329,
            10.2557226521405,
            7.01034560242983,
            212.246852369147,
            18446,
            15,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    logger.info('ASM1Reactor difference to MatLab solution: \n %s', y_out3_matlab - y_out3)
    assert np.allclose(y_out3, y_out3_matlab, rtol=1e-5, atol=1e-5)


test_asm1()


def test_asm1_ol():
    # definition of the reactors:
    reactor3 = ASM1Reactor(
        asm1init.KLA3,
        asm1init.VOL3,
        asm1init.YINIT3,
        asm1init.PAR3,
        asm1init.CARB3,
        asm1init.CARBONSOURCECONC,
        tempmodel=tempmodel,
        activate=activate,
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

    start = time.perf_counter()

    for step in tqdm(simtime):
        # get influent data that is smaller than and closest to current time step
        y_in_timestep = y_in[np.where(data_time <= step)[0][-1], :]

        y_out3 = reactor3.output(timestep, step, y_in_timestep)

    stop = time.perf_counter()

    logger.info('Dynamic open loop simulation completed after: %s seconds', stop - start)
    logger.info('ASM1Reactor Output at t = %s d: \n %s', endtime, y_out3)

    # Values from 50 days dynamic simulation in Matlab (asm1_test_ol.slx):
    y_out3_matlab = np.array(
        [
            33.2972943166905,
            45.4715684289492,
            103.735225947961,
            391.263490010357,
            70.2387342052505,
            0,
            0.0802099669552863,
            7.66724518052077,
            0,
            15.4123647867143,
            4.89801408270735,
            16.4167919722471,
            7.00887319736455,
            423.988245097985,
            21036.4553586539,
            11.4404477663154,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    logger.info('ASM1Reactor difference to MatLab solution: \n %s', y_out3_matlab - y_out3)
    assert np.allclose(y_out3, y_out3_matlab, rtol=1e-1, atol=7e-1)


test_asm1_ol()
