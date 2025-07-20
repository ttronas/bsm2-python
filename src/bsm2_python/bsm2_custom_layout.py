"""This represents a custom real world wastewater treatment plant layout (N. Hvala et al. 2018) with use of the
BSM2 group of classes.

- BSM2 base: Primary clarifier, 4 asm1 reactors, secondary settler, primary sludge thickener,
primary sludge centrifuge (dewatering), waste sludge thickener, waste sludge centrifuge (dewatering),
adm1 fermenter, secondary sludge thickener, centrifuge (dewatering) and sludge drying (dewatering)
in dynamic simulation (with dissolved oxygen (DO) controllers).
"""

import csv
import os

import numpy as np
from tqdm import tqdm

# import bsm2_python.bsm2.init.dewateringinit_bsm2 as dewateringinit  # not used
# import bsm2_python.bsm2.init.storageinit_bsm2 as storageinit  # not used
# import bsm2_python.bsm2.init.thickenerinit_bsm2 as thickenerinit  # not used
import bsm2_python.bsm2.init.adm1init_bsm2 as adm1init
import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
import bsm2_python.bsm2.init.plantperformanceinit_bsm2 as pp_init
import bsm2_python.bsm2.init.primclarinit_bsm2 as primclarinit
import bsm2_python.bsm2.init.reginit_bsm2 as reginit
import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit
import bsm2_python.bsm2_custom_layoutinit as custominit

# from bsm2_python.bsm2.storage_bsm2 import Storage  # not used
from bsm2_python.bsm2.adm1_bsm2 import ADM1Reactor
from bsm2_python.bsm2.aerationcontrol import PID, Actuator, Sensor
from bsm2_python.bsm2.asm1_bsm2 import ASM1Reactor
from bsm2_python.bsm2.dewatering_bsm2 import Dewatering
from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter
from bsm2_python.bsm2.init import aerationcontrolinit
from bsm2_python.bsm2.plantperformance import PlantPerformance
from bsm2_python.bsm2.primclar_bsm2 import PrimaryClarifier
from bsm2_python.bsm2.settler1d_bsm2 import Settler
from bsm2_python.bsm2.thickener_bsm2 import Thickener
from bsm2_python.bsm_base import BSMBase
from bsm2_python.log import logger

path_name = os.path.dirname(__file__)

SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = np.arange(21)


