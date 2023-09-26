"""Execution file for asm3 model with second clarifier in steady state simulation

This script will run the plant (ams3 model + settling model) to steady state. The results are saved as csv file and
are necessary for further dynamic simulations.

This script requires that the following packages are installed within the Python environment you are running this script
in: 'numpy', 'csv', 'time', 'scipy.integrate', 'numba'.

The parameters 'tempmodel' and 'activate' can be set to 'True' if you want to activate them.
"""

import numpy as np
import csv
import time
import asm3init
import settler1dinit_asm3
import asm3
import settler1d_asm3
import plantperformance


tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated


# definition of the reactors:
reactor1 = asm3.ASM3reactor(asm3init.par1, asm3init.yinit1, asm3init.kla1, asm3init.vol1, asm3init.carb1, asm3init.carbonsourceconc, tempmodel, activate)
reactor2 = asm3.ASM3reactor(asm3init.par2, asm3init.yinit2, asm3init.kla2, asm3init.vol2, asm3init.carb2, asm3init.carbonsourceconc, tempmodel, activate)
reactor3 = asm3.ASM3reactor(asm3init.par3, asm3init.yinit3, asm3init.kla3, asm3init.vol3, asm3init.carb3, asm3init.carbonsourceconc, tempmodel, activate)
reactor4 = asm3.ASM3reactor(asm3init.par4, asm3init.yinit4, asm3init.kla4, asm3init.vol4, asm3init.carb4, asm3init.carbonsourceconc, tempmodel, activate)
reactor5 = asm3.ASM3reactor(asm3init.par5, asm3init.yinit5, asm3init.kla5, asm3init.vol5, asm3init.carb5, asm3init.carbonsourceconc, tempmodel, activate)
settler = settler1d_asm3.Settler(settler1dinit_asm3.dim, settler1dinit_asm3.layer, asm3init.Qr, asm3init.Qw, settler1dinit_asm3.settlerinit, settler1dinit_asm3.settlerpar, asm3init.par5, tempmodel)

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

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Effluent at t = 200 d: ', ys_eff)


with open('asm3_values_ss.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerow(y_out1[0:20])
    writer.writerow(y_out2[0:20])
    writer.writerow(y_out3[0:20])
    writer.writerow(y_out4[0:20])
    writer.writerow(y_out5[0:20])
    writer.writerow(ys_out)
    writer.writerow(ys_eff)
    writer.writerow(settler.ys0)



# plant performance:
evaltime = np.array([0, 2*timestep])
# aerationenergy:
kla = np.zeros((5, 2))
kla[0] = np.array([reactor1.kla, reactor1.kla])
kla[1] = np.array([reactor2.kla, reactor2.kla])
kla[2] = np.array([reactor3.kla, reactor3.kla])
kla[3] = np.array([reactor4.kla, reactor4.kla])
kla[4] = np.array([reactor5.kla, reactor5.kla])
vol = np.array([[reactor1.volume], [reactor2.volume], [reactor3.volume], [reactor4.volume], [reactor5.volume]])
sosat = np.array([[asm3init.SOSAT1], [asm3init.SOSAT2], [asm3init.SOSAT3], [asm3init.SOSAT4], [asm3init.SOSAT5]])

ae = plantperformance.aerationenergy(kla, vol, sosat, timestep, evaltime)

# pumping energy:
pumpfactor = np.array([[0.004], [0.008], [0.05]])
flows = np.zeros((3, 2))
flows[0] = np.array([asm3init.Qintr, asm3init.Qintr])
flows[1] = np.array([asm3init.Qr, asm3init.Qr])
flows[2] = np.array([asm3init.Qw, asm3init.Qw])

pe = plantperformance.pumpingenergy(flows, pumpfactor, timestep, evaltime)

# mixing energy:
me = plantperformance.mixingenergy(kla, vol, timestep, evaltime)

# SNH limit violations:
SNH_eff = np.array(ys_eff[3], ys_eff[3])
SNH_limit = 4
SNH_violationvalues = plantperformance.violation(SNH_eff, SNH_limit, timestep, evaltime)

# TSS limit violations:
TSS_eff = np.array(ys_eff[12], ys_eff[12])
TSS_limit = 30
TSS_violationvalues = plantperformance.violation(TSS_eff, TSS_limit, timestep, evaltime)

# totalN limit violations:
totalN_eff = np.array(ys_eff[21], ys_eff[21])
totalN_limit = 18
totalN_violationvalues = plantperformance.violation(totalN_eff, totalN_limit, timestep, evaltime)

# COD limit violations:
COD_eff = np.array(ys_eff[22], ys_eff[22])
COD_limit = 100
COD_violationvalues = plantperformance.violation(COD_eff, COD_limit, timestep, evaltime)

# BOD5 limit violations:
BOD5_eff = np.array(ys_eff[23], ys_eff[23])
BOD5_limit = 10
BOD5_violationvalues = plantperformance.violation(BOD5_eff, BOD5_limit, timestep, evaltime)

data = [[ae], [pe], [me], SNH_violationvalues, TSS_violationvalues, totalN_violationvalues, COD_violationvalues, BOD5_violationvalues]
names = ['aeration energy [kWh/d]', 'pumping energy [kWh/d]', 'mixing energy [kWh/d]', 'SNH: days of violation / percentage of time', 'TSS: days of violation / percentage of time', 'totalN: days of violation / percentage of time', 'COD: days of violation / percentage of time', 'BOD5: days of violation / percentage of time']

with open('evaluation_ss.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    for name, datarow in zip(names, data):
        output_row = [name]
        output_row.extend(datarow)
        writer.writerow(output_row)