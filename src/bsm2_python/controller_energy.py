import warnings

import numpy as np

# REVIEW: In the future, only instances of the gas utilities (chps, boilers,...) should be imported,
# and no more attributes (i.e. we will replace chp_gas_storage_rules and chp_maintenance_rules
# by simply importing the chps-List (as a numba-List)). This will declutter the code.
# class for the operator - schedules production (according to price and gas storage volume) and maintenance of CHPs
# in order to make it compatible to numba, all self.-variable types are defined with annotations right at the beginning
# of the class (all other type annotations are ignored by numba, also the ones in the __init__ method.
# See https://numba.readthedocs.io/en/stable/user/jitclass.html)
# numba has troubles dealing with Lists. So often, using Tuples instead will fix the problem.
# Also, when defining new arrays inside, don't use Numpys dtype argument,
# as Numba will automatically choose a C-datatype, which is not the same as Numpys dtypes.
# numba states that lists of classes are reflected lists which are pending for deprecation
# these lists will be calculated in normal python mode, they throw warnings whenever used however
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning

from bsm2_python.gas_management.boiler import Boiler
from bsm2_python.gas_management.chp import CHP
from bsm2_python.gas_management.cooler import Cooler
from bsm2_python.gas_management.flare import Flare
from bsm2_python.gas_management.gases.gases import Gas, GasMix
from bsm2_python.gas_management.heat_net import HeatNet
from bsm2_python.gas_management.storage import BiogasStorage

warnings.simplefilter('ignore', category=NumbaDeprecationWarning)
warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)


