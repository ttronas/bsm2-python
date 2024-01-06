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
    import asm1.asm1init as asm1init
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
    reactor1 = ASM1reactor(reginit.KLa1, asm1init.VOL1, asm1init.yinit1, asm1init.PAR1, asm1init.carb1, asm1init.carbonsourceconc, tempmodel, activate)
    reactor2 = ASM1reactor(reginit.KLa2, asm1init.VOL2, asm1init.yinit2, asm1init.PAR2, asm1init.carb2, asm1init.carbonsourceconc, tempmodel, activate)
    reactor3 = ASM1reactor(reginit.KLa3, asm1init.VOL3, asm1init.yinit3, asm1init.PAR3, asm1init.carb3, asm1init.carbonsourceconc, tempmodel, activate)
    reactor4 = ASM1reactor(reginit.KLa4, asm1init.VOL4, asm1init.yinit4, asm1init.PAR4, asm1init.carb4, asm1init.carbonsourceconc, tempmodel, activate)
    reactor5 = ASM1reactor(reginit.KLa5, asm1init.VOL5, asm1init.yinit5, asm1init.PAR5, asm1init.carb5, asm1init.carbonsourceconc, tempmodel, activate)
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
        y_c_as_bp = combiner_primclar_post.output(yp_of[:21], y_in_as_c)
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

        y_eff = combiner_effluent.output(y_plant_bp, y_as_bp_c_eff, ys_of[:21])

        yt_uf, yt_of = thickener.outputs(ys_was)
        yt_sp_p, yt_sp_as = splitter_thickener.outputs(yt_of[:21], (1 - reginit.Qthickener2AS, reginit.Qthickener2AS))

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
    y_eff_matlab = np.array([29.3874555415727, 1.52897362389913, 4.65581499640368, 0.379002962910597, 11.4884519506262, 0.283338588859770, 1.34614311406866, 1.11634446598105, 2.63708083635177, 11.8463975982329, 0.939298481689982, 0.0243302727885532, 6.14735014255456, 13.6145637096517, 20435.4639808569, 11.4654728282066, 0, 0, 0, 0, 0])
    qpass_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    to_primary_matlab = np.array([33.5386583267995, 42.6657147645442, 95.2453383187624, 364.191303597616, 51.0302955304413, 0, 0, 0, 0, 13.0991673987175, 4.42838614018600, 11.4328142772815, 7, 382.850203085115, 21036.4553586537, 11.4404477663155, 0, 0, 0, 0, 0])
    prim_in_matlab = np.array([33.5386583267995, 42.6657147645442, 95.2453383187624, 364.191303597616, 51.0302955304413, 0, 0, 0, 0, 13.0991673987175, 4.42838614018600, 11.4328142772815, 7, 382.850203085115, 21036.4553586537, 11.4404477663155, 0, 0, 0, 0, 0])
    qpass_plant_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qpassplant_to_as_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qpassAS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    to_as_matlab = np.array([33.3999934781535, 50.7398987839784, 55.0881654774035, 212.200089226992, 31.1396578308966, 0, 0, 0, 0, 14.9171022587047, 5.22582665599624, 8.56978432465493, 7.00000000003392, 223.820934401469, 20820.4878888560, 11.4654641214523, 0, 0, 0, 0, 0])
    feed_settler_matlab = np.array([30.7054605246313, 1.56982211945007, 1109.77832779000, 90.3406331074735, 2738.43247734499, 67.5376976074138, 320.871953729068, 1.03196994567784, 2.60407313539255, 11.4512587480900, 0.965954669534312, 5.79945927207412, 6.18795484614749, 3245.22081718421, 39266.4639808569, 11.4654728282066, 0, 0, 0, 0, 0])
    qthick2AS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qthick2prim_matlab = np.array([29.1207505541861, 1.47185187294242, 54.1059368588912, 4.40445129293437, 133.509054016778, 3.29272099737119, 15.6437346391749, 1.15310231492479, 2.74445441600068, 11.7880711869949, 0.880839932559978, 0.282745814486594, 6.10524740994449, 158.216923353862, 346.612072953946, 11.4654728282066, 0, 0, 0, 0, 0])
    qstorage2AS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qstorage2prim_matlab = np.array([124.536027125454, 366.691614670528, 331.999860061585, 59.8912247579954, 0, 0, 14.1456017021493, 0, 0, 1584.54475210733, 0.719786207647379, 2.35005049635899, 107.821564593880, 304.527514891297, 175.790457491095, 11.4654659265751, 0, 0, 0, 0, 0])
    sludge_matlab = np.array([124.536027125454, 366.691614670528, 305259.644109421, 55067.4146414149, 0, 0, 13006.2745824975, 0, 0, 1584.54475210733, 0.719786207647379, 2160.77072449561, 107.821564593880, 280000, 9.36828045323928, 11.4654659265751, 0, 0, 0, 0, 0])

    print('Effluent difference to MatLab solution: \n', y_eff_matlab - y_eff[:21])
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

    assert np.allclose(y_eff[:21], y_eff_matlab, rtol=3e-1, atol=1e0)
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
