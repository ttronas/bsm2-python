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
        # ============ Cooler ============
        ('max_heat_uptake', int32),
        ('capex', int32),
    ]
)
class Cooler(Module):
    def __init__(self, capex: int, max_heat_uptake: int):
        """
        A class that represents a cooler.
        Arguments:
            capex: capital expenditure of the cooler
            max_heat_uptake: maximum heat the cooler can process [kW]
        """
        self.capex = capex
        self.max_heat_uptake = max_heat_uptake
        self._consumption = np.array([0.0])
        self._products = np.array([0.0])
        self._load = 0.0

    def calculate_load(self, heat_surplus: float) -> float:
        if heat_surplus == 0.0:
            return 0.0
        elif heat_surplus > self.max_heat_uptake:
            return 1.0
        else:
            return float(heat_surplus / self.max_heat_uptake)

    @staticmethod
    def produce() -> np.ndarray:
        return np.array([0.0])

    def consume(self) -> np.ndarray:
        return np.array([self._load * self.max_heat_uptake])

    @staticmethod
    def calculate_maintenance_time() -> float:
        return 0.0

    @staticmethod
    def check_failure() -> bool:
        return False
