import numpy as np
from scipy.integrate import odeint
from numba import jit

# definition of constants for indexing:
indices_components = np.arange(24)
SO2, SI, SS, SNH4, SN2, SNOX, SALK, XI, XS, XH, XSTO, XA, XSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5, COD, N2, ION, TSS = indices_components


@jit(nopython=True)
def derivatives(t, y, y_in, asm3par, kla, volume, tempmodel, activate):
    """Returns an array containing the differential equations of ASM3

        Parameters
        ----------
        t : np.ndarray
            Time interval for integration, needed for the solver

        y : np.ndarray
            Solution of the differential equations, needed for the solver

        y_in : np.ndarray
            Reactor inlet concentrations of the 20 components (13 ASM3 components, Q, T and 5 dummy states)

        asm3par : np.ndarray
            37 parameters needed for ASM3 equations

        kla : int
            Oxygen transfer coefficient in aerated reactors

        volume : int
            Volume of the reactor

        tempmodel : bool
            If true, mass balance for the wastewater temperature is used in process rates,
            otherwise influent wastewater temperature is just passed through process reactors

        activate : bool
            If true, dummy states are activated, otherwise dummy states are activated

        Returns
        -------
        np.ndarray
            Array containing the 20 differential equations of ASM3 model

        """

    dy = np.zeros(20)
    reac = np.zeros(20)

    asm3kinpar_10 = np.array([2, 1, 2.5, 0.6, 0.2, 0.5, 2, 1, 1, 0.01, 0.1, 0.1, 0.05, 0.1, 0.05, 0.35, 1, 0.5, 0.5,
                              0.05, 0.02])
    asm3par_temp = np.zeros(21)
    # temperature compensation of kinetic parameters, saturation concentration of O2 and KLa:
    if not tempmodel:
        # compensation with the temperature at the inlet of the reactor:
        asm3par_temp[0:21] = asm3par[0:21] * np.exp(np.log(asm3par[0:21] / asm3kinpar_10) / (20 - 10) * (y_in[TEMP] - 20))
        sosat_temp = 0.9997743214 * 8.0 / 10.5 * (56.12 * 6791.5 * np.exp(-66.7354 + 87.4755 / ((y_in[TEMP] + 273.15) /
                        100.0) + 24.4526 * np.log((y_in[TEMP] + 273.15) / 100.0)))  # van't Hoff equation (Gernaey, 2015
                                                                                    # (Lide, 2004))
        kla_temp = kla * pow(1.024, (y_in[TEMP] - 15))  # from Gernaey, 2015 (ASCE, 1993)
    else:
        # compensation with the current temperature in the reactor:
        asm3par[0:21] = asm3par[0:21] * np.exp(np.log(asm3par[0:21] / asm3kinpar_10) / (20 - 10) * (y[TEMP] - 20))
        sosat_temp = 0.9997743214 * 8.0 / 10.5 * (56.12 * 6791.5 * np.exp(-66.7354 + 87.4755 / ((y[TEMP] + 273.15) /
                        100.0) + 24.4526 * np.log((y[TEMP] + 273.15) / 100.0)))  # van't Hoff equation (Gernaey, 2015
                                                                                 # (Lide, 2004))
        kla_temp = kla * pow(1.024, (y[TEMP] - 15))  # from Gernaey, 2015 (ASCE, 1993)

    k_H, K_X, k_STO, ny_NOX, K_O2, K_NOX, K_S, K_STO, mu_H, K_NH4, K_ALK, b_HO2, b_HNOX, b_STOO2, b_STONOX, mu_A, \
    K_ANH4, K_AO2, K_AALK, b_AO2, b_ANOX = asm3par_temp[0:21]
    f_SI, Y_STOO2, Y_STONOX, Y_HO2, Y_HNOX, Y_A, f_XI, i_NSI, i_NSS, i_NXI, i_NXS, i_NBM, i_SSXI, i_SSXS, i_SSBM, i_SSSTO = asm3par[21:37]

    # # from Gujer, 1999 and Hauduc, 2010 with original notation
    x1 = 1 - f_SI
    x2 = - (1 - Y_STOO2)
    x3 = - (1 - Y_STONOX) / 2.86
    x4 = - (1 - Y_HO2) / Y_HO2
    x5 = - (1 - Y_HNOX) / Y_HNOX * 1 / 2.86
    x6 = - (1 - f_XI)
    x7 = - (1 - f_XI) / 2.86
    x8 = - 1
    x9 = - 1 / 2.86
    x10 = - (4.57 - Y_A) / Y_A
    x11 = - (1 - f_XI)
    x12 = - (1 - f_XI) / 2.86

    y1 = - (1 - f_SI) * i_NSS - f_SI * i_NSI + i_NXS
    y2 = i_NSS
    y3 = i_NSS
    y4 = - i_NBM
    y5 = - i_NBM
    y6 = - f_XI * i_NXI + i_NBM
    y7 = - f_XI * i_NXI + i_NBM
    y10 = - 1 / Y_A - i_NBM
    y11 = - f_XI * i_NXI + i_NBM
    y12 = - f_XI * i_NXI + i_NBM

    z1 = y1 / 14     # in original: 1/14
    z2 = y2 / 14
    z3 = y3 / 14 + x3 / (-14)   # in original: - 1/14
    z4 = y4 / 14
    z5 = y5 / 14 + x5 / (-14)
    z6 = y6 / 14
    z7 = y7 / 14 + x7 / (-14)
    z9 = x9 / (- 14)
    z10 = y10 / 14 + 1 / (Y_A * (-14))
    z11 = y11 / 14
    z12 = y12 / 14 + x12 / (-14)

    t2 = Y_STOO2 * i_SSSTO
    t3 = Y_STONOX * i_SSSTO
    t4 = (- 1 / Y_HO2) * i_SSSTO + i_SSBM
    t5 = (- 1 / Y_HNOX) * i_SSSTO + i_SSBM
    t6 = - i_SSBM + f_XI * i_SSXI
    t7 = - i_SSBM + f_XI * i_SSXI
    t8 = - i_SSSTO
    t9 = - i_SSSTO
    t10 = i_SSBM
    t11 = - i_SSBM + f_XI * i_SSXI
    t12 = - i_SSBM + f_XI * i_SSXI

    y[y < 0.0] = 0.0    # concentrations can not be negative

    # fixed oxygen concentration in a reactor when kla is negative
    if kla < 0.0:
        y[SO2] = abs(kla)

    # process rates
    proc1 = k_H * (y[XS] / y[XH]) / (K_X + y[XS] / y[XH]) * y[XH]
    proc2 = k_STO * (y[SO2] / (K_O2 + y[SO2])) * y[SS] / (K_S + y[SS]) * y[XH]
    proc3 = k_STO * ny_NOX * K_O2 / (K_O2 + y[SO2]) * y[SNOX] / (K_NOX + y[SNOX]) * y[SS] / (K_S + y[SS]) * y[XH]
    proc4 = mu_H * y[SO2] / (K_O2 + y[SO2]) * y[SNH4] / (K_NH4 + y[SNH4]) * y[SALK] / (K_ALK + y[SALK]) * \
            y[XSTO] / y[XH] / (K_STO + y[XSTO] / y[XH]) * y[XH]
    proc5 = mu_H * ny_NOX * K_O2 / (K_O2 + y[SO2]) * y[SNOX] / (K_NOX + y[SNOX]) * y[SNH4] / (K_NH4 + y[SNH4]) * \
            y[SALK] / (K_ALK + y[SALK]) * y[XSTO] / y[XH] / (K_STO + y[XSTO] / y[XH]) * y[XH]
    proc6 = b_HO2 * y[SO2] / (K_O2 + y[SO2]) * y[XH]
    proc7 = b_HNOX * K_O2 / (K_O2 + y[SO2]) * y[SNOX] / (K_NOX + y[SNOX]) * y[XH]
    proc8 = b_STOO2 * y[SO2] / (K_O2 + y[SO2]) * y[XSTO]
    proc9 = b_STONOX * K_O2 / (K_O2 + y[SO2]) * y[SNOX] / (K_NOX + y[SNOX]) * y[XSTO]
    proc10 = mu_A * y[SO2] / (K_AO2 + y[SO2]) * y[SNH4] / (K_ANH4 + y[SNH4]) * y[SALK] / (K_AALK + y[SALK]) * y[XA]
    proc11 = b_AO2 * y[SO2] / (K_AO2 + y[SO2]) * y[XA]
    proc12 = b_ANOX * K_AO2 / (K_AO2 + y[SO2]) * y[SNOX] / (K_NOX + y[SNOX]) * y[XA]  

    # conversion rates:
    reac[SO2] = x2 * proc2 + x4 * proc4 + x6 * proc6 + x8 * proc8 + x10 * proc10 + x11 * proc11
    reac[SI] = f_SI * proc1
    reac[SS] = x1 * proc1 - proc2 - proc3
    reac[SNH4] = y1 * proc1 + y2 * proc2 + y3 * proc3 + y4 * proc4 + y5 * proc5 + y6 * proc6 + y7 * proc7 + \
                 y10 * proc10 + y11 * proc11 + y12 * proc12
    reac[SN2] = -x3 * proc3 - x5 * proc5 - x7 * proc7 - x9 * proc9 - x12 * proc12
    reac[SNOX] = x3 * proc3 + x5 * proc5 + x7 * proc7 + x9 * proc9 + 1/Y_A * proc10 + x12 * proc12
    reac[SALK] = z1 * proc1 + z2 * proc2 + z3 * proc3 + z4 * proc4 + z5 * proc5 + z6 * proc6 + z7 * proc7 + z9 * proc9\
                 + z10 * proc10 + z11 * proc11 + z12 * proc12
    reac[XI] = f_XI * proc6 + f_XI * proc7 + f_XI * proc11 + f_XI * proc12
    reac[XS] = - proc1
    reac[XH] = proc4 + proc5 - proc6 - proc7
    reac[XSTO] = Y_STOO2 * proc2 + Y_STONOX * proc3 - 1/Y_HO2 * proc4 - 1/Y_HNOX * proc5 - proc8 - proc9
    reac[XA] = proc10 - proc11 - proc12
    reac[XSS] = -i_SSXI * proc1 + t2 * proc2 + t3 * proc3 + t4 * proc4 + t5 * proc5 + t6 * proc6 + t7 * proc7 + t8 * \
                proc8 + t9 * proc9 + t10 * proc10 + t11 * proc11 + t12 * proc12

    reac[SD1] = 0.0
    reac[SD2] = 0.0
    reac[SD3] = 0.0
    reac[XD4] = 0.0
    reac[XD5] = 0.0

    # differential equations:
    if kla >= 0.0:
        dy[SO2] = 1.0 / volume * (y_in[Q] * (y_in[SO2] - y[SO2])) + reac[SO2] + kla_temp * (sosat_temp - y[SO2])
    dy[1:13] = 1.0 / volume * (y_in[Q] * (y_in[1:13] - y[1:13])) + reac[1:13]

    if tempmodel:
        dy[TEMP] = 1.0 / volume * (y_in[13] * (y_in[TEMP] - y[TEMP]))

    if activate:
        dy[15:20] = 1.0 / volume * (y_in[13] * (y_in[15:20] - y[15:20]))

    return dy


