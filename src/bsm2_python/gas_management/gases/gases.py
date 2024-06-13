import numpy as np
from numba import typeof
from numba.experimental import jitclass
from numba import float64

import logging
from gas_management.gases.gas_params import GAS_PARAMS


# A library with gas properties.

@jitclass(
    [('h_o', float64), ('h_u', float64), ('M', float64), ('kappa', float64), ('mass', float64), ('rho_norm', float64),
     ('cp', float64), ('h_evap_5bar', float64), ('h_evap_10bar', float64), ('h_8bar', float64), ('rho_l', float64),
     ('cp_l', float64)])
class Gas():
    """
    A class that represents a gas species. Contains properties such as density, enthalpy, etc.
    """

    def __init__(self, M: float, h_o: float = 0, h_u: float = 0, kappa: float = 0, mass: float = 0, rho_norm: float = 0,
                 cp: float = 0, h_evap_5bar: float = 0, h_evap_10bar: float = 0, h_8bar: float = 0, rho_l: float = 0,
                 cp_l: float = 0):
        self.h_o = h_o
        self.h_u = h_u
        self.M = M
        self.kappa = kappa
        self.mass = mass
        self.rho_norm = rho_norm
        self.cp = cp
        self.h_evap_5bar = h_evap_5bar
        self.h_evap_10bar = h_evap_10bar
        self.h_8bar = h_8bar
        self.rho_l = rho_l
        self.cp_l = cp_l


h2 = Gas(**GAS_PARAMS.H2)
ch4 = Gas(**GAS_PARAMS.CH4)
h2o = Gas(**GAS_PARAMS.H2O)
co2 = Gas(**GAS_PARAMS.CO2)
n2 = Gas(**GAS_PARAMS.N2)
o2 = Gas(**GAS_PARAMS.O2)


@jitclass(
    [('ch4_frac', float64), ('co2_frac', float64), ('h2_frac', float64), ('h2o_frac', float64), ('n2_frac', float64),
     ('h2', typeof(h2)), ('ch4', typeof(ch4)), ('h2o', typeof(h2o)), ('co2', typeof(co2)), ('n2', typeof(n2)),
     ('h_o', float64), ('h_u', float64), ('M', float64), ('rho_norm', float64), ('cp', float64), ('kappa', float64)])
class GasMix():
    def __init__(self, ch4_frac: float = 0, co2_frac: float = 0, h2_frac: float = 0, h2o_frac: float = 0,
                 n2_frac: float = 0, h2: Gas = h2, ch4: Gas = ch4, h2o: Gas = h2o, co2: Gas = co2, n2: Gas = n2):
        """
        A class that represents a Gas mixture of CH4, CO2, H2, H2O and N2.
        Contains composition as well as deducted properties (heating value etc.)
        """
        self.ch4_frac = ch4_frac
        self.co2_frac = co2_frac
        self.h2_frac = h2_frac
        self.h2o_frac = h2o_frac
        self.n2_frac = n2_frac

        total_frac = self.ch4_frac + self.co2_frac + self.h2_frac + self.h2o_frac + self.n2_frac

        self.ch4 = ch4
        self.co2 = co2
        self.h2 = h2
        self.h2o = h2o
        self.n2 = n2

        self.h_o = (ch4.h_o * self.ch4_frac + co2.h_o * self.co2_frac + h2.h_o * self.h2_frac +
                    h2o.h_o * self.h2o_frac + n2.h_o * self.n2_frac) / total_frac
        self.h_u = (ch4.h_u * self.ch4_frac + co2.h_u * self.co2_frac + h2.h_u * self.h2_frac +
                    h2o.h_u * self.h2o_frac + n2.h_u * self.n2_frac) / total_frac
        self.kappa = (ch4.kappa * self.ch4_frac + co2.kappa * self.co2_frac + h2.kappa * self.h2_frac +
                      h2o.kappa * self.h2o_frac + n2.kappa * self.n2_frac) / total_frac
        self.rho_norm = (ch4.rho_norm * self.ch4_frac + co2.rho_norm * self.co2_frac + h2.rho_norm * self.h2_frac +
                         h2o.rho_norm * self.h2o_frac + n2.rho_norm * self.n2_frac) / total_frac

    def mix(self, gas1_comp: np.ndarray, gas1_vol: float, gas2_comp: np.ndarray, gas2_vol: float):
        """
        Mixes two gases with their respective compositions and volumes.
        """
        # if a composition is changed, the heating value as well as the total fraction is recalculated
        self.ch4_frac = (gas1_comp[0] * gas1_vol + gas2_comp[0] * gas2_vol) / (gas1_vol + gas2_vol)
        self.co2_frac = (gas1_comp[1] * gas1_vol + gas2_comp[1] * gas2_vol) / (gas1_vol + gas2_vol)
        self.h2_frac = (gas1_comp[2] * gas1_vol + gas2_comp[2] * gas2_vol) / (gas1_vol + gas2_vol)
        self.h2o_frac = (gas1_comp[3] * gas1_vol + gas2_comp[3] * gas2_vol) / (gas1_vol + gas2_vol)
        self.n2_frac = (gas1_comp[4] * gas1_vol + gas2_comp[4] * gas2_vol) / (gas1_vol + gas2_vol)

        total_frac = self.ch4_frac + self.co2_frac + self.h2_frac + self.h2o_frac + self.n2_frac
        self.h_o = (self.ch4.h_o * self.ch4_frac + self.co2.h_o * self.co2_frac + self.h2.h_o * self.h2_frac +
                    self.h2o.h_o * self.h2o_frac + self.n2.h_o * self.n2_frac) / total_frac
        self.h_u = (self.ch4.h_u * self.ch4_frac + self.co2.h_u * self.co2_frac + self.h2.h_u * self.h2_frac +
                    self.h2o.h_u * self.h2o_frac + self.n2.h_u * self.n2_frac) / total_frac
        self.kappa = (self.ch4.kappa * self.ch4_frac + self.co2.kappa * self.co2_frac + self.h2.kappa *
                      self.h2_frac + self.h2o.kappa * self.h2o_frac + self.n2.kappa * self.n2_frac) / total_frac
        self.rho_norm = (self.ch4.rho_norm * self.ch4_frac + self.co2.rho_norm * self.co2_frac + self.h2.rho_norm *
                         self.h2_frac + self.h2o.rho_norm * self.h2o_frac + self.n2.rho_norm * self.n2_frac) / total_frac

        return np.array([self.ch4_frac, self.co2_frac, self.h2_frac, self.h2o_frac, self.n2_frac])


biogas = GasMix(**GAS_PARAMS.BIOGAS)
sng = GasMix(**GAS_PARAMS.SNG)

logging.debug("Imported gas properties.")
