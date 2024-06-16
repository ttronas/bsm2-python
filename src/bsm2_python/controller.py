import csv
import os

import numpy as np

from bsm2_python.gas_management.boiler import Boiler
from bsm2_python.gas_management.chp import CHP
from bsm2_python.gas_management.cooler import Cooler
from bsm2_python.gas_management.fermenter import Fermenter
from bsm2_python.gas_management.flare import Flare
from bsm2_python.gas_management.gases.gases import Gas, GasMix
from bsm2_python.gas_management.heat_net import HeatNet
from bsm2_python.gas_management.storage import BiogasStorage


class Controller:
    def __init__(
        self,
        timestep: float,
        price_percentile: float,
        klas_init: np.ndarray,
        kla_reduction: float,
        s_nh_threshold: float,
        biogas: GasMix,
        o2: Gas,
        ch4: Gas,
    ):
        """
        Creates a Controller object.

        Parameters
        ----------
        timestep : float
            Time step of the simulation in fraction of a day
        price_percentile : float
            Percentile of electricity prices used to adjust KLA values (aeration reduction at prices above the
            percentile)
        klas_init : np.ndarray
            Initial KLA values for the reactor compartments
        kla_reduction : float
            Reduction factor for KLA values
        s_nh_threshold : float
            Maximum value of ammonia concentration in the effluent
        biogas : GasMix
            Biogas object
        o2 : Gas
            Oxygen object
        ch4 : Gas
            Methane object
        """
        self.timestep = timestep
        self.price_percentile = price_percentile
        self.klas_init = klas_init
        self.kla_reduction = kla_reduction
        self.s_nh_threshold = s_nh_threshold
        self.steps_per_day = round(1 / timestep)
        self.is_price_in_percentile = np.full(self.steps_per_day, False)
        path_name = os.path.dirname(__file__)
        with open(path_name + '/data/electricity_prices_2023.csv', encoding='utf-8-sig') as f:
            prices = []
            data = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)
            for price in data:
                prices.append(price[0])
            self.electricity_prices = np.array(prices).astype(np.float64)
        self.biogas = biogas
        self.o2 = o2
        self.ch4 = ch4

    def get_klas(self, step: int, s_nh_reactors: np.ndarray):
        """
        Calculates and returns the KLA values for the reactor compartments based on electricity prices and ammonia
        concentration.

        Parameters
        ----------
        step : int
            Current simulation step
        s_nh_reactors : np.ndarray
            Ammonia concentration in the reactor compartments

        Returns
        -------
        np.ndarray
            KLA values for the reactor compartments
        """
        step_in_day = step % self.steps_per_day
        # get hours with the highest electricity prices
        if step_in_day == 0:
            electricity_prices_day = self.electricity_prices[step : step + self.steps_per_day]
            steps_in_percentile = round(self.steps_per_day * (1 - self.price_percentile))
            indices_percentile = np.argpartition(electricity_prices_day, -steps_in_percentile)[-steps_in_percentile:]
            for i in range(self.steps_per_day):
                self.is_price_in_percentile[i] = i in indices_percentile

        klas = np.zeros(len(self.klas_init))
        for i, s_nh in enumerate(s_nh_reactors):
            if self.s_nh_threshold > s_nh and self.is_price_in_percentile[step_in_day]:
                klas[i] = self.klas_init[i] * self.kla_reduction
            else:
                klas[i] = self.klas_init[i]

        return klas

    def control_gas_management(
        self,
        time_diff: float,
        chps: list[CHP],
        boilers: list[Boiler],
        biogas_storage: BiogasStorage,
        cooler: Cooler,
        flare: Flare,
        heat_net: HeatNet,
        fermenter: Fermenter,
    ):
        """
        Set loads for all gas management modules for current timestep.

        Parameters
        ----------
        time_diff : float
            Length of current timestep, h
        chps : List of CHP objects
        boilers : List of boiler objects
        biogas_storage : BiogasStorage object
        cooler : Cooler object
        flare : Flare object
        heat_net : HeatNet object
        fermenter : Fermenter object
        """
        # calculate loads for chps, electrolyzer, methanation
        self.calculate_load_chps(chps, biogas_storage)

        # calculate heat demand and load of boilers
        temperature_after_chps = self.calculate_temperature_after_chps(heat_net, chps, fermenter.heat_demand)

        biogas_consumption_chps = 0.0  # np.sum([chp.max_gas_power_uptake * chp.load for chp in chps]) / self.biogas.h_u
        for chp in chps:
            biogas_consumption_chps += chp.max_gas_power_uptake * chp.load / self.biogas.h_u
        biogas_storage_after_chps = self.predict_biogas_storage_vol(
            biogas_storage.vol, fermenter.gas_production, biogas_consumption_chps, time_diff
        )

        # reset boilers and coolers
        for boiler in boilers:
            boiler.load = 0
        cooler.load = 0
        if temperature_after_chps < heat_net.lower_threshold:
            temperature_deficit = heat_net.lower_threshold - temperature_after_chps
            self.calculate_load_boilers(temperature_deficit, heat_net, boilers, biogas_storage_after_chps)
        elif temperature_after_chps > heat_net.upper_threshold:
            temperature_surplus = temperature_after_chps - heat_net.upper_threshold
            self.calculate_load_cooler(temperature_surplus, heat_net, cooler)

        biogas_consumption_boiler = 0.0
        for boiler in boilers:
            biogas_consumption_boiler += boiler.max_gas_power_uptake * boiler.load / self.biogas.h_u
        biogas_storage_after_boilers = self.predict_biogas_storage_vol(
            biogas_storage_after_chps, 0, biogas_consumption_boiler, time_diff
        )
        # calculate load of flare depending on biogas storage fill level and useage
        self.calculate_load_flare(biogas_storage.max_vol, biogas_storage_after_boilers, flare)

    def calculate_load_chps(self, chps: list[CHP], biogas_storage: BiogasStorage):
        """
        Set loads for all chps by comparing fill level of biogas storage
        with chp thresholds set in chp_gas_storage_rules.

        Parameters
        ----------
        chps: list of CHP objects
        biogas_storage: BiogasStorage object
        """
        for chp in chps:
            # get rules for current chp, iterate over upper threshold, lower threshold
            for rule in chp.storage_rules:
                # if rules are met set load and break loop
                if (biogas_storage.vol / biogas_storage.max_vol > rule[0]) & (
                    biogas_storage.tendency * rule[1] >= 0
                ):
                    chp.load = rule[2]
                    break
                # if rules not met set load to 0 and potentially go to lower threshold
                else:
                    chp.load = 0
            if chp.under_maintenance:
                chp.load = 0

    @staticmethod
    def calculate_temperature_after_chps(heat_net: HeatNet, chps: list[CHP], heat_demand: float):
        """
        Calculate the new temperature of the heat net after supplying heat for the fermenter and using heat from chps.

        Parameters
        ----------
        chps: list of CHP objects
        heat_demand: float
            heat demand of the fermenter, kW

        Returns
        -------
        float
            temperature of heat net after using heat from chps, °C
        """
        chps_heat = 0
        for chp in chps:
            chps_heat += chp.get_products(chp.load)[1]

        total_heat = chps_heat - heat_demand

        return heat_net.calculate_temperature(total_heat, heat_net.temperature)

    @staticmethod
    def predict_biogas_storage_vol(fill_level, inflow, outflow, time_diff: float):
        """
        Predict the biogas storage volume at the end of the current timestep.

        Parameters
        ----------
        fill_level: float
            fill level of biogas storage at start of current timestep, Nm^3
        inflow: float
            inflow of biogas in current timestep, Nm^3/h
        outflow: float
            outflow of biogas in current timestep, Nm^3/h
        time_diff: float
            length of current timestep, 1/4 h

        Returns
        -------
        float
            fill level of biogas storage at end of current timestep, Nm^3
        """
        biogas_storage_vol_prog = fill_level + (inflow - outflow) * time_diff

        return biogas_storage_vol_prog

    def calculate_load_boilers(
        self, temperature_deficit: float, heat_net: HeatNet, boilers: list[Boiler], biogas_storage_fill_level: float
    ):
        """
        Calculate the load of the boilers.

        Parameters
        ----------
        temperature_deficit: float
            temperature deficit of the heat net after supplying heat for the fermenter
            and using heat from chps, K
        heat_net: HeatNet
            heat network object
        boilers: List
            list of Boiler objects
        biogas_storage_fill_level: float
            fill level of biogas storage after supplying biogas for the
            chps and using receiving biogas from the fermenter, Nm^3
        """
        heat_demand = temperature_deficit * heat_net.mass_flow * (heat_net.cp / 3600)
        for boiler in boilers:
            max_load_possible = min(biogas_storage_fill_level * self.biogas.h_u / boiler.max_gas_power_uptake, 1.0)
            load = boiler.calculate_load(heat_demand)
            if load <= max_load_possible:
                boiler.load = load
            elif max_load_possible >= boiler.minimum_load:
                boiler.load = max_load_possible
            else:
                boiler.load = 0
            heat_production = boiler.get_products(boiler.load)[0]
            heat_demand -= heat_production
            threshold = 1e-5
            if heat_demand <= threshold:
                heat_demand = 0

    @staticmethod
    def calculate_load_cooler(temperature_surplus: float, heat_net: HeatNet, cooler: Cooler):
        """
        Calculate the load of the cooler.

        Parameters
        temperature_surplus: float
            temperature surplus of the heat net after supplying heat for the fermenter and using heat from chps, K
        heat_net: HeatNet
            heat network object
        cooler: Cooler
            cooler object
        """
        excess_heat = temperature_surplus * heat_net.mass_flow * (heat_net.cp / 3600)
        cooler.load = cooler.calculate_load(excess_heat)

    @staticmethod
    def calculate_load_flare(biogas_storeage_max_vol: float, biogas_storage_vol_prog: float, flare: Flare):
        """
        Calculate the load of the flare.
        Calculate fill level of biogas storage at end of current timestep,
        adjust flare load if fill level above threshold.

        Parameters
        ----------
        biogas_storeage_max_vol: float
            maximum volume of biogas storage, Nm^3
        biogas_storage_vol_prog: float
            prognosis of fill level of biogas storage at end of current timestep, Nm^3
        flare: Flare
            flare object
        """
        flare_threshold = flare.threshold * biogas_storeage_max_vol
        if biogas_storage_vol_prog >= flare_threshold:
            flare.load = flare.calculate_load(biogas_storage_vol_prog - flare_threshold)
        else:
            flare.load = 0.0
