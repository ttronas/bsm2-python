import numpy as np

from bsm2_python.bsm1_base import BSM1Base
from bsm2_python.bsm2.init import reginit_bsm1 as reginit


class BSM1OL2Parallel(BSM1Base):
    """Creates a BSM1OL2Parallel object with two completely independent parallel WWTPs.

    This class contains two completely independent BSM1OL WWTPs running in parallel.
    Each WWTP has its own influent and effluent. There are no connections between the WWTPs.

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

        # Initialize components for WWTP 1
        from bsm2_python.bsm2.asm1_bsm2 import ASM1Reactor
        from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter
        from bsm2_python.bsm2.settler1d_bsm2 import Settler
        import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init
        import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit

        # WWTP 1 Components
        self.combiner1 = Combiner()
        self.reactor1_1 = ASM1Reactor(
            asm1init.KLA1, asm1init.VOL1, asm1init.YINIT1, asm1init.PAR1, asm1init.CARB1,
            asm1init.CARBONSOURCECONC, tempmodel=tempmodel, activate=activate
        )
        self.reactor2_1 = ASM1Reactor(
            asm1init.KLA2, asm1init.VOL2, asm1init.YINIT2, asm1init.PAR2, asm1init.CARB2,
            asm1init.CARBONSOURCECONC, tempmodel=tempmodel, activate=activate
        )
        self.reactor3_1 = ASM1Reactor(
            asm1init.KLA3, asm1init.VOL3, asm1init.YINIT3, asm1init.PAR3, asm1init.CARB3,
            asm1init.CARBONSOURCECONC, tempmodel=tempmodel, activate=activate
        )
        self.reactor4_1 = ASM1Reactor(
            asm1init.KLA4, asm1init.VOL4, asm1init.YINIT4, asm1init.PAR4, asm1init.CARB4,
            asm1init.CARBONSOURCECONC, tempmodel=tempmodel, activate=activate
        )
        self.reactor5_1 = ASM1Reactor(
            asm1init.KLA5, asm1init.VOL5, asm1init.YINIT5, asm1init.PAR5, asm1init.CARB5,
            asm1init.CARBONSOURCECONC, tempmodel=tempmodel, activate=activate
        )
        self.splitter1 = Splitter()
        self.settler1 = Settler(
            settler1dinit.DIM, settler1dinit.LAYER, asm1init.QR, asm1init.QW,
            settler1dinit.settlerinit, settler1dinit.SETTLERPAR, asm1init.PAR1, tempmodel, settler1dinit.MODELTYPE
        )

        # WWTP 2 Components
        self.combiner2 = Combiner()
        self.reactor1_2 = ASM1Reactor(
            asm1init.KLA1, asm1init.VOL1, asm1init.YINIT1, asm1init.PAR1, asm1init.CARB1,
            asm1init.CARBONSOURCECONC, tempmodel=tempmodel, activate=activate
        )
        self.reactor2_2 = ASM1Reactor(
            asm1init.KLA2, asm1init.VOL2, asm1init.YINIT2, asm1init.PAR2, asm1init.CARB2,
            asm1init.CARBONSOURCECONC, tempmodel=tempmodel, activate=activate
        )
        self.reactor3_2 = ASM1Reactor(
            asm1init.KLA3, asm1init.VOL3, asm1init.YINIT3, asm1init.PAR3, asm1init.CARB3,
            asm1init.CARBONSOURCECONC, tempmodel=tempmodel, activate=activate
        )
        self.reactor4_2 = ASM1Reactor(
            asm1init.KLA4, asm1init.VOL4, asm1init.YINIT4, asm1init.PAR4, asm1init.CARB4,
            asm1init.CARBONSOURCECONC, tempmodel=tempmodel, activate=activate
        )
        self.reactor5_2 = ASM1Reactor(
            asm1init.KLA5, asm1init.VOL5, asm1init.YINIT5, asm1init.PAR5, asm1init.CARB5,
            asm1init.CARBONSOURCECONC, tempmodel=tempmodel, activate=activate
        )
        self.splitter2 = Splitter()
        self.settler2 = Settler(
            settler1dinit.DIM, settler1dinit.LAYER, asm1init.QR, asm1init.QW,
            settler1dinit.settlerinit, settler1dinit.SETTLERPAR, asm1init.PAR1, tempmodel, settler1dinit.MODELTYPE
        )

        # Initialize arrays to store results for both WWTPs
        # WWTP 1 results
        self.ys_eff_1 = np.zeros(21)
        self.sludge_height_1 = 0.0
        self.ys_tss_internal_1 = np.zeros(10)
        
        # WWTP 2 results
        self.ys_eff_2 = np.zeros(21)
        self.sludge_height_2 = 0.0
        self.ys_tss_internal_2 = np.zeros(10)

        # Store internal streams for each WWTP
        # WWTP 1 streams
        self.y_in1_1 = np.zeros(21)
        self.y_out1_1 = np.zeros(21)
        self.y_out2_1 = np.zeros(21)
        self.y_out3_1 = np.zeros(21)
        self.y_out4_1 = np.zeros(21)
        self.y_out5_1 = np.zeros(21)
        self.ys_in_1 = np.zeros(21)
        self.y_out5_r_1 = np.zeros(21)
        self.ys_out_1 = np.zeros(21)

        # WWTP 2 streams
        self.y_in1_2 = np.zeros(21)
        self.y_out1_2 = np.zeros(21)
        self.y_out2_2 = np.zeros(21)
        self.y_out3_2 = np.zeros(21)
        self.y_out4_2 = np.zeros(21)
        self.y_out5_2 = np.zeros(21)
        self.ys_in_2 = np.zeros(21)
        self.y_out5_r_2 = np.zeros(21)
        self.ys_out_2 = np.zeros(21)

        # Additional performance arrays for convergence and energy
        self.violation_all = np.zeros(len(self.simtime))

        self.klas_1 = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])
        self.klas_2 = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])

    def step(
        self,
        i: int,
        klas_1: np.ndarray | None = None,
        klas_2: np.ndarray | None = None,
    ):
        """
        Perform one step of the simulation for both parallel WWTPs.

        Parameters
        ----------
        i : int
            Index of the current time step.
        klas_1 : np.ndarray | None (optional)
            KLA values for WWTP 1 reactors.
        klas_2 : np.ndarray | None (optional)
            KLA values for WWTP 2 reactors.
        """
        if klas_1 is None:
            self.klas_1 = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])
        else:
            self.klas_1 = klas_1
            
        if klas_2 is None:
            self.klas_2 = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])
        else:
            self.klas_2 = klas_2

        # Run the step normally
        step: float = self.simtime[i]
        stepsize: float = self.timesteps[i]

        # Set KLA values for both WWTPs
        self.reactor1_1.kla, self.reactor2_1.kla, self.reactor3_1.kla, self.reactor4_1.kla, self.reactor5_1.kla = self.klas_1
        self.reactor1_2.kla, self.reactor2_2.kla, self.reactor3_2.kla, self.reactor4_2.kla, self.reactor5_2.kla = self.klas_2

        # Get influent data that is smaller than and closest to current time step
        y_in_timestep = self.y_in[np.where(self.data_time <= step)[0][-1], :]

        # Each WWTP gets the same influent (they are completely independent)
        y_in_wwtp1 = y_in_timestep.copy()
        y_in_wwtp2 = y_in_timestep.copy()

        # Calculate IQI only once (for the original influent)
        iqi = self.performance.iqi(y_in_timestep)[0]
        self.iqi_all[i] = iqi

        # WWTP 1 processing
        self.y_in1_1 = self.combiner1.output(y_in_wwtp1, self.ys_out_1, self.y_out5_r_1)
        self.y_out1_1 = self.reactor1_1.output(stepsize, step, self.y_in1_1)
        self.y_out2_1 = self.reactor2_1.output(stepsize, step, self.y_out1_1)
        self.y_out3_1 = self.reactor3_1.output(stepsize, step, self.y_out2_1)
        self.y_out4_1 = self.reactor4_1.output(stepsize, step, self.y_out3_1)
        self.y_out5_1 = self.reactor5_1.output(stepsize, step, self.y_out4_1)

        self.ys_in_1, self.y_out5_r_1 = self.splitter1.output(
            self.y_out5_1, (max(self.y_out5_1[14] - self.qintr, 0.0), float(self.qintr))
        )

        self.ys_out_1, _, self.ys_eff_1, self.sludge_height_1, self.ys_tss_internal_1 = self.settler1.output(
            stepsize, step, self.ys_in_1
        )

        # WWTP 2 processing
        self.y_in1_2 = self.combiner2.output(y_in_wwtp2, self.ys_out_2, self.y_out5_r_2)
        self.y_out1_2 = self.reactor1_2.output(stepsize, step, self.y_in1_2)
        self.y_out2_2 = self.reactor2_2.output(stepsize, step, self.y_out1_2)
        self.y_out3_2 = self.reactor3_2.output(stepsize, step, self.y_out2_2)
        self.y_out4_2 = self.reactor4_2.output(stepsize, step, self.y_out3_2)
        self.y_out5_2 = self.reactor5_2.output(stepsize, step, self.y_out4_2)

        self.ys_in_2, self.y_out5_r_2 = self.splitter2.output(
            self.y_out5_2, (max(self.y_out5_2[14] - self.qintr, 0.0), float(self.qintr))
        )

        self.ys_out_2, _, self.ys_eff_2, self.sludge_height_2, self.ys_tss_internal_2 = self.settler2.output(
            stepsize, step, self.ys_in_2
        )

        # Calculate EQI for both WWTPs separately
        eqi_1 = self.performance.eqi(self.ys_eff_1)[0]
        eqi_2 = self.performance.eqi(self.ys_eff_2)[0]
        
        # Store average EQI (or could be sum, depending on requirements)
        self.eqi_all[i] = (eqi_1 + eqi_2) / 2.0

        # Calculate energy consumption for both WWTPs
        import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init
        import bsm2_python.bsm2.init.plantperformanceinit_bsm1 as pp_init
        
        # Calculate energy for each WWTP separately and sum them
        vol1 = np.array([
            self.reactor1_1.volume,
            self.reactor2_1.volume,
            self.reactor3_1.volume,
            self.reactor4_1.volume,
            self.reactor5_1.volume,
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
        ae1 = self.performance.aerationenergy_step(self.klas_1, vol1[0:5], sosat)
        ae2 = self.performance.aerationenergy_step(self.klas_2, vol2[0:5], sosat)
        self.ae = ae1 + ae2
        
        me1 = self.performance.mixingenergy_step(self.klas_1, vol1)
        me2 = self.performance.mixingenergy_step(self.klas_2, vol2)
        self.me = me1 + me2
        
        # Pumping energy calculations
        import bsm2_python.bsm2.init.plantperformanceinit_bsm1 as pp_init
        flows1 = np.array([y_in_wwtp1[14], asm1init.QR, asm1init.QW])
        flows2 = np.array([y_in_wwtp2[14], asm1init.QR, asm1init.QW])
        pe1 = self.performance.pumpingenergy_step(flows1, pp_init.PP_PAR[10:13])
        pe2 = self.performance.pumpingenergy_step(flows2, pp_init.PP_PAR[10:13])
        self.pe = pe1 + pe2

        # For the base class compatibility, set ys_eff to WWTP 1 effluent by default
        # Users can access both effluents via ys_eff_1 and ys_eff_2
        self.ys_eff = self.ys_eff_1
        self.sludge_height = self.sludge_height_1
        self.ys_tss_internal = self.ys_tss_internal_1