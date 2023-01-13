"""Execution file for simulation with asm1 model with second clarifier

This script will run a 609 d - simulation with an input file (.xlsx) containing measured values every 15 minutes. The results
are saved as excel (.xlsx). It is necessary to run the steady state file first.

This script requires that the following packages are installed within the Python environment you are running this script
in: 'numpy', 'pandas', 'pyexcelerate', 'scipy.integrate', 'numba'.

The parameters 'DECAY', 'SETTLER', 'TEMPMODEL' and 'ACTIVATE' can be set to 'True' if you want to activate them.
"""


import numpy as np
import pandas as pd
import time
import asm1init
import settler1dinit_asm1
from asm1 import asm1
import settler1d_asm1
from pyexcelerate import Workbook


DECAY = False       # if DECAY is True the decay of heterotrophs and autotrophs is depending on the electron acceptor present
                    # if DECAY is False the decay do not change

SETTLER = False     # if SETTLER is False the settling model is non-reactive
                    # if SETTLER is True the settling model is reactive

TEMPMODEL = False   # if TEMPMODEL is False influent wastewater temperature is just passed through process reactors
                    # if TEMPMODEL is True mass balance for the wastewater temperature is used in process reactors

ACTIVATE = False    # if ACTIVATE is False dummy states are 0
                    # if ACTIVATE is True dummy states are activated

# Anfangswerte aus Matlab für Dynamische Simulation:

df_init = pd.read_excel('results_ss_ode.xlsx', header=None)     # vielleicht eine Fehlermeldung einbauen, wenn man ss noch nicht gemacht hat
YINIT1 = df_init.loc[0, 0:20].to_numpy()
YINIT2 = df_init.loc[1, 0:20].to_numpy()
YINIT3 = df_init.loc[2, 0:20].to_numpy()
YINIT4 = df_init.loc[3, 0:20].to_numpy()
YINIT5 = df_init.loc[4, 0:20].to_numpy()
SETTLERINIT = df_init.loc[6].to_numpy()

# definition of the reactors:

reactor1 = asm1.ASM1reactor(asm1init.KLa1, asm1init.VOL1, asm1init.SOSAT1, YINIT1, asm1init.PAR1, TEMPMODEL, ACTIVATE, DECAY)
reactor2 = asm1.ASM1reactor(asm1init.KLa2, asm1init.VOL2, asm1init.SOSAT2, YINIT2, asm1init.PAR2, TEMPMODEL, ACTIVATE, DECAY)
reactor3 = asm1.ASM1reactor(asm1init.KLa3, asm1init.VOL3, asm1init.SOSAT3, YINIT3, asm1init.PAR3, TEMPMODEL, ACTIVATE, DECAY)
reactor4 = asm1.ASM1reactor(asm1init.KLa4, asm1init.VOL4, asm1init.SOSAT4, YINIT4, asm1init.PAR4, TEMPMODEL, ACTIVATE, DECAY)
reactor5 = asm1.ASM1reactor(asm1init.KLa5, asm1init.VOL5, asm1init.SOSAT5, YINIT5, asm1init.PAR5, TEMPMODEL, ACTIVATE, DECAY)
settler = settler1d_asm1.Settler(settler1dinit_asm1.DIM, settler1dinit_asm1.LAYER, asm1init.Qr, asm1init.Qw, SETTLERINIT, settler1dinit_asm1.SETTLERPAR, asm1init.PAR1, TEMPMODEL, DECAY, SETTLER)

# Dynamic Influent (Dryinfluent):
df = pd.read_excel('dyninfluent_asm1.xlsx', 'Tabelle1', header=None)     # select input file here

timestep = 1/(60*24)
starttime = 245
endtime = 609
simtime = np.arange(starttime, endtime, timestep)
y_out5 = YINIT5
ys_out = df_init.loc[5, 0:20].to_numpy()
Qintr = 55338
numberstep = 1

start = time.perf_counter()
row = 23520
y_in = df.loc[row, 1:21].to_numpy()

reactin = np.zeros((int((endtime-starttime)/(15/(60*24))+1), 21))
react1 = np.zeros((int((endtime-starttime)/(15/(60*24))+1), 21))
react2 = np.zeros((int((endtime-starttime)/(15/(60*24))+1), 21))
react3 = np.zeros((int((endtime-starttime)/(15/(60*24))+1), 21))
react4 = np.zeros((int((endtime-starttime)/(15/(60*24))+1), 21))
react5 = np.zeros((int((endtime-starttime)/(15/(60*24))+1), 21))
settlerout = np.zeros((int((endtime-starttime)/(15/(60*24))+1), 21))
settlerall = np.zeros((int((endtime-starttime)/(15/(60*24))+1), 203))

number = 0
reactin[number] = y_in
react1[number] = YINIT1
react2[number] = YINIT2
react3[number] = YINIT3
react4[number] = YINIT4
react5[number] = YINIT5
settlerout[number] = df_init.loc[5, 0:20].to_numpy()
number = number + 1

for step in simtime:
    if (numberstep-1) % 15 == 0.0:
        y_in = df.loc[row, 1:21].to_numpy()
        row = row + 1
    y_in_r = (y_in * y_in[14] + ys_out * ys_out[14]) / (y_in[14] + ys_out[14])
    y_in_r[14] = y_in[14] + ys_out[14]
    y_in1 = (y_in_r * y_in_r[14] + y_out5 * Qintr) / (y_in_r[14] + Qintr)
    y_in1[14] = y_in_r[14] + Qintr

    if numberstep % 15 == 0.0:
        reactin[[number]] = y_in1

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)

    if numberstep % 15 == 0.0:
        react1[[number]] = y_out1
        react2[[number]] = y_out2
        react3[[number]] = y_out3
        react4[[number]] = y_out4
        react5[[number]] = y_out5

    ys_in = y_out5
    ys_in[14] = ys_in[14] - Qintr
    ys_out, ys_out_all = settler.outputs(timestep, step, ys_in)
    if numberstep % 15 == 0.0:
        settlerout[[number]] = ys_out
        settlerall[[number]] = ys_out_all
        number = number + 1

    numberstep = numberstep + 1


stop = time.perf_counter()

print('Simulationszeit: ', stop - start)
print('Output bei t = 609 d: ', ys_out)

start_writer = time.perf_counter()
wb = Workbook()
ws = wb.new_sheet("yin", data=reactin)
ws = wb.new_sheet("yout1", data=react1)
ws = wb.new_sheet("yout2", data=react2)
ws = wb.new_sheet("yout3", data=react3)
ws = wb.new_sheet("yout4", data=react4)
ws = wb.new_sheet("yout5", data=react5)
ws = wb.new_sheet("ysout", data=settlerout)
ws = wb.new_sheet("ysout_all", data=settlerall)
wb.save("results_all_LT_1min.xlsx")

# output_all = [react1[number-1], react2[number-1], react3[number-1], react4[number-1], react5[number-1], settlerout[number-1], settler.ys0]
#
# wb2 = Workbook()
# ws = wb2.new_sheet("sheet1", data=output_all)
# wb2.save("results_ode.xlsx")

stop_writer = time.perf_counter()

print('Zeit für Excel: ', stop_writer - start_writer)

