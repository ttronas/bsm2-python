"""Initialization file for all states and parameters related to the wastewater storage.

All parameters and specifications are based on BSM2 model.
This file will be executed when running `bsm2_cl.py`, `bsm2_ol.py` or `bsm2_olem.py`.
"""

import numpy as np

VOL_S = 160  # Maximum volume of the sludge storage tank (m3)
"""Maximum volume of the sludge storage tank [m³]."""

# Initial values for the sludge storage
S_I_S = 140.1528
"""Soluble inert organic matter [g(COD) ⋅ m⁻³]."""
S_S_S = 260.0720
"""Readily biodegradable substrate [g(COD) ⋅ m⁻³]."""
X_I_S = 363.7842
"""Particulate inert organic matter [g(COD) ⋅ m⁻³]."""
X_S_S = 57.1637
"""Slowly biodegradable substrate [g(COD) ⋅ m⁻³]."""
X_BH_S = 0
"""Active heterotrophic biomass [g(COD) ⋅ m⁻³]."""
X_BA_S = 0
"""Active autotrophic biomass [g(COD) ⋅ m⁻³]."""
X_P_S = 13.7743
"""Particulate products arising from biomass decay [g(COD) ⋅ m⁻³]."""
S_O_S = 0
"""Dissolved oxygen [g(O₂) ⋅ m⁻³]."""
S_NO_S = 0
"""Nitrate and nitrite [g(N) ⋅ m⁻³]."""
S_NH_S = 1.5685e03
"""Ammonium plus ammonia nitrogen [g(N) ⋅ m⁻³]."""
S_ND_S = 0.4786
"""Soluble biodegradable organic nitrogen [g(N) ⋅ m⁻³]."""
X_ND_S = 2.2039
"""Particulate biodegradable organic nitrogen [g(N) ⋅ m⁻³]."""
S_ALK_S = 106.8816
"""Alkalinity [mol(HCO₃⁻) ⋅ m⁻³]."""
TSS_S = 326.0416
"""Total suspended solids [g(TSS) ⋅ m⁻³]."""
Q_S = 0
"""Flow rate [m³ ⋅ d⁻¹]."""
T_S = 14.8581
"""Temperature [°C]."""
S_D1_S = 0
"""Dummy state 1 [-]."""
S_D2_S = 0
"""Dummy state 2 [-]."""
S_D3_S = 0
"""Dummy state 3 [-]."""
X_D4_S = 0
"""Dummy state 4 [-]."""
X_D5_S = 0
"""Dummy state 5 [-]."""
VOL_INIT_S = VOL_S * 0.5  # Initial liquid volume in storage tank
"""Initial liquid volume in storage tank [m³]."""

ystinit = np.array(
    [
        S_I_S,
        S_S_S,
        X_I_S,
        X_S_S,
        X_BH_S,
        X_BA_S,
        X_P_S,
        S_O_S,
        S_NO_S,
        S_NH_S,
        S_ND_S,
        X_ND_S,
        S_ALK_S,
        TSS_S,
        Q_S,
        T_S,
        S_D1_S,
        S_D2_S,
        S_D3_S,
        X_D4_S,
        X_D5_S,
        VOL_INIT_S,
    ]
)
"""Initial concentrations for the sludge storage."""
