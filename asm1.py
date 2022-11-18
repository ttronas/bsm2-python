import numpy as np
from scipy.integrate import solve_ivp, odeint


class ASM1reactor:

    def __init__(self, volume, kla, sosat, y0):
        self.volume = volume    # volume of the reactor compartment
        self.kla = kla       # oxygen transfer coefficient in aerated reactors
        self.sosat = sosat      # saturation concentration for oxygen
        self.y0 = y0        # initial states for integration (damit man es anpassen kann)

    # differential equations:
    def derivatives(self, t, y, y_in, parasm):
        S_I, S_S, X_I, X_S, X_BH, X_BA, X_P, S_O, S_NO, S_NH, S_ND, X_ND, S_ALK, TSS, Q, T, S_D1, S_D2, S_D3, X_D4, X_D5 = y
        S_I_in, S_S_in, X_I_in, X_S_in, X_BH_in, X_BA_in, X_P_in, S_O_in, S_NO_in, S_NH_in, S_ND_in, X_ND_in, S_ALK_in, TSS_in, Q_in, T_in, S_D1_in, S_D2_in, S_D3_in, X_D4_in, X_D5_in = y_in
        mu_H, K_S, K_OH, K_NO, b_H, mu_A, K_NH, K_OA, b_A, ny_g, k_a, k_h, K_X, ny_h, Y_H, Y_A, f_P, i_XB, i_XP = parasm
        # add decay parameter here

        # temperature compensation:

        # Kompensation dass nicht kleiner als 0 sein darf
        # S_O wird kompensiert wenn KLa kleiner als 0

        # process rates:
        proc1 = mu_H*(S_S/(K_S+S_S))*(S_O/(K_OH+S_O))*X_BH
        proc2 = mu_H*(S_S/(K_S+S_S))*(K_OH/(K_OH+S_O))*(S_NO/(K_NO+S_NO))*ny_g*X_BH
        proc3 = mu_A*(S_NH/(K_NH+S_NH))*(S_O/(K_OA+S_O))*X_BA
        proc4 = b_H*X_BH
        proc5 = b_A*X_BA
        proc6 = k_a*S_ND*X_BH
        proc7 = k_h*((X_S/X_BH)/(K_X+(X_S/X_BH)))*((S_O/(K_OH+S_O))+ny_h*(K_OH/(K_OH+S_O))*(S_NO/(K_NO+S_NO)))*X_BH
        proc8 = proc7*(X_ND/X_S)

        # conversion rates:
        reac1 = 0.0
        reac2 = (-proc1-proc2)/Y_H+proc7
        reac3 = 0.0
        reac4 = (1.0-f_P)*(proc4+proc5)-proc7
        reac5 = proc1+proc2-proc4
        reac6 = proc3-proc5
        reac7 = f_P*(proc4+proc5)
        reac8 = -((1.0-Y_H)/Y_H)*proc1-((4.57-Y_A)/Y_A)*proc3
        reac9 = -((1.0-Y_H)/(2.86*Y_H))*proc2+proc3/Y_A
        reac10 = -i_XB*(proc1+proc2)-(i_XB+(1.0/Y_A))*proc3+proc6
        reac11 = -proc6+proc8
        reac12 = (i_XB-f_P*i_XP)*(proc4+proc5)-proc8
        reac13 = -i_XB/14.0*proc1+((1.0-Y_H)/(14.0*2.86*Y_H)-(i_XB/14.0))*proc2-((i_XB/14.0)+1.0/(7.0*Y_A))*proc3+proc6/14.0

        reac16 = 0.0
        reac17 = 0.0
        reac18 = 0.0
        reac19 = 0.0
        reac20 = 0.0

        # differential equations:
        dS_I = 1.0 / self.volume * (Q_in * (S_I_in - S_I)) + reac1
        dS_S = 1.0 / self.volume * (Q_in * (S_S_in - S_S)) + reac2
        dX_I = 1.0 / self.volume * (Q_in * (X_I_in - X_I)) + reac3
        dX_S = 1.0 / self.volume * (Q_in * (X_S_in - X_S)) + reac4
        dX_BH = 1.0 / self.volume * (Q_in * (X_BH_in - X_BH)) + reac5
        dX_BA = 1.0 / self.volume * (Q_in * (X_BA_in - X_BA)) + reac6
        dX_P = 1.0 / self.volume * (Q_in * (X_P_in - X_P)) + reac7
        dS_O = 1.0 / self.volume * (Q_in * (S_O_in - S_O)) + reac8+self.kla*(self.sosat-S_O) # wenn kla<0, dann dS_O = 0.0 --> einbauen?
        dS_NO = 1.0 / self.volume * (Q_in * (S_NO_in - S_NO)) + reac9
        dS_NH = 1.0 / self.volume * (Q_in * (S_NH_in - S_NH)) + reac10
        dS_ND = 1.0 / self.volume * (Q_in * (S_ND_in - S_ND)) + reac11
        dX_ND = 1.0 / self.volume * (Q_in * (X_ND_in - X_ND)) + reac12
        dS_ALK = 1.0 / self.volume * (Q_in * (S_ALK_in - S_ALK)) + reac13
        dTSS = 0.0
        dQ = 0.0
        dT = 0.0 # TEMPMODEL hier einbauen
        dS_D1 = 1.0 / self.volume * (Q_in * (S_D1_in - S_D1)) + reac16
        dS_D2 = 1.0 / self.volume * (Q_in * (S_D2_in - S_D2)) + reac17
        dS_D3 = 1.0 / self.volume * (Q_in * (S_D3_in - S_D3)) + reac18
        dX_D4 = 1.0 / self.volume * (Q_in * (X_D4_in - X_D4)) + reac19
        dX_D5 = 1.0 / self.volume * (Q_in * (X_D5_in - X_D5)) + reac20

        f = [dS_I, dS_S, dX_I, dX_S, dX_BH, dX_BA, dX_P, dS_O, dS_NO, dS_NH, dS_ND, dX_ND,
             dS_ALK, dTSS, dQ, dT, dS_D1, dS_D2, dS_D3, dX_D4, dX_D5]

        return f

    def output(self, timestep, step, y_in, parasm):
        t_span = [step-timestep, step+timestep]
        t_eval = np.arange(step-timestep, step+timestep, timestep)
        if len(t_eval) > 2:
            t_eval = np.array([t_eval[0], t_eval[1]])  # macht sonst teilweise einen zu großen Array
        sol = solve_ivp(self.derivatives, t_span, self.y0, t_eval=t_eval, args=(y_in, parasm,))
        y_out = np.array([x[1] for x in sol.y])
        self.y0 = y_out
        # ode = odeint(self.derivatives, y0, t_eval, tfirst=True, args=(y_in, parasm,))
        # y_out = ode[1]
        # print(z)

        # TSS fehlt noch!
        return y_out


