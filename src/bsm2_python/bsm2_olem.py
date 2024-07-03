import numpy as np

import bsm2_python.bsm2.init.reginit_bsm2 as reginit
from bsm2_python.bsm2_base import BSM2Base
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
from bsm2_python.gases.gases import BIOGAS, CH4, H2O, O2
from bsm2_python.log import logger


class BSM2OLEM(BSM2Base):
    def __init__(self, data_in=None, timestep=None, endtime=None, evaltime=None, *, tempmodel=False, activate=False):
        """
        Creates a BSM2OLEM object.

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

        super().__init__(
            data_in=data_in,
            timestep=timestep,
            endtime=endtime,
            evaltime=evaltime,
            tempmodel=tempmodel,
            activate=activate,
        )

        self.timestep_hour = np.dot(self.timestep, 24)

        # scenario 5, 75th percentile, 50% reduction when S_NH below 4g/m3
        self.controller = Controller(self.simtime, 0.75, self.klas, 0.5, 4, BIOGAS, O2, CH4)

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

    def step(self, i: int, *, stabilized: bool = False):
        s_nh_reactors = np.array(
            [self.reactor1.y0[9], self.reactor2.y0[9], self.reactor3.y0[9], self.reactor4.y0[9], self.reactor5.y0[9]]
        )
        self.klas = self.controller.get_klas(i, s_nh_reactors)

        super().step(i)

        # Energy Management
        if stabilized:
            gas_production, gas_parameters = self.get_gas_production()
            electricity_demand = self.ae + self.pe + self.me
            # aeration efficiency in standard conditions in process water (sae),
            # 25 kgO2/kWh, src: T. Frey, Invent Umwelt- und Verfahrenstechnik AG
            # alpha_sae = 2.5
            # oxygen_demand = ae * alpha_sae / O2.rho_norm  # kW * kgO2/kWh / kg/Nm3 = Nm3/h

            self.fermenter.step(gas_production, gas_parameters, self.heat_demand, electricity_demand)
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
            if self.klas is not None:
                kla_data: tuple[list, list, list, float] = ([], [], [], float(self.simtime[i]))
                for j, kla in enumerate(self.klas):
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

    def simulate(self):
        """
        Simulates the plant.
        """
        self.stabilize()
        for i in range(len(self.simtime)):
            self.step(i, stabilized=True)

            if i % 1000 == 0:
                logger.info('timestep: %s of %s\n', i, len(self.simtime) - 1)

            if self.evaltime[0] <= self.simtime[i] <= self.evaltime[1]:
                self.evaluator.update_data(
                    data1=(['iqi'], [''], [self.iqi_all[i]], float(self.simtime[i])),
                    data2=(['eqi'], [''], [self.eqi_all[i]], float(self.simtime[i])),
                    data3=(['oci'], [''], [self.oci_all[i]], float(self.simtime[i])),
                )

        self.oci_final = self.get_final_performance()[-1]
        self.evaluator.update_data(
            data1=(['oci_final'], [''], [self.oci_final], float(self.endtime)),
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
