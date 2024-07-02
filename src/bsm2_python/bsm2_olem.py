"""
Model file for bsm2 model with primary clarifier,
5 asm1-reactors and a second clarifier, sludge thickener,
adm1-fermenter and sludge storage in dynamic simulation without any controllers.
"""

import csv
import os

import numpy as np

import bsm2_python.bsm2.init.adm1init_bsm2 as adm1init
import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
import bsm2_python.bsm2.init.dewateringinit_bsm2 as dewateringinit
import bsm2_python.bsm2.init.plantperformanceinit_bsm2 as pp_init
import bsm2_python.bsm2.init.reginit_bsm2 as reginit
import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit
import bsm2_python.bsm2.init.storageinit_bsm2 as storageinit
import bsm2_python.bsm2.init.thickenerinit_bsm2 as thickenerinit
from bsm2_python.bsm2.adm1_bsm2 import ADM1Reactor
from bsm2_python.bsm2.asm1_bsm2 import ASM1reactor
from bsm2_python.bsm2.dewatering_bsm2 import Dewatering
from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter
from bsm2_python.bsm2.init import primclarinit_bsm2 as primclarinit
from bsm2_python.bsm2.plantperformance_new import PlantPerformance
from bsm2_python.bsm2.primclar_bsm2 import PrimaryClarifier
from bsm2_python.bsm2.settler1d_bsm2 import Settler
from bsm2_python.bsm2.storage_bsm2 import Storage
from bsm2_python.bsm2.thickener_bsm2 import Thickener
from bsm2_python.controller_em import Controller
from bsm2_python.energy_management.boiler import Boiler
from bsm2_python.energy_management.chp import CHP
from bsm2_python.energy_management.compressor import Compressor
from bsm2_python.energy_management.cooler import Cooler
from bsm2_python.energy_management.economics import Economics
from bsm2_python.energy_management.fermenter import Fermenter
from bsm2_python.energy_management.flare import Flare
from bsm2_python.energy_management.heat_net import HeatNet
from bsm2_python.energy_management.init import (
    boiler_init,
    chp_init,
    compressor_init,
    cooler_init,
    fermenter_init,
    flare_init,
    heat_net_init,
    storage_init,
)
from bsm2_python.energy_management.storage import BiogasStorage
from bsm2_python.evaluation import Evaluation
from bsm2_python.gases.gases import BIOGAS, CH4, H2O, O2
from bsm2_python.log import logger

path_name = os.path.dirname(__file__)


