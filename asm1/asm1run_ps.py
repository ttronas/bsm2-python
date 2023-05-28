"""Execution file for asm1 model with second clarifier and aeration control in reactor 3, 4 and 5

This script will run a 28 d - simulation with an input file (.xlsx) containing measured values every 15 minutes. The results
are saved as csv files. It is necessary to run the steady state file first.

This script also includes the scenarios for the flexible aeration study.

This script requires that the following packages are installed within the Python environment you are running this script
in: 'numpy', 'csv', 'pandas', 'time', 'scipy.integrate', 'numba', 'scipy'.

The parameters 'tempmodel' and 'activate' can be set to 'True' if you want to activate them.
"""


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
import plantperformance


tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated

# Initial values from steady state simulation:
with open('asm1_values_ss_ps.csv', 'r') as f:
    initdata = list(csv.reader(f, delimiter=" "))
yinit1 = np.array(initdata[0]).astype(np.float64)
yinit2 = np.array(initdata[1]).astype(np.float64)
yinit3 = np.array(initdata[2]).astype(np.float64)
yinit4 = np.array(initdata[3]).astype(np.float64)
yinit5 = np.array(initdata[4]).astype(np.float64)
settlerinit = np.array(initdata[7]).astype(np.float64)

with open('asm1_aerationvalues_ss_ps.csv', 'r') as f:
    controldata = list(csv.reader(f, delimiter=" "))
aerationvalues3 = np.array(controldata[0]).astype(np.float64)
aerationvalues4 = np.array(controldata[1]).astype(np.float64)
aerationvalues5 = np.array(controldata[2]).astype(np.float64)

# definition of the reactors:
reactor1 = asm1.ASM1reactor(asm1init.KLa1, asm1init.VOL1, yinit1, asm1init.PAR1, asm1init.carb1, asm1init.carbonsourceconc, tempmodel, activate)
reactor2 = asm1.ASM1reactor(asm1init.KLa2, asm1init.VOL2, yinit2, asm1init.PAR2, asm1init.carb2, asm1init.carbonsourceconc, tempmodel, activate)
reactor3 = asm1.ASM1reactor(aerationvalues3[0], asm1init.VOL3, yinit3, asm1init.PAR3, asm1init.carb3, asm1init.carbonsourceconc, tempmodel, activate)
reactor4 = asm1.ASM1reactor(aerationvalues4[0], asm1init.VOL4, yinit4, asm1init.PAR4, asm1init.carb4, asm1init.carbonsourceconc, tempmodel, activate)
reactor5 = asm1.ASM1reactor(aerationvalues5[0], asm1init.VOL5, yinit5, asm1init.PAR5, asm1init.carb5, asm1init.carbonsourceconc, tempmodel, activate)
settler = settler1d_asm1.Settler(settler1dinit_asm1.DIM, settler1dinit_asm1.LAYER, asm1init.Qr, asm1init.Qw, settlerinit, settler1dinit_asm1.SETTLERPAR, asm1init.PAR1, tempmodel)

SO3_sensor = aerationcontrol.Oxygensensor(aerationcontrolinit.min_SO3, aerationcontrolinit.max_SO3, aerationcontrolinit.T_SO3, aerationcontrolinit.std_SO3)
aerationcontrol3 = aerationcontrol.PIaeration(aerationcontrolinit.KLa3_min, aerationcontrolinit.KLa3_max, aerationcontrolinit.KSO3, aerationcontrolinit.TiSO3, aerationcontrolinit.TtSO3, aerationcontrolinit.SO3ref, aerationcontrolinit.KLa3offset, aerationvalues3[1], aerationvalues3[2], aerationvalues3[3], aerationvalues3[4])
kla3_actuator = aerationcontrol.KLaactuator(aerationcontrolinit.T_KLa3)

