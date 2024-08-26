import numpy as np
from numba import float64, typeof
from numba.experimental import jitclass

from bsm2_python.gases.gas_params import GAS_PARAMS
from bsm2_python.log import logger

# A library with gas properties.


@jitclass(
    [
        ('h_o', float64),
        ('h_u', float64),
        ('mole', float64),
        ('kappa', float64),
        ('mass', float64),
        ('rho_norm', float64),
        ('cp', float64),
        ('h_evap_5bar', float64),
        ('h_evap_10bar', float64),
        ('h_8bar', float64),
        ('rho_l', float64),
        ('cp_l', float64),
    ]
)
class Gas:
    """
    A class that represents a singular gas species. Contains properties such as density, enthalpy, etc.
    """

    def __init__(
        self,
        mole: float,
        h_o: float = 0,
        h_u: float = 0,
        kappa: float = 0,
        mass: float = 0,
        rho_norm: float = 0,
        cp: float = 0,
        h_evap_5bar: float = 0,
        h_evap_10bar: float = 0,
        h_8bar: float = 0,
        rho_l: float = 0,
        cp_l: float = 0,
    ):
        self.h_o = h_o
        self.h_u = h_u
        self.mole = mole
        self.kappa = kappa
        self.mass = mass
        self.rho_norm = rho_norm
        self.cp = cp
        self.h_evap_5bar = h_evap_5bar
        self.h_evap_10bar = h_evap_10bar
        self.h_8bar = h_8bar
        self.rho_l = rho_l
        self.cp_l = cp_l


H2 = Gas(**GAS_PARAMS.H2)
CH4 = Gas(**GAS_PARAMS.CH4)
H2O = Gas(**GAS_PARAMS.H2O)
CO2 = Gas(**GAS_PARAMS.CO2)
N2 = Gas(**GAS_PARAMS.N2)
O2 = Gas(**GAS_PARAMS.O2)


