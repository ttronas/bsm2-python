"""Execution file for the BSM2 Open Loop Test Case (not connected)

The test case is based on the BSM2 Benchmark Simulation Model No. 2 (BSM2) and does not contain any controllers. But it runs the BSM2 model with dynamic influent data.
In this specific test case the BSM2 model has (almost) no return flows. It is made for debugging purposes.
"""


def test_bsm2_ol():
    import sys
    import os
    import numpy as np
    import time
    import csv
    from tqdm import tqdm
    path_name = os.path.dirname(__file__)
    sys.path.append(path_name + '/..')

    from bsm2.primclar_bsm2 import PrimaryClarifier
    from bsm2 import primclarinit_bsm2 as primclarinit
    from asm1.asm1 import ASM1reactor
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

    # dyninfluent from BSM2:
    with open(path_name + '/../data/dyninfluent_bsm2.csv', 'r') as f:
        data_in = np.array(list(csv.reader(f, delimiter=","))).astype(np.float64)

    # timesteps = np.diff(data_in[:, 0], append=(2*data_in[-1, 0] - data_in[-2, 0]))
    timestep = 15/24/60  # 15 minutes in days
    endtime = 50  # data_in[-1, 0]
    data_time = data_in[:, 0]
    simtime = np.arange(0, endtime, timestep)

    y_in = data_in[:, 1:]
    del data_in

    yst_sp_p = np.zeros(21)
    yt_sp_p = np.zeros(21)
    ys_r = np.zeros(21)
    yst_sp_as = np.zeros(21)
    yt_sp_as = np.zeros(21)
    y_out5_r = np.zeros(21)

    y_in_all = np.zeros((len(simtime), 21))
    y_eff_all = np.zeros((len(simtime), 21))
    y_in_bp_all = np.zeros((len(simtime), 21))
    to_primary_all = np.zeros((len(simtime), 21))
    prim_in_all = np.zeros((len(simtime), 21))
    qpass_plant_all = np.zeros((len(simtime), 21))
    qpassplant_to_as_all = np.zeros((len(simtime), 21))
    qpassAS_all = np.zeros((len(simtime), 21))
    to_as_all = np.zeros((len(simtime), 21))
    feed_settler_all = np.zeros((len(simtime), 21))
    qthick2AS_all = np.zeros((len(simtime), 21))
    qthick2prim_all = np.zeros((len(simtime), 21))
    qstorage2AS_all = np.zeros((len(simtime), 21))
    qstorage2prim_all = np.zeros((len(simtime), 21))
    sludge_all = np.zeros((len(simtime), 21))

    sludge_height = 0

    y_out5_r[14] = asm1init.Qintr

    start = time.perf_counter()

    for i, step in enumerate(tqdm(simtime)):

        # timestep = timesteps[i]
        # get influent data that is smaller than and closest to current time step
        y_in_timestep = y_in[np.where(data_time <= step)[0][-1], :]

        yp_in_c, y_in_bp = input_splitter.outputs(y_in_timestep, (0, 0), reginit.Qbypass)
        y_plant_bp, y_in_as_c = bypass_plant.outputs(y_in_bp, (1 - reginit.Qbypassplant, reginit.Qbypassplant))
        # yp_in = combiner_primclar_pre.output(yp_in_c, yst_sp_p, yt_sp_p)
        yp_uf, yp_of = primclar.outputs(timestep, step, yp_in_c)
        y_c_as_bp = combiner_primclar_post.output(yp_of, y_in_as_c)
        y_bp_as, y_as_bp_c_eff = bypass_reactor.outputs(y_c_as_bp, (1 - reginit.QbypassAS, reginit.QbypassAS))

        # y_in1 = combiner_reactor.output(ys_r, y_bp_as, yst_sp_as, yt_sp_as, y_out5_r)
        y_in1 = combiner_reactor.output(ys_r, y_bp_as, y_out5_r)
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

        y_in_all[i] = y_in_timestep
        y_eff_all[i] = y_eff
        y_in_bp_all[i] = y_in_bp
        to_primary_all[i] = yp_in_c
        # prim_in_all[i] = yp_in
        qpass_plant_all[i] = y_plant_bp
        qpassplant_to_as_all[i] = y_in_as_c
        qpassAS_all[i] = y_as_bp_c_eff
        to_as_all[i] = y_bp_as
        feed_settler_all[i] = ys_in
        qthick2AS_all[i] = yt_sp_as
        qthick2prim_all[i] = yt_sp_p
        qstorage2AS_all[i] = yst_sp_as
        qstorage2prim_all[i] = yst_sp_p
        sludge_all[i] = ydw_s

    stop = time.perf_counter()

    # np.savetxt(path_name + '/../data/y_in.csv', y_in_all, delimiter=',')
    # np.savetxt(path_name + '/../data/y_eff.csv', y_eff_all, delimiter=',')
    # np.savetxt(path_name + '/../data/qpass.csv', y_in_bp_all, delimiter=',')
    # np.savetxt(path_name + '/../data/to_primary.csv', to_primary_all, delimiter=',')
    # # np.savetxt(path_name + '/../data/prim_in.csv', prim_in_all, delimiter=',')
    # np.savetxt(path_name + '/../data/qpassplant.csv', qpass_plant_all, delimiter=',')
    # np.savetxt(path_name + '/../data/qpassplant_to_as.csv', qpassplant_to_as_all, delimiter=',')
    # np.savetxt(path_name + '/../data/qpassAS.csv', qpassAS_all, delimiter=',')
    # np.savetxt(path_name + '/../data/to_as.csv', to_as_all, delimiter=',')
    # np.savetxt(path_name + '/../data/feed_settler.csv', feed_settler_all, delimiter=',')
    # np.savetxt(path_name + '/../data/qthick2AS.csv', qthick2AS_all, delimiter=',')
    # np.savetxt(path_name + '/../data/qthick2prim.csv', qthick2prim_all, delimiter=',')
    # np.savetxt(path_name + '/../data/qstorage2AS.csv', qstorage2AS_all, delimiter=',')
    # np.savetxt(path_name + '/../data/qstorage2prim.csv', qstorage2prim_all, delimiter=',')
    # np.savetxt(path_name + '/../data/sludge.csv', sludge_all, delimiter=',')

    print('Dynamic open loop simulation completed after: ', stop - start, 'seconds')
    print('Effluent at t =', endtime, 'd:  \n', y_eff)
    print('qpass at t =', endtime, 'd:  \n', y_in_bp)
    print('to_primary at t =', endtime, 'd:  \n', yp_in_c)
    print('qpassplant at t =', endtime, 'd:  \n', y_plant_bp)
    print('qpassplant_to_as at t =', endtime, 'd:  \n', y_in_as_c)
    print('qpassAS at t =', endtime, 'd:  \n', y_as_bp_c_eff)
    print('to_as at t =', endtime, 'd:  \n', y_bp_as)
    print('feed_settler at t =', endtime, 'd:  \n', ys_in)
    print('qthick2AS at t =', endtime, 'd:  \n', yt_sp_as)
    print('qthick2prim at t =', endtime, 'd:  \n', yt_sp_p)
    print('qstorage2AS at t =', endtime, 'd:  \n', yst_sp_as)
    print('qstorage2prim at t =', endtime, 'd:  \n', yst_sp_p)
    print('sludge at t =', endtime, 'd:  \n', ydw_s)
    print('Sludge height at t = ', endtime, ' d:  \n', sludge_height)

    # Values from 50 days dynamic simulation in Matlab (bsm2_ol_test_not_connected.slx):
    y_eff_matlab = np.array([29.5701627218864, 0.781629350879610, 5.57546631598799, 0.163302722142466, 10.1069363037130, 0.500556770399133, 3.09936913792749, 1.52879314324714, 4.83810091761127, 0.338518769678028, 0.595511827878188, 0.0117647165859621, 5.06135413492737, 14.5842234376276, 20522.4640073652, 11.4654727516866, 0, 0, 0, 0, 0])
    qpass_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    to_primary_matlab = np.array([33.5386583267995, 42.6657147645442, 95.2453383187624, 364.191303597616, 51.0302955304413, 0, 0, 0, 0, 13.0991673987175, 4.42838614018600, 11.4328142772815, 7, 382.850203085115, 21036.4553586537, 11.4404477663155, 0, 0, 0, 0, 0])
    prim_in_matlab = np.array([33.5386583267995, 42.6657147645442, 95.2453383187624, 364.191303597616, 51.0302955304413, 0, 0, 0, 0, 13.0991673987175, 4.42838614018600, 11.4328142772815, 7, 382.850203085115, 21036.4553586537, 11.4404477663155, 0, 0, 0, 0, 0])
    qpass_plant_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qpassplant_to_as_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qpassAS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    to_as_matlab = np.array([33.3999938840992, 50.7398990084671, 55.0881666485864, 212.200094347947, 31.1396587686024, 0, 0, 0, 0, 14.9171024017455, 5.22582672264216, 8.56978468353797, 7.00000000004085, 223.820939823852, 20820.5157433254, 11.4654539800124, 0, 0, 0, 0, 0])
    feed_settler_matlab = np.array([30.3230848045964, 0.820871226128821, 1435.89157594168, 42.0565724485342, 2602.91496255036, 128.912132037394, 798.203734658395, 1.36456389292010, 4.84141570783631, 0.312341746399907, 0.624999061419290, 3.02985552808076, 5.11635328079754, 3755.98423322727, 41470.4640073652, 11.4654727516866, 0, 0, 0, 0, 0])
    qthick2AS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qthick2prim_matlab = np.array([29.5814803943307, 0.759269461443454, 67.8484559475846, 1.98724858540202, 122.992407038873, 6.09132977600505, 37.7165601049305, 1.77104032261893, 4.89012902473365, 0.327128044801209, 0.574684669579540, 0.143166115582033, 5.03291520254189, 177.477001089596, 266.848384305499, 11.4654727516866, 0, 0, 0, 0, 0])
    qstorage2AS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qstorage2prim_matlab = np.array([121.367403560618, 337.626368580548, 335.415883993523, 55.5869404558766, 0, 0, 13.1268902432479, 0, 0, 1426.49495461122, 0.727090749562776, 2.17377750726011, 96.5290819385813, 303.097286019486, 170.859869471431, 11.4654574387844, 0, 0, 0, 0, 0])
    sludge_matlab = np.array([121.367403560618, 337.626368580548, 309855.785089903, 51350.9821616972, 0, 0, 12126.5660817336, 0, 0, 1426.49495461122, 0.727090749562776, 2008.12653265955, 96.5290819385813, 280000, 9.06275347712598, 11.4654574387844, 0, 0, 0, 0, 0])

    print('Effluent difference to MatLab solution: \n', y_eff_matlab - y_eff)
    # print('Sludge height difference to MatLab solution: \n', sludge_height_matlab - sludge_height)
    print('qpass difference to MatLab solution: \n', qpass_matlab - y_in_bp)
    print('to_primary difference to MatLab solution: \n', to_primary_matlab - yp_in_c)
    # print('prim_in difference to MatLab solution: \n', prim_in_matlab - yp_in)
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
    # print('prim_in flow difference to Matlab: \n', prim_in_matlab[14] - yp_in[14])
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

    assert np.allclose(y_eff, y_eff_matlab, rtol=3e-1, atol=1e0)
    # assert np.allclose(sludge_height, sludge_height_matlab, rtol=1e-2, atol=1e-2)
    assert np.allclose(y_in_bp, qpass_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(yp_in_c, to_primary_matlab, rtol=1e-3, atol=1e-3)
    # assert np.allclose(yp_in, prim_in_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(y_plant_bp, qpass_plant_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(y_in_as_c, qpassplant_to_as_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(y_as_bp_c_eff, qpassAS_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(y_bp_as, to_as_matlab, rtol=4e-2, atol=1e-1)
    assert np.allclose(ys_in, feed_settler_matlab, rtol=4e-1, atol=1e-1)
    assert np.allclose(yt_sp_as, qthick2AS_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(yt_sp_p, qthick2prim_matlab, rtol=4e-1, atol=1e-1)
    assert np.allclose(yst_sp_as, qstorage2AS_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(yst_sp_p, qstorage2prim_matlab, rtol=4e-1, atol=1e-1)
    assert np.allclose(ydw_s, sludge_matlab, rtol=4e-2, atol=1e-2)


test_bsm2_ol()
