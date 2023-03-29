"""Execution file for simulation with asm3 model with second clarifier

This script will run a 14 d - simulation with an input file (.xlsx) containing measured values every 15 minutes. The results
are saved as excel (.xlsx). It is necessary to run the steady state file first.

This script requires that the following packages are installed within the Python environment you are running this script
in: 'numpy', 'csv', 'scipy.integrate', 'numba'.

The parameters 'TEMPMODEL' and 'ACTIVATE' can be set to 'True' if you want to activate them.
"""

import numpy as np
import csv
import pandas as pd
import time
import asm3init
import settler1dinit_asm3
import asm3
import settler1d_asm3
import average_asm3


tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated

with open('asm3_values_ss_val.csv', 'r') as f:
    initdata = list(csv.reader(f, delimiter=" "))
yinit1 = np.array(initdata[0]).astype(np.float64)
yinit2 = np.array(initdata[1]).astype(np.float64)
yinit3 = np.array(initdata[2]).astype(np.float64)
yinit4 = np.array(initdata[3]).astype(np.float64)
yinit5 = np.array(initdata[4]).astype(np.float64)
settlerinit = np.array(initdata[7]).astype(np.float64)


# definition of the reactors:
reactor1 = asm3.ASM3reactor(asm3init.par1, yinit1, asm3init.kla1, asm3init.vol1, asm3init.carb1, asm3init.carbonsourceconc, tempmodel, activate)
reactor2 = asm3.ASM3reactor(asm3init.par2, yinit2, asm3init.kla2, asm3init.vol2, asm3init.carb2, asm3init.carbonsourceconc, tempmodel, activate)
reactor3 = asm3.ASM3reactor(asm3init.par3, yinit3, asm3init.kla3, asm3init.vol3, asm3init.carb3, asm3init.carbonsourceconc, tempmodel, activate)
reactor4 = asm3.ASM3reactor(asm3init.par4, yinit4, asm3init.kla4, asm3init.vol4, asm3init.carb4, asm3init.carbonsourceconc, tempmodel, activate)
reactor5 = asm3.ASM3reactor(asm3init.par5, yinit5, asm3init.kla5, asm3init.vol5, asm3init.carb5, asm3init.carbonsourceconc, tempmodel, activate)
settler = settler1d_asm3.Settler(settler1dinit_asm3.dim, settler1dinit_asm3.layer, asm3init.Qr, asm3init.Qw, settlerinit, settler1dinit_asm3.settlerpar, tempmodel)

# Dynamic Influent (Dryinfluent):
df = pd.read_excel('dryinfluent_asm3.xlsx', 'Tabelle1', header=None)     # select input file here

integration = 1/6     # step of integration in min
sample = 15         # results are saved every 15 min step

timestep = integration/(60*24)
sampleinterval = sample/(60*24)
endtime = 14
simtime = np.arange(0, endtime, timestep)
evaltime = np.array([7, 14])
y_out5 = yinit5
ys_in = np.zeros(20)
ys_out = np.array(initdata[5]).astype(np.float64)
Qintr = asm3init.Qintr
numberstep = 1

start = time.perf_counter()
row = 0
y_in = df.loc[row, 1:20].to_numpy()

reactin = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 20))
react1 = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 24))
react2 = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 24))
react3 = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 24))
react4 = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 24))
react5 = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 24))
settlerout = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 20))
settlereff = np.zeros((int((evaltime[1]-evaltime[0])/sampleinterval), 24))


number = 0

for step in simtime:
    if len(simtime) > 60 / integration * 24 * 14:
        if step > (14 - timestep):
            break
    if (numberstep-1) % (int(sample/integration)) == 0.0:
        y_in = df.loc[row, 1:20].to_numpy()
        row = row + 1
    y_in_r = (y_in * y_in[13] + ys_out[0:20] * ys_out[13]) / (y_in[13] + ys_out[13])
    y_in_r[13] = y_in[13] + ys_out[13]
    y_in1 = (y_in_r * y_in_r[13] + y_out5[0:20] * Qintr) / (y_in_r[13] + Qintr)
    y_in1[13] = y_in_r[13] + Qintr

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1[0:20])
    y_out3 = reactor3.output(timestep, step, y_out2[0:20])
    y_out4 = reactor4.output(timestep, step, y_out3[0:20])
    y_out5 = reactor5.output(timestep, step, y_out4[0:20])

    Qintr = asm3init.Qintr

    ys_in[0:13] = y_out5[0:13]
    ys_in[13] = y_out5[13] - Qintr
    ys_in[14:20] = y_out5[14:20]

    ys_out, ys_eff = settler.outputs(timestep, step, ys_in)

    numberstep = numberstep + 1

number = 0
row = 0
numberstep = 1

for step in simtime:
    if len(simtime) > 60 / integration * 24 * 14:
        if step > (14 - timestep):
            break
    if (numberstep-1) % (int(sample/integration)) == 0.0:
        y_in = df.loc[row, 1:20].to_numpy()
        row = row + 1
    y_in_r = (y_in * y_in[13] + ys_out[0:20] * ys_out[13]) / (y_in[13] + ys_out[13])
    y_in_r[13] = y_in[13] + ys_out[13]
    y_in1 = (y_in_r * y_in_r[13] + y_out5[0:20] * Qintr) / (y_in_r[13] + Qintr)
    y_in1[13] = y_in_r[13] + Qintr

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1[0:20])
    y_out3 = reactor3.output(timestep, step, y_out2[0:20])
    y_out4 = reactor4.output(timestep, step, y_out3[0:20])
    y_out5 = reactor5.output(timestep, step, y_out4[0:20])

    Qintr = asm3init.Qintr

    ys_in[0:13] = y_out5[0:13]
    ys_in[13] = y_out5[13] - Qintr
    ys_in[14:20] = y_out5[14:20]

    ys_out, ys_eff = settler.outputs(timestep, step, ys_in)
    if step >= (evaltime[0] - timestep):
        if (numberstep - 1) % (int(sample / integration)) == 0.0:
            print(step)
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

stop = time.perf_counter()

print('Simulationszeit: ', stop - start)
print('Output bei t = 14 d: ', ys_out, ys_eff)
ys_eff_av = np.transpose(average_asm3.averages(settlereff, sampleinterval, evaltime))
print('Average effluent values after 14 d simulation', ys_eff_av)

# Daten als csv-File abspeichern:
with open('asm3_effluentav_val_10s.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerow(ys_eff_av)

with open('asm3_effluent_val_10s.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerows(settlereff)


