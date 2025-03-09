"""Initialisation file for all states and parameters related to the dewatering.

All parameters and specifications are based on BSM1 model.
This file will be executed when running `bsm2_cl.py`, `bsm2_ol.py` or `bsm2_olem.py`.
"""

import numpy as np

VOL_P = 900 # Volume of the primary clarifier (m3)
"""Volume of the primary clarifier [m^3^]."""

F_CORR = 0.65 # Efficiency correction
"""Efficiency correction factor [-]."""

F_X = 0.85 # CODpart/CODtot ratio
"""COD~part~/COD~tot~ ratio [-]."""

T_M = 0.125 # Smoothing time constant for qm calculation
"""Smoothing time constant for m^2^ calculation [d]."""

F_PS = 0.007 # Ratio of primary sludge flow rate to the influent flow
"""Ratio of primary sludge flow rate to the influent flow [-]."""

# Initial values
S_I_P = 28.0670
"""Soluble inert organic matter [g(COD) $\cdot$ m^-3^]."""
S_S_P = 59.0473
"""Readily biodegradable substrate [g(COD) $\cdot$ m^-3^]."""
X_I_P = 94.3557
"""Particulate inert organic matter [g(COD) $\cdot$ m^-3^]."""
X_S_P = 356.8434
"""Slowly biodegradable substrate [g(COD) $\cdot$ m^-3^]."""
X_BH_P = 50.8946
"""Active heterotrophic biomass [g(COD) $\cdot$ m^-3^]."""
X_BA_P = 0.0946
"""Active autotrophic biomass [g(COD) $\cdot$ m^-3^]."""
X_P_P = 0.6531
"""Particulate products arising from biomass decay [g(COD) $\cdot$ m^-3^]."""
S_O_P = 0.0175
"""Dissolved oxygen [g(O~2~) $\cdot$ m^-3^]."""
S_NO_P = 0.1174
"""Nitrate and nitrite [g(N) $\cdot$ m^-3^]."""
S_NH_P = 34.9215
"""Ammonium plus ammonia nitrogen [g(N) $\cdot$ m^-3^]."""
S_ND_P = 5.5457
"""Soluble biodegradable organic nitrogen [g(N) $\cdot$ m^-3^]."""
X_ND_P = 15.8132
"""Particulate biodegradable organic nitrogen [g(N) $\cdot$ m^-3^]."""
S_ALK_P = 7.6965
"""Alkalinity [mol(HCO$_3^-$) $\cdot$ m^-3^]."""
TSS_P = 377.1311
"""Total suspended solids [g(TSS) $\cdot$ m^-3^]."""
Q_P = 2.1086e04
"""Flow rate [m^3^ $\cdot$ d^-1^]."""
T_P = 14.8581
"""Temperature [°C]."""
S_D1_P = 0
"""Dummy state 1 [-]."""
S_D2_P = 0
"""Dummy state 2 [-]."""
S_D3_P = 0
"""Dummy state 3 [-]."""
X_D4_P = 0
"""Dummy state 4 [-]."""
X_D5_P = 0
"""Dummy state 5 [-]."""

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
"""Initial values for the primary clarifier."""

# Vector with settleability of the 21 components of ASM1,
# compare with f_sx,i in Otterpohl/Freund
XVECTOR_P = np.array([0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1], dtype=bool)
"""Vector with settleability of the 21 components of ASM1. Compare with f_sx,i in Otterpohl/Freund."""

PAR_P = np.array([F_CORR, F_X, T_M, F_PS])
"""Parameters for the primary clarifier."""