SO4_sensor = aerationcontrol.Oxygensensor(aerationcontrolinit.min_SO4, aerationcontrolinit.max_SO4, aerationcontrolinit.T_SO4, aerationcontrolinit.std_SO4)
aerationcontrol4 = aerationcontrol.PIaeration(aerationcontrolinit.KLa4_min, aerationcontrolinit.KLa4_max, aerationcontrolinit.KSO4, aerationcontrolinit.TiSO4, aerationcontrolinit.TtSO4, aerationcontrolinit.SO4ref, aerationcontrolinit.KLa4offset, aerationvalues4[1], aerationvalues4[2], aerationvalues4[3], aerationvalues4[4])
kla4_actuator = aerationcontrol.KLaactuator(aerationcontrolinit.T_KLa4)

SO5_sensor = aerationcontrol.Oxygensensor(aerationcontrolinit.min_SO5, aerationcontrolinit.max_SO5, aerationcontrolinit.T_SO5, aerationcontrolinit.std_SO5)
aerationcontrol5 = aerationcontrol.PIaeration(aerationcontrolinit.KLa5_min, aerationcontrolinit.KLa5_max, aerationcontrolinit.KSO5, aerationcontrolinit.TiSO5, aerationcontrolinit.TtSO5, aerationcontrolinit.SO5ref, aerationcontrolinit.KLa5offset, aerationvalues5[1], aerationvalues5[2], aerationvalues5[3], aerationvalues5[4])
kla5_actuator = aerationcontrol.KLaactuator(aerationcontrolinit.T_KLa5)

# Dynamic Influent (Dryinfluent):
df = pd.read_excel('dryinfluent.xlsx', 'Tabelle1', header=None)     # select input file here

integration = 1/2           # step of integration in min
sample = 15                 # results are saved every 15 min step
control = 1/2               # step of aeration control in min, should be equal or bigger than integration
transferfunction = 15       # interval for transferfunction in min

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
controlnumber = 1

# sensor noise for oxygen sensor:
# noise_SO5 = np.zeros(20161)  # use this when no noise should be used
df_noise = pd.read_excel('sensornoise.xlsx', 'Tabelle1', header=None)
noise_SO3 = df_noise.loc[:, 1].to_numpy()
noise_SO4 = df_noise.loc[:, 2].to_numpy()
noise_SO5 = df_noise.loc[:, 3].to_numpy()

# Stromdaten für Parameterstudie:
with open('strompreise_average.csv', 'r') as f:
    stromdata = list(csv.reader(f, delimiter=" "))
stromdaten = np.array(stromdata).astype(np.float64)[0]
indexstrom = -1
intervalstrom = 15

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
kla1in = np.zeros(int((evaltime[1]-evaltime[0])/sampleinterval))
kla2in = np.zeros(int((evaltime[1]-evaltime[0])/sampleinterval))
kla3in = np.zeros(int((evaltime[1]-evaltime[0])/sampleinterval))
kla4in = np.zeros(int((evaltime[1]-evaltime[0])/sampleinterval))
kla5in = np.zeros(int((evaltime[1]-evaltime[0])/sampleinterval))
flows = np.zeros((3, int((evaltime[1]-evaltime[0])/sampleinterval)))
energy = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 3))
energycosts = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval)))

vol = np.array([[reactor1.volume], [reactor2.volume], [reactor3.volume], [reactor4.volume], [reactor5.volume]])
sosat = np.array([[asm1init.SOSAT1], [asm1init.SOSAT2], [asm1init.SOSAT3], [asm1init.SOSAT4], [asm1init.SOSAT5]])
pumpfactor = np.array([[0.004], [0.008], [0.05]])

kla3_a = aerationvalues3[0]
kla4_a = aerationvalues4[0]
kla5_a = aerationvalues5[0]
number = 0

SO3 = np.zeros(int(transferfunction/control)+1)
kla3 = np.zeros(int(transferfunction/control)+1)
SO3[int(transferfunction/control)-1] = yinit3[7]                    # for first step
kla3[int(transferfunction / control) - 1] = aerationvalues3[0]      # for first step

