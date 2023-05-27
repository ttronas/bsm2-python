import numpy as np
from scipy.integrate import odeint
from numba import jit


indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components


@jit(nopython=True)
def settlerequations(t, ys, ys_in, sedpar, dim, layer, Qr, Qw, tempmodel):
    """Returns an array containing the differential equations of a non-reactive sedimentation tank with variable number of layers (default model is 10 layers), which is compatible with ASM1 model

    Parameters
    ----------
    t : np.ndarray
        Time interval for integration, needed for the solver
    ys : np.ndarray
        Solution of the differential equations, needed for the solver
    ys_in : np.ndarray
        Settler inlet concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
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

    dys = np.zeros(12*nooflayers)   # differential equations only for soluble components, TSS and Temperature

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
        vs[i] = sedpar[1] * (np.exp(-sedpar[2] * (ystemp[i + 7 * nooflayers] - sedpar[4] * ys_in[TSS])) - np.exp(
            -sedpar[3] * (ystemp[i + 7 * nooflayers] - sedpar[4] * ys_in[TSS])))  # ystemp[i+7*nooflayers] is TSS
        vs[vs > sedpar[0]] = sedpar[0]
        vs[vs < 0.0] = 0.0

    # sludge flux due to sedimentation for each layer (not taking into account X limit)
    for i in range(nooflayers):
        Js_temp[i] = vs[i] * ystemp[i + 7 * nooflayers]

    # sludge flux due to sedimentation of each layer:
    for i in range(nooflayers-1):
        if i < (feedlayer - 1 - eps) and ystemp[i + 1 + 7*nooflayers] <= sedpar[5]:
            Js[i + 1] = Js_temp[i]
        elif Js_temp[i] < Js_temp[i + 1]:
            Js[i + 1] = Js_temp[i]
        else:
            Js[i + 1] = Js_temp[i + 1]

    # differential equations:
    # soluble component S_I:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i] = (-v_up * ystemp[i] + v_up * ystemp[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i] = (v_dn * ystemp[i - 1] - v_dn * ystemp[i]) / h
        else:
            dys[i] = (v_in * ys_in[SI] - v_up * ystemp[i] - v_dn * ystemp[i]) / h

    # soluble component S_S:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + nooflayers] = (-v_up * ystemp[i + nooflayers] + v_up * ystemp[i + 1 + nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + nooflayers] = (v_dn * ystemp[i - 1 + nooflayers] - v_dn * ystemp[i + nooflayers]) / h
        else:
            dys[i + nooflayers] = (v_in * ys_in[SS] - v_up * ystemp[i + nooflayers] - v_dn * ystemp[i + nooflayers]) / h

    # soluble component S_O:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 2*nooflayers] = (-v_up * ystemp[i + 2*nooflayers] + v_up * ystemp[i + 1 + 2*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 2*nooflayers] = (v_dn * ystemp[i - 1 + 2*nooflayers] - v_dn * ystemp[i + 2*nooflayers]) / h
        else:
            dys[i + 2*nooflayers] = (v_in * ys_in[SO] - v_up * ystemp[i + 2*nooflayers] - v_dn * ystemp[i + 2*nooflayers]) / h

    # soluble component S_NO:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 3*nooflayers] = (-v_up * ystemp[i + 3*nooflayers] + v_up * ystemp[i + 1 + 3*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 3*nooflayers] = (v_dn * ystemp[i - 1 + 3*nooflayers] - v_dn * ystemp[i + 3*nooflayers]) / h
        else:
            dys[i + 3*nooflayers] = (v_in * ys_in[SNO] - v_up * ystemp[i + 3*nooflayers] - v_dn * ystemp[i + 3*nooflayers]) / h

    # soluble component S_NH:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 4*nooflayers] = (-v_up * ystemp[i + 4*nooflayers] + v_up * ystemp[i + 1 + 4*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 4*nooflayers] = (v_dn * ystemp[i - 1 + 4*nooflayers] - v_dn * ystemp[i + 4*nooflayers]) / h
        else:
            dys[i + 4*nooflayers] = (v_in * ys_in[SNH] - v_up * ystemp[i + 4*nooflayers] - v_dn * ystemp[i + 4*nooflayers]) / h

    # soluble component S_ND:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 5*nooflayers] = (-v_up * ystemp[i + 5*nooflayers] + v_up * ystemp[i + 1 + 5*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 5*nooflayers] = (v_dn * ystemp[i - 1 + 5*nooflayers] - v_dn * ystemp[i + 5*nooflayers]) / h
        else:
            dys[i + 5*nooflayers] = (v_in * ys_in[SND] - v_up * ystemp[i + 5*nooflayers] - v_dn * ystemp[i + 5*nooflayers]) / h

    # soluble component S_ALK:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 6*nooflayers] = (-v_up * ystemp[i + 6*nooflayers] + v_up * ystemp[i + 1 + 6*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 6*nooflayers] = (v_dn * ystemp[i - 1 + 6*nooflayers] - v_dn * ystemp[i + 6*nooflayers]) / h
        else:
            dys[i + 6*nooflayers] = (v_in * ys_in[SALK] - v_up * ystemp[i + 6*nooflayers] - v_dn * ystemp[i + 6*nooflayers]) / h

    # particulate component X_TSS:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 7*nooflayers] = ((-v_up * ystemp[i + 7*nooflayers] + v_up * ystemp[i + 1 + 7*nooflayers] - Js[i + 1]) + Js[i]) / h
        elif i > (feedlayer - eps):
            dys[i + 7*nooflayers] = (v_dn * ystemp[i - 1 + 7*nooflayers] - v_dn * ystemp[i + 7*nooflayers] - Js[i + 1] + Js[i]) / h
        else:
            dys[i + 7*nooflayers] = (v_in * ys_in[TSS] - v_up * ystemp[i + 7*nooflayers] - v_dn * ystemp[i + 7*nooflayers] - Js[i + 1] + Js[i]) / h

    # Temperature:
    if tempmodel:
        for i in range(nooflayers):
            if i < (feedlayer - 1 - eps):
                dys[i + 8*nooflayers] = (-v_up * ystemp[i + 8*nooflayers] + v_up * ystemp[i + 1 + 8*nooflayers]) / h
            elif i > (feedlayer - eps):
                dys[i + 8*nooflayers] = (v_dn * ystemp[i - 1 + 8*nooflayers] - v_dn * ystemp[i + 8*nooflayers]) / h
            else:
                dys[i + 8*nooflayers] = (v_in * ys_in[TEMP] - v_up * ystemp[i + 8*nooflayers] - v_dn * ystemp[i + 8*nooflayers]) / h

    # soluble component S_D1:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 9*nooflayers] = (-v_up * ystemp[i + 9*nooflayers] + v_up * ystemp[i + 1 + 9*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 9*nooflayers] = (v_dn * ystemp[i - 1 + 9*nooflayers] - v_dn * ystemp[i + 9*nooflayers]) / h
        else:
            dys[i + 9*nooflayers] = (v_in * ys_in[SD1] - v_up * ystemp[i + 9*nooflayers] - v_dn * ystemp[i + 9*nooflayers]) / h

    # soluble component S_D2:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 10*nooflayers] = (-v_up * ystemp[i + 10*nooflayers] + v_up * ystemp[i + 1 + 10*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 10*nooflayers] = (v_dn * ystemp[i - 1 + 10*nooflayers] - v_dn * ystemp[i + 10*nooflayers]) / h
        else:
            dys[i + 10*nooflayers] = (v_in * ys_in[SD2] - v_up * ystemp[i + 10*nooflayers] - v_dn * ystemp[i + 10*nooflayers]) / h

    # soluble component S_D3:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 11*nooflayers] = (-v_up * ystemp[i + 11*nooflayers] + v_up * ystemp[i + 1 + 11*nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i + 11*nooflayers] = (v_dn * ystemp[i - 1 + 11*nooflayers] - v_dn * ystemp[i + 11*nooflayers]) / h
        else:
            dys[i + 11*nooflayers] = (v_in * ys_in[SD3] - v_up * ystemp[i + 11*nooflayers] - v_dn * ystemp[i + 11*nooflayers]) / h

    return dys


class Settler:
    def __init__(self, dim, layer, Qr, Qw, ys0, sedpar, asm1par, tempmodel):
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
            Initial values for the 12 components (without Q and particulates) for each layer, sorted by components
        sedpar : np.ndarray
            6 parameters needed for settler equations
        asm1par : np.ndarray
            24 parameters needed for ASM1 equations
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
        self.asm1par = asm1par
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
            Settler inlet concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)

        Returns
        -------
        (np.ndarray, np.ndarray)
            Tuple containing three array:
                ys_out: Array containing the values of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
                in the effluent (top layer of settler) at the current time step after the integration
                ys_eff: Array containing the values of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
                in the underflow (bottom layer of settler) at the current time step after the integration
        """

        nooflayers = self.layer[1]
        ys_out = np.zeros(21)
        ys_eff = np.zeros(25)
        ys_TSS = np.zeros(nooflayers)
        t_eval = np.array([step, step + timestep])

        odes = odeint(settlerequations, self.ys0, t_eval, tfirst=True, args=(ys_in, self.sedpar, self.dim, self.layer, self.Qr, self.Qw, self.tempmodel))
        ys_int = odes[1]

        self.ys0 = ys_int

        # underflow
        ys_out[SI] = ys_int[nooflayers-1]
        ys_out[SS] = ys_int[2*nooflayers-1]
        ys_out[SO] = ys_int[3*nooflayers-1]
        ys_out[SNO] = ys_int[4*nooflayers-1]
        ys_out[SNH] = ys_int[5*nooflayers-1]
        ys_out[SND] = ys_int[6*nooflayers-1]
        ys_out[SALK] = ys_int[7*nooflayers-1]
        ys_out[TSS] = ys_int[8*nooflayers-1]
        if self.tempmodel:
            ys_out[TEMP] = ys_int[9*nooflayers-1]
        else:
            ys_out[TEMP] = ys_in[TEMP]
        ys_out[SD1] = ys_int[10*nooflayers-1]
        ys_out[SD2] = ys_int[11*nooflayers-1]
        ys_out[SD3] = ys_int[12*nooflayers-1]

        ys_out[XI] = ys_out[TSS] / ys_in[TSS] * ys_in[XI]
        ys_out[XS] = ys_out[TSS] / ys_in[TSS] * ys_in[XS]
        ys_out[XBH] = ys_out[TSS] / ys_in[TSS] * ys_in[XBH]
        ys_out[XBA] = ys_out[TSS] / ys_in[TSS] * ys_in[XBA]
        ys_out[XP] = ys_out[TSS] / ys_in[TSS] * ys_in[XP]
        ys_out[XND] = ys_out[TSS] / ys_in[TSS] * ys_in[XND]
        ys_out[XD4] = ys_out[TSS] / ys_in[TSS] * ys_in[XD4]
        ys_out[XD5] = ys_out[TSS] / ys_in[TSS] * ys_in[XD5]

        ys_out[Q] = self.Qr

        # effluent
        ys_eff[SI] = ys_int[0]
        ys_eff[SS] = ys_int[nooflayers]
        ys_eff[SO] = ys_int[2*nooflayers]
        ys_eff[SNO] = ys_int[3*nooflayers]
        ys_eff[SNH] = ys_int[4*nooflayers]
        ys_eff[SND] = ys_int[5*nooflayers]
        ys_eff[SALK] = ys_int[6*nooflayers]
        ys_eff[TSS] = ys_int[7*nooflayers]
        if self.tempmodel:
            ys_eff[TEMP] = ys_int[8*nooflayers]
        else:
            ys_eff[TEMP] = ys_in[TEMP]
        ys_eff[SD1] = ys_int[9*nooflayers]
        ys_eff[SD2] = ys_int[10*nooflayers]
        ys_eff[SD3] = ys_int[11*nooflayers]

        ys_eff[XI] = ys_eff[TSS] / ys_in[TSS] * ys_in[XI]
        ys_eff[XS] = ys_eff[TSS] / ys_in[TSS] * ys_in[XS]
        ys_eff[XBH] = ys_eff[TSS] / ys_in[TSS] * ys_in[XBH]
        ys_eff[XBA] = ys_eff[TSS] / ys_in[TSS] * ys_in[XBA]
        ys_eff[XP] = ys_eff[TSS] / ys_in[TSS] * ys_in[XP]
        ys_eff[XND] = ys_eff[TSS] / ys_in[TSS] * ys_in[XND]
        ys_eff[XD4] = ys_eff[TSS] / ys_in[TSS] * ys_in[XD4]
        ys_eff[XD5] = ys_eff[TSS] / ys_in[TSS] * ys_in[XD5]

        ys_eff[Q] = ys_in[Q] - self.Qw - self.Qr

        # additional values to compare:
        # Kjeldahl N concentration:
        ys_eff[21] = ys_eff[SNH] + ys_eff[SND] + ys_eff[XND] + self.asm1par[17] * (ys_eff[XBH] + ys_eff[XBA]) + self.asm1par[18] * (ys_eff[XP] + ys_eff[XI])
        # total N concentration:
        ys_eff[22] = ys_eff[21] + ys_eff[SNO]
        # total COD concentration:
        ys_eff[23] = ys_eff[SS] + ys_eff[SI] + ys_eff[XS] + ys_eff[XI] + ys_eff[XBH] + ys_eff[XBA] + ys_eff[XP]
        # BOD5 concentration:
        ys_eff[24] = 0.25 * (ys_eff[SS] + ys_eff[XS] + (1-self.asm1par[16]) * (ys_eff[XBH] + ys_eff[XBA]))

        return ys_out, ys_eff