# @jitclass(
#     [
#         ('elapsed_time', int32),
#         ('chp_maintenance_rules', float64[:, :, :]),
#         ('chp_gas_storage_rules', float64[:, :, :]),
#         ('net_biogas', float64),
#         ('net_electricity', float64),
#         ('net_heat', float64),
#         ('sng_production', float64),
#         ('net_water', float64),
#         ('biogas', GasMix.class_type.instance_type),
#         ('o2', Gas.class_type.instance_type),
#         ('ch4', Gas.class_type.instance_type),
#         ('biogas_storage', BiogasStorage.class_type.instance_type),
#         ('num_gas_storage_rules', int64[:]),
#         ('gas_storage_above_threshold', float64[:, :]),
#         ('flare_threshold', float64),
#         ('num_chps', int32),
#         ('num_boilers', int32),
#         ('steps_per_hour', int32),
#         ('price_below_threshold', boolean),
#     ]
# )
class ControllerEnergy:
    def __init__(
        self,
        biogas: GasMix,
        o2: Gas,
        ch4: Gas,
        chp_gas_storage_rules: np.ndarray,
        num_gas_storage_rules: np.ndarray,
        gas_storage_above_threshold: np.ndarray,
        flare_threshold: float,
        num_chps: int,
        num_boilers: int,
        steps_per_hour: int,
    ):
        self.elapsed_time = 0
        self.chp_gas_storage_rules = chp_gas_storage_rules
        self.net_biogas = 0
        self.net_electricity = 0
        self.net_heat = 0
        self.sng_production = 0
        self.net_water = 0
        self.biogas = biogas
        self.o2 = o2
        self.ch4 = ch4
        self.flare_threshold = flare_threshold
        self.num_chps = num_chps
        self.num_boilers = num_boilers
        self.steps_per_hour = steps_per_hour

        # check if all rule-tables are addressing the same number of CHPs
        if self.num_chps != len(self.chp_gas_storage_rules):
            raise ValueError('chp_gas_storage_rules does not match the number of CHPs')

        # Helper variable to check if gas storage rules are active. Has shape (n_chps, n_rules)
        # self.is_gas_storage = np.zeros((self.num_chps, chp_gas_storage_rules.shape[1]))
        # Helper variable to hold number of valid (not NaN) gas storage rules for each CHP. Has shape (n_chps,)
        self.num_gas_storage_rules = num_gas_storage_rules
        # Helper variable to indicate if specific gas storage rules are active. Has shape (n_chps, n_rules)
        self.gas_storage_above_threshold = gas_storage_above_threshold

        # Helper variable to decide if it is economically feasible to run the CHPs
        self.price_below_threshold: bool = False

    def schedule_production(
        self,
        time_diff: float,
        chps: list[CHP],
        boilers: list[Boiler],
        biogas_storage: BiogasStorage,
        cooler: Cooler,
        flare: Flare,
        heat_net: HeatNet,
        heat_demand: float,
        gas_production: float,
    ):
        """
        Set loads for all modules for current timestep.
        Potentially create schedules for electrolyzer and methanation at certain intervals.
        Arguments:
            time: float, current timestep as hours passed since simulation begin, h
            time_diff: float, length of current timestep, h
            real_price: list[float], list with electricity prices for each timestep in simulation, EURO/MWh
            step: int, current absolute simulation step
            oxygen_demand: float, current oxygen demand of wwtp, Nm^3/h
            electricity_demand: float, current electricity demand of wwtp, kW
            chps: List, Numba-List of CHP objects
            boilers: List, Numba-List of boiler objects
        """
        # calculate loads for chps, electrolyzer, methanation
        self.calculate_load_chps(chps, biogas_storage)

        # calculate heat demand and load of boilers
        temperature_after_chps = self.calculate_temperature_after_chps(heat_net, chps, heat_demand)

        biogas_consumption_chps = 0.0  # np.sum([chp.max_gas_power_uptake * chp.load for chp in chps]) / self.biogas.h_u
        for chp in chps:
            biogas_consumption_chps += chp.max_gas_power_uptake * chp.load / self.biogas.h_u
        biogas_storage_after_chps = self.predict_biogas_storage_vol(
            biogas_storage.vol, gas_production, biogas_consumption_chps, time_diff
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
        Arguments:
            chps: List, Numba-List of CHP objects
        """
        for i, chp in enumerate(chps):
            # get rules for current chp, iterate over upper threshold, lower threshold
            for j in np.arange(self.num_gas_storage_rules[i]):
                # if rules are met set load and break loop
                if (biogas_storage.vol / biogas_storage.max_vol > self.chp_gas_storage_rules[i, j, 0]) & (
                    biogas_storage.tendency * self.chp_gas_storage_rules[i, j, 1] >= 0
                ):
                    self.gas_storage_above_threshold[i, j] = True
                    chp.load = self.chp_gas_storage_rules[i, j, 2]
                    break
                # if rules not met set load to 0 and potentially go to lower threshold
                else:
                    self.gas_storage_above_threshold[i, j] = False
                    chp.load = 0
            if not np.any(self.gas_storage_above_threshold[i, :]):
                # logging.debug("Gas Storage too low")
                pass
            if chp.under_maintenance:
                chp.load = 0

    @staticmethod
    def calculate_temperature_after_chps(heat_net: HeatNet, chps: list[CHP], heat_demand: float):
        """
        Calculate the new temperature of the heat net after supplying heat for the fermenter and using heat from chps.
        Arguments:
            chps: List, Numba-List of CHP objects
            heat_demand: float, fermenter heat demand of current timestep, kW
        Returns:
            float, temperature of heat net after using heat from chps °C
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
        Arguments:
            fill_level: float, fill level of biogas storage at start of current timestep, Nm^3
            inflow: float, inflow of biogas in current timestep, Nm^3/h
            outflow: float, outflow of biogas in current timestep, Nm^3/h
            time_diff: float, length of current timestep, 1/4 h
        Returns:
            float, fill level of biogas storage at end of current timestep, Nm^3
        """
        biogas_storage_vol_prog = fill_level + (inflow - outflow) * time_diff

        return biogas_storage_vol_prog

    def calculate_load_boilers(
        self, temperature_deficit: float, heat_net: HeatNet, boilers: list[Boiler], biogas_storage_fill_level: float
    ):
        """
        Calculate the load of the boilers.
        Arguments:
        ----------
            temperature_deficit: float
                temperature deficit of the heat net after supplying heat for the fermenter
                and using heat from chps, K
            heat_net: HeatNet
                heat network object
            boilers: List
                Numba-List of Boiler objects
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
        Arguments:
            temperature_surplus: float, temperature surplus of the heat net
            after supplying heat for the fermenter and using heat from chps, K
            heat_net: HeatNet, heat network object
            cooler: Cooler, cooler object
        """
        excess_heat = temperature_surplus * heat_net.mass_flow * (heat_net.cp / 3600)
        cooler.load = cooler.calculate_load(excess_heat)

    @staticmethod
    def calculate_load_flare(biogas_storeage_max_vol: float, biogas_storage_vol_prog: float, flare: Flare):
        """
        Calculate the load of the flare.
        Calculate fill level of biogas storage at end of current timestep,
        adjust flare load if fill level above threshold.
        Arguments:
        """
        flare_threshold = flare.threshold * biogas_storeage_max_vol
        if biogas_storage_vol_prog >= flare_threshold:
            flare.load = flare.calculate_load(biogas_storage_vol_prog - flare_threshold)
        else:
            flare.load = 0.0
