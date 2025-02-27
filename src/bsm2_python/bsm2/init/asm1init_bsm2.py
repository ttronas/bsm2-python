"""Initialisation file for all states and parameters related to the AS systems (reactors 1-5).

All parameters and specifications are based on BSM1 model.
This file will be executed when running `bsm2_cl.py`, `bsm2_ol.py` or `bsm2_olem.py`.
"""

import numpy as np

# flows:
QIN0 = 20648
"""Flow rate of influent [m^3^ $\cdot$ d^-1^]."""

QIN = QIN0
"""Flow rate of influent [m^3^ $\cdot$ d^-1^]."""
QINTR = 3 * QIN0
"""Flow rate of internal recirculation [m^3^ $\cdot$ d^-1^]."""
QR = QIN0
"""Flow rate of sludge return. [m^3^ $\cdot$ d^-1^]."""
QW = 300
"""Flow rate of waste sludge [m^3^ $\cdot$ d^-1^]."""

# The following states represent concentrations in different AS reactors (1 to 5)

S_I1 = 28.0643
S_S1 = 3.0503
X_I1 = 1532.3
X_S1 = 63.0433
X_BH1 = 2245.1
X_BA1 = 166.6699
X_P1 = 964.8992
S_O1 = 0.0093
S_NO1 = 3.9350
S_NH1 = 6.8924
S_ND1 = 0.9580
X_ND1 = 3.8453
S_ALK1 = 5.4213
TSS1 = 3729.0
Q1 = 103533
T1 = 14.8581
S_D1_1 = 0
S_D2_1 = 0
S_D3_1 = 0
X_D4_1 = 0
X_D5_1 = 0

S_I2 = 28.0643
S_S2 = 1.3412
X_I2 = 1532.3
X_S2 = 58.8579
X_BH2 = 2245.4
X_BA2 = 166.5512
X_P2 = 965.6805
S_O2 = 1.0907e-4
S_NO2 = 2.2207
S_NH2 = 7.2028
S_ND2 = 0.6862
X_ND2 = 3.7424
S_ALK2 = 5.5659
TSS2 = 3726.6
Q2 = 103533
T2 = 14.8581
S_D1_2 = 0
S_D2_2 = 0
S_D3_2 = 0
X_D4_2 = 0
X_D5_2 = 0

S_I3 = 28.0643
S_S3 = 0.9553
X_I3 = 1532.3
X_S3 = 46.2983
X_BH3 = 2246.8
X_BA3 = 167.3077
X_P3 = 967.2442
S_O3 = 0.4663
S_NO3 = 5.5141
S_NH3 = 3.4247
S_ND3 = 0.6513
X_ND3 = 3.1405
S_ALK3 = 5.0608
TSS3 = 3719.9
Q3 = 103533
T3 = 14.8581
S_D1_3 = 0
S_D2_3 = 0
S_D3_3 = 0
X_D4_3 = 0
X_D5_3 = 0

S_I4 = 28.0643
S_S4 = 0.7806
X_I4 = 1532.3
X_S4 = 37.3881
X_BH4 = 2245.6
X_BA4 = 167.8339
X_P4 = 968.8072
S_O4 = 1.4284
S_NO4 = 8.4066
S_NH4 = 0.6922
S_ND4 = 0.6094
X_ND4 = 2.6815
S_ALK4 = 4.6590
TSS4 = 3713.9
Q4 = 103533
T4 = 14.8581
S_D1_4 = 0
S_D2_4 = 0
S_D3_4 = 0
X_D4_4 = 0
X_D5_4 = 0

S_I5 = 28.0643
S_S5 = 0.6734
X_I5 = 1532.3
X_S5 = 31.9144
X_BH5 = 2242.1
X_BA5 = 167.8482
X_P5 = 970.3678
S_O5 = 1.3748
S_NO5 = 9.1948
S_NH5 = 0.1585
S_ND5 = 0.5594
X_ND5 = 2.3926
S_ALK5 = 4.5646
TSS5 = 3708.4
Q5 = 103533
T5 = 14.8581
S_D1_5 = 0
S_D2_5 = 0
S_D3_5 = 0
X_D4_5 = 0
X_D5_5 = 0

