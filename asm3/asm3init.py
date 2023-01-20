"""Initialisation file for all states and parameters for asm3 related to the AS systems (reactors 1-5)

All state values are based on ASM3 implementation within BSM1 from Matlab-file asm3init.m

This file will be executed when running the asm3run or asm3runss file.
"""

import numpy as np

Qin = 18446
Qintr = 3*Qin
Qr = Qin
Qw = 385

S_O2_1 = 2
S_I_1 = 30
S_S_1 = 2
S_NH4_1 = 20
S_N2_1 = 0
S_NOX_1 = 0
S_ALK_1 = 5
X_I_1 = 100
X_S_1 = 40
X_H_1 = 100
X_STO_1 = 40
X_A_1 = 1
X_SS_1 = 200
Q_1 = Qin + Qr + Qintr
T_1 = 14.8581
S_D1_1 = 0
S_D2_1 = 0
S_D3_1 = 0
X_D4_1 = 0
X_D5_1 = 0

S_O2_2 = 2
S_I_2 = 30
S_S_2 = 2
S_NH4_2 = 20
S_N2_2 = 0
S_NOX_2 = 0
S_ALK_2 = 5
X_I_2 = 100
X_S_2 = 40
X_H_2 = 100
X_STO_2 = 40
X_A_2 = 1
X_SS_2 = 200
Q_2 = Qin + Qr + Qintr
T_2 = 14.8581
S_D1_2 = 0
S_D2_2 = 0
S_D3_2 = 0
X_D4_2 = 0
X_D5_2 = 0

S_O2_3 = 2
S_I_3 = 30
S_S_3 = 2
S_NH4_3 = 20
S_N2_3 = 0
S_NOX_3 = 0
S_ALK_3 = 5
X_I_3 = 100
X_S_3 = 40
X_H_3 = 100
X_STO_3 = 40
X_A_3 = 1
X_SS_3 = 200
Q_3 = Qin + Qr + Qintr
T_3 = 14.8581
S_D1_3 = 0
S_D2_3 = 0
S_D3_3 = 0
X_D4_3 = 0
X_D5_3 = 0

S_O2_4 = 2
S_I_4 = 30
S_S_4 = 2
S_NH4_4 = 20
S_N2_4 = 0
S_NOX_4 = 0
S_ALK_4 = 5
X_I_4 = 100
X_S_4 = 40
X_H_4 = 100
X_STO_4 = 40
X_A_4 = 1
X_SS_4 = 200
Q_4 = Qin + Qr + Qintr
T_4 = 14.8581
S_D1_4 = 0
S_D2_4 = 0
S_D3_4 = 0
X_D4_4 = 0
X_D5_4 = 0

S_O2_5 = 2
S_I_5 = 30
S_S_5 = 2
S_NH4_5 = 20
S_N2_5 = 0
S_NOX_5 = 0
S_ALK_5 = 5
X_I_5 = 100
X_S_5 = 40
X_H_5 = 100
X_STO_5 = 40
X_A_5 = 1
X_SS_5 = 200
Q_5 = Qin + Qr + Qintr
T_5 = 14.8581
S_D1_5 = 0
S_D2_5 = 0
S_D3_5 = 0
X_D4_5 = 0
X_D5_5 = 0

yinit1 = np.array([S_O2_1, S_I_1, S_S_1, S_NH4_1, S_N2_1, S_NOX_1, S_ALK_1, X_I_1, X_S_1, X_H_1, X_STO_1, X_A_1, X_SS_1,
                   Q_1, T_1, S_D1_1, S_D2_1, S_D3_1, X_D4_1, X_D5_1])
yinit2 = np.array([S_O2_2, S_I_2, S_S_2, S_NH4_2, S_N2_2, S_NOX_2, S_ALK_2, X_I_2, X_S_2, X_H_2, X_STO_2, X_A_2, X_SS_2,
                   Q_2, T_2, S_D1_2, S_D2_2, S_D3_2, X_D4_2, X_D5_2])
