"""Initialisation file for the primary clarifier"""

import numpy as np

# Volume of the primary clarifier (m3)
VOL_P = 900

# Efficiency correction
F_CORR = 0.65

# CODpart/CODtot ratio
F_X = 0.85

# Smoothing time constant for qm calculation
T_M = 0.125

# Ratio of primary sludge flow rate to the influent flow
F_PS = 0.007

# Initial values
S_I_P = 28.0670
S_S_P = 59.0473
X_I_P = 94.3557
X_S_P = 356.8434
X_BH_P = 50.8946
X_BA_P = 0.0946
X_P_P = 0.6531
S_O_P = 0.0175
S_NO_P = 0.1174
S_NH_P = 34.9215
S_ND_P = 5.5457
X_ND_P = 15.8132
S_ALK_P = 7.6965
TSS_P = 377.1311
Q_P = 2.1086e04
T_P = 14.8581
S_D1_P = 0
S_D2_P = 0
S_D3_P = 0
X_D4_P = 0
X_D5_P = 0

YINIT1 = np.array(
    [
        S_I_P,
        S_S_P,
        X_I_P,
        X_S_P,
        X_BH_P,
        X_BA_P,
        X_P_P,
        S_O_P,
        S_NO_P,
        S_NH_P,
        S_ND_P,
        X_ND_P,
        S_ALK_P,
        TSS_P,
        Q_P,
        T_P,
        S_D1_P,
        S_D2_P,
        S_D3_P,
        X_D4_P,
        X_D5_P,
    ]
)

# Vector with settleability of the 21 components of ASM1,
# compare with f_sx,i in Otterpohl/Freund
XVECTOR_P = np.array([0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1], dtype=bool)

PAR_P = np.array([F_CORR, F_X, T_M, F_PS])
