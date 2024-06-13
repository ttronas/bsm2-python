import numpy as np
from bsm2_python.gas_management.module import Module
from numba import float64, boolean, int32
from numba.experimental import jitclass

@jitclass(spec=[
    # ============ Module ============
    ('global_time', float64),
    ('runtime', float64),
    ('remaining_maintenance_time', float64),
    ('products', float64[:]),
    ('consumption', float64[:]),
    ('time_since_last_maintenance', float64),
    ('total_maintenance_time', float64),
    ('maintenance_cost_per_hour', float64),
    ('MTTF', float64),
    ('MTTR', float64),
    ('under_maintenance', boolean),
    ('load', float64),
    # ============ Cooler ============
    ('max_heat_uptake', int32),
    ('capex', int32),
])
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
        self.consumption = np.array([0.])
        self.products = np.array([0.])

    def calculate_load(self, heat_surplus: float) -> float:
        if heat_surplus == 0.0:
            return float(0.0)
        elif heat_surplus > self.max_heat_uptake:
            return float(1.0)
        else:
            return float(heat_surplus / self.max_heat_uptake)

    def produce(self) -> np.ndarray:
        return np.array([0.])

    def consume(self) -> np.ndarray:
        return np.array([self.Load * self.max_heat_uptake])

    def calculate_maintenance_time(self) -> float:
        return 0.

    def check_failure(self) -> bool:
        return False
