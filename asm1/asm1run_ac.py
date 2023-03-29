import numpy as np
import csv
import pandas as pd
import time
import asm1init
import settler1dinit_asm1
import asm1
import settler1d_asm1
import average_asm1
import aerationcontrol
import aerationcontrolinit


DECAY = False       # if DECAY is True the decay of heterotrophs and autotrophs is depending on the electron acceptor present
                    # if DECAY is False the decay do not change

TEMPMODEL = False   # if TEMPMODEL is False influent wastewater temperature is just passed through process reactors
                    # if TEMPMODEL is True mass balance for the wastewater temperature is used in process reactors

ACTIVATE = False    # if ACTIVATE is False dummy states are 0
                    # if ACTIVATE is True dummy states are activated

# Initial values from steady state simulation:
with open('asm1_values_ss_ac.csv', 'r') as f:
    initdata = list(csv.reader(f, delimiter=" "))
yinit1 = np.array(initdata[0]).astype(np.float64)
yinit2 = np.array(initdata[1]).astype(np.float64)
yinit3 = np.array(initdata[2]).astype(np.float64)
yinit4 = np.array(initdata[3]).astype(np.float64)
yinit5 = np.array(initdata[4]).astype(np.float64)
settlerinit = np.array(initdata[7]).astype(np.float64)

with open('asm1_aerationvalues_ss_ac.csv', 'r') as f:
    controldata = list(csv.reader(f, delimiter=" "))
aerationvalues = np.array(controldata[0]).astype(np.float64)

# definition of the reactors:
reactor1 = asm1.ASM1reactor(asm1init.KLa1, asm1init.VOL1, yinit1, asm1init.PAR1, asm1init.carb1, asm1init.carbonsourceconc, TEMPMODEL, ACTIVATE, DECAY)
reactor2 = asm1.ASM1reactor(asm1init.KLa2, asm1init.VOL2, yinit2, asm1init.PAR2, asm1init.carb2, asm1init.carbonsourceconc, TEMPMODEL, ACTIVATE, DECAY)
reactor3 = asm1.ASM1reactor(asm1init.KLa3, asm1init.VOL3, yinit3, asm1init.PAR3, asm1init.carb3, asm1init.carbonsourceconc, TEMPMODEL, ACTIVATE, DECAY)
reactor4 = asm1.ASM1reactor(asm1init.KLa4, asm1init.VOL4, yinit4, asm1init.PAR4, asm1init.carb4, asm1init.carbonsourceconc, TEMPMODEL, ACTIVATE, DECAY)
reactor5 = asm1.ASM1reactor(aerationvalues[0], asm1init.VOL5, yinit5, asm1init.PAR5, asm1init.carb5, asm1init.carbonsourceconc, TEMPMODEL, ACTIVATE, DECAY)
settler = settler1d_asm1.Settler(settler1dinit_asm1.DIM, settler1dinit_asm1.LAYER, asm1init.Qr, asm1init.Qw, settlerinit, settler1dinit_asm1.SETTLERPAR, asm1init.PAR1, TEMPMODEL, DECAY)
SO5_sensor = aerationcontrol.Oxygensensor(aerationcontrolinit.min_SO5, aerationcontrolinit.max_SO5, aerationcontrolinit.T_SO5, aerationcontrolinit.std_SO5)
aerationcontrol5 = aerationcontrol.PIaeration(aerationcontrolinit.KLa5_max, aerationcontrolinit.KSO5, aerationcontrolinit.TiSO5, aerationcontrolinit.TtSO5, aerationcontrolinit.SO5ref, aerationcontrolinit.KLa5offset, aerationvalues[1], aerationvalues[2], aerationvalues[3], aerationvalues[4])
kla5_actuator = aerationcontrol.KLaactuator(aerationcontrolinit.T_KLa5)

# Dynamic Influent (Dryinfluent):
df = pd.read_excel('dryinfluent.xlsx', 'Tabelle1', header=None)     # select input file here

integration = 1     # step of integration in min
sample = 15         # results are saved every 15 min step

timestep = integration/(60*24)
sampleinterval = sample/(60*24)
endtime = 14
simtime = np.arange(0, endtime, timestep)
evaltime = np.array([7, 14])
y_out5 = yinit5
ys_in = np.zeros(21)
ys_out = np.array(initdata[5]).astype(np.float64)
Qintr = asm1init.Qintr
numberstep = 1

# sensor noise for oxygen sensor:
# noise_SO5 = np.zeros(20161)  # use this when no noise should be used
df_noise = pd.read_excel('sensornoise.xlsx', 'Tabelle1', header=None)
noise_SO5 = df_noise.loc[:, 1].to_numpy()

row = 0
y_in = df.loc[row, 1:21].to_numpy()

reactin = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 21))
react1 = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 21))
react2 = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 21))
react3 = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 21))
react4 = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 21))
react5 = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 21))
settlerout = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 21))
settlereff = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 25))
settlerTSS = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), settler1dinit_asm1.nooflayers))

