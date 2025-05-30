"""This represents the base model in an open loop simulation.

- BSM2 base: Primary clarifier, 5 asm1 reactors, a second clarifier, sludge thickener,
adm1 fermenter, sludge dewatering and wastewater storage in dynamic simulation without any controllers.
"""

import numpy as np

from bsm2_python.bsm2.init import reginit_bsm2 as reginit
from bsm2_python.bsm2_base import BSM2Base


class BSM2OL(BSM2Base):
    """Creates a BSM2OL object.

    Parameters
    ----------
    data_in : np.ndarray(n, 22) | str (optional)
        Influent data. Has to be a 2D array. <br>
        First column is time [d], the rest are 21 components
        (13 ASM1 components, TSS, Q, T and 5 dummy states).
        If a string is provided, it is interpreted as a file name.
        If not provided, the influent data from BSM2 is used. \n
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5]
    timestep : float (optional)
        Timestep for the simulation [d]. <br>
        If not provided, the timestep is set to 1 minute. <br>
        Please note: Due to sensor sensitivity, the timestep should not be larger than 1 minute.
    endtime : float (optional)
        Endtime for the simulation [d]. <br>
        If not provided, the endtime is the last time step in the influent data.
    evaltime : int | np.ndarray(2) (optional)
        Evaluation time for the simulation [d]. <br>
        When passed as an int, it defines the number of last days of the simulation to be evaluated.
        When passed as a 1D np.ndarray with two values, it defines the start and end time of the evaluation period.
        If not provided, the last 5 days of the simulation will be assessed. \n
        [starttime, self.simtime[-1]]
    data_out : str (optional)
        Path to the output data file. <br>
        If not provided, no output data is saved.
    tempmodel : bool (optional)
        If `True`, the temperature model dependencies are activated.
        Default is `False`.
    activate : bool (optional)
        If `True`, the dummy states are activated.
        Default is `False`.
    """

    def __init__(
        self,
        data_in: np.ndarray | str | None = None,
        timestep: float | None = None,
        endtime: float | None = None,
        evaltime: int | np.ndarray | None = None,
        data_out: str | None = None,
        *,
        tempmodel: bool = False,
        activate: bool = False,
    ):
        super().__init__(
            data_in=data_in,
            timestep=timestep,
            endtime=endtime,
            evaltime=evaltime,
            tempmodel=tempmodel,
            activate=activate,
            data_out=data_out,
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
            Index of the current time step [-].
        klas : np.ndarray (optional)
            Array with the values of the oxygen transfer coefficients for the 5 ASM1 reactors. \n
            Default is: [reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5]
        """

        if klas is None:
            self.klas = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])
        else:
            self.klas = klas

        super().step(i)
