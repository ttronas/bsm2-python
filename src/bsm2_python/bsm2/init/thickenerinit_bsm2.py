"""Initialisation file for all states and parameters related to the Thickener

All parameters and specifications are based on BSM2 model.

This file will be executed when running bsm2runss.py.
"""

import numpy as np

thickener_perc = 7  # %TSS in thickener underflow
TSS_removal_perc = 98  # %TSS removed from the thickener overflow
X_I2TSS = 0.75
X_S2TSS = 0.75
X_BH2TSS = 0.75
X_BA2TSS = 0.75
X_P2TSS = 0.75

THICKENERPAR = np.array([thickener_perc, TSS_removal_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS])
