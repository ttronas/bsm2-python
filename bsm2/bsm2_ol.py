"""
Model file for bsm2 model with primary clarifier,
5 asm1-reactors and a second clarifier, sludge thickener,
adm1-fermenter and sludge storage in steady state simulation

This file holds the plant in an open loop simulation (no control) with dynamic input data.
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

class BSM2_OL:
    def __init__(self, data_in=None, tempmodel=False, activate=False, timestep=None, endtime=None):
        """
        Creates a BSM2_OL object.

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

        if data_in is None:
            # dyninfluent from BSM2:
            with open(path_name + '/../data/dyninfluent_bsm2.csv', 'r', encoding='utf-8-sig') as f:
                data_in = np.array(list(csv.reader(f, delimiter=","))).astype(np.float64)

        if timestep is None:
            # calculate difference between each time step in data_in
            self.simtime = data_in[:, 0]
            self.timestep = np.diff(data_in[:, 0], append=(2*data_in[-1, 0] - data_in[-2, 0]))
        else:
            self.simtime = np.arange(0, data_in[-1, 0], timestep)
            self.timestep = timestep * np.ones(len(self.simtime) - 1)

        if endtime is None:
            self.endtime = data_in[-1, 0]
        else:
            if endtime > data_in[-1, 0]:
                raise ValueError("Endtime is larger than the last time step in data_in.\n Please provide a valid endtime.\n Endtime should be given in days.")
            self.endtime = endtime
            self.simtime = self.simtime[self.simtime <= endtime]
    
        self.data_time = data_in[:, 0]
        # self.simtime = np.arange(0, self.endtime, self.timestep)

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

        self.sludge_height = 0

        self.y_out5_r[14] = asm1init.Qintr

    def step(self, i : int, klas : np.ndarray = np.array((reginit.KLa1, reginit.KLa2, reginit.KLa3, reginit.KLa4, reginit.KLa5))):
        """
        Simulates one time step of the BSM2 model.

        Parameters
        ----------
        i : int
            Index of the current time step
        klas : np.ndarray, optional
            Array with the values of the oxygen transfer coefficients for the 5 ASM1 reactors. Default is (reginit.KLa1, reginit.KLa2, reginit.KLa3, reginit.KLa4, reginit.KLa5)
        """
        # timestep = timesteps[i]
        step : float = self.simtime[i]
        stepsize : float = self.timestep[i]

        self.reactor1.kla = klas[0]
        self.reactor2.kla = klas[1]
        self.reactor3.kla = klas[2]
        self.reactor4.kla = klas[3]
        self.reactor5.kla = klas[4]

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
        ys_in, self.y_out5_r = self.splitter_reactor.outputs(y_out5, (y_out5[14] - asm1init.Qintr, asm1init.Qintr))

        self.ys_r, ys_was, ys_of, sludge_height = self.settler.outputs(stepsize, step, ys_in)

        y_eff = self.combiner_effluent.output(y_plant_bp, y_as_bp_c_eff, ys_of[:21])

        yt_uf, yt_of = self.thickener.outputs(ys_was)
        self.yt_sp_p, self.yt_sp_as = self.splitter_thickener.outputs(yt_of[:21], (1 - reginit.Qthickener2AS, reginit.Qthickener2AS))

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