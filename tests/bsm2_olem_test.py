# From [tutorial](https://docs.pytest.org/en/7.1.x/getting-started.html)
# pytest tests all files containing test_*.py or *_test.py
# mind that pytest needs __init__.py files in the directories to work (they are used to be identified as python directories)

import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/../src/bsm2_python/')
import numpy as np
from bsm2_python.bsm2_olem import BSM2_OLEM

def test_bsm2_olem():
    TOTAL_SIM_STEPS = 35028

    timestep = 15 / 24 / 60  # 15 minutes in days
    endtime = TOTAL_SIM_STEPS * timestep

    tempmodel = False  # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

    activate = False  # if activate is False dummy states are 0
    # if activate is True dummy states are activated

    bsm2 = BSM2_OLEM(timestep=timestep, endtime=endtime, tempmodel=tempmodel, activate=activate)

    bsm2.stabilize()
    for i in range(0, TOTAL_SIM_STEPS):
        bsm2.step(i, True)
        if i % 1000 == 0:
            print(i)

    cumulative_cash_flow_simulated = np.array([bsm2.evaluator.economics_all[-1, 2]])
    cumulative_cash_flow_expected = np.array([92621366.91368307])

    assert np.allclose(cumulative_cash_flow_simulated, cumulative_cash_flow_expected, rtol=1e-5)

test_bsm2_olem()
