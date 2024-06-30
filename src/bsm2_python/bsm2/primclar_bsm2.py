"""
 The implementation is to a large extent based on an implementation of the
 Otterpohl/Freund model by Dr Jens Alex, IFAK, Magdeburg.
 In addition to ASM1 states, the clarifier will also pass on `TSS`, `Q`, `TEMP` and 5 dummy
 states to effluent and underflow.
 If `tempmodel` == True, T(out) is a first-order equation based on the
 heat content of the influent, the reactor and outflow.

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

from bsm2_python.bsm2.module import Module

indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components


@jit(nopython=True)
def primclarequations(t, yp, yp_in, p_par, volume, tempmodel):
    """
    Returns an array containing the differential equations for the primary clarifier.

    Parameters
    ----------
    t : np.ndarray
        Time interval for integration, needed for the solver
    yp : np.ndarray
        Solution of the differential equations, needed for the solver
    yp_in : np.ndarray
        Primary clarifier influent concentrations of the 21 components
        (13 ASM1 components, TSS, Q, T and 5 dummy states)
    p_par : np.ndarray
        primary clarifier parameters
    volume : float
        volume of the primary clarifier
    tempmodel : bool
        If true, mass balance for the wastewater temperature is used in process rates,
        otherwise influent wastewater temperature is just passed through process reactors
    """
    # u = yp_in
    # x = yp
    # dx = dyp
    dyp = np.zeros(21)

    dyp[0:13] = 1.0 / volume * (yp_in[Q] * (yp_in[0:13] - yp[0:13]))  # ASM1 states are mixing
    dyp[TSS] = 0.0
    dyp[Q] = (yp_in[Q] - yp[Q]) / p_par[2]

    if not tempmodel:
        dyp[TEMP] = 0.0
    else:
        dyp[TEMP] = 1.0 / volume * (yp_in[Q] * (yp_in[TEMP] - yp[TEMP]))

    dyp[16:21] = 1.0 / volume * (yp_in[Q] * (yp_in[16:21] - yp[16:21]))  # dummy states are mixing

    return dyp


class PrimaryClarifier(Module):
    def __init__(self, volume, yp0, p_par, asm1par, x_vector, tempmodel, activate):
        """
        This is an implementation of the Otterpohl/Freund primary clarifier model.
        The implementation is to a large extent based on an implementation of the
        Otterpohl/Freund model by Dr. Jens Alex, IFAK, Magdeburg.

        Parameters
        ----------
        volume : float
            volume of the primary clarifier
        yp0 : np.ndarray
            Initial integration values of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        p_par : np.ndarray
            [f_corr, f_X, t_m, f_PS]
            f_corr: efficiency correction for primary clarifier
            f_X: CODpart/CODtot ratio
            t_m: smoothing time constant for qm calculation
            f_PS: ratio of primary sludge flow rate to the influent flow
        asm1par : np.ndarray
            ASM1 parameters
        x_vector : np.ndarray
            primary clarifier state vector
        tempmodel : bool
            If true, first-order equation based on the heat content of the influent, the reactor and outflow is solved,
            otherwise influent wastewater temperature is just passed through process reactors
        activate : bool
            If true, dummy states are activated, otherwise dummy states are not activated
        """
        self.volume = volume
        self.yp0 = yp0
        self.p_par = p_par
        self.asm1par = asm1par
        self.x_vector = x_vector
        self.tempmodel = tempmodel
        self.activate = activate

    def output(self, timestep, step, yp_in):
        """
        Returns the overflow and underflow concentrations from a
        primary clarifier at the current time step.

        Parameters
        ----------
        timestep : float
            current time step
        step : float
            current time
        yp_in : np.ndarray
            primary clarifier influent concentrations of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states)

        Returns
        -------
        yp_uf : np.ndarray
            primary clarifier underflow (sludge) concentrations of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states)
        yp_of : np.ndarray
            primary clarifier overflow (effluent) concentrations of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states)
        yp_internal : np.ndarray
            primary clarifier internal (basically influent) concentrations of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states)
            Only for evaluation purposes
        """
        # f_corr, f_X, t_m, f_PS = p_par
        # y = yp_uf, yp_of
        # u = yp_int
        # x : yp_in

        yp_uf = np.zeros(21)
        yp_of = np.zeros(21)
        yp_internal = np.zeros(21)

        if not self.tempmodel:
            self.yp0[15] = yp_in[15]

        t_eval = np.array([step, step + timestep])  # time interval for odeint

        ode = odeint(
            primclarequations, self.yp0, t_eval, tfirst=True, args=(yp_in, self.p_par, self.volume, self.tempmodel)
        )

        yp_int = ode[1]

        self.yp0 = yp_int

        qu = self.p_par[3] * yp_in[Q]  # underflow from primary clarifier
        e = yp_in[Q] / qu  # thickening factor
        tt = self.volume / (yp_int[Q] + 0.001)  # hydraulic retention time

        # Total COD removal efficiency in primary clarifier nCOD
        ncod = self.p_par[0] * (2.88 * self.p_par[1] - 0.118) * (1.45 + 6.15 * np.log(tt * 24 * 60))
        # nX is removal efficiency of particulate COD in %, since assumption that soluble COD is not removed
        nx = ncod / self.p_par[1]
        nx = max(0, min(100, nx))  # nX is between 0 and 100

        ff = 1 - self.x_vector * nx / 100

        # ASM1 state outputs effluent
        yp_of[0:13] = ff[0:13] * yp_int[0:13]
        yp_of[yp_of < 0.0] = 0.0
        # dummy state outputs effluent
        yp_of[16:21] = ff[16:21] * yp_int[16:21]
        yp_of[yp_of < 0.0] = 0.0

        # TSS output effluent
        yp_of[TSS] = (
            self.asm1par[19] * yp_of[XI]
            + self.asm1par[20] * yp_of[XS]
            + self.asm1par[21] * yp_of[XBH]
            + self.asm1par[22] * yp_of[XBA]
            + self.asm1par[23] * yp_of[XP]
        )

        # ASM1 state outputs underflow
        yp_uf[0:13] = ((1 - ff[0:13]) * e + ff[0:13]) * yp_int[0:13]
        yp_uf[yp_uf < 0.0] = 0.0
        # dummy state outputs underflow
        yp_uf[16:21] = ((1 - ff[16:21]) * e + ff[16:21]) * yp_int[16:21]
        yp_uf[yp_uf < 0.0] = 0.0

        # TSS output underflow
        yp_uf[TSS] = (
            self.asm1par[19] * yp_uf[XI]
            + self.asm1par[20] * yp_uf[XS]
            + self.asm1par[21] * yp_uf[XBH]
            + self.asm1par[22] * yp_uf[XBA]
            + self.asm1par[23] * yp_uf[XP]
        )

        # only for plant performance!
        # ASM1 state outputs internal
        yp_internal[0:13] = yp_int[0:13]

        # dummy state outputs internal
        yp_internal[16:21] = yp_int[16:21]
        yp_internal[yp_internal < 0.0] = 0.0

        # TSS output internal
        yp_internal[TSS] = (
            self.asm1par[19] * yp_in[XI]
            + self.asm1par[20] * yp_in[XS]
            + self.asm1par[21] * yp_in[XBH]
            + self.asm1par[22] * yp_in[XBA]
            + self.asm1par[23] * yp_in[XP]
        )

        # Flow rates
        yp_of[Q] = yp_in[Q] - qu  # flow rate in effluent
        yp_uf[Q] = qu  # flow rate in underflow
        yp_internal[Q] = yp_in[Q]

        if not self.tempmodel:
            yp_of[TEMP] = yp_in[TEMP]
            yp_uf[TEMP] = yp_in[TEMP]
            yp_internal[TEMP] = yp_in[TEMP]
        else:
            yp_of[TEMP] = yp_int[TEMP]
            yp_uf[TEMP] = yp_int[TEMP]
            yp_internal[TEMP] = yp_int[TEMP]

        return yp_uf, yp_of, yp_internal
