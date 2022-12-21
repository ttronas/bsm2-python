import numpy as np
from scipy.integrate import solve_ivp, odeint
from numba import jit, njit
import nbkode


# differential equations in function because @jit does not compile class methods in nopython mode
@jit(nopython=True)
def derivatives_function(t, y, y_in, parasm, kla, volume, sosat):
    dy = np.zeros(21)

    mu_H, K_S, K_OH, K_NO, b_H, mu_A, K_NH, K_OA, b_A, ny_g, k_a, k_h, K_X, ny_h, Y_H, Y_A, f_P, i_XB, i_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS = parasm
    # add decay parameter here

    # temperature compensation:
    mu_H = mu_H * np.exp((np.log(mu_H / 3.0) / 5.0) * (y_in[15] - 15.0))  # temperature at the influent of the reactor
    b_H = b_H * np.exp((np.log(b_H / 0.2) / 5.0) * (y_in[15] - 15.0))
    mu_A = mu_A * np.exp((np.log(mu_A / 0.3) / 5.0) * (y_in[15] - 15.0))
    b_A = b_A * np.exp((np.log(b_A / 0.03) / 5.0) * (y_in[15] - 15.0))
    k_h = k_h * np.exp((np.log(k_h / 2.5) / 5.0) * (y_in[15] - 15.0))
    k_a = k_a * np.exp((np.log(k_a / 0.04) / 5.0) * (y_in[15] - 15.0))
    SO_sat_temp = 0.9997743214 * 8.0 / 10.5 * (56.12 * 6791.5 * np.exp(
        -66.7354 + 87.4755 / ((y_in[15] + 273.15) / 100.0) + 24.4526 * np.log(
            (y_in[15] + 273.15) / 100.0)))  # van't Hoff equation
    KLa_temp = kla * np.power(1.024, (y_in[15] - 15.0))

    # TEMPMODEL hier einbauen

    # analog zu Matlab:
    xtemp = y
    xtemp[xtemp < 0.0] = 0.0

    # bestimmte O2-Konzentration wird gehalten, wenn KLa negativ ist:
    if kla < 0.0:
        y[7] = abs(kla)

    # process rates:
    proc1 = mu_H * (xtemp[1] / (K_S + xtemp[1])) * (xtemp[7] / (K_OH + xtemp[7])) * xtemp[4]
    proc2 = mu_H * (xtemp[1] / (K_S + xtemp[1])) * (K_OH / (K_OH + xtemp[7])) * (
                xtemp[8] / (K_NO + xtemp[8])) * ny_g * xtemp[4]
    proc3 = mu_A * (xtemp[9] / (K_NH + xtemp[9])) * (xtemp[7] / (K_OA + xtemp[7])) * xtemp[5]
    proc4 = b_H * xtemp[4]
    proc5 = b_A * xtemp[5]
    proc6 = k_a * xtemp[10] * xtemp[4]
    proc7 = k_h * ((xtemp[3] / xtemp[4]) / (K_X + (xtemp[3] / xtemp[4]))) * (
            (xtemp[7] / (K_OH + xtemp[7])) + ny_h * (K_OH / (K_OH + xtemp[7])) * (
                    xtemp[8] / (K_NO + xtemp[8]))) * xtemp[4]
    proc8 = proc7 * (xtemp[11] / xtemp[3])

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
    dy[0] = 1.0 / volume * (y_in[14] * (y_in[0] - y[0])) + reac1
    dy[1] = 1.0 / volume * (y_in[14] * (y_in[1] - y[1])) + reac2
    dy[2] = 1.0 / volume * (y_in[14] * (y_in[2] - y[2])) + reac3
    dy[3] = 1.0 / volume * (y_in[14] * (y_in[3] - y[3])) + reac4
    dy[4] = 1.0 / volume * (y_in[14] * (y_in[4] - y[4])) + reac5
    dy[5] = 1.0 / volume * (y_in[14] * (y_in[5] - y[5])) + reac6
    dy[6] = 1.0 / volume * (y_in[14] * (y_in[6] - y[6])) + reac7
    if kla < 0.0:
        dy[7] = 0.0
    else:
        dy[7] = 1.0 / volume * (y_in[14] * (y_in[7] - y[7])) + reac8 + KLa_temp * (SO_sat_temp - y[7])
    dy[8] = 1.0 / volume * (y_in[14] * (y_in[8] - y[8])) + reac9
    dy[9] = 1.0 / volume * (y_in[14] * (y_in[9] - y[9])) + reac10
    dy[10] = 1.0 / volume * (y_in[14] * (y_in[10] - y[10])) + reac11
    dy[11] = 1.0 / volume * (y_in[14] * (y_in[11] - y[11])) + reac12
    dy[12] = 1.0 / volume * (y_in[14] * (y_in[12] - y[12])) + reac13
    dy[13] = 0.0
    dy[14] = 0.0
    dy[15] = 0.0  # TEMPMODEL hier einbauen
    # ACTIVATE hier einbauen, damit er nicht integrieren muss??
    dy[16] = 1.0 / volume * (y_in[14] * (y_in[16] - y[16])) + reac16
    dy[17] = 1.0 / volume * (y_in[14] * (y_in[17] - y[17])) + reac17
    dy[18] = 1.0 / volume * (y_in[14] * (y_in[18] - y[18])) + reac18
    dy[19] = 1.0 / volume * (y_in[14] * (y_in[19] - y[19])) + reac19
    dy[20] = 1.0 / volume * (y_in[14] * (y_in[20] - y[20])) + reac20

    return dy


class ASM1reactor:

    def __init__(self, volume, kla, sosat, y0, parasm):
        self.volume = volume        # volume of the reactor compartment
        self.kla = kla              # oxygen transfer coefficient in aerated reactors
        self.sosat = sosat          # saturation concentration for oxygen
        self.y0 = y0                # initial states for integration (damit man es anpassen kann)
        self.parasm = parasm        # Parameters of ASM1-Model

    def output(self, timestep, step, y_in):
        t_span = [step-timestep, step]
        t_eval = np.array([step-timestep, step])

        # sol = solve_ivp(derivatives_function, t_span, self.y0, args=(y_in, self.parasm,self.kla, self.volume, self.sosat,), rtol=1e-5, atol=1e-8)
        # y_out = np.array([x[1] for x in sol.y])

        ode = odeint(derivatives_function, self.y0, t_eval, tfirst=True, args=(y_in, self.parasm, self.kla, self.volume, self.sosat,), rtol=1e-5, atol=1e-8)
        y_out = ode[1]

        y_out[13] = self.parasm[19] * y_out[2] + self.parasm[20] * y_out[3] + self.parasm[21] * y_out[4] + self.parasm[22] * y_out[5] + self.parasm[23] * y_out[6]  # TSS
        y_out[14] = y_in[14]  # Flow
        y_out[15] = y_in[15]  # Temperature, TEMPMODEL fehlt hier noch
        self.y0 = y_out

        return y_out
