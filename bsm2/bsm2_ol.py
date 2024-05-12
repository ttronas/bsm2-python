"""
Execution file for bsm2 model with primary clarifier,
5 asm1-reactors and a second clarifier, sludge thickener,
adm1-fermenter and sludge storage in steady state simulation

This script will run the plant in an open loop simulation (no control) with dynamic input data.

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
from bsm2.asm1_bsm2 import ASM1reactor
import bsm2.asm1init_bsm2 as asm1init
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
from bsm2.plantperformance import PlantPerformance

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

# dyninfluent from BSM2:
with open(path_name + '/../data/dyninfluent_bsm2.csv', 'r') as f:
    data_in = np.array(list(csv.reader(f, delimiter=","))).astype(np.float64)

# timesteps = np.diff(data_in[:, 0], append=(2*data_in[-1, 0] - data_in[-2, 0]))
timestep = 15/24/60  # 15 minutes in days
endtime = 50  # data_in[-1, 0]
data_time = data_in[:, 0]
simtime = np.arange(0, endtime, timestep)

y_in = data_in[:, 1:]
del data_in

yst_sp_p = np.zeros(21)
yt_sp_p = np.zeros(21)
ys_r = np.zeros(21)
yst_sp_as = np.zeros(21)
yt_sp_as = np.zeros(21)
y_out5_r = np.zeros(21)

y_in_all = np.zeros((len(simtime), 21))
y_eff_all = np.zeros((len(simtime), 21))
y_in_bp_all = np.zeros((len(simtime), 21))
to_primary_all = np.zeros((len(simtime), 21))
prim_in_all = np.zeros((len(simtime), 21))
qpass_plant_all = np.zeros((len(simtime), 21))
qpassplant_to_as_all = np.zeros((len(simtime), 21))
qpassAS_all = np.zeros((len(simtime), 21))
to_as_all = np.zeros((len(simtime), 21))
feed_settler_all = np.zeros((len(simtime), 21))
qthick2AS_all = np.zeros((len(simtime), 21))
qthick2prim_all = np.zeros((len(simtime), 21))
qstorage2AS_all = np.zeros((len(simtime), 21))
qstorage2prim_all = np.zeros((len(simtime), 21))
sludge_all = np.zeros((len(simtime), 21))

sludge_height = 0

y_out5_r[14] = asm1init.Qintr

start = time.perf_counter()

for i, step in enumerate(tqdm(simtime)):

    # timestep = timesteps[i]
    # get influent data that is smaller than and closest to current time step
    y_in_timestep = y_in[np.where(data_time <= step)[0][-1], :]

    yp_in_c, y_in_bp = input_splitter.outputs(y_in_timestep, (0, 0), reginit.Qbypass)
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

    y_in_all[i] = y_in_timestep
    y_eff_all[i] = y_eff
    y_in_bp_all[i] = y_in_bp
    to_primary_all[i] = yp_in_c
    prim_in_all[i] = yp_in
    qpass_plant_all[i] = y_plant_bp
    qpassplant_to_as_all[i] = y_in_as_c
    qpassAS_all[i] = y_as_bp_c_eff
    to_as_all[i] = y_bp_as
    feed_settler_all[i] = ys_in
    qthick2AS_all[i] = yt_sp_as
    qthick2prim_all[i] = yt_sp_p
    qstorage2AS_all[i] = yst_sp_as
    qstorage2prim_all[i] = yst_sp_p
    sludge_all[i] = ydw_s

stop = time.perf_counter()