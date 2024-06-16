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
        # ============ CHP ============
        ('max_gas_power_uptake', int32),
        ('efficiency_rules', float64[:, :]),
        ('stepless_intervals', boolean),
        ('storage_rules', float64[:, :]),
        ('minimum_load', float64),
        ('capex', int32),
        ('biogas', GasMix.class_type.instance_type),
        ('o_and_m', float64),
    ]
)
class CHP(Module):
    def __init__(
        self,
        max_gas_power_uptake: int,
        efficiency_rules: np.ndarray,
        minimum_load: float,
        mttf: int,
        mttr: int,
        capex: int,
        biogas: GasMix,
        stepless_intervals: bool,
        storage_rules: np.ndarray,
    ):
        """
        A class that represents a combined heat and power unit.
        Arguments:
            max_gas_power_uptake: maximum power of gas the CHP can process [kW]
            efficiency_rules: a 2D array with the efficiency rules of the CHP showing efficiency at different loads
            minimum_load: minimum load the CHP can operate at
            MTTF: mean time to failure [h]
            MTTR: mean time to repair [h]
            capex: capital expenditure of the CHP
            biogas: GasMix object
            stepless_intervals: boolean, describes whether the CHP can operate at any load between minimum_load and 1
            storage_rules: a 2D array with the storage rules of the CHP showing the gas load at different fill levels
        """
        self.max_gas_power_uptake = max_gas_power_uptake
        self.efficiency_rules = efficiency_rules
        self.stepless_intervals = stepless_intervals
        self.storage_rules = storage_rules
        self.minimum_load = minimum_load
        self.mttf = mttf
        self.mttr = mttr
        self._products = np.array([0.0, 0.0])
        self._consumption = np.array([0.0])
        self._load = 0.0
        self.capex = capex
        self.biogas = biogas
        # costs for operation & maintenance, €/h at full load
        # costs chp o&m €/kWh: -8 * 10^(-7) * P(CHP) + 0.0132  10.1016/j.apenergy.2014.03.085
        # self.max_gas_power_uptake * self.get_efficiencies(1)[0] * 1 is power electric at load = 1
        self.o_and_m = (
            (-8 * pow(10, -7) * self.max_gas_power_uptake * self.get_efficiencies(1)[0] * 1 + 0.0132)
            * self.max_gas_power_uptake
            * self.get_efficiencies(1)[0]
            * 1
        )

    def get_efficiencies(self, load: float):
        """
        Returns the efficiency of the CHP at a certain load.
        """
        threshold = 1e-5
        if load - self.minimum_load < -threshold:
            if load > threshold:
                # logging.warning('Load below minimum load, efficiencies set to 0')
                pass
            return np.array([0.0, 0.0])
        else:
            closest_rule = np.argmin(np.abs(self.efficiency_rules[:, 0] - load))
            # electrical efficiency, thermal efficiency
            return np.array([self.efficiency_rules[closest_rule, 1], self.efficiency_rules[closest_rule, 2]])

    def get_consumption(self, load: float):
        """
        Returns the consumption of the CHP at a certain load.
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
        Returns the products of the CHP at a certain load.
        """
        threshold = 1e-5
        if load - self.minimum_load < -threshold:
            if load > threshold:
                # logging.warning('Load below minimum load, products set to 0')
                pass
            return np.array([0.0, 0.0])
        else:
            el_power = self.max_gas_power_uptake * self.get_efficiencies(load)[0] * load
            th_power = self.max_gas_power_uptake * self.get_efficiencies(load)[1] * load
            return np.array([el_power, th_power])

    def consume(self) -> np.ndarray:
        """
        Returns the consumption of the CHP at the current load.
        """
        return self.get_consumption(self._load)

    def produce(self) -> np.ndarray:
        """
        Returns the products of the CHP at the current load.
        """
        return self.get_products(self._load)

    def calculate_maintenance_time(self) -> float:
        """
        Returns the duration of the maintenance.
        """
        return self.mttr

    def check_failure(self) -> bool:
        """
        Returns whether the CHP goes into maintenance or not.
        """
        if self.time_since_last_maintenance > 0:
            return self.time_since_last_maintenance >= self.mttf
        else:
            return False
