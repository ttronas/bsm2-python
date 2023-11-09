"""Initialisation file for the sludge storage"""

import numpy as np

# Volume of the primary clarifier (m3)
VOL_S = 160

# Initial values for the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states) and initial storage volume
ystinit = np.ones(22)
ystinit[16:21] = 0  # dummy states
ystinit[21] = VOL_S * 0.5
