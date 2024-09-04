"""
This implements a simple storage tank of variable volume with complete mix. No biological reactions.
Dummy states are included. `tempmodel` defines how temperature changes in the input affect the liquid temperature.
It also defines rules for a potential necessary bypass of the storage tank.
`activate` used to activate dummy states.
See documentation by Dr Marie-Noelle Pons.

If liquid volume > 90% of total volume then automatically bypass flow.
If liquid volume < 10% of total volume then automatically input flow.
Storage output and automatic bypass streams are joined in a Combiner afterwards.

Copyright (2006):
 Ulf Jeppsson
 Dept. Industrial Electrical Engineering and Automation (IEA), Lund University, Sweden
 https://www.lth.se/iea/

Copyright (2024):
 Jonas Miederer
 Chair of Energy Process Engineering (EVT), FAU Erlangen-Nuremberg, Germany
 https://www.evt.tf.fau.de/
"""

import numpy as np
from numba import jit
from scipy.integrate import odeint

from bsm2_python.bsm2.helpers_bsm2 import Combiner
from bsm2_python.bsm2.module import Module

indices_components = np.arange(22)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5, VOL = (
    indices_components
)


@jit(nopython=True, cache=True)
def storageequations(t, yst, yst_in1, tempmodel, activate):
    """
    Returns an array containing the differential equations for the storage tank.

    Parameters
    ----------
    t : np.ndarray
        Time interval for integration, needed for the solver
    yst : np.ndarray
        Solution of the differential equations, needed for the solver
    yst_in1 : np.ndarray
        Storage tank influent concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
    tempmodel : bool
        If true, mass balance for the wastewater temperature is used in process rates,
        otherwise influent wastewater temperature is just passed through process reactors
    activate : bool
        If true, dummy states are activated, otherwise dummy states are not activated
    """
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


class Storage(Module):
    def __init__(self, volume, yst0, tempmodel, activate):
        """
        Parameters
        ----------
        volume : float
            volume of the primary clarifier
        yst0 : np.ndarray
            Initial integration values of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        tempmodel : bool
            If true, mass balance for the wastewater temperature is used in process rates,
            otherwise influent wastewater temperature is just passed through process reactors
        activate : bool
            If true, dummy states are activated, otherwise dummy states are not activated
        """
        self.curr_vol = yst0[VOL]
        self.max_vol = volume
        self.tempmodel = tempmodel
        self.activate = activate
        self.yst0 = yst0
        self.bypasscombiner = Combiner()

    def output(self, timestep, step, yst_in, qstorage):
        """
        Returns the solved differential equations for the storage tank.

        Parameters
        ----------
        timestep : int or float
            Size of integration interval in days
        step : int or float
            Upper boundary for integration interval in days
        yst_in : np.ndarray
            Storage tank influent concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        qstorage : float
            Storage tank influent flow rate

        Returns
        -------
        yst_out1 : np.ndarray
            Storage tank effluent concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        curr_vol : float
            Current volume of the storage tank
        """
        yst_in1 = np.zeros(22)
        yst_bp = np.zeros(21)  # bypass

        yst_in1[:21] = yst_in[:]
        yst_bp[:] = yst_in[:]

        if (self.curr_vol <= (0.9 * self.max_vol)) & (self.curr_vol >= (0.1 * self.max_vol)):
            yst_in1[14] = yst_in[14]
            # qstorage = qstorage
            yst_bp[14] = 0

        if (self.curr_vol >= (0.9 * self.max_vol)) & (yst_in[14] > qstorage):
            yst_in1[14] = 0
            qstorage = 0
            yst_bp[14] = yst_in[14]

        if (self.curr_vol >= (0.9 * self.max_vol)) & (yst_in[14] <= qstorage):
            yst_in1[14] = yst_in[14]
            # qstorage = qstorage
            yst_bp[14] = 0

        if self.curr_vol <= (0.1 * self.max_vol):
            yst_in1[14] = yst_in[14]
            qstorage = 0
            yst_bp[14] = 0

        yst_in1[21] = qstorage

        t_eval = np.array([step, step + timestep])  # time interval for odeint

        ode = odeint(storageequations, self.yst0, t_eval, tfirst=True, args=(yst_in1, self.tempmodel, self.activate))

        yst_int = ode[1]
        # y = yst_out
        # u = yst_in1
        # x : yst_int
        self.yst0 = yst_int

        yst_out = np.zeros(21)
        yst_out[:] = yst_int[:21]
        yst_out[14] = qstorage

        if not self.tempmodel:
            yst_out[15] = yst_in1[15]

        if not self.activate:
            yst_out[16:21] = 0

        self.curr_vol = yst_int[21]  # update current volume

        yst_out1 = self.bypasscombiner.output(yst_out, yst_bp)

        return yst_out1, self.curr_vol
