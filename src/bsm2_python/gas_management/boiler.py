import numpy as np
from numba import boolean, float64, int32
from numba.experimental import jitclass

from bsm2_python.gas_management.gases.gases import GasMix
from bsm2_python.gas_management.module import Module


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
        stepless_intervals: boolean,
        minimum_load: float,
        capex: int,
        biogas: GasMix,
    ):
        """
        A class that represents a boiler.
        Arguments:
            max_gas_power_uptake: maximum power of gas the boiler can process [kW]
            efficiency_rules: a 2D array with the efficiency rules of the boiler showing efficiency at different loads
            stepless_intervals: boolean, describes whether the boiler can operate at any load between minimum_load and 1
            minimum_load: minimum load the boiler can operate at
            capex: capital expenditure of the boiler
            biogas: GasMix object
        """
        self.max_gas_power_uptake = max_gas_power_uptake
        self.efficiency_rules = efficiency_rules
        self.stepless_intervals = stepless_intervals
        self.minimum_load = minimum_load
        self.capex = capex
        self._products = np.array([0.0])
        self._consumption = np.array([0.0])
        self.biogas = biogas
        self._load = 0.0

    def get_efficiencies(self, load: float):
        """
        Returns the efficiency of the boiler at a certain load.
        """
        threshold = 1e-5
        if load - self.minimum_load < -threshold:
            if load > threshold:
                # logging.warning('Load below minimum load, efficiencies set to 0')
                pass
            return np.array([0.0])
        else:
            closest_rule = np.argmin(np.abs(self.efficiency_rules[:, 0] - load))
            # thermal efficiency
            return np.array([self.efficiency_rules[closest_rule][1]])

    def get_consumption(self, load: float):
        """
        Returns the consumption of the boiler at a certain load.
        """
        threshold = 1e-5
        if load - self.minimum_load < -threshold:
            if load > threshold:
                # logging.warning('Load below minimum load, consumption set to 0')
                pass
            return np.array([0.0])
        else:
            return np.array([self.max_gas_power_uptake * load / self.biogas.h_u])

    def get_products(self, load: float):
        """
        Returns the products of the boiler at a certain load.
        """
        threshold = 1e-5
        if load - self.minimum_load < -threshold:
            if load > threshold:
                # logging.warning('Load below minimum load, products set to 0')
                pass
            return np.array([0.0])
        else:
            th_power = self.max_gas_power_uptake * self.get_efficiencies(load)[0] * load
            return np.array([th_power])

    def consume(self) -> np.ndarray:
        """
        Returns the consumption of the boiler at the current load.
        """
        return self.get_consumption(self._load)

    def produce(self) -> np.ndarray:
        """
        Returns the products of the boiler at the current load.
        """
        return self.get_products(self._load)

    def calculate_load(self, power_demand: float) -> float:
        """
        Returns the load of the boiler at a certain power demand.
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
        return self.mttr

    @staticmethod
    def check_failure() -> bool:
        return False
