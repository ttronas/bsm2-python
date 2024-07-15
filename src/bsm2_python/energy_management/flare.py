import numpy as np
from numba import boolean, float64, int32
from numba.experimental import jitclass

from bsm2_python.energy_management.module import Module


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

        Parameters
        ----------
        capex : int
            Capital expenditure of the flare
        max_gas_uptake : int
            Maximum gas the flare can process [Nm³/h]
        threshold : float
            The threshold at which the flare starts to operate
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

        Parameters
        ----------
        gas_surplus : float
            The gas surplus that the flare has to process [Nm³/h]
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
        Returns the production of the flare.
        (Flare does not produce anything, only here to satisfy the Module interface)
        """
        return np.array([0.0])

    def consume(self) -> np.ndarray:
        """
        Returns the consumption of the flare at the current load.

        Returns
        -------
        np.ndarray
            consumption of the flare [kW]
            [biogas]
        """
        return np.array([self._load * self.max_gas_uptake])

    @staticmethod
    def calculate_maintenance_time() -> float:
        """
        Returns the maintenance time of the flare.
        (Currently not implemented)
        """
        return 0.0

    @staticmethod
    def check_failure() -> bool:
        """
        Returns if the flare has failed.
        (Currently not implemented)
        """
        return False
