import numpy as np

from bsm2_python.energy_management.gases.gases import CH4, H2


class Fermenter:
    def __init__(self, capex_sp: float, opex_factor: float, t_op: float) -> None:
        """
        A class that represents a fermenter.
        Arguments:
            capex_sp: float
                capital expenditure of the fermenter
            opex_factor: float
                factor for the operational expenditure [h^-1]
                (will get multiplied with CAPEX, so that it forms [€/h])
            t_op: float
                operating temperature [°C]
        """
        self.capex_sp = capex_sp
        self.opex_factor = opex_factor
        self.gas_production = 0.0
        self.heat_demand = 0.0
        self.electricity_demand = 0.0
        self.p_h2 = 0.0
        self.p_ch4 = 0.6
        self.p_co2 = 0.4
        self.p_gas = 1.0
        self.t_op = t_op

    def step(
        self,
        gas_production: int | float,
        gas_parameters: np.ndarray,
        heat_demand: int | float,
        electricity_demand: int | float,
    ):
        """
        Get data from bsm, set gas composition, heat demand and electricity demand.
        """
        self.gas_production = gas_production
        self.heat_demand = heat_demand
        self.electricity_demand = electricity_demand

        self.p_h2 = gas_parameters[0]
        self.p_ch4 = gas_parameters[1]
        self.p_co2 = gas_parameters[2]
        self.p_gas = gas_parameters[3]

    def get_composition(self):
        """
        Get the gas composition.
        """
        ch4_frac = self.p_ch4 / self.p_gas
        co2_frac = self.p_co2 / self.p_gas
        h2_frac = self.p_h2 / self.p_gas
        h2o_frac = 0 / self.p_gas
        n2_frac = 0 / self.p_gas
        return np.array([ch4_frac, co2_frac, h2_frac, h2o_frac, n2_frac])

    def set_composition(self, gas_parameters: np.ndarray):
        """
        Set the gas composition.
        """
        self.p_gas = gas_parameters[3]
        self.p_h2 = gas_parameters[0] / self.p_gas
        self.p_ch4 = gas_parameters[1] / self.p_gas
        self.p_co2 = gas_parameters[2] / self.p_gas

    def get_lower_heating_value(self):
        """
        Get the lower heating value of the gas.
        """
        return (self.p_h2 * H2.h_u + self.p_ch4 * CH4.h_u) / self.p_gas
