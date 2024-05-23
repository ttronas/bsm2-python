
def test_bsm2_cl():
    import sys
    import os
    import numpy as np
    import time
    import csv
    from tqdm import tqdm
    import os

    path_name = os.path.dirname(__file__)
    sys.path.append(path_name + '/..')

    from bsm2.bsm2_cl import BSM2_CL

    bsm2_cl = BSM2_CL(endtime=50, timestep=1/60/24)
    start = time.perf_counter()
    for idx, stime in enumerate(tqdm(bsm2_cl.simtime)):
        bsm2_cl.step(idx)
    
    stop = time.perf_counter()    
    print('Dynamic open loop simulation completed after: ', stop - start, 'seconds')
    y_eff_matlab = np.array([30.325155279916,0.700246902106201,5.70368210115735,0.139538406214234,10.170734195434,0.694338562640143,3.10834182764915,1.65315755118803,10.8355276819539,0.280568276679927,0.552589025343316,0.0102191557618448,4.54640264730173,14.8624763198212,21027.7298540125,11.4418804233311,0,0,0,0,0])
    assert np.allclose(bsm2_cl.y_eff_all[-1,:], y_eff_matlab, rtol=3e-1, atol=1e0)

test_bsm2_cl()
