import numpy as np
from scipy.integrate import solve_ivp, odeint
from numba import jit, njit


indices_components = np.arange(24)
SO2, SI, SS, SNH4, SN2, SNOX, SALK, XI, XS, XH, XSTO, XA, XSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5, COD, N2, ION, TSS = indices_components


# differential equations in function because @jit does not compile class methods in nopython mode
@jit(nopython=True)
def derivativess(t, ys, ys_in, sedpar, dim, layer, Qr, Qw, tempmodel):
    """Returns an array containing the differential equations of a non-reactive sedimentation tank with variable number of layers (default model is 10 layers), which is compatible with ASM3 model

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
            If true, mass balance for the wastewater temperature is used in settler,
            otherwise influent wastewater temperature is just passed through settler

        Returns
        -------
        np.ndarray
            Array containing 120 differential equations of settling model with 10 layers

        """

    area = dim[0]
    feedlayer = layer[0]
    nooflayers = layer[1]
    h = dim[1] / nooflayers
    volume = area * dim[1]

    vs = np.zeros(nooflayers)
    Js = np.zeros(nooflayers+1)
    Js_temp = np.zeros(nooflayers)

    dys = np.zeros(12*nooflayers)        # only soluble components, XSS and Temperature

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

    # sedimentations velocity for each of the layers (Takacs, 1991):
    for i in range(nooflayers):

        vs[i] = sedpar[1] * (np.exp(-sedpar[2] * (ystemp[i + 7 * nooflayers] - sedpar[4] * ys_in[XSS])) - np.exp(
            -sedpar[3] * (ystemp[i + 7 * nooflayers] - sedpar[4] * ys_in[XSS])))
        vs[vs > sedpar[0]] = sedpar[0]
        vs[vs < 0.0] = 0.0


    # sludge flux due to sedimentation for each layer (not taking into account X limit)
    for i in range(nooflayers):
        Js_temp[i] = vs[i] * ystemp[i + 7*nooflayers]

    # sludge flux due to sedimentation of each layer:
    for i in range(nooflayers-1):
        if i < (feedlayer - 1 - eps) and ystemp[i + 1 + 7*nooflayers] <= sedpar[5]:
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
            dys[i+nooflayers] = (-v_up * ystemp[i+nooflayers] + v_up * ystemp[i + 1 + nooflayers]) / h
        elif i > (feedlayer - eps):
            dys[i+nooflayers] = (v_dn * ystemp[i - 1+nooflayers] - v_dn * ystemp[i+nooflayers]) / h
        else:
            dys[i+nooflayers] = (v_in * ys_in[SI] - v_up * ystemp[i+nooflayers] - v_dn * ystemp[i+nooflayers]) / h


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

    # particulate component X_SS:
    for i in range(nooflayers):
        if i < (feedlayer - 1 - eps):
            dys[i + 7*nooflayers] = (-v_up * ystemp[i + 7*nooflayers] + v_up * ystemp[i + 1 + 7*nooflayers] - Js[i + 1] + Js[i]) / h
        elif i > (feedlayer - eps):
            dys[i + 7*nooflayers] = (v_dn * ystemp[i - 1 + 7*nooflayers] - v_dn * ystemp[i + 7*nooflayers] - Js[i + 1] + Js[i]) / h
        else:
            dys[i + 7*nooflayers] = (v_in * ys_in[XSS] - v_up * ystemp[i + 7*nooflayers] - v_dn * ystemp[i + 7*nooflayers] - Js[i + 1] + Js[i]) / h

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
    def __init__(self, dim, layer, Qr, Qw, ys0, sedpar, tempmodel):
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
            Initial values for the 12 components (only soluble components, XSS and Temperature) for each layer, sorted by components

        sedpar : np.ndarray
            6 parameters needed for settler equations

        tempmodel : bool
            If true, mass balance for the wastewater temperature is used in settler,
            otherwise influent wastewater temperature is just passed through settler

        """

        self.dim = dim
        self.layer = layer
        self.Qr = Qr
        self.Qw = Qw
        self.ys0 = ys0
        self.sedpar = sedpar
        self.tempmodel = tempmodel

    def outputs(self, timestep, step, ys_in):

        nooflayers = self.layer[1]
        ys_out = np.zeros(20)
        ys_eff = np.zeros(24)
        t_eval = np.array([step, step + timestep])

        odes = odeint(derivativess, self.ys0, t_eval, tfirst=True, args=(ys_in, self.sedpar, self.dim, self.layer, self.Qr, self.Qw, self.tempmodel))
        ys_int = odes[1]

        self.ys0 = ys_int

        # underflow:
        ys_out[SO2] = ys_int[nooflayers - 1]
        ys_out[SI] = ys_int[2 * nooflayers - 1]
        ys_out[SS] = ys_int[3 * nooflayers - 1]
        ys_out[SNH4] = ys_int[4 * nooflayers - 1]
        ys_out[SN2] = ys_int[5 * nooflayers - 1]
        ys_out[SNOX] = ys_int[6 * nooflayers - 1]
        ys_out[SALK] = ys_int[7 * nooflayers - 1]
        ys_out[XSS] = ys_int[8 * nooflayers - 1]
        if self.tempmodel:
            ys_out[TEMP] = ys_int[9 * nooflayers - 1]
        else:
            ys_out[TEMP] = ys_in[TEMP]
        ys_out[SD1] = ys_int[10 * nooflayers - 1]
        ys_out[SD2] = ys_int[11 * nooflayers - 1]
        ys_out[SD3] = ys_int[12 * nooflayers - 1]

        ys_out[XI] = ys_out[XSS] / ys_in[XSS] * ys_in[XI]
        ys_out[XS] = ys_out[XSS] / ys_in[XSS] * ys_in[XS]
        ys_out[XH] = ys_out[XSS] / ys_in[XSS] * ys_in[XH]
        ys_out[XSTO] = ys_out[XSS] / ys_in[XSS] * ys_in[XSTO]
        ys_out[XA] = ys_out[XSS] / ys_in[XSS] * ys_in[XA]
        ys_out[XD4] = ys_out[XSS] / ys_in[XSS] * ys_in[XD4]
        ys_out[XD5] = ys_out[XSS] / ys_in[XSS] * ys_in[XD5]

        ys_out[Q] = self.Qr

        # effluent:
        ys_eff[SO2] = ys_int[0]
        ys_eff[SI] = ys_int[nooflayers]
        ys_eff[SS] = ys_int[2 * nooflayers]
        ys_eff[SNH4] = ys_int[3 * nooflayers]
        ys_eff[SN2] = ys_int[4 * nooflayers]
        ys_eff[SNOX] = ys_int[5 * nooflayers]
        ys_eff[SALK] = ys_int[6 * nooflayers]
        ys_eff[XSS] = ys_int[7 * nooflayers]
        if self.tempmodel:
            ys_eff[TEMP] = ys_int[8 * nooflayers]
        else:
            ys_eff[TEMP] = ys_in[TEMP]
        ys_eff[SD1] = ys_int[9 * nooflayers]
        ys_eff[SD2] = ys_int[10 * nooflayers]
        ys_eff[SD3] = ys_int[11 * nooflayers]

        ys_eff[XI] = ys_eff[XSS] / ys_in[XSS] * ys_in[XI]
        ys_eff[XS] = ys_eff[XSS] / ys_in[XSS] * ys_in[XS]
        ys_eff[XH] = ys_eff[XSS] / ys_in[XSS] * ys_in[XH]
        ys_eff[XSTO] = ys_eff[XSS] / ys_in[XSS] * ys_in[XSTO]
        ys_eff[XA] = ys_eff[XSS] / ys_in[XSS] * ys_in[XA]
        ys_eff[XD4] = ys_eff[XSS] / ys_in[XSS] * ys_in[XD4]
        ys_eff[XD5] = ys_eff[XSS] / ys_in[XSS] * ys_in[XD5]

        ys_eff[Q] = ys_in[Q] - self.Qw - self.Qr

        # ys_eff[COD] = - ys_eff[SO2] + ys_eff[SI] + ys_eff[SS] - 1.71 * ys_eff[SN2] - 4.57 * ys_eff[SNOX] + ys_eff[XI] + \
        #            ys_eff[XS] + ys_eff[XH] + ys_eff[XSTO] + ys_eff[XA]
        # ys_eff[N2] = 0.01 * ys_eff[SI] + 0.03 * ys_eff[SS] + ys_eff[SNH4] + ys_eff[SNOX] + 0.02 * ys_eff[XI] \
        #             + 0.04 * ys_eff[XS] + 0.07 * ys_eff[XH] + 0.07 * ys_eff[XA]  #+ ys_eff[SN2]
        # ys_eff[ION] = 1 / 14 * ys_eff[SNH4] - 1 / 14 * ys_eff[SNOX] - ys_eff[SALK]
        # ys_eff[TSS] = 0.75 * ys_eff[XI] + 0.75 * ys_eff[XS] + 0.90 * ys_eff[XH] + 0.6 * ys_eff[XSTO] + 0.90 * \
        #              ys_eff[XA]


        # for i in range(10):
        #     for j in range(12):
        #         ys_out_all[(i * 12) + j] = ys_int[i + j * 10]
        #     if not self.tempmodel:
        #         ys_out_all[(i * 12) + 8] = ys_in[14]
        #
        # # flow rates out of the clarifier:
        # ys_out_all[120] = ys_in[13] - self.Qr - self.Qw
        # ys_out_all[121] = self.Qr
        # ys_out_all[122] = self.Qw
        #
        # # underflow
        # ys_out[0:7] = ys_out_all[108:115]
        # ys_out[7:12] = ys_out_all[115] / ys_in[12] * ys_in[7:12]
        # ys_out[12] = ys_out_all[115]    # XSS
        # ys_out[13] = self.Qr
        # ys_out[14:18] = ys_out_all[116:120]
        # ys_out[18:20] = ys_out_all[115] / ys_in[12] * ys_in[18:20]
        #
        # # effluent:
        # ys_eff[0:7] = ys_out_all[0:7]      # soluble
        # ys_eff[7:12] = ys_out_all[7] / ys_in[12] * ys_in[7:12]    # particulate
        # ys_eff[12] = ys_out_all[7]  # XSS
        # ys_eff[13] = ys_in[13] - self.Qr - self.Qw
        # ys_eff[14:18] = ys_out_all[8:12]
        # ys_eff[18:20] = ys_out_all[7] / ys_in[12] * ys_in[18:20]

        return ys_out, ys_eff
