"""This represents the base model of the BSM1 group of classes.

Model file for bsm1 model with 5 asm1-reactors and a secondary clarifier
in dynamic simulation without any controllers.
"""

import os

import numpy as np
from tqdm import tqdm

import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init
import bsm2_python.bsm2.init.plantperformanceinit_bsm1 as pp_init
import bsm2_python.bsm2.init.reginit_bsm1 as reginit
import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit
from bsm2_python.bsm2.asm1_bsm2 import ASM1Reactor
from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter
from bsm2_python.bsm2.plantperformance import PlantPerformance
from bsm2_python.bsm2.settler1d_bsm2 import Settler
from bsm2_python.bsm_base import BSMBase

path_name = os.path.dirname(__file__)

SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = np.arange(21)


class BSM1Base(BSMBase):
    """Creates a BSM1Base object. It is a base class and resembles the BSM1 model without any controllers.

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
    tempmodel : bool (optional)
        If `True`, the temperature model dependencies are activated.
        Default is `False`.
    activate : bool (optional)
        If `True`, the dummy states are activated.
        Default is `False`.
    data_out : str (optional)
        Path to the output data file. <br>
        If not provided, no output data is saved.
    """

    def __init__(
        self,
        data_in: np.ndarray | str | None = None,
        timestep: float | None = None,
        endtime: float | None = None,
        evaltime: int | np.ndarray | None = None,
        *,
        tempmodel: bool = False,
        activate: bool = False,
        data_out: str | None = None,
    ):
        super().__init__(
            data_in=data_in,
            timestep=timestep,
            endtime=endtime,
            evaltime=evaltime,
            data_out=data_out,
        )

        self.combiner = Combiner()
        self.reactor1 = ASM1Reactor(
            asm1init.KLA1,
            asm1init.VOL1,
            asm1init.YINIT1,
            asm1init.PAR1,
            asm1init.CARB1,
            asm1init.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor2 = ASM1Reactor(
            asm1init.KLA2,
            asm1init.VOL2,
            asm1init.YINIT2,
            asm1init.PAR2,
            asm1init.CARB2,
            asm1init.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor3 = ASM1Reactor(
            asm1init.KLA3,
            asm1init.VOL3,
            asm1init.YINIT3,
            asm1init.PAR3,
            asm1init.CARB3,
            asm1init.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor4 = ASM1Reactor(
            asm1init.KLA4,
            asm1init.VOL4,
            asm1init.YINIT4,
            asm1init.PAR4,
            asm1init.CARB4,
            asm1init.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor5 = ASM1Reactor(
            asm1init.KLA5,
            asm1init.VOL5,
            asm1init.YINIT5,
            asm1init.PAR5,
            asm1init.CARB5,
            asm1init.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.reactor5 = ASM1Reactor(
            asm1init.KLA5,
            asm1init.VOL5,
            asm1init.YINIT5,
            asm1init.PAR5,
            asm1init.CARB5,
            asm1init.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.splitter = Splitter()
        self.settler = Settler(
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

        self.performance = PlantPerformance(pp_init.PP_PAR)

        self.y_in = self.data_in[:, 1:]

        self.y_in1 = np.zeros(21)
        self.y_out1 = np.zeros(21)
        self.y_out2 = np.zeros(21)
        self.y_out3 = np.zeros(21)
        self.y_out4 = np.zeros(21)
        self.y_out5 = np.zeros(21)
        self.y_out5_r = np.zeros(21)
        self.ys_in = np.zeros(21)
        self.ys_out = np.zeros(21)
        self.ys_eff = np.zeros(21)
        self.qintr = asm1init.QINTR
        self.sludge_height = 0

        self.y_in_all = np.zeros((len(self.simtime), 21))
        self.y_in1_all = np.zeros((len(self.simtime), 21))
        self.y_out1_all = np.zeros((len(self.simtime), 21))
        self.y_out2_all = np.zeros((len(self.simtime), 21))
        self.y_out3_all = np.zeros((len(self.simtime), 21))
        self.y_out4_all = np.zeros((len(self.simtime), 21))
        self.y_out5_all = np.zeros((len(self.simtime), 21))
        self.y_out5_r_all = np.zeros((len(self.simtime), 21))
        self.ys_in_all = np.zeros((len(self.simtime), 21))
        self.ys_out_all = np.zeros((len(self.simtime), 21))
        self.ys_eff_all = np.zeros((len(self.simtime), 21))
        self.sludge_height_all = np.zeros(len(self.simtime))

        self.ae = 0
        self.pe = 0
        self.me = 0
        self.iqi_all = np.zeros(len(self.simtime))
        self.eqi_all = np.zeros(len(self.simtime))
        self.perf_factors_all = np.zeros((len(self.simtime), 3))
        self.violation_all = np.zeros(len(self.simtime))

        self.klas = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])

    def step(self, i: int, *args, **kwargs):
        """Simulates one time step of the BSM1 model.

        Parameters
        ----------
        i : int
            Index of the current time step [-].
        """

        # timestep = timesteps[i]
        step: float = self.simtime[i]
        stepsize: float = self.timesteps[i]

        self.reactor1.kla, self.reactor2.kla, self.reactor3.kla, self.reactor4.kla, self.reactor5.kla = self.klas

        # get influent data that is smaller than and closest to current time step
        y_in_timestep = self.y_in[np.where(self.data_time <= step)[0][-1], :]

        iqi = self.performance.iqi(y_in_timestep)[0]
        self.iqi_all[i] = iqi

        self.y_in1 = self.combiner.output(y_in_timestep, self.ys_out, self.y_out5_r)

        self.y_out1 = self.reactor1.output(stepsize, step, self.y_in1)
        self.y_out2 = self.reactor2.output(stepsize, step, self.y_out1)
        self.y_out3 = self.reactor3.output(stepsize, step, self.y_out2)
        self.y_out4 = self.reactor4.output(stepsize, step, self.y_out3)
        self.y_out5 = self.reactor5.output(stepsize, step, self.y_out4)

        self.ys_in, self.y_out5_r = self.splitter.output(self.y_out5, (self.y_out5[14] - self.qintr, self.qintr))

        self.ys_out, _, self.ys_eff, self.sludge_height, self.ys_tss_internal = self.settler.output(
            stepsize, step, self.ys_in
        )

        eqi = self.performance.eqi(self.ys_eff)[0]
        self.eqi_all[i] = eqi

        vol = np.array(
            [
                self.reactor1.volume,
                self.reactor2.volume,
                self.reactor3.volume,
                self.reactor4.volume,
                self.reactor5.volume,
            ]
        )
        sosat = np.array([asm1init.SOSAT1, asm1init.SOSAT2, asm1init.SOSAT3, asm1init.SOSAT4, asm1init.SOSAT5])
        self.ae = self.performance.aerationenergy_step(self.klas, vol[0:5], sosat)
        flows = np.array([self.qintr, asm1init.QR, asm1init.QW])
        self.pe = self.performance.pumpingenergy_step(flows, pp_init.PP_PAR[10:13])
        self.me = self.performance.mixingenergy_step(self.klas, vol)

        # These values are used to calculate the exact performance values at the end of the simulation
        self.perf_factors_all[i] = [
            self.pe * 24,
            self.ae * 24,
            self.me * 24,
        ]

        # store the results
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
        self.violation_all[i] = self.performance.violation_step(self.ys_eff[SNH], 4)[0]

    def stabilize(self, atol: float = 1e-3):
        """Stabilizes the plant.

        Parameters
        ----------
        atol : float (optional)
            Absolute tolerance for the stabilization. <br>
            Default is 1e-3.

        Returns
        -------
        stable : bool
            Returns `True` if plant is stabilized after iterations.
        """
        # every element of check_vars must be an equally-sized array as attribute of the class
        check_vars = [
            'ys_eff',
            'ys_in',
            'y_out1',
            'y_out2',
            'y_out3',
            'y_out4',
            'y_out5',
        ]
        stable = super()._stabilize(check_vars=check_vars, atol=atol)
        return stable

    def simulate(self, *, plot: bool = True):
        """Simulates the plant."""
        for i, _ in enumerate(tqdm(self.simtime)):
            self.step(i)

            if i == 0:
                self.evaluator.add_new_data('iqi', 'iqi')
                self.evaluator.add_new_data('eqi', 'eqi')
            if self.evaltime[0] <= self.simtime[i] <= self.evaltime[1]:
                self.evaluator.update_data('iqi', self.iqi_all[i], self.simtime[i])
                self.evaluator.update_data('eqi', self.eqi_all[i], self.simtime[i])
        self.finish_evaluation(plot=plot)

    def finish_evaluation(self, *, plot=True):
        """Finishes the evaluation of the plant.

        Parameters
        ----------
        plot : bool (optional)
            If `True`, the data is plotted. <br>
            Default is `True`.
        """

        if plot:
            self.evaluator.plot_data()
        self.evaluator.export_data()

    def get_violations(self, comp: tuple = ('SNH',), lim: tuple = (4,)):
        """Returns the violations of the given components within the evaluation interval.

        Parameters
        ----------
        comp : tuple(str) (optional)
            List of components to check for violations. <br>
            Default is ('SNH').
        lim : tuple(float) (optional)
            List of limits for the components. <br>
            Default is (4).

        Returns
        -------
        violations : dict{'comp': float}
            Dictionary with the components as keys and the violation time [d].
        """

        comp_dict = {
            'SI': 0,
            'SS': 1,
            'XI': 2,
            'XS': 3,
            'XBH': 4,
            'XBA': 5,
            'XP': 6,
            'SO': 7,
            'SNO': 8,
            'SNH': 9,
            'SND': 10,
            'XND': 11,
            'SALK': 12,
            'TSS': 13,
            'Q': 14,
            'TEMP': 15,
            'SD1': 16,
            'SD2': 17,
            'SD3': 18,
            'XD4': 19,
            'XD5': 20,
        }
        if len(comp) != len(lim):
            raise ValueError('The length of comp and lim has to be the same.')
        for c in comp:
            if c not in comp_dict:
                err = f'The component {c} is not in the list of components.'
                raise ValueError(err)
        comps = [comp_dict[c] for c in comp]

        violations = {}
        for i in range(len(comp)):
            comp_eff = self.ys_eff_all[self.eval_idx[0] : self.eval_idx[1], comps[i]]
            violations[comp[i]] = np.sum(self.performance.violation_step(comp_eff, lim[i])) / 60 / 24
        return violations

    def get_final_performance(self):
        """Returns the final performance values for evaluation period.

        Returns
        -------
        iqi_eval : float
            Final iqi value [kg ⋅ d⁻¹].
        eqi_eval : float
            Final eqi value [kg ⋅ d⁻¹].
        mixingenergy : float
            Mixing energy [kWh ⋅ d⁻¹].
        pumpingenergy : float
            Pumping energy [kWh ⋅ d⁻¹].
        aerationenergy : float
            Aeration energy [kWh ⋅ d⁻¹].
        """

        # calculate the final performance values

        num_eval_timesteps = self.eval_idx[1] - self.eval_idx[0]

        iqi_eval = np.sum(self.iqi_all[self.eval_idx[0] : self.eval_idx[1]]) / num_eval_timesteps
        eqi_eval = np.sum(self.eqi_all[self.eval_idx[0] : self.eval_idx[1]]) / num_eval_timesteps

        perf_factors_eval = self.perf_factors_all[self.eval_idx[0] : self.eval_idx[1]]
        pumpingenergy = np.sum(perf_factors_eval[:, 0]) / num_eval_timesteps
        aerationenergy = np.sum(perf_factors_eval[:, 1]) / num_eval_timesteps
        mixingenergy = np.sum(perf_factors_eval[:, 2]) / num_eval_timesteps

        return (
            iqi_eval,
            eqi_eval,
            mixingenergy,
            pumpingenergy,
            aerationenergy,
        )
