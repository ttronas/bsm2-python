import numpy as np
from numba import float64
from numba.experimental import jitclass

from bsm2_python.gases.gases import GasMix


@jitclass(
    spec=[
        ('tendency', float64),
        ('max_vol', float64),
        ('vol', float64),
        ('p_store', float64),
        ('inflow', float64),
        ('outflow', float64),
        ('surplus', float64),
        ('deficiency', float64),
        ('capex_sp', float64),
        ('capex', float64),
        ('opex_factor', float64),
        ('biogas', GasMix.class_type.instance_type),
        ('gas_composition', float64[:]),
    ]
)
class BiogasStorage:
    def __init__(
        self,
        max_vol: int | float,
        p_store: int | float,
        vol_init: int | float,
        capex_sp: int | float,
        opex_factor: int | float,
        biogas: GasMix,
        gas_composition: np.ndarray,
    ):
        """
        A class that represents a gas storage.

        Parameters
        ----------
        max_vol : int
            Maximum volume of the storage [Nm³]
        p_store : int
            Pressure of the storage [bar]
        vol_init : int
            Initial volume of the storage [Nm³]
        capex_sp : int
            Capital expenditure per volume of the storage [€/Nm³]
        opex_factor : int
            Operational expenditure factor [h^-1]
        biogas : GasMix
        gas_composition : np.ndarray
            Initial gas composition of the storage
            [ch4_frac, co2_frac, h2_frac, h2o_frac, n2_frac]
        """
        self.tendency = 0.0
        self.max_vol = max_vol
        self.vol = vol_init
        self.p_store = p_store
        self.inflow = 0.0
        self.outflow = 0.0
        self.surplus = 0.0
        self.deficiency = 0.0
        self.capex_sp = capex_sp
        self.capex = capex_sp * max_vol
        self.opex_factor = opex_factor
        self.biogas = biogas
        self.gas_composition = gas_composition

    def update_inflow(self, gas_flow_in: int | float, gas_flow_in_composition: np.ndarray, time_diff: int | float):
        """
        Updates the gas composition and volume of the storage with only the inflow.
        Volume can at first be higher than the maximum volume.

        Parameters
        ----------
        gas_flow_in : int | float
            The gas flow that is coming into the storage [Nm³/h]
        gas_flow_in_composition : np.ndarray
            The gas composition of the incoming gas
            [ch4_frac, co2_frac, h2_frac, h2o_frac, n2_frac]
        time_diff : int | float
            The time difference since the last update [h]

        Returns
        -------
        GasMix
            The biogas object with the updated gas composition
        """
        self.gas_composition = self.biogas.mix(self.gas_composition, self.vol, gas_flow_in_composition, gas_flow_in)
        self.vol += gas_flow_in * time_diff

        return self.biogas

    def update_outflow(self, gas_flow_out: int | float, time_diff: int | float):
        """
        Updates the gas composition and volume of the storage with only the outflow.
        Maximum volume is now considered.

        Parameters
        ----------
        gas_flow_out : int | float
            The gas flow that is coming out of the storage [Nm³/h]
        time_diff : int | float
            The time difference since the last update [h]

        Returns
        -------
        tuple
            The surplus and deficiency of the storage, respectively [Nm³]
        """
        self.vol -= gas_flow_out * time_diff

        if self.vol > self.max_vol:
            self.surplus = self.vol - self.max_vol
            self.vol = self.max_vol
        else:
            self.surplus = 0
        if self.vol < 0:
            self.deficiency = -self.vol
            self.vol = 0
        else:
            self.deficiency = 0

        return self.surplus, self.deficiency
