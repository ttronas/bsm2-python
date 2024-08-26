import math

import numpy as np
from tqdm import tqdm

import bsm2_python.bsm2.init.reginit_bsm2 as reginit
from bsm2_python.bsm2_base import BSM2Base
from bsm2_python.controller_em import ControllerEM
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

SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = np.arange(21)


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
        self.perf_factors_all = np.zeros((len(self.simtime), 14))

        self.timestep_hour = np.dot(self.timestep, 24)

        # scenario 5, 75th percentile, 50% reduction when S_NH below 4g/m3
        self.controller = ControllerEM(0.75, self.klas, 0.5, 4, BIOGAS, O2, CH4)

        self.fermenter = Fermenter(fermenter_init.CAPEX_SP, fermenter_init.OPEX_FACTOR, reginit.T_OP)

        chp1 = CHP(
            chp_init.MAX_POWER_1,
            chp_init.EFFICIENCY_RULES_1,
            chp_init.MINIMUM_LOAD_1,
            chp_init.FAILURE_RULES_1[0],
            chp_init.FAILURE_RULES_1[1],
            chp_init.LOAD_CHANGE_TIME_1,
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
            chp_init.LOAD_CHANGE_TIME_2,
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
            boiler_init.LOAD_CHANGE_TIME_1,
            boiler_init.CAPEX_1,
            BIOGAS,
            stepless_intervals=boiler_init.STEPLESS_INTERVALS_1,
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
        self.contr_prices_all = np.zeros((len(self.simtime), 1))
        self.prices_all = np.zeros((len(self.simtime), 1))
        self.income_all = np.zeros((len(self.simtime), 1))
        self.klas_all = np.zeros((len(self.simtime), len(self.klas)))
        self.chps_electricity_all = np.zeros((len(self.simtime), len(self.chps)))
        self.chps_heat_all = np.zeros((len(self.simtime), len(self.chps)))
        self.boilers_heat_all = np.zeros((len(self.simtime), len(self.boilers)))
        self.flare_gas_all = np.zeros((len(self.simtime), 1))
        self.cooler_cool_all = np.zeros((len(self.simtime), 1))
        self.biogas_vol_all = np.zeros((len(self.simtime), 1))
        self.heat_net_temp_all = np.zeros((len(self.simtime), 1))

    def step(self, i: int, *, stabilized: bool = False):
        self.klas = self.controller.get_klas(self.simtime[i], self.y_eff[SNH])

        super().step(i)

        # Energy Management
        if stabilized:
            gas_production, gas_parameters = self.get_gas_production()
            electricity_demand = self.ae + self.pe + self.me
            # aeration efficiency in standard conditions in process water (sae),
            # 25 kgO2/kWh, src: T. Frey, Invent Umwelt- und Verfahrenstechnik AG
            # alpha_sae = 2.5
            # oxygen_demand = ae * alpha_sae / O2.rho_norm  # kW * kgO2/kWh / kg/Nm3 = Nm3/h

            self.fermenter.step(gas_production, gas_parameters, self.heat_demand)
            biogas = self.biogas_storage.update_inflow(
                self.fermenter.gas_production, self.fermenter.get_composition(), self.timestep_hour[i]
            )
            self.controller.biogas = biogas
            for chp in self.chps:
                chp.biogas = biogas
            for boiler in self.boilers:
                boiler.biogas = biogas
            self.compressor.load = self.compressor.calculate_load(self.fermenter.gas_production)

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

            # TODO: Lukas, the heat net is encountering serious trouble at some point during the simulation
            # The temperature is falling to -20 °C. Please fix this - perhaps we have to rescale some component?
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

            self.prices_all[i] = self.controller.electricity_prices[
                np.where(self.controller.price_times <= self.simtime[i])[0][-1]
            ]
            self.klas_all[i] = self.klas
            self.chps_electricity_all[i] = [chp.products[chp_init.ELECTRICITY] for chp in self.chps]
            self.chps_heat_all[i] = [chp.products[chp_init.HEAT] for chp in self.chps]
            self.boilers_heat_all[i] = [boiler.products[boiler_init.HEAT] for boiler in self.boilers]
            self.flare_gas_all[i] = self.flare.consumption[flare_init.BIOGAS]
            self.cooler_cool_all[i] = self.cooler.consumption[cooler_init.HEAT]
            self.biogas_vol_all[i] = self.biogas_storage.vol
            self.heat_net_temp_all[i] = self.heat_net.temperature

            chp_production = np.sum([chp.products[chp_init.ELECTRICITY] for chp in self.chps])
            heat_production = np.sum([chp.products[chp_init.HEAT] for chp in self.chps]) + np.sum(
                [boiler.products[boiler_init.HEAT] for boiler in self.boilers]
            )

            net_electricity = electricity_demand - chp_production

            el_price_idx = np.argmin(np.abs(self.controller.price_times - self.simtime[i]))
            self.income_all[i] = self.economics.get_income(net_electricity, self.simtime, i)
            self.economics.get_expenditures(net_electricity, self.simtime, i)

            if i == 0:
                self.evaluator.add_new_data('s_nh', ['s_nh_eff'], ['g/m3'])
                self.evaluator.add_new_data('kla', ['kla1', 'kla2', 'kla3', 'kla4', 'kla5'], ['1/d'])
                self.evaluator.add_new_data('electricity', ['demand', 'price'], ['kW', '€/MWh'])
            self.evaluator.update_data('s_nh', self.y_eff[SNH], self.simtime[i])
            self.evaluator.update_data('kla', self.klas, self.simtime[i])
            self.evaluator.update_data(
                'electricity', [electricity_demand, self.controller.electricity_prices[el_price_idx]], self.simtime[i]
            )

            tss_mass = self.performance.tss_mass_bsm2(
                self.yp_of,
                self.yp_uf,
                self.yp_internal,
                self.y_out1,
                self.y_out2,
                self.y_out3,
                self.y_out4,
                self.y_out5,
                self.ys_tss_internal,
                self.yd_out,
                self.yst_out,
                self.yst_vol,
            )
            ydw_s_tss_flow = self.performance.tss_flow(self.ydw_s)
            y_eff_tss_flow = self.performance.tss_flow(self.y_eff)
            carb = reginit.CARB1 + reginit.CARB2 + reginit.CARB3 + reginit.CARB4 + reginit.CARB5
            added_carbon_mass = self.performance.added_carbon_mass(carb, reginit.CARBONSOURCECONC)
            self.heat_demand = self.performance.heat_demand_step(self.yd_in, reginit.T_OP)[0]
            ch4_prod, h2_prod, co2_prod, q_gas = self.performance.gas_production(self.yd_out, reginit.T_OP)
            # This calculates an approximate oci value for each time step,
            # neglecting changes in the tss mass inside the whole plant
            self.oci_all[i] = self.oci_dynamic(
                self.pe * 24,
                self.ae * 24,
                self.me * 24,
                chp_production * 24,
                ydw_s_tss_flow,
                added_carbon_mass,
                self.heat_demand * 24,
                heat_production * 24,
                simtime=self.simtime[i],
            )
            # These values are used to calculate the exact performance values at the end of the simulation
            self.perf_factors_all[i] = [
                self.pe * 24,
                self.ae * 24,
                self.me * 24,
                chp_production * 24,
                ydw_s_tss_flow,
                y_eff_tss_flow,
                tss_mass,
                added_carbon_mass,
                self.heat_demand * 24,
                heat_production * 24,
                ch4_prod,
                h2_prod,
                co2_prod,
                q_gas,
            ]

    def simulate(self):
        """
        Simulates the plant.
        """
        self.stabilize()
        self.evaluator.add_new_data('oci', ['oci'], [''])
        self.evaluator.add_new_data('oci_final', ['oci_final'], [''])
        self.evaluator.add_new_data('iqi', ['iqi'], [''])
        self.evaluator.add_new_data('eqi', ['eqi'], [''])
        for i, _ in enumerate(tqdm(self.simtime)):
            self.step(i, stabilized=True)

            if self.evaltime[0] <= self.simtime[i] <= self.evaltime[1]:
                self.evaluator.update_data('oci', [self.oci_all[i]], self.simtime[i])
                self.evaluator.update_data('iqi', [self.iqi_all[i]], self.simtime[i])
                self.evaluator.update_data('eqi', [self.eqi_all[i]], self.simtime[i])

        self.oci_final = self.get_final_performance()[-1]
        self.evaluator.update_data('oci_final', [self.oci_final], self.evaltime[1])

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

    @staticmethod
    def oci(pe, ae, me, eg, tss, cm, hd, hp):
        """
        Calculates the operational cost index of the plant.

        Parameters
        ----------
        pe : float
            The pumping energy of the plant / kWh/d
        ae : float
            The aeration energy of the plant / kWh/d
        me : float
            The mixing energy of the plant / kWh/d
        eg : float
            The electricity generation of the plant / kWh/d
        tss : float
            The total suspended solids production of the plant / kg/d
        cm : float
            The added carbon mass of the plant / kg/d
        hd : float
            The heating demand of the sludge / kWh/d
        hp : float
            The heat production of the plant / kWh/d

        Returns
        -------
        float
            The operational cost index of the plant
        """
        tss_cost = 3 * tss
        ae_cost = ae
        me_cost = me
        pe_cost = pe
        eg_income = eg
        cm_cost = 3 * cm
        hd_cost = hd
        hp_income = hp
        return tss_cost + ae_cost + me_cost + pe_cost - eg_income + cm_cost + np.maximum(0, hd_cost - hp_income)

    def oci_dynamic(self, pe, ae, me, eg, tss, cm, hd, hp, simtime):
        """
        Calculates the operational cost index of the plant while considering the dynamic electricity prices.

        Parameters
        ----------
        pe : float
            The pumping energy of the plant / kWh/d
        ae : float
            The aeration energy of the plant / kWh/d
        me : float
            The mixing energy of the plant / kWh/d
        eg : float
            The electricity generation of the plant / kWh/d
        tss : float
            The total suspended solids production of the plant / kg/d
        cm : float
            The added carbon mass of the plant / kg/d
        hd : float
            The heating demand of the sludge / kWh/d
        hp : float
            The heat production of the plant / kWh/d
        simtime : float | None
            The current time step. Only needed if dyn is True. Defaults to None. / d

        Returns
        -------
        float
            The operational cost index of the plant
        """
        tss_cost = 3 * tss
        ae_cost = ae
        me_cost = me
        pe_cost = pe
        eg_income = eg
        cm_cost = 3 * cm
        hd_cost = hd
        hp_income = hp
        eps = 1e-8
        step_day_start = np.where(self.controller.price_times - math.floor(simtime + eps) <= 0)[0][-1]
        step_day_end = np.where(self.controller.price_times - math.floor(simtime + eps + 1) <= 0)[0][-1]
        step_in_day = np.where(self.controller.price_times - (simtime + eps) <= 0)[0][-1] - step_day_start
        daily_avg_price = np.mean(self.controller.electricity_prices[step_day_start:step_day_end])
        cur_price = self.controller.electricity_prices[step_day_start + step_in_day]
        ae_cost *= cur_price / daily_avg_price
        me_cost *= cur_price / daily_avg_price
        pe_cost *= cur_price / daily_avg_price
        eg_income *= cur_price / daily_avg_price
        return tss_cost + ae_cost + me_cost + pe_cost - eg_income + cm_cost + np.maximum(0, hd_cost - hp_income)

    def get_final_performance(self):
        """
        Returns the final performance values for evaluation period.

        Returns
        -------
        iqi_eval : float
            The final iqi value / kg/d
        eqi_eval : float
            The final eqi value / kg/d
        tot_sludge_prod : float
            The total sludge production / kg/d
        tot_tss_mass : float
            The total tss mass / kg/d
        carb_mass : float
            The carbon mass / kg_COD/d
        ch4_prod : float
            The methane production / kg_CH4/d
        h2_prod : float
            The hydrogen production / kg_H2/d
        co2_prod : float
            The carbon dioxide production / kg_CO2/d
        q_gas : float
            The total gas production / m3/d
        heat_demand : float
            The heat demand / kWh/d
        mixingenergy : float
            The mixing energy / kWh/d
        pumpingenergy : float
            The pumping energy / kWh/d
        aerationenergy : float
            The aeration energy / kWh/d
        oci_eval : float
            The final oci value
        """
        # calculate the final performance values
        eval_idx = np.array(
            [np.where(self.simtime <= self.evaltime[0])[0][-1], np.where(self.simtime <= self.evaltime[1])[0][-1]]
        )
        num_eval_timesteps = eval_idx[1] - eval_idx[0]

        iqi_eval = np.sum(self.iqi_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps
        eqi_eval = np.sum(self.eqi_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps

        oci_factors_eval = self.perf_factors_all[eval_idx[0] : eval_idx[1]]
        pumpingenergy = np.sum(oci_factors_eval[:, 0]) / num_eval_timesteps
        aerationenergy = np.sum(oci_factors_eval[:, 1]) / num_eval_timesteps
        mixingenergy = np.sum(oci_factors_eval[:, 2]) / num_eval_timesteps
        chp_production = np.sum(oci_factors_eval[:, 3]) / num_eval_timesteps
        tot_tss_mass = np.sum(oci_factors_eval[:, 4]) / num_eval_timesteps + (
            oci_factors_eval[-1, 6] - oci_factors_eval[0, 6]
        ) / (self.evaltime[-1] - self.evaltime[0])
        tot_sludge_prod = (np.sum(oci_factors_eval[:, 5]) + np.sum(oci_factors_eval[:, 4])) / num_eval_timesteps + (
            oci_factors_eval[-1, 6] - oci_factors_eval[0, 6]
        ) / (self.evaltime[-1] - self.evaltime[0])
        carb_mass = np.sum(oci_factors_eval[:, 7]) / num_eval_timesteps
        heat_demand = np.sum(oci_factors_eval[:, 8]) / num_eval_timesteps
        heat_production = np.sum(oci_factors_eval[:, 9]) / num_eval_timesteps
        ch4_prod = np.sum(oci_factors_eval[:, 10]) / num_eval_timesteps
        h2_prod = np.sum(oci_factors_eval[:, 11]) / num_eval_timesteps
        co2_prod = np.sum(oci_factors_eval[:, 12]) / num_eval_timesteps
        q_gas = np.sum(oci_factors_eval[:, 13]) / num_eval_timesteps

        oci_eval = self.oci(
            pumpingenergy,
            aerationenergy,
            mixingenergy,
            chp_production,
            tot_tss_mass,
            carb_mass,
            heat_demand,
            heat_production,
        )

        return (
            iqi_eval,
            eqi_eval,
            tot_sludge_prod,
            tot_tss_mass,
            carb_mass,
            ch4_prod,
            h2_prod,
            co2_prod,
            q_gas,
            heat_demand,
            mixingenergy,
            pumpingenergy,
            aerationenergy,
            oci_eval,
        )
