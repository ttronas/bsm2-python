import csv
import os

import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

import bsm2_python.bsm2.init.aerationcontrolinit as acc
from bsm2_python.bsm2.aerationcontrol_new import PID, Actuator, Sensor

path_name = os.path.dirname(__file__)

# Properties of the simulation
simulation_time = 100  # min - duration of the simulation

# Properties of the system
timestep = 1  # min - time step of the simulation
noise_so5 = 0.1  # noise of the sensor
decay_so5 = 0.4  # random decay of so5 in the system

# Properties of the input signal (so5)
amplitude = 1.5  # amplitude of the input signal
frequency = 0.01  # 0.01 / min - frequency of the input signal
phase = 0  # phase of the input signal
shift = 2  # shift of the input signal


class System:
    @staticmethod
    def step(so5_input, kla_add):
        so5_resulting = so5_input + 0.001 * kla_add
        return so5_resulting


noise_file = path_name + '/src/bsm2_python/data/sensornoise.csv'
with open(noise_file, encoding='utf-8-sig') as f:
    noise_data = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)
noise_so4 = noise_data[:, 1]
noise_time = noise_data[:, 0]


system = System()
num_sen = 1
den_sen = [acc.T_SO4**2, 2 * acc.T_SO4, 1]
sensor = Sensor(num_sen, den_sen, acc.MIN_SO4, acc.MAX_SO4, acc.STD_SO4)
pid = PID(
    acc.KSO4, acc.TISO4, acc.TDSO4, acc.TTSO4, acc.KLA4OFFSET, acc.KLA4_MIN, acc.KLA4_MAX, acc.SO4REF, acc.SO4AWSTATE
)
num_act = 1
den_act = [acc.T_KLA4**2, 2 * acc.T_KLA4, 1]
actuator = Actuator(acc.T90_KLA4, num_act, den_act)


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
ax.set_ylim(acc.MIN_SO4, acc.MAX_SO4)
(line0,) = ax.plot(t, [acc.SO4REF] * len(t), label='Setpoint')
(line1,) = ax.plot(t, input_signal, label='Input Signal')
(line2,) = ax.plot(t, sensor_signal, label='Sensor Signal')
(line3,) = ax.plot(t, control_signal, label='Control Signal')
(line9,) = ax.plot(t, output_signal, label='Output Signal')
fig.legend()

# Simulation loop
for i in tqdm(range(len(t))):
    idx_noise = int(np.where(noise_time - 1e-7 <= i)[0][-1])
    sensor_signal[i] = sensor.output(system_signal, timestep, noise_so4[idx_noise])
    control_signal[i] = pid.output(sensor_signal[i], timestep)
    actuator_signal = actuator.output(control_signal[i], timestep)
    system_signal = system.step(input_signal[i], actuator_signal)
    output_signal[i] = system_signal

    ax.set_title(f'Time: {t[i]:.2f} min')
    line0.set_ydata([acc.SO4REF] * len(t))
    line2.set_ydata(sensor_signal)
    line3.set_ydata(control_signal)
    line9.set_ydata(output_signal)
    fig.canvas.draw()
    fig.canvas.flush_events()
