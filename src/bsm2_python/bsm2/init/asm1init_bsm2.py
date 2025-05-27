"""Initialization file for all states and parameters related to the AS systems (reactors 1-5).

All parameters and specifications are based on BSM1 model.
This file will be executed when running `bsm2_cl.py`, `bsm2_ol.py` or `bsm2_olem.py`.
"""

import numpy as np

# flows:
QIN0 = 20648
"""Flow rate of influent [m³ ⋅ d⁻¹]."""

QIN = QIN0
"""Flow rate of influent [m³ ⋅ d⁻¹]."""
QINTR = 3 * QIN0
"""Flow rate of internal recirculation [m³ ⋅ d⁻¹]."""
QR = QIN0
"""Flow rate of sludge return [m³ ⋅ d⁻¹]."""
QW = 300
"""Flow rate of waste sludge [m³ ⋅ d⁻¹]."""

# The following states represent concentrations in different AS reactors (1 to 5)

S_I1 = 28.0643
"""Soluble inert organic matter (reactor 1) [g(COD) ⋅ m⁻³]."""
S_S1 = 3.0503
"""Readily biodegradable substrate (reactor 1) [g(COD) ⋅ m⁻³]."""
X_I1 = 1532.3
"""Particulate inert organic matter (reactor 1) [g(COD) ⋅ m⁻³]."""
X_S1 = 63.0433
"""Slowly biodegradable substrate (reactor 1) [g(COD) ⋅ m⁻³]."""
X_BH1 = 2245.1
"""Active heterotrophic biomass (reactor 1) [g(COD) ⋅ m⁻³]."""
X_BA1 = 166.6699
"""Active autotrophic biomass (reactor 1) [g(COD) ⋅ m⁻³]."""
X_P1 = 964.8992
"""Particulate products arising from biomass decay (reactor 1) [g(COD) ⋅ m⁻³]."""
S_O1 = 0.0093
"""Dissolved oxygen (reactor 1) [g(O₂) ⋅ m⁻³]."""
S_NO1 = 3.9350
"""Nitrate and nitrite (reactor 1) [g(N) ⋅ m⁻³]."""
S_NH1 = 6.8924
"""Ammonium plus ammonia nitrogen (reactor 1) [g(N) ⋅ m⁻³]."""
S_ND1 = 0.9580
"""Soluble biodegradable organic nitrogen (reactor 1) [g(N) ⋅ m⁻³]."""
X_ND1 = 3.8453
"""Particulate biodegradable organic nitrogen (reactor 1) [g(N) ⋅ m⁻³]."""
S_ALK1 = 5.4213
"""Alkalinity (reactor 1) [mol(HCO₃⁻) ⋅ m⁻³]."""
TSS1 = 3729.0
"""Total suspended solids (reactor 1) [g(TSS) ⋅ m⁻³]."""
Q1 = 103533
"""Flow rate (reactor 1) [m³ ⋅ d⁻¹]."""
T1 = 14.8581
"""Temperature (reactor 1) [°C]."""
S_D1_1 = 0
"""Dummy state 1 (reactor 1) [-]."""
S_D2_1 = 0
"""Dummy state 2 (reactor 1) [-]."""
S_D3_1 = 0
"""Dummy state 3 (reactor 1) [-]."""
X_D4_1 = 0
"""Dummy state 4 (reactor 1) [-]."""
X_D5_1 = 0
"""Dummy state 5 (reactor 1) [-]."""

