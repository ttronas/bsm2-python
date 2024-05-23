"""
Model file for bsm2 model with primary clarifier,
5 asm1-reactors and a second clarifier, sludge thickener,
adm1-fermenter and sludge storage in steady state simulation

This file holds the plant in a closed loop simulation with dynamic input data.
"""
import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')

import numpy as np
import csv
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
from bsm2.plantperformance import PlantPerformance
from bsm2 import aerationcontrol
from bsm2 import aerationcontrolinit


class BSM2_CL:
    def __init__(self, data_in=None, tempmodel=False, activate=False, timestep=None, endtime=None, use_noise=1, noise_file=None, noise_seed=1):
        """
        Creates a BSM2_CL object.

        Parameters
        ----------
        data_in : np.ndarray, optional
            Influent data. Has to be a 2D array. First column is time in days, the rest are 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
            If not provided, the influent data from BSM2 is used
        tempmodel : bool, optional
            If True, the temperature model dependencies are activated. Default is False
        activate : bool, optional
            If True, the dummy states are activated. Default is False
        timestep : float, optional
            Timestep for the simulation in days. If not provided, the timestep is calculated from the influent data
        endtime : float, optional
            Endtime for the simulation in days. If not provided, the endtime is the last time step in the influent data
        use_noise : int, optional
            If 0, no noise is added to the sensor data.
            If 1, a noise file is used to add noise to the sensor data. If so, a noise_file has to be provided. Needs to have at least 2 columns: time and noise data
            If 2, a random number generator is used to add noise to the sensor data. Seed is used from noise_seed. Default is 1
        noise_in : str, optional
            Noise data. Needs to be provided if use_noise is 1. If not provided, the default noise file is used
        noise_seed : int, optional
            Seed for the random number generator. Default is 1
        """

        # definition of the objects:
        self.input_splitter = Splitter(sp_type=2)
        self.bypass_plant = Splitter()
        self.combiner_primclar_pre = Combiner()
        self.primclar = PrimaryClarifier(primclarinit.VOL_P, primclarinit.yinit1, primclarinit.PAR_P, asm1init.PAR1, primclarinit.XVECTOR_P, tempmodel, activate)
        self.combiner_primclar_post = Combiner()
        self.bypass_reactor = Splitter()
        self.combiner_reactor = Combiner()
        self.reactor1 = ASM1reactor(reginit.KLa1, asm1init.VOL1, asm1init.yinit1, asm1init.PAR1, reginit.carb1, reginit.carbonsourceconc, tempmodel, activate)
        self.reactor2 = ASM1reactor(reginit.KLa2, asm1init.VOL2, asm1init.yinit2, asm1init.PAR2, reginit.carb2, reginit.carbonsourceconc, tempmodel, activate)
        self.reactor3 = ASM1reactor(reginit.KLa3, asm1init.VOL3, asm1init.yinit3, asm1init.PAR3, reginit.carb3, reginit.carbonsourceconc, tempmodel, activate)
        self.reactor4 = ASM1reactor(reginit.KLa4, asm1init.VOL4, asm1init.yinit4, asm1init.PAR4, reginit.carb4, reginit.carbonsourceconc, tempmodel, activate)
        self.reactor5 = ASM1reactor(reginit.KLa5, asm1init.VOL5, asm1init.yinit5, asm1init.PAR5, reginit.carb5, reginit.carbonsourceconc, tempmodel, activate)
        self.splitter_reactor = Splitter()
        self.settler = Settler(settler1dinit.DIM, settler1dinit.LAYER, asm1init.Qr, asm1init.Qw, settler1dinit.settlerinit, settler1dinit.SETTLERPAR, asm1init.PAR1, tempmodel, settler1dinit.MODELTYPE)
        self.combiner_effluent = Combiner()
        self.thickener = Thickener(thickenerinit.THICKENERPAR, asm1init.PAR1)
        self.splitter_thickener = Splitter()
        self.combiner_adm1 = Combiner()
        self.adm1_reactor = ADM1Reactor(adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, adm1init.DIM_D)
        self.dewatering = Dewatering(dewateringinit.DEWATERINGPAR)
        self.storage = Storage(storageinit.VOL_S, storageinit.ystinit, tempmodel, activate)
        self.splitter_storage = Splitter()

        self.SO4_sensor = aerationcontrol.Oxygensensor(aerationcontrolinit.min_SO4, aerationcontrolinit.max_SO4, aerationcontrolinit.T_SO4, aerationcontrolinit.std_SO4)
        self.aerationcontrol4 = aerationcontrol.PIaeration(aerationcontrolinit.KLa4_min, aerationcontrolinit.KLa4_max, aerationcontrolinit.KSO4, aerationcontrolinit.TiSO4, aerationcontrolinit.TtSO4, aerationcontrolinit.SO4ref, aerationcontrolinit.KLa4offset, aerationcontrolinit.SO4intstate, aerationcontrolinit.SO4awstate, aerationcontrolinit.kla4_lim, aerationcontrolinit.kla4_calc, aerationcontrolinit.useantiwindupSO4)

        self.kla4_actuator = aerationcontrol.KLaactuator(aerationcontrolinit.T_KLa4)

        if data_in is None:
            # dyninfluent from BSM2:
            with open(path_name + '/../data/dyninfluent_bsm2.csv', 'r', encoding='utf-8-sig') as f:
                data_in = np.array(list(csv.reader(f, delimiter=","))).astype(np.float64)

        if endtime is None:
            self.endtime = data_in[-1, 0]
        else:
            if endtime > data_in[-1, 0]:
                raise ValueError("Endtime is larger than the last time step in data_in.\n Please provide a valid endtime.\n Endtime should be given in days.")
            self.endtime = endtime

        if use_noise == 0:
            self.noise_SO4 = np.zeros((2))
            self.noise_timestep = np.array((0, self.endtime))
        elif use_noise == 1:
            if noise_file is None:
                noise_file = path_name + '/../data/sensornoise.csv'
            with open(noise_file, 'r', encoding='utf-8-sig') as f:
                noise_data = np.array(list(csv.reader(f, delimiter=","))).astype(np.float64)
            if noise_data[-1,0] < self.endtime:
                raise ValueError("Noise file does not cover the whole simulation time.\n Please provide a valid noise file.")
            if noise_data.shape[1] < 2:
                raise ValueError("Noise file needs to have at least 2 columns: time and noise data")
            self.noise_SO4 = noise_data[:, 1]
            self.noise_timestep = noise_data[:, 0]
            del noise_data

        if timestep is None:
            # calculate difference between each time step in data_in
            self.simtime = self.noise_timestep
            self.timestep = np.diff(self.noise_timestep, append=(2*self.noise_timestep[-1,] - self.noise_timestep[-2,]))
        else:
            self.simtime = np.arange(0, data_in[-1, 0], timestep)
            self.timestep = timestep * np.ones(len(self.simtime))

        self.simtime = self.simtime[self.simtime <= self.endtime]

        if use_noise == 0 or use_noise == 1:
            pass
        elif use_noise == 2:
            np.random.seed(noise_seed)
            # create random noise array with mean 0 and variance 1
            self.noise_SO4 = np.random.normal(0, 1, len(self.simtime))
            self.noise_timestep = np.arange(0, self.endtime, self.timestep)
        else:
            raise ValueError("use_noise has to be 0, 1 or 2")

        self.data_time = data_in[:, 0]
        # self.simtime = np.arange(0, self.endtime, self.timestep)


        self.timestep_integration = np.round(self.timestep*24*60)    # step of integration in min
        self.control = np.round(self.timestep*24*60)  # step of aeration self.control in min, should be equal or bigger than timestep_integration
        self.transferfunction = 15       # interval for transferfunction in min
        self.max_transfer_per_control = int(np.max(self.transferfunction/self.control, axis=0))

        self.numberstep = 1
        self.controlnumber = 1

        self.y_in = data_in[:, 1:]


        self.yst_sp_p = np.zeros(21)
        self.yt_sp_p = np.zeros(21)
        self.ys_r = np.zeros(21)
        self.yst_sp_as = np.zeros(21)
        self.yt_sp_as = np.zeros(21)
        self.y_out5_r = np.zeros(21)

        self.y_in_all = np.zeros((len(self.simtime), 21))
        self.y_eff_all = np.zeros((len(self.simtime), 21))
        self.y_in_bp_all = np.zeros((len(self.simtime), 21))
        self.to_primary_all = np.zeros((len(self.simtime), 21))
        self.prim_in_all = np.zeros((len(self.simtime), 21))
        self.qpass_plant_all = np.zeros((len(self.simtime), 21))
        self.qpassplant_to_as_all = np.zeros((len(self.simtime), 21))
        self.qpassAS_all = np.zeros((len(self.simtime), 21))
        self.to_as_all = np.zeros((len(self.simtime), 21))
        self.feed_settler_all = np.zeros((len(self.simtime), 21))
        self.qthick2AS_all = np.zeros((len(self.simtime), 21))
        self.qthick2prim_all = np.zeros((len(self.simtime), 21))
        self.qstorage2AS_all = np.zeros((len(self.simtime), 21))
        self.qstorage2prim_all = np.zeros((len(self.simtime), 21))
        self.sludge_all = np.zeros((len(self.simtime), 21))

        self.kla4 = np.zeros(self.max_transfer_per_control+1)
        self.kla4[self.max_transfer_per_control - 1] = aerationcontrolinit.kLa4_init    # for first step

        self.SO4 = np.zeros(self.max_transfer_per_control+1)
        self.SO4[self.max_transfer_per_control-1] = asm1init.yinit4[7]                    # for first step

        self.kla4_a = aerationcontrolinit.kLa4_init
        self.kla3_a = aerationcontrolinit.KLa3gain * self.kla4_a
        self.kla5_a = aerationcontrolinit.KLa5gain * self.kla4_a

        self.sludge_height = 0

        self.y_out5_r[14] = asm1init.Qintr

    def step(self, i : int):
        """
        Simulates one time step of the BSM2 model.

        Parameters
        ----------
        i : int
            Index of the current time step
        """
        # timestep = timesteps[i]
        step : float = self.simtime[i]
        stepsize : float = self.timestep[i]

        self.reactor3.kla = self.kla3_a
        self.reactor4.kla = self.kla4_a
        self.reactor5.kla = self.kla5_a

        # get influent data that is smaller than and closest to current time step
        y_in_timestep = self.y_in[np.where(self.data_time <= step)[0][-1], :]

        yp_in_c, y_in_bp = self.input_splitter.outputs(y_in_timestep, (0, 0), reginit.Qbypass)
        y_plant_bp, y_in_as_c = self.bypass_plant.outputs(y_in_bp, (1 - reginit.Qbypassplant, reginit.Qbypassplant))
        yp_in = self.combiner_primclar_pre.output(yp_in_c, self.yst_sp_p, self.yt_sp_p)
        yp_uf, yp_of = self.primclar.outputs(self.timestep[i], step, yp_in)
        y_c_as_bp = self.combiner_primclar_post.output(yp_of[:21], y_in_as_c)
        y_bp_as, y_as_bp_c_eff = self.bypass_reactor.outputs(y_c_as_bp, (1 - reginit.QbypassAS, reginit.QbypassAS))

        y_in1 = self.combiner_reactor.output(self.ys_r, y_bp_as, self.yst_sp_as, self.yt_sp_as, self.y_out5_r)
        y_out1 = self.reactor1.output(stepsize, step, y_in1)
        y_out2 = self.reactor2.output(stepsize, step, y_out1)
        y_out3 = self.reactor3.output(stepsize, step, y_out2)
        y_out4 = self.reactor4.output(stepsize, step, y_out3)
        y_out5 = self.reactor5.output(stepsize, step, y_out4)

        if (self.numberstep - 1) % (int(self.control[i] / self.timestep_integration[i])) == 0:
            # get index of noise that is smaller than and closest to current time step within a small tolerance
            idx_noise = int(np.where(self.noise_timestep - 1e-7 <= step)[0][-1])

            self.SO4[self.max_transfer_per_control] = y_out4[7]

            SO4_meas = self.SO4_sensor.measureSO(self.SO4, step, self.controlnumber, self.noise_SO4[idx_noise], self.transferfunction, self.control[i])
            kla4_ = self.aerationcontrol4.output(SO4_meas, step, self.timestep[i])
            self.kla4[self.max_transfer_per_control] = kla4_
            self.kla4_a = self.kla4_actuator.real_actuator(self.kla4, step, self.controlnumber, self.transferfunction, self.control[i])
            self.kla3_a = aerationcontrolinit.KLa3gain * self.kla4_a
            self.kla5_a = aerationcontrolinit.KLa5gain * self.kla4_a

            # for next step:
            self.SO4[0:self.max_transfer_per_control] = self.SO4[1:(self.max_transfer_per_control + 1)]
            self.kla4[0:self.max_transfer_per_control] = self.kla4[1:(self.max_transfer_per_control + 1)]

            self.controlnumber = self.controlnumber + 1


        ys_in, self.y_out5_r = self.splitter_reactor.outputs(y_out5, (y_out5[14] - asm1init.Qintr, asm1init.Qintr))

        self.ys_r, ys_was, ys_of, sludge_height = self.settler.outputs(stepsize, step, ys_in)

        y_eff = self.combiner_effluent.output(y_plant_bp, y_as_bp_c_eff, ys_of)

        yt_uf, yt_of = self.thickener.outputs(ys_was)
        self.yt_sp_p, self.yt_sp_as = self.splitter_thickener.outputs(yt_of, (1 - reginit.Qthickener2AS, reginit.Qthickener2AS))

        yd_in = self.combiner_adm1.output(yt_uf, yp_uf)
        y_out2, _, _ = self.adm1_reactor.outputs(stepsize, step, yd_in, reginit.T_op)
        ydw_s, ydw_r = self.dewatering.outputs(y_out2)
        yst_out, yst_vol = self.storage.output(stepsize, step, ydw_r, reginit.Qstorage)

        self.yst_sp_p, self.yst_sp_as = self.splitter_storage.outputs(yst_out, (1 - reginit.Qstorage2AS, reginit.Qstorage2AS))

        self.y_in_all[i] = y_in_timestep
        self.y_eff_all[i] = y_eff
        self.y_in_bp_all[i] = y_in_bp
        self.to_primary_all[i] = yp_in_c
        self.prim_in_all[i] = yp_in
        self.qpass_plant_all[i] = y_plant_bp
        self.qpassplant_to_as_all[i] = y_in_as_c
        self.qpassAS_all[i] = y_as_bp_c_eff
        self.to_as_all[i] = y_bp_as
        self.feed_settler_all[i] = ys_in
        self.qthick2AS_all[i] = self.yt_sp_as
        self.qthick2prim_all[i] = self.yt_sp_p
        self.qstorage2AS_all[i] = self.yst_sp_as
        self.qstorage2prim_all[i] = self.yst_sp_p
        self.sludge_all[i] = ydw_s


    def stabilize(self, atol : float = 1e-3):
        """
        Stabilizes the plant.
        
        Parameters
        ----------
        atol : float, optional
            Absolute tolerance for the stabilization. Default is 1e-3
        """
        stable = False
        i = 0
        s = 0  # index of the timestep to call repeatedly until stabilization
        old_check_vars = np.concatenate([self.y_eff_all[s], self.y_in_bp_all[s], self.to_primary_all[s], self.prim_in_all[s], self.qpass_plant_all[s], self.qpassplant_to_as_all[s], self.qpassAS_all[s], self.to_as_all[s], self.feed_settler_all[s], self.qthick2AS_all[s], self.qthick2prim_all[s], self.qstorage2AS_all[s], self.qstorage2prim_all[s], self.sludge_all[s]])
        while not stable:
            i += 1
            print(f"Stabilizing iteration {i}", end="\r")
            self.step(s)
            check_vars = np.concatenate([self.y_eff_all[s], self.y_in_bp_all[s], self.to_primary_all[s], self.prim_in_all[s], self.qpass_plant_all[s], self.qpassplant_to_as_all[s], self.qpassAS_all[s], self.to_as_all[s], self.feed_settler_all[s], self.qthick2AS_all[s], self.qthick2prim_all[s], self.qstorage2AS_all[s], self.qstorage2prim_all[s], self.sludge_all[s]])
            if np.isclose(check_vars, old_check_vars, atol=atol).all():
                stable = True
            old_check_vars = np.array((check_vars))
        print(f"Stabilized after {i} iterations")