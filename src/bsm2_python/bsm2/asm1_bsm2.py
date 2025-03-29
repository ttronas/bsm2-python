# Copyright ASM1 and Carboncombiner (2006)
# Ulf Jeppsson
# Dept. Industrial Electrical Engineering and Automation (IEA), Lund University, Sweden
# https://www.lth.se/iea/

# Copyright (2024)
# Maike Böhm, Jonas Miederer
# Chair of Energy Process Engineering (EVT), FAU Erlangen-Nuremberg, Germany
# https://www.evt.tf.fau.de/

import numpy as np
from numba import jit
from scipy.integrate import odeint

from bsm2_python.bsm2.module import Module

indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components


@jit(nopython=True, cache=True)
def asm1equations(t, y, y_in, asm1par, kla, volume, tempmodel, activate):
    """Returns an array containing the differential equations based on ASM1.

    Parameters
    ----------
    t : np.ndarray(2)
        Time interval for integration, needed for the solver. \n
        [step, step + timestep]
    y : np.ndarray(21)
        Solution of the differential equations from the previous step, needed for the solver. \n
        [S_I, S_S, X_I, X_S, X_BH, X_BA, X_P, S_O, S_NO, S_NH, S_ND, X_ND,
        S_ALK, TSS, Q, T, S_D1, S_D2, S_D3, X_D4, X_D5]
    y_in : np.ndarray(21)
        Influent concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        before the activated sludge reactor. \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
        SD1, SD2, SD3, XD4, XD5]
    asm1par : np.ndarray(24)
        Parameters needed for the ASM1 equations. \n
        [MU_H, K_S, K_OH, K_NO, B_H, MU_A, K_NH, K_OA, B_A, NY_G, K_A, K_H, K_X, NY_H,
        Y_H, Y_A, F_P, I_XB, I_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS]
    kla : float
        Oxygen transfer coefficient in aerated reactors [d⁻¹].
    volume : float
        Volume of the reactor [m³].
    tempmodel : bool
        If true, mass balance for the wastewater temperature is used in process rates,
        otherwise influent wastewater temperature is just passed through process reactors.
    activate : bool
        If true, dummy states are activated, otherwise dummy states are not activated.

    Returns
    -------
    dy : np.ndarray(21)
        Array containing the 21 differential values of `y_in` based on ASM1. \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
        SD1, SD2, SD3, XD4, XD5]
    """

    dy = np.zeros(21)
    reac = np.zeros(21)

    (
        mu_h,
        k_s,
        k_oh,
        k_no,
        b_h,
        mu_a,
        k_nh,
        k_oa,
        b_a,
        ny_g,
        k_a,
        k_h,
        k_x,
        ny_h,
        y_h,
        y_a,
        f_p,
        i_xb,
        i_xp,
        _,
        _,
        _,
        _,
        _,
    ) = asm1par

    # temperature compensation:
    # temperature at the influent of the reactor
    if not tempmodel:
        mu_h *= np.exp((np.log(mu_h / 3.0) / 5.0) * (y_in[TEMP] - 15.0))
        b_h *= np.exp((np.log(b_h / 0.2) / 5.0) * (y_in[TEMP] - 15.0))
        mu_a *= np.exp((np.log(mu_a / 0.3) / 5.0) * (y_in[TEMP] - 15.0))
        b_a *= np.exp((np.log(b_a / 0.03) / 5.0) * (y_in[TEMP] - 15.0))
        k_h *= np.exp((np.log(k_h / 2.5) / 5.0) * (y_in[TEMP] - 15.0))
        k_a *= np.exp((np.log(k_a / 0.04) / 5.0) * (y_in[TEMP] - 15.0))
        so_sat_temp = (
            0.9997743214
            * 8.0
            / 10.5
            * (
                56.12
                * 6791.5
                * np.exp(
                    -66.7354
                    + 87.4755 / ((y_in[TEMP] + 273.15) / 100.0)
                    + 24.4526 * np.log((y_in[TEMP] + 273.15) / 100.0)
                )
            )
        )  # van't Hoff equation
        kla_temp = kla * np.power(1.024, (y_in[TEMP] - 15.0))

    else:
        mu_h *= np.exp((np.log(mu_h / 3.0) / 5.0) * (y[TEMP] - 15.0))  # current temperature in the reactor
        b_h *= np.exp((np.log(b_h / 0.2) / 5.0) * (y[TEMP] - 15.0))
        mu_a *= np.exp((np.log(mu_a / 0.3) / 5.0) * (y[TEMP] - 15.0))
        b_a *= np.exp((np.log(b_a / 0.03) / 5.0) * (y[TEMP] - 15.0))
        k_h *= np.exp((np.log(k_h / 2.5) / 5.0) * (y[TEMP] - 15.0))
        k_a *= np.exp((np.log(k_a / 0.04) / 5.0) * (y[TEMP] - 15.0))
        so_sat_temp = (
            0.9997743214
            * 8.0
            / 10.5
            * (
                56.12
                * 6791.5
                * np.exp(-66.7354 + 87.4755 / ((y[TEMP] + 273.15) / 100.0) + 24.4526 * np.log((y[15] + 273.15) / 100.0))
            )
        )  # van't Hoff equation
        kla_temp = kla * np.power(1.024, (y[TEMP] - 15.0))

    # concentrations should not be negative:
    ytemp = y
    ytemp[ytemp < 0.0] = 0.0
    y[y < 0.0] = 0.0

    # for fixed oxygen concentration:
    if kla < 0.0:
        y[SO] = abs(kla)

    # process rates:
    proc1 = mu_h * (ytemp[SS] / (k_s + ytemp[SS])) * (ytemp[SO] / (k_oh + ytemp[SO])) * ytemp[XBH]
    proc2 = (
        mu_h
        * (ytemp[SS] / (k_s + ytemp[SS]))
        * (k_oh / (k_oh + ytemp[SO]))
        * (ytemp[SNO] / (k_no + ytemp[SNO]))
        * ny_g
        * ytemp[XBH]
    )
    proc3 = mu_a * (ytemp[SNH] / (k_nh + ytemp[SNH])) * (ytemp[SO] / (k_oa + ytemp[SO])) * ytemp[XBA]
    proc4 = b_h * ytemp[XBH]
    proc5 = b_a * ytemp[XBA]
    proc6 = k_a * ytemp[SND] * ytemp[XBH]
    proc7 = (
        k_h
        * ((ytemp[XS] / ytemp[XBH]) / (k_x + (ytemp[XS] / ytemp[XBH])))
        * ((ytemp[SO] / (k_oh + ytemp[SO])) + ny_h * (k_oh / (k_oh + ytemp[SO])) * (ytemp[SNO] / (k_no + ytemp[SNO])))
        * ytemp[XBH]
    )
    proc8 = proc7 * (ytemp[XND] / ytemp[XS])

    # conversion rates:
    reac[SI] = 0.0
    reac[SS] = (-proc1 - proc2) / y_h + proc7
    reac[XI] = 0.0
    reac[XS] = (1.0 - f_p) * (proc4 + proc5) - proc7
    reac[XBH] = proc1 + proc2 - proc4
    reac[XBA] = proc3 - proc5
    reac[XP] = f_p * (proc4 + proc5)
    reac[SO] = -(1.0 - y_h) / y_h * proc1 - (4.57 - y_a) / y_a * proc3
    reac[SNO] = -((1.0 - y_h) / (2.86 * y_h)) * proc2 + proc3 / y_a
    reac[SNH] = -i_xb * (proc1 + proc2) - (i_xb + (1.0 / y_a)) * proc3 + proc6
    reac[SND] = -proc6 + proc8
    reac[XND] = (i_xb - f_p * i_xp) * (proc4 + proc5) - proc8
    reac[SALK] = (
        -i_xb / 14.0 * proc1
        + ((1.0 - y_h) / (14.0 * 2.86 * y_h) - (i_xb / 14.0)) * proc2
        - ((i_xb / 14.0) + 1.0 / (7.0 * y_a)) * proc3
        + proc6 / 14.0
    )
    reac[SD1] = 0.0
    reac[SD2] = 0.0
    reac[SD3] = 0.0
    reac[XD4] = 0.0
    reac[XD5] = 0.0

    # differential equations:
    dy[0:7] = 1.0 / volume * (y_in[Q] * (y_in[0:7] - y[0:7])) + reac[0:7]
    if kla >= 0.0:
        dy[SO] = 1.0 / volume * (y_in[Q] * (y_in[SO] - y[SO])) + reac[SO] + kla_temp * (so_sat_temp - y[SO])
    dy[8:13] = 1.0 / volume * (y_in[Q] * (y_in[8:13] - y[8:13])) + reac[8:13]

    if tempmodel:
        dy[TEMP] = 1.0 / volume * (y_in[Q] * (y_in[TEMP] - y[TEMP]))

    if activate:
        dy[16:21] = 1.0 / volume * (y_in[Q] * (y_in[16:21] - y[16:21])) + reac[16:21]

    return dy