S_I2 = 28.0643
"""Soluble inert organic matter (reactor 2) [g(COD) ⋅ m⁻³]."""
S_S2 = 1.3412
"""Readily biodegradable substrate (reactor 2) [g(COD) ⋅ m⁻³]."""
X_I2 = 1532.3
"""Particulate inert organic matter (reactor 2) [g(COD) ⋅ m⁻³]."""
X_S2 = 58.8579
"""Slowly biodegradable substrate (reactor 2) [g(COD) ⋅ m⁻³]."""
X_BH2 = 2245.4
"""Active heterotrophic biomass (reactor 2) [g(COD) ⋅ m⁻³]."""
X_BA2 = 166.5512
"""Active autotrophic biomass (reactor 2) [g(COD) ⋅ m⁻³]."""
X_P2 = 965.6805
"""Particulate products arising from biomass decay (reactor 2) [g(COD) ⋅ m⁻³]."""
S_O2 = 1.0907e-4
"""Dissolved oxygen (reactor 2) [g(O₂) ⋅ m⁻³]."""
S_NO2 = 2.2207
"""Nitrate and nitrite (reactor 2) [g(N) ⋅ m⁻³]."""
S_NH2 = 7.2028
"""Ammonium plus ammonia nitrogen (reactor 2) [g(N) ⋅ m⁻³]."""
S_ND2 = 0.6862
"""Soluble biodegradable organic nitrogen (reactor 2) [g(N) ⋅ m⁻³]."""
X_ND2 = 3.7424
"""Particulate biodegradable organic nitrogen (reactor 2) [g(N) ⋅ m⁻³]."""
S_ALK2 = 5.5659
"""Alkalinity (reactor 2) [mol(HCO₃⁻) ⋅ m⁻³]."""
TSS2 = 3726.6
"""Total suspended solids (reactor 2) [g(TSS) ⋅ m⁻³]."""
Q2 = 103533
"""Flow rate (reactor 2) [m³ ⋅ d⁻¹]."""
T2 = 14.8581
"""Temperature (reactor 2) [°C]."""
S_D1_2 = 0
"""Dummy state 1 (reactor 2) [-]."""
S_D2_2 = 0
"""Dummy state 2 (reactor 2) [-]."""
S_D3_2 = 0
"""Dummy state 3 (reactor 2) [-]."""
X_D4_2 = 0
"""Dummy state 4 (reactor 2) [-]."""
X_D5_2 = 0
"""Dummy state 5 (reactor 2) [-]."""

S_I3 = 28.0643
"""Soluble inert organic matter (reactor 3) [g(COD) ⋅ m⁻³]."""
S_S3 = 0.9553
"""Readily biodegradable substrate (reactor 3) [g(COD) ⋅ m⁻³]."""
X_I3 = 1532.3
"""Particulate inert organic matter (reactor 3) [g(COD) ⋅ m⁻³]."""
X_S3 = 46.2983
"""Slowly biodegradable substrate (reactor 3) [g(COD) ⋅ m⁻³]."""
X_BH3 = 2246.8
"""Active heterotrophic biomass (reactor 3) [g(COD) ⋅ m⁻³]."""
X_BA3 = 167.3077
"""Active autotrophic biomass (reactor 3) [g(COD) ⋅ m⁻³]."""
X_P3 = 967.2442
"""Particulate products arising from biomass decay (reactor 3) [g(COD) ⋅ m⁻³]."""
S_O3 = 0.4663
"""Dissolved oxygen (reactor 3) [g(O₂) ⋅ m⁻³]."""
S_NO3 = 5.5141
"""Nitrate and nitrite (reactor 3) [g(N) ⋅ m⁻³]."""
S_NH3 = 3.4247
"""Ammonium plus ammonia nitrogen (reactor 3) [g(N) ⋅ m⁻³]."""
S_ND3 = 0.6513
"""Soluble biodegradable organic nitrogen (reactor 3) [g(N) ⋅ m⁻³]."""
X_ND3 = 3.1405
"""Particulate biodegradable organic nitrogen (reactor 3) [g(N) ⋅ m⁻³]."""
S_ALK3 = 5.0608
"""Alkalinity (reactor 3) [mol(HCO₃⁻) ⋅ m⁻³]."""
TSS3 = 3719.9
"""Total suspended solids (reactor 3) [g(TSS) ⋅ m⁻³]."""
Q3 = 103533
"""Flow rate (reactor 3) [m³ ⋅ d⁻¹]."""
T3 = 14.8581
"""Temperature (reactor 3) [°C]."""
S_D1_3 = 0
"""Dummy state 1 (reactor 3) [-]."""
S_D2_3 = 0
"""Dummy state 2 (reactor 3) [-]."""
S_D3_3 = 0
"""Dummy state 3 (reactor 3) [-]."""
X_D4_3 = 0
"""Dummy state 4 (reactor 3) [-]."""
X_D5_3 = 0
"""Dummy state 5 (reactor 3) [-]."""

