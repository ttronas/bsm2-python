"""
test dewatering_bsm2.py
"""


def test_dewatering():
    import sys
    import os
    path_name = os.path.dirname(__file__)
    sys.path.append(path_name + '/..')

    import numpy as np
    import time
    from bsm2 import asm1init_bsm2 as asm1init
    from bsm2 import dewateringinit_bsm2 as dewateringinit
    from bsm2.dewatering_bsm2 import Dewatering

    # definition of the tested dewatering:
    dewatering = Dewatering(dewateringinit.DEWATERINGPAR)

    # CONSTINFLUENT from BSM2:
    y_in = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])

    timestep = 15/(60*24)
    endtime = 200
    simtime = np.arange(0, endtime, timestep)

    ydw_s = np.zeros(21)
    ydw_r = np.zeros(21)

    start = time.perf_counter()

    for step in simtime:

        ydw_s, ydw_r = dewatering.outputs(y_in)

    stop = time.perf_counter()

    print('Steady state simulation completed after: ', stop - start, 'seconds')
    print('Sludge flow at t = 200 d: \n', ydw_s)
    print('Reject flow at t = 200 d: \n', ydw_r)

    ydw_s_matlab = np.array([30, 69.5000000000000, 67857.1005952170, 268141.574070787, 37334.6586673293, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 14035.2870176435, 7, 280000, 13.6396410675000, 15, 0, 0, 0, 0, 0])
    ydw_r_matlab = np.array([30, 69.5000000000000, 1.02475774302266, 4.04939426891298, 0.563816906659147, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 0.211956728488476, 7, 4.22847668894609, 18432.3603589325, 15, 0, 0, 0, 0, 0])

    print('Sludge flow difference to MatLab solution: \n', ydw_s_matlab - ydw_s)
    print('Reject flow difference to MatLab solution: \n', ydw_r_matlab - ydw_r)

    assert np.allclose(ydw_s, ydw_s_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(ydw_r, ydw_r_matlab, rtol=1e-5, atol=1e-5)


test_dewatering()
