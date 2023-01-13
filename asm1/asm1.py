import numpy as np
from scipy.integrate import solve_ivp, odeint
from numba import jit, njit


@jit(nopython=True)
def derivatives(t, y, y_in, asmpar, kla, volume, sosat, tempmodel, decay_switch):
    """Returns an array containing the differential equations of ASM1

    Parameters
    ----------
    t : np.ndarray
        Time interval for integration, needed for the solver

    y : np.ndarray
        Solution of the differential equations, needed for the solver

    y_in : np.ndarray
        Reactor inlet concentrations of the 21 ASM1 components

    asmpar : np.ndarray
        26 parameters needed for ASM1 equations

    kla : int
        Oxygen transfer coefficient in aerated reactors

    volume : int
        Volume of the reactor

    sosat : int
        Saturation concentration for oxygen

    tempmodel : bool
        If true, mass balance for the wastewater temperature is used in process rates,
        otherwise influent wastewater temperature is just passed through process reactors

    decay_switch : bool
        If true, the decay of heterotrophs and autotrophs is depending on the electron acceptor present,
        otherwise the decay do not change

    Returns
    -------
    np.ndarray
        Array containing the 21 differential equations of ASM1 model

    """

    dy = np.zeros(21)

    indices_components = np.arange(21)
    SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components

    mu_H, K_S, K_OH, K_NO, b_H, mu_A, K_NH, K_OA, b_A, ny_g, k_a, k_h, K_X, ny_h, Y_H, Y_A, f_P, i_XB, i_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS, hH_NO3_end, hA_NO3_end = asmpar

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

    # for fixed oxygen concentration:
    if kla < 0.0:
        y[SO] = abs(kla)

    # process rates:
    if decay_switch:
        proc1 = mu_H * (ytemp[SS] / (K_S + ytemp[SS])) * (ytemp[SO] / (K_OH + ytemp[SO])) * ytemp[XBH]
        proc2 = mu_H * (ytemp[SS] / (K_S + ytemp[SS])) * (K_OH / (K_OH + ytemp[SO])) * (ytemp[SNO] / (K_NO + ytemp[SNO])) * ny_g * ytemp[XBH]
        proc3 = mu_A * (ytemp[SNH] / (K_NH + ytemp[SNH])) * (ytemp[SO] / (K_OA + ytemp[SO])) * ytemp[XBA]
        proc4 = b_H * (ytemp[SO] / (K_OH + ytemp[SO]) + hH_NO3_end * K_OH / (K_OH + ytemp[SO]) * ytemp[SNO] / (K_NO + ytemp[SNO])) * ytemp[XBH]
        proc5 = b_A * (ytemp[SO] / (K_OH + ytemp[SO]) + hA_NO3_end * K_OH / (K_OH + ytemp[SO]) * ytemp[SNO] / (K_NO + ytemp[SNO])) * ytemp[XBA]
        proc6 = k_a * ytemp[SND] * ytemp[XBH]
        proc7 = k_h * ((ytemp[XS] / ytemp[XBH]) / (K_X + (ytemp[XS] / ytemp[XBH]))) * ((ytemp[SO] / (K_OH + ytemp[SO])) + ny_h * (K_OH / (K_OH + ytemp[SO])) * (ytemp[SNO] / (K_NO + ytemp[SNO]))) * ytemp[XBH]
        proc8 = proc7 * (ytemp[XND] / ytemp[XS])

    elif not decay_switch:
        proc1 = mu_H * (ytemp[SS] / (K_S + ytemp[SS])) * (ytemp[SO] / (K_OH + ytemp[SO])) * ytemp[XBH]
        proc2 = mu_H * (ytemp[SS] / (K_S + ytemp[SS])) * (K_OH / (K_OH + ytemp[SO])) * (ytemp[SNO] / (K_NO + ytemp[SNO])) * ny_g * ytemp[XBH]
        proc3 = mu_A * (ytemp[SNH] / (K_NH + ytemp[SNH])) * (ytemp[SO] / (K_OA + ytemp[SO])) * ytemp[XBA]
        proc4 = b_H * ytemp[XBH]
        proc5 = b_A * ytemp[XBA]
        proc6 = k_a * ytemp[SND] * ytemp[XBH]
        proc7 = k_h * ((ytemp[XS] / ytemp[XBH]) / (K_X + (ytemp[XS] / ytemp[XBH]))) * ((ytemp[SO] / (K_OH + ytemp[SO])) + ny_h * (K_OH / (K_OH + ytemp[SO])) * (ytemp[SNO] / (K_NO + ytemp[SNO]))) * ytemp[XBH]
        proc8 = proc7 * (ytemp[XND] / ytemp[XS])

    # conversion rates:
    reac1 = 0.0
    reac2 = (-proc1 - proc2) / Y_H + proc7
    reac3 = 0.0
    reac4 = (1.0 - f_P) * (proc4 + proc5) - proc7
    reac5 = proc1 + proc2 - proc4
    reac6 = proc3 - proc5
    reac7 = f_P * (proc4 + proc5)
    reac8 = -((1.0 - Y_H) / Y_H) * proc1 - ((4.57 - Y_A) / Y_A) * proc3
    reac9 = -((1.0 - Y_H) / (2.86 * Y_H)) * proc2 + proc3 / Y_A
    reac10 = -i_XB * (proc1 + proc2) - (i_XB + (1.0 / Y_A)) * proc3 + proc6
    reac11 = -proc6 + proc8
    reac12 = (i_XB - f_P * i_XP) * (proc4 + proc5) - proc8
    reac13 = -i_XB / 14.0 * proc1 + ((1.0 - Y_H) / (14.0 * 2.86 * Y_H) - (i_XB / 14.0)) * proc2 - (
                (i_XB / 14.0) + 1.0 / (7.0 * Y_A)) * proc3 + proc6 / 14.0
    reac16 = 0.0
    reac17 = 0.0
    reac18 = 0.0
    reac19 = 0.0
    reac20 = 0.0

    # differential equations:
    dy[SI] = 1.0 / volume * (y_in[Q] * (y_in[SI] - y[SI])) + reac1
    dy[SS] = 1.0 / volume * (y_in[Q] * (y_in[SS] - y[SS])) + reac2
    dy[XI] = 1.0 / volume * (y_in[Q] * (y_in[XI] - y[XI])) + reac3
    dy[XS] = 1.0 / volume * (y_in[Q] * (y_in[XS] - y[XS])) + reac4
    dy[XBH] = 1.0 / volume * (y_in[Q] * (y_in[XBH] - y[XBH])) + reac5
    dy[XBA] = 1.0 / volume * (y_in[Q] * (y_in[XBA] - y[XBA])) + reac6
    dy[XP] = 1.0 / volume * (y_in[Q] * (y_in[XP] - y[XP])) + reac7
    if kla < 0.0:
        dy[SO] = 0.0
    else:
        dy[SO] = 1.0 / volume * (y_in[Q] * (y_in[SO] - y[SO])) + reac8 + KLa_temp * (SO_sat_temp - y[SO])
    dy[SNO] = 1.0 / volume * (y_in[Q] * (y_in[SNO] - y[SNO])) + reac9
    dy[SNH] = 1.0 / volume * (y_in[Q] * (y_in[SNH] - y[SNH])) + reac10
    dy[SND] = 1.0 / volume * (y_in[Q] * (y_in[SND] - y[SND])) + reac11
    dy[XND] = 1.0 / volume * (y_in[Q] * (y_in[XND] - y[XND])) + reac12
    dy[SALK] = 1.0 / volume * (y_in[Q] * (y_in[SALK] - y[SALK])) + reac13
    dy[TSS] = 0.0
    dy[Q] = 0.0
    if not tempmodel:
        dy[TEMP] = 0.0
    else:
        dy[TEMP] = 1.0 / volume * (y_in[Q] * (y_in[TEMP] - y[TEMP]))

    dy[SD1] = 1.0 / volume * (y_in[Q] * (y_in[SD1] - y[SD1])) + reac16
    dy[SD2] = 1.0 / volume * (y_in[Q] * (y_in[SD2] - y[SD2])) + reac17
    dy[SD3] = 1.0 / volume * (y_in[Q] * (y_in[SD3] - y[SD3])) + reac18
    dy[XD4] = 1.0 / volume * (y_in[Q] * (y_in[XD4] - y[XD4])) + reac19
    dy[XD5] = 1.0 / volume * (y_in[Q] * (y_in[XD5] - y[XD5])) + reac20

    return dy