S_I4 = 28.0643
"""Soluble inert organic matter (reactor 4) [g(COD) ⋅ m⁻³]."""
S_S4 = 0.7806
"""Readily biodegradable substrate (reactor 4) [g(COD) ⋅ m⁻³]."""
X_I4 = 1532.3
"""Particulate inert organic matter (reactor 4) [g(COD) ⋅ m⁻³]."""
X_S4 = 37.3881
"""Slowly biodegradable substrate (reactor 4) [g(COD) ⋅ m⁻³]."""
X_BH4 = 2245.6
"""Active heterotrophic biomass (reactor 4) [g(COD) ⋅ m⁻³]."""
X_BA4 = 167.8339
"""Active autotrophic biomass (reactor 4) [g(COD) ⋅ m⁻³]."""
X_P4 = 968.8072
"""Particulate products arising from biomass decay (reactor 4) [g(COD) ⋅ m⁻³]."""
S_O4 = 1.4284
"""Dissolved oxygen (reactor 4) [g(O₂) ⋅ m⁻³]."""
S_NO4 = 8.4066
"""Nitrate and nitrite (reactor 4) [g(N) ⋅ m⁻³]."""
S_NH4 = 0.6922
"""Ammonium plus ammonia nitrogen (reactor 4) [g(N) ⋅ m⁻³]."""
S_ND4 = 0.6094
"""Soluble biodegradable organic nitrogen (reactor 4) [g(N) ⋅ m⁻³]."""
X_ND4 = 2.6815
"""Particulate biodegradable organic nitrogen (reactor 4) [g(N) ⋅ m⁻³]."""
S_ALK4 = 4.6590
"""Alkalinity (reactor 4) [mol(HCO₃⁻) ⋅ m⁻³]."""
TSS4 = 3713.9
"""Total suspended solids (reactor 4) [g(TSS) ⋅ m⁻³]."""
Q4 = 103533
"""Flow rate (reactor 4) [m³ ⋅ d⁻¹]."""
T4 = 14.8581
"""Temperature (reactor 4) [°C]."""
S_D1_4 = 0
"""Dummy state 1 (reactor 4) [-]."""
S_D2_4 = 0
"""Dummy state 2 (reactor 4) [-]."""
S_D3_4 = 0
"""Dummy state 3 (reactor 4) [-]."""
X_D4_4 = 0
"""Dummy state 4 (reactor 4) [-]."""
X_D5_4 = 0
"""Dummy state 5 (reactor 4) [-]."""

S_I5 = 28.0643
"""Soluble inert organic matter (reactor 5) [g(COD) ⋅ m⁻³]."""
S_S5 = 0.6734
"""Readily biodegradable substrate (reactor 5) [g(COD) ⋅ m⁻³]."""
X_I5 = 1532.3
"""Particulate inert organic matter (reactor 5) [g(COD) ⋅ m⁻³]."""
X_S5 = 31.9144
"""Slowly biodegradable substrate (reactor 5) [g(COD) ⋅ m⁻³]."""
X_BH5 = 2242.1
"""Active heterotrophic biomass (reactor 5) [g(COD) ⋅ m⁻³]."""
X_BA5 = 167.8482
"""Active autotrophic biomass (reactor 5) [g(COD) ⋅ m⁻³]."""
X_P5 = 970.3678
"""Particulate products arising from biomass decay (reactor 5) [g(COD) ⋅ m⁻³]."""
S_O5 = 1.3748
"""Dissolved oxygen (reactor 5) [g(O₂) ⋅ m⁻³]."""
S_NO5 = 9.1948
"""Nitrate and nitrite (reactor 5) [g(N) ⋅ m⁻³]."""
S_NH5 = 0.1585
"""Ammonium plus ammonia nitrogen (reactor 5) [g(N) ⋅ m⁻³]."""
S_ND5 = 0.5594
"""Soluble biodegradable organic nitrogen (reactor 5) [g(N) ⋅ m⁻³]."""
X_ND5 = 2.3926
"""Particulate biodegradable organic nitrogen (reactor 5) [g(N) ⋅ m⁻³]."""
S_ALK5 = 4.5646
"""Alkalinity (reactor 5) [mol(HCO₃⁻) ⋅ m⁻³]."""
TSS5 = 3708.4
"""Total suspended solids (reactor 5) [g(TSS) ⋅ m⁻³]."""
Q5 = 103533
"""Flow rate (reactor 5) [m³ ⋅ d⁻¹]."""
T5 = 14.8581
"""Temperature (reactor 5) [°C]."""
S_D1_5 = 0
"""Dummy state 1 (reactor 5) [-]."""
S_D2_5 = 0
"""Dummy state 2 (reactor 5) [-]."""
S_D3_5 = 0
"""Dummy state 3 (reactor 5) [-]."""
X_D4_5 = 0
"""Dummy state 4 (reactor 5) [-]."""
X_D5_5 = 0
"""Dummy state 5 (reactor 5) [-]."""

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
"""Initial concentrations for the activated sludge reactor 1."""

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
"""Initial concentrations for the activated sludge reactor 2."""

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
"""Initial concentrations for the activated sludge reactor 3."""

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
"""Initial concentrations for the activated sludge reactor 4."""

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
"""Initial concentrations for the activated sludge reactor 5."""