number = 0

SO5 = np.zeros(16)
kla5 = np.zeros(16)
SO5[14] = y_out5[7]         # for first step
kla5_a = asm1init.KLa5      # for first step

start1 = time.perf_counter()
for step in simtime:
    if len(simtime) > 60 / integration * 24 * 14:
        if step > (14-timestep):
            break
    if (numberstep-1) % (int(sample/integration)) == 0.0:
        y_in = df.loc[row, 1:21].to_numpy()
        row = row + 1
    y_in_r = (y_in * y_in[14] + ys_out * ys_out[14]) / (y_in[14] + ys_out[14])
    y_in_r[14] = y_in[14] + ys_out[14]
    y_in1 = (y_in_r * y_in_r[14] + y_out5 * Qintr) / (y_in_r[14] + Qintr)
    y_in1[14] = y_in_r[14] + Qintr

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)
    SO5[15] = y_out5[7]

    SO5_meas = SO5_sensor.measureSO(SO5, step, timestep, numberstep, noise_SO5[numberstep - 1])

    kla5[14] = kla5_a
    kla5[15] = aerationcontrol5.output(SO5_meas, step, timestep)
    kla5_a = kla5_actuator.real_actuator(kla5, step, timestep, numberstep)
    reactor5 = asm1.ASM1reactor(kla5_a, asm1init.VOL5, y_out5, asm1init.PAR5, asm1init.carb5,
                                asm1init.carbonsourceconc, TEMPMODEL, ACTIVATE, DECAY)

    # for next step:
    SO5[0:15] = SO5[1:16]
    kla5[0:15] = kla5[1:16]

    ys_in[0:14] = y_out5[0:14]
    ys_in[14] = y_out5[14] - Qintr
    ys_in[15:21] = y_out5[15:21]

    ys_out, ys_eff, ys_TSS = settler.outputs(timestep, step, ys_in)

    numberstep = numberstep + 1

stop1 = time.perf_counter()

print('First 14 d simulation completed after', stop1-start1)

SO5 = np.zeros(16)
kla5 = np.zeros(16)
SO5[14] = y_out5[7]
number = 0
row = 0
numberstep = 1

start2 = time.perf_counter()
for step in simtime:
    if len(simtime) > 60 / integration * 24 * 14:
        if step > (14-timestep):
            break
    if (numberstep-1) % (int(sample/integration)) == 0.0:
        y_in = df.loc[row, 1:21].to_numpy()
        row = row + 1
    y_in_r = (y_in * y_in[14] + ys_out * ys_out[14]) / (y_in[14] + ys_out[14])
    y_in_r[14] = y_in[14] + ys_out[14]
    y_in1 = (y_in_r * y_in_r[14] + y_out5 * Qintr) / (y_in_r[14] + Qintr)
    y_in1[14] = y_in_r[14] + Qintr

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)

    SO5[15] = y_out5[7]

    SO5_meas = SO5_sensor.measureSO(SO5, step, timestep, numberstep, noise_SO5[numberstep - 1])
    kla5[14] = kla5_a
    kla5[15] = aerationcontrol5.output(SO5_meas, step, timestep)
    kla5_a = kla5_actuator.real_actuator(kla5, step, timestep, numberstep)
    reactor5 = asm1.ASM1reactor(kla5_a, asm1init.VOL5, y_out5, asm1init.PAR5, asm1init.carb5,
                                asm1init.carbonsourceconc, TEMPMODEL, ACTIVATE, DECAY)
    # for next step:
    SO5[0:15] = SO5[1:16]
    kla5[0:15] = kla5[1:16]

    ys_in[0:14] = y_out5[0:14]
    ys_in[14] = y_out5[14] - Qintr
    ys_in[15:21] = y_out5[15:21]

    ys_out, ys_eff, ys_TSS = settler.outputs(timestep, step, ys_in)
    if step >= (evaltime[0] - timestep):
        if (numberstep - 1) % (int(sample / integration)) == 0.0:
            reactin[[number]] = y_in1
            react1[[number]] = y_out1
            react2[[number]] = y_out2
            react3[[number]] = y_out3
            react4[[number]] = y_out4
            react5[[number]] = y_out5
            settlerout[[number]] = ys_out
            settlereff[[number]] = ys_eff
            number = number + 1

    numberstep = numberstep + 1

stop2 = time.perf_counter()

print('Second 14 d simulation completed after', stop2 - start2)
ys_eff_av = average_asm1.averages(settlereff, sampleinterval, evaltime)
print('Average effluent values after second 14 d simulation', ys_eff_av)


# # Save data in csv-File:
# with open('asm1_effluentav_val_1min_ac.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile, delimiter=' ')
#     writer.writerow(ys_eff_av)
#
# with open('asm1_effluent_val.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile, delimiter=' ')
#     writer.writerows(settlereff)
