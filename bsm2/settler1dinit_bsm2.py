"""Initialisation file for all states and parameters related to the secondary clarifier.

All parameters and specifications are based on BSM1 model.

This file will be executed when running asm1runss.py or asm1run.py.
"""


import numpy as np

settlerinit = np.ones(120)
settlerinit[80:90] = 15
settlerinit[90:120] = 0

# parameters for Takács settler model, based on Alex et al (2018) (BSM1)
v0_max = 250
v0 = 474
r_h = 0.000576
r_p = 0.00286
f_ns = 0.00228
X_t = 3000
sb_limit = 3000

SETTLERPAR = np.array([v0_max, v0, r_h, r_p, f_ns, X_t])

area = 1500
height = 4

DIM = np.array([area, height])

# number of layers is flexible, default model is a 10 layer sedimentation tank
feedlayer = 5
nooflayers = 10

LAYER = np.array([feedlayer, nooflayers])


# to use model with nooflayers for solubles use MODELTYPE 0 (IWA/COST Benchmark)
# to use model with 1 layer for solubles use MODELTYPE 1 (GSP-X implementation) (not implemented yet)
# to use model with 0 layers for solubles use MODELTYPE 2 (old WEST implementation) (not implemented yet)
MODELTYPE = 0