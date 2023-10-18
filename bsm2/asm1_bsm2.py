import numpy as np
from scipy.integrate import odeint
from numba import jit


indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components

@jit(nopython=True)
def asm1equations(t, y, y_in, asm1par, kla, volume, tempmodel, activate):
    """Returns an array containing the differential equations based on ASM1

    Parameters
    ----------
    t : np.ndarray
        Time interval for integration, needed for the solver
    y : np.ndarray
        Solution of the differential equations, needed for the solver
    y_in : np.ndarray
        Reactor inlet concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
    asm1par : np.ndarray
        24 parameters needed for ASM1 equations
    kla : int
        Oxygen transfer coefficient in aerated reactors
    volume : int
        Volume of the reactor
    tempmodel : bool
        If true, mass balance for the wastewater temperature is used in process rates,
        otherwise influent wastewater temperature is just passed through process reactors
    activate : bool
            If true, dummy states are activated, otherwise dummy states are not activated

    Returns
    -------
    np.ndarray
        Array containing the 21 differential equations based on ASM1 model
    """

    dy = np.zeros(21)
    reac = np.zeros(21)

    mu_H, K_S, K_OH, K_NO, b_H, mu_A, K_NH, K_OA, b_A, ny_g, k_a, k_h, K_X, ny_h, Y_H, Y_A, f_P, i_XB, i_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS = asm1par

    # temperature compensation:
    if not tempmodel:
        mu_H = mu_H * np.exp((np.log(mu_H / 3.0) / 5.0) * (y_in[TEMP] - 15.0))  # temperature at the influent of the reactor
        b_H = b_H * np.exp((np.log(b_H / 0.2) / 5.0) * (y_in[TEMP] - 15.0))
        mu_A = mu_A * np.exp((np.log(mu_A / 0.3) / 5.0) * (y_in[TEMP] - 15.0))
        b_A = b_A * np.exp((np.log(b_A / 0.03) / 5.0) * (y_in[TEMP] - 15.0))
        k_h = k_h * np.exp((np.log(k_h / 2.5) / 5.0) * (y_in[TEMP] - 15.0))
        k_a = k_a * np.exp((np.log(k_a / 0.04) / 5.0) * (y_in[TEMP] - 15.0))
        SO_sat_temp = 0.9997743214 * 8.0 / 10.5 * (56.12 * 6791.5 * np.exp(
            -66.7354 + 87.4755 / ((y_in[TEMP] + 273.15) / 100.0) + 24.4526 * np.log(
                (y_in[TEMP] + 273.15) / 100.0)))  # van't Hoff equation
        KLa_temp = kla * np.power(1.024, (y_in[TEMP] - 15.0))

    else:
        mu_H = mu_H * np.exp((np.log(mu_H / 3.0) / 5.0) * (y[TEMP] - 15.0))  # current temperature in the reactor
        b_H = b_H * np.exp((np.log(b_H / 0.2) / 5.0) * (y[TEMP] - 15.0))
        mu_A = mu_A * np.exp((np.log(mu_A / 0.3) / 5.0) * (y[TEMP] - 15.0))
        b_A = b_A * np.exp((np.log(b_A / 0.03) / 5.0) * (y[TEMP] - 15.0))
        k_h = k_h * np.exp((np.log(k_h / 2.5) / 5.0) * (y[TEMP] - 15.0))
        k_a = k_a * np.exp((np.log(k_a / 0.04) / 5.0) * (y[TEMP] - 15.0))
        SO_sat_temp = 0.9997743214 * 8.0 / 10.5 * (56.12 * 6791.5 * np.exp(
            -66.7354 + 87.4755 / ((y[TEMP] + 273.15) / 100.0) + 24.4526 * np.log(
                (y[15] + 273.15) / 100.0)))  # van't Hoff equation
        KLa_temp = kla * np.power(1.024, (y[TEMP] - 15.0))

    # concentrations should not be negative:
    ytemp = y
    ytemp[ytemp < 0.0] = 0.0
    y[y < 0.0] = 0.0

    # for fixed oxygen concentration:
    if kla < 0.0:
        y[SO] = abs(kla)

    # process rates:
    proc1 = mu_H * (ytemp[SS] / (K_S + ytemp[SS])) * (ytemp[SO] / (K_OH + ytemp[SO])) * ytemp[XBH]
    proc2 = mu_H * (ytemp[SS] / (K_S + ytemp[SS])) * (K_OH / (K_OH + ytemp[SO])) * (ytemp[SNO] / (K_NO + ytemp[SNO])) * ny_g * ytemp[XBH]
    proc3 = mu_A * (ytemp[SNH] / (K_NH + ytemp[SNH])) * (ytemp[SO] / (K_OA + ytemp[SO])) * ytemp[XBA]
    proc4 = b_H * ytemp[XBH]
    proc5 = b_A * ytemp[XBA]
    proc6 = k_a * ytemp[SND] * ytemp[XBH]
    proc7 = k_h * ((ytemp[XS] / ytemp[XBH]) / (K_X + (ytemp[XS] / ytemp[XBH]))) * ((ytemp[SO] / (K_OH + ytemp[SO])) + ny_h * (K_OH / (K_OH + ytemp[SO])) * (ytemp[SNO] / (K_NO + ytemp[SNO]))) * ytemp[XBH]
    proc8 = proc7 * (ytemp[XND] / ytemp[XS])

    # conversion rates:
    reac[SI] = 0.0
    reac[SS] = (-proc1 - proc2) / Y_H + proc7
    reac[XI] = 0.0
    reac[XS] = (1.0 - f_P) * (proc4 + proc5) - proc7
    reac[XBH] = proc1 + proc2 - proc4
    reac[XBA] = proc3 - proc5
    reac[XP] = f_P * (proc4 + proc5)
    reac[SO] = -(1.0 - Y_H) / Y_H * proc1 - (4.57 - Y_A) / Y_A * proc3
    reac[SNO] = -((1.0 - Y_H) / (2.86 * Y_H)) * proc2 + proc3 / Y_A
    reac[SNH] = -i_XB * (proc1 + proc2) - (i_XB + (1.0 / Y_A)) * proc3 + proc6
    reac[SND] = -proc6 + proc8
    reac[XND] = (i_XB - f_P * i_XP) * (proc4 + proc5) - proc8
    reac[SALK] = -i_XB / 14.0 * proc1 + ((1.0 - Y_H) / (14.0 * 2.86 * Y_H) - (i_XB / 14.0)) * proc2 - (
                (i_XB / 14.0) + 1.0 / (7.0 * Y_A)) * proc3 + proc6 / 14.0
    reac[SD1] = 0.0
    reac[SD2] = 0.0
    reac[SD3] = 0.0
    reac[XD4] = 0.0
    reac[XD5] = 0.0

    # differential equations:
    dy[0:7] = 1.0 / volume * (y_in[Q] * (y_in[0:7] - y[0:7])) + reac[0:7]
    if kla >= 0.0:
        dy[SO] = 1.0 / volume * (y_in[Q] * (y_in[SO] - y[SO])) + reac[SO] + KLa_temp * (SO_sat_temp - y[SO])
    dy[8:13] = 1.0 / volume * (y_in[Q] * (y_in[8:13] - y[8:13])) + reac[8:13]

    if tempmodel:
        dy[TEMP] = 1.0 / volume * (y_in[Q] * (y_in[TEMP] - y[TEMP]))

    if activate:
        dy[16:21] = 1.0 / volume * (y_in[Q] * (y_in[16:21] - y[16:21])) + reac[16:21]

    return dy

