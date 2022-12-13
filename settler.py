import numpy as np
import math
from scipy.integrate import solve_ivp, odeint
from numba import jit, njit


# differential equations in function because @jit does not compile class methods in nopython mode
@jit(nopython=True)
def derivatives_function(t, y, y_in, parset, dim, layer, Qr, Qw):
    # S_I_in, S_S_in, X_I_in, X_S_in, X_BH_in, X_BA_in, X_P_in, S_O_in, S_NO_in, S_NH_in, S_ND_in, X_ND_in, S_ALK_in, TSS_in, Q_in, T_in, S_D1_in, S_D2_in, S_D3_in, X_D4_in, X_D5_in = y_in
    # v0_max, v0, r_h, r_p, f_ns, X_t = parset

    vs = np.zeros(10)
    Js = np.zeros(11)
    Js_temp = np.zeros(10)
    Jflow = np.zeros(11)

    reac1 = np.zeros(10)
    reac2 = np.zeros(10)
    reac3 = np.zeros(10)
    reac4 = np.zeros(10)
    reac5 = np.zeros(10)
    reac6 = np.zeros(10)
    reac7 = np.zeros(10)
    reac8 = np.zeros(10)
    reac9 = np.zeros(10)
    reac10 = np.zeros(10)
    reac11 = np.zeros(10)
    reac12 = np.zeros(10)
    reac13 = np.zeros(10)
    reac14 = np.zeros(10)
    reac15 = np.zeros(10)
    reac16 = np.zeros(10)
    reac17 = np.zeros(10)
    reac18 = np.zeros(10)
    reac19 = np.zeros(10)
    reac20 = np.zeros(10)
    dx = np.zeros(200)
    xtemp = np.zeros(200)

    area = dim[0]
    h = dim[1] / layer[1]
    feedlayer = layer[0]
    volume = area * dim[1]

    eps = 0.01
    v_in = y_in[14] / area
    Q_f = y_in[14]
    Q_u = Qr + Qw
    Q_e = y_in[14] - Q_u
    v_up = Q_e / area
    v_dn = Q_u / area

    xtemp = y
    xtemp[xtemp < 0.0] = 0.0

    # sedimentations velocity for each of the layers:
    for i in range(10):
        vs[i] = parset[1] * (math.exp(-parset[2] * (xtemp[i + 130] - parset[4] * y_in[13])) - math.exp(
            -parset[3] * (xtemp[i + 130] - parset[4] * y_in[13])))
        vs[vs > parset[0]] = parset[0]
        vs[vs < 0.0] = 0.0

    # sludge flux due to sedimentation for each layer (not taking into account X limit)
    for i in range(10):
        Js_temp[i] = vs[i] * xtemp[i + 130]

    # sludge flux due to the liquid flow (upflow or downflow, depending on layer)
    for i in range(11):
        if i < (feedlayer - eps):
            Jflow[i] = v_up * xtemp[i + 130]
        else:
            Jflow[i] = v_dn * xtemp[i - 1 + 130]

    # sludge flux due to sedimentation of each layer:
    for i in range(9):
        if i < (feedlayer - 1 - eps) and xtemp[i + 1 + 130] <= parset[5]:
            Js[i + 1] = Js_temp[i]
        elif Js_temp[i] < Js_temp[i + 1]:
            Js[i + 1] = Js_temp[i]
        else:
            Js[i + 1] = Js_temp[i + 1]

    # hier fehlen noch die Gleichung von ASM1 (SETTLER) --> reaci und TEMPMODEL und DECAY
    # ASM1 model component balances of the layers
    # without conversion rates (SETTLER) --> müssen davor noch eingefügt werden

    # soluble component S_I:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i] = (-v_up * xtemp[i] + v_up * xtemp[i + 1]) / h + reac1[i]
        elif i > (feedlayer - eps):
            dx[i] = (v_dn * xtemp[i - 1] - v_dn * xtemp[i]) / h + reac1[i]
        else:
            dx[i] = (v_in * y_in[0] - v_up * xtemp[i] - v_dn * xtemp[i]) / h + reac1[i]

    # soluble component S_S:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 10] = (-v_up * xtemp[i + 10] + v_up * xtemp[i + 1 + 10]) / h + reac2[i]
        elif i > (feedlayer - eps):
            dx[i + 10] = (v_dn * xtemp[i - 1 + 10] - v_dn * xtemp[i + 10]) / h + reac2[i]
        else:
            dx[i + 10] = (v_in * y_in[1] - v_up * xtemp[i + 10] - v_dn * xtemp[i + 10]) / h + reac2[i]

    # particulate component X_I:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 20] = ((xtemp[i + 20] / xtemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        xtemp[i - 1 + 20] / xtemp[i - 1 + 130]) * Js[i] + (xtemp[i + 1 + 20] / xtemp[i + 1 + 130]) *
                          Jflow[i + 1]) / h + reac3[i]
        elif i > (feedlayer - eps):
            dx[i + 20] = ((xtemp[i + 20] / xtemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 20] / xtemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac3[i]
        else:
            dx[i + 20] = ((xtemp[i + 20] / xtemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 20] / xtemp[i - 1 + 130]) * Js[i] + v_in * y_in[2]) / h + reac3[i]

    # particulate component X_S:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 30] = ((xtemp[i + 30] / xtemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        xtemp[i - 1 + 30] / xtemp[i - 1 + 130]) * Js[i] + (xtemp[i + 1 + 30] / xtemp[i + 1 + 130]) *
                          Jflow[i + 1]) / h + reac4[i]
        elif i > (feedlayer - eps):
            dx[i + 30] = ((xtemp[i + 30] / xtemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 30] / xtemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac4[i]
        else:
            dx[i + 30] = ((xtemp[i + 30] / xtemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 30] / xtemp[i - 1 + 130]) * Js[i] + v_in * y_in[3]) / h + reac4[i]

    # particulate component X_BH:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 40] = ((xtemp[i + 40] / xtemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        xtemp[i - 1 + 40] / xtemp[i - 1 + 130]) * Js[i] + (xtemp[i + 1 + 40] / xtemp[i + 1 + 130]) *
                          Jflow[i + 1]) / h + reac5[i]
        elif i > (feedlayer - eps):
            dx[i + 40] = ((xtemp[i + 40] / xtemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 40] / xtemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac5[i]
        else:
            dx[i + 40] = ((xtemp[i + 40] / xtemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 40] / xtemp[i - 1 + 130]) * Js[i] + v_in * y_in[4]) / h + reac5[i]

    # particulate component X_BA:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 50] = ((xtemp[i + 50] / xtemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        xtemp[i - 1 + 50] / xtemp[i - 1 + 130]) * Js[i] + (xtemp[i + 1 + 50] / xtemp[i + 1 + 130]) *
                          Jflow[i + 1]) / h + reac6[i]
        elif i > (feedlayer - eps):
            dx[i + 50] = ((xtemp[i + 50] / xtemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 50] / xtemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac6[i]
        else:
            dx[i + 50] = ((xtemp[i + 50] / xtemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 50] / xtemp[i - 1 + 130]) * Js[i] + v_in * y_in[5]) / h + reac6[i]

    # particulate component X_P:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 60] = ((xtemp[i + 60] / xtemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        xtemp[i - 1 + 60] / xtemp[i - 1 + 130]) * Js[i] + (xtemp[i + 1 + 60] / xtemp[i + 1 + 130]) *
                          Jflow[i + 1]) / h + reac7[i]
        elif i > (feedlayer - eps):
            dx[i + 60] = ((xtemp[i + 60] / xtemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 60] / xtemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac7[i]
        else:
            dx[i + 60] = ((xtemp[i + 60] / xtemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 60] / xtemp[i - 1 + 130]) * Js[i] + v_in * y_in[6]) / h + reac7[i]

    # soluble component S_O:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 70] = (-v_up * xtemp[i + 70] + v_up * xtemp[i + 1 + 70]) / h + reac8[i]
        elif i > (feedlayer - eps):
            dx[i + 70] = (v_dn * xtemp[i - 1 + 70] - v_dn * xtemp[i + 70]) / h + reac8[i]
        else:
            dx[i + 70] = (v_in * y_in[7] - v_up * xtemp[i + 70] - v_dn * xtemp[i + 70]) / h + reac8[i]

    # soluble component S_NO:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 80] = (-v_up * xtemp[i + 80] + v_up * xtemp[i + 1 + 80]) / h + reac9[i]
        elif i > (feedlayer - eps):
            dx[i + 80] = (v_dn * xtemp[i - 1 + 80] - v_dn * xtemp[i + 80]) / h + reac9[i]
        else:
            dx[i + 80] = (v_in * y_in[8] - v_up * xtemp[i + 80] - v_dn * xtemp[i + 80]) / h + reac9[i]

    # soluble component S_NH:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 90] = (-v_up * xtemp[i + 90] + v_up * xtemp[i + 1 + 90]) / h + reac10[i]
        elif i > (feedlayer - eps):
            dx[i + 90] = (v_dn * xtemp[i - 1 + 90] - v_dn * xtemp[i + 90]) / h + reac10[i]
        else:
            dx[i + 90] = (v_in * y_in[9] - v_up * xtemp[i + 90] - v_dn * xtemp[i + 90]) / h + reac10[i]

    # soluble component S_ND:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 100] = (-v_up * xtemp[i + 100] + v_up * xtemp[i + 1 + 100]) / h + reac11[i]
        elif i > (feedlayer - eps):
            dx[i + 100] = (v_dn * xtemp[i - 1 + 100] - v_dn * xtemp[i + 100]) / h + reac11[i]
        else:
            dx[i + 100] = (v_in * y_in[10] - v_up * xtemp[i + 100] - v_dn * xtemp[i + 100]) / h + reac11[i]

    # particulate component X_ND:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 110] = ((xtemp[i + 110] / xtemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        xtemp[i - 1 + 110] / xtemp[i - 1 + 130]) * Js[i] + (xtemp[i + 1 + 110] / xtemp[i + 1 + 130]) *
                           Jflow[i + 1]) / h + reac12[i]
        elif i > (feedlayer - eps):
            dx[i + 110] = ((xtemp[i + 110] / xtemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 110] / xtemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac12[i]
        else:
            dx[i + 110] = ((xtemp[i + 110] / xtemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 110] / xtemp[i - 1 + 130]) * Js[i] + v_in * y_in[11]) / h + reac12[i]

    # soluble component S_ALK:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 120] = (-v_up * xtemp[i + 120] + v_up * xtemp[i + 1 + 120]) / h + reac13[i]
        elif i > (feedlayer - eps):
            dx[i + 120] = (v_dn * xtemp[i - 1 + 120] - v_dn * xtemp[i + 120]) / h + reac13[i]
        else:
            dx[i + 120] = (v_in * y_in[12] - v_up * xtemp[i + 120] - v_dn * xtemp[i + 120]) / h + reac13[i]

    # particulate component X_TSS:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 130] = ((-Jflow[i] - Js[i + 1]) + Js[i] + Jflow[i + 1]) / h + reac14[i]
        elif i > (feedlayer - eps):
            dx[i + 130] = ((-Jflow[i + 1] - Js[i + 1]) + (Jflow[i] + Js[i])) / h + reac14[i]
        else:
            dx[i + 130] = ((-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + Js[i] + v_in * y_in[13]) / h + reac14[i]

    # Temperature:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 140] = (-v_up * xtemp[i + 140] + v_up * xtemp[i + 1 + 140]) / h
        elif i > (feedlayer - eps):
            dx[i + 140] = (v_dn * xtemp[i - 1 + 140] - v_dn * xtemp[i + 140]) / h
        else:
            dx[i + 140] = (v_in * y_in[15] - v_up * xtemp[i + 140] - v_dn * xtemp[i + 140]) / h

    # soluble component S_D1:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 150] = (-v_up * xtemp[i + 150] + v_up * xtemp[i + 1 + 150]) / h + reac16[i]
        elif i > (feedlayer - eps):
            dx[i + 150] = (v_dn * xtemp[i - 1 + 150] - v_dn * xtemp[i + 150]) / h + reac16[i]
        else:
            dx[i + 150] = (v_in * y_in[16] - v_up * xtemp[i + 150] - v_dn * xtemp[i + 150]) / h + reac16[i]

    # soluble component S_D2:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 160] = (-v_up * xtemp[i + 160] + v_up * xtemp[i + 1 + 160]) / h + reac17[i]
        elif i > (feedlayer - eps):
            dx[i + 160] = (v_dn * xtemp[i - 1 + 160] - v_dn * xtemp[i + 160]) / h + reac17[i]
        else:
            dx[i + 160] = (v_in * y_in[17] - v_up * xtemp[i + 160] - v_dn * xtemp[i + 160]) / h + reac17[i]

    # soluble component S_D3:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dx[i + 170] = (-v_up * xtemp[i + 170] + v_up * xtemp[i + 1 + 170]) / h + reac18[i]
        elif i > (feedlayer - eps):
            dx[i + 170] = (v_dn * xtemp[i - 1 + 170] - v_dn * xtemp[i + 170]) / h + reac18[i]
        else:
            dx[i + 170] = (v_in * y_in[18] - v_up * xtemp[i + 170] - v_dn * xtemp[i + 170]) / h + reac18[i]

    # particulate component X_D4:
    dx[180] = ((y[180] / y[130]) * (-Jflow[0] - Js[1]) + (y[181] / y[131]) * Jflow[1]) / h + reac19[0]
    for i in range(1, 10):
        if i < (feedlayer - 1 - eps):
            dx[i + 180] = ((xtemp[i + 180] / xtemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        xtemp[i - 1 + 180] / xtemp[i - 1 + 130]) * Js[i] + (xtemp[i + 1 + 180] / xtemp[i + 1 + 130]) *
                           Jflow[i + 1]) / h + reac19[i]
        elif i > (feedlayer - eps):
            dx[i + 180] = ((xtemp[i + 180] / xtemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 180] / xtemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac19[i]
        else:
            dx[i + 180] = ((xtemp[i + 180] / xtemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 180] / xtemp[i - 1 + 130]) * Js[i] + v_in * y_in[19]) / h + reac19[i]

    # particulate component X_D5:
    dx[190] = ((y[190] / y[130]) * (-Jflow[0] - Js[1]) + (y[191] / y[131]) * Jflow[1]) / h + reac20[0]
    for i in range(1, 10):
        if i < (feedlayer - 1 - eps):
            dx[i + 190] = ((xtemp[i + 190] / xtemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        xtemp[i - 1 + 190] / xtemp[i - 1 + 130]) * Js[i] + (xtemp[i + 1 + 190] / xtemp[i + 1 + 130]) *
                           Jflow[i + 1]) / h + reac20[i]
        elif i > (feedlayer - eps):
            dx[i + 190] = ((xtemp[i + 190] / xtemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 190] / xtemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac20[i]
        else:
            dx[i + 190] = ((xtemp[i + 190] / xtemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        xtemp[i - 1 + 190] / xtemp[i - 1 + 130]) * Js[i] + v_in * y_in[20]) / h + reac20[i]

    return dx


class Settler:

    def __init__(self, dim, layer, Qr, Qw, y0):
        self.dim = dim      # dimensions of the settler, area and height
        self.layer = layer  # feedlayer and number of layers
        self.Qr = Qr        # sludge recycle
        self.Qw = Qw        # waste flow
        self.y0 = y0        # initial states for integration

    def derivatives(self, t, y, y_in, parasm):
        return derivatives_function(t, y, y_in, parasm, self.dim, self.layer, self.Qr, self.Qw)

    def output(self, timestep, step, y_in, parset):
        y_outs_all = np.zeros(203)
        y_outs = np.zeros(21)
        t_span = [step - timestep, step]
        t_eval = np.array([step - timestep, step])

        sols = solve_ivp(self.derivatives, t_span, self.y0, args=(y_in, parset,), rtol=1e-5, atol=1e-8)
        y_int = np.array([x[1] for x in sols.y])

        # odes = odeint(self.derivatives, self.y0, t_eval, tfirst=True, args=(y_in, parset,), rtol=1e-5, atol=1e-8)
        # y_int = odes[1]

        self.y0 = y_int

        for i in range(10):
            for j in range(15):
                y_outs_all[(i*20)+j] = y_int[i+j*10]  # tempmodel fehlt hier noch
            y_outs_all[(i*20)+15] = y_in[14]
            for k in range(15, 20):
                y_outs_all[(i*20)+k] = y_int[i+k*10]

        # flow rates out of the clarifier:
        y_outs_all[200] = y_in[14] - self.Qr - self.Qw
        y_outs_all[201] = self.Qr
        y_outs_all[202] = self.Qw

        y_outs[0:14] = y_outs_all[180:194]
        y_outs[14] = self.Qr
        y_outs[15:21] = y_outs_all[194:200]

        return y_outs


