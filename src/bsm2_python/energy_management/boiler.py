import numpy as np
from numba import boolean, float64, int32
from numba.experimental import jitclass

from bsm2_python.energy_management.module import Module
from bsm2_python.gases.gases import GasMix


@jitclass(
    spec=[
        # ============ Module ============
        ('global_time', float64),
        ('_runtime', float64),
        ('_remaining_maintenance_time', float64),
        ('_products', float64[:]),
        ('_consumption', float64[:]),
        ('_time_since_last_maintenance', float64),
        ('_total_maintenance_time', float64),
        ('maintenance_cost_per_hour', float64),
        ('mttf', float64),
        ('mttr', float64),
        ('load_change_time', float64),
        ('_remaining_load_change_time', float64),
        ('_previous_load', float64),
        ('_ready_to_change_load', boolean),
        ('_under_maintenance', boolean),
        ('_load', float64),
        # ============ Boiler ============
        ('max_gas_power_uptake', float64),
        ('efficiency_rules', float64[:, :]),
        ('stepless_intervals', boolean),
        ('minimum_load', float64),
        ('maintenance_cost_per_hour', float64),
        ('capex', int32),
        ('biogas', GasMix.class_type.instance_type),
    ]
)
class Boiler(Module):
    def __init__(
        self,
        max_gas_power_uptake: int,
        efficiency_rules: np.ndarray,
        minimum_load: float,
        load_change_time: float,
        capex: int,
        biogas: GasMix,
        *,
        stepless_intervals: bool,
    ):
        """
        A class that represents a boiler.

        Parameters
        ----------
        max_gas_power_uptake : int
            Maximum power of gas the boiler can process [kW]
        efficiency_rules : np.ndarray
            A 2D array with the efficiency rules of the boiler showing efficiency at different loads
            [[gas load state 1, eta_th1], [gas load state 2, eta_th2], ...]
        minimum_load : float
            Minimum load the boiler can operate at
        load_change_time : float
            Time it takes to change the load of the boiler [hours]
        capex : int
            Capital expenditure of the boiler
        biogas : GasMix
        stepless_intervals : boolean
            Describes whether the boiler can operate at any load between minimum_load and 1
        """
        self.max_gas_power_uptake = max_gas_power_uptake
        self.efficiency_rules = efficiency_rules
        self.minimum_load = minimum_load
        self.load_change_time = load_change_time
        self.capex = capex
        self._products = np.array([0.0])
        self._consumption = np.array([0.0])
        self.biogas = biogas
        self.stepless_intervals = stepless_intervals
        self._load = 0.0

    def get_efficiencies(self, load: float):
        """
        Returns the efficiency of the boiler at a certain load.

        Parameters
        ----------
        load : float
            Load of the boiler

        Returns
        -------
        np.ndarray
            Efficiency of the boiler at the given load
            [eta_th]
        """
        threshold = 1e-5
        if load - self.minimum_load < -threshold:
            if load > threshold:
                # logger.warning('Load below minimum load, efficiencies set to 0')
                pass
            return np.array([0.0])
        else:
            closest_rule = np.argmin(np.abs(self.efficiency_rules[:, 0] - load))
            # thermal efficiency
            return np.array([self.efficiency_rules[closest_rule][1]])

    def get_consumption(self, load: float):
        """
        Returns the consumption of the boiler at a certain load.

        Parameters
        ----------
        load : float
            Load of the boiler

        Returns
        -------
        np.ndarray
            Gas consumption of the boiler at the given load [Nm³/h]
            [biogas consumption]
        """
        threshold = 1e-5
        if load - self.minimum_load < -threshold:
            if load > threshold:
                # logger.warning('Load below minimum load, consumption set to 0')
                pass
            return np.array([0.0])
        else:
            return np.array([self.max_gas_power_uptake * load / self.biogas.h_u])

    def get_products(self, load: float):
        """
        Returns the products of the boiler at a certain load.

        Parameters
        ----------
        load : float
            Load of the boiler

        Returns
        -------
        np.ndarray
            Products of the boiler at the given load [kW]
            [heat]
        """
        threshold = 1e-5
        if load - self.minimum_load < -threshold:
            if load > threshold:
                # logger.warning('Load below minimum load, products set to 0')
                pass
            return np.array([0.0])
        else:
            th_power = self.max_gas_power_uptake * self.get_efficiencies(load)[0] * load
            return np.array([th_power])

    def consume(self) -> np.ndarray:
        """
        Returns the consumption of the boiler at the current load.

        Returns
        -------
        np.ndarray
            Gas consumption of the boiler at the current load [Nm³/h]
            [biogas consumption]
        """
        return self.get_consumption(self._load)

    def produce(self) -> np.ndarray:
        """
        Returns the products of the boiler at the current load.

        Returns
        -------
        np.ndarray
            Products of the boiler at the current load [kW]
            [heat]
        """
        return self.get_products(self._load)

    def calculate_load(self, power_demand: float) -> float:
        """
        Returns the load of the boiler at a certain power demand.

        Parameters
        ----------
        power_demand : float
            Power demand for the boiler

        Returns
        -------
        float
            Load of the boiler to satisfy the given power demand
        """
        max_heat_output = self.max_gas_power_uptake * self.get_efficiencies(1.0)[0]
        if power_demand <= 0.0:
            return 0.0
        elif power_demand >= max_heat_output:
            return 1.0
        else:
            load = power_demand / max_heat_output
            if load < self.minimum_load:
                return self.minimum_load
            else:
                return load

    def calculate_maintenance_time(self) -> float:
        """
        Returns the time it takes to maintain the boiler.
        (Currently not implemented)
        """
        return self.mttr

    @staticmethod
    def check_failure() -> bool:
        """
        Returns whether the boiler has failed.
        (Currently not implemented)
        """
        return False
