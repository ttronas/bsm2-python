import numpy as np
from bsm2_python.gas_management.gases.gases import GasMix
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
    # ============ CHP ============
    ('max_gas_power_uptake', int32),
    ('efficiency_rules', float64[:, :]),
    ('stepless_intervals', boolean),
    ('minimum_load', float64),
    ('capex', int32),
    ('biogas', GasMix.class_type.instance_type),
    ('o_and_m', float64),
])
class CHP(Module):
    def __init__(self, max_gas_power_uptake: int, efficiency_rules: np.ndarray, stepless_intervals: boolean,
                 minimum_load: float, MTTF: int, MTTR: int, capex: int, biogas: GasMix):
        """
        A class that represents a combined heat and power unit.
        Arguments:
            max_gas_power_uptake: maximum power of gas the CHP can process [kW]
            efficiency_rules: a 2D array with the efficiency rules of the CHP showing efficiency at different loads
            stepless_intervals: boolean, describes whether the CHP can operate at any load between minimum_load and 1
            minimum_load: minimum load the CHP can operate at
            MTTF: mean time to failure [h]
            MTTR: mean time to repair [h]
            capex: capital expenditure of the CHP
            biogas: GasMix object
        """
        self.max_gas_power_uptake = max_gas_power_uptake
        self.efficiency_rules = efficiency_rules
        self.stepless_intervals = stepless_intervals
        self.minimum_load = minimum_load
        self.MTTF = MTTF
        self.MTTR = MTTR
        self.products = np.array([0., 0.])
        self.consumption = np.array([0.])
        self.capex = capex
        self.biogas = biogas
        # costs for operation & maintenance, €/h at full load
        # costs chp o&m €/kWh: -8 * 10^(-7) * P(CHP) + 0.0132  10.1016/j.apenergy.2014.03.085
        # self.max_gas_power_uptake * self.get_efficiencies(1)[0] * 1 is power electric at load = 1
        self.o_and_m = (-8 * pow(10, -7) * self.max_gas_power_uptake * self.get_efficiencies(1)[0] * 1 + 0.0132) \
                       * self.max_gas_power_uptake * self.get_efficiencies(1)[0] * 1

    def get_efficiencies(self, load: float):
        """
        Returns the efficiency of the CHP at a certain load.
        """
        if load - self.minimum_load < -1e-5:
            if load > 1e-5:
                print("Warning: Load below minimum load, efficiencies set to 0")
            return np.array([0., 0.])
        else:
            closest_rule = np.argmin(np.abs(self.efficiency_rules[:, 0] - load))
            # electrical efficiency, thermal efficiency
            return np.array([self.efficiency_rules[closest_rule, 1], self.efficiency_rules[closest_rule, 2]])

    def get_consumption(self, load: float):
        """
        Returns the consumption of the CHP at a certain load.
        """
        if load - self.minimum_load < -1e-5:
            if load > 1e-5:
                print("Warning: Load below minimum load, consumption set to 0")
            return np.array([0.])
        else:
            return np.array([self.max_gas_power_uptake * load / self.biogas.h_u])

    def get_products(self, load: float):
        """
        Returns the products of the CHP at a certain load.
        """
        if load - self.minimum_load < -1e-5:
            if load > 1e-5:
                print("Warning: Load below minimum load, products set to 0")
            return np.array([0., 0.])
        else:
            el_power = self.max_gas_power_uptake * self.get_efficiencies(load)[0] * load
            th_power = self.max_gas_power_uptake * self.get_efficiencies(load)[1] * load
            return np.array([el_power, th_power])

    def consume(self) -> np.ndarray:
        """
        Returns the consumption of the CHP at the current load.
        """
        return self.get_consumption(self.Load)

    def produce(self) -> np.ndarray:
        """
        Returns the products of the CHP at the current load.
        """
        return self.get_products(self.Load)

    def calculate_maintenance_time(self) -> float:
        """
        Returns the duration of the maintenance.
        """
        return self.MTTR

    def check_failure(self) -> bool:
        """
        Returns whether the CHP goes into maintenance or not.
        """
        if self.TimeSinceLastMaintenance > 0:
            if self.TimeSinceLastMaintenance >= self.MTTF:
                return True
            else:
                return False
        else:
            return False
