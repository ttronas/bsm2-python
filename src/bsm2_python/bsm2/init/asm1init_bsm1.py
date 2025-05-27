"""Initialization file for all states and parameters related to the AS systems (reactors 1-5).

All parameters and specifications are based on BSM1 model.
"""

import numpy as np

# flows:
QIN0 = 18446
"""Flow rate of influent [m³ ⋅ d⁻¹]."""

QIN = QIN0
"""Flow rate of influent [m³ ⋅ d⁻¹]."""
QINTR = 3 * QIN0
"""Flow rate of internal recirculation [m³ ⋅ d⁻¹]."""
QR = QIN0
"""Flow rate of sludge return. [m³ ⋅ d⁻¹]."""
QW = 385
"""Flow rate of waste sludge [m³ ⋅ d⁻¹]."""


YINIT1 = np.concatenate((np.ones(16), np.zeros(5)))
"""Initial concentrations for the AS system in reactor 2 (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
[S_I2, S_S2, X_I2, X_S2, X_BH2, X_BA2, X_P2, S_O2, S_NO2, S_NH2, S_ND2, X_ND2, S_ALK2, TSS2, Q2, T2, S_D1_2,
S_D2_2, S_D3_2, X_D4_2, X_D5_2]
"""

YINIT2 = YINIT1
"""Initial concentrations for the AS system in reactor 2 (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
[S_I2, S_S2, X_I2, X_S2, X_BH2, X_BA2, X_P2, S_O2, S_NO2, S_NH2, S_ND2, X_ND2, S_ALK2, TSS2, Q2, T2, S_D1_2,
S_D2_2, S_D3_2, X_D4_2, X_D5_2]
"""
YINIT3 = YINIT1
"""Initial concentrations for the AS system in reactor 3 (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
[S_I3, S_S3, X_I3, X_S3, X_BH3, X_BA3, X_P3, S_O3, S_NO3, S_NH3, S_ND3, X_ND3, S_ALK3, TSS3, Q3, T3, S_D1_3,
S_D2_3, S_D3_3, X_D4_3, X_D5_3]"""
YINIT4 = YINIT1
"""Initial concentrations for the AS system in reactor 4 (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
[S_I4, S_S4, X_I4, X_S4, X_BH4, X_BA4, X_P4, S_O4, S_NO4, S_NH4, S_ND4, X_ND4, S_ALK4, TSS4, Q4, T4, S_D1_4,
S_D2_4, S_D3_4, X_D4_4, X_D5_4]"""
YINIT5 = YINIT1
"""Initial concentrations for the AS system in reactor 5 (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
[S_I5, S_S5, X_I5, X_S5, X_BH5, X_BA5, X_P5, S_O5, S_NO5, S_NH5, S_ND5, X_ND5, S_ALK5, TSS5, Q5, T5, S_D1_5,
S_D2_5, S_D3_5, X_D4_5, X_D5_5]"""

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
VOL1 = 1000
"""Volume of reactor 1 [m³]."""
VOL2 = VOL1
"""Volume of reactor 2 [m³]."""
VOL3 = 1333
"""Volume of reactor 3 [m³]."""
VOL4 = VOL3
"""Volume of reactor 4 [m³]."""
VOL5 = VOL3
"""Volume of reactor 5 [m³]."""

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

# Default KLa (oxygen transfer coefficient) values for AS reactors:
KLA1 = 0
"""Default KLa (oxygen transfer coefficient) value for reactor 1 [d⁻¹]."""
KLA2 = 0
"""Default KLa (oxygen transfer coefficient) value for reactor 2 [d⁻¹]."""
KLA3 = 240
"""Default KLa (oxygen transfer coefficient) value for reactor 3 [d⁻¹]."""
KLA4 = 240
"""Default KLa (oxygen transfer coefficient) value for reactor 4 [d⁻¹]."""
KLA5 = 84
"""Default KLa (oxygen transfer coefficient) value for reactor 5 [d⁻¹]."""

# external carbon flow rates for reactor 1 to 5:
CARB1 = 0
"""External carbon flow rate to reactor 1 [kg(COD) ⋅ d⁻¹]."""
CARB2 = 0
"""External carbon flow rate to reactor 2 [kg(COD) ⋅ d⁻¹]."""
CARB3 = 0
"""External carbon flow rate to reactor 3 [kg(COD) ⋅ d⁻¹]."""
CARB4 = 0
"""External carbon flow rate to reactor 4 [kg(COD) ⋅ d⁻¹]."""
CARB5 = 0
"""External carbon flow rate to reactor 5 [kg(COD) ⋅ d⁻¹]."""
# external carbon source concentration = 400000 mg COD / L from BSM1
CARBONSOURCECONC = 400000
"""External carbon source concentration [g(COD) ⋅ m⁻³]."""
