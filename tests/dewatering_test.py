"""
test dewatering_bsm2.py
"""

import csv
import logging
import os
import time

import numpy as np
from tqdm import tqdm

from bsm2_python.bsm2.dewatering_bsm2 import Dewatering
from bsm2_python.bsm2.init import dewateringinit_bsm2 as dewateringinit

path_name = os.path.dirname(__file__)


def test_dewatering():
    # definition of the tested dewatering:
    dewatering = Dewatering(dewateringinit.DEWATERINGPAR)

    # CONSTINFLUENT from BSM2:
    y_in = np.array(
        [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0]
    )

    timestep = 15 / (60 * 24)
    endtime = 200
    simtime = np.arange(0, endtime, timestep)

    ydw_s = np.zeros(21)
    ydw_r = np.zeros(21)

    start = time.perf_counter()

    for _ in simtime:
        ydw_s, ydw_r = dewatering.output(y_in)

    stop = time.perf_counter()

    logging.info('Steady state simulation completed after: %s seconds', stop - start)
    logging.info('Sludge flow at t = %s d: \n%s', endtime, ydw_s)
    logging.info('Reject flow at t = %s d: \n%s', endtime, ydw_r)

    ydw_s_matlab = np.array(
        [
            30,
            69.5000000000000,
            67857.1005952170,
            268141.574070787,
            37334.6586673293,
            0,
            0,
            0,
            0,
            31.5600000000000,
            6.95000000000000,
            14035.2870176435,
            7,
            280000,
            13.6396410675000,
            15,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    ydw_r_matlab = np.array(
        [
            30,
            69.5000000000000,
            1.02475774302266,
            4.04939426891298,
            0.563816906659147,
            0,
            0,
            0,
            0,
            31.5600000000000,
            6.95000000000000,
            0.211956728488476,
            7,
            4.22847668894609,
            18432.3603589325,
            15,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    logging.info('Sludge flow difference to MatLab solution: \n%s', ydw_s_matlab - ydw_s)
    logging.info('Reject flow difference to MatLab solution: \n%s', ydw_r_matlab - ydw_r)

    assert np.allclose(ydw_s, ydw_s_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(ydw_r, ydw_r_matlab, rtol=1e-5, atol=1e-5)


test_dewatering()


def test_dewatering_dyn():
    # definition of the tested dewatering:
    dewatering = Dewatering(dewateringinit.DEWATERINGPAR)
    # dyninfluent from BSM2:
    with open(path_name + '/../src/bsm2_python/data/dyninfluent_bsm2.csv', encoding='utf-8-sig') as f:
        data_in = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)

    timestep = 15 / 24 / 60  # 15 minutes in days
    endtime = 50  # data_in[-1, 0]
    data_time = data_in[:, 0]
    simtime = np.arange(0, endtime, timestep)
    y_in = data_in[:, 1:]
    del data_in

    ydw_s = np.zeros(21)
    ydw_r = np.zeros(21)
    ydw_s_all = np.zeros((len(simtime), 21))
    ydw_r_all = np.zeros((len(simtime), 21))

    start = time.perf_counter()

    for i, step in enumerate(tqdm(simtime)):
        # get influent data that is smaller than and closest to current time step
        y_in_timestep = y_in[np.where(data_time <= step)[0][-1], :]
        ydw_s, ydw_r = dewatering.output(y_in_timestep)
        ydw_s_all[i, :] = ydw_s
        ydw_r_all[i, :] = ydw_r

    stop = time.perf_counter()

    # np.savetxt(path_name + '/../data/test_ydw_s_all.csv', ydw_s_all, delimiter=',')
    # np.savetxt(path_name + '/../data/test_ydw_r_all.csv', ydw_r_all, delimiter=',')

    logging.info('Dynamic simulation completed after: %s seconds', stop - start)
    logging.info('Sludge flow at t = %s d: \n%s', endtime, ydw_s)
    logging.info('Reject flow at t = %s d: \n%s', endtime, ydw_r)

    # Values from 50 days dynamic simulation in Matlab (dewatering_test_dyn.slx):
    ydw_s_matlab = np.array(
        [
            33.5386583268000,
            42.6657147645379,
            69658.3011171199,
            266353.691824116,
            37321.3403920977,
            0,
            0,
            0,
            0,
            13.0991673987171,
            4.42838614018597,
            8361.46349627682,
            7,
            280000,
            28.1883392218788,
            11.4404477663154,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    ydw_r_matlab = np.array(
        [
            33.5386583268000,
            42.6657147645379,
            1.90746272008929,
            7.29359931788214,
            1.02197533273164,
            0,
            0,
            0,
            0,
            13.0991673987171,
            4.42838614018597,
            0.228963090525556,
            7,
            7.66727802802730,
            21008.2670194321,
            11.4404477663154,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    logging.info('Sludge flow difference to MatLab solution: \n%s', ydw_s_matlab - ydw_s)
    logging.info('Reject flow difference to MatLab solution: \n%s', ydw_r_matlab - ydw_r)

    assert np.allclose(ydw_s, ydw_s_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(ydw_r, ydw_r_matlab, rtol=1e-5, atol=1e-5)


test_dewatering_dyn()