class BSM2CustomLayout(BSMBase):
    """Creates the customized wwtp object.

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
    use_noise : int (optional)
        - 0: No noise is added to the sensor data.
        - 1: A noise file is used to add noise to the sensor data.
             If so, a noise_file has to be provided. Needs to have at least 2 columns: time and noise data
        - 2: A random number generator is used to add noise to the sensor data. Seed is used from noise_seed. <br>
             Default is 1.
    noise_file : str (optional)
        Noise data. Needs to be provided if use_noise is 1.
        If not provided, the default noise file is used.
    noise_seed : int (optional)
        Seed for the random number generator.
        Default is 1.
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
        use_noise: int = 1,
        noise_file: str | None = None,
        noise_seed: int = 1,
        data_out: str | None = None,
        *,
        tempmodel: bool = False,
        activate: bool = False,
    ):
        logger.info(msg='Initialize bsm2_custom\n')

        if timestep is not None and timestep > 1 / 60 / 24:
            logger.warning("""Timestep should not be larger than 1 minute due to sensor sensitivity.
                      Will continue with provided timestep, but most probably fail.
            """)

        super().__init__(
            data_in=data_in,
            timestep=timestep,
            endtime=endtime,
            evaltime=evaltime,
            data_out=data_out,
        )

        # wwtp objects
        self.combiner_primclar = Combiner()

        self.primclar = PrimaryClarifier(
            custominit.VOL_PRIM_CLAR,
            primclarinit.YINIT1,
            primclarinit.PAR_P,
            asm1init.PAR1,
            primclarinit.XVECTOR_P,
            tempmodel=tempmodel,
            activate=activate,
        )

        self.combiner_ext_recirc = Combiner()
        self.asm1_reactor1 = ASM1Reactor(
            custominit.KLA_ANAEROBIC,
            custominit.VOL_REACTOR1,
            asm1init.YINIT1,
            asm1init.PAR1,
            custominit.CARB1,
            custominit.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.combiner_int_recirc = Combiner()
        self.asm1_reactor2 = ASM1Reactor(
            custominit.KLA_ANOXIC,
            custominit.VOL_REACTOR2,
            asm1init.YINIT2,
            asm1init.PAR2,
            custominit.CARB2,
            custominit.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.asm1_reactor3 = ASM1Reactor(
            custominit.KLA_AEROBIC,
            custominit.VOL_REACTOR3,
            asm1init.YINIT3,
            asm1init.PAR3,
            custominit.CARB3,
            custominit.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )
        self.splitter_int_recirc = Splitter()
        self.asm1_reactor4 = ASM1Reactor(
            custominit.KLA_AEROBIC,
            custominit.VOL_REACTOR4,
            asm1init.YINIT4,
            asm1init.PAR4,
            custominit.CARB4,
            custominit.CARBONSOURCECONC,
            tempmodel=tempmodel,
            activate=activate,
        )

        self.settler = Settler(
            custominit.DIM_SETTLER,
            settler1dinit.LAYER,
            custominit.QR,
            custominit.QW,
            settler1dinit.settlerinit,
            settler1dinit.SETTLERPAR,
            asm1init.PAR1,
            tempmodel,
            settler1dinit.MODELTYPE,
        )

        self.prim_thickener = Thickener(custominit.PRIM_THICKENERPAR)
        self.prim_centrifuge = Dewatering(custominit.PRIM_CENTRIFUGEPAR)

        self.waste_thickener = Thickener(custominit.WASTE_THICKENERPAR)
        self.waste_centrifuge = Dewatering(custominit.WASTE_CENTRIFUGEPAR)

        self.combiner_adm1 = Combiner()

        self.adm1_reactor = ADM1Reactor(
            adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, custominit.DIM_AD
        )

        self.sec_thickener = Thickener(custominit.SEC_THICKENERPAR)
        self.dewatering_centrifuge = Dewatering(custominit.DEWATERING_CENTRIFUGEPAR)
        self.sludge_drying = Dewatering(custominit.SLUDGE_DRYINGPAR)

        self.combiner_recirc_water = Combiner()

        # wwtp streams
        self.y_in = self.data_in[:, 1:]

        self.ysett_tss_internal = np.zeros(settler1dinit.LAYER[1])
        self.yad_out = np.zeros(51)
        self.yrecirc_water = np.zeros(21)
        (
            self.yas_r1_out,
            self.yas_r2_out,
            self.yas_r3_out,
            self.yas_r4_out,
            self.ysett_ext_recirc,
            self.ysett_waste,
            self.ysett_of,
            self.yprim_clar_uf,
            self.yprim_clar_of,
            self.yprim_clar_internal,
            self.yprim_thic_uf,
            self.yprim_thic_of,
            self.ywaste_thic_uf,
            self.ywaste_thic_of,
            self.ysec_thic_uf,
            self.ysec_thic_of,
            self.yad_in,
            self.yad_out2,
            self.yprim_centr_uf,
            self.yprim_centr_of,
            self.ywaste_centr_uf,
            self.ywaste_centr_of,
            self.ydw_centr_uf,
            self.ydw_centr_of,
            self.ysl_drying_uf,
            self.ysl_drying_of,
            self.yint_recirc,
            self.y_eff,
        ) = self._create_copies(self.y_in[0], 28)

        self.qintr = custominit.INT_RECIRC
        self.yint_recirc[14] = self.qintr

        self.yst_vol = 0  # does not exist, but necessary for performance.tss_mass_bsm2 function
        self.yst_out = np.zeros(21)  # does not exist, but necessary for performance.tss_mass_bsm2 function
        self.y_out5 = np.zeros(21)  # does not exist, but necessary for performance.tss_mass_bsm2 function

        # variables for data collection
        self.y_in_all = np.zeros((len(self.simtime), 21))
        self.y_eff_all = np.zeros((len(self.simtime), 21))
        self.prim_clar_in_all = np.zeros((len(self.simtime), 21))
        self.feed_settler_all = np.zeros((len(self.simtime), 21))
        self.sludge_all = np.zeros((len(self.simtime), 21))

        self.yas_r1_out_all = np.zeros((len(self.simtime), 21))
        self.yas_r2_out_all = np.zeros((len(self.simtime), 21))
        self.yas_r3_out_all = np.zeros((len(self.simtime), 21))
        self.yas_r4_out_all = np.zeros((len(self.simtime), 21))
        self.ysett_ext_recirc_all = np.zeros((len(self.simtime), 21))
        self.ysett_waste_all = np.zeros((len(self.simtime), 21))
        self.ysett_of_all = np.zeros((len(self.simtime), 21))
        self.ysett_tss_internal_all = np.zeros((len(self.simtime), settler1dinit.LAYER[1]))
        self.yprim_clar_uf_all = np.zeros((len(self.simtime), 21))
        self.yprim_clar_of_all = np.zeros((len(self.simtime), 21))
        self.yprim_clar_internal_all = np.zeros((len(self.simtime), 21))
        self.yprim_thic_uf_all = np.zeros((len(self.simtime), 21))
        self.yprim_thic_of_all = np.zeros((len(self.simtime), 21))
        self.ywaste_thic_uf_all = np.zeros((len(self.simtime), 21))
        self.ywaste_thic_of_all = np.zeros((len(self.simtime), 21))
        self.ysec_thic_uf_all = np.zeros((len(self.simtime), 21))
        self.ysec_thic_of_all = np.zeros((len(self.simtime), 21))
        self.yad_out2_all = np.zeros((len(self.simtime), 21))
        self.yad_out_all = np.zeros((len(self.simtime), 51))
        self.yprim_centr_uf_all = np.zeros((len(self.simtime), 21))
        self.yprim_centr_of_all = np.zeros((len(self.simtime), 21))
        self.ywaste_centr_uf_all = np.zeros((len(self.simtime), 21))
        self.ywaste_centr_of_all = np.zeros((len(self.simtime), 21))
        self.ydw_centr_uf_all = np.zeros((len(self.simtime), 21))
        self.ydw_centr_of_all = np.zeros((len(self.simtime), 21))
        self.ysl_drying_uf_all = np.zeros((len(self.simtime), 21))
        self.ysl_drying_of_all = np.zeros((len(self.simtime), 21))

        # evaluation object
        self.performance = PlantPerformance(pp_init.PP_PAR)

        # variables for evaluation
        self.klas = np.array(
            [custominit.KLA_ANAEROBIC, custominit.KLA_ANOXIC, custominit.KLA_AEROBIC, custominit.KLA_AEROBIC]
        )

        self.sludge_height = 0

        self.ae = 0
        self.pe = 0
        self.me = 0
        self.heat_demand = 0
        self.iqi_all = np.zeros(len(self.simtime))
        self.eqi_all = np.zeros(len(self.simtime))
        self.oci_all = np.zeros(len(self.simtime))
        self.perf_factors_all = np.zeros((len(self.simtime), 12))
        self.violation_all = np.zeros(len(self.simtime))
        self.adv_quants_eff_all = np.zeros((len(self.simtime), 7))

        # dissolved oxygen (DO) control
        num_sen = 1
        den_sen4 = [aerationcontrolinit.T_SO4**2, 2 * aerationcontrolinit.T_SO4, 1]
        self.so4_sensor = Sensor(
            num_sen, den_sen4, aerationcontrolinit.MIN_SO4, aerationcontrolinit.MAX_SO4, aerationcontrolinit.STD_SO4
        )
        self.pid4 = PID(**custominit.PID4_PARAMS)
        num_act = 1
        den_act4 = [aerationcontrolinit.T_KLA4**2, 2 * aerationcontrolinit.T_KLA4, 1]
        self.kla4_actuator = Actuator(num_act, den_act4)

        if use_noise == 0:
            self.noise_so4 = np.zeros(2)
            self.noise_timestep = np.array((0, self.endtime)).flatten()
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
            self.noise_so4 = noise_data[:, 1].flatten()
            self.noise_timestep = noise_data[:, 0].flatten()
            del noise_data

        if timestep is None:
            # calculate difference between each time step in data_in
            self.simtime = self.noise_timestep
            self.timesteps = np.diff(
                self.noise_timestep, append=(2 * self.noise_timestep[-1,] - self.noise_timestep[-2,])
            )
        else:
            self.simtime = np.arange(0, self.data_in[-1, 0], timestep)
            self.timesteps = timestep * np.ones(len(self.simtime))

        self.simtime = self.simtime[self.simtime <= self.endtime]

        rng_mode = 2  # random number generator mode
        if use_noise in {0, 1}:
            pass
        elif use_noise == rng_mode:
            np.random.seed(noise_seed)
            # create random noise array with mean 0 and variance 1
            self.noise_so4 = np.random.normal(0, 1, len(self.simtime)).flatten()
            self.noise_timestep = self.simtime
        else:
            err = 'use_noise has to be 0, 1 or 2'
            raise ValueError(err)

        self.data_time = self.data_in[:, 0]
        # self.simtime = np.arange(0, self.endtime, self.timestep)

        self.kla4_a = aerationcontrolinit.KLA4_INIT
        self.kla3_a = aerationcontrolinit.KLA3GAIN * self.kla4_a

    def step(self, i: int, so4ref: float | None = None, *args, **kwargs):
        """Simulates one time step of the BSM2 model.

        Parameters
        ----------
        i : int
            Index of the current time step [-].
        so4ref : float (optional)
            Setpoint for the dissolved oxygen concentration [g(O₂) ⋅ m⁻³] \n
            If not provided, the setpoint is set to aerationcontrolinit.SO4REF.
        """

        # disolved oxygen (DO) control
        if so4ref is None:
            self.pid4.setpoint = custominit.SO4REF
        else:
            self.pid4.setpoint = so4ref

        step: float = self.simtime[i]
        stepsize: float = self.timesteps[i]

        # get index of noise that is smaller than and closest to current time step within a small tolerance
        idx_noise = int(np.where(self.noise_timestep - 1e-7 <= step)[0][-1])

        sensor_signal = self.so4_sensor.output(self.yas_r4_out[SO], stepsize, self.noise_so4[idx_noise])
        control_signal = self.pid4.output(sensor_signal, stepsize)
        actuator_signal = self.kla4_actuator.output(control_signal, stepsize)
        self.kla4_a = actuator_signal
        self.kla3_a = aerationcontrolinit.KLA3GAIN * self.kla4_a

        # kla values from actuator
        self.klas = np.array([0, 0, self.kla3_a, self.kla4_a])
        # updates kla values for activated sludge reactors
        self.asm1_reactor1.kla, self.asm1_reactor2.kla, self.asm1_reactor3.kla, self.asm1_reactor4.kla = self.klas

        # wwtp simulation step
        # get influent data that is smaller than and closest to current time step
        y_in_timestep = self.y_in[np.where(self.data_time <= step)[0][-1], :]

        iqi = self.performance.iqi(y_in_timestep)[0]
        self.iqi_all[i] = iqi

        yprim_clar_in = self.combiner_primclar.output(y_in_timestep, self.yrecirc_water)
        self.yprim_clar_uf, self.yprim_clar_of, self.yprim_clar_internal = self.primclar.output(
            stepsize, step, yprim_clar_in
        )

        yas_in = self.combiner_ext_recirc.output(self.yprim_clar_of, self.ysett_ext_recirc)
        self.yas_r1_out = self.asm1_reactor1.output(stepsize, step, yas_in)
        yas_r2_in = self.combiner_int_recirc.output(self.yas_r1_out, self.yint_recirc)
        self.yas_r2_out = self.asm1_reactor2.output(stepsize, step, yas_r2_in)
        self.yas_r3_out = self.asm1_reactor3.output(stepsize, step, self.yas_r2_out)
        yas_r3_pass, self.yint_recirc = self.splitter_int_recirc.output(
            self.yas_r3_out, (max(self.yas_r3_out[14] - self.qintr, 0.0), float(self.qintr))
        )
        self.yas_r4_out = self.asm1_reactor4.output(stepsize, step, yas_r3_pass)

        self.ysett_ext_recirc, self.ysett_waste, self.ysett_of, _, self.ysett_tss_internal = self.settler.output(
            stepsize, step, self.yas_r4_out
        )
        self.y_eff = self.ysett_of

        eqi = self.performance.eqi(self.y_eff)[0]
        self.eqi_all[i] = eqi

        self.yprim_thic_uf, self.yprim_thic_of = self.prim_thickener.output(self.yprim_clar_uf)
        self.yprim_centr_uf, self.yprim_centr_of = self.prim_centrifuge.output(self.yprim_thic_uf)

        self.ywaste_thic_uf, self.ywaste_thic_of = self.waste_thickener.output(self.ysett_waste)
        self.ywaste_centr_uf, self.ywaste_centr_of = self.waste_centrifuge.output(self.ywaste_thic_uf)

        self.yad_in = self.combiner_adm1.output(self.yprim_centr_uf, self.ywaste_centr_uf)
        self.yad_out2, self.yad_out, _ = self.adm1_reactor.output(stepsize, step, self.yad_in, reginit.T_OP)

        self.ysec_thic_uf, self.ysec_thic_of = self.sec_thickener.output(self.yad_out2)
        self.ydw_centr_uf, self.ydw_centr_of = self.dewatering_centrifuge.output(self.ysec_thic_uf)
        self.ysl_drying_uf, self.ysl_drying_of = self.sludge_drying.output(self.ydw_centr_uf)

        self.yrecirc_water = self.combiner_recirc_water.output(
            self.yprim_thic_of,
            self.yprim_centr_of,
            self.ywaste_thic_of,
            self.ywaste_centr_of,
            self.ysec_thic_of,
            self.ydw_centr_of,
            self.ysl_drying_of,
        )

        # wwtp evaluation step
        vol = np.array(
            [
                self.asm1_reactor1.volume,
                self.asm1_reactor2.volume,
                self.asm1_reactor3.volume,
                self.asm1_reactor4.volume,
                0,
                self.adm1_reactor.volume_liq,
            ]
        )
        sosat = np.array([asm1init.SOSAT1, asm1init.SOSAT2, asm1init.SOSAT3, asm1init.SOSAT4])
        self.ae = self.performance.aerationenergy_step(self.klas, vol[0:4], sosat)
        flows = np.array(
            [
                self.qintr,
                custominit.QR,
                custominit.QW,
                self.yprim_clar_uf[14],
                self.yprim_thic_uf[14],
                self.ywaste_thic_uf[14],
                self.ysec_thic_uf[14],
                self.yprim_centr_uf[14],
                self.ywaste_centr_uf[14],
                self.ydw_centr_uf[14],
                self.ysl_drying_uf[14],
            ]
        )
        self.pe = self.performance.pumpingenergy_step(flows, custominit.PP_PAR[10:21])
        self.me = self.performance.mixingenergy_step(self.klas, vol, custominit.PP_PAR[21])

        tss_mass = self.performance.tss_mass_bsm2(
            self.yprim_clar_of,
            self.yprim_clar_uf,
            self.yprim_clar_internal,
            self.yas_r1_out,
            self.yas_r2_out,
            self.yas_r3_out,
            self.yas_r4_out,
            self.y_out5,
            self.ysett_tss_internal,
            self.yad_out,
            self.yst_out,
            self.yst_vol,
        )

        ysl_drying_uf_tss_flow = self.performance.tss_flow(self.ysl_drying_uf)
        y_eff_tss_flow = self.performance.tss_flow(self.y_eff)
        carb = custominit.CARB1 + custominit.CARB2 + custominit.CARB3 + custominit.CARB4
        added_carbon_mass = self.performance.added_carbon_mass(carb, custominit.CARBONSOURCECONC)
        self.heat_demand = self.performance.heat_demand_step(self.yad_in, reginit.T_OP)[0]
        ch4_prod, h2_prod, co2_prod, q_gas = self.performance.gas_production(self.yad_out, reginit.T_OP)

        # This calculates an approximate oci value for each time step,
        # neglecting changes in the tss mass inside the whole plant
        self.oci_all[i] = self.performance.oci(
            self.pe * 24,
            self.ae * 24,
            self.me * 24,
            ysl_drying_uf_tss_flow,
            added_carbon_mass,
            self.heat_demand * 24,
            ch4_prod,
        )

        # These values are used to calculate the exact performance values at the end of the simulation
        self.perf_factors_all[i, :12] = [
            self.pe * 24,
            self.ae * 24,
            self.me * 24,
            ysl_drying_uf_tss_flow,
            y_eff_tss_flow,
            tss_mass,
            added_carbon_mass,
            self.heat_demand * 24,
            ch4_prod,
            h2_prod,
            co2_prod,
            q_gas,
        ]

        self.adv_quants_eff = self.performance.advanced_quantities(self.y_eff)

        # data collection step
        self.adv_quants_eff_all[i] = np.concatenate(([self.y_eff[14]], self.adv_quants_eff.ravel()))
        self.y_in_all[i] = y_in_timestep
        self.y_eff_all[i] = self.y_eff
        self.prim_clar_in_all[i] = yprim_clar_in
        self.feed_settler_all[i] = self.yas_r4_out
        self.sludge_all[i] = self.ysl_drying_uf

        # data for calculation of final oci
        self.violation_all[i] = self.performance.violation_step(self.y_eff[SNH], 4)[0]
        self.yas_r1_out_all[i] = self.yas_r1_out
        self.yas_r2_out_all[i] = self.yas_r2_out
        self.yas_r3_out_all[i] = self.yas_r3_out
        self.yas_r4_out_all[i] = self.yas_r4_out
        self.ysett_ext_recirc_all[i] = self.ysett_ext_recirc
        self.ysett_waste_all[i] = self.ysett_waste
        self.ysett_of_all[i] = self.ysett_of
        self.ysett_tss_internal_all[i] = self.ysett_tss_internal
        self.yprim_clar_uf_all[i] = self.yprim_clar_uf
        self.yprim_clar_of_all[i] = self.yprim_clar_of
        self.yprim_clar_internal_all[i] = self.yprim_clar_internal
        self.yprim_thic_uf_all[i] = self.yprim_thic_uf
        self.yprim_thic_of_all[i] = self.yprim_thic_of
        self.ywaste_thic_uf_all[i] = self.ywaste_thic_uf
        self.ywaste_thic_of_all[i] = self.ywaste_thic_of
        self.ysec_thic_uf_all[i] = self.ysec_thic_uf
        self.ysec_thic_of_all[i] = self.ysec_thic_of
        self.yad_out2_all[i] = self.yad_out2
        self.yad_out_all[i] = self.yad_out
        self.yprim_centr_uf_all[i] = self.yprim_centr_uf
        self.yprim_centr_of_all[i] = self.yprim_centr_of
        self.ywaste_centr_uf_all[i] = self.ywaste_centr_uf
        self.ywaste_centr_of_all[i] = self.ywaste_centr_of
        self.ydw_centr_uf_all[i] = self.ydw_centr_uf
        self.ydw_centr_of_all[i] = self.ydw_centr_of
        self.ysl_drying_uf_all[i] = self.ysl_drying_uf
        self.ysl_drying_of_all[i] = self.ysl_drying_of

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
        check_vars = [
            'y_eff',
            'yas_r1_out',
            'yas_r2_out',
            'yas_r3_out',
            'yas_r4_out',
            'ysl_drying_uf',
            'yas_r1_out',
            'yas_r2_out',
            'yas_r3_out',
            'yas_r4_out',
            'ysett_of',
            'yprim_clar_uf',
            'yrecirc_water',
        ]
        stable = super()._stabilize(check_vars=check_vars, atol=atol)
        return stable

    def simulate(self, *, plot=True, export=True):
        """Simulates the plant.

        Parameters
        ----------
        plot : bool (optional)
            If `True`, the data is plotted. <br>
            Default is `True`.
        export : bool (optional)
            If `True`, the data is exported. <br>
            Default is `True`.
        """

        logger.info('Stabilize bsm2_custom\n')
        self.stabilize()
        self.evaluator.add_new_data('iqi', 'iqi')
        self.evaluator.add_new_data('eqi', 'eqi')
        self.evaluator.add_new_data('oci', 'oci')
        self.evaluator.add_new_data('oci_final', 'oci_final')
        self.evaluator.add_new_data('q_flow_eff', 'q_flow_eff', 'm3/d')
        self.evaluator.add_new_data('kjeldahlN_eff', 'kjeldahlN_eff', 'g(N)/m3')
        self.evaluator.add_new_data('totalN_eff', 'totalN_eff', 'g(N)/m3')
        self.evaluator.add_new_data('COD_eff', 'COD_eff', 'g(COD)/m3')
        self.evaluator.add_new_data('BOD5_eff', 'BOD5_eff', 'g(O2)/m3')
        self.evaluator.add_new_data('X_TSS_eff', 'X_TSS_eff', 'g(SS)/m3')

        logger.info('Simulate bsm2_custom\n')
        for i, _ in enumerate(tqdm(self.simtime)):
            self.step(i)

            if self.evaltime[0] <= self.simtime[i] <= self.evaltime[1]:
                self.evaluator.update_data('iqi', self.iqi_all[i], self.simtime[i])
                self.evaluator.update_data('eqi', self.eqi_all[i], self.simtime[i])
                self.evaluator.update_data('oci', self.oci_all[i], self.simtime[i])
                self.evaluator.update_data('q_flow_eff', self.adv_quants_eff_all[i, 0], self.simtime[i])
                self.evaluator.update_data('kjeldahlN_eff', self.adv_quants_eff_all[i, 1], self.simtime[i])
                self.evaluator.update_data('totalN_eff', self.adv_quants_eff_all[i, 2], self.simtime[i])
                self.evaluator.update_data('COD_eff', self.adv_quants_eff_all[i, 3], self.simtime[i])
                self.evaluator.update_data('BOD5_eff', self.adv_quants_eff_all[i, 4], self.simtime[i])
                self.evaluator.update_data('X_TSS_eff', self.adv_quants_eff_all[i, 5], self.simtime[i])

        self.oci_final = self.get_final_performance()[-1]
        self.evaluator.update_data('oci_final', self.oci_final, self.evaltime[1])

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
            comp_eff = self.y_eff_all[self.eval_idx[0] : self.eval_idx[1], comps[i]]
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
        tot_sludge_prod : float
            Total sludge production [kg ⋅ d⁻¹].
        tot_tss_mass : float
            Total tss mass [kg ⋅ d⁻¹].
        carb_mass : float
            Carbon mass [kg(COD) ⋅ d⁻¹].
        ch4_prod : float
            Methane production [kg(CH4) ⋅ d⁻¹].
        h2_prod : float
            Hydrogen production [kg(H2) ⋅ d⁻¹].
        co2_prod : float
            Carbon dioxide production [kg(CO2) ⋅ d⁻¹].
        q_gas : float
            Total gas production [m³ ⋅ d⁻¹].
        heat_demand : float
            Heat demand [kWh ⋅ d⁻¹].
        mixingenergy : float
            Mixing energy [kWh ⋅ d⁻¹].
        pumpingenergy : float
            Pumping energy [kWh ⋅ d⁻¹].
        aerationenergy : float
            Aeration energy [kWh ⋅ d⁻¹].
        oci_eval : float
            Final operational cost index value [-].
        """

        # calculate the final performance values

        num_eval_timesteps = self.eval_idx[1] - self.eval_idx[0]

        iqi_eval = np.sum(self.iqi_all[self.eval_idx[0] : self.eval_idx[1]]) / num_eval_timesteps
        eqi_eval = np.sum(self.eqi_all[self.eval_idx[0] : self.eval_idx[1]]) / num_eval_timesteps

        oci_factors_eval = self.perf_factors_all[self.eval_idx[0] : self.eval_idx[1]]
        pumpingenergy = np.sum(oci_factors_eval[:, 0]) / num_eval_timesteps
        aerationenergy = np.sum(oci_factors_eval[:, 1]) / num_eval_timesteps
        mixingenergy = np.sum(oci_factors_eval[:, 2]) / num_eval_timesteps
        tot_tss_mass = np.sum(oci_factors_eval[:, 3]) / num_eval_timesteps + (
            oci_factors_eval[-1, 5] - oci_factors_eval[0, 5]
        ) / (self.evaltime[-1] - self.evaltime[0])
        tot_sludge_prod = (np.sum(oci_factors_eval[:, 4]) + np.sum(oci_factors_eval[:, 3])) / num_eval_timesteps + (
            oci_factors_eval[-1, 5] - oci_factors_eval[0, 5]
        ) / (self.evaltime[-1] - self.evaltime[0])
        carb_mass = np.sum(oci_factors_eval[:, 6]) / num_eval_timesteps
        heat_demand = np.sum(oci_factors_eval[:, 7]) / num_eval_timesteps
        ch4_prod = np.sum(oci_factors_eval[:, 8]) / num_eval_timesteps
        h2_prod = np.sum(oci_factors_eval[:, 9]) / num_eval_timesteps
        co2_prod = np.sum(oci_factors_eval[:, 10]) / num_eval_timesteps
        q_gas = np.sum(oci_factors_eval[:, 11]) / num_eval_timesteps

        oci_eval = self.performance.oci(
            pumpingenergy, aerationenergy, mixingenergy, tot_tss_mass, carb_mass, heat_demand, ch4_prod
        )

        return (
            iqi_eval,
            eqi_eval,
            tot_sludge_prod,
            tot_tss_mass,
            carb_mass,
            ch4_prod,
            h2_prod,
            co2_prod,
            q_gas,
            heat_demand,
            mixingenergy,
            pumpingenergy,
            aerationenergy,
            oci_eval,
        )