class ASM3reactor:
    def __init__(self, asm3par, y0, kla, volume, carb, csourceconc, tempmodel, activate):
        """
        Parameters
        ----------
        asm3par : np.ndarray
            37 parameters needed for ASM3 equations

        y0 : np.ndarray
            Initial values for the 20 components (13 ASM3 components, Q, T and 5 dummy states)

        kla : int
            Oxygen transfer coefficient in aerated reactors

        volume : int
            Volume of the reactor

        carb : int
            external carbon flow rates for carbon addition to a reator

        csourceconc : int
            external carbon source concentration

        tempmodel : bool
            If true, mass balance for the wastewater temperature is used in process rates,
            otherwise influent wastewater temperature is just passed through process reactors

        activate : bool
            If true, dummy states are activated, otherwise dummy states are activated
        """

        self.asm3par = asm3par
        self.y0 = y0
        self.kla = kla
        self.volume = volume
        # self.sosat = sosat      # kann man das vllt rausschmeißen? nimmt man eh nie
        self.carb = carb
        self.csourceconc = csourceconc
        self.tempmodel = tempmodel
        self.activate = activate

    def carbonaddition(self, y_in):
        """Returns the reactor inlet concentrations after adding an external carbon source.

        Parameters:
        ----------
        y_in : np.ndarray
            Reactor inlet concentrations of the 20 components (13 ASM3 components, Q, T and 5 dummy states) before adding external carbon source.

        Returns
        -------
        np.ndarray
            Array containing the reactor inlet concentrations of the 20 components (13 ASM3 components, Q, T and 5 dummy states) after adding external carbon source
        """

        y_in[SO2] = (y_in[SO2] * y_in[Q]) / (self.carb + y_in[Q])
        y_in[SI] = (y_in[SI] * y_in[Q] + self.csourceconc * self.carb) / (self.carb + y_in[Q])
        y_in[2:13] = (y_in[2:13] * y_in[Q]) / (self.carb + y_in[Q])
        y_in[14:20] = (y_in[14:20] * y_in[Q]) / (self.carb + y_in[Q])
        y_in[Q] = self.carb + y_in[Q]

        return y_in

    def output(self, timestep, step, y_in):
        """Returns the solved differential equations of ASM3 model.

        Parameters
        ----------
        timestep : int or float
            Size of integration interval in days
        step : int or float
            Upper boundary for integration interval in days
        y_in : np.ndarray
            Reactor inlet concentrations of the 20 components (13 ASM3 components, Q, T and 5 dummy states)

        Returns
        -------
        np.ndarray
            Array containing the concentrations of the 20 components at the current time step after the integration
        """

        k_H, K_X, k_STO, ny_NOX, K_O2, K_NOX, K_S, K_STO, mu_H, K_NH4, K_ALK, b_HO2, b_HNOX, b_STOO2, b_STONOX, mu_A, K_ANH4, K_AO2, K_AALK, b_AO2, b_ANOX, f_SI, Y_STOO2, Y_STONOX, Y_HO2, Y_HNOX, Y_A, f_XI, i_NSI, i_NSS, i_NXI, i_NXS, i_NBM, i_SSXI, i_SSXS, i_SSBM, i_SSSTO = self.asm3par
        y_out = np.zeros(24)
        t_eval = np.array([step, step + timestep])  # time interval for odeint

        if self.carb > 0.0:
            y_in = self.carbonaddition(y_in)
        ode = odeint(derivatives, self.y0, t_eval, tfirst=True,
                     args=(y_in, self.asm3par, self.kla, self.volume, self.tempmodel, self.activate,),
                     rtol=1e-5, atol=1e-8)
        y_out[0:20] = ode[1]

        y_out[Q] = y_in[Q]  # Flow
        if not self.tempmodel:
            y_out[TEMP] = y_in[TEMP]  # Temperature

        y_out[COD] = - y_out[SO2] + y_out[SI] + y_out[SS] - 1.71 * y_out[SN2] - 4.57 * y_out[SNOX] + y_out[XI] +\
                     y_out[XS] + y_out[XH] + y_out[XSTO] + y_out[XA]
        y_out[N2] = i_NSI * y_out[SI] + i_NSS * y_out[SS] + y_out[SNH4] + y_out[SN2] + y_out[SNOX] + i_NXI * y_out[XI]\
                    + i_NXS * y_out[XS] + i_NBM * y_out[XH] + i_NBM * y_out[XA]
        y_out[ION] = 1/14 * y_out[SNH4] - 1/14 * y_out[SNOX] - y_out[SALK]
        y_out[TSS] = i_SSXI * y_out[XI] + i_SSXS * y_out[XS] + i_SSBM * y_out[XH] + 0.6 * y_out[XSTO] + i_SSBM *\
                     y_out[XA]

        self.y0 = y_out[0:20]

        return y_out