# Initialization:

import asm1init
Qin = asm1init.Qin
Qintr = asm1init.Qintr
Qr = asm1init.Qr
Qw = asm1init.Qw

PAR = asm1init.PAR  #in Matlab wird nochmal aufgeteilt in die Reaktoren (aber ist immer gleich)

# definition of the reactors:
reactor1 = ASM1reactor(asm1init.VOL1, asm1init.KLa1, asm1init.SOSAT1, asm1init.XINIT1)
reactor2 = ASM1reactor(asm1init.VOL2, asm1init.KLa2, asm1init.SOSAT2, asm1init.XINIT2)
reactor3 = ASM1reactor(asm1init.VOL3, asm1init.KLa3, asm1init.SOSAT3, asm1init.XINIT3)
reactor4 = ASM1reactor(asm1init.VOL4, asm1init.KLa4, asm1init.SOSAT4, asm1init.XINIT4)
reactor5 = ASM1reactor(asm1init.VOL5, asm1init.KLa5, asm1init.SOSAT5, asm1init.XINIT5)


# nur zum ausprobieren:
y_in1 = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])

timestep = 15/(60*24)
time = np.arange(timestep, 3*15/(60*24), timestep)

for step in time:
    y_out1 = reactor1.output(timestep, step, y_in1, PAR)
    y_out2 = reactor2.output(timestep, step, y_out1, PAR)
    y_in1 = y_out2


