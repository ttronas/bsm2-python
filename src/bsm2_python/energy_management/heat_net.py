# class to model the heating network
from numba import float64
from numba.experimental import jitclass


@jitclass(
    [
        ('cp', float64),
        ('temperature', float64),
        ('mass_flow', float64),
        ('lower_threshold', float64),
        ('upper_threshold', float64),
    ]
)
class HeatNet:
    def __init__(
        self, cp: float, initial_temp: float, mass_flow: float, lower_threshold: float, upper_threshold: float
    ) -> None:
        """
        A class that represents a heating network.

        Parameters
        ----------
        cp : float
            Specific heat capacity of the fluid in the heating network [kJ/kgK]
        initial_temp : float
            Initial temperature of the heating network [°C]
        mass_flow : float
            Mass flow of the fluid in the heating network [kg/h]
        lower_threshold : float
            Lower threshold of the heating network (temperature must not fall below this value) [°C]
        upper_threshold : float
            Upper threshold of the heating network (temperature must not rise above this value) [°C]
        """
        self.cp = cp
        self.temperature = initial_temp
        self.mass_flow = mass_flow
        self.lower_threshold = lower_threshold
        self.upper_threshold = upper_threshold

    def update_temperature(self, heat: float) -> None:
        """
        Sets new temperature based on heat input, previous temperature of HeatNet and mass_flow in the heat_network
        Implements the equation: $T_{new} = T_{old} + Q/(m_dot*c_p)$

        Parameters
        ----------
        heat: float
            heat input [kW]
        """
        self.temperature += heat / (self.mass_flow * (self.cp / 3600))

    def calculate_heat(self, new_temperature: float) -> float:
        """
        Calculates heat output based on old and new temperature and mass flow in the heat_network
        Implements the equation: $Q = m_dot*c_p*(T_{new}-T_{old})$

        Parameters
        ----------
        new_temperature: float
            temperature [°C]

        Returns
        -------
        float
            heat output [kW]
        """
        return self.mass_flow * (self.cp / 3600) * (new_temperature - self.temperature)

    def calculate_temperature(self, heat: float, temperature_old: float) -> float:
        """
        Calculates temperature based on heat input, previous temperature and mass_flow in the heat_network
        Implements the equation: $T_{new} = T_{old} + Q/(m_dot*c_p)$

        Parameters
        ----------
        heat: float
            heat input [kW]
        temperature_old: float
            initial temperature [°C]

        Returns
        -------
        float
            new temperature [°C]
        """
        temperature_new = temperature_old + heat / (self.mass_flow * (self.cp / 3600))
        return temperature_new
