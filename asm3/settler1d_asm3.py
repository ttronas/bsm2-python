import numpy as np
from scipy.integrate import solve_ivp, odeint
from numba import jit, njit


# differential equations in function because @jit does not compile class methods in nopython mode
@jit(nopython=True)
def derivativess(t, ys, ys_in, sedpar, dim, layer, Qr, Qw, tempmodel):
    """Returns an array containing the differential equations of a non-reactive 10 layer sedimentation tank, which is compatible with ASM3 model

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

    indices_components = np.arange(20)
    SO2, SI, SS, SNH4, SN2, SNOX, SALK, XI, XS, XH, XSTO, XA, XSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components

    vs = np.zeros(10)
    Js = np.zeros(11)
    Js_temp = np.zeros(10)
    Jflow = np.zeros(11)

    dys = np.zeros(120)

    area = dim[0]
    feedlayer = layer[0]
    h = dim[1] / layer[1]
    volume = area * dim[1]

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
    for i in range(10):
        vs[i] = sedpar[1] * (np.exp(-sedpar[2] * (ystemp[i + 70] - sedpar[4] * ys_in[XSS])) - np.exp(
            -sedpar[3] * (ystemp[i + 70] - sedpar[4] * ys_in[XSS])))
        vs[vs > sedpar[0]] = sedpar[0]
        vs[vs < 0.0] = 0.0


    # sludge flux due to sedimentation for each layer (not taking into account X limit)
    for i in range(10):
        Js_temp[i] = vs[i] * ystemp[i + 70]

    # sludge flux due to the liquid flow (upflow or downflow, depending on layer)
    for i in range(11):
        if i < (feedlayer - eps):
            Jflow[i] = v_up * ystemp[i + 70]
        else:
            Jflow[i] = v_dn * ystemp[i - 1 + 70]

    # sludge flux due to sedimentation of each layer:
    for i in range(9):
        if i < (feedlayer - 1 - eps) and ystemp[i + 1 + 70] <= sedpar[5]:
            Js[i + 1] = Js_temp[i]
        elif Js_temp[i] < Js_temp[i + 1]:
            Js[i + 1] = Js_temp[i]
        else:
            Js[i + 1] = Js_temp[i + 1]

    # soluble component S_O:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i] = (-v_up * ystemp[i] + v_up * ystemp[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i] = (v_dn * ystemp[i - 1] - v_dn * ystemp[i]) / h
        else:
            dys[i] = (v_in * ys_in[SO2] - v_up * ystemp[i] - v_dn * ystemp[i]) / h


    # soluble component S_I:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i+10] = (-v_up * ystemp[i+10] + v_up * ystemp[i + 1+10]) / h
        elif i > (feedlayer - eps):
            dys[i+10] = (v_dn * ystemp[i - 1+10] - v_dn * ystemp[i+10]) / h
        else:
            dys[i+10] = (v_in * ys_in[SI] - v_up * ystemp[i+10] - v_dn * ystemp[i+10]) / h


    # soluble component S_S:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 20] = (-v_up * ystemp[i + 20] + v_up * ystemp[i + 1 + 20]) / h
        elif i > (feedlayer - eps):
            dys[i + 20] = (v_dn * ystemp[i - 1 + 20] - v_dn * ystemp[i + 20]) / h
        else:
            dys[i + 20] = (v_in * ys_in[SS] - v_up * ystemp[i + 20] - v_dn * ystemp[i + 20]) / h

    # soluble component S_NH4:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 30] = (-v_up * ystemp[i + 30] + v_up * ystemp[i + 1 + 30]) / h
        elif i > (feedlayer - eps):
            dys[i + 30] = (v_dn * ystemp[i - 1 + 30] - v_dn * ystemp[i + 30]) / h
        else:
            dys[i + 30] = (v_in * ys_in[SNH4] - v_up * ystemp[i + 30] - v_dn * ystemp[i + 30]) / h

    # soluble component S_N2:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 40] = (-v_up * ystemp[i + 40] + v_up * ystemp[i + 1 + 40]) / h
        elif i > (feedlayer - eps):
            dys[i + 40] = (v_dn * ystemp[i - 1 + 40] - v_dn * ystemp[i + 40]) / h
        else:
            dys[i + 40] = (v_in * ys_in[SN2] - v_up * ystemp[i + 40] - v_dn * ystemp[i + 40]) / h

    # soluble component S_NOX:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 50] = (-v_up * ystemp[i + 50] + v_up * ystemp[i + 1 + 50]) / h
        elif i > (feedlayer - eps):
            dys[i + 50] = (v_dn * ystemp[i - 1 + 50] - v_dn * ystemp[i + 50]) / h
        else:
            dys[i + 50] = (v_in * ys_in[SNOX] - v_up * ystemp[i + 50] - v_dn * ystemp[i + 50]) / h

    # soluble component S_ALK:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 60] = (-v_up * ystemp[i + 60] + v_up * ystemp[i + 1 + 60]) / h
        elif i > (feedlayer - eps):
            dys[i + 60] = (v_dn * ystemp[i - 1 + 60] - v_dn * ystemp[i + 60]) / h
        else:
            dys[i + 60] = (v_in * ys_in[SALK] - v_up * ystemp[i + 60] - v_dn * ystemp[i + 60]) / h

    # particulate component X_SS:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 70] = ((-Jflow[i] - Js[i + 1]) + Js[i] + Jflow[i + 1]) / h
        elif i > (feedlayer - eps):
            dys[i + 70] = ((-Jflow[i + 1] - Js[i + 1]) + (Jflow[i] + Js[i])) / h
        else:
            dys[i + 70] = ((-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + Js[i] + v_in * ys_in[XSS]) / h

    # Temperature:
    if tempmodel:
        for i in range(10):
            if i < (feedlayer - 1 - eps):
                dys[i + 80] = (-v_up * ystemp[i + 80] + v_up * ystemp[i + 1 + 80]) / h
            elif i > (feedlayer - eps):
                dys[i + 80] = (v_dn * ystemp[i - 1 + 80] - v_dn * ystemp[i + 80]) / h
            else:
                dys[i + 80] = (v_in * ys_in[TEMP] - v_up * ystemp[i + 80] - v_dn * ystemp[i + 80]) / h

    # soluble component S_D1:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 90] = (-v_up * ystemp[i + 90] + v_up * ystemp[i + 1 + 90]) / h
        elif i > (feedlayer - eps):
            dys[i + 90] = (v_dn * ystemp[i - 1 + 90] - v_dn * ystemp[i + 90]) / h
        else:
            dys[i + 90] = (v_in * ys_in[SD1] - v_up * ystemp[i + 90] - v_dn * ystemp[i + 90]) / h

    # soluble component S_D2:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 100] = (-v_up * ystemp[i + 100] + v_up * ystemp[i + 1 + 100]) / h
        elif i > (feedlayer - eps):
            dys[i + 100] = (v_dn * ystemp[i - 1 + 100] - v_dn * ystemp[i + 100]) / h
        else:
            dys[i + 100] = (v_in * ys_in[SD2] - v_up * ystemp[i + 100] - v_dn * ystemp[i + 100]) / h

    # soluble component S_D3:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 110] = (-v_up * ystemp[i + 110] + v_up * ystemp[i + 1 + 110]) / h
        elif i > (feedlayer - eps):
            dys[i + 110] = (v_dn * ystemp[i - 1 + 110] - v_dn * ystemp[i + 110]) / h
        else:
            dys[i + 110] = (v_in * ys_in[SD3] - v_up * ystemp[i + 110] - v_dn * ystemp[i + 110]) / h

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

        ys_out_all = np.zeros(123)
        ys_out = np.zeros(20)
        ys_eff = np.zeros(20)
        t_eval = np.array([step, step + timestep])

        odes = odeint(derivativess, self.ys0, t_eval, tfirst=True, args=(ys_in, self.sedpar, self.dim, self.layer, self.Qr, self.Qw, self.tempmodel), rtol=1e-5, atol=1e-8)
        ys_int = odes[1]

        self.ys0 = ys_int

        for i in range(10):
            for j in range(12):
                ys_out_all[(i * 12) + j] = ys_int[i + j * 10]
            if not self.tempmodel:
                ys_out_all[(i * 12) + 8] = ys_in[14]

        # flow rates out of the clarifier:
        ys_out_all[120] = ys_in[13] - self.Qr - self.Qw
        ys_out_all[121] = self.Qr
        ys_out_all[122] = self.Qw

        # underflow
        ys_out[0:7] = ys_out_all[108:115]
        ys_out[7:12] = ys_out_all[115] / ys_in[12] * ys_in[7:12]
        ys_out[12] = ys_out_all[115]    # XSS
        ys_out[13] = self.Qr
        ys_out[14:18] = ys_out_all[116:120]
        ys_out[18:20] = ys_out_all[115] / ys_in[12] * ys_in[18:20]

        # effluent:
        ys_eff[0:7] = ys_out_all[0:7]      # soluble
        ys_eff[7:12] = ys_out_all[7] / ys_in[12] * ys_in[7:12]    # particulate
        ys_eff[12] = ys_out_all[7]  # XSS
        ys_eff[13] = ys_in[13] - self.Qr - self.Qw
        ys_eff[14:18] = ys_out_all[8:12]
        ys_eff[18:20] = ys_out_all[7] / ys_in[12] * ys_in[18:20]

        return ys_out, ys_eff
