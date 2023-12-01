"""
Execution file for bsm2 model with primary clarifier,
5 asm1-reactors and a second clarifier, sludge thickener,
adm1-fermenter and sludge storage in steady state simulation

This script will run the plant to steady state. The results are saved as csv file and
are necessary for further dynamic simulations.

This script requires that the packages from requirements.txt are installed
within the Python environment you are running this script.

The parameters 'tempmodel' and 'activate' can be set to 'True' if you want to activate them.
"""
import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')

import numpy as np
import time
import csv
from bsm2.primclar_bsm2 import PrimaryClarifier
from bsm2 import primclarinit_bsm2 as primclarinit
from asm1.asm1 import ASM1reactor
import asm1.asm1init as asm1init
from bsm2.settler1d_bsm2 import Settler
import bsm2.settler1dinit_bsm2 as settler1dinit
from bsm2.thickener_bsm2 import Thickener
import bsm2.thickenerinit_bsm2 as thickenerinit
from bsm2.adm1_bsm2 import ADM1Reactor
import bsm2.adm1init_bsm2 as adm1init
from bsm2.dewatering_bsm2 import Dewatering
import bsm2.dewateringinit_bsm2 as dewateringinit
from bsm2.storage_bsm2 import Storage
import bsm2.storageinit_bsm2 as storageinit
from bsm2.helpers_bsm2 import Combiner, Splitter
import bsm2.reginit_bsm2 as reginit
from asm1.plantperformance import PlantPerformance

tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated

# definition of the objects:
input_splitter = Splitter(sp_type=2)
bypass_plant = Splitter()
combiner_primclar_pre = Combiner()
primclar = PrimaryClarifier(primclarinit.VOL_P, primclarinit.yinit1, primclarinit.PAR_P, asm1init.PAR1, primclarinit.XVECTOR_P, tempmodel, activate)
combiner_primclar_post = Combiner()
bypass_reactor = Splitter()
combiner_reactor = Combiner()
reactor1 = ASM1reactor(reginit.KLa1, asm1init.VOL1, asm1init.yinit1, asm1init.PAR1, asm1init.carb1, asm1init.carbonsourceconc, tempmodel, activate)
reactor2 = ASM1reactor(reginit.KLa2, asm1init.VOL2, asm1init.yinit2, asm1init.PAR2, asm1init.carb2, asm1init.carbonsourceconc, tempmodel, activate)
reactor3 = ASM1reactor(reginit.KLa3, asm1init.VOL3, asm1init.yinit3, asm1init.PAR3, asm1init.carb3, asm1init.carbonsourceconc, tempmodel, activate)
reactor4 = ASM1reactor(reginit.KLa4, asm1init.VOL4, asm1init.yinit4, asm1init.PAR4, asm1init.carb4, asm1init.carbonsourceconc, tempmodel, activate)
reactor5 = ASM1reactor(reginit.KLa5, asm1init.VOL5, asm1init.yinit5, asm1init.PAR5, asm1init.carb5, asm1init.carbonsourceconc, tempmodel, activate)
splitter_reactor = Splitter()
settler = Settler(settler1dinit.DIM, settler1dinit.LAYER, asm1init.Qr, asm1init.Qw, settler1dinit.settlerinit, settler1dinit.SETTLERPAR, asm1init.PAR1, tempmodel, settler1dinit.MODELTYPE)
combiner_effluent = Combiner()
thickener = Thickener(thickenerinit.THICKENERPAR, asm1init.PAR1)
splitter_thickener = Splitter()
combiner_adm1 = Combiner()
adm1_reactor = ADM1Reactor(adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, adm1init.DIM_D)
dewatering = Dewatering(dewateringinit.DEWATERINGPAR)
storage = Storage(storageinit.VOL_S, storageinit.ystinit, tempmodel, activate)
splitter_storage = Splitter()

plantperformance = PlantPerformance()

# CONSTINFLUENT from BSM2:
y_in = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

yst_sp_p = np.zeros(21)
yt_sp_p = np.zeros(21)
ys_r = np.zeros(21)
yst_sp_as = np.zeros(21)
yt_sp_as = np.zeros(21)
y_out5_r = np.zeros(21)

sludge_height = 0

y_out5_r[14] = asm1init.Qintr

start = time.perf_counter()

