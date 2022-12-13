import numpy as np
import math
from scipy.integrate import solve_ivp, odeint
from numba import jit, njit


# differential equations in function because @jit does not compile class methods in nopython mode
@jit(nopython=True)
def derivatives_function(t, y, y_in, parasm, kla, volume, sosat):
    S_I_in, S_S_in, X_I_in, X_S_in, X_BH_in, X_BA_in, X_P_in, S_O_in, S_NO_in, S_NH_in, S_ND_in, X_ND_in, S_ALK_in, TSS_in, Q_in, T_in, S_D1_in, S_D2_in, S_D3_in, X_D4_in, X_D5_in = y_in
    mu_H, K_S, K_OH, K_NO, b_H, mu_A, K_NH, K_OA, b_A, ny_g, k_a, k_h, K_X, ny_h, Y_H, Y_A, f_P, i_XB, i_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS = parasm
    # add decay parameter here

    # temperature compensation:
    mu_H = mu_H * math.exp((math.log(mu_H / 3.0) / 5.0) * (T_in - 15.0))  # temperature at the influent of the reactor
    b_H = b_H * math.exp((math.log(b_H / 0.2) / 5.0) * (T_in - 15.0))
    mu_A = mu_A * math.exp((math.log(mu_A / 0.3) / 5.0) * (T_in - 15.0))
    b_A = b_A * math.exp((math.log(b_A / 0.03) / 5.0) * (T_in - 15.0))
    k_h = k_h * math.exp((math.log(k_h / 2.5) / 5.0) * (T_in - 15.0))
    k_a = k_a * math.exp((math.log(k_a / 0.04) / 5.0) * (T_in - 15.0))
    SO_sat_temp = 0.9997743214 * 8.0 / 10.5 * (56.12 * 6791.5 * math.exp(
        -66.7354 + 87.4755 / ((T_in + 273.15) / 100.0) + 24.4526 * math.log(
            (T_in + 273.15) / 100.0)))  # van't Hoff equation
    KLa_temp = kla * pow(1.024, (T_in - 15.0))

    # TEMPMODEL hier einbauen

    # analog zu Matlab:
    y_temp = y
    y_temp[y_temp < 0.0] = 0.0

    S_I_temp, S_S_temp, X_I_temp, X_S_temp, X_BH_temp, X_BA_temp, X_P_temp, S_O_temp, S_NO_temp, S_NH_temp, S_ND_temp, X_ND_temp, S_ALK_temp, TSS_temp, Q_temp, T_temp, S_D1_temp, S_D2_temp, S_D3_temp, X_D4_temp, X_D5_temp = y_temp

    # bestimmte O2-Konzentration wird gehalten, wenn KLa negativ ist:
    if kla < 0.0:
        y[7] = abs(kla)

    S_I, S_S, X_I, X_S, X_BH, X_BA, X_P, S_O, S_NO, S_NH, S_ND, X_ND, S_ALK, TSS, Q, T, S_D1, S_D2, S_D3, X_D4, X_D5 = y

    # process rates:
    proc1 = mu_H * (S_S_temp / (K_S + S_S_temp)) * (S_O_temp / (K_OH + S_O_temp)) * X_BH_temp
    proc2 = mu_H * (S_S_temp / (K_S + S_S_temp)) * (K_OH / (K_OH + S_O_temp)) * (
                S_NO_temp / (K_NO + S_NO_temp)) * ny_g * X_BH_temp
    proc3 = mu_A * (S_NH_temp / (K_NH + S_NH_temp)) * (S_O_temp / (K_OA + S_O_temp)) * X_BA_temp
    proc4 = b_H * X_BH_temp
    proc5 = b_A * X_BA_temp
    proc6 = k_a * S_ND_temp * X_BH_temp
    proc7 = k_h * ((X_S_temp / X_BH_temp) / (K_X + (X_S_temp / X_BH_temp))) * (
                (S_O_temp / (K_OH + S_O_temp)) + ny_h * (K_OH / (K_OH + S_O_temp)) * (
                    S_NO_temp / (K_NO + S_NO_temp))) * X_BH_temp
    proc8 = proc7 * (X_ND_temp / X_S_temp)

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
    dS_I = 1.0 / volume * (Q_in * (S_I_in - S_I)) + reac1
    dS_S = 1.0 / volume * (Q_in * (S_S_in - S_S)) + reac2
    dX_I = 1.0 / volume * (Q_in * (X_I_in - X_I)) + reac3
    dX_S = 1.0 / volume * (Q_in * (X_S_in - X_S)) + reac4
    dX_BH = 1.0 / volume * (Q_in * (X_BH_in - X_BH)) + reac5
    dX_BA = 1.0 / volume * (Q_in * (X_BA_in - X_BA)) + reac6
    dX_P = 1.0 / volume * (Q_in * (X_P_in - X_P)) + reac7
    if kla < 0.0:
        dS_O = 0.0
    else:
        dS_O = 1.0 / volume * (Q_in * (S_O_in - S_O)) + reac8 + KLa_temp * (SO_sat_temp - S_O)
    dS_NO = 1.0 / volume * (Q_in * (S_NO_in - S_NO)) + reac9
    dS_NH = 1.0 / volume * (Q_in * (S_NH_in - S_NH)) + reac10
    dS_ND = 1.0 / volume * (Q_in * (S_ND_in - S_ND)) + reac11
    dX_ND = 1.0 / volume * (Q_in * (X_ND_in - X_ND)) + reac12
    dS_ALK = 1.0 / volume * (Q_in * (S_ALK_in - S_ALK)) + reac13
    dTSS = 0.0
    dQ = 0.0
    dT = 0.0  # TEMPMODEL hier einbauen
    # ACTIVATE hier einbauen, damit er nicht integrieren muss??
    dS_D1 = 1.0 / volume * (Q_in * (S_D1_in - S_D1)) + reac16
    dS_D2 = 1.0 / volume * (Q_in * (S_D2_in - S_D2)) + reac17
    dS_D3 = 1.0 / volume * (Q_in * (S_D3_in - S_D3)) + reac18
    dX_D4 = 1.0 / volume * (Q_in * (X_D4_in - X_D4)) + reac19
    dX_D5 = 1.0 / volume * (Q_in * (X_D5_in - X_D5)) + reac20

    f = [dS_I, dS_S, dX_I, dX_S, dX_BH, dX_BA, dX_P, dS_O, dS_NO, dS_NH, dS_ND, dX_ND,
         dS_ALK, dTSS, dQ, dT, dS_D1, dS_D2, dS_D3, dX_D4, dX_D5]

    return f


