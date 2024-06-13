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
    # ============ Flare ============
    ('max_gas_uptake', int32),
    ('capex', int32),
    ('threshold', float64),
])
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
        self.consumption = np.array([0.])
        self.products = np.array([0.])

    def calculate_load(self, gas_surplus: float) -> float:
        """
        Calculates the load of the flare depending on the gas surplus.
        """
        if gas_surplus == 0.0:
            return float(0.0)
        elif gas_surplus > self.max_gas_uptake:
            return float(1.0)
        else:
            return float(gas_surplus / self.max_gas_uptake)

    def produce(self) -> np.ndarray:
        """
        Returns the products of the flare at the current load.
        """
        return np.array([0.])

    def consume(self) -> np.ndarray:
        """
        Returns the consumption of the flare at the current load.
        """
        return np.array([self.Load * self.max_gas_uptake])

    def calculate_maintenance_time(self) -> float:
        return 0.

    def check_failure(self) -> bool:
        return False
