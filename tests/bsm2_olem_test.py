# From [tutorial](https://docs.pytest.org/en/7.1.x/getting-started.html)
# pytest tests all files containing test_*.py or *_test.py
# mind that pytest needs __init__.py files in the directories to work
# (they are used to be identified as python directories)

import numpy as np

from bsm2_python.bsm2_olem import BSM2OLEM
from bsm2_python.log import logger


def test_bsm2_olem():
    # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler
    tempmodel = False

    activate = False  # if activate is False dummy states are 0
    # if activate is True dummy states are activated

    bsm2_olem = BSM2OLEM(endtime=20, timestep=15 / 24 / 60, tempmodel=tempmodel, activate=activate)

    bsm2_olem.simulate()

    cumulative_cash_flow_simulated = np.array([bsm2_olem.economics.cum_cash_flow])
    cumulative_cash_flow_expected = np.array([154648.75876754])
    logger.info('cumulative cash flow: %s', cumulative_cash_flow_simulated)
    logger.info('difference to expected value: %s', cumulative_cash_flow_simulated - cumulative_cash_flow_expected)
    assert np.allclose(cumulative_cash_flow_simulated, cumulative_cash_flow_expected, rtol=1e-2)


test_bsm2_olem()
