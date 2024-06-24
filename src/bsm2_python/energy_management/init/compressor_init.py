"""
This file initiates parameter values and sets initial conditions for the model implementation of compressor.py.
"""

import numpy as np

INDICES_CONSUMABLES = np.arange(1)
ELECTRICITY = INDICES_CONSUMABLES[0]


EFFICIENCY = 0.87  # efficiency %

OPEX_FACTOR = 0.05  # [€/h]
