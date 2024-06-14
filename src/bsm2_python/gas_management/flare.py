import numpy as np
from numba import boolean, float64, int32
from numba.experimental import jitclass

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
        # ============ Flare ============
        ('max_gas_uptake', int32),
        ('capex', int32),
        ('threshold', float64),
    ]
)
class Flare(Module):
    def __init__(self, capex: int, max_gas_uptake: int, threshold: float):
        """
        A class that represents a flare.
        Arguments:
            capex: capital expenditure of the flare
            max_gas_uptake: maximum gas the flare can process [Nm³/h]
            threshold: threshold for the flare to start processing gas [Nm³/h]
        """
        self.capex = capex
        self.max_gas_uptake = max_gas_uptake
        self.threshold = threshold
        self._consumption = np.array([0.0])
        self._products = np.array([0.0])
        self._load = 0.0

    def calculate_load(self, gas_surplus: float) -> float:
        """
        Calculates the load of the flare depending on the gas surplus.
        """
        if gas_surplus == 0.0:
            return 0.0
        elif gas_surplus > self.max_gas_uptake:
            return 1.0
        else:
            return float(gas_surplus / self.max_gas_uptake)

    @staticmethod
    def produce() -> np.ndarray:
        """
        Returns the products of the flare at the current load.
        """
        return np.array([0.0])

    def consume(self) -> np.ndarray:
        """
        Returns the consumption of the flare at the current load.
        """
        return np.array([self._load * self.max_gas_uptake])

    @staticmethod
    def calculate_maintenance_time() -> float:
        return 0.0

    @staticmethod
    def check_failure() -> bool:
        return False
