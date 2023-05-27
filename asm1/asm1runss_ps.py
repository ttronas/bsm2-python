"""Execution file for asm1 model with second clarifier and aeration control in reactor 3, 4 and 5 in steady state simulation

This script will run the plant (ams1 model + settling model + aeration control model) to steady state. The results are
saved as csv file and are necessary for further dynamic simulations.

This script requires that the following packages are installed within the Python environment you are running this script
in: 'numpy', 'csv', 'time', 'scipy.integrate', 'numba', 'scipy'.

The parameters 'tempmodel' and 'activate' can be set to 'True' if you want to activate them.
"""

import numpy as np
import csv
import time
import asm1init
import settler1dinit_asm1
import asm1
import settler1d_asm1
import aerationcontrol
import aerationcontrolinit
import plantperformance


tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if ACTIVATE is False dummy states are 0
                    # if ACTIVATE is True dummy states are activated


# definition of the reactors:
reactor1 = asm1.ASM1reactor(asm1init.KLa1, asm1init.VOL1, asm1init.yinit1, asm1init.PAR1, asm1init.carb1, asm1init.carbonsourceconc, tempmodel, activate)
reactor2 = asm1.ASM1reactor(asm1init.KLa2, asm1init.VOL2, asm1init.yinit2, asm1init.PAR2, asm1init.carb2, asm1init.carbonsourceconc, tempmodel, activate)
reactor3 = asm1.ASM1reactor(asm1init.KLa3, asm1init.VOL3, asm1init.yinit3, asm1init.PAR3, asm1init.carb3, asm1init.carbonsourceconc, tempmodel, activate)
reactor4 = asm1.ASM1reactor(asm1init.KLa4, asm1init.VOL4, asm1init.yinit4, asm1init.PAR4, asm1init.carb4, asm1init.carbonsourceconc, tempmodel, activate)
reactor5 = asm1.ASM1reactor(asm1init.KLa5, asm1init.VOL5, asm1init.yinit5, asm1init.PAR5, asm1init.carb5, asm1init.carbonsourceconc, tempmodel, activate)
settler = settler1d_asm1.Settler(settler1dinit_asm1.DIM, settler1dinit_asm1.LAYER, asm1init.Qr, asm1init.Qw, settler1dinit_asm1.settlerinit, settler1dinit_asm1.SETTLERPAR, asm1init.PAR1, tempmodel)

aerationcontrol3 = aerationcontrol.PIaeration(aerationcontrolinit.KLa3_min, aerationcontrolinit.KLa3_max, aerationcontrolinit.KSO3, aerationcontrolinit.TiSO3, aerationcontrolinit.TtSO3, aerationcontrolinit.SO3ref, aerationcontrolinit.KLa3offset, aerationcontrolinit.SO3intstate, aerationcontrolinit.SO3awstate, aerationcontrolinit.kla3_lim, aerationcontrolinit.kla3_calc)
aerationcontrol4 = aerationcontrol.PIaeration(aerationcontrolinit.KLa4_min, aerationcontrolinit.KLa4_max, aerationcontrolinit.KSO4, aerationcontrolinit.TiSO4, aerationcontrolinit.TtSO4, aerationcontrolinit.SO4ref, aerationcontrolinit.KLa4offset, aerationcontrolinit.SO4intstate, aerationcontrolinit.SO4awstate, aerationcontrolinit.kla4_lim, aerationcontrolinit.kla4_calc)
aerationcontrol5 = aerationcontrol.PIaeration(aerationcontrolinit.KLa5_min, aerationcontrolinit.KLa5_max, aerationcontrolinit.KSO5, aerationcontrolinit.TiSO5, aerationcontrolinit.TtSO5, aerationcontrolinit.SO5ref, aerationcontrolinit.KLa5offset, aerationcontrolinit.SO5intstate, aerationcontrolinit.SO5awstate, aerationcontrolinit.kla_lim, aerationcontrolinit.kla_calc)

# CONSTINFLUENT:
y_in = np.array([30, 69.5000000000000, 51.2000000000000, 202.320000000000, 28.1700000000000, 0, 0, 0, 0, 31.5600000000000, 6.95000000000000, 10.5900000000000, 7, 211.267500000000, 18446, 15, 0, 0, 0, 0, 0])

timestep = 1/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

y_out5 = np.zeros(21)
ys_out = np.zeros(21)
ys_in = np.zeros(21)
Qintr = 0

kla3 = asm1init.KLa3
kla4 = asm1init.KLa4
kla5 = asm1init.KLa5

start = time.perf_counter()

for step in simtime:
    y_in_r = (y_in*y_in[14]+ys_out*ys_out[14])/(y_in[14]+ys_out[14])
    y_in_r[14] = y_in[14] + ys_out[14]
    y_in1 = (y_in_r*y_in_r[14]+y_out5*Qintr)/(y_in_r[14]+Qintr)
    y_in1[14] = y_in_r[14]+Qintr

    reactor3.kla = kla3
    reactor4.kla = kla4
    reactor5.kla = kla5

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)

    kla3 = aerationcontrol3.output(y_out3[7], step, timestep)
    kla4 = aerationcontrol4.output(y_out4[7], step, timestep)
    kla5 = aerationcontrol5.output(y_out5[7], step, timestep)

    Qintr = asm1init.Qintr

    ys_in[0:14] = y_out5[0:14]
    ys_in[14] = y_out5[14] - Qintr
    ys_in[15:21] = y_out5[15:21]
    if ys_in[14] < 0.0:
        ys_in[14] = 0.0

    ys_out, ys_eff = settler.outputs(timestep, step, ys_in)

stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start)
print('Effluent at t = 200 d: ', ys_eff)


with open('asm1_values_ss_ps.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerow(y_out1)
    writer.writerow(y_out2)
    writer.writerow(y_out3)
    writer.writerow(y_out4)
    writer.writerow(y_out5)
    writer.writerow(ys_out)
    writer.writerow(ys_eff)
    writer.writerow(settler.ys0)

aerationvalues = np.zeros((3, 5))
aerationvalues[0] = np.array([kla3, aerationcontrol3.SOintstate, aerationcontrol3.SOawstate, aerationcontrol3.kla_lim, aerationcontrol3.kla_calc])
aerationvalues[1] = np.array([kla4, aerationcontrol4.SOintstate, aerationcontrol4.SOawstate, aerationcontrol4.kla_lim, aerationcontrol4.kla_calc])
aerationvalues[2] = np.array([kla5, aerationcontrol5.SOintstate, aerationcontrol5.SOawstate, aerationcontrol5.kla_lim, aerationcontrol5.kla_calc])
with open('asm1_aerationvalues_ss_ps.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    writer.writerows(aerationvalues)

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

with open('evaluation_ps_ss.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=' ')
    for name, datarow in zip(names, data):
        output_row = [name]
        output_row.extend(datarow)
        writer.writerow(output_row)
