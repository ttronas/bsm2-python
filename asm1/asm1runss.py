"""Execution file for asm1 model with second clarifier in steady state simulation

This script will run the plant (ams1 model + settling model) to steady state. The results are saved as excel (.xlsx)
file and are necessary for further simulation.

This script requires that the following packages are installed within the Python environment you are running this script
in: 'numpy', 'pyexcelerate', 'scipy.integrate', 'numba'.

The parameters 'DECAY', 'SETTLER', 'TEMPMODEL' and 'ACTIVATE' can be set to 'True' if you want to activate them.
"""


import numpy as np
import time         # dieses Package am Ende immernoch?
import asm1init
import settler1dinit_asm1
import asm1
import settler1d_asm1

DECAY = False       # if DECAY is True the decay of heterotrophs and autotrophs is depending on the electron acceptor present
                    # if DECAY is False the decay do not change

SETTLER = False     # if SETTLER is False the settling model is non-reactive
                    # if SETTLER is True the settling model is reactive

TEMPMODEL = False   # if TEMPMODEL is False influent wastewater temperature is just passed through process reactors
                    # if TEMPMODEL is True mass balance for the wastewater temperature is used in process reactors

ACTIVATE = False    # if ACTIVATE is False dummy states are 0
                    # if ACTIVATE is True dummy states are activated


# definition of the reactors:
reactor1 = asm1.ASM1reactor(asm1init.KLa1, asm1init.VOL1, asm1init.SOSAT1, asm1init.YINIT1, asm1init.PAR1, TEMPMODEL, ACTIVATE, DECAY)
reactor2 = asm1.ASM1reactor(asm1init.KLa2, asm1init.VOL2, asm1init.SOSAT2, asm1init.YINIT2, asm1init.PAR2, TEMPMODEL, ACTIVATE, DECAY)
reactor3 = asm1.ASM1reactor(asm1init.KLa3, asm1init.VOL3, asm1init.SOSAT3, asm1init.YINIT3, asm1init.PAR3, TEMPMODEL, ACTIVATE, DECAY)
reactor4 = asm1.ASM1reactor(asm1init.KLa4, asm1init.VOL4, asm1init.SOSAT4, asm1init.YINIT4, asm1init.PAR4, TEMPMODEL, ACTIVATE, DECAY)
reactor5 = asm1.ASM1reactor(asm1init.KLa5, asm1init.VOL5, asm1init.SOSAT5, asm1init.YINIT5, asm1init.PAR5, TEMPMODEL, ACTIVATE, DECAY)
settler = settler1d_asm1.Settler(settler1dinit_asm1.DIM, settler1dinit_asm1.LAYER, asm1init.Qr, asm1init.Qw, settler1dinit_asm1.SETTLERINIT, settler1dinit_asm1.SETTLERPAR, asm1init.PAR1, TEMPMODEL, DECAY, SETTLER)

# CONSTINFLUENT:
y_in = np.array([30, 69.5000000000000, 51.2000000000000, 202.320000000000, 28.1700000000000, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 10.5900000000000, 7, 211.267500000000, 18446, 15, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

y_out5 = np.zeros(21)
ys_out = np.zeros(21)
ys_in = np.zeros(21)
Qintr = 0


start = time.perf_counter()

for step in simtime:
    y_in_r = (y_in*y_in[14]+ys_out*ys_out[14])/(y_in[14]+ys_out[14])
    y_in_r[14] = y_in[14] + ys_out[14]
    y_in1 = (y_in_r*y_in_r[14]+y_out5*Qintr)/(y_in_r[14]+Qintr)
    y_in1[14] = y_in_r[14]+Qintr

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)

    Qintr = asm1init.Qintr

    ys_in[0:14] = y_out5[0:14]
    ys_in[14] = y_out5[14] - Qintr
    ys_in[15:21] = y_out5[15:21]
    if ys_in[14] < 0.0:
        ys_in[14] = 0.0

    ys_out, ys_out_all = settler.outputs(timestep, step, ys_in)

stop = time.perf_counter()

print('Simulationszeit: ', stop - start)
print('Output bei t = 200 d: ', ys_out)

# start_writer = time.perf_counter()

# output = [y_out1, y_out2, y_out3, y_out4, y_out5, ys_out, settler.ys0]
#
# wb2 = Workbook()
# ws = wb2.new_sheet("sheet1", data=output)
# wb2.save("results_ss_ode.xlsx")
#
# stop_writer = time.perf_counter()
#
# print('Zeit für Excel: ', stop_writer - start_writer)

