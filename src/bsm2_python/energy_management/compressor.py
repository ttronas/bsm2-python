import numpy as np
from numba import boolean, float64, int32
from numba.experimental import jitclass

from bsm2_python.energy_management.module import Module
from bsm2_python.gases.gases import GasMix


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
        ('capex', float64),
    ]
)
class Compressor(Module):
    def __init__(
        self, gas: GasMix, p_in: float, p_out: float, eta: float, max_gas_flow: float, t_in: float, opex_factor: float
    ):
        """
        A class that represents a compressor.

        Parameters
        ----------
        gas : GasMix
        p_in : float
            inlet pressure [bar]
        p_out : float
            outlet pressure [bar]
        eta : float
            electrical efficiency [-]
        max_gas_flow : float
            maximum flow of gas compressor is designed to handle [Nm³/h]
        t_in : float
            inlet temperature [°C]
        opex_factor : float
            factor for the operational expenditure [h^-1]
            (will get multiplied with CAPEX, so that it forms [€/h])
        """
        self.gas = gas
        self.p_in = p_in
        self.p_out = p_out
        self.eta = eta
        self.t_in = t_in
        self.t_out = (
            ((self.t_in + 273.15) * ((self.p_out / self.p_in) ** (self.gas.kappa - 1)) - (self.t_in + 273.15))
            / self.eta
            + (self.t_in + 273.15)
            - 273.15
        )
        self.max_gas_flow = max_gas_flow
        self.max_el_power_uptake = (
            self.gas.cp
            * (t_in + 273.15)
            * max_gas_flow
            * self.gas.rho_norm
            / self.eta
            * ((self.p_out / self.p_in) ** ((self.gas.kappa - 1) / self.gas.kappa) - 1)
        ) / 3600
        self.opex_factor = opex_factor
        self.capex = 88000 * pow(self.max_el_power_uptake, 0.55)  # source https://doi.org/10.1016/j.egypro.2013.06.183

    def calculate_load(self, gas_flow: float) -> float:
        """
        Calculates the load of the compressor based on the gas flow.

        Parameters
        ----------
        gas_flow : float
            gas flow [Nm³/h]

        Returns
        -------
        float
            load of the compressor [-]
        """
        if self.max_gas_flow > 0:
            threshold = 1e-5
            if gas_flow - self.max_gas_flow > threshold:
                raise ValueError('gas flow too high for compressor')
            else:
                return float(gas_flow / self.max_gas_flow)
        else:
            return 0

    @staticmethod
    def produce() -> np.ndarray:
        """
        Returns the production of the compressor.
        (Compressor does not produce anything, only here to satisfy the Module interface)
        """
        return np.array([0.0])

    def consume(self) -> np.ndarray:
        """
        Returns the consumption of the compressor.

        Returns
        -------
        np.ndarray
            consumption of the compressor [kW]
            [electricity]
        """
        return np.array([self._load * self.max_el_power_uptake])

    @staticmethod
    def calculate_maintenance_time() -> float:
        """
        Returns the maintenance time of the compressor.
        (Currently not implemented)
        """
        return 0.0

    @staticmethod
    def check_failure() -> bool:
        """
        Returns if the compressor has failed.
        (Currently not implemented)
        """
        return False
