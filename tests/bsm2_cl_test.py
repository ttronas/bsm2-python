
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
    from asm1 import aerationcontrol
    from asm1 import aerationcontrolinit
        
    # dyninfluent from BSM2:
    with open(path_name + '/../data/dyninfluent_bsm2.csv', 'r') as f:
        data_in = np.array(list(csv.reader(f, delimiter=","))).astype(np.float64)


    with open(path_name + '/../data/asm1_aerationvalues_ss_ps.csv', 'r') as f:
        controldata = list(csv.reader(f, delimiter=" "))
    aerationvalues3 = np.array(controldata[0]).astype(np.float64)
    aerationvalues4 = np.array(controldata[1]).astype(np.float64)
    aerationvalues5 = np.array(controldata[2]).astype(np.float64)

    with open(path_name + '/../data/asm1_values_ss_ps.csv', 'r') as f:
        initdata = list(csv.reader(f, delimiter=" "))
    yinit1 = np.array(initdata[0]).astype(np.float64)
    yinit2 = np.array(initdata[1]).astype(np.float64)
    yinit3 = np.array(initdata[2]).astype(np.float64)
    yinit4 = np.array(initdata[3]).astype(np.float64)
    yinit5 = np.array(initdata[4]).astype(np.float64)
    settlerinit = np.array(initdata[7]).astype(np.float64)

    with open(path_name + '/../data/sensornoise.csv', 'r', encoding='utf-8-sig') as f:
        noise = list(csv.reader(f, delimiter=","))
    noise = np.array(noise).astype(np.float64)
    noise_SO3 = noise[:,1]
    noise_SO4 = noise[:,2]
    noise_SO5 = noise[:,3]
    # noise_SO5 = np.zeros(len(simtime))  # use this when no noise should be used
    # noise_SO4 = np.zeros(len(simtime))  # use this when no noise should be used
    # noise_SO3 = np.zeros(len(simtime))  # use this when no noise should be used



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


    SO3_sensor = aerationcontrol.Oxygensensor(aerationcontrolinit.min_SO3, aerationcontrolinit.max_SO3, aerationcontrolinit.T_SO3, aerationcontrolinit.std_SO3)
    aerationcontrol3 = aerationcontrol.PIaeration(aerationcontrolinit.KLa3_min, aerationcontrolinit.KLa3_max, aerationcontrolinit.KSO3, aerationcontrolinit.TiSO3, aerationcontrolinit.TtSO3, aerationcontrolinit.SO3ref, aerationcontrolinit.KLa3offset, aerationvalues3[1], aerationvalues3[2], aerationvalues3[3], aerationvalues3[4])
    kla3_actuator = aerationcontrol.KLaactuator(aerationcontrolinit.T_KLa3)

    SO4_sensor = aerationcontrol.Oxygensensor(aerationcontrolinit.min_SO4, aerationcontrolinit.max_SO4, aerationcontrolinit.T_SO4, aerationcontrolinit.std_SO4)
    aerationcontrol4 = aerationcontrol.PIaeration(aerationcontrolinit.KLa4_min, aerationcontrolinit.KLa4_max, aerationcontrolinit.KSO4, aerationcontrolinit.TiSO4, aerationcontrolinit.TtSO4, aerationcontrolinit.SO4ref, aerationcontrolinit.KLa4offset, aerationvalues4[1], aerationvalues4[2], aerationvalues4[3], aerationvalues4[4])
    kla4_actuator = aerationcontrol.KLaactuator(aerationcontrolinit.T_KLa4)

    SO5_sensor = aerationcontrol.Oxygensensor(aerationcontrolinit.min_SO5, aerationcontrolinit.max_SO5, aerationcontrolinit.T_SO5, aerationcontrolinit.std_SO5)
    aerationcontrol5 = aerationcontrol.PIaeration(aerationcontrolinit.KLa5_min, aerationcontrolinit.KLa5_max, aerationcontrolinit.KSO5, aerationcontrolinit.TiSO5, aerationcontrolinit.TtSO5, aerationcontrolinit.SO5ref, aerationcontrolinit.KLa5offset, aerationvalues5[1], aerationvalues5[2], aerationvalues5[3], aerationvalues5[4])
    kla5_actuator = aerationcontrol.KLaactuator(aerationcontrolinit.T_KLa5)


    integration = 1            # step of integration in min
    control = 1                 # step of aeration control in min, should be equal or bigger than integration
    transferfunction = 15       # interval for transferfunction in min


    timestep = 15/(60*24)      # step of integration in mins
    endtime = 50               # end time of simulation in days
    simtime = np.arange(0, endtime, timestep)
    y_out5 = yinit5
    ys_in = np.zeros(21)
    ys_out = np.array(initdata[5]).astype(np.float64)
    Qintr = asm1init.Qintr
    numberstep = 0
    controlnumber = 1
    number_noise = 0
    control_timestep = integration/ (60 * 24)

    y_in = data_in[:, 1:]
    data_time = data_in[:, 0]
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

    SO3 = np.zeros(int(transferfunction/control)+1)
    kla3 = np.zeros(int(transferfunction/control)+1)
    SO3[int(transferfunction/control)-1] = yinit3[7]                    # for first step
    kla3[int(transferfunction / control) - 1] = aerationvalues3[0]      # for first step

    SO4 = np.zeros(int(transferfunction/control)+1)
    kla4 = np.zeros(int(transferfunction/control)+1)
    SO4[int(transferfunction/control)-1] = yinit4[7]                    # for first step
    kla4[int(transferfunction / control) - 1] = aerationvalues4[0] #      # for first step

    SO5 = np.zeros(int(transferfunction/control)+1)
    kla5 = np.zeros(int(transferfunction/control)+1)
    SO5[int(transferfunction/control)-1] = y_out5[7]                    # for first step
    kla5[int(transferfunction / control) - 1] = aerationvalues5[0]      # for first step

    kla3_a = aerationvalues3[0]
    kla4_a = aerationvalues4[0]
    kla5_a = aerationvalues5[0]

    sludge_height = 0
    y_out5_r[14] = asm1init.Qintr
    y_out5 = yinit5

    start = time.perf_counter()

    for i, step in enumerate(tqdm(simtime)):
        # get influent data that is smaller than and closest to current time step
        y_in_timestep = y_in[np.where(data_time <= step)[0][-1], :]

        yp_in_c, y_in_bp = input_splitter.outputs(y_in_timestep, (0, 0), reginit.Qbypass)
        y_plant_bp, y_in_as_c = bypass_plant.outputs(y_in_bp, (1 - reginit.Qbypassplant, reginit.Qbypassplant))
        yp_in = combiner_primclar_pre.output(yp_in_c, yst_sp_p, yt_sp_p)
        yp_uf, yp_of = primclar.outputs(timestep, step, yp_in)
        y_c_as_bp = combiner_primclar_post.output(yp_of[:21], y_in_as_c)
        y_bp_as, y_as_bp_c_eff = bypass_reactor.outputs(y_c_as_bp, (1 - reginit.QbypassAS, reginit.QbypassAS))

        control_start_time = step
        control_end_time = step + timestep
        control_time = np.arange(control_start_time, control_end_time, control_timestep)
        for i,step_CONTROL in enumerate(control_time):
            y_in1 = combiner_reactor.output(ys_r, y_bp_as, yst_sp_as, yt_sp_as, y_out5_r)
            reactor3.kla = kla3_a
            reactor4.kla = kla4_a
            reactor5.kla = kla5_a
            y_out1 = reactor1.output(control_timestep, step_CONTROL, y_in1)
            y_out2 = reactor2.output(control_timestep, step_CONTROL, y_out1)
            y_out3 = reactor3.output(control_timestep, step_CONTROL, y_out2)
            y_out4 = reactor4.output(control_timestep, step_CONTROL, y_out3)
            y_out5 = reactor5.output(control_timestep, step_CONTROL, y_out4)

            SO3[int(transferfunction / control)] = y_out3[7]
            SO3_meas = SO3_sensor.measureSO(SO3, step_CONTROL, controlnumber, noise_SO3[number_noise], transferfunction, control)
            kla3_value = aerationcontrol3.output(SO3_meas, step_CONTROL, control_timestep)
            kla3[int(transferfunction / control)] = kla3_value if np.isscalar(kla3_value) else kla3_value[0]
            kla3_a = kla3_actuator.real_actuator(kla3, step_CONTROL, controlnumber, transferfunction, control)

            SO4[int(transferfunction / control)] = y_out4[7]
            SO4_meas = SO4_sensor.measureSO(SO4, step_CONTROL, controlnumber, noise_SO4[number_noise], transferfunction, control)
            kla4_value = aerationcontrol4.output(SO4_meas, step_CONTROL, control_timestep)
            kla4[int(transferfunction / control)] = kla4_value if np.isscalar(kla4_value) else kla4_value[0]
            kla4_a = kla4_actuator.real_actuator(kla4, step_CONTROL, controlnumber, transferfunction, control)

            SO5[int(transferfunction / control)] = y_out5[7]
            SO5_meas = SO5_sensor.measureSO(SO5, step_CONTROL, controlnumber, noise_SO5[number_noise], transferfunction, control)
            kla5_value = aerationcontrol5.output(SO5_meas, step_CONTROL, control_timestep)
            kla5[int(transferfunction / control)] = kla5_value if np.isscalar(kla5_value) else kla5_value[0]
            kla5_a = kla5_actuator.real_actuator(kla5, step_CONTROL, controlnumber, transferfunction, control)

            # for next step:
            SO3[0:int(transferfunction / control)] = SO3[1:(int(transferfunction / control) + 1)]
            kla3[0:int(transferfunction / control)] = kla3[1:(int(transferfunction / control) + 1)]

            SO4[0:int(transferfunction / control)] = SO4[1:(int(transferfunction / control) + 1)]
            kla4[0:int(transferfunction / control)] = kla4[1:(int(transferfunction / control) + 1)]

            SO5[0:int(transferfunction / control)] = SO5[1:(int(transferfunction / control) + 1)]
            kla5[0:int(transferfunction / control)] = kla5[1:(int(transferfunction / control) + 1)]

            number_noise += integration
            controlnumber = controlnumber + 1
            


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


    # Values from 50 days dynamic simulation in Matlab (bsm2_cl_test.slx):
    primaryout_matlab = np.array([34.0781695508385, 51.5088963430345, 55.5857355633134, 206.725250300590, 30.9483923743901, 0.0558093647662130, 0.305988561533712, 0.0238319730037380, 0.162590425718072, 25.9391863475649, 5.03254977543043, 8.12994927486516, 7.69286894220047, 220.215882123445, 21326.4030238398, 11.5115295465660, 0, 0, 0, 0, 0, 34.0781695508385, 51.5088963430345, 6930.21891663931, 25773.7210034456, 3858.52830944870, 6.95810015841009, 38.1494945767302, 0.0238319730037380, 0.162590425718072, 25.9391863475649, 5.03254977543043, 1013.61127427761, 7.69286894220047, 27455.6818682015, 150.337181436937, 11.5115295465660, 0, 0, 0, 0, 0, 34.0781695508385, 51.5088963430345, 103.708167830845, 385.694220572605, 57.7414517939103, 0.104125400321720, 0.570893103640088, 0.0238319730037380, 0.162590425718072, 25.9391863475649, 5.03254977543043, 15.1683185498844, 7.69286894220047, 410.864144025992, 21476.7402052767, 11.5115295465660, 0, 0, 0, 0, 0])
    SO3sensor_matlab = np.array([2.11309986767853, 2.08120251139749, 2.08120251139749, 0.0566073608601569, 2.13780987225764, 2.13780987225764])
    SO4sensor_matlab = np.array([2.07870609801482, 2.05445423298982, 2.05445423298982, 0.0566073608601569, 2.11106159384998, 2.11106159384998])
    SO5sensor_matlab = np.array([2.02431182977198, 2.00809763296601, 2.00809763296601, 0.0566073608601569, 2.06470499382617, 2.06470499382617])
    y_eff_matlab = np.array([30.3250109236350, 0.689227316080032, 5.69343355598311, 0.135863291881529, 10.1575881568484, 0.698110467246864, 3.11953740878253, 2.03463230311151, 13.0904183836608, 0.228133523818833, 0.544227974746346, 0.00994323707008142, 4.38161644447488, 14.8533996605568, 21027.7386956929, 11.1859044949032, 0, 0, 0, 0, 0])
    qpass_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    prim_in_matlab = np.array([34.1981984542604, 44.6344144042572, 96.9713156128289, 357.287967311833, 51.5755352686212, 0.108133685078857, 0.589594846065591, 0.0250099505853193, 0.165211043084054, 24.4706176588244, 4.35039708310642, 11.2282792500961, 7.69780972291982, 379.899410043321, 21476.7402052767, 11.4372448790711, 0, 0, 0, 0, 0])
    qthick2AS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    sludge_matlab = np.array([119.312076891418, 343.593241516994, 310851.059661709, 50549.5702318803, 0, 0, 11932.7034397439, 0, 0, 1423.57907921454, 0.727706133036176, 1977.22102498423, 96.4033861788181, 280000, 9.38332357804472, 11.4455635064044, 0, 0, 0, 0, 0])
    qpassplant_to_as_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qpassAS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qthick2AS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    qstorage2AS_matlab = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    digesterout_matlab = np.array([0.0155254842729878, 0.00742557278608343, 0.135198402077787, 0.0176580966467297, 0.0199136452167958, 0.0247901198265885, 0.123081920690022, 3.22717181711647e-07, 0.0570786793959828, 0.0935869905856207, 0.0932511017461753, 0.119312076891418, 0.106143040440605, 0.0239852699735182, 0.112159458133552, 0.0507630736378084, 0.298109834500200, 0.943370703856276, 0.318975573673795, 0.337887451029054, 0.100264862545969, 0.665247083801272, 0.278231984083526, 16.0949037335317, 1.93994465447537e-44, 0.00528106367366438, 184.924556579061, 35, 0, 0, 0, 0, 0, 7.24170660191394, 5.73183127867197e-08, 0.0175874111784679, 0.0198412832197717, 0.0246812759823951, 0.122665401749438, 0.0838517744981659, 0.00973521608745478, 0.00177199209104278, 0.0914791096551325, 1.37624565014599e-05, 1.65889747282557, 0.0139040267766605, 2.20381069517217e-05, 0.664106729859468, 0.356236901900346, 1.07603341494176, 3347.78187241945])
    dewateringout_matlab = np.array([119.312076891418, 343.593241516994, 310851.059661709, 50549.5702318803, 0, 0, 11932.7034397439, 0, 0, 1423.57907921454, 0.727706133036176, 1977.22102498423, 96.4033861788181, 280000, 9.38332357804472, 11.4455635064044, 0, 0, 0, 0, 0, 119.312076891418, 343.593241516994, 339.104708930555, 55.1440851406495, 0, 0, 13.0172820742275, 0, 0, 1423.57907921454, 0.727706133036176, 2.15693316567208, 96.4033861788181, 305.449557109074, 175.541233001016, 11.4455635064044, 0, 0, 0, 0, 0])
    reac1_matlab = np.array([31.4959520637021, 2.90212669693944, 1513.64794046399, 71.3318589279459, 2698.70823726119, 184.168835398638, 823.914931064313, 0.0167778530790522, 6.83377451205077, 5.31228189491389, 0.922175929436329, 4.15331107212265, 5.31942223241556, 3968.82885233706, 103919.738695693, 11.2933687540066, 0, 0, 0, 0, 0])
    reac2_matlab = np.array([31.4542417522998, 1.34646556810971, 1508.58981718754, 66.0047545769406, 2691.17700673677, 183.466421721259, 821.867091438560, 0.000229678724635429, 4.94195878954588, 5.83177868592767, 0.695205551194924, 4.04400365017071, 5.47833682117649, 3953.32881874580, 103919.738695693, 11.2918256697711, 0, 0, 0, 0, 0])
    reac3_matlab = np.array([31.3584717439000, 0.980358549000252, 1494.01475711470, 51.6789593183165, 2668.56726001168, 182.567988585855, 815.344636116989, 2.02431182977198, 9.01165983209980, 2.28278518330499, 0.666039799269140, 3.40219052482129, 4.91147372186115, 3909.13020086065, 103919.738695693, 11.2863276969765, 0, 0, 0, 0, 0])
    reac4_matlab = np.array([31.2372664347240, 0.807837772954514, 1480.65461407474, 41.8055193890797, 2644.54046136157, 181.393948439357, 809.589990512238, 2.07870609801482, 11.3330536322631, 0.594494575991418, 0.603571637835450, 2.91963902553834, 4.60605738905843, 3868.48840033273, 103919.738695693, 11.2775266114138, 0, 0, 0, 0, 0])
    reac5_matlab = np.array([31.0830046871660, 0.689621206217737, 1470.86490003589, 35.0994782439970, 2624.15284942211, 180.352712036482, 805.914047087675, 2.11309986767853, 12.3757709606985, 0.182065036103153, 0.544921239239450, 2.56877651338342, 4.48600078957072, 3837.28799011962, 103919.738695693, 11.2651714765060, 0, 0, 0, 0, 0])
    thickenerin_matlab = np.array([30.3102005857051, 0.676585760544700, 3156.57929766537, 75.3259435187784, 5631.61617235773, 387.049576802243, 1729.54810239377, 2.02379142425514, 13.3679392430598, 0.203688699211867, 0.528396516163222, 5.51277466902452, 4.33652654078189, 8235.08931955342, 300.000000000000, 11.1588360948071, 0, 0, 0, 0, 0])
    kla3in_matlab = 183.802422461255
    kla4in_matlab = 117.445710897531
    kla5in_matlab = 80.2352227511895
    so4_matlab = SO4sensor_matlab[0]
    so5_matlab = SO5sensor_matlab[0]
    so3_matlab = SO3sensor_matlab[0]

    assert np.allclose(y_eff, y_eff_matlab, rtol=3e-1, atol=1e0)
    assert np.allclose(y_in_bp, qpass_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(yp_in, prim_in_matlab, rtol=1e0, atol=1e0)
    assert np.allclose(y_in_as_c, qpassplant_to_as_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(y_as_bp_c_eff, qpassAS_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(yt_sp_as, qthick2AS_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(yst_sp_as, qstorage2AS_matlab, rtol=1e-3, atol=1e-3)
    assert np.allclose(ydw_s, sludge_matlab, rtol=4e-2, atol=1e-2)

test_bsm2_cl()