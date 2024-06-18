"""
test storage_bsm2.py
"""

import csv
import os
import time

import numpy as np
from tqdm import tqdm

import bsm2_python.bsm2.init.storageinit_bsm2 as storageinit
from bsm2_python.bsm2.storage_bsm2 import Storage
from bsm2_python.logger import log

path_name = os.path.dirname(__file__)

tempmodel = (
    False  # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
)
# if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False  # if activate is False dummy states are 0
# if activate is True dummy states are activated

Qstorage = 0  # storage flow rate regulation not used in this test


def test_storage():
    # definition of the tested storage:
    storage = Storage(storageinit.VOL_S, storageinit.ystinit, tempmodel, activate)

    # Constant influent based on digester input from BSM2:
    yst_in = np.array(
        [
            28.0665048629843,
            48.9525780251450,
            10361.7145189587,
            20375.0163964256,
            10210.0695779898,
            553.280744847661,
            3204.66026217631,
            0.252251384955929,
            1.68714307465010,
            28.9098125063162,
            4.68341082328394,
            906.093288634802,
            7.15490225533614,
            33528.5561252986,
            178.467454963180,
            14.8580800598190,
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

    yst_out = np.zeros(21)
    yst_vol = 0

    start = time.perf_counter()

    for step in simtime:
        yst_out, yst_vol = storage.output(timestep, step, yst_in, Qstorage)

    stop = time.perf_counter()

    log.info('Steady state simulation completed after: %s seconds', stop - start)
    log.info('Sludge at t = %s d: \n%s', endtime, yst_out)

    yst_out_matlab = np.array(
        [
            28.0665048629843,
            48.9525780251450,
            10361.7145189587,
            20375.0163964256,
            10210.0695779898,
            553.280744847661,
            3204.66026217631,
            0.252251384955929,
            1.68714307465010,
            28.9098125063162,
            4.68341082328394,
            906.093288634802,
            7.15490225533614,
            33528.5561252986,
            178.467454963180,
            14.8580800598190,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    yst_vol_matlab = 144.364056261084

    log.info('Sludge difference to MatLab solution: \n%s', yst_out_matlab - yst_out)
    log.info('Volume difference to MatLab solution: \n%s', yst_vol_matlab - yst_vol)

    assert np.allclose(yst_out, yst_out_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(
        yst_vol, yst_vol_matlab, rtol=1e-1, atol=1
    )  # tolerance is higher for volume because of the integration method.
    # If the step size is reduced the result gets more accurate!


test_storage()


def test_storage_dyn():
    # definition of the tested storage:
    storage = Storage(storageinit.VOL_S, storageinit.ystinit, tempmodel, activate)
    # dynsludge from BSM2 open loop (digesterinpreinterface):
    with open(path_name + '/../src/bsm2_python/data/dynsludge_bsm2.csv', encoding='utf-8-sig') as f:
        data_in = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)

    timestep = 15 / 24 / 60  # 15 minutes in days
    endtime = 50  # data_in[-1, 0]
    data_time = data_in[:, 0]
    simtime = np.arange(0, endtime, timestep)
    y_in = data_in[:, 1:]
    del data_in

    yst_out = np.zeros(21)
    yst_vol = 0
    yst_out_all = np.zeros((len(simtime), 21))
    yst_vol_all = np.zeros((len(simtime), 1))

    start = time.perf_counter()

    for i, step in enumerate(tqdm(simtime)):
        # get influent data that is smaller than and closest to current time step
        y_in_timestep = y_in[np.where(data_time <= step)[0][-1], :]
        yst_out, yst_vol = storage.output(timestep, step, y_in_timestep, Qstorage)
        yst_out_all[i] = yst_out
        yst_vol_all[i] = yst_vol

    stop = time.perf_counter()

    # np.savetxt(path_name + '/../data/test_yst_out_all.csv', yst_out_all, delimiter=',')
    # np.savetxt(path_name + '/../data/test_yst_vol_all.csv', yst_vol_all, delimiter=',')

    log.info('Dynamic simulation completed after: %s seconds', stop - start)
    log.info('Sludge at t = %s d: \n%s', endtime, yst_out)
    log.info('Volume at t = %s d: \n%s', endtime, yst_vol)

    # Values from 50 days dynamic simulation in Matlab (storage_test_dyn.slx)
    yst_out_matlab = np.array(
        [
            33.2152509553435,
            41.8798580642530,
            10544.6314538123,
            20874.3609507103,
            15318.3975401057,
            380.110859861603,
            1449.37232064426,
            0.189234381018648,
            0.778303638555896,
            26.5243175258826,
            4.21913273099171,
            849.450689053129,
            7.57679382207250,
            36425.1548438506,
            190.028282672942,
            11.4654536074904,
            4.97422833876973e-34,
            0,
            0,
            0,
            0,
        ]
    )
    yst_vol_matlab = 144.496536811897

    log.info('Sludge difference to MatLab solution: \n%s', yst_out_matlab - yst_out)
    log.info('Volume difference to MatLab solution: \n%s', yst_vol_matlab - yst_vol)

    assert np.allclose(yst_out, yst_out_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(
        yst_vol, yst_vol_matlab, rtol=2e-2
    )  # tolerance is higher for volume because of the integration method.
    # If the step size is reduced the result gets more accurate!


test_storage_dyn()