@jit(nopython=True)
def carbonaddition(y_in, carb, csourceconc):
    """Returns the reactor inlet concentrations after adding an external carbon source

    Parameters
    ----------
    y_in : np.ndarray
        Reactor inlet concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states) before adding external carbon source.
    carb : float
        external carbon flow rate for carbon addition to a reactor
    csourceconc : float
        external carbon source concentration

    Returns
    -------
    np.ndarray
        Array containing the reactor inlet concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states) after adding external carbon source
    """
    yr_in = np.zeros(21)
    yr_in[SI] = (y_in[SI] * y_in[Q]) / (carb + y_in[Q])
    yr_in[SS] = (y_in[SS] * y_in[Q] + csourceconc * carb) / (carb + y_in[Q])
    yr_in[2:14] = (y_in[2:14] * y_in[Q]) / (carb + y_in[Q])
    yr_in[Q] = carb + y_in[Q]
    # Temperature stays the same
    yr_in[16:21] = (y_in[16:21] * y_in[Q]) / (carb + y_in[Q])

    return yr_in


class ASM1reactor:
    def __init__(self,  kla, volume, y0, asm1par, carb, csourceconc, tempmodel, activate):
        """
        Parameters
        ----------
        kla : float
            Oxygen transfer coefficient in aerated reactors
        volume : float
            Volume of the reactor
        y0 : np.ndarray
            Initial integration values of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        asm1par : np.ndarray
            24 parameters needed for ASM1 equations
        carb : float
            external carbon flow rate for carbon addition to a reactor
        csourceconc : float
            external carbon source concentration
        tempmodel : bool
            If true, mass balance for the wastewater temperature is used in process rates,
            otherwise influent wastewater temperature is just passed through process reactors
        activate : bool
            If true, dummy states are activated, otherwise dummy states are not activated
        """

        self.kla = kla
        self.volume = volume
        self.y0 = y0
        self.asm1par = asm1par
        self.carb = carb
        self.csourceconc = csourceconc
        self.tempmodel = tempmodel
        self.activate = activate

    def output(self, timestep, step, y_in):
        """Returns the solved differential equations based on ASM1 model

        Parameters
        ----------
        timestep : int or float
            Size of integration interval in days
        step : int or float
            Bottom boundary for integration interval in days
        y_in : np.ndarray
            Reactor inlet concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)

        Returns
        -------
        np.ndarray
            Array containing the values of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states) at the current time step after the integration
        """

        t_eval = np.array([step, step+timestep])    # time interval for odeint

        if self.carb > 0.0:
            yr_in = carbonaddition(y_in, self.carb, self.csourceconc)
        else:
            yr_in = y_in

        ode = odeint(asm1equations, self.y0, t_eval, tfirst=True, args=(yr_in, self.asm1par, self.kla, self.volume, self.tempmodel, self.activate))
        y_out = ode[1]

        y_out[TSS] = self.asm1par[19] * y_out[XI] + self.asm1par[20] * y_out[XS] + self.asm1par[21] * y_out[XBH] + self.asm1par[22] * y_out[XBA] + self.asm1par[23] * y_out[XP]
        y_out[Q] = y_in[Q]

        if not self.tempmodel:
            y_out[TEMP] = y_in[TEMP]

        if not self.activate:
            y_out[16:20] = 0.0

        self.y0 = y_out  # initial integration values for next integration

        return y_out
