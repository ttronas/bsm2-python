import numpy as np

from bsm2_python.bsm2.init import reginit_bsm2 as reginit
from bsm2_python.bsm2_base import BSM2Base


class BSM2OL(BSM2Base):
    """Creates a BSM2OL object.

    Parameters
    ----------
    data_in : np.ndarray (optional)
        Influent data. Has to be a 2D array. <br>
        First column is time [days], the rest are 21 components
        (13 ASM1 components, TSS, Q, T and 5 dummy states). <br>
        If not provided, the influent data from BSM2 is used.
    timestep : float (optional)
        Timestep for the simulation (days). <br>
        If not provided, the timestep is calculated from the influent data.
    endtime : float (optional)
        Endtime for the simulation [days]. <br>
        If not provided, the endtime is the last time step in the influent data.
    tempmodel : bool (optional)
        If True, the temperature model dependencies are activated. <br>
        Default is False.
    activate : bool (optional)
        If True, the dummy states are activated. <br>
        Default is False.
    """

    def __init__(self, data_in=None, timestep=None, endtime=None, evaltime=None, *, tempmodel=False, activate=False):
        super().__init__(
            data_in=data_in,
            timestep=timestep,
            endtime=endtime,
            evaltime=evaltime,
            tempmodel=tempmodel,
            activate=activate,
        )

    def step(
        self,
        i: int,
        klas: np.ndarray | None = None,
    ):
        """Simulates one time step of the BSM2 model.

        Parameters
        ----------
        i : int
            Index of the current time step.
        klas : np.ndarray (optional)
            Array with the values of the oxygen transfer coefficients for the 5 ASM1 reactors. <br>
            Default is: [reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5]
        """

        if klas is None:
            self.klas = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])
        else:
            self.klas = klas

        super().step(i)
