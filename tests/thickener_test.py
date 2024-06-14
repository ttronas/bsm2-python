"""
test thickener_bsm2.py
"""

import csv
import logging
import os
import time

import numpy as np
from tqdm import tqdm

from bsm2_python.bsm2.init import thickenerinit_bsm2 as thickenerinit
from bsm2_python.bsm2.thickener_bsm2 import Thickener

path_name = os.path.dirname(__file__)


def test_thickener():
    # definition of the tested thickener:
    thickener = Thickener(thickenerinit.THICKENERPAR)

    # CONSTINFLUENT from BSM2:
    y_in = np.array(
        [
            30,
            69.5000000000000,
            51.2000000000000,
            202.320000000000,
            28.1700000000000,
            0,
            0,
            0,
            0,
            31.5600000000000,
            6.95000000000000,
            10.5900000000000,
            7,
            211.267500000000,
            18446,
            15,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    timestep = 15 / (60 * 24)
    endtime = 200
    simtime = np.arange(0, endtime, timestep)

    yt_uf = np.zeros(21)
    yt_of = np.zeros(21)

    start = time.perf_counter()

    for _ in simtime:
        yt_uf, yt_of = thickener.output(y_in)

    stop = time.perf_counter()
    logging.info('Steady state simulation completed after: %s seconds', stop - start)
    logging.info('Underflow at t = %s d: \n%s', endtime, yt_uf)
    logging.info('Overflow at t = %s d: \n%s', endtime, yt_of)

    yt_uf_matlab = np.array(
        [
            30,
            69.5000000000000,
            16964.2751488042,
            67035.3935176968,
            9333.66466683233,
            0,
            0,
            0,
            0,
            31.5600000000000,
            6.95000000000000,
            3508.82175441088,
            7,
            70000,
            54.5585642700000,
            15,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    yt_of_matlab = np.array(
        [
            30,
            69.5000000000000,
            1.02703771566833,
            4.05840372332064,
            0.565071336921423,
            0,
            0,
            0,
            0,
            31.5600000000000,
            6.95000000000000,
            0.212428308768118,
            7,
            4.23788458193279,
            18391.4414357300,
            15,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    logging.info('Underflow difference to MatLab solution: \n%s', str(yt_uf_matlab - yt_uf))
    logging.info('Overflow difference to MatLab solution: \n%s', str(yt_of_matlab - yt_of))

    assert np.allclose(yt_uf, yt_uf_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(yt_of, yt_of_matlab, rtol=1e-5, atol=1e-5)


test_thickener()


def test_thickener_dyn():
    # definition of the tested thickener:
    thickener = Thickener(thickenerinit.THICKENERPAR)

    # dyninfluent from BSM2:
    with open(path_name + '/../src/bsm2_python/data/dyninfluent_bsm2.csv', encoding='utf-8-sig') as f:
        data_in = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)

    timestep = 15 / 24 / 60  # 15 minutes in days
    endtime = 50  # data_in[-1, 0]
    data_time = data_in[:, 0]
    simtime = np.arange(0, endtime, timestep)
    y_in = data_in[:, 1:]
    del data_in

    yt_uf = np.zeros(21)
    yt_of = np.zeros(21)
    yt_uf_all = np.zeros((len(simtime), 21))
    yt_of_all = np.zeros((len(simtime), 21))

    start = time.perf_counter()

    for i, step in enumerate(tqdm(simtime)):
        # get influent data that is smaller than and closest to current time step
        y_in_timestep = y_in[np.where(data_time <= step)[0][-1], :]
        yt_uf, yt_of = thickener.output(y_in_timestep)
        yt_uf_all[i] = yt_uf
        yt_of_all[i] = yt_of

    stop = time.perf_counter()

    # np.savetxt(path_name + '/../data/test_yt_uf_all.csv', yt_uf_all, delimiter=',')
    # np.savetxt(path_name + '/../data/test_yt_of.csv', yt_of_all, delimiter=',')

    logging.info('Dynamic simulation completed after: %s seconds', stop - start)
    logging.info('Underflow at t = %s d: \n%s', endtime, yt_uf)
    logging.info('Overflow at t = %s d: \n%s', endtime, yt_of)

    # Values from 50 days dynamic simulation in Matlab (thickener_test_dyn.slx):
    yt_uf_matlab = np.array(
        [
            33.5386583268000,
            42.6657147645379,
            17414.5752792800,
            66588.4229560290,
            9330.33509802443,
            0,
            0,
            0,
            0,
            13.0991673987171,
            4.42838614018597,
            2090.36587406921,
            7,
            70000,
            112.753356887515,
            11.4404477663154,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    yt_of_matlab = np.array(
        [
            33.5386583268000,
            42.6657147645379,
            1.91517190169622,
            7.32307705347169,
            1.02610573766949,
            0,
            0,
            0,
            0,
            13.0991673987171,
            4.42838614018597,
            0.229888465384815,
            7,
            7.69826601962806,
            20923.7020017664,
            11.4404477663154,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    logging.info('Underflow difference to MatLab solution: \n%s', str(yt_uf_matlab - yt_uf))
    logging.info('Overflow difference to MatLab solution: \n%s', str(yt_of_matlab - yt_of))

    assert np.allclose(yt_uf, yt_uf_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(yt_of, yt_of_matlab, rtol=1e-5, atol=1e-5)


test_thickener_dyn()
