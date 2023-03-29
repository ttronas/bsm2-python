"""Initialisation file for all states and parameters related to the secondary clarifier.

All state values are based on Matlab/Simulink implementation.

This file will be executed when running the asm3run or asm3runss file.
"""


import numpy as np

# settlerinit = np.ones(120)
# settlerinit[90:120] = 0
SO_1 = 2
SO_2 = 2
SO_3 = 2
SO_4 = 2
SO_5 = 2
SO_6 = 2
SO_7 = 2
SO_8 = 2
SO_9 = 2
SO_10 = 2

SI_1 = 0.80801
SI_2 = 0.80801
SI_3 = 0.80801
SI_4 = 0.80801
SI_5 = 0.80801
SI_6 = 0.80801
SI_7 = 0.80801
SI_8 = 0.80801
SI_9 = 0.80801
SI_10 = 0.80801

SS_1 = 0.80801
SS_2 = 0.80801
SS_3 = 0.80801
SS_4 = 0.80801
SS_5 = 0.80801
SS_6 = 0.80801
SS_7 = 0.80801
SS_8 = 0.80801
SS_9 = 0.80801
SS_10 = 0.80801

SNH_1 = 0.67193
SNH_2 = 0.67193
SNH_3 = 0.67193
SNH_4 = 0.67193
SNH_5 = 0.67193
SNH_6 = 0.67193
SNH_7 = 0.67193
SNH_8 = 0.67193
SNH_9 = 0.67193
SNH_10 = 0.67193

SN2_1 = 13.5243
SN2_2 = 13.5243
SN2_3 = 13.5243
SN2_4 = 13.5243
SN2_5 = 13.5243
SN2_6 = 13.5243
SN2_7 = 13.5243
SN2_8 = 13.5243
SN2_9 = 13.5243
SN2_10 = 13.5243

SNO3_1 = 2
SNO3_2 = 2
SNO3_3 = 2
SNO3_4 = 2
SNO3_5 = 2
SNO3_6 = 2
SNO3_7 = 2
SNO3_8 = 2
SNO3_9 = 2
SNO3_10 = 2

SALK_1 = 3.8277
SALK_2 = 3.8277
SALK_3 = 3.8277
SALK_4 = 3.8277
SALK_5 = 3.8277
SALK_6 = 3.8277
SALK_7 = 3.8277
SALK_8 = 3.8277
SALK_9 = 3.8277
SALK_10 = 3.8277

XSS_1 = 10
XSS_2 = 20
XSS_3 = 30
XSS_4 = 70
XSS_5 = 400
XSS_6 = 400
XSS_7 = 400
XSS_8 = 400
XSS_9 = 400
XSS_10 = 4000

T_1 = 14.8581
T_2 = 14.8581
T_3 = 14.8581
T_4 = 14.8581
T_5 = 14.8581
T_6 = 14.8581
T_7 = 14.8581
T_8 = 14.8581
T_9 = 14.8581
T_10 = 14.8581

SD1_1 = 0
SD1_2 = 0
SD1_3 = 0
SD1_4 = 0
SD1_5 = 0
SD1_6 = 0
SD1_7 = 0
SD1_8 = 0
SD1_9 = 0
SD1_10 = 0

SD2_1 = 0
SD2_2 = 0
SD2_3 = 0
SD2_4 = 0
SD2_5 = 0
SD2_6 = 0
SD2_7 = 0
SD2_8 = 0
SD2_9 = 0
SD2_10 = 0

SD3_1 = 0
SD3_2 = 0
SD3_3 = 0
SD3_4 = 0
SD3_5 = 0
SD3_6 = 0
SD3_7 = 0
SD3_8 = 0
SD3_9 = 0
SD3_10 = 0

settlerinit = np.array([SO_1, SO_2, SO_3, SO_4, SO_5, SO_6, SO_7, SO_8, SO_9, SO_10, SI_1, SI_2, SI_3, SI_4, SI_5, SI_6, SI_7, SI_8, SI_9, SI_10,
               SS_1, SS_2, SS_3, SS_4, SS_5, SS_6, SS_7, SS_8, SS_9, SS_10, SNH_1, SNH_2, SNH_3, SNH_4, SNH_5, SNH_6, SNH_7, SNH_8,
               SNH_9, SNH_10, SN2_1, SN2_2, SN2_3, SN2_4, SN2_5, SN2_6, SN2_7, SN2_8, SN2_9, SN2_10, SNO3_1, SNO3_2, SNO3_3, SNO3_4,
               SNO3_5, SNO3_6, SNO3_7, SNO3_8, SNO3_9, SNO3_10, SALK_1, SALK_2, SALK_3, SALK_4, SALK_5, SALK_6, SALK_7, SALK_8,
               SALK_9, SALK_10, XSS_1, XSS_2, XSS_3, XSS_4, XSS_5, XSS_6, XSS_7, XSS_8, XSS_9, XSS_10, T_1, T_2, T_3, T_4, T_5,
               T_6, T_7, T_8, T_9, T_10, SD1_1, SD1_2, SD1_3, SD1_4, SD1_5, SD1_6, SD1_7, SD1_8, SD1_9, SD1_10, SD2_1, SD2_2,
               SD2_3, SD2_4, SD2_5, SD2_6, SD2_7, SD2_8, SD2_9, SD2_10, SD3_1, SD3_2, SD3_3, SD3_4, SD3_5, SD3_6, SD3_7, SD3_8, SD3_9,
               SD3_10])

v0_max = 250
v0 = 474
r_h = 0.000576     # (0.148 + 0.00210 * 100)/1000    # 0.000576    # (0.148 + 0.00210 * 100)/1000   # Änderung: berechnen in WEST diesen Parameter so, statt 0.000576
r_p = 0.00286
f_ns = 0.00228
X_t = 3000

settlerpar = np.array([v0_max, v0, r_h, r_p, f_ns, X_t])


area = 1500
height = 4

dim = np.array([area, height])

# layers are flexible, default model is a 10 layer sedimentation tank
feedlayer = 5
nooflayers = 10

layer = np.array([feedlayer, nooflayers])