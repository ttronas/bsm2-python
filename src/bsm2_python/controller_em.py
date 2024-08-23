import numpy as np

from bsm2_python.controller import Controller
from bsm2_python.energy_management.boiler import Boiler
from bsm2_python.energy_management.chp import CHP
from bsm2_python.energy_management.cooler import Cooler
from bsm2_python.energy_management.fermenter import Fermenter
from bsm2_python.energy_management.flare import Flare
from bsm2_python.energy_management.heat_net import HeatNet
from bsm2_python.energy_management.storage import BiogasStorage
from bsm2_python.gases.gases import Gas, GasMix


class ControllerEM(Controller):
    def __init__(
        self,
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
        price_percentile : float
            Percentile of electricity prices used to adjust KLA values (aeration reduction at prices above the
            percentile, e.g. 0.9 -> aerate less when electricity prices are in the top 10%)
        klas_init : np.ndarray
            Initial KLA values for the reactor compartments [1/d]
        kla_reduction : float
            Reduction factor for KLA values
        s_nh_threshold : float
            Maximum value of ammonia concentration in the effluent [g/m3]
        biogas : GasMix
            Biogas object
        o2 : Gas
            Oxygen object
        ch4 : Gas
            Methane object
        """
        super().__init__(
            price_percentile=price_percentile,
            klas_init=klas_init,
            kla_reduction=kla_reduction,
            s_nh_threshold=s_nh_threshold,
        )
        self.biogas = biogas
        self.o2 = o2
        self.ch4 = ch4

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
            Length of current timestep [h]
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

        temperature_deficit = max(heat_net.lower_threshold - temperature_after_chps, 0)
        self.calculate_load_boilers(temperature_deficit, heat_net, boilers, biogas_storage_after_chps)

        temperature_surplus = max(temperature_after_chps - heat_net.upper_threshold, 0)
        self.calculate_load_cooler(temperature_surplus, heat_net, cooler)

        biogas_consumption_boiler = 0.0
        for boiler in boilers:
            biogas_consumption_boiler += boiler.max_gas_power_uptake * boiler.load / self.biogas.h_u
        biogas_storage_after_boilers = self.predict_biogas_storage_vol(
            biogas_storage_after_chps, 0, biogas_consumption_boiler, time_diff
        )
        # calculate load of flare depending on biogas storage fill level and useage
        self.calculate_load_flare(biogas_storage.max_vol, biogas_storage_after_boilers, flare)

    @staticmethod
    def calculate_load_chps(chps: list[CHP], biogas_storage: BiogasStorage):
        """
        Set loads for all chps by comparing fill level of biogas storage
        with chp thresholds set in chp_gas_storage_rules.

        Parameters
        ----------
        chps: list of CHP objects
        biogas_storage: BiogasStorage object
        """
        for chp in chps:
            if not chp.ready_to_change_load:
                continue
            # get rules for current chp, iterate over upper threshold, lower threshold
            for rule in chp.storage_rules:
                # if rules are met set load and break loop
                if (biogas_storage.vol / biogas_storage.max_vol > rule[0]) & (biogas_storage.tendency * rule[1] >= 0):
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
            heat demand of the fermenter [kW]

        Returns
        -------
        float
            temperature of heat net after using heat from chps [°C]
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
            fill level of biogas storage at start of current timestep [Nm^3]
        inflow: float
            inflow of biogas in current timestep [Nm^3/h]
        outflow: float
            outflow of biogas in current timestep [Nm^3/h]
        time_diff: float
            length of current timestep [h]

        Returns
        -------
        float
            fill level of biogas storage at end of current timestep [Nm^3]
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
            and using heat from chps [K]
        heat_net: HeatNet
            heat network object
        boilers: List
            list of Boiler objects
        biogas_storage_fill_level: float
            fill level of biogas storage after supplying biogas for the
            chps and using receiving biogas from the fermenter [Nm^3]
        """
        heat_demand = temperature_deficit * heat_net.mass_flow * (heat_net.cp / 3600)
        for boiler in boilers:
            max_load_possible = min(biogas_storage_fill_level * self.biogas.h_u / boiler.max_gas_power_uptake, 1.0)
            load = boiler.calculate_load(heat_demand)
            current_load = boiler.load
            # only check changes from on to off/off to on
            supposed_to_change = (load == 0 and current_load > 0) or (load > 0 and current_load == 0)
            # boiler can't change on/off status if not ready to change load, however partial load level can change
            if supposed_to_change and not boiler.ready_to_change_load:
                continue
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
            temperature surplus of the heat net after supplying heat for the fermenter and using heat from chps [K]
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
            maximum volume of biogas storage [Nm^3]
        biogas_storage_vol_prog: float
            prognosis of fill level of biogas storage at end of current timestep [Nm^3]
        flare: Flare
            flare object
        """
        flare_threshold = flare.threshold * biogas_storeage_max_vol
        if biogas_storage_vol_prog >= flare_threshold:
            flare.load = flare.calculate_load(biogas_storage_vol_prog - flare_threshold)
        else:
            flare.load = 0.0
