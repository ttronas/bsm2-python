"""Initialisation file for all states and parameters related to the secondary clarifier.

All parameters and specifications are based on BSM1 model.

This file will be executed when running the asm1run or asm1runss file.
"""


import numpy as np

settlerinit = np.ones(120)
# settlerinit[0:90] = np.random.rand(90)
settlerinit[90:120] = 0

v0_max = 250
v0 = 474
r_h = 0.000576
r_p = 0.00286
f_ns = 0.00228
X_t = 3000

SETTLERPAR = np.array([v0_max, v0, r_h, r_p, f_ns, X_t])

area = 1500
height = 4

DIM = np.array([area, height])

# layers are flexible, default model is a 10 layer sedimentation tank
feedlayer = 5
nooflayers = 10

LAYER = np.array([feedlayer, nooflayers])
