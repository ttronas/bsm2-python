"""Initialisation file for all states and parameters related to the dewatering.

All parameters and specifications are based on BSM2 model.
This file will be executed when running `bsm2_cl.py`, `bsm2_ol.py` or `bsm2_olem.py`.
"""

import numpy as np

dewater_perc = 28  # %TSS in dewatered sludge
"""Percentage of TSS in dewatered sludge [%]."""
TSS_removal_perc = 98  # %TSS removed from the dewatering overflow (reject water)
"""Percentage of TSS removed from the dewatering overflow (reject water) [%]."""
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

DEWATERINGPAR = np.array([dewater_perc, TSS_removal_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS])
"""Dewatering parameters."""