@jitclass(
    [
        ('ch4_frac', float64),
        ('co2_frac', float64),
        ('h2_frac', float64),
        ('h2o_frac', float64),
        ('n2_frac', float64),
        ('h2', typeof(H2)),
        ('ch4', typeof(CH4)),
        ('h2o', typeof(H2O)),
        ('co2', typeof(CO2)),
        ('n2', typeof(N2)),
        ('h_o', float64),
        ('h_u', float64),
        ('mole', float64),
        ('rho_norm', float64),
        ('cp', float64),
        ('kappa', float64),
    ]
)
class GasMix:
    def __init__(
        self,
        ch4_frac: float = 0,
        co2_frac: float = 0,
        h2_frac: float = 0,
        h2o_frac: float = 0,
        n2_frac: float = 0,
        h2: Gas = H2,
        ch4: Gas = CH4,
        h2o: Gas = H2O,
        co2: Gas = CO2,
        n2: Gas = N2,
    ):
        """
        A class that represents a mixture of gases. Contains fractions of each gas

        Parameters
        ----------
        ch4_frac : float
            Volumetric fraction of methane
        co2_frac : float
            Volumetric fraction of carbon dioxide
        h2_frac : float
            Volumetric fraction of hydrogen
        h2o_frac : float
            Volumetric fraction of water
        n2_frac : float
            Volumetric fraction of nitrogen
        h2 : Gas
        ch4 : Gas
        h2o : Gas
        co2 : Gas
        n2 : Gas
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

        self.h_o = (
            ch4.h_o * self.ch4_frac
            + co2.h_o * self.co2_frac
            + h2.h_o * self.h2_frac
            + h2o.h_o * self.h2o_frac
            + n2.h_o * self.n2_frac
        ) / total_frac
        self.h_u = (
            ch4.h_u * self.ch4_frac
            + co2.h_u * self.co2_frac
            + h2.h_u * self.h2_frac
            + h2o.h_u * self.h2o_frac
            + n2.h_u * self.n2_frac
        ) / total_frac
        self.kappa = (
            ch4.kappa * self.ch4_frac
            + co2.kappa * self.co2_frac
            + h2.kappa * self.h2_frac
            + h2o.kappa * self.h2o_frac
            + n2.kappa * self.n2_frac
        ) / total_frac
        self.rho_norm = (
            ch4.rho_norm * self.ch4_frac
            + co2.rho_norm * self.co2_frac
            + h2.rho_norm * self.h2_frac
            + h2o.rho_norm * self.h2o_frac
            + n2.rho_norm * self.n2_frac
        ) / total_frac
        self.cp = (
            ch4.cp * self.ch4_frac
            + co2.cp * self.co2_frac
            + h2.cp * self.h2_frac
            + h2o.cp * self.h2o_frac
            + n2.cp * self.n2_frac
        ) / total_frac

    def mix(self, gas1_comp: np.ndarray, gas1_vol: float, gas2_comp: np.ndarray, gas2_vol: float):
        """
        Mixes two gases with their respective compositions and volumes and updates the properties of the mixture

        Parameters
        ----------
        gas1_comp : np.ndarray
            Composition of gas 1
            [ch4_frac, co2_frac, h2_frac, h2o_frac, n2_frac]
        gas1_vol : float
            Volume of gas 1
        gas2_comp : np.ndarray
            Composition of gas 2
            [ch4_frac, co2_frac, h2_frac, h2o_frac, n2_frac]
        gas2_vol : float
            Volume of gas 2

        Returns
        -------
        np.ndarray
            New composition of the gas mixture
            [ch4_frac, co2_frac, h2_frac, h2o_frac, n2_frac]
        """
        # if a composition is changed, the heating value as well as the total fraction is recalculated
        self.ch4_frac = (gas1_comp[0] * gas1_vol + gas2_comp[0] * gas2_vol) / (gas1_vol + gas2_vol)
        self.co2_frac = (gas1_comp[1] * gas1_vol + gas2_comp[1] * gas2_vol) / (gas1_vol + gas2_vol)
        self.h2_frac = (gas1_comp[2] * gas1_vol + gas2_comp[2] * gas2_vol) / (gas1_vol + gas2_vol)
        self.h2o_frac = (gas1_comp[3] * gas1_vol + gas2_comp[3] * gas2_vol) / (gas1_vol + gas2_vol)
        self.n2_frac = (gas1_comp[4] * gas1_vol + gas2_comp[4] * gas2_vol) / (gas1_vol + gas2_vol)

        total_frac = self.ch4_frac + self.co2_frac + self.h2_frac + self.h2o_frac + self.n2_frac
        self.h_o = (
            self.ch4.h_o * self.ch4_frac
            + self.co2.h_o * self.co2_frac
            + self.h2.h_o * self.h2_frac
            + self.h2o.h_o * self.h2o_frac
            + self.n2.h_o * self.n2_frac
        ) / total_frac
        self.h_u = (
            self.ch4.h_u * self.ch4_frac
            + self.co2.h_u * self.co2_frac
            + self.h2.h_u * self.h2_frac
            + self.h2o.h_u * self.h2o_frac
            + self.n2.h_u * self.n2_frac
        ) / total_frac
        self.kappa = (
            self.ch4.kappa * self.ch4_frac
            + self.co2.kappa * self.co2_frac
            + self.h2.kappa * self.h2_frac
            + self.h2o.kappa * self.h2o_frac
            + self.n2.kappa * self.n2_frac
        ) / total_frac
        self.rho_norm = (
            self.ch4.rho_norm * self.ch4_frac
            + self.co2.rho_norm * self.co2_frac
            + self.h2.rho_norm * self.h2_frac
            + self.h2o.rho_norm * self.h2o_frac
            + self.n2.rho_norm * self.n2_frac
        ) / total_frac
        self.cp = (
            self.ch4.cp * self.ch4_frac
            + self.co2.cp * self.co2_frac
            + self.h2.cp * self.h2_frac
            + self.h2o.cp * self.h2o_frac
            + self.n2.cp * self.n2_frac
        ) / total_frac

        return np.array([self.ch4_frac, self.co2_frac, self.h2_frac, self.h2o_frac, self.n2_frac])


BIOGAS = GasMix(**GAS_PARAMS.BIOGAS)

logger.debug('Imported gas properties.')