yinit3 = np.array([S_O2_3, S_I_3, S_S_3, S_NH4_3, S_N2_3, S_NOX_3, S_ALK_3, X_I_3, X_S_3, X_H_3, X_STO_3, X_A_3, X_SS_3,
                   Q_3, T_3, S_D1_3, S_D2_3, S_D3_3, X_D4_3, X_D5_3])
yinit4 = np.array([S_O2_4, S_I_4, S_S_4, S_NH4_4, S_N2_4, S_NOX_4, S_ALK_4, X_I_4, X_S_4, X_H_4, X_STO_4, X_A_4, X_SS_4,
                   Q_4, T_4, S_D1_4, S_D2_4, S_D3_4, X_D4_4, X_D5_4])
yinit5 = np.array([S_O2_5, S_I_5, S_S_5, S_NH4_5, S_N2_5, S_NOX_5, S_ALK_5, X_I_5, X_S_5, X_H_5, X_STO_5, X_A_5, X_SS_5,
                   Q_5, T_5, S_D1_5, S_D2_5, S_D3_5, X_D4_5, X_D5_5])

# kinetic parameters of asm3 at 20 °C from Gujer, 1999 (Table 3)
k_H = 3
K_X = 1
k_STO = 5
ny_NOX = 0.6
K_O2 = 0.2
K_NOX = 0.5
K_S = 2
K_STO = 1
mu_H = 2
K_NH4 = 0.01
K_ALK = 0.1
b_HO2 = 0.2
b_HNOX = 0.1
b_STOO2 = 0.2
b_STONOX = 0.1
mu_A = 1.0
K_ANH4 = 1
K_AO2 = 0.5
K_AALK = 0.5
b_AO2 = 0.15
b_ANOX = 0.05

# stoichiometric and composition parameters for asm3 from Gujer, 1999 (Table 4)
f_SI = 0
Y_STOO2 = 0.85
Y_STONOX = 0.80
Y_HO2 = 0.63
Y_HNOX = 0.54
Y_A = 0.24
f_XI = 0.20     # from stoichiometric matrix of ASM3 from Gujer, 1999 (Table 6)
i_NSI = 0.01
i_NSS = 0.03
i_NXI = 0.02
i_NXS = 0.04
i_NBM = 0.07
i_SSXI = 0.75
i_SSXS = 0.75
i_SSBM = 0.90
i_SSSTO = 0.60  # from stoichiometric matrix of ASM3 from Gujer, 1999 (Table 1)

par1 = np.array([k_H, K_X, k_STO, ny_NOX, K_O2, K_NOX, K_S, K_STO, mu_H, K_NH4, K_ALK, b_HO2, b_HNOX, b_STOO2, b_STONOX, mu_A, K_ANH4, K_AO2, K_AALK, b_AO2, b_ANOX, f_SI, Y_STOO2, Y_STONOX, Y_HO2, Y_HNOX, Y_A, f_XI, i_NSI, i_NSS, i_NXI, i_NXS, i_NBM, i_SSXI, i_SSXS, i_SSBM, i_SSSTO])
par2 = par1
par3 = par1
par4 = par1
par5 = par1

# reactor volumes:
vol1 = 1000
vol2 = vol1
vol3 = 1333
vol4 = vol3
vol5 = vol3

# sosat lasse ich jetzt weg, da es überhaupt nicht benutzt wird

# Default KLa (oxygen transfer coefficient) values for AS reactors:
kla1 = 0
kla2 = 0
kla3 = 240
kla4 = 240
kla5 = 240

# external carbon flow rates for reactor 1 to 5:
carb1 = 0
carb2 = 0
carb3 = 0
carb4 = 0
carb5 = 0
# external carbon source concentration = 400000 mg COD / L from BSM1
carbonsourceconc = 400000
