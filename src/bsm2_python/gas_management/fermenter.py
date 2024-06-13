import numpy as np
from bsm2_python.gas_management.gases.gases import ch4, h2

class Fermenter:
    def __init__(self, capex_sp: float, opex_factor: float, T_op: float) -> None:
        """
        A class that represents a fermenter.
        Arguments:
            capex_sp: capital expenditure of the fermenter
            opex_factor: factor for the operational expenditure [h^-1] (will get multiplied with CAPEX, so that it forms [€/h])
            T_op: operating temperature [°C]
        """
        self.capex_sp = capex_sp
        self.opex_factor = opex_factor
        self.gas_production = 0
        self.heat_demand = 0
        self.electricity_demand = 0
        self.p_H2 = 0
        self.p_CH4 = 0.6
        self.p_CO2 = 0.4
        self.P_gas = 1
        self.T_op = T_op

    def step(self, gas_production: float, gas_parameters: np.ndarray, heat_demand: float, electricity_demand: float):
        """
        Get data from bsm, set gas composition, heat demand and electricity demand.
        """
        self.gas_production = gas_production
        self.heat_demand = heat_demand
        self.electricity_demand = electricity_demand

        self.p_H2 = gas_parameters[0]
        self.p_CH4 = gas_parameters[1]
        self.p_CO2 = gas_parameters[2]
        self.P_gas = gas_parameters[3]

    def get_composition(self):
        """
        Get the gas composition.
        """
        ch4_frac = self.p_CH4 / self.P_gas
        co2_frac = self.p_CO2 / self.P_gas
        h2_frac = self.p_H2 / self.P_gas
        h2o_frac = 0 / self.P_gas
        n2_frac = 0 / self.P_gas
        return np.array([ch4_frac, co2_frac, h2_frac, h2o_frac, n2_frac])

    def set_composition(self, gas_parameters: np.ndarray):
        """
        Set the gas composition.
        """
        self.P_gas = gas_parameters[3]
        self.p_H2 = gas_parameters[0] / self.P_gas
        self.p_CH4 = gas_parameters[1] / self.P_gas
        self.p_CO2 = gas_parameters[2] / self.P_gas

    def get_lower_heating_value(self):
        """
        Get the lower heating value of the gas.
        """
        return (self.p_H2 * h2.h_u + self.p_CH4 * ch4.h_u) / self.P_gas
