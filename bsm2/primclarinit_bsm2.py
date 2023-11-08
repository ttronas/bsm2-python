"""Initialisation file for the primary clarifier"""

import numpy as np

# Volume of the primary clarifier (m3)
VOL_P = 900

# Efficiency correction
f_corr = 0.65

# CODpart/CODtot ratio
f_X = 0.85

# Smoothing time constant for qm calculation
t_m = 0.125

# Ratio of primary sludge flow rate to the influent flow
f_PS = 0.007

# Initial values for the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
yinit1 = np.ones(21)
yinit1[16:21] = 0

# Vector with settleability of the 21 components of ASM1,
# compare with f_sx,i in Otterpohl/Freund
XVECTOR_P = np.array([0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1], dtype=bool)

PAR_P = np.array([f_corr, f_X, t_m, f_PS])
