"""Execution file for asm1 model with second clarifier in steady state simulation

This script will run the plant (ams1 model + settling model) to steady state.

This script requires that the following packages are installed within the Python environment you are running this script
in: 'numpy', 'csv', 'time', 'scipy.integrate', 'numba'.

The parameters 'tempmodel' and 'activate' can be set to 'True' if you want to activate them.
"""
import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')

import numpy as np
import time
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


tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated


# definition of the objects:
input_splitter = Splitter()
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
adm1_reactor = ADM1Reactor(adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, adm1init.DIM_D)
dewatering = Dewatering(dewateringinit.DEWATERINGPAR)
storage = Storage(storageinit.VOL_S, storageinit.ystinit, tempmodel, activate)
splitter_storage = Splitter()

# CONSTINFLUENT from BSM2:
y_in = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

yp_of = np.zeros(25)
yp_uf = np.zeros(21)
y_c_as_bp = np.zeros(21)
y_out1 = np.zeros(21)
y_out2 = np.zeros(21)
y_out3 = np.zeros(21)
y_out4 = np.zeros(21)
y_out5 = np.zeros(21)
y_out5_r = np.zeros(21)
ys_r = np.zeros(21)
ys_was = np.zeros(21)
ys_of = np.zeros(25)
y_eff = np.zeros(21)
yt_in = np.zeros(21)
yt_uf = np.zeros(21)
yt_of = np.zeros(21)
yt_sp_as = np.zeros(21)
yt_sp_p = np.zeros(21)
ys_in = np.zeros(21)
yst_in = np.zeros(21)
yst_out = np.zeros(21)
yst_sp_p = np.zeros(21)
yst_sp_as = np.zeros(21)
Qintr = asm1init.Qintr
sludge_height = 0


start = time.perf_counter()

for step in simtime:

    yp_in_c, y_in_bp = input_splitter.outputs(y_in, np.array([y_in[14]- reginit.Qbypass, reginit.Qbypass]))
    y_in_as, y_plant_bp = bypass_plant.outputs(y_in_bp, np.array([y_in_bp[14] - reginit.Qbypassplant, reginit.Qbypassplant]))

    yp_in = combiner_primclar_pre.output(yp_in_c, yst_sp_p, yt_sp_p)
    yp_uf, yp_of = primclar.outputs(timestep, step, yp_in)
    y_c_as_bp = combiner_primclar_post.output(yp_of[:21], y_in_as)
    y_as_bp_c_eff, y_as_bp = bypass_reactor.outputs(y_c_as_bp, np.array([y_c_as_bp[14] - reginit.QbypassAS, reginit.QbypassAS]))
    
    y_in1 = combiner_reactor.output(ys_r, y_as_bp, yst_sp_as, yt_sp_as)
    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)
    ys_in, y_out5_r = splitter_reactor.outputs(y_out5, np.array([y_out5[14] - asm1init.Qintr, asm1init.Qintr]))

    ys_r, ys_was, ys_of, sludge_height = settler.outputs(timestep, step, ys_in)

    y_eff = combiner_effluent.output(y_plant_bp, y_as_bp_c_eff, ys_of[:21])

    yt_uf, yt_of = thickener.outputs(ys_was)
    yt_sp_p, yt_sp_as = splitter_thickener.outputs(yt_of[:21], np.array([yt_of[14] - reginit.Qthickener2AS, reginit.Qthickener2AS]))

    y_out2, _, _ = adm1_reactor.outputs(timestep, step, yt_uf, reginit.T_op)
    ydw_s, ydw_r = dewatering.outputs(y_out2)
    yst_out = storage.output(timestep, step, yst_in, reginit.Qstorage)

    yst_sp_p, yst_sp_as = splitter_storage.outputs(yst_out, np.array([yst_out[14] - reginit.Qstorage2AS, reginit.Qstorage2AS]))
stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Effluent at t = 200 d:  \n', y_eff)
print('Sludge height at t = 200 d:  \n', sludge_height)

y_eff_matlab = np.array([30.6576079091768, 0.803552804256930, 3.09124292484164, 0.142713283391346, 8.30442587915406, 0.918856159066539, 1.43595752043470, 0.688300722946280, 26.1866889987896, 1.34139306275546, 0.684317039035914, 0.0104203958259101, 2.89588189824968, 10.4198968251662, 18440.7870053519, 15.0000000000001, 0, 0, 0, 0, 0])
sludge_height_matlab = 0.447178539974702
print('Effluent difference to MatLab solution: \n', y_eff_matlab - y_eff[:21])
print('Sludge height difference to MatLab solution: \n', sludge_height_matlab - sludge_height)


assert np.allclose(y_eff[:21], y_eff_matlab, rtol=1e-5, atol=1e-5)
