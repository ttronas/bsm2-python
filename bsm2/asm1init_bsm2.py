"""Initialisation file for all states and parameters related to the AS systems (reactors 1-5)

All parameters and specifications are based on BSM1 model.

This file will be executed when running asm1runss.py or asm1run.py.
"""


import numpy as np

# flows:
Qin0 = 20648

Qin = Qin0
Qintr = 3*Qin0
Qr = Qin0
Qw = 300

yinit1 = np.ones(21)
yinit1[16:21] = 0

yinit2 = yinit1
yinit3 = yinit1
yinit4 = yinit1
yinit5 = yinit1

S_I1 =  28.0643
S_S1 =  3.0503
X_I1 =  1532.3
X_S1 =  63.0433
X_BH1 = 2245.1
X_BA1 = 166.6699
X_P1 =  964.8992
S_O1 =  0.0093
S_NO1 = 3.9350
S_NH1 = 6.8924
S_ND1 = 0.9580
X_ND1 = 3.8453
S_ALK1 = 5.4213
TSS1 = 3729.0
Q1 = 103533
T1 = 14.8581
S_D1_1 = 0
S_D2_1 = 0
S_D3_1 = 0
X_D4_1 = 0
X_D5_1 = 0

yinit1 = np.array([S_I1, S_S1, X_I1, X_S1, X_BH1, X_BA1, X_P1, S_O1, S_NO1, S_NH1, S_ND1, X_ND1, S_ALK1, TSS1, Q1, T1, S_D1_1, S_D2_1, S_D3_1, X_D4_1, X_D5_1])

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

PAR1 = np.array([mu_H, K_S, K_OH, K_NO, b_H, mu_A, K_NH, K_OA, b_A, ny_g, k_a, k_h, K_X, ny_h, Y_H, Y_A, f_P,
                 i_XB, i_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS])
PAR2 = PAR1
PAR3 = PAR1
PAR4 = PAR1
PAR5 = PAR1

# reactor volumes:
VOL1 = 1500
VOL2 = VOL1
VOL3 = 3000
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
KLa3 = 120
KLa4 = 120
KLa5 = 60

# external carbon flow rates for reactor 1 to 5:
carb1 = 2
carb2 = 0
carb3 = 0
carb4 = 0
carb5 = 0
# external carbon source concentration = 400000 mg COD / L from BSM1
carbonsourceconc = 400000