SO4 = np.zeros(int(transferfunction/control)+1)
kla4 = np.zeros(int(transferfunction/control)+1)
SO4[int(transferfunction/control)-1] = yinit4[7]                    # for first step
kla4[int(transferfunction / control) - 1] = aerationvalues4[0]      # for first step

SO5 = np.zeros(int(transferfunction/control)+1)
kla5 = np.zeros(int(transferfunction/control)+1)
SO5[int(transferfunction/control)-1] = y_out5[7]                    # for first step
kla5[int(transferfunction / control) - 1] = aerationvalues5[0]      # for first step

number_noise = -1
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

    if (numberstep-1) % (int(intervalstrom/integration)) == 0.0:
        indexstrom = indexstrom + 1

    # Scenario 1:
    reactor3.kla = kla3_a
    reactor4.kla = kla4_a
    reactor5.kla = kla5_a

    # Scenario 2 and 3:
    # if stromdaten[indexstrom] >= 261.97:
    #     reactor3.kla = 0      # 117
    #     reactor4.kla = 0      # 87
    #     reactor5.kla = 0      # 68
    # else:
    #     reactor3.kla = kla3_a
    #     reactor4.kla = kla4_a
    #     reactor5.kla = kla5_a

    # Scenario 4 and 5:
    # if stromdaten[indexstrom] >= 261.97 and ys_eff[9] < 4.0:
    #     reactor3.kla = 0      # 117
    #     reactor4.kla = 0      # 87
    #     reactor5.kla = 0      # 68
    # else:
    #     reactor3.kla = kla3_a
    #     reactor4.kla = kla4_a
    #     reactor5.kla = kla5_a

    # Scenario 6:
    # if stromdaten[indexstrom] >= 261.97 and y_in[9] < 25.0:
    #     reactor3.kla = 0
    #     reactor4.kla = 0
    #     reactor5.kla = 0
    # else:
    #     reactor3.kla = kla3_a
    #     reactor4.kla = kla4_a
    #     reactor5.kla = kla5_a

    # Scenario 7:
    # if stromdaten[indexstrom] >= 261.97 and y_in[9] < 25.0:
    #     reactor3.kla = 0
    #     reactor4.kla = 0
    #     reactor5.kla = 0
    # elif stromdaten[indexstrom] >= 261.97 and ys_eff[9] < 4.0:
    #     reactor3.kla = 117
    #     reactor4.kla = 87
    #     reactor5.kla = 68
    # else:
    #     reactor3.kla = kla3_a
    #     reactor4.kla = kla4_a
    #     reactor5.kla = kla5_a

    if indexstrom+1 == len(stromdaten):
        indexstrom = -1

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)

    if (numberstep - 1) % (int(1 / integration)) == 0:
        number_noise = number_noise + 1
    if (numberstep - 1) % (int(control / integration)) == 0:
        SO3[int(transferfunction / control)] = y_out3[7]
        SO3_meas = SO3_sensor.measureSO(SO3, step, controlnumber, noise_SO3[number_noise], transferfunction, control)
        kla3[int(transferfunction / control)] = aerationcontrol3.output(SO3_meas, step, timestep)
        kla3_a = kla3_actuator.real_actuator(kla3, step, controlnumber, transferfunction, control)

        SO4[int(transferfunction / control)] = y_out4[7]
        SO4_meas = SO4_sensor.measureSO(SO4, step, controlnumber, noise_SO4[number_noise], transferfunction, control)
        kla4[int(transferfunction / control)] = aerationcontrol4.output(SO4_meas, step, timestep)
        kla4_a = kla4_actuator.real_actuator(kla4, step, controlnumber, transferfunction, control)

        SO5[int(transferfunction / control)] = y_out5[7]
        SO5_meas = SO5_sensor.measureSO(SO5, step, controlnumber, noise_SO5[number_noise], transferfunction, control)
        kla5[int(transferfunction / control)] = aerationcontrol5.output(SO5_meas, step, timestep)
        kla5_a = kla5_actuator.real_actuator(kla5, step, controlnumber, transferfunction, control)

        # for next step:
        SO3[0:int(transferfunction / control)] = SO3[1:(int(transferfunction / control) + 1)]
        kla3[0:int(transferfunction / control)] = kla3[1:(int(transferfunction / control) + 1)]

        SO4[0:int(transferfunction / control)] = SO4[1:(int(transferfunction / control) + 1)]
        kla4[0:int(transferfunction / control)] = kla4[1:(int(transferfunction / control) + 1)]

        SO5[0:int(transferfunction / control)] = SO5[1:(int(transferfunction / control) + 1)]
        kla5[0:int(transferfunction / control)] = kla5[1:(int(transferfunction / control) + 1)]
        controlnumber = controlnumber + 1

    ys_in[0:14] = y_out5[0:14]
    ys_in[14] = y_out5[14] - Qintr
    ys_in[15:21] = y_out5[15:21]

    ys_out, ys_eff = settler.outputs(timestep, step, ys_in)

    numberstep = numberstep + 1

