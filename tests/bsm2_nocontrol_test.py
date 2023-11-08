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
from bsm2.helpers_bsm2 import Combiner, Splitter


tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated


# definition of the objects:
input_splitter = Splitter()
combiner_primclar_pre = Combiner()
primclar = PrimaryClarifier(primclarinit.VOL_P, primclarinit.yinit1, primclarinit.PAR_P, asm1init.PAR1, primclarinit.XVECTOR_P, tempmodel, activate)
combiner_primclar_post = Combiner()
bypass_reactor = Splitter()
combiner_reactor = Combiner()
reactor1 = ASM1reactor(asm1init.KLa1, asm1init.VOL1, asm1init.yinit1, asm1init.PAR1, asm1init.carb1, asm1init.carbonsourceconc, tempmodel, activate)
reactor2 = ASM1reactor(asm1init.KLa2, asm1init.VOL2, asm1init.yinit2, asm1init.PAR2, asm1init.carb2, asm1init.carbonsourceconc, tempmodel, activate)
reactor3 = ASM1reactor(asm1init.KLa3, asm1init.VOL3, asm1init.yinit3, asm1init.PAR3, asm1init.carb3, asm1init.carbonsourceconc, tempmodel, activate)
reactor4 = ASM1reactor(asm1init.KLa4, asm1init.VOL4, asm1init.yinit4, asm1init.PAR4, asm1init.carb4, asm1init.carbonsourceconc, tempmodel, activate)
reactor5 = ASM1reactor(asm1init.KLa5, asm1init.VOL5, asm1init.yinit5, asm1init.PAR5, asm1init.carb5, asm1init.carbonsourceconc, tempmodel, activate)
reactor5 = ASM1reactor(asm1init.KLa5, asm1init.VOL5, asm1init.yinit5, asm1init.PAR5, asm1init.carb5, asm1init.carbonsourceconc, tempmodel, activate)
splitter_reactor = Splitter()
settler = Settler(settler1dinit.DIM, settler1dinit.LAYER, asm1init.Qr, asm1init.Qw, settler1dinit.settlerinit, settler1dinit.SETTLERPAR, asm1init.PAR1, tempmodel, settler1dinit.MODELTYPE)
combiner_effluent = Combiner()
thickener = Thickener(thickenerinit.THICKENERPAR, asm1init.PAR1)
splitter_thickener = Splitter()
adm1_reactor = ADM1Reactor(adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, adm1init.DIM_D)
dewatering = Dewatering(dewateringinit.DEWATERINGPAR)
splitter_storage = Splitter()

# CONSTINFLUENT from BSM2:
y_in = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])

timestep = 15/(60*24)
endtime = 200
simtime = np.arange(0, endtime, timestep)

yp_out = np.zeros(21)
yp_eff = np.zeros(25)
y_out1 = np.zeros(21)
y_out2 = np.zeros(21)
y_out3 = np.zeros(21)
y_out4 = np.zeros(21)
y_out5 = np.zeros(21)
y_out5_r = np.zeros(21)
ys_out = np.zeros(21)
ys_eff = np.zeros(25)
ys_in = np.zeros(21)
Qintr = asm1init.Qintr
sludge_height = 0


start = time.perf_counter()

for step in simtime:

    yp_out, yp_eff = primclar.outputs(timestep, step, y_in)

    y_in1 = combiner_reactor.output(y_in, ys_out, y_out5_r)

    y_out1 = reactor1.output(timestep, step, y_in1)
    y_out2 = reactor2.output(timestep, step, y_out1)
    y_out3 = reactor3.output(timestep, step, y_out2)
    y_out4 = reactor4.output(timestep, step, y_out3)
    y_out5 = reactor5.output(timestep, step, y_out4)

    ys_in, y_out5_r = splitter.outputs(y_out5, np.array([y_out5[14] - Qintr, Qintr]))

    ys_out, ys_was, ys_eff, sludge_height = settler.outputs(timestep, step, ys_in)

    yt_uf, yt_of = thickener.outputs(ys_was)

    y_out2, yd_out, y_out1 = adm1_reactor.outputs(timestep, step, y_in, adm1init.T_op)

    ydw_s, ydw_r = dewatering.outputs(y_in)

    # storage here

stop = time.perf_counter()

print('Steady state simulation completed after: ', stop - start, 'seconds')
print('Effluent at t = 200 d:  \n', ys_eff)
print('Sludge height at t = 200 d:  \n', sludge_height)

ys_eff_matlab = np.array([30.0000000000000, 0.889492799653682, 4.39182747787874, 0.188440413683379, 9.78152406404732, 0.572507856962265, 1.72830016782928, 0.490943515687561, 10.4152201204309, 1.73333146817512, 0.688280004678034, 0.0134804685779854, 4.12557938198182, 12.4969499853007, 18061, 15, 0, 0, 0, 0, 0])
sludge_height_matlab = 0.447178539974702
print('Effluent difference to MatLab solution: \n', ys_eff_matlab - ys_eff[:21])
print('Sludge height difference to MatLab solution: \n', sludge_height_matlab - sludge_height)


assert np.allclose(ys_eff[:21], ys_eff_matlab, rtol=1e-5, atol=1e-5)
assert np.allclose(sludge_height, sludge_height_matlab, rtol=1e-5, atol=1e-5)