class ASM1reactor:

    def __init__(self, volume, kla, sosat, y0):
        self.volume = volume    # volume of the reactor compartment
        self.kla = kla       # oxygen transfer coefficient in aerated reactors
        self.sosat = sosat      # saturation concentration for oxygen
        self.y0 = y0        # initial states for integration (damit man es anpassen kann)

    def derivatives(self, t, y, y_in, parasm):
        return derivatives_function(t, y, y_in, parasm, self.kla, self.volume, self.sosat)

    def output(self, timestep, step, y_in, parasm):
        t_span = [step-timestep, step]
        t_eval = np.array([step-timestep, step])

        sol = solve_ivp(self.derivatives, t_span, self.y0, args=(y_in, parasm,), rtol=1e-5, atol=1e-8)
        y_out = np.array([x[1] for x in sol.y])

        # ode = odeint(self.derivatives, self.y0, t_eval, tfirst=True, args=(y_in, parasm,), rtol=1e-5, atol=1e-8)
        # y_out = ode[1]

        y_out[13] = parasm[19] * y_out[2] + parasm[20] * y_out[3] + parasm[21] * y_out[4] + parasm[22] * y_out[5] + parasm[23] * y_out[6]  # TSS
        y_out[14] = y_in[14]  # Flow
        y_out[15] = y_in[15]  # Temperature, TEMPMODEL fehlt hier noch
        self.y0 = y_out

        return y_out
