"""
This file initiates parameter values and sets initial conditions for the model implementation of boiler.py.
"""

import numpy as np

INDICES_PRODUCTS = np.arange(1)
HEAT = INDICES_PRODUCTS[0]

INDICES_BIOGAS = np.arange(1)
BIOGAS = INDICES_BIOGAS[0]


MAX_POWER_1 = 720  # kW of gas uptake

EFFICIENCY_RULES_1 = np.array(
    [
        # gas load, eta_th
        [0, 0],
        [0.3, 0.9],
        [1, 0.9],
    ]
)

MINIMUM_LOAD_1 = 0.3

# can run at any load between minimum_load and 1
STEPLESS_INTERVALS_1 = True

# time after changing the load until a new change can be made [hours]
# if set too high can lead to violation of lower heat net threshold
LOAD_CHANGE_TIME_1 = 1

CAPEX_SP_1 = 68  # €/kW

CAPEX_1 = CAPEX_SP_1 * MAX_POWER_1  # €
