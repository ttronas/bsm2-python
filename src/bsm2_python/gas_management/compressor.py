from bsm2_python.gas_management.gases.gases import GasMix
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
    # ============ Compressor ============
    ('gas', GasMix.class_type.instance_type),
    ('p_in', int32),
    ('p_out', int32),
    ('eta', float64),
    ('t_in', float64),
    ('t_out', float64),
    ('max_gas_flow', float64),
    ('max_el_power_uptake', float64),
    ('opex_factor', float64),
    ('capex', float64)
])
class Compressor(Module):
    def __init__(self, gas: GasMix, p_in: float, p_out: float, eta: float, max_gas_flow: float, t_in: float,
                 opex_factor: float):
        """
        A class that represents a compressor.
        Arguments:
            gas: Gas object
            p_in: inlet pressure [bar]
            p_out: outlet pressure [bar]
            eta: efficiency [-]
            max_gas_flow: maximum flow of gas compressor is designed to handle [Nm³/h]
            t_in: inlet temperature [°C]
            opex_factor: factor for the operational expenditure [h^-1] (will get multiplied with CAPEX, so that it forms [€/h])
        """
        self.gas = gas
        self.p_in = p_in
        self.p_out = p_out
        self.eta = eta
        self.t_in = t_in
        self.t_out = (((self.t_in + 273.15) * ((self.p_out / self.p_in) ** (self.gas.kappa - 1)) -
                       (self.t_in + 273.15)) / self.eta + (self.t_in + 273.15) - 273.15)
        self.max_gas_flow = max_gas_flow
        self.max_el_power_uptake = (self.gas.cp * (t_in + 273.15) * max_gas_flow * self.gas.rho_norm / self.eta *
                                    ((self.p_out / self.p_in) ** ((self.gas.kappa - 1) / self.gas.kappa) - 1)) / 3600
        self.opex_factor = opex_factor
        self.capex = 88000 * pow(self.max_el_power_uptake, 0.55)  # source https://doi.org/10.1016/j.egypro.2013.06.183

    def calculate_load(self, gas_flow: float) -> float:
        if self.max_gas_flow > 0:
            if gas_flow - self.max_gas_flow > 1e-5:
                raise ValueError(f"gas flow too high for compressor")
            else:
                return float(gas_flow / self.max_gas_flow)
        else:
            return 0

    def produce(self) -> np.ndarray:
        return np.array([0.])

    def consume(self) -> np.ndarray:
        return np.array([self.Load * self.max_el_power_uptake])

    def calculate_maintenance_time(self) -> float:
        return 0.

    def check_failure(self) -> bool:
        return False