# parameters for AS system at 15 degC, based on Alex et al (2018) (BSM1)
MU_H = 4.0
"""Maximum heterotrophic growth rate [d⁻¹]."""
K_S = 10.0
"""Substrate half-saturation coefficient for heterotrophic growth [g(COD) ⋅ m⁻³]."""
K_OH = 0.2
"""Oxygen half-saturation coefficient for heterotrophic growth [g(O₂) ⋅ m⁻³]."""
K_NO = 0.5
"""Nitrate half-saturation coefficient for anoxic heterotrophic growth [g(N) ⋅ m⁻³]."""
B_H = 0.3
"""Heterotrophic decay rate [d⁻¹]."""
MU_A = 0.5
"""Maximum autotrophic growth rate [d⁻¹]."""
K_NH = 1.0
"""Ammonia half-saturation coefficient for autotrophic growth [g(N) ⋅ m⁻³]."""
K_OA = 0.4
"""Oxygen half-saturation coefficient for autotrophic growth [g(O₂) ⋅ m⁻³]."""
B_A = 0.05
"""Autotrophic decay rate [d⁻¹]."""
NY_G = 0.8
"""Anoxic growth rate correction factor [-]."""
K_A = 0.05
"""Ammonification rate [m³ ⋅ (g(COD) ⋅ d)⁻¹]."""
K_H = 3.0
"""Maximum specific hydrolysis rate [g(COD) ⋅ (g(COD) ⋅ d)⁻¹]."""
K_X = 0.1
"""Particulate substrate half-saturation coefficient for hydrolysis [g(COD) ⋅ g(COD)⁻¹]."""
NY_H = 0.8
"""Anoxic hydrolysis rate correction factor [-]."""
Y_H = 0.67
"""Heterotrophic yield [g(COD) ⋅ g(COD)⁻¹]."""
Y_A = 0.24
"""Autotrophic yield [g(COD) ⋅ g(N)⁻¹]."""
F_P = 0.08
"""Fraction of biomass leading to particulate inert products [-]."""
I_XB = 0.08
"""Fraction of nitrogen in biomass [g(N) ⋅ g(COD)⁻¹]."""
I_XP = 0.06
"""Fraction of nitrogen in organic particulate inerts [g(N) ⋅ g(COD)⁻¹]."""
X_I2TSS = 0.75
"""Conversion factor for particulate inert organic matter to TSS [-]."""
X_S2TSS = 0.75
"""Conversion factor for readily biodegradable substrate to TSS [-]."""
X_BH2TSS = 0.75
"""Conversion factor for heterotrophic biomass to TSS [-]."""
X_BA2TSS = 0.75
"""Conversion factor for autotrophic biomass to TSS [-]."""
X_P2TSS = 0.75
"""Conversion factor for particulate products to TSS [-]."""

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
"""Parameters for the activated sludge reactor 1 at 15 °C, based on Alex et al (2018) (BSM1)."""

PAR2 = PAR1
"""Parameters for the activated sludge reactor 2 at 15 °C, based on Alex et al (2018) (BSM1)."""
PAR3 = PAR1
"""Parameters for the activated sludge reactor 3 at 15 °C, based on Alex et al (2018) (BSM1)."""
PAR4 = PAR1
"""Parameters for the activated sludge reactor 4 at 15 °C, based on Alex et al (2018) (BSM1)."""
PAR5 = PAR1
"""Parameters for the activated sludge reactor 5 at 15 °C, based on Alex et al (2018) (BSM1)."""

# reactor volumes:
VOL1 = 1500
"""Volume of reactor 1 [m³]."""
VOL2 = VOL1
"""Volume of reactor 2 [m³]."""
VOL3 = 3000
"""Volume of reactor 3 [m³]."""
VOL4 = VOL3
"""Volume of reactor 4 [m³]."""
VOL5 = VOL3
"""Volume of reactor 5 [m³]."""

# oxygen saturation concentration at 15 degC, based on BSM1
SOSAT1 = 8
"""Oxygen saturation concentration at 15 °C in reactor 1 [g(O₂) ⋅ m⁻³]."""
SOSAT2 = SOSAT1
"""Oxygen saturation concentration at 15 °C in reactor 2 [g(O₂) ⋅ m⁻³]."""
SOSAT3 = SOSAT1
"""Oxygen saturation concentration at 15 °C in reactor 3 [g(O₂) ⋅ m⁻³]."""
SOSAT4 = SOSAT1
"""Oxygen saturation concentration at 15 °C in reactor 4 [g(O₂) ⋅ m⁻³]."""
SOSAT5 = SOSAT1
"""Oxygen saturation concentration at 15 °C in reactor 5 [g(O₂) ⋅ m⁻³]."""
