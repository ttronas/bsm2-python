"""Execution file for bsm2 model with primary clarifier,
5 asm1-reactors and a second clarifier, sludge thickener,
adm1-fermenter and sludge storage in steady state simulation

This script will run the plant to steady state.

This script requires that the packages from requirements.txt are installed
within the Python environment you are running this script.

The parameters 'tempmodel' and 'activate' can be set to 'True' if you want to activate them.
"""


def test_bsm2_ss():
    import sys
    import os
    path_name = os.path.dirname(__file__)
    sys.path.append(path_name + '/..')

    import numpy as np
    import time
    from bsm2.primclar_bsm2 import PrimaryClarifier
    from bsm2 import primclarinit_bsm2 as primclarinit
    from bsm2.asm1_bsm2 import ASM1reactor
    import bsm2.asm1init_bsm2 as asm1init
    from bsm2.settler1d_bsm2 import Settler
    import bsm2.settler1dinit_bsm2 as settler1dinit
    from bsm2.thickener_bsm2 import Thickener
    import bsm2.thickenerinit_bsm2 as thickenerinit
    from bsm2.adm1_bsm2 import ADM1Reactor
    import bsm2.adm1init_bsm2 as adm1init
    from bsm2.dewatering_bsm2 import Dewatering
    import bsm2.dewateringinit_bsm2 as dewateringinit
    from bsm2.storage_bsm2 import Storage
    import bsm2.storageinit_bsm2 as storageinit
    from bsm2.helpers_bsm2 import Combiner, Splitter
    import bsm2.reginit_bsm2 as reginit

    tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                        # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

    activate = False    # if activate is False dummy states are 0
                        # if activate is True dummy states are activated

    # definition of the objects:
    input_splitter = Splitter(sp_type=2)
    bypass_plant = Splitter()
    combiner_primclar_pre = Combiner()
    primclar = PrimaryClarifier(primclarinit.VOL_P, primclarinit.yinit1, primclarinit.PAR_P, asm1init.PAR1, primclarinit.XVECTOR_P, tempmodel, activate)
    combiner_primclar_post = Combiner()
    bypass_reactor = Splitter()
    combiner_reactor = Combiner()
    reactor1 = ASM1reactor(reginit.KLa1, asm1init.VOL1, asm1init.yinit1, asm1init.PAR1, reginit.carb1, reginit.carbonsourceconc, tempmodel, activate)
    reactor2 = ASM1reactor(reginit.KLa2, asm1init.VOL2, asm1init.yinit2, asm1init.PAR2, reginit.carb2, reginit.carbonsourceconc, tempmodel, activate)
    reactor3 = ASM1reactor(reginit.KLa3, asm1init.VOL3, asm1init.yinit3, asm1init.PAR3, reginit.carb3, reginit.carbonsourceconc, tempmodel, activate)
    reactor4 = ASM1reactor(reginit.KLa4, asm1init.VOL4, asm1init.yinit4, asm1init.PAR4, reginit.carb4, reginit.carbonsourceconc, tempmodel, activate)
    reactor5 = ASM1reactor(reginit.KLa5, asm1init.VOL5, asm1init.yinit5, asm1init.PAR5, reginit.carb5, reginit.carbonsourceconc, tempmodel, activate)
    splitter_reactor = Splitter()
    settler = Settler(settler1dinit.DIM, settler1dinit.LAYER, asm1init.Qr, asm1init.Qw, settler1dinit.settlerinit, settler1dinit.SETTLERPAR, asm1init.PAR1, tempmodel, settler1dinit.MODELTYPE)
    combiner_effluent = Combiner()
    thickener = Thickener(thickenerinit.THICKENERPAR, asm1init.PAR1)
    splitter_thickener = Splitter()
    combiner_adm1 = Combiner()
    adm1_reactor = ADM1Reactor(adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, adm1init.DIM_D)
    dewatering = Dewatering(dewateringinit.DEWATERINGPAR)
    storage = Storage(storageinit.VOL_S, storageinit.ystinit, tempmodel, activate)
    splitter_storage = Splitter()

    # CONSTINFLUENT from BSM2:
    y_in = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])

    timestep = 15/(60*24)
    endtime = 200
    simtime = np.arange(0, endtime, timestep)

    yst_sp_p = np.zeros(21)
    yt_sp_p = np.zeros(21)
    ys_r = np.zeros(21)
    yst_sp_as = np.zeros(21)
    yt_sp_as = np.zeros(21)
    y_out5_r = np.zeros(21)

    sludge_height = 0

    y_out5_r[14] = asm1init.Qintr

    start = time.perf_counter()

    for step in simtime:

        yp_in_c, y_in_bp = input_splitter.outputs(y_in, (0, 0), reginit.Qbypass)
        y_plant_bp, y_in_as_c = bypass_plant.outputs(y_in_bp, (1 - reginit.Qbypassplant, reginit.Qbypassplant))
        yp_in = combiner_primclar_pre.output(yp_in_c, yst_sp_p, yt_sp_p)
        yp_uf, yp_of = primclar.outputs(timestep, step, yp_in)
        y_c_as_bp = combiner_primclar_post.output(yp_of, y_in_as_c)
        y_bp_as, y_as_bp_c_eff = bypass_reactor.outputs(y_c_as_bp, (1 - reginit.QbypassAS, reginit.QbypassAS))

        y_in1 = combiner_reactor.output(ys_r, y_bp_as, yst_sp_as, yt_sp_as, y_out5_r)
        y_out1 = reactor1.output(timestep, step, y_in1)
        y_out2 = reactor2.output(timestep, step, y_out1)
        y_out3 = reactor3.output(timestep, step, y_out2)
        y_out4 = reactor4.output(timestep, step, y_out3)
        y_out5 = reactor5.output(timestep, step, y_out4)
        ys_in, y_out5_r = splitter_reactor.outputs(y_out5, (y_out5[14] - asm1init.Qintr, asm1init.Qintr))

        ys_r, ys_was, ys_of, sludge_height = settler.outputs(timestep, step, ys_in)

        y_eff = combiner_effluent.output(y_plant_bp, y_as_bp_c_eff, ys_of)

        yt_uf, yt_of = thickener.outputs(ys_was)
        yt_sp_p, yt_sp_as = splitter_thickener.outputs(yt_of, (1 - reginit.Qthickener2AS, reginit.Qthickener2AS))

        yd_in = combiner_adm1.output(yt_uf, yp_uf)
        y_out2, _, _ = adm1_reactor.outputs(timestep, step, yd_in, reginit.T_op)
        ydw_s, ydw_r = dewatering.outputs(y_out2)
        yst_out, yst_vol = storage.output(timestep, step, ydw_r, reginit.Qstorage)

        yst_sp_p, yst_sp_as = splitter_storage.outputs(yst_out, (1 - reginit.Qstorage2AS, reginit.Qstorage2AS))

    stop = time.perf_counter()

    print('Steady state simulation completed after: ', stop - start, 'seconds')
    print('Effluent at t =', endtime, 'd:  \n', y_eff)
    print('Sludge height at t =', endtime, 'd:  \n', sludge_height)

    y_eff_matlab = np.array([30.5979681770102, 0.608361609456786, 3.66353722641872, 0.0898060284541909, 7.01040592443153, 0.786722105819775, 3.20074668356883, 3.25700843348046, 21.3898677651971, 0.0892571717264604, 0.549016345972289, 0.00701055885157449, 3.15017550810844, 11.0634134765198, 18442.7973813784, 15.0000000000001, 0, 0, 0, 0, 0])
    sludge_height_matlab = 0.457724633312847
    qpass_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    to_primary_matlab = np.array([30, 69.5000000000000, 51.2000000000000, 202.320000000000, 28.1700000000000, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 10.5900000000000, 7, 211.267500000000, 18446, 15, 0, 0, 0, 0, 0])
    prim_in_matlab = np.array([30.6012293502389, 69.4674432367099, 52.2843613673603, 198.009773123217, 28.4106946334078, 0.0985201683875570, 0.462372394797204, 0.0486140495865043, 0.319264783918738, 39.0318681732599, 6.80468221689654, 10.3612369728268, 7.43733219932853, 209.449291265377, 18872.9077355476, 15.0000000000000, 0, 0, 0, 0, 0])
    qpass_plant_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qpassplant_to_as_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qpassAS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    to_as_matlab = np.array([30.6012295422528, 69.4674432849700, 26.7028164843932, 101.128105674736, 14.5099895063862, 0.0503164980100970, 0.236144166638143, 0.0486140490194917, 0.319264781943206, 39.0318684074969, 6.80468221858581, 5.29171995393789, 7.43733221649640, 106.970529247623, 18740.7973813886, 15.0000000000000, 0, 0, 0, 0, 0])
    feed_settler_matlab = np.array([30.5979675660498, 0.608361610600194, 769.146945065516, 18.8544644601662, 1471.81042997526, 165.169579810250, 671.985674348427, 3.25700847044332, 21.3898676553269, 0.0892571862104238, 0.549016348029494, 1.47184253649897, 3.15017551643095, 2322.72532024472, 39390.7973813784, 15.0000000000001, 0, 0, 0, 0, 0])
    qthick2AS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qthick2prim_matlab = np.array([30.5979682321423, 0.608361609353706, 30.7370004837285, 0.753470694970006, 58.8171586565332, 6.60058196563786, 26.8541975366578, 3.25700843014223, 21.3898677751696, 0.0892571704195771, 0.549016345786742, 0.0588184417120548, 3.15017550735201, 92.8218070031455, 281.696683375599, 15.0000000000001, 0, 0, 0, 0, 00])
    qstorage2AS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qstorage2prim_matlab = np.array([106.981057708769, 198.912362049107, 231.829578406794, 33.1462972232107, 0, 0, 7.99920631596549, 0, 0, 1063.72029553350, 0.480566488836894, 1.28750843380016, 71.3078670610311, 204.731311459478, 145.211052171986, 15.0000000000000, 0, 0, 0, 0, 0])
    sludge_matlab = np.array([106.981057708769, 198.912362049107, 317060.841798742, 45332.4074189598, 0, 0, 10940.0841156320, 0, 0, 1063.72029553350, 0.480566488836894, 1760.85601608330, 71.3078670610311, 280000, 5.20261860117672, 15.0000000000000, 0, 0, 0, 0, 0])

    print('Effluent difference to MatLab solution: \n', y_eff_matlab - y_eff)
    print('Sludge height difference to MatLab solution: \n', sludge_height_matlab - sludge_height)
    print('qpass difference to MatLab solution: \n', qpass_matlab - y_in_bp)
    print('to_primary difference to MatLab solution: \n', to_primary_matlab - yp_in_c)
    print('prim_in difference to MatLab solution: \n', prim_in_matlab - yp_in)
    print('qpassplant difference to MatLab solution: \n', qpass_plant_matlab - y_plant_bp)
    print('qpassplant_to_as difference to MatLab solution: \n', qpassplant_to_as_matlab - y_in_as_c)
    print('qpassAS difference to MatLab solution: \n', qpassAS_matlab - y_as_bp_c_eff)
    print('to_as difference to MatLab solution: \n', to_as_matlab - y_bp_as)
    print('feed (settler) difference to MatLab solution: \n', feed_settler_matlab - ys_in)
    print('qthick2AS difference to MatLab solution: \n', qthick2AS_matlab - yt_sp_as)
    print('qthick2prim difference to MatLab solution: \n', qthick2prim_matlab - yt_sp_p)
    print('qstorage2AS difference to MatLab solution: \n', qstorage2AS_matlab - yst_sp_as)
    print('qstorage2prim difference to MatLab solution: \n', qstorage2prim_matlab - yst_sp_p)
    print('sludge difference to MatLab solution: \n', sludge_matlab - ydw_s)

    print('Effluent flow difference to Matlab: \n', y_eff_matlab[14] - y_eff[14])
    print('qpass flow difference to Matlab: \n', qpass_matlab[14] - y_in_bp[14])
    print('to_primary flow difference to Matlab: \n', to_primary_matlab[14] - yp_in_c[14])
    print('prim_in flow difference to Matlab: \n', prim_in_matlab[14] - yp_in[14])
    print('qpassplant flow difference to Matlab: \n', qpass_plant_matlab[14] - y_plant_bp[14])
    print('qpassplant_to_as flow difference to Matlab: \n', qpassplant_to_as_matlab[14] - y_in_as_c[14])
    print('qpassAS flow difference to Matlab: \n', qpassAS_matlab[14] - y_as_bp_c_eff[14])
    print('to_as flow difference to Matlab: \n', to_as_matlab[14] - y_bp_as[14])
    print('feed (settler) flow difference to Matlab: \n', feed_settler_matlab[14] - ys_in[14])
    print('qthick2AS flow difference to Matlab: \n', qthick2AS_matlab[14] - yt_sp_as[14])
    print('qthick2prim flow difference to Matlab: \n', qthick2prim_matlab[14] - yt_sp_p[14])
    print('qstorage2AS flow difference to Matlab: \n', qstorage2AS_matlab[14] - yst_sp_as[14])
    print('qstorage2prim flow difference to Matlab: \n', qstorage2prim_matlab[14] - yst_sp_p[14])
    print('sludge flow difference to Matlab: \n', sludge_matlab[14] - ydw_s[14])

    assert np.allclose(y_eff, y_eff_matlab, rtol=5e-2, atol=5e-2)
    assert np.allclose(sludge_height, sludge_height_matlab, rtol=1e-2, atol=1e-2)
    assert np.allclose(y_in_bp, qpass_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(yp_in_c, to_primary_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(yp_in, prim_in_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(y_plant_bp, qpass_plant_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(y_in_as_c, qpassplant_to_as_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(y_as_bp_c_eff, qpassAS_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(y_bp_as, to_as_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(ys_in, feed_settler_matlab, rtol=5e-2, atol=5e-2)
    assert np.allclose(yt_sp_as, qthick2AS_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(yt_sp_p, qthick2prim_matlab, rtol=5e-2, atol=5e-2)
    assert np.allclose(yst_sp_as, qstorage2AS_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(yst_sp_p, qstorage2prim_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(ydw_s, sludge_matlab, rtol=1e-3, atol=1e-3)


test_bsm2_ss()
