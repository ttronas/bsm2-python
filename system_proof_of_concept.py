import control as ct
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

# we have a control system with a sensor, a PID controller, an actuator, and a system
# the sensor measures the concentration of a substance (so5) in a tank
# the PID controller adjusts the flow rate of a separate substance (kla).
# the separate substance then reacts to the measured substance and increases its concentration in the tank
# the actuator controls the flow rate of the substance into the tank
# the system is a simple first-order system that models the dynamics of the tank
# (the measured substance is consumed at a constant rate)

# the sensor has a transfer function that models its response time and a noise model.
# It also has a minimum and maximum value
# the data flow is: input signal -> transfer function -> noise -> limit check -> output signal
# the PID controller has a proportional, integral, and derivative term, as well as an anti-windup mechanism.
# It also has a minimum and maximum value
# the data flow is:
# error signal -> proportional term -> integral term -> derivative term -> anti-windup term -> control signal
# the actuator has a transfer function that models its response time
# the data flow is: control signal -> transfer function -> output signal

# Properties of sensor
t90_so5 = 1  # min - response time of the sensor
t_so5 = 0.257  # min - time constant of the transfer function
num_so5 = 1  # numerator of the transfer function of the sensor
den_so5 = [t_so5**2, 2 * t_so5, 1]  # denominator of the transfer function of the sensor
min_so5 = 0  # minimum value of the sensor
max_so5 = 10  # maximum value of the sensor
std_so5 = 0.025  # standard deviation of the sensor

# Properties of the PID controller
kla_min = 0  # minimum value of the controller
kla_max = 360  # maximum value of the controller
k_so5 = 25  # gain of the controller
t_i_so5 = 2.88  # min - integral time constant of the controller
so5_int = 0  # g_COD/m^3 - initial value of the integral term
t_d_so5 = 0  # min - derivative time constant of the controller
t_t_so5 = 1.44  # min - time constant of the anti-windup mechanism
so5_aw = 0  # g_COD/m^3 - initial value of the anti-windup term
so5_set = 2  # g_COD/m^3 - setpoint of the controller

# Properties of the actuator
t90_kla5 = 4  # min - response time of the actuator
t_kla5 = 1.028  # min - time constant of the transfer function
num_kla5 = 1  # numerator of the transfer function of the actuator
den_kla5 = [t_kla5**2, 2 * t_kla5, 1]  # denominator of the transfer function of the actuator

no_transfer = 15  # min - interval for transfer function

# Properties of the system
timestep = 1  # min - time step of the simulation
noise_so5 = 0.1  # noise of the sensor
decay_so5 = 0.4  # random decay of so5 in the system

# Properties of the input signal (so5)
amplitude = 1.5  # amplitude of the input signal
frequency = 0.01  # 0.01 / min - frequency of the input signal
phase = 0  # phase of the input signal
shift = so5_set  # shift of the input signal

# Properties of the simulation
simulation_time = 100  # min - duration of the simulation


class System:
    @staticmethod
    def step(so5_input, kla_add):
        so5_resulting = so5_input + 0.1 * kla_add
        return so5_resulting


# define Sensor class
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

    def step(self, input_signal, dt):
        dt = np.array([0, dt])
        response = ct.forced_response(self.state_space, U=input_signal, T=dt, X0=self.state)
        self.state = response.states[:, -1]
        y_out = response.outputs[-1]
        noise = np.random.normal(0, self.std)
        output_signal = y_out + noise
        if output_signal < self.min_value:
            output_signal = self.min_value
        elif output_signal > self.max_value:
            output_signal = self.max_value
        return output_signal


class PID:
    def __init__(self, k, t_i, t_d, t_t, min_value, max_value, setpoint):
        self.k = k
        self.t_i = t_i
        self.t_d = t_d
        self.t_t = t_t
        self.min_value = min_value
        self.max_value = max_value
        self.setpoint = setpoint
        self.integral = 0
        self.derivative = 0
        self.error = 0
        self.prev_error = 0
        self.aw = 0

    def step(self, error, dt):
        self.error = error
        self.integral += self.error * dt
        self.derivative = (self.error - self.prev_error) / dt
        self.prev_error = self.error
        control_signal = self.k * self.error + (self.k / self.t_i * self.integral + self.k * self.t_d * self.derivative)
        if control_signal < self.min_value:
            control_signal = self.min_value
        elif control_signal > self.max_value:
            control_signal = self.max_value
        if self.error == 0:
            self.integral = 0
        if control_signal in {self.min_value, self.max_value}:
            self.aw = self.k * self.t_t * self.error
            control_signal = self.aw
        return control_signal


class Actuator:
    def __init__(self, t90, num, den):
        self.t90 = t90
        self.num = num
        self.den = den
        self.state_space = ct.tf2ss(num, den)
        n_states = self.state_space.nstates
        self.state = np.zeros(n_states)

    def step(self, input_signal, dt):
        dt = np.array([0, dt])
        response = ct.forced_response(self.state_space, U=input_signal, T=dt, X0=self.state)
        self.state = response.states[:, -1]
        y_out = response.outputs[-1]
        return y_out


# Initialize the system
system = System()
sensor = Sensor(t90_so5, den_so5, min_so5, max_so5, std_so5)
pid = PID(k_so5, t_i_so5, t_d_so5, t_t_so5, kla_min, kla_max, so5_set)
actuator = Actuator(t90_kla5, num_kla5, den_kla5)

# Initialize the simulation
t = np.arange(0, simulation_time, timestep)
input_signal = amplitude * np.sin(2 * np.pi * frequency * t + phase) + shift
output_signal = np.full_like(input_signal, np.nan)
sensor_signal = np.full_like(input_signal, np.nan)
control_signal = np.full_like(input_signal, np.nan)
actuator_signal = 0
system_signal = 0

# Plot an empty graph
plt.ion()
fig, ax = plt.subplots()
ax.set_xlim(0, simulation_time)
ax.set_ylim(min_so5, max_so5)
(line0,) = ax.plot(t, [so5_set] * len(t), label='Setpoint')
(line1,) = ax.plot(t, input_signal, label='Input Signal')
(line2,) = ax.plot(t, sensor_signal, label='Sensor Signal')
(line3,) = ax.plot(t, control_signal, label='Control Signal')
(line9,) = ax.plot(t, output_signal, label='Output Signal')

fig.legend()

# Simulation loop
for i in tqdm(range(len(t))):
    # Get sensor signal
    sensor_signal[i] = sensor.step(system_signal, timestep)
    # Get error signal
    error = pid.setpoint - sensor_signal[i]
    # Get control signal
    control_signal[i] = pid.step(error, timestep)
    # Get actuator signal
    actuator_signal = actuator.step(control_signal[i], timestep)
    # Get system signal
    system_signal = system.step(input_signal[i], actuator_signal)

    # Store output signal
    output_signal[i] = system_signal

    # Update plot
    ax.set_title(f'Time: {t[i]:.2f} min')
    line0.set_ydata([so5_set] * len(t))
    line1.set_ydata(input_signal)
    line2.set_ydata(sensor_signal)
    line3.set_ydata(control_signal)
    line9.set_ydata(output_signal)
    fig.canvas.draw()
    fig.canvas.flush_events()
