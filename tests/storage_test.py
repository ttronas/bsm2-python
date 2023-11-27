"""
test storage_bsm2.py
"""

def test_storage():
    import sys
    import os
    path_name = os.path.dirname(__file__)
    sys.path.append(path_name + '/..')

    import numpy as np
    import time
    import bsm2.storageinit_bsm2 as storageinit
    from bsm2.storage_bsm2 import Storage


    tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                        # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

    activate = False    # if activate is False dummy states are 0
                        # if activate is True dummy states are activated

    Qstorage = 0        # storage flow rate regulation not used in this test


    # definition of the tested clarifier:
    storage = Storage(storageinit.VOL_S, storageinit.ystinit, tempmodel, activate)

    # Constant influent based on digester input from BSM2:
    yst_in = np.array([28.0665048629843, 48.9525780251450, 10361.7145189587, 20375.0163964256, 10210.0695779898, 553.280744847661, 3204.66026217631, 0.252251384955929, 1.68714307465010, 28.9098125063162, 4.68341082328394, 906.093288634802, 7.15490225533614, 33528.5561252986, 178.467454963180, 14.8580800598190, 0, 0, 0, 0, 0])

    timestep = 15/(60*24)
    endtime = 200
    simtime = np.arange(0, endtime, timestep)

    yst_out = np.zeros(21)
    yst_vol = 0


    start = time.perf_counter()

    for step in simtime:

        yst_out, yst_vol = storage.output(timestep, step, yst_in, Qstorage)


    stop = time.perf_counter()

    print('Steady state simulation completed after: ', stop - start, 'seconds')
    print('Sludge at t = 200 d: \n', yst_out)

    yst_out_matlab = np.array([28.0665048629843, 48.9525780251450, 10361.7145189587, 20375.0163964256, 10210.0695779898, 553.280744847661, 3204.66026217631, 0.252251384955929, 1.68714307465010, 28.9098125063162, 4.68341082328394, 906.093288634802, 7.15490225533614, 33528.5561252986, 178.467454963180, 14.8580800598190, 0, 0, 0, 0, 0])
    yst_vol_matlab = 144.364056261084

    print('Sludge difference to MatLab solution: \n', yst_out_matlab - yst_out)
    print('Volume difference to MatLab solution: \n', yst_vol_matlab - yst_vol)

    assert np.allclose(yst_out, yst_out_matlab, rtol=1e-5, atol=1e-5)
    assert np.allclose(yst_vol, yst_vol_matlab, rtol=1e-1, atol=1)  # tolerance is higher for volume because of the integration method. If the step size is reduced the result gets more accurate!


test_storage()
