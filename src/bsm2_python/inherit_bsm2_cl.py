import csv
import os

import numpy as np

import bsm2_python.bsm2.init.plantperformanceinit_bsm2 as pp_init
import bsm2_python.bsm2.init.reginit_bsm2 as reginit
from bsm2_python.bsm2 import aerationcontrol
from bsm2_python.bsm2.init import aerationcontrolinit
from bsm2_python.bsm2.init import asm1init_bsm2 as asm1init
from bsm2_python.bsm2_base import BSM2BASE

path_name = os.path.dirname(__file__)


class BSM2CL(BSM2BASE):
    def __init__(
        self, endtime, timestep=None, use_noise=1, noise_file=None, noise_seed=1, *, tempmodel=False, activate=False
    ):
        super().__init__(endtime=endtime, tempmodel=tempmodel, activate=activate)

        self.so4_sensor = aerationcontrol.OxygenSensor(
            aerationcontrolinit.MIN_SO4,
            aerationcontrolinit.MAX_SO4,
            aerationcontrolinit.T_SO4,
            aerationcontrolinit.STD_SO4,
        )
        self.aerationcontrol4 = aerationcontrol.PIAeration(
            aerationcontrolinit.KLA4_MIN,
            aerationcontrolinit.KLA4_MAX,
            aerationcontrolinit.KSO4,
            aerationcontrolinit.TISO4,
            aerationcontrolinit.TTSO4,
            aerationcontrolinit.SO4REF,
            aerationcontrolinit.KLA4OFFSET,
            aerationcontrolinit.SO4INTSTATE,
            aerationcontrolinit.SO4AWSTATE,
            aerationcontrolinit.KLA4_LIM,
            aerationcontrolinit.KLA4_CALC,
            use_antiwindup=aerationcontrolinit.USEANTIWINDUPSO4,
        )

        self.kla4_actuator = aerationcontrol.KLaActuator(aerationcontrolinit.T_KLA4)

        if use_noise == 0:
            self.noise_so4 = np.zeros(2)
            self.noise_timestep = np.array((0, self.endtime))
        elif use_noise == 1:
            if noise_file is None:
                noise_file = path_name + '/data/sensornoise.csv'
            with open(noise_file, encoding='utf-8-sig') as f:
                noise_data = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)
            if noise_data[-1, 0] < self.endtime:
                err = 'Noise file does not cover the whole simulation time.\n \
                    Please provide a valid noise file.'
                raise ValueError(err)
            noise_shape_criteria = 2
            if noise_data.shape[1] < noise_shape_criteria:
                err = 'Noise file needs to have at least 2 columns: time and noise data'
                raise ValueError(err)
            self.noise_so4 = noise_data[:, 1]
            self.noise_timestep = noise_data[:, 0]
            del noise_data

        if timestep is None:
            # calculate difference between each time step in data_in
            self.simtime = self.noise_timestep
            self.timestep = np.diff(
                self.noise_timestep, append=(2 * self.noise_timestep[-1,] - self.noise_timestep[-2,])
            )
        else:
            self.simtime = np.arange(0, self.data_in[-1, 0], timestep)
            self.timestep = timestep * np.ones(len(self.simtime))

        self.simtime = self.simtime[self.simtime <= self.endtime]

        rng_mode = 2
        if use_noise in {0, 1}:
            pass
        elif use_noise == rng_mode:
            np.random.seed(noise_seed)
            # create random noise array with mean 0 and variance 1
            self.noise_so4 = np.random.normal(0, 1, len(self.simtime))
            self.noise_timestep = np.arange(0, self.endtime, self.timestep)
        else:
            err = 'use_noise has to be 0, 1 or 2'
            raise ValueError(err)

        self.data_time = self.data_in[:, 0]
        # self.simtime = np.arange(0, self.endtime, self.timestep)

        self.timestep_integration = np.round(self.timestep * 24 * 60)  # step of integration in min
        self.control = np.round(
            self.timestep * 24 * 60
        )  # step of aeration self.control in min, should be equal or bigger than timestep_integration
        self.transferfunction = 15  # interval for transferfunction in min
        self.max_transfer_per_control = int(np.max(self.transferfunction / self.control, axis=0))

        self.numberstep = 1
        self.controlnumber = 1

        self.kla4 = np.zeros(self.max_transfer_per_control + 1)
        self.kla4[self.max_transfer_per_control - 1] = aerationcontrolinit.KLA4_INIT  # for first step

        self.so4 = np.zeros(self.max_transfer_per_control + 1)
        self.so4[self.max_transfer_per_control - 1] = asm1init.YINIT4[7]  # for first step

        self.kla4_a = aerationcontrolinit.KLA4_INIT
        self.kla3_a = aerationcontrolinit.KLA3GAIN * self.kla4_a
        self.kla5_a = aerationcontrolinit.KLA5GAIN * self.kla4_a

        # TODO all dependant on self.simtime, changes in bsm2_cl from original value -> need to be re-initialized
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
        self.iqi_all = np.zeros(len(self.simtime))
        self.eqi_all = np.zeros(len(self.simtime))
        self.oci_all = np.zeros(len(self.simtime))
        self.oci_factors_all = np.zeros((len(self.simtime), 8))
        self.violation_all = np.zeros(len(self.simtime))

    # TODO doesn't really combine well with bsm2_ol structure, has different parts inside
    # other methods work well

    # def step(
    #     self,
    #     i: int,
    #     klas: np.ndarray | None = None,
    # ):
    #     step: float = self.simtime[i]
    #
    #     klas = np.array([0, 0, self.kla3_a, self.kla4_a, self.kla5_a])
    #
    #     if (self.numberstep - 1) % (int(self.control[i] / self.timestep_integration[i])) == 0:
    #         # get index of noise that is smaller than and closest to current time step within a small tolerance
    #         idx_noise = int(np.where(self.noise_timestep - 1e-7 <= step)[0][-1])
    #
    #         self.so4[self.max_transfer_per_control] = y_out4[7]
    #
    #         so4_meas = self.so4_sensor.measure_so(
    #             self.so4, step, self.controlnumber, self.noise_so4[idx_noise], self.transferfunction, self.control[i]
    #         )
    #         kla4_ = self.aerationcontrol4.output(so4_meas, step, self.timestep[i])
    #         self.kla4[self.max_transfer_per_control] = kla4_
    #         self.kla4_a = self.kla4_actuator.real_actuator(
    #             self.kla4, step, self.controlnumber, self.transferfunction, self.control[i]
    #         )
    #         self.kla3_a = aerationcontrolinit.KLA3GAIN * self.kla4_a
    #         self.kla5_a = aerationcontrolinit.KLA5GAIN * self.kla4_a
    #
    #         # for next step:
    #         self.so4[0 : self.max_transfer_per_control] = self.so4[1 : (self.max_transfer_per_control + 1)]
    #         self.kla4[0 : self.max_transfer_per_control] = self.kla4[1 : (self.max_transfer_per_control + 1)]
    #
    #         self.controlnumber += 1
    #
    #     super().step(i, klas)

    def step(
        self,
        i: int,
        klas: np.ndarray | None = None,
    ):
        """
        Simulates one time step of the BSM2 model.

        Parameters
        ----------
        i : int
            Index of the current time step
        """
        # timestep = timesteps[i]
        step: float = self.simtime[i]
        stepsize: float = self.timestep[i]

        self.reactor3.kla = self.kla3_a
        self.reactor4.kla = self.kla4_a
        self.reactor5.kla = self.kla5_a

        # get influent data that is smaller than and closest to current time step
        y_in_timestep = self.y_in[np.where(self.data_time <= step)[0][-1], :]

        iqi = self.performance.qi(y_in_timestep)[0]
        self.iqi_all[i] = iqi

        yp_in_c, y_in_bp = self.input_splitter.output(y_in_timestep, (0, 0), reginit.QBYPASS)
        y_plant_bp, y_in_as_c = self.bypass_plant.output(y_in_bp, (1 - reginit.QBYPASSPLANT, reginit.QBYPASSPLANT))
        yp_in = self.combiner_primclar_pre.output(yp_in_c, self.yst_sp_p, self.yt_sp_p)
        yp_uf, yp_of, _ = self.primclar.output(self.timestep[i], step, yp_in)
        y_c_as_bp = self.combiner_primclar_post.output(yp_of[:21], y_in_as_c)
        y_bp_as, y_as_bp_c_eff = self.bypass_reactor.output(y_c_as_bp, (1 - reginit.QBYPASSAS, reginit.QBYPASSAS))

        y_in1 = self.combiner_reactor.output(self.ys_r, y_bp_as, self.yst_sp_as, self.yt_sp_as, self.y_out5_r)
        y_out1 = self.reactor1.output(stepsize, step, y_in1)
        y_out2 = self.reactor2.output(stepsize, step, y_out1)
        y_out3 = self.reactor3.output(stepsize, step, y_out2)
        y_out4 = self.reactor4.output(stepsize, step, y_out3)
        y_out5 = self.reactor5.output(stepsize, step, y_out4)

        if (self.numberstep - 1) % (int(self.control[i] / self.timestep_integration[i])) == 0:
            # get index of noise that is smaller than and closest to current time step within a small tolerance
            idx_noise = int(np.where(self.noise_timestep - 1e-7 <= step)[0][-1])

            self.so4[self.max_transfer_per_control] = y_out4[7]

            so4_meas = self.so4_sensor.measure_so(
                self.so4, step, self.controlnumber, self.noise_so4[idx_noise], self.transferfunction, self.control[i]
            )
            kla4_ = self.aerationcontrol4.output(so4_meas, step, self.timestep[i])
            self.kla4[self.max_transfer_per_control] = kla4_
            self.kla4_a = self.kla4_actuator.real_actuator(
                self.kla4, step, self.controlnumber, self.transferfunction, self.control[i]
            )
            self.kla3_a = aerationcontrolinit.KLA3GAIN * self.kla4_a
            self.kla5_a = aerationcontrolinit.KLA5GAIN * self.kla4_a

            # for next step:
            self.so4[0 : self.max_transfer_per_control] = self.so4[1 : (self.max_transfer_per_control + 1)]
            self.kla4[0 : self.max_transfer_per_control] = self.kla4[1 : (self.max_transfer_per_control + 1)]

            self.controlnumber += 1

        ys_in, self.y_out5_r = self.splitter_reactor.output(y_out5, (y_out5[14] - asm1init.QINTR, asm1init.QINTR))

        self.ys_r, ys_was, ys_of, _, _ = self.settler.output(stepsize, step, ys_in)

        y_eff = self.combiner_effluent.output(y_plant_bp, y_as_bp_c_eff, ys_of)

        eqi = self.performance.qi(y_eff, eqi=True)[0]
        self.eqi_all[i] = eqi

        yt_uf, yt_of = self.thickener.output(ys_was)
        self.yt_sp_p, self.yt_sp_as = self.splitter_thickener.output(
            yt_of, (1 - reginit.QTHICKENER2AS, reginit.QTHICKENER2AS)
        )

        self.yd_in = self.combiner_adm1.output(yt_uf, yp_uf)
        y_out2, self.yd_out, _ = self.adm1_reactor.output(stepsize, step, self.yd_in, reginit.T_OP)
        ydw_s, ydw_r = self.dewatering.output(y_out2)
        yst_out, _ = self.storage.output(stepsize, step, ydw_r, reginit.QSTORAGE)

        self.yst_sp_p, self.yst_sp_as = self.splitter_storage.output(
            yst_out, (1 - reginit.QSTORAGE2AS, reginit.QSTORAGE2AS)
        )

        kla = np.array([self.reactor1.kla, self.reactor2.kla, self.reactor3.kla, self.reactor4.kla, self.reactor5.kla])
        vol = np.array(
            [
                self.reactor1.volume,
                self.reactor2.volume,
                self.reactor3.volume,
                self.reactor4.volume,
                self.reactor5.volume,
                self.adm1_reactor.volume_liq,
            ]
        )
        sosat = np.array([asm1init.SOSAT1, asm1init.SOSAT2, asm1init.SOSAT3, asm1init.SOSAT4, asm1init.SOSAT5])
        ae = self.performance.aerationenergy_step(kla, vol[0:5], sosat)
        flows = np.array([asm1init.QINTR, asm1init.QR, asm1init.QW, yp_uf[14], yt_uf[14], ydw_s[14]])
        pe = self.performance.pumpingenergy_step(flows, pp_init.PP_PAR[10:16])
        me = self.performance.mixingenergy_step(kla, vol, pp_init.PP_PAR[16])

        ydw_s_tss_flow = self.performance.tss_flow(ydw_s)
        carb = reginit.CARB1 + reginit.CARB2 + reginit.CARB3 + reginit.CARB4 + reginit.CARB5
        added_carbon_mass = self.performance.added_carbon_mass(carb, reginit.CARBONSOURCECONC)
        heat_demand = self.performance.heat_demand_step(self.yd_in, reginit.T_OP)[0]
        ch4_prod, _, _, _ = self.performance.gas_production(self.yd_out, reginit.T_OP)
        self.oci_all[i] = self.performance.oci(
            pe * 24, ae * 24, me * 24, 0, ydw_s_tss_flow, added_carbon_mass, heat_demand * 24, ch4_prod
        )
        self.oci_factors_all[i] = [
            pe * 24,
            ae * 24,
            me * 24,
            0,
            ydw_s_tss_flow,
            added_carbon_mass,
            heat_demand * 24,
            ch4_prod,
        ]

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
