import numpy as np
from scipy.integrate import solve_ivp, odeint
from numba import jit, njit


# differential equations in function because @jit does not compile class methods in nopython mode
@jit(nopython=True)
def derivativess(t, ys, ys_in, sedpar, dim, layer, Qr, Qw, asmpar, tempmodel, decay_switch, reactive_settler):
    """Returns an array containing the differential equations of a reactive 10 layer sedimentation tank, which is compatible with ASM1 model

    Parameters
    ----------
    t : np.ndarray
        Time interval for integration, needed for the solver

    ys : np.ndarray
        Solution of the differential equations, needed for the solver

    ys_in : np.ndarray
        Settler inlet concentrations of the 21 ASM1 components

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

    asmpar : np.ndarray
        26 parameters needed for ASM1 equations

    tempmodel : bool
        If true, mass balance for the wastewater temperature is used in process rates,
        otherwise influent wastewater temperature is just passed through process reactors

    decay_switch : bool
        If true, the decay of heterotrophs and autotrophs is depending on the electron acceptor present,
        otherwise the decay do not change

    reactive_settler : bool
        If true, the settling model is non-reactive, otherwise the settling model is reactive

    Returns
    -------
    np.ndarray
        Array containing 200 differential equations of settling model with 10 layers

    """

    indices_components = np.arange(21)
    SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components
    mu_H, K_S, K_OH, K_NO, b_H, mu_A, K_NH, K_OA, b_A, ny_g, k_a, k_h, K_X, ny_h, Y_H, Y_A, f_P, i_XB, i_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS, hH_NO3_end, hA_NO3_end = asmpar

    vs = np.zeros(10)
    Js = np.zeros(11)
    Js_temp = np.zeros(10)
    Jflow = np.zeros(11)

    proc1 = np.zeros(10)
    proc2 = np.zeros(10)
    proc3 = np.zeros(10)
    proc4 = np.zeros(10)
    proc5 = np.zeros(10)
    proc6 = np.zeros(10)
    proc7 = np.zeros(10)
    proc8 = np.zeros(10)

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

    mu_H_T = np.zeros(10)
    b_H_T = np.zeros(10)
    mu_A_T = np.zeros(10)
    b_A_T = np.zeros(10)
    k_h_T = np.zeros(10)
    k_a_T = np.zeros(10)

    dys = np.zeros(200)

    area = dim[0]
    h = dim[1] / layer[1]
    feedlayer = layer[0]
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

    # sedimentations velocity for each of the layers:
    for i in range(10):
        vs[i] = sedpar[1] * (np.exp(-sedpar[2] * (ystemp[i + TSS * 10] - sedpar[4] * ys_in[TSS])) - np.exp(
            -sedpar[3] * (ystemp[i + TSS * 10] - sedpar[4] * ys_in[TSS])))
        vs[vs > sedpar[0]] = sedpar[0]
        vs[vs < 0.0] = 0.0

    # sludge flux due to sedimentation for each layer (not taking into account X limit)
    for i in range(10):
        Js_temp[i] = vs[i] * ystemp[i + TSS * 10]

    # sludge flux due to the liquid flow (upflow or downflow, depending on layer)
    for i in range(11):
        if i < (feedlayer - eps):
            Jflow[i] = v_up * ystemp[i + TSS * 10]
        else:
            Jflow[i] = v_dn * ystemp[i - 1 + TSS * 10]

    # sludge flux due to sedimentation of each layer:
    for i in range(9):
        if i < (feedlayer - 1 - eps) and ystemp[i + 1 + TSS * 10] <= sedpar[5]:
            Js[i + 1] = Js_temp[i]
        elif Js_temp[i] < Js_temp[i + 1]:
            Js[i + 1] = Js_temp[i]
        else:
            Js[i + 1] = Js_temp[i + 1]

    # Reaction rates ASM1 model

    for i in range(10):

        if not tempmodel:
            mu_H_T[i] = mu_H * np.exp((np.log(mu_H / 3.0) / 5.0) * (ys_in[TEMP] - 15.0))  # temperature at the influent of the reactor
            b_H_T[i] = b_H * np.exp((np.log(b_H / 0.2) / 5.0) * (ys_in[TEMP] - 15.0))
            mu_A_T[i] = mu_A * np.exp((np.log(mu_A / 0.3) / 5.0) * (ys_in[TEMP] - 15.0))
            b_A_T[i] = b_A * np.exp((np.log(b_A / 0.03) / 5.0) * (ys_in[TEMP] - 15.0))
            k_h_T[i] = k_h * np.exp((np.log(k_h / 2.5) / 5.0) * (ys_in[TEMP] - 15.0))
            k_a_T[i] = k_a * np.exp((np.log(k_a / 0.04) / 5.0) * (ys_in[TEMP] - 15.0))

        else:
            mu_H_T[i] = mu_H * np.exp((np.log(mu_H / 3.0) / 5.0) * (ys[TEMP] - 15.0))  # current temperature in the reactor
            b_H_T[i] = b_H * np.exp((np.log(b_H / 0.2) / 5.0) * (ys[TEMP] - 15.0))
            mu_A_T[i] = mu_A * np.exp((np.log(mu_A / 0.3) / 5.0) * (ys[TEMP] - 15.0))
            b_A_T[i] = b_A * np.exp((np.log(b_A / 0.03) / 5.0) * (ys[TEMP] - 15.0))
            k_h_T[i] = k_h * np.exp((np.log(k_h / 2.5) / 5.0) * (ys[TEMP] - 15.0))
            k_a_T[i] = k_a * np.exp((np.log(k_a / 0.04) / 5.0) * (ys[TEMP] - 15.0))

        if decay_switch:
            proc1[i] = mu_H_T[i] * (ystemp[i + SS * 10] / (K_S + ystemp[i + SS * 10])) * (ystemp[i + SO * 10] / (K_OH + ystemp[i + SO * 10])) * ystemp[i + XBH * 10]
            proc2[i] = mu_H_T[i] * (ystemp[i + SS * 10] / (K_S + ystemp[i + SS * 10])) * (K_OH / (K_OH + ystemp[i + SO * 10])) * (ystemp[i + SNO * 10] / (K_NO + ystemp[i + SNO * 10])) * ny_g * ystemp[i + XBH * 10]
            proc3[i] = mu_A_T[i] * (ystemp[i + SNH * 10] / (K_NH + ystemp[i + SNH * 10])) * (ystemp[i + SO * 10] / (K_OA + ystemp[i + SO * 10])) * ystemp[i + XBA * 10]
            proc4[i] = b_H_T[i] * (ystemp[i + SO * 10] / (K_OH + ystemp[i + SO * 10]) + hH_NO3_end * K_OH / (K_OH + ystemp[i + SO * 10]) * ystemp[i + SNO * 10] / (K_NO + ystemp[i + SNO * 10])) * ystemp[i + XBH * 10]
            proc5[i] = b_A_T[i] * (ystemp[i + SO * 10] / (K_OH + ystemp[i + SO * 10]) + hH_NO3_end * K_OH / (K_OH + ystemp[i + SO * 10]) * ystemp[i + SNO * 10] / (K_NO + ystemp[i + SNO * 10])) * ystemp[i + XBA * 10]
            proc6[i] = k_a_T[i] * ystemp[i + SND * 10] * ystemp[i + XBH * 10]
            proc7[i] = k_h_T[i] * ((ystemp[i + XS * 10] / ystemp[i + XBH * 10]) / (K_X + (ystemp[i + XS * 10] / ystemp[i + XBH * 10]))) * ((ystemp[i + SO * 10] / (K_OH + ystemp[i + SO * 10])) + ny_h * (K_OH / (K_OH + ystemp[i + SO * 10])) * (ystemp[i + SNO * 10] / (K_NO + ystemp[i + SNO * 10]))) * ystemp[i + XBH * 10]
            proc8[i] = proc7[i] * ystemp[i + XND * 10] / ystemp[i + XS * 10]

        elif not decay_switch:
            proc1[i] = mu_H_T[i] * (ystemp[i + SS * 10] / (K_S + ystemp[i + SS * 10])) * (ystemp[i + SO * 10] / (K_OH + ystemp[i + SO * 10])) * ystemp[i + XBH * 10]
            proc2[i] = mu_H_T[i] * (ystemp[i + SS * 10] / (K_S + ystemp[i + SS * 10])) * (K_OH / (K_OH + ystemp[i + SO * 10])) * (ystemp[i + SNO * 10] / (K_NO + ystemp[i + SNO * 10])) * ny_g * ystemp[i + XBH * 10]
            proc3[i] = mu_A_T[i] * (ystemp[i + SNH * 10] / (K_NH + ystemp[i + SNH * 10])) * (ystemp[i + SO * 10] / (K_OA + ystemp[i + SO * 10])) * ystemp[i + XBA * 10]
            proc4[i] = b_H_T[i] * ystemp[i + XBH * 10]
            proc5[i] = b_A_T[i] * ystemp[i + XBA * 10]
            proc6[i] = k_a_T[i] * ystemp[i + SND * 10] * ystemp[i + XBH * 10]
            proc7[i] = k_h_T[i] * ((ystemp[i + XS * 10] / ystemp[i + XBH * 10]) / (K_X + (ystemp[i + XS * 10] / ystemp[i + XBH * 10]))) * ((ystemp[i + SO * 10] / (K_OH + ystemp[i + SO * 10])) + ny_h * (K_OH / (K_OH + ystemp[i + SO * 10])) * (ystemp[i + SNO * 10] / (K_NO + ystemp[i + SNO * 10]))) * ystemp[i + XBH * 10]
            proc8[i] = proc7[i] * ystemp[i + XND * 10] / ystemp[i + XS * 10]

        if reactive_settler:
            reac1[i] = 0.0
            reac2[i] = (-proc1[i] - proc2[i]) / Y_H + proc7[i]
            reac3[i] = 0.0
            reac4[i] = (1.0 - f_P) * (proc4[i] + proc5[i]) - proc7[i]
            reac5[i] = proc1[i] + proc2[i] - proc4[i]
            reac6[i] = proc3[i] - proc5[i]
            reac7[i] = f_P * (proc4[i] + proc5[i])
            reac8[i] = -((1.0 - Y_H) / Y_H) * proc1[i] - ((4.57 - Y_A) / Y_A) * proc3[i]
            reac9[i] = -((1.0 - Y_H) / (2.86 * Y_H)) * proc2[i] + proc3[i] / Y_A
            reac10[i] = -i_XB * (proc1[i] + proc2[i]) - (i_XB + (1.0 / Y_A)) * proc3[i] + proc6[i]
            reac11[i] = -proc6[i] + proc8[i]
            reac12[i] = (i_XB - f_P * i_XP) * (proc4[i] + proc5[i]) - proc8[i]
            reac13[i] = -i_XB / 14.0 * proc1[i] + ((1.0 - Y_H) / (14.0 * 2.86 * Y_H) - (i_XB / 14.0)) * proc2[i] - ((i_XB / 14.0) + 1.0 / (7.0 * Y_A)) * proc3[i] + proc6[i] / 14.0
            reac14[i] = X_I2TSS * reac3[i] + X_S2TSS * reac4[i] + X_BH2TSS * reac5[i] + X_BA2TSS * reac6[i] + X_P2TSS * reac7[i]

            reac16[i] = 0.0
            reac17[i] = 0.0
            reac18[i] = 0.0
            reac19[i] = 0.0
            reac20[i] = 0.0

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
    """
    A class representing a settler as a reactive sedimentation tank with certain number of layers, which is compatible with ASM1 model.

    Attributes
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
        Initial values for the 20 components (without Q) for each layer, sorted by components

    sedpar : np.ndarray
        6 parameters needed for settler equations

    asmpar : np.ndarray
        26 parameters needed for ASM1 equations

    tempmodel : bool
        If true, mass balance for the wastewater temperature is used in process rates,
        otherwise influent wastewater temperature is just passed through process reactors

    decay_switch : bool
        If true, the decay of heterotrophs and autotrophs is depending on the electron acceptor present,
        otherwise the decay do not change

    reactive_settler : bool
        If true, the settling model is non-reactive, otherwise the settling model is reactive

    Methods
    -------
    outputs(timestep, step, ys_in)
        Returns the solved differential equations of settling model
    """

    def __init__(self, dim, layer, Qr, Qw, ys0, sedpar, asmpar, tempmodel, decay_switch, reactive_settler):
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
            Initial values for the 20 components (without Q) for each layer, sorted by components

        sedpar : np.ndarray
            6 parameters needed for settler equations

        asmpar : np.ndarray
            26 parameters needed for ASM1 equations

        tempmodel : bool
            If true, mass balance for the wastewater temperature is used in process rates,
            otherwise influent wastewater temperature is just passed through process reactors

        decay_switch : bool
            If true, the decay of heterotrophs and autotrophs is depending on the electron acceptor present,
            otherwise the decay do not change

        reactive_settler : bool
            If true, the settling model is non-reactive, otherwise the settling model is reactive
        """

        self.dim = dim
        self.layer = layer
        self.Qr = Qr
        self.Qw = Qw
        self.ys0 = ys0
        self.sedpar = sedpar
        self.asmpar = asmpar
        self.tempmodel = tempmodel
        self.decay_switch = decay_switch
        self.reactive_settler = reactive_settler

    def outputs(self, timestep, step, ys_in):
        """Returns the solved differential equations of settling model.

        Parameters
        ----------
        timestep : int or float
            Size of integration interval in days
        step : int or float
            Upper boundary for integration interval in days
        ys_in : np.ndarray
            Settler inlet concentrations of the 21 ASM1 components

        Returns
        -------
        np.ndarray
            Array containing the concentrations of the 20 components in each layer at the current time step after the integration, sorted by layer plus Qe, Qr, Qw
        """

        ys_out_all = np.zeros(203)
        ys_out = np.zeros(21)
        t_eval = np.array([step, step + timestep])

        odes = odeint(derivativess, self.ys0, t_eval, tfirst=True, args=(ys_in, self.sedpar, self.dim, self.layer, self.Qr, self.Qw, self.asmpar, self.tempmodel, self.decay_switch, self.reactive_settler), rtol=1e-5, atol=1e-8)
        ys_int = odes[1]

        self.ys0 = ys_int

        for i in range(10):
            for j in range(15):
                ys_out_all[(i * 20) + j] = ys_int[i + j * 10]
            if not self.tempmodel:
                ys_out_all[(i * 20) + 15] = ys_in[14]
            else:
                ys_out_all[(i * 20) + 15] = ys_int[i + 14 * 10]
            for k in range(15, 20):
                ys_out_all[(i * 20) + k] = ys_int[i + k * 10]

        # flow rates out of the clarifier:
        ys_out_all[200] = ys_in[14] - self.Qr - self.Qw
        ys_out_all[201] = self.Qr
        ys_out_all[202] = self.Qw

        ys_out[0:14] = ys_out_all[180:194]
        ys_out[14] = self.Qr
        ys_out[15:21] = ys_out_all[194:200]

        return ys_out, ys_out_all
