import numpy as np
from scipy.integrate import solve_ivp, odeint
from numba import jit, njit


# differential equations in function because @jit does not compile class methods in nopython mode
@jit(nopython=True)
def derivativess(t, ys, ys_in, parset, dim, layer, Qr, Qw):

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
    dys = np.zeros(200)
    ystemp = np.zeros(200)

    area = dim[0]
    h = dim[1] / layer[1]
    feedlayer = layer[0]
    volume = area * dim[1]

    eps = 0.01
    v_in = ys_in[14] / area
    Q_f = ys_in[14]
    Q_u = Qr + Qw
    Q_e = ys_in[14] - Q_u
    v_up = Q_e / area
    v_dn = Q_u / area

    ystemp = ys
    ystemp[ystemp < 0.0] = 0.00001

    # sedimentations velocity for each of the layers:
    for i in range(10):
        vs[i] = parset[1] * (np.exp(-parset[2] * (ystemp[i + 130] - parset[4] * ys_in[13])) - np.exp(
            -parset[3] * (ystemp[i + 130] - parset[4] * ys_in[13])))
        vs[vs > parset[0]] = parset[0]
        vs[vs < 0.0] = 0.0

    # sludge flux due to sedimentation for each layer (not taking into account X limit)
    for i in range(10):
        Js_temp[i] = vs[i] * ystemp[i + 130]

    # sludge flux due to the liquid flow (upflow or downflow, depending on layer)
    for i in range(11):
        if i < (feedlayer - eps):
            Jflow[i] = v_up * ystemp[i + 130]
        else:
            Jflow[i] = v_dn * ystemp[i - 1 + 130]

    # sludge flux due to sedimentation of each layer:
    for i in range(9):
        if i < (feedlayer - 1 - eps) and ystemp[i + 1 + 130] <= parset[5]:
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
            dys[i] = (-v_up * ystemp[i] + v_up * ystemp[i + 1]) / h + reac1[i]
        elif i > (feedlayer - eps):
            dys[i] = (v_dn * ystemp[i - 1] - v_dn * ystemp[i]) / h + reac1[i]
        else:
            dys[i] = (v_in * ys_in[0] - v_up * ystemp[i] - v_dn * ystemp[i]) / h + reac1[i]

    # soluble component S_S:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 10] = (-v_up * ystemp[i + 10] + v_up * ystemp[i + 1 + 10]) / h + reac2[i]
        elif i > (feedlayer - eps):
            dys[i + 10] = (v_dn * ystemp[i - 1 + 10] - v_dn * ystemp[i + 10]) / h + reac2[i]
        else:
            dys[i + 10] = (v_in * ys_in[1] - v_up * ystemp[i + 10] - v_dn * ystemp[i + 10]) / h + reac2[i]

    # particulate component X_I:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 20] = ((ystemp[i + 20] / ystemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        ystemp[i - 1 + 20] / ystemp[i - 1 + 130]) * Js[i] + (ystemp[i + 1 + 20] / ystemp[i + 1 + 130]) *
                          Jflow[i + 1]) / h + reac3[i]
        elif i > (feedlayer - eps):
            dys[i + 20] = ((ystemp[i + 20] / ystemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 20] / ystemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac3[i]
        else:
            dys[i + 20] = ((ystemp[i + 20] / ystemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 20] / ystemp[i - 1 + 130]) * Js[i] + v_in * ys_in[2]) / h + reac3[i]

    # particulate component X_S:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 30] = ((ystemp[i + 30] / ystemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        ystemp[i - 1 + 30] / ystemp[i - 1 + 130]) * Js[i] + (ystemp[i + 1 + 30] / ystemp[i + 1 + 130]) *
                          Jflow[i + 1]) / h + reac4[i]
        elif i > (feedlayer - eps):
            dys[i + 30] = ((ystemp[i + 30] / ystemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 30] / ystemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac4[i]
        else:
            dys[i + 30] = ((ystemp[i + 30] / ystemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 30] / ystemp[i - 1 + 130]) * Js[i] + v_in * ys_in[3]) / h + reac4[i]

    # particulate component X_BH:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 40] = ((ystemp[i + 40] / ystemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        ystemp[i - 1 + 40] / ystemp[i - 1 + 130]) * Js[i] + (ystemp[i + 1 + 40] / ystemp[i + 1 + 130]) *
                          Jflow[i + 1]) / h + reac5[i]
        elif i > (feedlayer - eps):
            dys[i + 40] = ((ystemp[i + 40] / ystemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 40] / ystemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac5[i]
        else:
            dys[i + 40] = ((ystemp[i + 40] / ystemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 40] / ystemp[i - 1 + 130]) * Js[i] + v_in * ys_in[4]) / h + reac5[i]

    # particulate component X_BA:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 50] = ((ystemp[i + 50] / ystemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        ystemp[i - 1 + 50] / ystemp[i - 1 + 130]) * Js[i] + (ystemp[i + 1 + 50] / ystemp[i + 1 + 130]) *
                          Jflow[i + 1]) / h + reac6[i]
        elif i > (feedlayer - eps):
            dys[i + 50] = ((ystemp[i + 50] / ystemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 50] / ystemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac6[i]
        else:
            dys[i + 50] = ((ystemp[i + 50] / ystemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 50] / ystemp[i - 1 + 130]) * Js[i] + v_in * ys_in[5]) / h + reac6[i]

    # particulate component X_P:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 60] = ((ystemp[i + 60] / ystemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        ystemp[i - 1 + 60] / ystemp[i - 1 + 130]) * Js[i] + (ystemp[i + 1 + 60] / ystemp[i + 1 + 130]) *
                          Jflow[i + 1]) / h + reac7[i]
        elif i > (feedlayer - eps):
            dys[i + 60] = ((ystemp[i + 60] / ystemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 60] / ystemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac7[i]
        else:
            dys[i + 60] = ((ystemp[i + 60] / ystemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 60] / ystemp[i - 1 + 130]) * Js[i] + v_in * ys_in[6]) / h + reac7[i]

    # soluble component S_O:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 70] = (-v_up * ystemp[i + 70] + v_up * ystemp[i + 1 + 70]) / h + reac8[i]
        elif i > (feedlayer - eps):
            dys[i + 70] = (v_dn * ystemp[i - 1 + 70] - v_dn * ystemp[i + 70]) / h + reac8[i]
        else:
            dys[i + 70] = (v_in * ys_in[7] - v_up * ystemp[i + 70] - v_dn * ystemp[i + 70]) / h + reac8[i]

    # soluble component S_NO:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 80] = (-v_up * ystemp[i + 80] + v_up * ystemp[i + 1 + 80]) / h + reac9[i]
        elif i > (feedlayer - eps):
            dys[i + 80] = (v_dn * ystemp[i - 1 + 80] - v_dn * ystemp[i + 80]) / h + reac9[i]
        else:
            dys[i + 80] = (v_in * ys_in[8] - v_up * ystemp[i + 80] - v_dn * ystemp[i + 80]) / h + reac9[i]

    # soluble component S_NH:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 90] = (-v_up * ystemp[i + 90] + v_up * ystemp[i + 1 + 90]) / h + reac10[i]
        elif i > (feedlayer - eps):
            dys[i + 90] = (v_dn * ystemp[i - 1 + 90] - v_dn * ystemp[i + 90]) / h + reac10[i]
        else:
            dys[i + 90] = (v_in * ys_in[9] - v_up * ystemp[i + 90] - v_dn * ystemp[i + 90]) / h + reac10[i]

    # soluble component S_ND:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 100] = (-v_up * ystemp[i + 100] + v_up * ystemp[i + 1 + 100]) / h + reac11[i]
        elif i > (feedlayer - eps):
            dys[i + 100] = (v_dn * ystemp[i - 1 + 100] - v_dn * ystemp[i + 100]) / h + reac11[i]
        else:
            dys[i + 100] = (v_in * ys_in[10] - v_up * ystemp[i + 100] - v_dn * ystemp[i + 100]) / h + reac11[i]

    # particulate component X_ND:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 110] = ((ystemp[i + 110] / ystemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        ystemp[i - 1 + 110] / ystemp[i - 1 + 130]) * Js[i] + (ystemp[i + 1 + 110] / ystemp[i + 1 + 130]) *
                           Jflow[i + 1]) / h + reac12[i]
        elif i > (feedlayer - eps):
            dys[i + 110] = ((ystemp[i + 110] / ystemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 110] / ystemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac12[i]
        else:
            dys[i + 110] = ((ystemp[i + 110] / ystemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 110] / ystemp[i - 1 + 130]) * Js[i] + v_in * ys_in[11]) / h + reac12[i]

    # soluble component S_ALK:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 120] = (-v_up * ystemp[i + 120] + v_up * ystemp[i + 1 + 120]) / h + reac13[i]
        elif i > (feedlayer - eps):
            dys[i + 120] = (v_dn * ystemp[i - 1 + 120] - v_dn * ystemp[i + 120]) / h + reac13[i]
        else:
            dys[i + 120] = (v_in * ys_in[12] - v_up * ystemp[i + 120] - v_dn * ystemp[i + 120]) / h + reac13[i]

    # particulate component X_TSS:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 130] = ((-Jflow[i] - Js[i + 1]) + Js[i] + Jflow[i + 1]) / h + reac14[i]
        elif i > (feedlayer - eps):
            dys[i + 130] = ((-Jflow[i + 1] - Js[i + 1]) + (Jflow[i] + Js[i])) / h + reac14[i]
        else:
            dys[i + 130] = ((-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + Js[i] + v_in * ys_in[13]) / h + reac14[i]

    # Temperature:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 140] = (-v_up * ystemp[i + 140] + v_up * ystemp[i + 1 + 140]) / h
        elif i > (feedlayer - eps):
            dys[i + 140] = (v_dn * ystemp[i - 1 + 140] - v_dn * ystemp[i + 140]) / h
        else:
            dys[i + 140] = (v_in * ys_in[15] - v_up * ystemp[i + 140] - v_dn * ystemp[i + 140]) / h

    # soluble component S_D1:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 150] = (-v_up * ystemp[i + 150] + v_up * ystemp[i + 1 + 150]) / h + reac16[i]
        elif i > (feedlayer - eps):
            dys[i + 150] = (v_dn * ystemp[i - 1 + 150] - v_dn * ystemp[i + 150]) / h + reac16[i]
        else:
            dys[i + 150] = (v_in * ys_in[16] - v_up * ystemp[i + 150] - v_dn * ystemp[i + 150]) / h + reac16[i]

    # soluble component S_D2:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 160] = (-v_up * ystemp[i + 160] + v_up * ystemp[i + 1 + 160]) / h + reac17[i]
        elif i > (feedlayer - eps):
            dys[i + 160] = (v_dn * ystemp[i - 1 + 160] - v_dn * ystemp[i + 160]) / h + reac17[i]
        else:
            dys[i + 160] = (v_in * ys_in[17] - v_up * ystemp[i + 160] - v_dn * ystemp[i + 160]) / h + reac17[i]

    # soluble component S_D3:
    for i in range(10):
        if i < (feedlayer - 1 - eps):
            dys[i + 170] = (-v_up * ystemp[i + 170] + v_up * ystemp[i + 1 + 170]) / h + reac18[i]
        elif i > (feedlayer - eps):
            dys[i + 170] = (v_dn * ystemp[i - 1 + 170] - v_dn * ystemp[i + 170]) / h + reac18[i]
        else:
            dys[i + 170] = (v_in * ys_in[18] - v_up * ystemp[i + 170] - v_dn * ystemp[i + 170]) / h + reac18[i]

    # particulate component X_D4:
    dys[180] = ((ys[180] / ys[130]) * (-Jflow[0] - Js[1]) + (ys[181] / ys[131]) * Jflow[1]) / h + reac19[0]
    for i in range(1, 10):
        if i < (feedlayer - 1 - eps):
            dys[i + 180] = ((ystemp[i + 180] / ystemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        ystemp[i - 1 + 180] / ystemp[i - 1 + 130]) * Js[i] + (ystemp[i + 1 + 180] / ystemp[i + 1 + 130]) *
                           Jflow[i + 1]) / h + reac19[i]
        elif i > (feedlayer - eps):
            dys[i + 180] = ((ystemp[i + 180] / ystemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 180] / ystemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac19[i]
        else:
            dys[i + 180] = ((ystemp[i + 180] / ystemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 180] / ystemp[i - 1 + 130]) * Js[i] + v_in * ys_in[19]) / h + reac19[i]

    # particulate component X_D5:
    dys[190] = ((ys[190] / ys[130]) * (-Jflow[0] - Js[1]) + (ys[191] / ys[131]) * Jflow[1]) / h + reac20[0]
    for i in range(1, 10):
        if i < (feedlayer - 1 - eps):
            dys[i + 190] = ((ystemp[i + 190] / ystemp[i + 130]) * (-Jflow[i] - Js[i + 1]) + (
                        ystemp[i - 1 + 190] / ystemp[i - 1 + 130]) * Js[i] + (ystemp[i + 1 + 190] / ystemp[i + 1 + 130]) *
                           Jflow[i + 1]) / h + reac20[i]
        elif i > (feedlayer - eps):
            dys[i + 190] = ((ystemp[i + 190] / ystemp[i + 130]) * (-Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 190] / ystemp[i - 1 + 130]) * (Jflow[i] + Js[i])) / h + reac20[i]
        else:
            dys[i + 190] = ((ystemp[i + 190] / ystemp[i + 130]) * (-Jflow[i] - Jflow[i + 1] - Js[i + 1]) + (
                        ystemp[i - 1 + 190] / ystemp[i - 1 + 130]) * Js[i] + v_in * ys_in[20]) / h + reac20[i]

    return dys