@jit(nopython=True)
def carbonaddition(y_in, carb, csourceconc):
    """Returns the reactor inlet concentrations after adding an external carbon source to the general flow.

    Parameters
    ----------
    y_in : np.ndarray(21)
        Influent concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        before adding external carbon source. \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
        SD1, SD2, SD3, XD4, XD5]
    carb : float
        External carbon flow rate for carbon addition to a reactor [kg(COD) ⋅ d⁻¹].
    csourceconc : float
        External carbon source concentration [g(COD) ⋅ m⁻³].

    Returns
    -------
    y_in : np.ndarray(21)
        Influent concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        after adding external carbon source. \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
        SD1, SD2, SD3, XD4, XD5]
    """

    y_in[SI] = (y_in[SI] * y_in[Q]) / (carb + y_in[Q])
    y_in[SS] = (y_in[SS] * y_in[Q] + csourceconc * carb) / (carb + y_in[Q])
    y_in[3:14] = (y_in[3:14] * y_in[Q]) / (carb + y_in[Q])
    # Temperature stays the same
    y_in[16:21] = (y_in[16:21] * y_in[Q]) / (carb + y_in[Q])
    y_in[Q] += carb

    return y_in


class ASM1Reactor(Module):
    """IAWQ ASM1 (Activated Sludge Model No. 1) with temperature dependencies of the kinetic parameters.

    In addition to the ASM1 states, TSS and dummy states are included.
    Temperature dependency for oxygen saturation concentration and KLa has
    also been added in accordance with BSM2 documentation.

    Parameters
    ----------
    kla : float
        Oxygen transfer coefficient in aerated reactors [d⁻¹].
    volume : float
        Volume of the reactor [m³].
    y0 : np.ndarray(21)
        Initial integration values of the 21 components
        (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
        [S_I, S_S, X_I, X_S, X_BH, X_BA, X_P, S_O, S_NO, S_NH, S_ND, X_ND,
        S_ALK, TSS, Q, T, S_D1, S_D2, S_D3, X_D4, X_D5]
    asm1par : np.ndarray(24)
        Parameters needed for the ASM1 equations. \n
        [MU_H, K_S, K_OH, K_NO, B_H, MU_A, K_NH, K_OA, B_A, NY_G, K_A, K_H, K_X, NY_H,
        Y_H, Y_A, F_P, I_XB, I_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS]
    carb : float
        External carbon flow rate for carbon addition to a reactor [kg(COD) ⋅ d⁻¹].
    csourceconc : float
        External carbon source concentration [g(COD) ⋅ m⁻³].
    tempmodel : bool
        If true, mass balance for the wastewater temperature is used in process rates,
        otherwise influent wastewater temperature is just passed through process reactors.
    activate : bool
        If true, dummy states are activated, otherwise dummy states are not activated.
    """

    def __init__(
        self,
        kla: float,
        volume: float,
        y0: np.ndarray,
        asm1par: np.ndarray,
        carb: float,
        csourceconc: float,
        *,
        tempmodel: bool,
        activate: bool,
    ):
        self.kla = kla
        self.volume = volume
        self.y0 = y0
        self.asm1par = asm1par
        self.carb = carb
        self.csourceconc = csourceconc
        self.tempmodel = tempmodel
        self.activate = activate

    def output(self, timestep: int | float, step: int | float, y_in: np.ndarray) -> np.ndarray:
        """Returns the solved differential equations based on ASM1 model.

        Parameters
        ----------
        timestep : float
            Size of integration interval [d].
        step : float
            Start time for integration interval [d].
        y_in : np.ndarray(21)
            Influent concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
            before the activated sludge reactor. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]

        Returns
        -------
        y_out : np.ndarray(21)
            Effluent concentration of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
            after the activated sludge reactor. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        """

        t_eval = np.array([step, step + timestep])  # time interval for odeint

        if self.carb > 0.0:
            y_in = carbonaddition(y_in, self.carb, self.csourceconc)

        ode = odeint(
            asm1equations,
            self.y0,
            t_eval,
            tfirst=True,
            args=(y_in, self.asm1par, self.kla, self.volume, self.tempmodel, self.activate),
        )
        y_out = ode[1]

        y_out[TSS] = (
            self.asm1par[19] * y_out[XI]
            + self.asm1par[20] * y_out[XS]
            + self.asm1par[21] * y_out[XBH]
            + self.asm1par[22] * y_out[XBA]
            + self.asm1par[23] * y_out[XP]
        )
        y_out[Q] = y_in[Q]

        if not self.tempmodel:
            y_out[TEMP] = y_in[TEMP]

        if not self.activate:
            y_out[16:20] = 0.0

        self.y0 = y_out  # initial integration values for next integration

        return y_out
