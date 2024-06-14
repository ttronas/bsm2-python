import numpy as np
from numba import jit
from scipy import signal
from scipy.integrate import odeint


class OxygenSensor:
    def __init__(self, min_so: float, max_so: float, t_so: float, std_so: float):
        """
        Parameters:
        ----------
        min_so : int or float
            Lower measuring limit of the oxygen sensor

        max_so : int or float
            Upper measuring limit of the oxygen sensor

        t_so : float
            Time constant of transfer function

        std_so : float
            Standard deviation for adding measurement noise
        """
        self.min_so = min_so
        self.max_so = max_so
        self.t_so = t_so
        self.std_so = std_so

    def measure_so(
        self, so: np.ndarray, step: float, controlnumber: int, noise_so: float, transferfunction: float, control: float
    ) -> float:
        """Returns the measured oxygen concentration in a reactor compartment

        Parameters
        ----------
        so : np.ndarray
            Oxygen concentration from ASM1 model at every time step of the interval for the transfer function
        step : int or float
            Current time step of the simulation loop
        controlnumber : int
            Number of the current oxygen measurement
        noise_so : float
            Value for adding measurement noise
        transferfunction : int or float
            Interval for transfer function in min
        control : int or float
            step of aeration control in min

        Returns
        -------
        float
            Float value of the measured oxygen concentration in the reactor compartment
        """

        num_so = [1]
        den_so = [self.t_so * self.t_so, 2 * self.t_so, 1]
        timestep = control / (60 * 24)

        if step == 0:
            so_meas = so[int(transferfunction / control) - 1] + noise_so * self.max_so * self.std_so
        elif step <= transferfunction / (60 * 24):
            t_so_lower15 = np.linspace(0, step + 2 * timestep, controlnumber)
            so_slice = so[
                ((int(transferfunction / control) + 1) - controlnumber) : (int(transferfunction / control) + 1)
            ]
            _, yout_so, _ = signal.lsim((num_so, den_so), so_slice, t_so_lower15[0:controlnumber])
            so_meas = yout_so[controlnumber - 1] + noise_so * self.max_so * self.std_so
        else:
            t_so_15 = np.arange(step - int(transferfunction / control) * timestep, step + timestep, timestep)
            _, yout_so, _ = signal.lsim((num_so, den_so), so, t_so_15[0 : (int(transferfunction / control) + 1)])
            so_meas = yout_so[int(transferfunction / control)] + noise_so * self.max_so * self.std_so

        so_meas = max(so_meas, self.min_so)
        so_meas = min(so_meas, self.max_so)

        return so_meas


@jit(nopython=True, cache=True)
def function_ac(t, y, soref, so_meas, kso, tiso):
    return (soref - so_meas) * kso / tiso


@jit(nopython=True, cache=True)
def function_aw(t, y, kla_lim, kla_calc, ttso):
    return (kla_lim - kla_calc) / ttso


class PIAeration:
    def __init__(
        self,
        kla_min: float,
        kla_max: float,
        kso: float,
        tiso: float,
        ttso: float,
        soref: float,
        klaoffset: float,
        sointstate: float,
        soawstate: float,
        kla_lim: float,
        kla_calc: float,
        *,
        use_antiwindup: bool,
    ):
        """
        Parameters:
        ----------
        kla_min : int or float
            Lower limit of the adjustable KLa value
        kla_max : int or float
            Upper limit of the adjustable KLa value
        kso : int or float
            Amplification constant for PI calculation
        tiso : float
            Time constant of integral part
        ttso : float
            Time constant for integration of 'antiwindup'
        soref : int or float
            set point for oxygen concentration
        klaoffset : int or float
            Controller output when the rest is turned off
        sointstate : int or float
            Initial integration value for integration part
        soawstate : int or float
            Initial integration value for 'antiwindup'
        kla_lim : float
            Kla value after adjusting to upper and lower limit
        kla_calc : float
            Kla value calculated from PI control
        use_antiwindup : bool
            If True, antiwindup is used in the PI control. Strongly recommended
        """

        self.kla_min = kla_min
        self.kla_max = kla_max
        self.kso = kso
        self.tiso = tiso
        self.ttso = ttso
        self.soref = soref
        self.klaoffset = klaoffset
        self.sointstate = sointstate
        self.soawstate = soawstate
        self.kla_lim = kla_lim
        self.kla_calc = kla_calc
        self.use_antiwindup = use_antiwindup

    def output(self, so_meas: float, step: float, timestep: float) -> float:
        """Returns the KLa value determined by the PI control to adjust the oxygen concentration to the set point in
        the reactor compartment

        Parameters
        ----------
        so_meas : float
            Measured oxygen concentration in the reactor compartment
        step : int or float
            Bottom boundary for integration interval in days
        timestep : int or float
            Size of integration interval in days

        Returns
        -------
        float
            Float value of the KLa value determined by the PI control
            to adjust the oxygen concentration to the set point
            in the reactor compartment
        """

        error_so = (self.soref - so_meas) * self.kso

        t_ac = np.array([step, step + timestep])
        ode_ac = odeint(
            function_ac, self.sointstate, t_ac, args=(self.soref, so_meas, self.kso, self.tiso), tfirst=True
        )

        integral_ac = ode_ac[1][0]
        self.sointstate = integral_ac

        if self.use_antiwindup:
            ode_aw = odeint(
                function_aw, self.soawstate, t_ac, args=(self.kla_lim, self.kla_calc, self.ttso), tfirst=True
            )
            antiwindup = ode_aw[1][0]
        else:
            antiwindup = 0

        self.kla_calc = error_so + integral_ac + self.klaoffset + antiwindup

        kla = self.kla_calc
        kla = max(kla, self.kla_min)
        kla = min(kla, self.kla_max)
        self.kla_lim = kla

        return kla


class KLaActuator:
    def __init__(self, t_kla: float):
        """
        Parameters
        ----------
        t_kla : float
            Time constant of transfer function
        """

        self.t_kla = t_kla

    def real_actuator(
        self, kla: np.ndarray, step: float, controlnumber: int, transferfunction: float, control: float
    ) -> float:
        """Returns the delayed KLa value for the reactor compartment

        Parameters
        ----------
        kla : np.ndarray
            KLa value from PI control at every time step of the interval for the transfer function
        step : int or float
            Current time step of the simulation loop
        controlnumber : int
            Number of the current aeration control
        transferfunction : int or float
            Interval for transfer function in min
        control : int or float
            step of aeration control in min

        Returns
        -------
        float
            Float value of the delayed KLa value for the reactor compartment
        """

        num_kla = [1]
        den_kla = [self.t_kla * self.t_kla, 2 * self.t_kla, 1]
        timestep = control / (60 * 24)
        if step == 0:
            kla_out = kla[14]
        elif step <= transferfunction / (60 * 24):
            t_kla_lower15 = np.linspace(0, step + 2 * timestep, controlnumber)
            _, yout_kla, _ = signal.lsim(
                (num_kla, den_kla),
                kla[((int(transferfunction / control) + 1) - controlnumber) : (int(transferfunction / control) + 1)],
                t_kla_lower15[0:controlnumber],
            )
            kla_out = yout_kla[controlnumber - 1]
        else:
            t_kla_15 = np.arange(step - transferfunction / control * timestep, step + timestep, timestep)
            _, yout_kla, _ = signal.lsim((num_kla, den_kla), kla, t_kla_15[0 : (int(transferfunction / control) + 1)])
            kla_out = yout_kla[int(transferfunction / control)]

        return kla_out
