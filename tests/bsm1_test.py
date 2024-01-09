"""Execution file for BSM1 model (5 ASM1 reactors in series + settler) test case
"""
import csv
import sys
import os
import numpy as np
import time
from tqdm import tqdm
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')
from bsm2.settler1d_bsm2 import Settler
import bsm2.settler1dinit_bsm2 as settler1dinit
from asm1.asm1 import ASM1reactor
import asm1.asm1init as asm1init
from bsm2.helpers_bsm2 import Combiner, Splitter

tempmodel = False   # if False influent wastewater temperature is just passed through process reactors and settler
                    # if True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if False dummy states are 0
                    # if True dummy states are activated

# definition of the reactors:
combiner = Combiner()
reactor1 = ASM1reactor(asm1init.KLa1, asm1init.VOL1, asm1init.yinit1, asm1init.PAR1,
                       asm1init.carb1, asm1init.carbonsourceconc, tempmodel, activate)
reactor2 = ASM1reactor(asm1init.KLa2, asm1init.VOL2, asm1init.yinit2, asm1init.PAR2,
                       asm1init.carb2, asm1init.carbonsourceconc, tempmodel, activate)
reactor3 = ASM1reactor(asm1init.KLa3, asm1init.VOL3, asm1init.yinit3, asm1init.PAR3,
                       asm1init.carb3, asm1init.carbonsourceconc, tempmodel, activate)
reactor4 = ASM1reactor(asm1init.KLa4, asm1init.VOL4, asm1init.yinit4, asm1init.PAR4,
                       asm1init.carb4, asm1init.carbonsourceconc, tempmodel, activate)
reactor5 = ASM1reactor(asm1init.KLa5, asm1init.VOL5, asm1init.yinit5, asm1init.PAR5,
                       asm1init.carb5, asm1init.carbonsourceconc, tempmodel, activate)
reactor5 = ASM1reactor(asm1init.KLa5, asm1init.VOL5, asm1init.yinit5, asm1init.PAR5,
                       asm1init.carb5, asm1init.carbonsourceconc, tempmodel, activate)
splitter = Splitter()
settler = Settler(settler1dinit.DIM, settler1dinit.LAYER, asm1init.Qr, asm1init.Qw, settler1dinit.settlerinit,
                  settler1dinit.SETTLERPAR, asm1init.PAR1, tempmodel, settler1dinit.MODELTYPE)


def test_bsm1():
    # CONSTINFLUENT from BSM2:
    y_in = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])

    timestep = 15/(60*24)
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
    Qintr = asm1init.Qintr
    sludge_height = 0

    start = time.perf_counter()

    for step in simtime:
        y_in1 = combiner.output(y_in, ys_out, y_out5_r)

        y_out1 = reactor1.output(timestep, step, y_in1)
        y_out2 = reactor2.output(timestep, step, y_out1)
        y_out3 = reactor3.output(timestep, step, y_out2)
        y_out4 = reactor4.output(timestep, step, y_out3)
        y_out5 = reactor5.output(timestep, step, y_out4)

        ys_in, y_out5_r = splitter.outputs(y_out5, (y_out5[14] - Qintr, Qintr))

        ys_out, _, ys_eff, sludge_height = settler.outputs(timestep, step, ys_in)

    stop = time.perf_counter()

    print('Steady state simulation completed after: ', stop - start, 'seconds')
    print('Effluent at t =', endtime, 'd:  \n', ys_eff)
    print('Sludge height at t =', endtime, 'd:  \n', sludge_height)

    ys_eff_matlab = np.array([30.0000000000000, 0.889492799653682, 4.39182747787874, 0.188440413683379, 9.78152406404732, 0.572507856962265, 1.72830016782928, 0.490943515687561, 10.4152201204309, 1.73333146817512, 0.688280004678034, 0.0134804685779854, 4.12557938198182, 12.4969499853007, 18061, 15, 0, 0, 0, 0, 0])
    sludge_height_matlab = 0.447178539974702
    print('Effluent difference to MatLab solution: \n', ys_eff_matlab - ys_eff)
    print('Sludge height difference to MatLab solution: \n', sludge_height_matlab - sludge_height)

    assert np.allclose(ys_eff, ys_eff_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(sludge_height, sludge_height_matlab, rtol=1e-5, atol=1e-5)


test_bsm1()


def test_bsm1_ol():
    # dyninfluent from BSM2:
    with open(path_name + '/../data/dyninfluent_bsm2.csv', 'r') as f:
        data_in = np.array(list(csv.reader(f, delimiter=","))).astype(np.float64)

    timestep = 15/24/60  # 15 minutes in days
    endtime = 50  # only 50 days for testing
    data_time = data_in[:, 0]
    simtime = np.arange(0, endtime, timestep)
    y_in = data_in[:, 1:]
    del data_in

    y_out5_r = np.zeros(21)
    ys_in = np.zeros(21)
    ys_out = np.zeros(21)
    ys_eff = np.zeros(21)
    Qintr = asm1init.Qintr
    sludge_height = 0

    ys_eff_all = np.zeros((len(simtime), 21))
    sludge_height_all = np.zeros((len(simtime), 1))

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

        ys_in, y_out5_r = splitter.outputs(y_out5, (y_out5[14] - Qintr, Qintr))

        ys_out, _, ys_eff, sludge_height = settler.outputs(timestep, step, ys_in)

        ys_eff_all[i] = ys_eff
        sludge_height_all[i] = sludge_height

    stop = time.perf_counter()

    # np.savetxt(path_name + '/../data/test_ys_eff_all.csv', ys_eff_all, delimiter=',')
    # np.savetxt(path_name + '/../data/test_sludge_height_all.csv', sludge_height_all, delimiter=',')

    print('Dynamic open loop simulation completed after: ', stop - start, 'seconds')
    print('Effluent at t =', endtime, 'd:  \n', ys_eff)
    print('Sludge height at t =', endtime, 'd:  \n', sludge_height)

    # Values from 50 days dynamic simulation in Matlab (bsm1_test_ol.slx):
    ys_eff_matlab = np.array([29.9041779036345, 2.86336250854119, 10.4985364014802, 1.77550626455255, 24.7216745020295, 0.0113748400676772, 2.29517384745407, 0.244476849395549, 0.00553950757372690, 26.6011848861327, 0.994115660400043, 0.106244650636689, 7.41009979441910, 29.4766993916880, 20650.7908684698, 11.4415311578628, 0, 0, 0, 0, 0])
    sludge_height_matlab = 2.83301562022632  # refers to settler[166] in MatLab

    print('Effluent difference to MatLab solution: \n', ys_eff_matlab - ys_eff)
    print('Sludge height difference to MatLab solution: \n', sludge_height_matlab - sludge_height)

    # high tolerances to speed up testing. If timestep is refined (e.g. up to 1 minute), smaller tolerances are achieved.
    assert np.allclose(ys_eff, ys_eff_matlab, rtol=1e-1, atol=7e-1)
    assert np.allclose(sludge_height, sludge_height_matlab, rtol=1e-1)


test_bsm1_ol()