class ASM1reactor:
    def __init__(self,  kla, volume, sosat, y0, asmpar, tempmodel, activate, decay_switch):
        """
        Parameters
        ----------
        kla : int
            Oxygen transfer coefficient in aerated reactors

        volume : int
            Volume of the reactor

        sosat : int
            Saturation concentration for oxygen

        y0 : np.ndarray
            Initial values for the 21 components

        asmpar : np.ndarray
            26 parameters needed for ASM1 equations

        tempmodel : bool
            If true, mass balance for the wastewater temperature is used in process rates,
            otherwise influent wastewater temperature is just passed through process reactors

        activate : bool
            If true, dummy states are activated, otherwise dummy states are activated

        decay_switch : bool
            If true, the decay of heterotrophs and autotrophs is depending on the electron acceptor present,
            otherwise the decay do not change
        """

        self.kla = kla              # oxygen transfer coefficient in aerated reactors
        self.volume = volume  # volume of the reactor compartment
        self.sosat = sosat          # saturation concentration for oxygen
        self.y0 = y0                # initial states for integration (damit man es anpassen kann)
        self.asmpar = asmpar        # Parameters of ASM1-Model
        self.tempmodel = tempmodel
        self.activate = activate
        self.decay_switch = decay_switch

    def output(self, timestep, step, y_in):
        """Returns the solved differential equations of ASM1 model.

        Parameters
        ----------
        timestep : int or float
            Size of integration interval in days
        step : int or float
            Upper boundary for integration interval in days
        y_in : np.ndarray
            Reactor inlet concentrations of the 21 ASM1 components

        Returns
        -------
        np.ndarray
            Array containing the concentrations of the 21 components at the current time step after the integration
        """

        t_eval = np.array([step, step+timestep])    # time interval for odeint

        ode = odeint(derivatives, self.y0, t_eval, tfirst=True, args=(y_in, self.asmpar, self.kla, self.volume, self.sosat, self.tempmodel, self.decay_switch,), rtol=1e-5, atol=1e-8)
        y_out = ode[1]

        y_out[13] = self.asmpar[19] * y_out[2] + self.asmpar[20] * y_out[3] + self.asmpar[21] * y_out[4] + self.asmpar[22] * y_out[5] + self.asmpar[23] * y_out[6]  # TSS
        y_out[14] = y_in[14]  # Flow
        if not self.tempmodel:
            y_out[15] = y_in[15]  # Temperature

        if not self.activate:
            y_out[16:20] = 0.0
        self.y0 = y_out

        return y_out
