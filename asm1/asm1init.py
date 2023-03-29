"""Initialisation file for all states and parameters related to the AS systems (reactors 1-5)

All parameters and specifications are based on BSM1 model.

This file will be executed when running the asm1run or asm1runss file.
"""


import numpy as np

# flows:
Qin0 = 18446

Qin = Qin0
Qintr = 3*Qin0
Qr = Qin0
Qw = 385

yinit1 = np.ones(21)
# yinit1[0:15] = np.random.rand(15)
yinit1[16:21] = 0

yinit2 = yinit1
yinit3 = yinit1
yinit4 = yinit1
yinit5 = yinit1

# parameters for AS system at 15 degC, based on Alex et al (2018) (BSM1)
mu_H = 4.0
K_S = 10.0
K_OH = 0.2
K_NO = 0.5
b_H = 0.3
mu_A = 0.5
K_NH = 1.0
K_OA = 0.4
b_A = 0.05
ny_g = 0.8
k_a = 0.05
k_h = 3.0
K_X = 0.1
ny_h = 0.8
Y_H = 0.67
Y_A = 0.24
f_P = 0.08
i_XB = 0.08
i_XP = 0.06
X_I2TSS = 0.75
X_S2TSS = 0.75
X_BH2TSS = 0.75
X_BA2TSS = 0.75
X_P2TSS = 0.75

# Additional parameters (e- decay dependency)

hH_NO3_end = 0.5    # Anoxic reduction factor for endogenous respiration
hA_NO3_end = 0.33   # Anoxic reduction factor for decay of autotrophs

PAR1 = np.array([mu_H, K_S, K_OH, K_NO, b_H, mu_A, K_NH, K_OA, b_A, ny_g, k_a, k_h, K_X, ny_h, Y_H, Y_A, f_P,
                 i_XB, i_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS, hH_NO3_end, hA_NO3_end])
PAR2 = PAR1
PAR3 = PAR1
PAR4 = PAR1
PAR5 = PAR1

# reactor volumes:
VOL1 = 1000
VOL2 = VOL1
VOL3 = 1333
VOL4 = VOL3
VOL5 = VOL3

# oxygen saturation concentration at 15 degC, based on BSM1
SOSAT1 = 8
SOSAT2 = SOSAT1
SOSAT3 = SOSAT1
SOSAT4 = SOSAT1
SOSAT5 = SOSAT1

# Default KLa (oxygen transfer coefficient) values for AS reactors:
KLa1 = 0
KLa2 = 0
KLa3 = 240
KLa4 = 240
KLa5 = 144

# external carbon flow rates for reactor 1 to 5:
carb1 = 0
carb2 = 0
carb3 = 0
carb4 = 0
carb5 = 0
# external carbon source concentration = 400000 mg COD / L from BSM1
carbonsourceconc = 400000

