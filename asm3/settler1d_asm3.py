import numpy as np
from scipy.integrate import odeint
from numba import jit
import asm3init


indices_components = np.arange(20)
SO2, SI, SS, SNH4, SN2, SNOX, SALK, XI, XS, XH, XSTO, XA, XTSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components


@jit(nopython=True)
def derivativess(t, ys, ys_in, sedpar, dim, layer, Qr, Qw, tempmodel):
    """Returns an array containing the differential equations of a non-reactive sedimentation tank with ten layers, which is compatible with ASM3 model

    Parameters
    ----------
    t : np.ndarray
        Time interval for integration, needed for the solver
    ys : np.ndarray
        Solution of the differential equations, needed for the solver
    ys_in : np.ndarray
        Settler inlet concentrations of the 20 components (13 ASM3 components, Q, T and 5 dummy states)
    sedpar : np.ndarray
        6 parameters needed for settler equations
    dim : np.ndarray
        Dimensions of the settler, area and height
    layer : np.ndarray
        Feedlayer and number of layers in the settler
    Qr : int
        Return sludge flow rate
    Qw : int
        flow rate of waste sludge
    tempmodel : bool
        If true, differential equation for the wastewater temperature is used,
        otherwise influent wastewater temperature is just passed through the settler

    Returns
    -------
    np.ndarray
        Array containing the differential equations of settling model with certain number of layers
    """

    area = dim[0]
    feedlayer = layer[0]
    nooflayers = layer[1]
    h = dim[1] / nooflayers
    volume = area * dim[1]

    vs = np.zeros(nooflayers)
    Js = np.zeros(nooflayers+1)
    Js_temp = np.zeros(nooflayers)

    dys = np.zeros(19*nooflayers)   # differential equations only for soluble components, TSS and Temperature
    Jflow = np.zeros(1 + nooflayers)

    eps = 0.01
    v_in = ys_in[Q] / area
    Q_f = ys_in[Q]
    Q_u = Qr + Qw
    Q_e = ys_in[Q] - Q_u
    v_up = Q_e / area
    v_dn = Q_u / area

    ystemp = ys
    ystemp[ystemp < 0.0] = 0.00001
    ys[ys < 0.0] = 0.00001

    # sedimentation velocity for each of the layers:
    for i in range(nooflayers):
        vs[i] = sedpar[1] * (np.exp(-sedpar[2] * (ystemp[i + XTSS * nooflayers] - sedpar[4] * ys_in[XTSS])) - np.exp(
            -sedpar[3] * (ystemp[i + XTSS * nooflayers] - sedpar[4] * ys_in[XTSS])))
        vs[vs > sedpar[0]] = sedpar[0]
        vs[vs < 0.0] = 0.0

    # sludge flux due to sedimentation for each layer (not taking into account X limit)
    for i in range(nooflayers):
        Js_temp[i] = vs[i] * ystemp[i + XTSS * nooflayers]

    # sludge flux due to the liquid flow (upflow or downflow, depending on layer)
    for i in range(1 + nooflayers):
        if i < (feedlayer - eps):
            Jflow[i] = v_up * ystemp[i + XTSS * nooflayers]
        else:
            Jflow[i] = v_dn * ystemp[i - 1 + XTSS * nooflayers]

    # sludge flux due to sedimentation of each layer:
    for i in range(nooflayers-1):
        if i < (feedlayer - 1 - eps) and ystemp[i + 1 + XTSS * nooflayers] <= sedpar[5]:
            Js[i + 1] = Js_temp[i]
        elif Js_temp[i] < Js_temp[i + 1]:
            Js[i + 1] = Js_temp[i]
        else:
            Js[i + 1] = Js_temp[i + 1]

    # soluble component S_O:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i] = (-v_up * ystemp[i] + v_up * ystemp[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i] = (v_dn * ystemp[i - 1] - v_dn * ystemp[i]) / h
        else:
            dys[i] = (v_in * ys_in[SO2] - v_up * ystemp[i] - v_dn * ystemp[i]) / h

    # soluble component S_I:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + nooflayers] = (-v_up * ystemp[i + nooflayers] + v_up * ystemp[i + 1 + nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + nooflayers] = (v_dn * ystemp[i - 1 + nooflayers] - v_dn * ystemp[i + nooflayers]) / h
        else:
            dys[i + nooflayers] = (v_in * ys_in[SI] - v_up * ystemp[i + nooflayers] - v_dn * ystemp[i + nooflayers]) / h

    # soluble component S_S:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 2*nooflayers] = (-v_up * ystemp[i + 2*nooflayers] + v_up * ystemp[i + 1 + 2*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 2*nooflayers] = (v_dn * ystemp[i - 1 + 2*nooflayers] - v_dn * ystemp[i + 2*nooflayers]) / h
        else:
            dys[i + 2*nooflayers] = (v_in * ys_in[SS] - v_up * ystemp[i + 2*nooflayers] - v_dn * ystemp[i + 2*nooflayers]) / h

    # soluble component S_NH4:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 3*nooflayers] = (-v_up * ystemp[i + 3*nooflayers] + v_up * ystemp[i + 1 + 3*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 3*nooflayers] = (v_dn * ystemp[i - 1 + 3*nooflayers] - v_dn * ystemp[i + 3*nooflayers]) / h
        else:
            dys[i + 3*nooflayers] = (v_in * ys_in[SNH4] - v_up * ystemp[i + 3*nooflayers] - v_dn * ystemp[i + 3*nooflayers]) / h

    # soluble component S_N2:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 4*nooflayers] = (-v_up * ystemp[i + 4*nooflayers] + v_up * ystemp[i + 1 + 4*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 4*nooflayers] = (v_dn * ystemp[i - 1 + 4*nooflayers] - v_dn * ystemp[i + 4*nooflayers]) / h
        else:
            dys[i + 4*nooflayers] = (v_in * ys_in[SN2] - v_up * ystemp[i + 4*nooflayers] - v_dn * ystemp[i + 4*nooflayers]) / h

    # soluble component S_NOX:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 5*nooflayers] = (-v_up * ystemp[i + 5*nooflayers] + v_up * ystemp[i + 1 + 5*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 5*nooflayers] = (v_dn * ystemp[i - 1 + 5*nooflayers] - v_dn * ystemp[i + 5*nooflayers]) / h
        else:
            dys[i + 5*nooflayers] = (v_in * ys_in[SNOX] - v_up * ystemp[i + 5*nooflayers] - v_dn * ystemp[i + 5*nooflayers]) / h

    # soluble component S_ALK:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 6*nooflayers] = (-v_up * ystemp[i + 6*nooflayers] + v_up * ystemp[i + 1 + 6*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 6*nooflayers] = (v_dn * ystemp[i - 1 + 6*nooflayers] - v_dn * ystemp[i + 6*nooflayers]) / h
        else:
            dys[i + 6*nooflayers] = (v_in * ys_in[SALK] - v_up * ystemp[i + 6*nooflayers] - v_dn * ystemp[i + 6*nooflayers]) / h

    # particulate component X_I:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 7*nooflayers] = ((ystemp[i + 7*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Js[i + 1]) + (
                    ystemp[i - 1 + 7*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + (ystemp[i + 1 + 7*nooflayers] / ystemp[i + 1 + 12*nooflayers]) *
                           Jflow[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i + 7*nooflayers] = ((ystemp[i + 7*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 7*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * (Jflow[i] + Js[i])) / h
        else:
            dys[i + 7*nooflayers] = ((ystemp[i + 7*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 7*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + v_in * ys_in[XI]) / h

    # particulate component X_S:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 8*nooflayers] = ((ystemp[i + 8*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Js[i + 1]) + (
                    ystemp[i - 1 + 8*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + (ystemp[i + 1 + 8*nooflayers] / ystemp[i + 1 + 12*nooflayers]) *
                           Jflow[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i + 8*nooflayers] = ((ystemp[i + 8*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 8*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * (Jflow[i] + Js[i])) / h
        else:
            dys[i + 8*nooflayers] = ((ystemp[i + 8*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 8*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + v_in * ys_in[XS]) / h

    # particulate component X_H:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 9*nooflayers] = ((ystemp[i + 9*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Js[i + 1]) + (
                    ystemp[i - 1 + 9*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + (ystemp[i + 1 + 9*nooflayers] / ystemp[i + 1 + 12*nooflayers]) *
                           Jflow[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i + 9*nooflayers] = ((ystemp[i + 9*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 9*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * (Jflow[i] + Js[i])) / h
        else:
            dys[i + 9*nooflayers] = ((ystemp[i + 9*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 9*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + v_in * ys_in[XH]) / h

    # particulate component X_STO:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 10*nooflayers] = ((ystemp[i + 10*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Js[i + 1]) + (
                    ystemp[i - 1 + 10*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + (
                                       ystemp[i + 1 + 10*nooflayers] / ystemp[i + 1 + 12*nooflayers]) *
                           Jflow[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i + 10*nooflayers] = ((ystemp[i + 10*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 10*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * (Jflow[i] + Js[i])) / h
        else:
            dys[i + 10*nooflayers] = ((ystemp[i + 10*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 10*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + v_in * ys_in[XSTO]) / h

    # particulate component X_A:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 11*nooflayers] = ((ystemp[i + 11*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Js[i + 1]) + (
                    ystemp[i - 1 + 11*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + (ystemp[i + 1 + 11*nooflayers] / ystemp[i + 1 + 12*nooflayers]) *
                           Jflow[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i + 11*nooflayers] = ((ystemp[i + 11*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 11*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * (Jflow[i] + Js[i])) / h
        else:
            dys[i + 11*nooflayers] = ((ystemp[i + 11*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 11*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + v_in * ys_in[XA]) / h

    # particulate component X_TSS:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 12*nooflayers] = ((-Jflow[i] - Js[i + 1]) + Js[i] + Jflow[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i + 12*nooflayers] = ((-Jflow[i + 1] - Js[i + 1]) + (Jflow[i] + Js[i])) / h
        else:
            dys[i + 12*nooflayers] = ((-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + Js[i] + v_in * ys_in[XTSS]) / h

    # Temperature:
    if tempmodel:
        for i in range(nooflayers):
            if i < (feedlayer - 1 - eps):
                dys[i + 13*nooflayers] = (-v_up * ystemp[i + 13*nooflayers] + v_up * ystemp[i + 1 + 13*nooflayers]) / h
            elif i > (feedlayer - eps):
                dys[i + 13*nooflayers] = (v_dn * ystemp[i - 1 + 13*nooflayers] - v_dn * ystemp[i + 13*nooflayers]) / h
            else:
                dys[i + 13*nooflayers] = (v_in * ys_in[TEMP] - v_up * ystemp[i + 13*nooflayers] - v_dn * ystemp[i + 13*nooflayers]) / h

    # soluble component S_D1:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 14*nooflayers] = (-v_up * ystemp[i + 14*nooflayers] + v_up * ystemp[i + 1 + 14*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 14*nooflayers] = (v_dn * ystemp[i - 1 + 14*nooflayers] - v_dn * ystemp[i + 14*nooflayers]) / h
        else:
            dys[i + 14*nooflayers] = (v_in * ys_in[SD1] - v_up * ystemp[i + 14*nooflayers] - v_dn * ystemp[i + 14*nooflayers]) / h

    # soluble component S_D2:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 15*nooflayers] = (-v_up * ystemp[i + 15*nooflayers] + v_up * ystemp[i + 1 + 15*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 15*nooflayers] = (v_dn * ystemp[i - 1 + 15*nooflayers] - v_dn * ystemp[i + 15*nooflayers]) / h
        else:
            dys[i + 15*nooflayers] = (v_in * ys_in[SD2] - v_up * ystemp[i + 15*nooflayers] - v_dn * ystemp[i + 15*nooflayers]) / h

    # soluble component S_D3:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 16*nooflayers] = (-v_up * ystemp[i + 16*nooflayers] + v_up * ystemp[i + 1 + 16*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 16*nooflayers] = (v_dn * ystemp[i - 1 + 16*nooflayers] - v_dn * ystemp[i + 16*nooflayers]) / h
        else:
            dys[i + 16*nooflayers] = (v_in * ys_in[SD3] - v_up * ystemp[i + 16*nooflayers] - v_dn * ystemp[i + 16*nooflayers]) / h

    # particulate component X_D4:
    dys[17*nooflayers] = ((ys[17*nooflayers] / ys[12*nooflayers]) * (-Jflow[0] - Js[1]) + (ys[1 + 17*nooflayers] / ys[1 + 12*nooflayers]) * Jflow[1]) / h
    for i in range(1, nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 17*nooflayers] = ((ystemp[i + 17*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Js[i + 1]) + (
                    ystemp[i - 1 + 17*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + (
                                        ystemp[i + 1 + 17*nooflayers] / ystemp[i + 1 + 12*nooflayers]) *
                            Jflow[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i + 17*nooflayers] = ((ystemp[i + 17*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 17*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * (Jflow[i] + Js[i])) / h
        else:
            dys[i + 17*nooflayers] = ((ystemp[i + 17*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 17*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + v_in * ys_in[XD4]) / h

    # particulate component X_D5:
    dys[18*nooflayers] = ((ys[18*nooflayers] / ys[12*nooflayers]) * (-Jflow[0] - Js[1]) + (ys[1 + 18*nooflayers] / ys[1 + 12*nooflayers]) * Jflow[1]) / h
    for i in range(1, nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 18*nooflayers] = ((ystemp[i + 18*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Js[i + 1]) + (
                    ystemp[i - 1 + 18*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + (ystemp[i + 1 + 18*nooflayers] / ystemp[i + 1 + 12*nooflayers]) *
                            Jflow[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i + 18*nooflayers] = ((ystemp[i + 18*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 18*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * (Jflow[i] + Js[i])) / h
        else:
            dys[i + 18*nooflayers] = ((ystemp[i + 18*nooflayers] / ystemp[i + 12*nooflayers]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                    ystemp[i - 1 + 18*nooflayers] / ystemp[i - 1 + 12*nooflayers]) * Js[i] + v_in * ys_in[XD5]) / h

    return dys


class Settler:
    def __init__(self, dim, layer, Qr, Qw, ys0, sedpar, asm3par, tempmodel):
        """
        Parameters
        ----------
        dim : np.ndarray
            Dimensions of the settler, area and height
        layer : np.ndarray
            Feedlayer and number of layers in the settler
        Qr : int
            Return sludge flow rate
        Qw : int
            flow rate of waste sludge
        ys0 : np.ndarray
            Initial values for the 19 components (without Q) for each layer, sorted by components
        sedpar : np.ndarray
            6 parameters needed for settler equations
        asm3par : np.ndarray
            37 parameters needed for ASM3 equations
        tempmodel : bool
            If true, differential equation for the wastewater temperature is used,
            otherwise influent wastewater temperature is just passed through the settler
        """

        self.dim = dim
        self.layer = layer
        self.Qr = Qr
        self.Qw = Qw
        self.ys0 = ys0
        self.sedpar = sedpar
        self.asm3par = asm3par
        self.tempmodel = tempmodel

    def outputs(self, timestep, step, ys_in):
        """Returns the solved differential equations of settling model.

        Parameters
        ----------
        timestep : int or float
            Size of integration interval in days
        step : int or float
            Upper boundary for integration interval in days
        ys_in : np.ndarray
            Settler inlet concentrations of the 20 components (13 ASM3 components, Q, T and 5 dummy states)

        Returns
        -------
        (np.ndarray, np.ndarray)
            Tuple containing three array:
                ys_out: Array containing the values of the 20 components (13 ASM3 components, Q, T and 5 dummy states)
                in the effluent (top layer of settler) at the current time step after the integration
                ys_eff: Array containing the values of the 20 components (13 ASM3 components, Q, T and 5 dummy states)
                in the underflow (bottom layer of settler) at the current time step after the integration
        """

        nooflayers = self.layer[1]
        ys_out_all = np.zeros(13 + 19*nooflayers)
        ys_out = np.zeros(20)
        ys_eff = np.zeros(24)
        t_eval = np.array([step, step + timestep])
        odes = derivativess(t_eval[0], self.ys0, ys_in, self.sedpar, self.dim, self.layer, self.Qr, self.Qw, self.tempmodel)
        odes = odeint(derivativess, self.ys0, t_eval, tfirst=True, args=(ys_in, self.sedpar, self.dim, self.layer, self.Qr, self.Qw, self.tempmodel))
        ys_int = odes[1]

        self.ys0 = ys_int

        for i in range(nooflayers):
            for j in range(19):
                ys_out_all[(i * 19) + j] = ys_int[i + j * nooflayers]
            if not self.tempmodel:
                ys_out_all[(i * 19) + 13] = ys_in[14]

        # flow rates out of the clarifier:
        ys_out_all[0 + 19*nooflayers] = ys_in[13] - self.Qr - self.Qw
        ys_out_all[1 + 19*nooflayers] = self.Qr
        ys_out_all[2 + 19*nooflayers] = self.Qw

        # underflow:
        ys_out[0:13] = ys_out_all[19*nooflayers - 19 : 19*nooflayers - 6]
        ys_out[13] = self.Qr
        ys_out[14:20] = ys_out_all[19*nooflayers - 6 : 19*nooflayers]

        # effluent:
        ys_eff[0:13] = ys_out_all[0:13]
        ys_eff[13] = ys_out_all[19*nooflayers]
        ys_eff[14:20] = ys_out_all[13:19]
        # additional values to compare:
        # Kjeldahl N concentration:
        # SNHeav + i_NSI*(SIeav) + i_NSS*(SSeav) + i_NXI*(XIeav) + i_NXS*(XSeav) + i_NBM*( XBHeav + XBAeav))
        ys_eff[20] = ys_eff[SNH4] + self.asm3par[28]*ys_eff[SI] + self.asm3par[29]*ys_eff[SS] + self.asm3par[30]*ys_eff[XI] + self.asm3par[31]*ys_eff[XS] + self.asm3par[32]*(ys_eff[XH] + ys_eff[XA])
        # total N concentration:
        # SNOeav + SNHeav+ i_NSI*(SIeav) + i_NSS*(SSeav) + i_NXI*(XIeav) + i_NXS*(XSeav) + i_NBM*( XBHeav + XBAeav))
        ys_eff[21] = ys_eff[20] + ys_eff[SNOX]
        # total COD concentration:
        # SIeav+SSeav+XIeav+XSeav+XBHeav+XBAeav+XSTOeav
        ys_eff[22] = ys_eff[SI] + ys_eff[SS] + ys_eff[XI] + ys_eff[XS] + ys_eff[XH] + ys_eff[XA] + ys_eff[XSTO]
        # BOD5 concentration:
        # 0.65*(SSeav+XSeav+(1-f_P)*(XBHeav+XBAeav + XBAeav))
        ys_eff[23] = 0.65 * (ys_eff[SS] + ys_eff[XS] + (1-asm3init.f_P)*(ys_eff[XH] + ys_eff[XA] + ys_eff[XSTO]))
        return ys_out, ys_eff
