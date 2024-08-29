"""Initialisation file for all states and parameters related to the secondary clarifier.

All parameters and specifications are based on BSM1 model.

This file will be executed when running asm1runss.py or asm1run.py.
"""

import numpy as np

# parameters for Takács settler model, based on Alex et al (2018) (BSM1)
v0_max = 250
v0 = 474
r_h = 0.000576
r_p = 0.00286
f_ns = 0.00228
X_t = 3000
sb_limit = 3000

SETTLERPAR = np.array([v0_max, v0, r_h, r_p, f_ns, X_t, sb_limit])

area = 1500
height = 4

DIM = np.array([area, height])

# number of layers is flexible, default model is a 10 layer sedimentation tank
feedlayer = 5
nooflayers = 10

settlerinit = np.zeros(12 * nooflayers)
settlerinit[0 * nooflayers : 1 * nooflayers] = 28.0643  # SI
settlerinit[1 * nooflayers : 2 * nooflayers] = 0.6734  # S_S
settlerinit[2 * nooflayers : 3 * nooflayers] = 1.3748  # S_O
settlerinit[3 * nooflayers : 4 * nooflayers] = 9.1948  # S_NO
settlerinit[4 * nooflayers : 5 * nooflayers] = 0.1585  # S_NH
settlerinit[5 * nooflayers : 6 * nooflayers] = 0.5594  # S_ND
settlerinit[6 * nooflayers : 7 * nooflayers] = 4.5646  # S_ALK
settlerinit[7 * nooflayers : 8 * nooflayers] = [
    14.3255,
    20.8756,
    34.2948,
    81.0276,
    423.2035,
    423.2035,
    423.2035,
    423.2035,
    3.7106e03,
    7.3483e03,
]  # TSS
settlerinit[8 * nooflayers : 9 * nooflayers] = 14.8581  # T
settlerinit[9 * nooflayers : 12 * nooflayers] = 0  # soluble dummy states

LAYER = np.array((feedlayer, nooflayers))


# to use model with nooflayers for solubles use MODELTYPE 0 (IWA/COST Benchmark)
# to use model with 1 layer for solubles use MODELTYPE 1 (GSP-X implementation) (not implemented yet)
# to use model with 0 layers for solubles use MODELTYPE 2 (old WEST implementation) (not implemented yet)
MODELTYPE = 0
