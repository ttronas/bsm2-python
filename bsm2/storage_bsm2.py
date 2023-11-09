import numpy as np
from scipy.integrate import odeint
from numba import jit
import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')
from bsm2.helpers_bsm2 import Combiner


indices_components = np.arange(22)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5, VOL = indices_components


@jit(nopython=True, cache=True)
def storageequations(t, yst, yst_in1, tempmodel, activate):
    # u = yst_in1
    # x = yst
    # dx = dyst
    dyst = np.zeros(22)

    dyst[:14] = yst_in1[Q] / yst[VOL] * (yst_in1[:14] - yst[:14])
    dyst[Q] = 0

    if not tempmodel:
        dyst[TEMP] = 0.0
    else:
        dyst[TEMP] = yst_in1[Q] / yst[VOL] * (yst_in1[TEMP] - yst[TEMP])

    if activate:
        dyst[16:21] = yst_in1[Q] / yst[VOL] * (yst_in1[16:21] - yst[16:21])

    dyst[VOL] = yst_in1[Q] - yst_in1[VOL]  # change in volume

    return dyst


class Storage:
    def __init__(self, volume, yst0, tempmodel, activate):
        self.curr_vol = 0
        self.max_vol = volume
        self.tempmodel = tempmodel
        self.activate = activate
        self.yst0 = yst0
        self.bypasscombiner = Combiner()

    def output(self, timestep, step, yst_in, Qstorage):

        yst_in1 = np.zeros(22)
        yst_bp = np.zeros(21)  # bypass

        yst_in1[:21] = yst_in[:]
        yst_bp[:] = yst_in[:]

        if (self.curr_vol <= (0.9*self.max_vol)) & (self.curr_vol >= (0.1*self.max_vol)):
            yst_in1[14] = yst_in[14]
            Qstorage = Qstorage
            yst_bp[14] = 0

        if (self.curr_vol >= (0.9*self.max_vol)) & (yst_in[14] > Qstorage):
            yst_in1[14] = 0
            Qstorage = 0
            yst_bp[14] = yst_in[14]

        if (self.curr_vol >= (0.9*self.max_vol)) & (yst_in[14] <= Qstorage):
            yst_in1[14] = yst_in[14]
            Qstorage = Qstorage
            yst_bp[14] = 0

        if self.curr_vol <= (0.1*self.max_vol):
            yst_in1[14] = yst_in[14]
            Qstorage = 0
            yst_bp[14] = 0

        yst_in1[21] = Qstorage

        t_eval = np.array([step, step+timestep])    # time interval for odeint

        ode = odeint(storageequations, self.yst0, t_eval, tfirst=True, args=(yst_in1, self.tempmodel, self.activate))

        yst_int = ode[1]
        # y = yst_out
        # u = yst_in1
        # x : yst_int
        self.yst0 = yst_int

        yst_out = np.zeros(21)
        yst_out[:] = yst_int[:21]
        yst_out[14] = Qstorage

        if not self.tempmodel:
            yst_out[15] = yst_in1[15]

        if not self.activate:
            yst_out[16:21] = 0

        self.curr_vol = yst_int[21]  # update current volume

        yst_out1 = self.bypasscombiner.output(yst_out, yst_bp)

        return yst_out1
