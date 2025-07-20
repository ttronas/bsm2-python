import csv
import os

import numpy as np

import bsm2_python.bsm2_custom_layout as bsm2_cul

path_name = os.path.dirname(__file__)
with open(path_name + '/data/dyncustominfluent_bsm2.csv', encoding='utf-8-sig') as f:
    data_in = np.array(list(csv.reader(f, delimiter=','))).astype(float)

timestep = 1 / 24 / 60  # 1 minute in fraction of a day
"""1 minute in fraction of a day [d⁻¹]."""

endtime = 30  # 30 days
"""Endtime [d]."""

total_steps = int(endtime / timestep)
"""Total simulation steps [-]."""

# if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler
# if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
tempmodel = False

# if activate is True dummy states are activated
activate = False  # if activate is False dummy states are 0

safe_data_out = False
data_out = 'data_out' if safe_data_out else None

bsm2_custom = bsm2_cul.BSM2CustomLayout(
    data_in=data_in, timestep=timestep, endtime=endtime, data_out=data_out, tempmodel=tempmodel, activate=activate
)

bsm2_custom.simulate()
