"""
This file initiates parameter values and sets initial conditions for the model implementation of chp.py.
"""

import numpy as np

INDICES_PRODUCTS = np.arange(2)
ELECTRICITY, HEAT = INDICES_PRODUCTS

INDICES_CONSUMABLES = np.arange(1)
BIOGAS = INDICES_CONSUMABLES[0]


STORAGE_RULES_1 = np.array(
    [
        # threshold, tendency, gas load
        # above 50% biogas storage fill level, tendency doesn't matter, full load
        [0.50, 0, 1],
        # above 35% biogas storage fill level, tendency positive, 50% load
        [0.35, 1, 0.54],
    ]
)
STORAGE_RULES_2 = np.array(
    [
        # threshold, tendency, gas load
        # above 15% biogas storage fill level, tendency doesn't matter, full load
        [0.50, 0, 1],
        # above 10% biogas storage fill level, tendency positive, 50% load
        [0.35, 1, 0.54],
    ]
)

EFFICIENCY_RULES_1 = np.array(
    [
        # gas load, eta_el, eta_th
        [0, 0, 0],
        [0.54, 0.373, 0.494],
        [1, 0.408, 0.448],
    ]
)
EFFICIENCY_RULES_2 = np.array(
    [
        # gas load, eta_el, eta_th
        [0, 0, 0],
        [0.54, 0.373, 0.494],
        [1, 0.408, 0.448],
    ]
)

MINIMUM_LOAD_1 = 0.54
MINIMUM_LOAD_2 = 0.54

# can run at any load between minimum_load and 1
STEPLESS_INTERVALS_1 = True
STEPLESS_INTERVALS_2 = True

MAX_POWER_1 = 610  # kW of gas uptake
MAX_POWER_2 = 610  # kW of gas uptake

# time after changing the load until a new change can be made [hours]
LOAD_CHANGE_TIME_1 = 6
LOAD_CHANGE_TIME_2 = 6

# avg occurence [hours], duration [hours]
FAILURE_RULES_1 = np.array([144, 12])
FAILURE_RULES_2 = np.array([124, 16])

CAPEX_SP_1 = 411  # €/kW
CAPEX_SP_2 = 411  # €/kW

CAPEX_1 = CAPEX_SP_1 * MAX_POWER_1  # €
CAPEX_2 = CAPEX_SP_2 * MAX_POWER_2  # €
