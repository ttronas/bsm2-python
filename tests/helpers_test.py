"""
test helpers_bsm2.py
"""

import logging
import time

import numpy as np

from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter


def test_helpers():
    combiner = Combiner()
    splitter = Splitter()
    splitter2 = Splitter(sp_type=2)

    # CONSTINFLUENT from BSM2:
    y_in1 = np.array(
        [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0]
    )

    # Constant influent based on digester input from BSM2:
    y_in2 = np.array(
        [
            28.0665048629843,
            48.9525780251450,
            10361.7145189587,
            20375.0163964256,
            10210.0695779898,
            553.280744847661,
            3204.66026217631,
            0.252251384955929,
            1.68714307465010,
            28.9098125063162,
            4.68341082328394,
            906.093288634802,
            7.15490225533614,
            33528.5561252986,
            178.467454963180,
            14.8580800598190,
            0,
            0,
            0,
            0,
            0,
        ]
    )

    y_mix = np.zeros(21)
    y_split1 = np.zeros(21)
    y_split2 = np.zeros(21)
    y_split3 = np.zeros(21)
    y_split4 = np.zeros(21)

    start = time.perf_counter()

    y_mix = combiner.output(y_in1, y_in2)

    y_split1, y_split2 = splitter.outputs(y_in1, (0.6, 0.4))
    y_split3, y_split4 = splitter2.outputs(y_in1, (0, 0), 18000)

    stop = time.perf_counter()

    logging.info('Simulation completed after: %s seconds', stop - start)
    logging.info('Mix: \n%s', y_mix)
    logging.info('Split flow 1: \n%s', y_split1)
    logging.info('Split flow 2: \n%s', y_split2)
    logging.info('Split flow 3: \n%s', y_split3)
    logging.info('Split flow 4: \n%s', y_split4)
    logging.info('3 flow: \n%s', y_split3[14])
    logging.info('4 flow: \n%s', y_split4[14])

    y_mix_ref = np.array(
        [
            2.99814724e01,
            6.93031060e01,
            1.49999673e02,
            3.95623234e02,
            1.25737230e02,
            5.30176805e00,
            3.07083981e01,
            2.41717852e-03,
            1.61669122e-02,
            3.15346048e01,
            6.92828059e00,
            1.91710879e01,
            7.00148434e00,
            5.30527727e02,
            1.86244675e04,
            1.49986401e01,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    y_split1_ref = np.array(
        [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 1.106760e04, 15, 0, 0, 0, 0, 0]
    )
    y_split2_ref = np.array(
        [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 7.378400e03, 15, 0, 0, 0, 0, 0]
    )
    y_split3_ref = np.array(
        [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18000, 15, 0, 0, 0, 0, 0]
    )
    y_split4_ref = np.array(
        [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 446, 15, 0, 0, 0, 0, 0]
    )

    logging.info('Mix difference: \n%s', y_mix_ref - y_mix)
    logging.info('Split flow 1 difference: \n%s', y_split1_ref - y_split1)
    logging.info('Split flow 2 difference: \n%s', y_split2_ref - y_split2)
    logging.info('Split flow 3 difference: \n%s', y_split3_ref - y_split3)
    logging.info('Split flow 4 difference: \n%s', y_split4_ref - y_split4)

    assert np.allclose(y_mix, y_mix_ref, rtol=1e-5, atol=1e-5)
    assert np.allclose(y_split1, y_split1_ref, rtol=1e-5, atol=1e-5)
    assert np.allclose(y_split2, y_split2_ref, rtol=1e-5, atol=1e-5)
    assert np.allclose(y_split3, y_split3_ref, rtol=1e-5, atol=1e-5)
    assert np.allclose(y_split4, y_split4_ref, rtol=1e-5, atol=1e-5)


test_helpers()
