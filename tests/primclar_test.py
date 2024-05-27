"""
test primclar_bsm2.py
"""

import csv
import logging
import os
import time

import numpy as np
from tqdm import tqdm

from bsm2_python.bsm2 import asm1init_bsm2 as asm1init
from bsm2_python.bsm2 import primclarinit_bsm2 as primclarinit
from bsm2_python.bsm2.primclar_bsm2 import PrimaryClarifier

path_name = os.path.dirname(__file__)

tempmodel = (
    False  # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
)
# if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False  # if activate is False dummy states are 0
# if activate is True dummy states are activated


def test_primclar():
    # definition of the tested clarifier:
    primclar = PrimaryClarifier(
        primclarinit.VOL_P,
        primclarinit.YINIT1,
        primclarinit.PAR_P,
        asm1init.PAR1,
        primclarinit.XVECTOR_P,
        tempmodel,
        activate,
    )

    # CONSTINFLUENT from BSM2:
    y_in = np.array(
        [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0]
    )

    timestep = 15 / (60 * 24)
    endtime = 200
    simtime = np.arange(0, endtime, timestep)

    yp_uf = np.zeros(21)
    yp_of = np.zeros(21)

    start = time.perf_counter()

    for step in simtime:
        yp_uf, yp_of = primclar.outputs(timestep, step, y_in)

    stop = time.perf_counter()

    logging.info('Steady state simulation completed after: %s seconds', stop - start)
    logging.info('Effluent at t = 200 d: \n%s', yp_of)
    logging.info('Sludge at t = 200 d: \n%s', yp_uf)

    yp_of_matlab = np.array(
        [
            30,
            69.5000000000000,
            26.0206415019475,
            102.822191185039,
            14.3164349826144,
            0,
            0,
            0,
            0,
            31.5600000000000,
            6.95000000000000,
            5.38200377940671,
            7,
            107.369450752201,
            18316.8780000000,
            15,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    yp_uf_matlab = np.array(
        [
            30,
            69.5000000000000,
            3623.07185550945,
            14316.7948790366,
            1993.39715175198,
            0,
            0,
            0,
            0,
            31.5600000000000,
            6.95000000000000,
            749.381463864162,
            7,
            14949.9479147235,
            129.122000000000,
            15,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    logging.info('Effluent difference to MatLab solution: \n%s', yp_of_matlab - yp_of)
    logging.info('Sludge difference to MatLab solution: \n%s', yp_uf_matlab - yp_uf)

    assert np.allclose(yp_of, yp_of_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(yp_uf, yp_uf_matlab, rtol=1e-5, atol=1e-5)


test_primclar()


def test_primclar_dyn():
    # definition of the tested clarifier:
    primclar = PrimaryClarifier(
        primclarinit.VOL_P,
        primclarinit.YINIT1,
        primclarinit.PAR_P,
        asm1init.PAR1,
        primclarinit.XVECTOR_P,
        tempmodel,
        activate,
    )
    # dyninfluent from BSM2:
    with open(path_name + '/../src/bsm2_python/data/dyninfluent_bsm2.csv', encoding='utf-8-sig') as f:
        data_in = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)

    timestep = 15 / 24 / 60  # 15 minutes in days
    endtime = 50  # data_in[-1, 0]
    data_time = data_in[:, 0]
    simtime = np.arange(0, endtime, timestep)
    y_in = data_in[:, 1:]
    del data_in

    yp_uf = np.zeros(21)
    yp_of = np.zeros(21)
    yp_uf_all = np.zeros((len(simtime), 21))
    yp_of_all = np.zeros((len(simtime), 21))

    start = time.perf_counter()

    for i, step in enumerate(tqdm(simtime)):
        # get influent data that is smaller than and closest to current time step
        y_in_timestep = y_in[np.where(data_time <= step)[0][-1], :]
        yp_uf, yp_of = primclar.outputs(timestep, step, y_in_timestep)
        yp_uf_all[i] = yp_uf
        yp_of_all[i] = yp_of

    stop = time.perf_counter()

    # np.savetxt(path_name + '/../data/test_yp_uf.csv', yp_uf_all, delimiter=',')
    # np.savetxt(path_name + '/../data/test_yp_of.csv', yp_of_all, delimiter=',')

    logging.info('Dynamic simulation completed after: %s seconds', stop - start)
    logging.info('Effluent at t = %s d: \n%s', endtime, yp_of)
    logging.info('Sludge at t = %s d: \n%s', endtime, yp_uf)

    # Values from 50 days dynamic simulation in Matlab (primclar_test_dyn.slx):
    yp_uf_matlab = np.array(
        [
            33.4154125970948,
            49.8211097011199,
            6860.88076663431,
            26407.1948377440,
            3856.64505042994,
            1.99000000000000e-321,
            1.99000000000000e-321,
            3.00000000000000e-323,
            3.00000000000000e-323,
            14.7088952119447,
            5.13430535495627,
            1041.33852549727,
            7.00000000000000,
            27843.5404911062,
            147.255187510577,
            11.4404477663154,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    yp_of_matlab = np.array(
        [
            33.4154125970948,
            49.8211097011199,
            54.5638774436205,
            210.013698206756,
            30.6715005015946,
            1.50000000000000e-323,
            1.50000000000000e-323,
            3.00000000000000e-323,
            3.00000000000000e-323,
            14.7088952119447,
            5.13430535495627,
            8.28165794089829,
            7.00000000000000,
            221.436807113978,
            20889.2001711433,
            11.4404477663154,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    logging.info('Effluent difference to MatLab solution: \n%s', yp_of_matlab - yp_of)
    logging.info('Sludge difference to MatLab solution: \n%s', yp_uf_matlab - yp_uf)

    assert np.allclose(yp_of, yp_of_matlab, rtol=1e-2)
    assert np.allclose(yp_uf, yp_uf_matlab, rtol=1e-2)


test_primclar_dyn()
