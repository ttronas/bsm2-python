"""Execution file for simulation with asm3 model with second clarifier

This script will run a 14 d - simulation with an input file (.xlsx) containing measured values every 15 minutes. The results
are saved as excel (.xlsx). It is necessary to run the steady state file first.

This script requires that the following packages are installed within the Python environment you are running this script
in: 'numpy', 'pandas', 'pyexcelerate', 'scipy.integrate', 'numba'.

The parameters 'TEMPMODEL' and 'ACTIVATE' can be set to 'True' if you want to activate them.
"""


import numpy as np
import pandas as pd
import time
import asm3init
import settler1dinit_asm3
import asm3
import settler1d_asm3
from pyexcelerate import Workbook


tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated

# Initial values from steady state simulation:
df_init = pd.read_excel('results_ss.xlsx', header=None)     # vielleicht eine Fehlermeldung einbauen, wenn man ss noch nicht gemacht hat
yinit1 = df_init.loc[0, 0:19].to_numpy()
yinit2 = df_init.loc[1, 0:19].to_numpy()
yinit3 = df_init.loc[2, 0:19].to_numpy()
yinit4 = df_init.loc[3, 0:19].to_numpy()
yinit5 = df_init.loc[4, 0:19].to_numpy()
settlerinit = df_init.loc[7].to_numpy()

# definition of the reactors:
reactor1 = asm3.ASM3reactor(asm3init.par1, yinit1, asm3init.kla1, asm3init.vol1, asm3init.carb1, asm3init.carbonsourceconc, tempmodel, activate)
reactor2 = asm3.ASM3reactor(asm3init.par2, yinit2, asm3init.kla2, asm3init.vol2, asm3init.carb2, asm3init.carbonsourceconc, tempmodel, activate)
reactor3 = asm3.ASM3reactor(asm3init.par3, yinit3, asm3init.kla3, asm3init.vol3, asm3init.carb3, asm3init.carbonsourceconc, tempmodel, activate)
reactor4 = asm3.ASM3reactor(asm3init.par4, yinit4, asm3init.kla4, asm3init.vol4, asm3init.carb4, asm3init.carbonsourceconc, tempmodel, activate)
reactor5 = asm3.ASM3reactor(asm3init.par5, yinit5, asm3init.kla5, asm3init.vol5, asm3init.carb5, asm3init.carbonsourceconc, tempmodel, activate)
settler = settler1d_asm3.Settler(settler1dinit_asm3.dim, settler1dinit_asm3.layer, asm3init.Qr, asm3init.Qw, settlerinit, settler1dinit_asm3.settlerpar, tempmodel)

# Dynamic Influent (Dryinfluent):
df = pd.read_excel('dryinfluent_asm3.xlsx', 'Tabelle1', header=None)     # select input file here

timestep = 1/(60*24)
sampleinterval = 15/(60*24)
endtime = 14
simtime = np.arange(0, endtime, timestep)
y_out5 = yinit5
ys_in = np.zeros(20)
ys_out = df_init.loc[5, 0:19].to_numpy()
Qintr = asm3init.Qintr
numberstep = 1

start = time.perf_counter()
row = 0
y_in = df.loc[row, 1:20].to_numpy()

reactin = np.zeros((int(endtime/sampleinterval+1), 20))
react1 = np.zeros((int(endtime/sampleinterval+1), 20))
react2 = np.zeros((int(endtime/sampleinterval+1), 20))
react3 = np.zeros((int(endtime/sampleinterval+1), 20))
react4 = np.zeros((int(endtime/sampleinterval+1), 20))
react5 = np.zeros((int(endtime/sampleinterval+1), 20))
settlerout = np.zeros((int(endtime/sampleinterval+1), 20))
settlereff = np.zeros((int(endtime/sampleinterval+1), 20))

number = 0
reactin[number] = y_in
react1[number] = yinit1
react2[number] = yinit2
react3[number] = yinit3
react4[number] = yinit4
react5[number] = yinit5
settlerout[number] = df_init.loc[5, 0:19].to_numpy()
settlereff[number] = df_init.loc[6, 0:19].to_numpy()
number = number + 1

for step in simtime:
    if (numberstep-1) % 15 == 0.0:
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

    # print('settler:', ys_out)

    if numberstep % 15 == 0.0:
        reactin[[number]] = y_in1[0:20]
        react1[[number]] = y_out1[0:20]
        react2[[number]] = y_out2[0:20]
        react3[[number]] = y_out3[0:20]
        react4[[number]] = y_out4[0:20]
        react5[[number]] = y_out5[0:20]
        settlerout[[number]] = ys_out[0:20]
        settlereff[[number]] = ys_eff[0:20]
        number = number + 1

    numberstep = numberstep + 1

stop = time.perf_counter()

print('Simulationszeit: ', stop - start)
print('Output bei t = 14 d: ', ys_out, ys_eff)

start_writer = time.perf_counter()
wb = Workbook()
ws = wb.new_sheet("yin", data=reactin)
ws = wb.new_sheet("yout1", data=react1)
ws = wb.new_sheet("yout2", data=react2)
ws = wb.new_sheet("yout3", data=react3)
ws = wb.new_sheet("yout4", data=react4)
ws = wb.new_sheet("yout5", data=react5)
ws = wb.new_sheet("ysout", data=settlerout)
ws = wb.new_sheet("yseff", data=settlereff)
wb.save("results_all_asm3.xlsx")

output_all = [react1[number-1], react2[number-1], react3[number-1], react4[number-1], react5[number-1], settlerout[number-1], settlereff[number-1], settler.ys0]

wb2 = Workbook()
ws = wb2.new_sheet("sheet1", data=output_all)
wb2.save("results_asm3.xlsx")

stop_writer = time.perf_counter()


print('Zeit für Excel: ', stop_writer - start_writer)