YINIT1 = np.array(
    [
        S_I1,
        S_S1,
        X_I1,
        X_S1,
        X_BH1,
        X_BA1,
        X_P1,
        S_O1,
        S_NO1,
        S_NH1,
        S_ND1,
        X_ND1,
        S_ALK1,
        TSS1,
        Q1,
        T1,
        S_D1_1,
        S_D2_1,
        S_D3_1,
        X_D4_1,
        X_D5_1,
    ]
)
"""Initial concentrations for the AS system in reactor 1.

Other Parameters
----------------
S_I1 : float
    Initial concentration of soluble inert substrate [g(COD) $\cdot$ m^-3^].
S_S1 : float
    Initial concentration of readily biodegradable substrate [g(COD) $\cdot$ m^-3^].
X_I1 : float
    Initial concentration of particulate inert organic matter [g(COD) $\cdot$ m^-3^].
X_S1 : float
    Initial concentration of slowly biodegradable substrate [g(COD) $\cdot$ m^-3^].
X_BH1 : float
    Initial concentration of heterotrophic biomass [g(COD) $\cdot$ m^-3^].
X_BA1 : float
    Initial concentration of active autotrophic biomass [g(COD) $\cdot$ m^-3^].
X_P1 : float
    Initial concentration of particulate products [g(COD) $\cdot$ m^-3^].
S_O1 : float
    Initial concentration of dissolved oxygen [g(O~2~) $\cdot$ m^-3^].
S_NO1 : float
    Initial concentration of nitrate [g(N) $\cdot$ m^-3^].
S_NH1 : float
    Initial concentration of ammonium [g(N) $\cdot$ m^-3^].
S_ND1 : float
    Initial concentration of soluble biodegradable dissolved organic nitrogen [g(N) $\cdot$ m^-3^].
X_ND1 : float
    Initial concentration of particulate biodegradable organic nitrogen [g(N) $\cdot$ m^-3^].
S_ALK1 : float
    Initial concentration of alkalinity [mol $\cdot$ m^-3^].
TSS1 : float
    Initial concentration of total suspended solids [g(TSS) $\cdot$ m^-3^].
Q1 : float
    Initial flow rate [m^3^ $\cdot$ d^-1^].
T1 : float
    Initial temperature [°C].
S_D1_1 : float
    Initial dummy state 1 [-].
S_D2_1 : float
    Initial dummy state 2 [-].
S_D3_1 : float
    Initial dummy state 3 [-].
X_D4_1 : float
    Initial dummy state 4 [-].
X_D5_1 : float
    Initial dummy state 5 [-].
"""

YINIT2 = np.array(
    [
        S_I2,
        S_S2,
        X_I2,
        X_S2,
        X_BH2,
        X_BA2,
        X_P2,
        S_O2,
        S_NO2,
        S_NH2,
        S_ND2,
        X_ND2,
        S_ALK2,
        TSS2,
        Q2,
        T2,
        S_D1_2,
        S_D2_2,
        S_D3_2,
        X_D4_2,
        X_D5_2,
    ]
)
"""Initial concentrations for the AS system in reactor 2."""

YINIT3 = np.array(
    [
        S_I3,
        S_S3,
        X_I3,
        X_S3,
        X_BH3,
        X_BA3,
        X_P3,
        S_O3,
        S_NO3,
        S_NH3,
        S_ND3,
        X_ND3,
        S_ALK3,
        TSS3,
        Q3,
        T3,
        S_D1_3,
        S_D2_3,
        S_D3_3,
        X_D4_3,
        X_D5_3,
    ]
)
"""Initial concentrations for the AS system in reactor 3."""

YINIT4 = np.array(
    [
        S_I4,
        S_S4,
        X_I4,
        X_S4,
        X_BH4,
        X_BA4,
        X_P4,
        S_O4,
        S_NO4,
        S_NH4,
        S_ND4,
        X_ND4,
        S_ALK4,
        TSS4,
        Q4,
        T4,
        S_D1_4,
        S_D2_4,
        S_D3_4,
        X_D4_4,
        X_D5_4,
    ]
)
"""Initial concentrations for the AS system in reactor 4."""

YINIT5 = np.array(
    [
        S_I5,
        S_S5,
        X_I5,
        X_S5,
        X_BH5,
        X_BA5,
        X_P5,
        S_O5,
        S_NO5,
        S_NH5,
        S_ND5,
        X_ND5,
        S_ALK5,
        TSS5,
        Q5,
        T5,
        S_D1_5,
        S_D2_5,
        S_D3_5,
        X_D4_5,
        X_D5_5,
    ]
)
"""Initial concentrations for the AS system in reactor 5."""


# parameters for AS system at 15 degC, based on Alex et al (2018) (BSM1)
MU_H = 4.0
K_S = 10.0
K_OH = 0.2
K_NO = 0.5
B_H = 0.3
MU_A = 0.5
K_NH = 1.0
K_OA = 0.4
B_A = 0.05
NY_G = 0.8
K_A = 0.05
K_H = 3.0
K_X = 0.1
NY_H = 0.8
Y_H = 0.67
Y_A = 0.24
F_P = 0.08
I_XB = 0.08
I_XP = 0.06
X_I2TSS = 0.75
X_S2TSS = 0.75
X_BH2TSS = 0.75
X_BA2TSS = 0.75
X_P2TSS = 0.75

