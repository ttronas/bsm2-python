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

settlerinit = np.ones(12*nooflayers)

# settlerinit[0:nooflayers] = np.linspace(np.sqrt(14.3255), np.sqrt(7.3483e3), nooflayers)**2  # TSS
settlerinit[0:nooflayers] = np.array([14.3255, 20.8756, 34.2948, 81.0276, 423.2035, 423.2035, 423.2035, 423.2035, 3.7106e+03, 7.3483e+03])
settlerinit[nooflayers:2*nooflayers] = 28.0643         # SI
settlerinit[2*nooflayers:3*nooflayers] = 0.6734        # SS
settlerinit[3*nooflayers:4*nooflayers] = 1.3748        # SO
settlerinit[4*nooflayers:5*nooflayers] = 9.1948        # SNO
settlerinit[5*nooflayers:6*nooflayers] = 0.1585        # SNH
settlerinit[6*nooflayers:7*nooflayers] = 0.5594        # SND
settlerinit[7*nooflayers:8*nooflayers] = 4.5646        # SALK
settlerinit[8*nooflayers:110*nooflayers] = 0           # dummy states
settlerinit[110*nooflayers:120*nooflayers] = 14.8581   # T

LAYER = np.array([feedlayer, nooflayers])


# to use model with nooflayers for solubles use MODELTYPE 0 (IWA/COST Benchmark)
# to use model with 1 layer for solubles use MODELTYPE 1 (GSP-X implementation) (not implemented yet)
# to use model with 0 layers for solubles use MODELTYPE 2 (old WEST implementation) (not implemented yet)
MODELTYPE = 0