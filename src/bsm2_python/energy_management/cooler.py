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
        # ============ Cooler ============
        ('max_heat_uptake', int32),
        ('capex', int32),
    ]
)
class Cooler(Module):
    def __init__(self, capex: int, max_heat_uptake: int):
        """
        A class that represents a cooler.

        Parameters
        ----------
        capex : int
            Capital expenditure of the cooler
        max_heat_uptake : int
            Maximum heat the cooler can compensate [kW]
        """
        self.capex = capex
        self.max_heat_uptake = max_heat_uptake
        self._consumption = np.array([0.0])
        self._products = np.array([0.0])
        self._load = 0.0

    def calculate_load(self, heat_surplus: float) -> float:
        """
        Calculate the load of the cooler based on the heat surplus.

        Parameters
        ----------
        heat_surplus : float
            The heat surplus that the cooler has to compensate [kW]

        Returns
        -------
        float
            The load of the cooler [-]
        """
        if heat_surplus == 0.0:
            return 0.0
        elif heat_surplus > self.max_heat_uptake:
            return 1.0
        else:
            return float(heat_surplus / self.max_heat_uptake)

    @staticmethod
    def produce() -> np.ndarray:
        """
        Returns the production of the cooler.
        (Cooler does not produce anything, only here to satisfy the Module interface)
        """
        return np.array([0.0])

    def consume(self) -> np.ndarray:
        """
        Returns the consumption of the cooler.

        Returns
        -------
        np.ndarray
            consumption of the cooler [kW]
            [heat]
        """
        return np.array([self._load * self.max_heat_uptake])

    @staticmethod
    def calculate_maintenance_time() -> float:
        """
        Returns the maintenance time of the cooler.
        (Currently not implemented)
        """
        return 0.0

    @staticmethod
    def check_failure() -> bool:
        """
        Returns if the cooler has failed.
        (Currently not implemented)
        """
        return False
