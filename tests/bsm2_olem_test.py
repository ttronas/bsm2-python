# From [tutorial](https://docs.pytest.org/en/7.1.x/getting-started.html)
# pytest tests all files containing test_*.py or *_test.py
# mind that pytest needs __init__.py files in the directories to work
# (they are used to be identified as python directories)
import logging

import numpy as np
from tqdm import tqdm

from bsm2_python.bsm2_olem import BSM2OLEM


def test_bsm2_olem():
    # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler
    tempmodel = False

    activate = False  # if activate is False dummy states are 0
    # if activate is True dummy states are activated

    bsm2_olem = BSM2OLEM(endtime=50, timestep=15 / 24 / 60, tempmodel=tempmodel, activate=activate)

    bsm2_olem.stabilize()
    for i, _ in enumerate(tqdm(bsm2_olem.simtime)):
        print(i, bsm2_olem.simtime)
        bsm2_olem.step(i, stabilized=True)
        if i % 1000 == 0:
            logging.info(i)

    cumulative_cash_flow_simulated = np.array([bsm2_olem.economics.cum_cash_flow])
    cumulative_cash_flow_expected = np.array([15931573.30219831])

    assert np.allclose(cumulative_cash_flow_simulated, cumulative_cash_flow_expected, rtol=1e-2)


test_bsm2_olem()
