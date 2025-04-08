import control as ct
import numpy as np
from numba import jit
from scipy.integrate import odeint


class Sensor:
    def __init__(self, num, den, min_value, max_value, std):
        self.num = num
        self.den = den
        self.min_value = min_value
        self.max_value = max_value
        self.std = std
        self.state_space = ct.tf2ss(num, den)
        n_states = self.state_space.nstates
        self.state = np.zeros(n_states)

    def output(self, input_signal, dt, noise):
        dt = np.array([0, dt])
        response = ct.forced_response(self.state_space, U=input_signal, T=dt, X0=self.state)
        self.state = response.states[:, -1]
        y_out = response.outputs[-1]
        output_signal = y_out + noise * self.max_value * self.std
        if output_signal < self.min_value:
            output_signal = self.min_value
        elif output_signal > self.max_value:
            output_signal = self.max_value
        return output_signal


@jit(nopython=True, cache=True)
def function_int(t, y, setpoint, signal, k, t_i):
    return (setpoint - signal) * k / t_i


@jit(nopython=True, cache=True)
def function_aw(t, y, lim, signal, t_t):
    return (lim - signal) / t_t


class PID:
    def __init__(self, k, t_i, t_d, t_t, offset, min_value, max_value, setpoint, aw_init=None, *, use_antiwindup=True):
        self.k = k
        self.t_i = t_i
        self.t_d = t_d
        self.t_t = t_t
        self.offset = offset
        self.min_value = min_value
        self.max_value = max_value
        self.setpoint = setpoint
        self.integral = 0
        self.derivative = 0
        self.error = 0
        self.prev_error = 0
        self.prev_signal = 0
        self.prev_lim = 0
        self.aw = 0
        self.aw_init = aw_init
        self.use_antiwindup = use_antiwindup

    def output(self, signal, dt):
        dt = np.array([0, dt])
        ode_integral = odeint(
            function_int, self.integral, dt, args=(self.setpoint, signal, self.k, self.t_i), tfirst=True
        )
        self.integral = ode_integral[1][0]
        self.error = self.k * (self.setpoint - signal)
        self.derivative = self.k * self.t_d * (self.error - self.prev_error) / (dt[1] - dt[0])
        self.prev_error = self.error
        antiwindup_integral = odeint(
            function_aw, self.aw_init, dt, args=(self.prev_lim, self.prev_signal, self.t_t), tfirst=True
        )
        self.aw = antiwindup_integral[1][0]
        control_signal = self.error + self.integral + self.derivative + self.offset + self.aw
        self.prev_signal = control_signal
        control_signal = max(control_signal, self.min_value)
        control_signal = min(control_signal, self.max_value)
        self.prev_lim = control_signal
        return control_signal


class Actuator:
    def __init__(self, t90, num, den):
        self.t90 = t90
        self.num = num
        self.den = den
        self.state_space = ct.tf2ss(num, den)
        n_states = self.state_space.nstates
        self.state = np.zeros(n_states)

    def output(self, input_signal, dt):
        dt = np.array([0, dt])
        response = ct.forced_response(self.state_space, U=input_signal, T=dt, X0=self.state)
        self.state = response.states[:, -1]
        y_out = response.outputs[-1]
        return y_out