stop1 = time.perf_counter()

print('First 14 d simulation completed after', stop1-start1, 'seconds')

SO3 = np.zeros(int(transferfunction/control)+1)
kla3 = np.zeros(int(transferfunction/control)+1)
SO3[int(transferfunction/control)-1] = y_out3[7]        # for first step
kla3[int(transferfunction/control)-1] = kla3_a          # for first step

SO4 = np.zeros(int(transferfunction/control)+1)
kla4 = np.zeros(int(transferfunction/control)+1)
SO4[int(transferfunction/control)-1] = y_out4[7]        # for first step
kla4[int(transferfunction/control)-1] = kla4_a          # for first step

SO5 = np.zeros(int(transferfunction/control)+1)
kla5 = np.zeros(int(transferfunction/control)+1)
SO5[int(transferfunction/control)-1] = y_out5[7]        # for first step
kla5[int(transferfunction/control)-1] = kla5_a          # for first step

kla_flex = np.zeros((int(0.25*(evaltime[1]-evaltime[0])/sampleinterval), 5))
energycosts_flex = np.zeros((int(0.25*(evaltime[1]-evaltime[0])/sampleinterval)))
flexnumber = 0
number = 0
row = 0
numberstep = 1
number_noise = -1
controlnumber = 1
indexstrom = -1

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

    if (numberstep-1) % (int(intervalstrom/integration)) == 0.0:
        indexstrom = indexstrom + 1

    # Scenario 1:
    reactor3.kla = kla3_a
    reactor4.kla = kla4_a
    reactor5.kla = kla5_a

    # Scenario 2 and 3:
    # if stromdaten[indexstrom] >= 261.97:
    #     reactor3.kla = 0      # 117
    #     reactor4.kla = 0      # 87
    #     reactor5.kla = 0      # 68
    # else:
    #     reactor3.kla = kla3_a
    #     reactor4.kla = kla4_a
    #     reactor5.kla = kla5_a

    # Scenario 4 and 5:
    # if stromdaten[indexstrom] >= 261.97 and ys_eff[9] < 4.0:
    #     reactor3.kla = 0      # 117
    #     reactor4.kla = 0      # 87
    #     reactor5.kla = 0      # 68
    # else:
    #     reactor3.kla = kla3_a
    #     reactor4.kla = kla4_a
    #     reactor5.kla = kla5_a

    # Scenario 6:
    # if stromdaten[indexstrom] >= 261.97 and y_in[9] < 25.0:
    #     reactor3.kla = 0
    #     reactor4.kla = 0
    #     reactor5.kla = 0
    # else:
    #     reactor3.kla = kla3_a
    #     reactor4.kla = kla4_a
    #     reactor5.kla = kla5_a

    # Scenario 7:
    # if stromdaten[indexstrom] >= 261.97 and y_in[9] < 25.0:
    #     reactor3.kla = 0
    #     reactor4.kla = 0
    #     reactor5.kla = 0
    # elif stromdaten[indexstrom] >= 261.97 and ys_eff[9] < 4.0:
    #     reactor3.kla = 117
    #     reactor4.kla = 87
    #     reactor5.kla = 68
    # else:
    #     reactor3.kla = kla3_a
    #     reactor4.kla = kla4_a
    #     reactor5.kla = kla5_a

    if indexstrom+1 == len(stromdaten):
        indexstrom = -1

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)

    if (numberstep - 1) % (int(1 / integration)) == 0:
        number_noise = number_noise + 1
    if (numberstep - 1) % (int(control / integration)) == 0:
        SO3[int(transferfunction / control)] = y_out3[7]
        SO3_meas = SO3_sensor.measureSO(SO3, step, controlnumber, noise_SO3[number_noise], transferfunction, control)
        kla3[int(transferfunction / control)] = aerationcontrol3.output(SO3_meas, step, timestep)
        kla3_a = kla3_actuator.real_actuator(kla3, step, controlnumber, transferfunction, control)

        SO4[int(transferfunction / control)] = y_out4[7]
        SO4_meas = SO4_sensor.measureSO(SO4, step, controlnumber, noise_SO4[number_noise], transferfunction, control)
        kla4[int(transferfunction / control)] = aerationcontrol4.output(SO4_meas, step, timestep)
        kla4_a = kla4_actuator.real_actuator(kla4, step, controlnumber, transferfunction, control)

        SO5[int(transferfunction/control)] = y_out5[7]
        SO5_meas = SO5_sensor.measureSO(SO5, step, controlnumber, noise_SO5[number_noise], transferfunction, control)
        kla5[int(transferfunction/control)] = aerationcontrol5.output(SO5_meas, step, timestep)
        kla5_a = kla5_actuator.real_actuator(kla5, step, controlnumber, transferfunction, control)

        # for next step:
        SO3[0:int(transferfunction / control)] = SO3[1:(int(transferfunction / control) + 1)]
        kla3[0:int(transferfunction / control)] = kla3[1:(int(transferfunction / control) + 1)]

        SO4[0:int(transferfunction / control)] = SO4[1:(int(transferfunction / control) + 1)]
        kla4[0:int(transferfunction / control)] = kla4[1:(int(transferfunction / control) + 1)]

        SO5[0:int(transferfunction/control)] = SO5[1:(int(transferfunction/control)+1)]
        kla5[0:int(transferfunction/control)] = kla5[1:(int(transferfunction/control)+1)]
        controlnumber = controlnumber+1

    ys_in[0:14] = y_out5[0:14]
    ys_in[14] = y_out5[14] - Qintr
    ys_in[15:21] = y_out5[15:21]

    ys_out, ys_eff = settler.outputs(timestep, step, ys_in)
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
            kla1in[number] = reactor1.kla
            kla2in[number] = reactor2.kla
            kla3in[number] = reactor3.kla
            kla4in[number] = reactor4.kla
            kla5in[number] = reactor5.kla
            flows[0, number] = Qintr
            flows[1, number] = asm1init.Qr
            flows[2, number] = asm1init.Qw

            energy[number, 0] = plantperformance.aerationenergy(np.array([[reactor1.kla], [reactor2.kla], [reactor3.kla], [reactor4.kla], [reactor5.kla]]), vol, sosat, sampleinterval, evaltime)*7
            energy[number, 1] = plantperformance.mixingenergy(np.array([[reactor1.kla], [reactor2.kla], [reactor3.kla], [reactor4.kla], [reactor5.kla]]), vol, sampleinterval, evaltime)*7
            energy[number, 2] = plantperformance.pumpingenergy(np.array([[Qintr], [asm1init.Qr], [asm1init.Qw]]), pumpfactor, sampleinterval, evaltime)*7
            energycosts[number] = sum(energy[number])*stromdaten[indexstrom]/1000
            if stromdaten[indexstrom] >= 261.97:
                kla_flex[flexnumber] = np.array([reactor1.kla, reactor2.kla, reactor3.kla, reactor4.kla, reactor5.kla])
                energycosts_flex[flexnumber] = energycosts[number]
                flexnumber = flexnumber + 1
            number = number + 1

    numberstep = numberstep + 1

