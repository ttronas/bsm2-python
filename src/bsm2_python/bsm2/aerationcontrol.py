import numpy as np
from numba import jit
from scipy import signal
from scipy.integrate import odeint


class OxygenSensor:
    """Class for measuring oxygen concentration in a reactor compartment.

    Parameters
    ----------
    min_so : float
        Lower measuring limit of the oxygen sensor [g(O₂) ⋅ m⁻³].
    max_so : float
        Upper measuring limit of the oxygen sensor [g(O₂) ⋅ m⁻³].
    t_so : float
        Integral part time constant *τ* of transfer function [d].
    std_so : float
        Standard deviation for adding measurement noise [-].
    """

    def __init__(self, min_so: float, max_so: float, t_so: float, std_so: float):
        self.min_so = min_so
        self.max_so = max_so
        self.t_so = t_so
        self.std_so = std_so

    def measure_so(
        self, so: np.ndarray, step: float, controlnumber: int, noise_so: float, transferfunction: float, control: float
    ) -> float:
        """Returns the measured oxygen concentration in a reactor compartment.

        Parameters
        ----------
        so : np.ndarray(2)
            Oxygen concentration from ASM1 model at every time step of the interval for the transfer function <br>
            [g(O₂) ⋅ m⁻³]. \n
            [so_i-1, so_i]
        step : float
            Current time step of the simulation loop [d].
        controlnumber : int
            Number of the current oxygen measurement [-].
        noise_so : float
            Value for adding measurement noise [-].
        transferfunction : float
            Interval for transfer function [min].
        control : float
            Step of aeration control [min].

        Returns
        -------
        so_meas : float
            Measured oxygen concentration in the reactor compartment [g(O₂) ⋅ m⁻³].
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
    """Class for a PI controller to adjust aeration in reactor compartments.

    Parameters
    ----------
    kla_min : float
        Lower limit of the adjustable KLa value [d⁻¹].
    kla_max : float
        Upper limit of the adjustable KLa value [d⁻¹].
    kso : float
        Amplification constant for PI controller [-].
    tiso : float
        Integral part time constant *τ* [d].
    ttso : float
        Integral part time constant *τ* of 'antiwindup' [d].
    soref : float
        Set point for oxygen concentration [g(O₂) ⋅ m⁻³].
    klaoffset : float
        Controller output when the rest is turned off [d⁻¹].
    sointstate : float
        Initial integration value for saturated oxygen concentration [g(O₂) ⋅ m⁻³].
    soawstate : float
        Initial integration value of 'antiwindup' for saturated oxygen concentration [g(O₂) ⋅ m⁻³].
    kla_lim : float
        KLa value after adjusting to upper and lower limit [d⁻¹].
    kla_calc : float
        KLa value calculated from PI control [d⁻¹].
    use_antiwindup : bool
        If True, 'antiwindup' is used in the PI control. Strongly recommended.
    """

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
        the reactor compartment.

        Parameters
        ----------
        so_meas : float
            Measured oxygen concentration in the reactor compartment [g(O₂) ⋅ m⁻³].
        step : float
            Bottom boundary for integration interval [d].
        timestep : float
            Size of integration interval [d].

        Returns
        -------
        kla : float
            KLa value determined by the PI control to adjust the oxygen concentration to the set point
            in the reactor compartment [d⁻¹].
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
    """Class for a real actuator for the reactor compartments.

    Parameters
    ----------
    t_kla : float
        Integral part time constant *τ* for KLa actuator [d].
    """

    def __init__(self, t_kla: float):
        self.t_kla = t_kla

    def real_actuator(
        self, kla: np.ndarray, step: float, controlnumber: int, transferfunction: float, control: float
    ) -> float:
        """Returns the delayed KLa value for the reactor compartment.

        Parameters
        ----------
        kla : np.ndarray(2)
            KLa value from PI control at every time step of the interval for the transfer function [d⁻¹]. \n
            [KLa_i-1, KLa_i]
        step : float
            Current time step of the simulation loop [d].
        controlnumber : int
            Number of the current aeration control [-].
        transferfunction : float
            Interval for transfer function [min].
        control : float
            Step of aeration control [min].

        Returns
        -------
        kla_out : float
            Delayed KLa value for the reactor compartment [d⁻¹].
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
