"""Execution file for asm3 model with second clarifier in steady state simulation

This script will run the plant (ams3 model + settling model) to steady state. The results are saved as excel (.xlsx)
file and are necessary for further simulation.

This script requires that the following packages are installed within the Python environment you are running this script
in: 'numpy', 'csv', 'scipy.integrate', 'numba'.

The parameters 'TEMPMODEL' and 'ACTIVATE' can be set to 'True' if you want to activate them.
"""


import numpy as np
import csv
import time         # dieses Package am Ende immernoch?
import asm3init
import settler1dinit_asm3
import asm3
import settler1d_asm3


tempmodel = False   # if TEMPMODEL is False influent wastewater temperature is just passed through process reactors
                    # if TEMPMODEL is True mass balance for the wastewater temperature is used in process reactors

activate = False    # if ACTIVATE is False dummy states are 0
                    # if ACTIVATE is True dummy states are activated


# definition of the reactors:
reactor1 = asm3.ASM3reactor(asm3init.par1, asm3init.yinit1, asm3init.kla1, asm3init.vol1, asm3init.carb1, asm3init.carbonsourceconc, tempmodel, activate)
reactor2 = asm3.ASM3reactor(asm3init.par2, asm3init.yinit2, asm3init.kla2, asm3init.vol2, asm3init.carb2, asm3init.carbonsourceconc, tempmodel, activate)
reactor3 = asm3.ASM3reactor(asm3init.par3, asm3init.yinit3, asm3init.kla3, asm3init.vol3, asm3init.carb3, asm3init.carbonsourceconc, tempmodel, activate)
reactor4 = asm3.ASM3reactor(asm3init.par4, asm3init.yinit4, asm3init.kla4, asm3init.vol4, asm3init.carb4, asm3init.carbonsourceconc, tempmodel, activate)
reactor5 = asm3.ASM3reactor(asm3init.par5, asm3init.yinit5, asm3init.kla5, asm3init.vol5, asm3init.carb5, asm3init.carbonsourceconc, tempmodel, activate)
settler = settler1d_asm3.Settler(settler1dinit_asm3.dim, settler1dinit_asm3.layer, asm3init.Qr, asm3init.Qw, settler1dinit_asm3.settlerinit, settler1dinit_asm3.settlerpar, tempmodel)

# CONSTINFLUENT:
y_in = np.array([0,	30, 69.5000000000000, 31.5600000000000, 0, 0, 7, 51.2000000000000, 202.320000000000, 28.1700000000000, 0, 0, 215.493000000000, 18446, 15, 0, 0,	0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

y_out5 = np.zeros(20)
ys_out = np.zeros(20)
ys_in = np.zeros(20)
Qintr = 0

start = time.perf_counter()

for step in simtime:
    y_in_r = (y_in*y_in[13]+ys_out[0:20]*ys_out[13])/(y_in[13]+ys_out[13])
    y_in_r[13] = y_in[13] + ys_out[13]
    y_in1 = (y_in_r*y_in_r[13]+y_out5[0:20]*Qintr)/(y_in_r[13]+Qintr)
    y_in1[13] = y_in_r[13]+Qintr

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1[0:20])
    y_out3 = reactor3.output(timestep, step, y_out2[0:20])
    y_out4 = reactor4.output(timestep, step, y_out3[0:20])
    y_out5 = reactor5.output(timestep, step, y_out4[0:20])

    Qintr = asm3init.Qintr

    ys_in[0:13] = y_out5[0:13]
    ys_in[13] = y_out5[13] - Qintr
    ys_in[14:20] = y_out5[14:20]
    if ys_in[13] < 0.0:
        ys_in[13] = 0.000001
    ys_out, ys_eff = settler.outputs(timestep, step, ys_in)

stop = time.perf_counter()

print('Simulationszeit: ', stop - start)
print('Output bei t = 200 d: ', ys_out, ys_eff)
print('TSS Output: ', settler.ys0[70:80])

start_writer = time.perf_counter()

# with open('asm3_values_ss_val.csv', 'w', newline='') as csvfile:
#     writer = csv.writer(csvfile, delimiter=' ')
#     writer.writerow(y_out1[0:20])
#     writer.writerow(y_out2[0:20])
#     writer.writerow(y_out3[0:20])
#     writer.writerow(y_out4[0:20])
#     writer.writerow(y_out5[0:20])
#     writer.writerow(ys_out)
#     writer.writerow(ys_eff)
#     writer.writerow(settler.ys0)
#
stop_writer = time.perf_counter()

print('Zeit für Excel: ', stop_writer - start_writer)

