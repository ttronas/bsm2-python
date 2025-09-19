import numpy as np

from bsm2_python.bsm1_base import BSM1Base
from bsm2_python.bsm2.init import reginit_bsm1 as reginit
from bsm2_python.bsm2.helpers_bsm2 import Combiner


class BSM1OLDouble(BSM1Base):
    """Creates a BSM1OLDouble object with two parallel WWTPs connected to one effluent.

    This class contains everything that bsm1_ol.py contains, but doubled. 
    This represents two parallel running WWTPs, but at the end, connects them to one Effluent.

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
        # Call parent constructor to set up the first WWTP
        super().__init__(
            data_in=data_in,
            timestep=timestep,
            endtime=endtime,
            evaltime=evaltime,
            tempmodel=tempmodel,
            activate=activate,
            data_out=data_out,
        )
        
        # Create a second complete WWTP (just like the first one)
        from bsm2_python.bsm2.asm1_bsm2 import ASM1Reactor
        from bsm2_python.bsm2.helpers_bsm2 import Splitter
        from bsm2_python.bsm2.settler1d_bsm2 import Settler
        import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init
        import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit
        
        # Second WWTP components (WWTP2)
        self.combiner2 = Combiner()
        self.reactor1_2 = ASM1Reactor(
            asm1init.KLA1,
            asm1init.VOL1,
            asm1init.YINIT1,
            asm1init.PAR1,
            asm1init.CARB1,
            asm1init.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor2_2 = ASM1Reactor(
            asm1init.KLA2,
            asm1init.VOL2,
            asm1init.YINIT2,
            asm1init.PAR2,
            asm1init.CARB2,
            asm1init.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor3_2 = ASM1Reactor(
            asm1init.KLA3,
            asm1init.VOL3,
            asm1init.YINIT3,
            asm1init.PAR3,
            asm1init.CARB3,
            asm1init.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor4_2 = ASM1Reactor(
            asm1init.KLA4,
            asm1init.VOL4,
            asm1init.YINIT4,
            asm1init.PAR4,
            asm1init.CARB4,
            asm1init.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor5_2 = ASM1Reactor(
            asm1init.KLA5,
            asm1init.VOL5,
            asm1init.YINIT5,
            asm1init.PAR5,
            asm1init.CARB5,
            asm1init.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.splitter2 = Splitter()
        self.settler2 = Settler(
            settler1dinit.DIM,
            settler1dinit.LAYER,
            asm1init.QR,
            asm1init.QW,
            settler1dinit.settlerinit,
            settler1dinit.SETTLERPAR,
            asm1init.PAR1,
            tempmodel,
            settler1dinit.MODELTYPE,
        )
        
        # Final combiner to merge effluents from both WWTPs
        self.final_combiner = Combiner()
        
        # Initialize streams for second WWTP
        (
            self.y_in1_2,
            self.y_out1_2,
            self.y_out2_2,
            self.y_out3_2,
            self.y_out4_2,
            self.y_out5_2,
            self.y_out5_r_2,
            self.ys_in_2,
            self.ys_out_2,
            self.ys_eff_2,
        ) = self._create_copies(self.y_in[0], 10)
        
        # Additional storage arrays for second WWTP
        self.y_in1_2_all = np.zeros((len(self.simtime), 21))
        self.y_out1_2_all = np.zeros((len(self.simtime), 21))
        self.y_out2_2_all = np.zeros((len(self.simtime), 21))
        self.y_out3_2_all = np.zeros((len(self.simtime), 21))
        self.y_out4_2_all = np.zeros((len(self.simtime), 21))
        self.y_out5_2_all = np.zeros((len(self.simtime), 21))
        self.y_out5_r_2_all = np.zeros((len(self.simtime), 21))
        self.ys_in_2_all = np.zeros((len(self.simtime), 21))
        self.ys_out_2_all = np.zeros((len(self.simtime), 21))
        self.ys_eff_2_all = np.zeros((len(self.simtime), 21))
        self.sludge_height_2_all = np.zeros(len(self.simtime))
        
        # Combined final effluent
        self.final_effluent = self.y_in[0].copy()
        self.final_effluent_all = np.zeros((len(self.simtime), 21))
        
        # Sludge height for second settler
        self.sludge_height_2 = 0
        
        # KLA values for second WWTP (same as first)
        self.klas_2 = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])

    def step(
        self,
        i: int,
        klas: np.ndarray | None = None,
        klas_2: np.ndarray | None = None,
    ):
        """Simulates one time step of the BSM1OLDouble model.

        Parameters
        ----------
        i : int
            Index of the current time step [-].
        klas : np.ndarray (optional)
            Array with the values of the oxygen transfer coefficients for the 5 ASM1 reactors in WWTP1. \n
            Default is: [reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5]
        klas_2 : np.ndarray (optional)
            Array with the values of the oxygen transfer coefficients for the 5 ASM1 reactors in WWTP2. \n
            Default is: [reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5]
        """

        if klas is None:
            self.klas = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])
        else:
            self.klas = klas
            
        if klas_2 is None:
            self.klas_2 = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])
        else:
            self.klas_2 = klas_2

        # Run the first WWTP step normally
        step: float = self.simtime[i]
        stepsize: float = self.timesteps[i]

        # Set KLA values for both WWTPs
        self.reactor1.kla, self.reactor2.kla, self.reactor3.kla, self.reactor4.kla, self.reactor5.kla = self.klas
        self.reactor1_2.kla, self.reactor2_2.kla, self.reactor3_2.kla, self.reactor4_2.kla, self.reactor5_2.kla = self.klas_2

        # Get influent data that is smaller than and closest to current time step
        y_in_timestep = self.y_in[np.where(self.data_time <= step)[0][-1], :]

        # Split influent equally between two WWTPs (50/50 split)
        y_in_wwtp1 = y_in_timestep.copy()
        y_in_wwtp1[14] = y_in_timestep[14] / 2.0  # Half the flow rate

        y_in_wwtp2 = y_in_timestep.copy()
        y_in_wwtp2[14] = y_in_timestep[14] / 2.0  # Half the flow rate

        # Calculate IQI only once (for the original full influent)
        iqi = self.performance.iqi(y_in_timestep)[0]
        self.iqi_all[i] = iqi

        # WWTP 1 processing
        self.y_in1 = self.combiner.output(y_in_wwtp1, self.ys_out, self.y_out5_r)
        self.y_out1 = self.reactor1.output(stepsize, step, self.y_in1)
        self.y_out2 = self.reactor2.output(stepsize, step, self.y_out1)
        self.y_out3 = self.reactor3.output(stepsize, step, self.y_out2)
        self.y_out4 = self.reactor4.output(stepsize, step, self.y_out3)
        self.y_out5 = self.reactor5.output(stepsize, step, self.y_out4)

        self.ys_in, self.y_out5_r = self.splitter.output(
            self.y_out5, (max(self.y_out5[14] - self.qintr/2, 0.0), float(self.qintr/2))
        )

        self.ys_out, _, self.ys_eff, self.sludge_height, self.ys_tss_internal = self.settler.output(
            stepsize, step, self.ys_in
        )

        # WWTP 2 processing
        self.y_in1_2 = self.combiner2.output(y_in_wwtp2, self.ys_out_2, self.y_out5_r_2)
        self.y_out1_2 = self.reactor1_2.output(stepsize, step, self.y_in1_2)
        self.y_out2_2 = self.reactor2_2.output(stepsize, step, self.y_out1_2)
        self.y_out3_2 = self.reactor3_2.output(stepsize, step, self.y_out2_2)
        self.y_out4_2 = self.reactor4_2.output(stepsize, step, self.y_out3_2)
        self.y_out5_2 = self.reactor5_2.output(stepsize, step, self.y_out4_2)

        self.ys_in_2, self.y_out5_r_2 = self.splitter2.output(
            self.y_out5_2, (max(self.y_out5_2[14] - self.qintr/2, 0.0), float(self.qintr/2))
        )

        self.ys_out_2, _, self.ys_eff_2, self.sludge_height_2, self.ys_tss_internal_2 = self.settler2.output(
            stepsize, step, self.ys_in_2
        )

        # Combine both effluents into final effluent
        self.final_effluent = self.final_combiner.output(self.ys_eff, self.ys_eff_2)

        # Calculate EQI for the combined final effluent
        eqi = self.performance.eqi(self.final_effluent)[0]
        self.eqi_all[i] = eqi

        # Calculate energy consumption for both WWTPs
        import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init
        import bsm2_python.bsm2.init.plantperformanceinit_bsm1 as pp_init
        
        # Calculate energy for each WWTP separately and sum them
        vol1 = np.array([
            self.reactor1.volume,
            self.reactor2.volume,
            self.reactor3.volume,
            self.reactor4.volume,
            self.reactor5.volume,
        ])
        
        vol2 = np.array([
            self.reactor1_2.volume,
            self.reactor2_2.volume,
            self.reactor3_2.volume,
            self.reactor4_2.volume,
            self.reactor5_2.volume,
        ])
        
        sosat = np.array([asm1init.SOSAT1, asm1init.SOSAT2, asm1init.SOSAT3, asm1init.SOSAT4, asm1init.SOSAT5])
        
        # Calculate energy for each WWTP and sum
        ae1 = self.performance.aerationenergy_step(self.klas, vol1[0:5], sosat)
        ae2 = self.performance.aerationenergy_step(self.klas_2, vol2[0:5], sosat)
        self.ae = ae1 + ae2
        
        me1 = self.performance.mixingenergy_step(self.klas, vol1)
        me2 = self.performance.mixingenergy_step(self.klas_2, vol2)
        self.me = me1 + me2
        
        flows = np.array([self.qintr, asm1init.QR*2, asm1init.QW*2])  # Double flows for two WWTPs
        self.pe = self.performance.pumpingenergy_step(flows, pp_init.PP_PAR[10:13])

        # Performance factors
        self.perf_factors_all[i] = [
            self.pe * 24,
            self.ae * 24,
            self.me * 24,
        ]

        # Store results for WWTP1 (original arrays)
        self.y_in_all[i, :] = y_in_timestep
        self.y_in1_all[i, :] = self.y_in1
        self.y_out1_all[i, :] = self.y_out1
        self.y_out2_all[i, :] = self.y_out2
        self.y_out3_all[i, :] = self.y_out3
        self.y_out4_all[i, :] = self.y_out4
        self.y_out5_all[i, :] = self.y_out5
        self.y_out5_r_all[i, :] = self.y_out5_r
        self.ys_in_all[i, :] = self.ys_in
        self.ys_out_all[i, :] = self.ys_out
        self.ys_eff_all[i, :] = self.ys_eff
        self.sludge_height_all[i] = self.sludge_height

        # Store results for WWTP2 (new arrays)
        self.y_in1_2_all[i, :] = self.y_in1_2
        self.y_out1_2_all[i, :] = self.y_out1_2
        self.y_out2_2_all[i, :] = self.y_out2_2
        self.y_out3_2_all[i, :] = self.y_out3_2
        self.y_out4_2_all[i, :] = self.y_out4_2
        self.y_out5_2_all[i, :] = self.y_out5_2
        self.y_out5_r_2_all[i, :] = self.y_out5_r_2
        self.ys_in_2_all[i, :] = self.ys_in_2
        self.ys_out_2_all[i, :] = self.ys_out_2
        self.ys_eff_2_all[i, :] = self.ys_eff_2
        self.sludge_height_2_all[i] = self.sludge_height_2

        # Store final combined effluent
        self.final_effluent_all[i, :] = self.final_effluent
        
        # Calculate violation for final effluent
        from bsm2_python.bsm1_base import SNH
        self.violation_all[i] = self.performance.violation_step(self.final_effluent[SNH], 4)[0]