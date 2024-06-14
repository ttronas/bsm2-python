"""Initialisation file for all states and parameters related to the AS systems (reactors 1-5)

All parameters and specifications are based on BSM1 model.

This file will be executed when running asm1runss.py or asm1run.py.
"""

import numpy as np

# flows:
QIN0 = 18446

QIN = QIN0
QINTR = 3 * QIN0
QR = QIN0
QW = 385

YINIT1 = np.ones(21)
YINIT1[16:21] = 0

YINIT2 = YINIT1
YINIT3 = YINIT1
YINIT4 = YINIT1
YINIT5 = YINIT1

# parameters for AS system at 15 degC, based on Alex et al (2018) (BSM1)
MU_H = 4.0
K_S = 10.0
K_OH = 0.2
K_NO = 0.5
B_H = 0.3
MU_A = 0.5
K_NH = 1.0
K_OA = 0.4
B_A = 0.05
NY_G = 0.8
K_A = 0.05
K_H = 3.0
K_X = 0.1
NY_H = 0.8
Y_H = 0.67
Y_A = 0.24
F_P = 0.08
I_XB = 0.08
I_XP = 0.06
X_I2TSS = 0.75
X_S2TSS = 0.75
X_BH2TSS = 0.75
X_BA2TSS = 0.75
X_P2TSS = 0.75

PAR1 = np.array(
    [
        MU_H,
        K_S,
        K_OH,
        K_NO,
        B_H,
        MU_A,
        K_NH,
        K_OA,
        B_A,
        NY_G,
        K_A,
        K_H,
        K_X,
        NY_H,
        Y_H,
        Y_A,
        F_P,
        I_XB,
        I_XP,
        X_I2TSS,
        X_S2TSS,
        X_BH2TSS,
        X_BA2TSS,
        X_P2TSS,
    ]
)
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
KLA1 = 0
KLA2 = 0
KLA3 = 240
KLA4 = 240
KLA5 = 84

# external carbon flow rates for reactor 1 to 5:
CARB1 = 0
CARB2 = 0
CARB3 = 0
CARB4 = 0
CARB5 = 0
# external carbon source concentration = 400000 mg COD / L from BSM1
CARBONSOURCECONC = 400000
