import numpy as np

from bsm2_python.gases.gases import CH4, H2


class Fermenter:
    """A class that represents a fermenter.

    Parameters
    ----------
    capex_sp : float
        Specific capital expenditure of the fermenter. <br>
        (Should get multiplied with the gas production to get the total capital expenditure) <br>
        (Currently not implemented)
    opex_factor : float
        Factor for the operational expenditure [1/h]. <br>
        Will get multiplied with CAPEX, so that it forms [€/h].
    t_op : float
        Operating temperature of the fermenter [°C].
    """

    def __init__(self, capex_sp: float, opex_factor: float, t_op: float) -> None:
        self.capex_sp = capex_sp
        self.opex_factor = opex_factor
        self.gas_production = 0.0
        self.heat_demand = 0.0
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
    ):
        """Update the fermenter with new values.

        Parameters
        ----------
        gas_production : int or float
            The gas production of the fermenter [Nm³/h].
        gas_parameters : np.ndarray
            Array that contains the gas pressure of the fermenter gas. <br>
            [p_H2, p_CH4, p_CO2, P_gas] \n
            - p_H2: Pressure fraction of hydrogen [bar].
            - p_CH4: Pressure fraction of methane [bar].
            - p_CO2: Pressure fraction of carbon dioxide [bar].
            - P_gas: Total pressure of the gas [bar].
        heat_demand : int or float
            The heat demand of the fermenter [kW].
        """

        self.gas_production = gas_production
        self.heat_demand = heat_demand

        self.p_h2 = gas_parameters[0]
        self.p_ch4 = gas_parameters[1]
        self.p_co2 = gas_parameters[2]
        self.p_gas = gas_parameters[3]

    def get_composition(self):
        """Returns the gas composition.

        Returns
        -------
        np.ndarray
            Array that contains the gas composition of the fermenter gas. <br>
            [ch4_frac, co2_frac, h2_frac, h2o_frac, n2_frac] \n
            - ch4_frac: Gas fraction of methane.
            - co2_frac: Gas fraction of carbon dioxide.
            - h2_frac: Gas fraction of hydrogen.
            - h2o_frac: Gas fraction of water.
            - n2_frac: Gas fraction of nitrogen.
        """

        ch4_frac = self.p_ch4 / self.p_gas
        co2_frac = self.p_co2 / self.p_gas
        h2_frac = self.p_h2 / self.p_gas
        h2o_frac = 0 / self.p_gas
        n2_frac = 0 / self.p_gas
        return np.array([ch4_frac, co2_frac, h2_frac, h2o_frac, n2_frac])

    def set_composition(self, gas_parameters: np.ndarray):
        """Set the gas composition.

        Parameters
        ----------
        gas_parameters : np.ndarray
            Array that contains the gas pressure of the fermenter gas. <br>
            [p_H2, p_CH4, p_CO2, P_gas] \n
            - p_H2: Pressure fraction of hydrogen [bar].
            - p_CH4: Pressure fraction of methane [bar].
            - p_CO2: Pressure fraction of carbon dioxide [bar].
            - P_gas: Total pressure of the gas [bar].
        """

        self.p_gas = gas_parameters[3]
        self.p_h2 = gas_parameters[0] / self.p_gas
        self.p_ch4 = gas_parameters[1] / self.p_gas
        self.p_co2 = gas_parameters[2] / self.p_gas

    def get_lower_heating_value(self):
        """Returns the lower heating value of the gas.

        Returns
        -------
        float
            Lower heating value of the gas [kWh/Nm³].
        """

        return (self.p_h2 * H2.h_u + self.p_ch4 * CH4.h_u) / self.p_gas
