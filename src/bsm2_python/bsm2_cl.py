import csv
import os

import numpy as np

from bsm2_python.bsm2 import aerationcontrol
from bsm2_python.bsm2.init import aerationcontrolinit
from bsm2_python.bsm2.init import asm1init_bsm2 as asm1init
from bsm2_python.bsm2_base import BSM2Base
from bsm2_python.log import logger

path_name = os.path.dirname(__file__)


class BSM2CL(BSM2Base):
    def __init__(
        self,
        data_in=None,
        timestep=1 / 60 / 24,
        endtime=None,
        evaltime=None,
        use_noise=1,
        noise_file=None,
        noise_seed=1,
        *,
        tempmodel=False,
        activate=False,
    ):
        """
        Creates a BSM2CL object.

        Parameters
        ----------
        data_in : np.ndarray, optional
            Influent data. Has to be a 2D array. First column is time in days, the rest are 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states)
            If not provided, the influent data from BSM2 is used
        timestep : float, optional
            Timestep for the simulation in days. If not provided, the timestep is set to 1 minute.
            Please note: due to sensor sensitivity, the timestep should not be larger than 1 minute.
        endtime : float, optional
            Endtime for the simulation in days. If not provided, the endtime is the last time step in the influent data
        use_noise : int, optional
            If 0, no noise is added to the sensor data.
            If 1, a noise file is used to add noise to the sensor data.
                  If so, a noise_file has to be provided. Needs to have at least 2 columns: time and noise data
            If 2, a random number generator is used to add noise to the sensor data. Seed is used from noise_seed.
            Default is 1
        noise_in : str, optional
            Noise data. Needs to be provided if use_noise is 1. If not provided, the default noise file is used
        noise_seed : int, optional
            Seed for the random number generator. Default is 1
        tempmodel : bool, optional
            If True, the temperature model dependencies are activated. Default is False
        activate : bool, optional
            If True, the dummy states are activated. Default is False
        """
        if timestep is not None and timestep > 1 / 60 / 24:
            logger.warning(
                'Timestep should not be larger than 1 minute due to sensor sensitivity. \
                           Will continue with provided timestep, but most probably fail.'
            )

        super().__init__(
            data_in=data_in,
            timestep=timestep,
            endtime=endtime,
            evaltime=evaltime,
            tempmodel=tempmodel,
            activate=activate,
        )

        self.so4_sensor = aerationcontrol.OxygenSensor(
            aerationcontrolinit.MIN_SO4,
            aerationcontrolinit.MAX_SO4,
            aerationcontrolinit.T_SO4,
            aerationcontrolinit.STD_SO4,
        )
        self.aerationcontrol4 = aerationcontrol.PIAeration(
            aerationcontrolinit.KLA4_MIN,
            aerationcontrolinit.KLA4_MAX,
            aerationcontrolinit.KSO4,
            aerationcontrolinit.TISO4,
            aerationcontrolinit.TTSO4,
            aerationcontrolinit.SO4REF,
            aerationcontrolinit.KLA4OFFSET,
            aerationcontrolinit.SO4INTSTATE,
            aerationcontrolinit.SO4AWSTATE,
            aerationcontrolinit.KLA4_LIM,
            aerationcontrolinit.KLA4_CALC,
            use_antiwindup=aerationcontrolinit.USEANTIWINDUPSO4,
        )

        self.kla4_actuator = aerationcontrol.KLaActuator(aerationcontrolinit.T_KLA4)

        if use_noise == 0:
            self.noise_so4 = np.zeros(2)
            self.noise_timestep = np.array((0, self.endtime))
        elif use_noise == 1:
            if noise_file is None:
                noise_file = path_name + '/data/sensornoise.csv'
            with open(noise_file, encoding='utf-8-sig') as f:
                noise_data = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)
            if noise_data[-1, 0] < self.endtime:
                err = 'Noise file does not cover the whole simulation time.\n \
                    Please provide a valid noise file.'
                raise ValueError(err)
            noise_shape_criteria = 2
            if noise_data.shape[1] < noise_shape_criteria:
                err = 'Noise file needs to have at least 2 columns: time and noise data'
                raise ValueError(err)
            self.noise_so4 = noise_data[:, 1]
            self.noise_timestep = noise_data[:, 0]
            del noise_data

        if timestep is None:
            # calculate difference between each time step in data_in
            self.simtime = self.noise_timestep
            self.timestep = np.diff(
                self.noise_timestep, append=(2 * self.noise_timestep[-1,] - self.noise_timestep[-2,])
            )
        else:
            self.simtime = np.arange(0, self.data_in[-1, 0], timestep)
            self.timestep = timestep * np.ones(len(self.simtime))

        self.simtime = self.simtime[self.simtime <= self.endtime]

        rng_mode = 2
        if use_noise in {0, 1}:
            pass
        elif use_noise == rng_mode:
            np.random.seed(noise_seed)
            # create random noise array with mean 0 and variance 1
            self.noise_so4 = np.random.normal(0, 1, len(self.simtime))
            self.noise_timestep = np.arange(0, self.endtime, self.timestep)
        else:
            err = 'use_noise has to be 0, 1 or 2'
            raise ValueError(err)

        self.data_time = self.data_in[:, 0]
        # self.simtime = np.arange(0, self.endtime, self.timestep)

        self.timestep_integration = np.round(self.timestep * 24 * 60)  # step of integration in min
        self.control = np.round(
            self.timestep * 24 * 60
        )  # step of aeration self.control in min, should be equal or bigger than timestep_integration
        self.transferfunction = 15  # interval for transferfunction in min
        self.max_transfer_per_control = int(np.max(self.transferfunction / self.control, axis=0))

        self.numberstep = 1
        self.controlnumber = 1

        self.kla4 = np.zeros(self.max_transfer_per_control + 1)
        self.kla4[self.max_transfer_per_control - 1] = aerationcontrolinit.KLA4_INIT  # for first step

        self.so4 = np.zeros(self.max_transfer_per_control + 1)
        self.so4[self.max_transfer_per_control - 1] = asm1init.YINIT4[7]  # for first step

        self.kla4_a = aerationcontrolinit.KLA4_INIT
        self.kla3_a = aerationcontrolinit.KLA3GAIN * self.kla4_a
        self.kla5_a = aerationcontrolinit.KLA5GAIN * self.kla4_a

        self.y_in_all = np.zeros((len(self.simtime), 21))
        self.y_eff_all = np.zeros((len(self.simtime), 21))
        self.y_in_bp_all = np.zeros((len(self.simtime), 21))
        self.to_primary_all = np.zeros((len(self.simtime), 21))
        self.prim_in_all = np.zeros((len(self.simtime), 21))
        self.qpass_plant_all = np.zeros((len(self.simtime), 21))
        self.qpassplant_to_as_all = np.zeros((len(self.simtime), 21))
        self.qpassAS_all = np.zeros((len(self.simtime), 21))
        self.to_as_all = np.zeros((len(self.simtime), 21))
        self.feed_settler_all = np.zeros((len(self.simtime), 21))
        self.qthick2AS_all = np.zeros((len(self.simtime), 21))
        self.qthick2prim_all = np.zeros((len(self.simtime), 21))
        self.qstorage2AS_all = np.zeros((len(self.simtime), 21))
        self.qstorage2prim_all = np.zeros((len(self.simtime), 21))
        self.sludge_all = np.zeros((len(self.simtime), 21))
        self.iqi_all = np.zeros(len(self.simtime))
        self.eqi_all = np.zeros(len(self.simtime))
        self.oci_all = np.zeros(len(self.simtime))
        self.oci_factors_all = np.zeros((len(self.simtime), 8))
        self.violation_all = np.zeros(len(self.simtime))

    def step(self, i: int, so4ref: float | None = None):
        """
        Simulates one time step of the BSM2 model.

        Parameters
        ----------
        i : int
            Index of the current time step
        """
        if so4ref is None:
            self.aerationcontrol4.soref = aerationcontrolinit.SO4REF
        else:
            self.aerationcontrol4.soref = so4ref

        self.klas = np.array([0, 0, self.kla3_a, self.kla4_a, self.kla5_a])
        step: float = self.simtime[i]

        if (self.numberstep - 1) % (int(self.control[i] / self.timestep_integration[i])) == 0:
            # get index of noise that is smaller than and closest to current time step within a small tolerance
            idx_noise = int(np.where(self.noise_timestep - 1e-7 <= step)[0][-1])

            self.so4[self.max_transfer_per_control] = self.y_out4[7]

            so4_meas = self.so4_sensor.measure_so(
                self.so4, step, self.controlnumber, self.noise_so4[idx_noise], self.transferfunction, self.control[i]
            )
            kla4_ = self.aerationcontrol4.output(so4_meas, step, self.timestep[i])
            self.kla4[self.max_transfer_per_control] = kla4_
            self.kla4_a = self.kla4_actuator.real_actuator(
                self.kla4, step, self.controlnumber, self.transferfunction, self.control[i]
            )
            self.kla3_a = aerationcontrolinit.KLA3GAIN * self.kla4_a
            self.kla5_a = aerationcontrolinit.KLA5GAIN * self.kla4_a

            # for next step:
            self.so4[0 : self.max_transfer_per_control] = self.so4[1 : (self.max_transfer_per_control + 1)]
            self.kla4[0 : self.max_transfer_per_control] = self.kla4[1 : (self.max_transfer_per_control + 1)]

            self.controlnumber += 1

        super().step(i)