class Settler:

    def __init__(self, dim, layer, Qr, Qw, ys0, parset):
        self.dim = dim          # dimensions of the settler, area and height
        self.layer = layer      # feedlayer and number of layers
        self.Qr = Qr            # sludge recycle
        self.Qw = Qw            # waste flow
        self.ys0 = ys0          # initial states for integration
        self.parset = parset    # Parameters of settler-model

    def outputs(self, timestep, step, ys_in):
        ys_out_all = np.zeros(203)
        ys_out = np.zeros(21)
        t_span = [step - timestep, step]
        t_eval = np.array([step - timestep, step])

        # sols = solve_ivp(derivativess, t_span, self.ys0, args=(y_in, self.parset, self.dim, self.layer, self.Qr, self.Qw,), rtol=1e-5, atol=1e-8)
        # y_int = np.array([x[1] for x in sols.y])

        odes = odeint(derivativess, self.ys0, t_eval, tfirst=True, args=(ys_in, self.parset, self.dim, self.layer, self.Qr, self.Qw,), rtol=1e-5, atol=1e-8)
        ys_int = odes[1]

        self.ys0 = ys_int

        for i in range(10):
            for j in range(15):
                ys_out_all[(i*20)+j] = ys_int[i+j*10]  # tempmodel fehlt hier noch
            ys_out_all[(i*20)+15] = ys_in[14]
            for k in range(15, 20):
                ys_out_all[(i*20)+k] = ys_int[i+k*10]

        # flow rates out of the clarifier:
        ys_out_all[200] = ys_in[14] - self.Qr - self.Qw
        ys_out_all[201] = self.Qr
        ys_out_all[202] = self.Qw

        ys_out[0:14] = ys_out_all[180:194]
        ys_out[14] = self.Qr
        ys_out[15:21] = ys_out_all[194:200]

        return ys_out, ys_out_all


