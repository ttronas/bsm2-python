"""Initialization file for all states and parameters related to the dewatering.

All parameters and specifications are based on BSM2 model.
This file will be executed when running `bsm2_cl.py`, `bsm2_ol.py` or `bsm2_olem.py`.
"""

import numpy as np

dewater_perc = 28  # %TSS in dewatered sludge
"""Percentage of TSS in dewatered sludge [%]."""
TSS_removal_perc = 98  # %TSS removed from the dewatering overflow (reject water)
"""Percentage of TSS removed from the influent sludge [%]."""
X_I2TSS = 0.75
"""Conversion factor of inert particulate organic matter X_I to TSS [g(SS) ⋅ g(COD)⁻¹]."""
X_S2TSS = 0.75
"""Conversion factor of slowly biodegradable substrat X_S to TSS [g(SS) ⋅ g(COD)⁻¹]."""
X_BH2TSS = 0.75
"""Conversion factor of heterotrophic biomass X_B,H to TSS [g(SS) ⋅ g(COD)⁻¹]."""
X_BA2TSS = 0.75
"""Conversion factor of autotrophic biomass X_B,A to TSS [g(SS) ⋅ g(COD)⁻¹]."""
X_P2TSS = 0.75
"""Conversion factor of particulate products from biomass decay X_P to TSS [g(SS) ⋅ g(COD)⁻¹]."""

DEWATERINGPAR = np.array([dewater_perc, TSS_removal_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS])
"""Dewatering parameters."""
