"""Execution file for bsm2 model with primary clarifier, 5 asm1-reactors and a second clarifier in steady state simulation

This script will run the plant (ams1 model + settling model) to steady state. The results are saved as csv file and
are necessary for further dynamic simulations.

This script requires that the following packages are installed within the Python environment you are running this script
in: 'numpy', 'csv', 'time', 'scipy.integrate', 'numba'.

The parameters 'tempmodel' and 'activate' can be set to 'True' if you want to activate them.
"""
import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')

import numpy as np
import csv
import time
import primclarinit_bsm2
from primclar_bsm2 import PrimaryClarifier
from settler1d_bsm2 import Settler
import asm1init_bsm2 as asm1init
import settler1dinit_bsm2 as settler1dinit
from asm1_bsm2 import ASM1reactor

from asm1.plantperformance import PlantPerformance

tempmodel = True   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated


# definition of the reactors:
primclar = PrimaryClarifier(primclarinit_bsm2.VOL_P, primclarinit_bsm2.yinit1, primclarinit_bsm2.PAR_P, asm1init.PAR1, primclarinit_bsm2.XVECTOR_P, tempmodel, activate)
reactor1 = ASM1reactor(asm1init.KLa1, asm1init.VOL1, asm1init.yinit1, asm1init.PAR1, asm1init.carb1, asm1init.carbonsourceconc, tempmodel, activate)
reactor2 = ASM1reactor(asm1init.KLa2, asm1init.VOL2, asm1init.yinit2, asm1init.PAR2, asm1init.carb2, asm1init.carbonsourceconc, tempmodel, activate)
reactor3 = ASM1reactor(asm1init.KLa3, asm1init.VOL3, asm1init.yinit3, asm1init.PAR3, asm1init.carb3, asm1init.carbonsourceconc, tempmodel, activate)
reactor4 = ASM1reactor(asm1init.KLa4, asm1init.VOL4, asm1init.yinit4, asm1init.PAR4, asm1init.carb4, asm1init.carbonsourceconc, tempmodel, activate)
reactor5 = ASM1reactor(asm1init.KLa5, asm1init.VOL5, asm1init.yinit5, asm1init.PAR5, asm1init.carb5, asm1init.carbonsourceconc, tempmodel, activate)
settler = Settler(settler1dinit.DIM, settler1dinit.LAYER, asm1init.Qr, asm1init.Qw, settler1dinit.settlerinit, settler1dinit.SETTLERPAR, asm1init.PAR1, tempmodel, settler1dinit.MODELTYPE)

plantperformance = PlantPerformance()

# CONSTINFLUENT from BSM1:
y_in = np.array([27.2261906234849, 58.1761856778940, 92.4990010554089, 363.943473006786, 50.6832881484832, 0, 0, 0, 0, 23.8594656340447, 5.65160603095694, 16.1298160611318, 7, 380.344321658009, 20648.3612112084, 14.8580800598190, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

y_out1 = np.zeros(21)
y_out2 = np.zeros(21)
y_out3 = np.zeros(21)
y_out4 = np.zeros(21)
y_out5 = np.zeros(21)
ys_out = np.zeros(21)
ys_eff = np.zeros(25)
ys_in = np.zeros(21)
Qintr = 0


start = time.perf_counter()

for step in simtime:
    y_in_r = (y_in*y_in[14]+ys_out*ys_out[14])/(y_in[14]+ys_out[14])
    y_in_r[14] = y_in[14] + ys_out[14]
    y_in1 = (y_in_r*y_in_r[14]+y_out5*Qintr)/(y_in_r[14]+Qintr)
    y_in1[14] = y_in_r[14]+Qintr

    yp_out, yp_eff = primclar.output(timestep, step, y_in1)

    y_out1 = reactor1.output(timestep, step, yp_eff[:21])
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)

    Qintr = asm1init.Qintr

    ys_in[0:14] = y_out5[0:14]
    ys_in[14] = y_out5[14] - Qintr
    ys_in[15:21] = y_out5[15:21]
    ys_in[14] = max(0, ys_in[14])

    ys_out, ys_eff = settler.outputs(timestep, step, ys_in)

stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Effluent at t = 200 d: \n', ys_eff)


with open('asm1_values_ss.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerow(y_out1)
    writer.writerow(y_out2)
    writer.writerow(y_out3)
    writer.writerow(y_out4)
    writer.writerow(y_out5)
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
sosat = np.array([[asm1init.SOSAT1], [asm1init.SOSAT2], [asm1init.SOSAT3], [asm1init.SOSAT4], [asm1init.SOSAT5]])

ae = plantperformance.aerationenergy(kla, vol, sosat, timestep, evaltime)

# pumping energy:
pumpfactor = np.array([[0.004], [0.008], [0.05]])
flows = np.zeros((3, 2))
flows[0] = np.array([asm1init.Qintr, asm1init.Qintr])
flows[1] = np.array([asm1init.Qr, asm1init.Qr])
flows[2] = np.array([asm1init.Qw, asm1init.Qw])

pe = plantperformance.pumpingenergy(flows, pumpfactor, timestep, evaltime)

# mixing energy:
me = plantperformance.mixingenergy(kla, vol, timestep, evaltime)

# SNH limit violations:
SNH_eff = np.array(ys_eff[7], ys_eff[7])
SNH_limit = 4
SNH_violationvalues = plantperformance.violation(SNH_eff, SNH_limit, timestep, evaltime)

# TSS limit violations:
TSS_eff = np.array(ys_eff[13], ys_eff[13])
TSS_limit = 30
TSS_violationvalues = plantperformance.violation(TSS_eff, TSS_limit, timestep, evaltime)

# totalN limit violations:
totalN_eff = np.array(ys_eff[22], ys_eff[22])
totalN_limit = 18
totalN_violationvalues = plantperformance.violation(totalN_eff, totalN_limit, timestep, evaltime)

# COD limit violations:
COD_eff = np.array(ys_eff[23], ys_eff[23])
COD_limit = 100
COD_violationvalues = plantperformance.violation(COD_eff, COD_limit, timestep, evaltime)

# BOD5 limit violations:
BOD5_eff = np.array(ys_eff[24], ys_eff[24])
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
