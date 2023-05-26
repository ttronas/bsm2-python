"""Initialisation file for all states and parameters related to the secondary clarifier.

All state values are based on ASM3 implementation within BSM1 from Matlab-file settler1dinit_asm3.m

This file will be executed when running asm3runss.py or asm3run.py.
"""

import numpy as np

settlerinit = np.ones(190)
settlerinit[130:140] = 15
settlerinit[140:190] = 0

v0_max = 250
v0 = 474
r_h = 0.000576
r_p = 0.00286
f_ns = 0.00228
X_t = 3000

settlerpar = np.array([v0_max, v0, r_h, r_p, f_ns, X_t])


area = 1500
height = 4

dim = np.array([area, height])

feedlayer = 5
nooflayers = 10

layer = np.array([feedlayer, nooflayers])