PAR1 = np.array(
    [
        MU_H,
        K_S,
        K_OH,
        K_NO,
        B_H,
        MU_A,
        K_NH,
        K_OA,
        B_A,
        NY_G,
        K_A,
        K_H,
        K_X,
        NY_H,
        Y_H,
        Y_A,
        F_P,
        I_XB,
        I_XP,
        X_I2TSS,
        X_S2TSS,
        X_BH2TSS,
        X_BA2TSS,
        X_P2TSS,
    ]
)
"""Parameters for the AS system at 15 °C, based on Alex et al (2018) (BSM1).

Other Parameters
----------------
MU_H : float
    Maximum specific growth rate of heterotrophic biomass [d^-1^].
K_S : float
    Half-saturation constant for substrate [g(COD) $\cdot$ m^-3^].
K_OH : float
    Oxygen half-saturation coefficient for heterotrophic growth [g(O~2~) $\cdot$ m^-3^].
K_NO : float
    Half-saturation constant for nitrate [g(N) $\cdot$ m^-3^].
B_H : float
    Decay coefficient for heterotrophic biomass [d^-1^].
MU_A : float
    Maximum specific growth rate of autotrophic biomass [d^-1^].
K_NH : float
    Half-saturation constant for ammonium [g(N) $\cdot$ m^-3^].
K_OA : float
    Oxygen half-saturation coefficient for autotrophic growth [g(O~2~) $\cdot$ m^-3^].
B_A : float
    Decay coefficient for autotrophic biomass [d^-1^].
NY_G : float
    Anoxic growth rate correction factor [-].
K_A : float
    Ammonification rate [m^3^ $\cdot$ (g(COD) $\cdot$ d)^-1^].
K_H : float
    Hydrolysis rate [g(COD) $\cdot$ (g(COD) $\cdot$ d)^-1^].
K_X : float
    Particulate half-saturation constant for hydrolysis [g(COD) $\cdot$ g(COD)^-1^].
NY_H : float
    Anoxic hydrolysis rate correction factor [-].
Y_H : float
    Yield coefficient for heterotrophic biomass [g(COD) $\cdot$ g(COD)^-1^].
Y_A : float
    Yield coefficient for autotrophic biomass [g(COD) $\cdot$ g(N)^-1^].
F_P : float
    Fraction of particulate inert products of biomass [-].
I_XB : float
    Fraction of nitrogen in biomass [g(N) $\cdot$ g(COD)^-1^].
I_XP : float
    Fraction of nitrogen in organic particulate inerts [g(N) $\cdot$ g(COD)^-1^].
X_I2TSS : float
    Conversion factor from inert organic matter to TSS [-].
X_S2TSS : float
    Conversion factor from readily biodegradable substrate to TSS [-].
X_BH2TSS : float
    Conversion factor from heterotrophic biomass to TSS [-].
X_BA2TSS : float
    Conversion factor from autotrophic biomass to TSS [-].
X_P2TSS : float
    Conversion factor from particulate products to TSS [-].
"""

PAR2 = PAR1
"""Parameters for the AS system at 15 °C, based on Alex et al (2018) (BSM1)."""
PAR3 = PAR1
"""Parameters for the AS system at 15 °C, based on Alex et al (2018) (BSM1)."""
PAR4 = PAR1
"""Parameters for the AS system at 15 °C, based on Alex et al (2018) (BSM1)."""
PAR5 = PAR1
"""Parameters for the AS system at 15 °C, based on Alex et al (2018) (BSM1)."""

# reactor volumes:
VOL1 = 1500
"""Volume of reactor 1 [m^3^]."""
VOL2 = VOL1
"""Volume of reactor 2 [m^3^]."""
VOL3 = 3000
"""Volume of reactor 3 [m^3^]."""
VOL4 = VOL3
"""Volume of reactor 4 [m^3^]."""
VOL5 = VOL3
"""Volume of reactor 5 [m^3^]."""

# oxygen saturation concentration at 15 degC, based on BSM1
SOSAT1 = 8
"""Oxygen saturation concentration at 15 °C in reactor 1 [%]."""
SOSAT2 = SOSAT1
"""Oxygen saturation concentration at 15 °C in reactor 2 [%]."""
SOSAT3 = SOSAT1
"""Oxygen saturation concentration at 15 °C in reactor 3 [%]."""
SOSAT4 = SOSAT1
"""Oxygen saturation concentration at 15 °C in reactor 4 [%]."""
SOSAT5 = SOSAT1
"""Oxygen saturation concentration at 15 °C in reactor 5 [%]."""
