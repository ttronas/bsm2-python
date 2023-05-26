"""Initialisation file for all states and parameters for asm3 related to the AS systems (reactors 1-5)

All state values are based on ASM3 implementation within BSM1 from Matlab-file asm3init.m

This file will be executed when running the asm3runss.py or asm3run.py.
"""

import numpy as np

Qin = 18446
Qintr = 3*Qin
Qr = Qin
Qw = 385

yinit1 = np.ones(20)
yinit1[13] = Qin
yinit1[15:20] = 0
yinit2 = yinit1
yinit3 = yinit1
yinit4 = yinit1
yinit5 = yinit1

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

# oxygen saturation concentration at 15 degC, based on BSM1
SOSAT1 = 8
SOSAT2 = SOSAT1
SOSAT3 = SOSAT1
SOSAT4 = SOSAT1
SOSAT5 = SOSAT1

# Default KLa (oxygen transfer coefficient) values for AS reactors:
kla1 = 0
kla2 = 0
kla3 = 240
kla4 = 240
kla5 = 84

# external carbon flow rates for reactor 1 to 5:
carb1 = 0
carb2 = 0
carb3 = 0
carb4 = 0
carb5 = 0
# external carbon source concentration = 400000 mg COD / L from BSM1
carbonsourceconc = 400000