stop2 = time.perf_counter()

print('Second 14 d simulation completed after', stop2 - start2, 'seconds')
ys_eff_av = average_asm1.averages(settlereff, sampleinterval, evaltime)
print('Average effluent values after second 14 d simulation', ys_eff_av)

with open('ps_klaflex.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerows(kla_flex)

kla = np.array([kla1in, kla2in, kla3in, kla4in, kla5in])
with open('ps_kla.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerows(kla)

with open('ps_effav.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerow(ys_eff_av)

with open('ps_eff.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerows(settlereff)

with open('ps_energy.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerows(energy)

with open('ps_energycosts.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerow(energycosts)

with open('ps_energycostsflex.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerow(energycosts_flex)

# plant performance:
# aeration energy
kla = np.array([kla1in, kla2in, kla3in, kla4in, kla5in])
vol = np.array([[reactor1.volume], [reactor2.volume], [reactor3.volume], [reactor4.volume], [reactor5.volume]])
sosat = np.array([[asm1init.SOSAT1], [asm1init.SOSAT2], [asm1init.SOSAT3], [asm1init.SOSAT4], [asm1init.SOSAT5]])

ae = plantperformance.aerationenergy(kla, vol, sosat, sampleinterval, evaltime)

# pumping energy:
pumpfactor = np.array([[0.004], [0.008], [0.05]])

pe = plantperformance.pumpingenergy(flows, pumpfactor, sampleinterval, evaltime)

# mixing energy:
me = plantperformance.mixingenergy(kla, vol, sampleinterval, evaltime)

# SNH limit violations:
SNH_limit = 4
SNH_violationvalues = plantperformance.violation(settlereff[:, 9], SNH_limit, sampleinterval, evaltime)

# TSS limit violations:
TSS_limit = 30
TSS_violationvalues = plantperformance.violation(settlereff[:, 13], TSS_limit, sampleinterval, evaltime)

# SNH limit violations:
totalN_limit = 18
totalN_violationvalues = plantperformance.violation(settlereff[:, 22], totalN_limit, sampleinterval, evaltime)

# COD limit violations:
COD_limit = 100
COD_violationvalues = plantperformance.violation(settlereff[:, 23], COD_limit, sampleinterval, evaltime)

# BOD5 limit violations:
BOD5_limit = 10
BOD5_violationvalues = plantperformance.violation(settlereff[:, 24], BOD5_limit, sampleinterval, evaltime)

# aeration energy during flextime:
ae_flex = plantperformance.aerationenergy(np.transpose(kla_flex), vol, sosat, sampleinterval, evaltime)

# mixing energy during flextime:
me_flex = plantperformance.mixingenergy(np.transpose(kla_flex), vol, sampleinterval, evaltime)

data = [[ae], [pe], [me], [ae_flex], [me_flex], SNH_violationvalues, TSS_violationvalues, totalN_violationvalues, COD_violationvalues, BOD5_violationvalues]
names = ['aeration energy [kWh/d]', 'pumping energy [kWh/d]', 'mixing energy [kWh/d]', 'aeration energy during flex time [kWh/d]', 'mixing energy during flex time [kWh/d]', 'SNH: days of violation / percentage of time', 'TSS: days of violation / percentage of time', 'totalN: days of violation / percentage of time', 'COD: days of violation / percentage of time', 'BOD5: days of violation / percentage of time']

with open('ps_evaluation.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    for name, datarow in zip(names, data):
        output_row = [name]
        output_row.extend(datarow)
        writer.writerow(output_row)
