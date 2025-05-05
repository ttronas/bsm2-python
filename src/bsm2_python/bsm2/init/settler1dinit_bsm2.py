"""Initialization file for all states and parameters related to the secondary clarifier (settler).

All parameters and specifications are based on BSM1 model.
This file will be executed when running `bsm2_cl.py`, `bsm2_ol.py` or `bsm2_olem.py`.
"""

import numpy as np

# parameters for Takács settler model, based on Alex et al (2018) (BSM1)
v0_max = 250
"""Maximum settling velocity [m ⋅ d⁻¹]."""
v0 = 474
"""Maximum theoretical (Vesilind) settling velocity [m ⋅ d⁻¹]."""
r_h = 0.000576
"""Settling parameter related to the hindered zone [m³ ⋅ g⁻¹]."""
r_p = 0.00286
"""Settling parameter related to the flocculant zone [m³ ⋅ g⁻¹]."""
f_ns = 0.00228
"""Non-settleable fraction [-]."""
X_t = 3000
"""Threshold concentration for the non-settleable fraction [g ⋅ m⁻³]."""
sb_limit = 3000
"""Limit for the sludge blanket [g ⋅ m⁻³]."""

SETTLERPAR = np.array([v0_max, v0, r_h, r_p, f_ns, X_t, sb_limit])
"""Settler parameters."""

area = 1500
"""Area of the settler [m²]."""
height = 4
"""Height of the settler [m]."""

DIM = np.array([area, height])
"""Settler dimensions."""

# number of layers is flexible, default model is a 10 layer sedimentation tank
feedlayer = 5
"""Layer where the feed enters the settler."""
nooflayers = 10
"""Number of layers in the settler."""

settlerinit = np.zeros(12 * nooflayers)
settlerinit[0 * nooflayers : 1 * nooflayers] = 28.0643  # SI
"""Initial value for soluble inert organic matter [g(COD) ⋅ m⁻³]."""
settlerinit[1 * nooflayers : 2 * nooflayers] = 0.6734  # S_S
"""Initial value for readily biodegradable substrate [g(COD) ⋅ m⁻³]."""
settlerinit[2 * nooflayers : 3 * nooflayers] = 1.3748  # S_O
"""Initial value for dissolved oxygen [g(O₂) ⋅ m⁻³]."""
settlerinit[3 * nooflayers : 4 * nooflayers] = 9.1948  # S_NO
"""Initial value for nitrate and nitrite [g(N) ⋅ m⁻³]."""
settlerinit[4 * nooflayers : 5 * nooflayers] = 0.1585  # S_NH
"""Initial value for ammonium plus ammonia nitrogen [g(N) ⋅ m⁻³]."""
settlerinit[5 * nooflayers : 6 * nooflayers] = 0.5594  # S_ND
"""Initial value for soluble biodegradable organic nitrogen [g(N) ⋅ m⁻³]."""
settlerinit[6 * nooflayers : 7 * nooflayers] = 4.5646  # S_ALK
"""Initial value for alkalinity [mol ⋅ m⁻³]."""
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
"""Initial value for total suspended solids [g(TSS) ⋅ m⁻³]."""
settlerinit[8 * nooflayers : 9 * nooflayers] = 14.8581  # T
"""Initial value for temperature [°C]."""
settlerinit[9 * nooflayers : 12 * nooflayers] = 0  # soluble dummy states
"""Initial value for soluble dummy states [-]."""

LAYER = np.array((feedlayer, nooflayers))
"""Parameters for the settler layers."""


# to use model with nooflayers for solubles use MODELTYPE 0 (IWA/COST Benchmark)
# to use model with 1 layer for solubles use MODELTYPE 1 (GSP-X implementation) (not implemented yet)
# to use model with 0 layers for solubles use MODELTYPE 2 (old WEST implementation) (not implemented yet)
MODELTYPE = 0
"""Model type for the settler.

- 0: Model with nooflayers for solubles (IWA/COST Benchmark).
- 1: Model with 1 layer for solubles (GSP-X implementation) (not implemented yet).
- 2: Model with 0 layers for solubles (old WEST implementation) (not implemented yet).
"""
