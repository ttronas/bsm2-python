"""Initialization file for all states and parameters related to the thickener.

All parameters and specifications are based on BSM2 model.
This file will be executed when running `bsm2_cl.py`, `bsm2_ol.py` or `bsm2_olem.py`.
"""

import numpy as np

thickener_perc = 7  # %TSS in thickener underflow
"""TSS in thickener underflow [%]."""
TSS_removal_perc = 98  # %TSS removed from the thickener overflow
"""TSS removed from the thickener overflow [%]."""
X_I2TSS = 0.75
"""Conversion factor for particulate inert organic matter to TSS [-]."""
X_S2TSS = 0.75
"""Conversion factor for slowly biodegradable substrate to TSS [-]."""
X_BH2TSS = 0.75
"""Conversion factor for heterotrophic biomass to TSS [-]."""
X_BA2TSS = 0.75
"""Conversion factor for autotrophic biomass to TSS [-]."""
X_P2TSS = 0.75
"""Conversion factor for particulate products to TSS [-]."""

THICKENERPAR = np.array([thickener_perc, TSS_removal_perc, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS])
"""Thickener parameters."""
