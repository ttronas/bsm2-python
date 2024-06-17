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
        Initializes the heat network with a specific heat capacity c_p in kJ/(kg*K).
        Arguments:
            cp: float, specific heat capacity in kJ/(kg*K)
            initial_temp: float, temperature at simulation begin in °C
            mass_flow: float, mass flow in heat net in kg/h
            lower_threshold: float, lower threshold for temperature in °C (temperature must not be lower)
            upper_threshold: float, upper threshold for temperature in °C (temperature must not be higher)
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
        Arguments:
            heat: float, heat input in kW
        """
        self.temperature += heat / (self.mass_flow * (self.cp / 3600))

    def calculate_heat(self, new_temperature: float) -> float:
        """
        Calculates heat output based on old and new temperature and mass flow in the heat_network
        Implements the equation: $Q = m_dot*c_p*(T_{new}-T_{old})$
        Arguments:
            new_temperature: float, temperature in °C
        Returns:
            heat: float, heat output in kW
        """
        return self.mass_flow * (self.cp / 3600) * (new_temperature - self.temperature)

    def calculate_temperature(self, heat: float, temperature_old: float) -> float:
        """
        Calculates temperature based on heat input, previous temperature and mass_flow in the heat_network
        Implements the equation: $T_{new} = T_{old} + Q/(m_dot*c_p)$
        Arguments:
            heat: float, heat input in kW
            old_temperature: float, temperature in °C
        Returns:
            new_temperature: float, temperature in °C
        """
        temperature_new = temperature_old + heat / (self.mass_flow * (self.cp / 3600))
        return temperature_new