for step in simtime:

    yp_in_c, y_in_bp = input_splitter.outputs(y_in, (0, 0), reginit.Qbypass)
    y_plant_bp, y_in_as_c = bypass_plant.outputs(y_in_bp, (1 - reginit.Qbypassplant, reginit.Qbypassplant))
    yp_in = combiner_primclar_pre.output(yp_in_c, yst_sp_p, yt_sp_p)
    yp_uf, yp_of = primclar.outputs(timestep, step, yp_in)
    y_c_as_bp = combiner_primclar_post.output(yp_of[:21], y_in_as_c)
    y_bp_as, y_as_bp_c_eff = bypass_reactor.outputs(y_c_as_bp, (1 - reginit.QbypassAS, reginit.QbypassAS))

    y_in1 = combiner_reactor.output(ys_r, y_bp_as, yst_sp_as, yt_sp_as, y_out5_r)
    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)
    ys_in, y_out5_r = splitter_reactor.outputs(y_out5, (y_out5[14] - asm1init.Qintr, asm1init.Qintr))

    ys_r, ys_was, ys_of, sludge_height = settler.outputs(timestep, step, ys_in)

    y_eff = combiner_effluent.output(y_plant_bp, y_as_bp_c_eff, ys_of[:21])

    yt_uf, yt_of = thickener.outputs(ys_was)
    yt_sp_p, yt_sp_as = splitter_thickener.outputs(yt_of[:21], (1 - reginit.Qthickener2AS, reginit.Qthickener2AS))

    yd_in = combiner_adm1.output(yt_uf, yp_uf)
    y_out2, _, _ = adm1_reactor.outputs(timestep, step, yd_in, reginit.T_op)
    ydw_s, ydw_r = dewatering.outputs(y_out2)
    yst_out, yst_vol = storage.output(timestep, step, ydw_r, reginit.Qstorage)

    yst_sp_p, yst_sp_as = splitter_storage.outputs(yst_out, (1 - reginit.Qstorage2AS, reginit.Qstorage2AS))

stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Effluent at t =', simtime, ' d:  \n', y_eff)
print('Sludge height at t = ', simtime, ' d:  \n', sludge_height)


with open(path_name + '/../data/bsm2_values_ss.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(primclar.yp0)
    writer.writerow(reactor1.y0)
    writer.writerow(reactor2.y0)
    writer.writerow(reactor3.y0)
    writer.writerow(reactor4.y0)
    writer.writerow(reactor5.y0)
    writer.writerow(settler.ys0)
    writer.writerow(adm1_reactor.yd0)
    writer.writerow(storage.yst0)

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
SNH_eff = np.array(ys_of[7], ys_of[7])
SNH_limit = 4
SNH_violationvalues = plantperformance.violation(SNH_eff, SNH_limit, timestep, evaltime)

# TSS limit violations:
TSS_eff = np.array(ys_of[13], ys_of[13])
TSS_limit = 30
TSS_violationvalues = plantperformance.violation(TSS_eff, TSS_limit, timestep, evaltime)

# totalN limit violations:
totalN_eff = np.array(ys_of[22], ys_of[22])
totalN_limit = 18
totalN_violationvalues = plantperformance.violation(totalN_eff, totalN_limit, timestep, evaltime)

# COD limit violations:
COD_eff = np.array(ys_of[23], ys_of[23])
COD_limit = 100
COD_violationvalues = plantperformance.violation(COD_eff, COD_limit, timestep, evaltime)

# BOD5 limit violations:
BOD5_eff = np.array(ys_of[24], ys_of[24])
BOD5_limit = 10
BOD5_violationvalues = plantperformance.violation(BOD5_eff, BOD5_limit, timestep, evaltime)

data = [[ae], [pe], [me], SNH_violationvalues, TSS_violationvalues, totalN_violationvalues, COD_violationvalues, BOD5_violationvalues]
names = ['aeration energy [kWh/d]', 'pumping energy [kWh/d]', 'mixing energy [kWh/d]', 'SNH: days of violation / percentage of time', 'TSS: days of violation / percentage of time', 'totalN: days of violation / percentage of time', 'COD: days of violation / percentage of time', 'BOD5: days of violation / percentage of time']

with open(path_name + '/../data/evaluation_ss.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for name, datarow in zip(names, data):
        output_row = [name]
        output_row.extend(datarow)
        writer.writerow(output_row)
