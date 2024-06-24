"""
This file initiates parameter values and sets initial conditions for the model implementation of chp.py.
"""

import numpy as np

INDICES_CONSUMABLES = np.arange(1)
BIOGAS = INDICES_CONSUMABLES[0]

MAX_GAS_UPTAKE = 1000  # Nm^3/h

FLARE_THRESHOLD = 0.9  # % of biogas storage fill level

CAPEX = 0  # €
