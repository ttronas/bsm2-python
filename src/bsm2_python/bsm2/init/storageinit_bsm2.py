"""Initialisation file for the sludge storage"""

import numpy as np

# Maximum volume of the sludge storage tank (m3)
VOL_S = 160

# Initial values for the sludge storage
S_I_S = 140.1528
S_S_S = 260.0720
X_I_S = 363.7842
X_S_S = 57.1637
X_BH_S = 0
X_BA_S = 0
X_P_S = 13.7743
S_O_S = 0
S_NO_S = 0
S_NH_S = 1.5685e03
S_ND_S = 0.4786
X_ND_S = 2.2039
S_ALK_S = 106.8816
TSS_S = 326.0416
Q_S = 0
T_S = 14.8581
S_D1_S = 0
S_D2_S = 0
S_D3_S = 0
X_D4_S = 0
X_D5_S = 0
VOL_INIT_S = VOL_S * 0.5  # Initial liquid volume in storage tank

ystinit = np.array(
    [
        S_I_S,
        S_S_S,
        X_I_S,
        X_S_S,
        X_BH_S,
        X_BA_S,
        X_P_S,
        S_O_S,
        S_NO_S,
        S_NH_S,
        S_ND_S,
        X_ND_S,
        S_ALK_S,
        TSS_S,
        Q_S,
        T_S,
        S_D1_S,
        S_D2_S,
        S_D3_S,
        X_D4_S,
        X_D5_S,
        VOL_INIT_S,
    ]
)