class BSM2OLEM:
    def __init__(
        self,
        data_in=None,
        timestep=None,
        endtime=None,
        evaltime=None,
        *,
        tempmodel=False,
        activate=False,
    ):
        """
        Creates a BSM2OL object.

        Parameters
        ----------
        data_in : np.ndarray, optional
            Influent data. Has to be a 2D array. First column is time in days, the rest are 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states)
            If not provided, the influent data from BSM2 is used
        timestep : float, optional
            Timestep for the simulation in days. If not provided, the timestep is calculated from the influent data
        endtime : float, optional
            Endtime for the simulation in days. If not provided, the endtime is the last time step in the influent data
        tempmodel : bool, optional
            If True, the temperature model dependencies are activated. Default is False
        activate : bool, optional
            If True, the dummy states are activated. Default is False
        """

        # definition of the objects:
        self.input_splitter = Splitter(sp_type=2)
        self.bypass_plant = Splitter()
        self.combiner_primclar_pre = Combiner()
        self.primclar = PrimaryClarifier(
            primclarinit.VOL_P,
            primclarinit.YINIT1,
            primclarinit.PAR_P,
            asm1init.PAR1,
            primclarinit.XVECTOR_P,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.combiner_primclar_post = Combiner()
        self.bypass_reactor = Splitter()
        self.combiner_reactor = Combiner()
        self.reactor1 = ASM1reactor(
            reginit.KLA1,
            asm1init.VOL1,
            asm1init.YINIT1,
            asm1init.PAR1,
            reginit.CARB1,
            reginit.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor2 = ASM1reactor(
            reginit.KLA2,
            asm1init.VOL2,
            asm1init.YINIT2,
            asm1init.PAR2,
            reginit.CARB2,
            reginit.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor3 = ASM1reactor(
            reginit.KLA3,
            asm1init.VOL3,
            asm1init.YINIT3,
            asm1init.PAR3,
            reginit.CARB3,
            reginit.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor4 = ASM1reactor(
            reginit.KLA4,
            asm1init.VOL4,
            asm1init.YINIT4,
            asm1init.PAR4,
            reginit.CARB4,
            reginit.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor5 = ASM1reactor(
            reginit.KLA5,
            asm1init.VOL5,
            asm1init.YINIT5,
            asm1init.PAR5,
            reginit.CARB5,
            reginit.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.splitter_reactor = Splitter()
        self.settler = Settler(
            settler1dinit.DIM,
            settler1dinit.LAYER,
            asm1init.QR,
            asm1init.QW,
            settler1dinit.settlerinit,
            settler1dinit.SETTLERPAR,
            asm1init.PAR1,
            tempmodel,
            settler1dinit.MODELTYPE,
        )
        self.combiner_effluent = Combiner()
        self.thickener = Thickener(thickenerinit.THICKENERPAR)
        self.splitter_thickener = Splitter()
        self.combiner_adm1 = Combiner()
        self.adm1_reactor = ADM1Reactor(
            adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, adm1init.DIM_D
        )
        self.dewatering = Dewatering(dewateringinit.DEWATERINGPAR)
        self.storage = Storage(storageinit.VOL_S, storageinit.ystinit, tempmodel, activate)
        self.splitter_storage = Splitter()

        if data_in is None:
            # dyninfluent from BSM2:
            with open(path_name + '/data/dyninfluent_bsm2.csv', encoding='utf-8-sig') as f:
                data_in = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)
        if timestep is None:
            # calculate difference between each time step in data_in
            self.simtime = data_in[:, 0]
            self.timestep = np.diff(data_in[:, 0], append=(2 * data_in[-1, 0] - data_in[-2, 0]))
        else:
            self.simtime = np.arange(0, data_in[-1, 0], timestep)
            self.timestep = timestep * np.ones(len(self.simtime) - 1)
        self.timestep_hour = np.dot(self.timestep, 24)

        if endtime is None:
            self.endtime = data_in[-1, 0]
        else:
            if endtime > data_in[-1, 0]:
                err = 'Endtime is larger than the last time step in data_in.\n \
                    Please provide a valid endtime.\n Endtime should be given in days.'
                raise ValueError(err)
            self.endtime = endtime
            self.simtime = self.simtime[self.simtime <= endtime]
        self.data_time = data_in[:, 0]

        if evaltime is None:
            # evaluate the last 5 days of the simulation
            starttime = self.simtime[np.argmin(np.abs(self.simtime - (self.simtime[-1] - 5)))]
            self.evaltime = np.array([starttime, self.simtime[-1]])

        self.evaluator = Evaluation(path_name + '/data/output_evaluation.csv')

        self.performance = PlantPerformance(pp_init.PP_PAR)

        klas = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])
        # scenario 5, 75th percentile, 50% reduction when S_NH below 4g/m3
        self.controller = Controller(self.simtime, 0.75, klas, 0.5, 4, BIOGAS, O2, CH4)

        self.y_in = data_in[:, 1:]

        self.yst_sp_p = np.zeros(21)
        self.yt_sp_p = np.zeros(21)
        self.ys_r = np.zeros(21)
        self.yst_sp_as = np.zeros(21)
        self.yt_sp_as = np.zeros(21)
        self.yd_in = np.zeros(21)
        self.yd_out = np.zeros(51)
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

        self.iqi_all = np.zeros(len(self.simtime))
        self.eqi_all = np.zeros(len(self.simtime))
        self.oci_all = np.zeros(len(self.simtime))
        self.oci_factors_all = np.zeros((len(self.simtime), 8))
        self.violation_all = np.zeros(len(self.simtime))

        self.y_out1_all = np.zeros((len(self.simtime), 21))
        self.y_out2_all = np.zeros((len(self.simtime), 21))
        self.y_out3_all = np.zeros((len(self.simtime), 21))
        self.y_out4_all = np.zeros((len(self.simtime), 21))
        self.y_out5_all = np.zeros((len(self.simtime), 21))
        self.ys_r_all = np.zeros((len(self.simtime), 21))
        self.ys_was_all = np.zeros((len(self.simtime), 21))
        self.ys_of_all = np.zeros((len(self.simtime), 21))
        self.yp_uf_all = np.zeros((len(self.simtime), 21))
        self.yp_of_all = np.zeros((len(self.simtime), 21))
        self.yi_out2_all = np.zeros((len(self.simtime), 21))
        self.yst_out_all = np.zeros((len(self.simtime), 21))
        self.yst_vol_all = np.zeros((len(self.simtime), 2))
        self.ydw_s_all = np.zeros((len(self.simtime), 21))
        self.yt_uf_all = np.zeros((len(self.simtime), 21))
        self.yp_internal_all = np.zeros((len(self.simtime), 21))
        self.yd_out_all = np.zeros((len(self.simtime), 51))
        self.yt_uf_all = np.zeros((len(self.simtime), 21))

        self.y_out5_r[14] = asm1init.QINTR

        self.fermenter = Fermenter(fermenter_init.CAPEX_SP, fermenter_init.OPEX_FACTOR, reginit.T_OP)

        chp1 = CHP(
            chp_init.MAX_POWER_1,
            chp_init.EFFICIENCY_RULES_1,
            chp_init.MINIMUM_LOAD_1,
            chp_init.FAILURE_RULES_1[0],
            chp_init.FAILURE_RULES_1[1],
            chp_init.CAPEX_1,
            BIOGAS,
            chp_init.STORAGE_RULES_1,
            stepless_intervals=chp_init.STEPLESS_INTERVALS_1,
        )
        chp2 = CHP(
            chp_init.MAX_POWER_2,
            chp_init.EFFICIENCY_RULES_2,
            chp_init.MINIMUM_LOAD_2,
            chp_init.FAILURE_RULES_2[0],
            chp_init.FAILURE_RULES_2[1],
            chp_init.CAPEX_2,
            BIOGAS,
            chp_init.STORAGE_RULES_2,
            stepless_intervals=chp_init.STEPLESS_INTERVALS_2,
        )
        self.chps = [chp1, chp2]

        boiler1 = Boiler(
            boiler_init.MAX_POWER_1,
            boiler_init.EFFICIENCY_RULES_1,
            boiler_init.MINIMUM_LOAD_1,
            boiler_init.CAPEX_1,
            BIOGAS,
            boiler_init.STEPLESS_INTERVALS_1,
        )
        self.boilers = [boiler1]

        self.biogas_storage = BiogasStorage(
            storage_init.MAX_VOL,
            storage_init.P_STORE,
            storage_init.VOL_INIT,
            storage_init.CAPEX_SP,
            storage_init.OPEX_FACTOR,
            BIOGAS,
            self.fermenter.get_composition(),
        )

        self.compressor = Compressor(
            BIOGAS,
            self.fermenter.p_gas,
            self.biogas_storage.p_store,
            compressor_init.EFFICIENCY,
            self.fermenter.gas_production * 2,
            self.fermenter.t_op,
            compressor_init.OPEX_FACTOR,
        )

        self.flare = Flare(flare_init.CAPEX, flare_init.MAX_GAS_UPTAKE, flare_init.FLARE_THRESHOLD)

        self.cooler = Cooler(cooler_init.CAPEX, cooler_init.MAX_HEAT)

        self.heat_net = HeatNet(
            H2O.cp_l,
            heat_net_init.TEMP_INIT,
            heat_net_init.VOL_FLOW * H2O.rho_l,
            heat_net_init.TEMP_THRESHOLDS[0],
            heat_net_init.TEMP_THRESHOLDS[1],
        )

        self.economics = Economics(
            self.chps,
            self.boilers,
            self.biogas_storage,
            self.compressor,
            self.fermenter,
            self.flare,
            self.heat_net,
            self.cooler,
        )

    def step(self, i: int, *, stabilized: bool):
        """
        Simulates one time step of the BSM2 model.

        Parameters
        ----------
        i : int
            Index of the current time step
        """
        s_nh_reactors = np.array(
            [self.reactor1.y0[9], self.reactor2.y0[9], self.reactor3.y0[9], self.reactor4.y0[9], self.reactor5.y0[9]]
        )
        klas = self.controller.get_klas(i, s_nh_reactors)

        step: float = self.simtime[i]
        stepsize: float = self.timestep[i]

        self.reactor1.kla = klas[0]
        self.reactor2.kla = klas[1]
        self.reactor3.kla = klas[2]
        self.reactor4.kla = klas[3]
        self.reactor5.kla = klas[4]

        # get influent data that is smaller than and closest to current time step
        y_in_timestep = self.y_in[np.where(self.data_time <= step)[0][-1], :]

        iqi = self.performance.qi(y_in_timestep)[0]
        self.iqi_all[i] = iqi

        yp_in_c, y_in_bp = self.input_splitter.output(y_in_timestep, (0, 0), reginit.QBYPASS)
        y_plant_bp, y_in_as_c = self.bypass_plant.output(y_in_bp, (1 - reginit.QBYPASSPLANT, reginit.QBYPASSPLANT))
        yp_in = self.combiner_primclar_pre.output(yp_in_c, self.yst_sp_p, self.yt_sp_p)
        self.yp_uf, yp_of, yp_internal = self.primclar.output(self.timestep[i], step, yp_in)
        y_c_as_bp = self.combiner_primclar_post.output(yp_of[:21], y_in_as_c)
        y_bp_as, y_as_bp_c_eff = self.bypass_reactor.output(y_c_as_bp, (1 - reginit.QBYPASSAS, reginit.QBYPASSAS))

        y_in1 = self.combiner_reactor.output(self.ys_r, y_bp_as, self.yst_sp_as, self.yt_sp_as, self.y_out5_r)
        y_out1 = self.reactor1.output(stepsize, step, y_in1)
        y_out2 = self.reactor2.output(stepsize, step, y_out1)
        y_out3 = self.reactor3.output(stepsize, step, y_out2)
        y_out4 = self.reactor4.output(stepsize, step, y_out3)
        y_out5 = self.reactor5.output(stepsize, step, y_out4)
        ys_in, self.y_out5_r = self.splitter_reactor.output(y_out5, (y_out5[14] - asm1init.QINTR, asm1init.QINTR))

        self.ys_r, ys_was, ys_of, _, _ = self.settler.output(stepsize, step, ys_in)

        y_eff = self.combiner_effluent.output(y_plant_bp, y_as_bp_c_eff, ys_of[:21])

        eqi = self.performance.qi(y_eff, eqi=True)[0]
        self.eqi_all[i] = eqi

        self.yt_uf, yt_of = self.thickener.output(ys_was)
        self.yt_sp_p, self.yt_sp_as = self.splitter_thickener.output(
            yt_of[:21], (1 - reginit.QTHICKENER2AS, reginit.QTHICKENER2AS)
        )

        self.yd_in = self.combiner_adm1.output(self.yt_uf, self.yp_uf)
        yi_out2, self.yd_out, _ = self.adm1_reactor.output(stepsize, step, self.yd_in, reginit.T_OP)
        self.ydw_s, ydw_r = self.dewatering.output(yi_out2)
        yst_out, yst_vol = self.storage.output(stepsize, step, ydw_r, reginit.QSTORAGE)

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
        flows = np.array([asm1init.QINTR, asm1init.QR, asm1init.QW, self.yp_uf[14], self.yt_uf[14], self.ydw_s[14]])
        pe = self.performance.pumpingenergy_step(flows, pp_init.PP_PAR[10:16])
        me = self.performance.mixingenergy_step(kla, vol, pp_init.PP_PAR[16])

        ydw_s_tss_flow = self.performance.tss_flow(self.ydw_s)
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

        self.y_out1_all[i] = y_out1
        self.y_out2_all[i] = y_out2
        self.y_out3_all[i] = y_out3
        self.y_out4_all[i] = y_out4
        self.y_out5_all[i] = y_out5
        self.ys_r_all[i] = self.ys_r
        self.ys_was_all[i] = ys_was
        self.ys_of_all[i] = ys_of
        self.yp_uf_all[i] = self.yp_uf
        self.yp_of_all[i] = yp_of
        self.yt_uf_all[i] = self.yt_uf
        self.yd_out_all[i] = self.yd_out
        self.yi_out2_all[i] = yi_out2
        self.yst_out_all[i] = yst_out
        self.yst_vol_all[i] = yst_vol, step
        self.ydw_s_all[i] = self.ydw_s
        self.yp_internal_all[i] = yp_internal

        # Energy Management
        if stabilized:
            gas_production, gas_parameters = self.get_gas_production()
            electricity_demand = ae + pe + me
            # aeration efficiency in standard conditions in process water (sae),
            # 25 kgO2/kWh, src: T. Frey, Invent Umwelt- und Verfahrenstechnik AG
            # alpha_sae = 2.5
            # oxygen_demand = ae * alpha_sae / O2.rho_norm  # kW * kgO2/kWh / kg/Nm3 = Nm3/h

            self.fermenter.step(gas_production, gas_parameters, heat_demand, electricity_demand)
            biogas = self.biogas_storage.update_inflow(
                self.fermenter.gas_production, self.fermenter.get_composition(), self.timestep_hour[i]
            )
            self.controller.biogas = biogas
            for chp in self.chps:
                chp.biogas = biogas
            for boiler in self.boilers:
                boiler.biogas = biogas

            self.controller.control_gas_management(
                self.timestep_hour[i],
                self.chps,
                self.boilers,
                self.biogas_storage,
                self.cooler,
                self.flare,
                self.heat_net,
                self.fermenter,
            )

            [chp.step(self.timestep_hour[i]) for chp in self.chps]
            [boiler.step(self.timestep_hour[i]) for boiler in self.boilers]
            self.flare.step(self.timestep_hour[i])
            self.cooler.step(self.timestep_hour[i])
            self.compressor.step(self.timestep_hour[i])

            self.heat_net.update_temperature(
                np.sum([boiler.products[boiler_init.HEAT] * self.timestep_hour[i] for boiler in self.boilers])
                + np.sum([chp.products[chp_init.HEAT] * self.timestep_hour[i] for chp in self.chps])
                - self.fermenter.heat_demand * self.timestep_hour[i]
                - self.cooler.consumption[cooler_init.HEAT] * self.timestep_hour[i]
            )

            biogas_net_outflow = (
                np.sum([chp.consumption[chp_init.BIOGAS] for chp in self.chps])
                + np.sum([boiler.consumption[boiler_init.BIOGAS] for boiler in self.boilers])
                + self.flare.consumption[flare_init.BIOGAS]
            )

            self.biogas_storage.update_outflow(biogas_net_outflow, self.timestep_hour[i])

            net_electricity = self.fermenter.electricity_demand - np.sum(
                [chp.products[chp_init.ELECTRICITY] for chp in self.chps]
            )

            self.economics.get_income(net_electricity, i, self.timestep_hour[i])
            self.economics.get_expenditures(net_electricity, i, self.timestep_hour[i])

            s_nh_data: tuple[list, list, list, float] = ([], [], [], float(self.simtime[i]))
            for j, s_nh in enumerate(s_nh_reactors):
                s_nh_data[0].append('s_nh' + str(j + 1))
                s_nh_data[1].append('g/m3')
                s_nh_data[2].append(s_nh)
            kla_data: tuple[list, list, list, float] = ([], [], [], float(self.simtime[i]))
            for j, kla in enumerate(klas):
                kla_data[0].append('kla' + str(j + 1))
                kla_data[1].append('1/d')
                kla_data[2].append(kla)
            elec_data = (
                ['demand', 'price'],
                ['kW', '€/MWh'],
                [self.fermenter.electricity_demand, self.controller.electricity_prices[i]],
                float(self.simtime[i]),
            )
            self.evaluator.update_data(data1=s_nh_data, data2=kla_data, data3=elec_data)

    def stabilize(self, atol: float = 1e-3):
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
        old_check_vars = np.concatenate(
            [
                self.y_eff_all[s],
                self.y_in_bp_all[s],
                self.to_primary_all[s],
                self.prim_in_all[s],
                self.qpass_plant_all[s],
                self.qpassplant_to_as_all[s],
                self.qpassAS_all[s],
                self.to_as_all[s],
                self.feed_settler_all[s],
                self.qthick2AS_all[s],
                self.qthick2prim_all[s],
                self.qstorage2AS_all[s],
                self.qstorage2prim_all[s],
                self.sludge_all[s],
            ]
        )
        while not stable:
            i += 1
            logger.debug('Stabilizing iteration %s', i)
            self.step(s, stabilized=stable)
            check_vars = np.concatenate(
                [
                    self.y_eff_all[s],
                    self.y_in_bp_all[s],
                    self.to_primary_all[s],
                    self.prim_in_all[s],
                    self.qpass_plant_all[s],
                    self.qpassplant_to_as_all[s],
                    self.qpassAS_all[s],
                    self.to_as_all[s],
                    self.feed_settler_all[s],
                    self.qthick2AS_all[s],
                    self.qthick2prim_all[s],
                    self.qstorage2AS_all[s],
                    self.qstorage2prim_all[s],
                    self.sludge_all[s],
                ]
            )
            if np.isclose(check_vars, old_check_vars, atol=atol).all():
                stable = True
            old_check_vars = np.array(check_vars)
        logger.info('Stabilized after %s iterations\n', i)

    def simulate(self):
        """
        Simulates the plant.
        """
        for i in range(len(self.simtime)):
            self.step(i, stabilized=True)

            if i % 1000 == 0:
                logger.info('timestep: %s of %s\n', i, len(self.simtime))

            if self.evaltime[0] <= self.simtime[i] <= self.evaltime[1]:
                self.evaluator.update_data(
                    data1=(['iqi'], [''], [self.iqi_all[i]], float(self.simtime[i])),
                    data2=(['eqi'], [''], [self.eqi_all[i]], float(self.simtime[i])),
                    data3=(['oci'], [''], [self.oci_all[i]], float(self.simtime[i])),
                )

        oci_final = self.performance.oci(
            np.mean(self.oci_factors_all[:, 0]),
            np.mean(self.oci_factors_all[:, 1]),
            np.mean(self.oci_factors_all[:, 2]),
            np.mean(self.oci_factors_all[:, 3]),
            np.mean(self.oci_factors_all[:, 4]),
            np.mean(self.oci_factors_all[:, 5]),
            np.mean(self.oci_factors_all[:, 6]),
            np.mean(self.oci_factors_all[:, 7]),
        )
        self.evaluator.update_data(
            data1=(['oci_final'], [''], [oci_final], float(self.endtime)),
        )

        self.finish_evaluation()

    def get_gas_production(self):
        """
        Returns the gas production of the plant.

        Returns
        -------
        float
            Gas production of the plant
        """
        gas_production = self.yd_out[-1] / 24  # Nm3/d -> Nm3/h
        gas_parameters = self.yd_out[-5:]  # [p_H2 [bar], p_CH4 [bar], p_CO2 [bar], P_gas [bar], q_gas [Nm3/d]]

        return gas_production, gas_parameters

    def finish_evaluation(self):
        """
        Finishes the evaluation of the plant.
        """
        self.evaluator.plot_data()

        self.evaluator.export_data()
