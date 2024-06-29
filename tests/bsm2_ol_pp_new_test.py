# %%
import time

import numpy as np
from tqdm import tqdm

import bsm2_python.bsm2.init.adm1init_bsm2 as adm1init
import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
import bsm2_python.bsm2.init.plantperformanceinit_bsm2 as pp_init
import bsm2_python.bsm2.init.reginit_bsm2 as reginit
from bsm2_python.bsm2.plantperformance_new import PlantPerformance
from bsm2_python.bsm2_ol_pp import BSM2OLPP
from bsm2_python.log import logger

SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = np.arange(21)


bsm2_ol_pp = BSM2OLPP(endtime=20, timestep=15 / 60 / 24, tempmodel=False, activate=False)
evaltime = np.array([15, 20])
eval_idx = evaltime * int(60/15) * 24
num_eval_timesteps = eval_idx[1] - eval_idx[0]
performance = PlantPerformance(pp_init.PP_PAR, bsm2_ol_pp.simtime, evaltime)
pe_flow_all = np.zeros((len(bsm2_ol_pp.simtime), 6))
pumpingenergy_all = np.zeros(len(bsm2_ol_pp.simtime))
aerationenergy_all = np.zeros(len(bsm2_ol_pp.simtime))
mixingenergy_all = np.zeros(len(bsm2_ol_pp.simtime))
iqi_all = np.zeros(len(bsm2_ol_pp.simtime))
eqi_all = np.zeros(len(bsm2_ol_pp.simtime))
violation_all = np.zeros(len(bsm2_ol_pp.simtime))
tss_mass_bsm2_all = np.zeros(len(bsm2_ol_pp.simtime))
y_eff_tss_flow_all = np.zeros(len(bsm2_ol_pp.simtime))
ydw_s_tss_flow_all = np.zeros(len(bsm2_ol_pp.simtime))
added_carbon_mass_all = np.zeros(len(bsm2_ol_pp.simtime))
ch4_prod_all = np.zeros(len(bsm2_ol_pp.simtime))
h2_prod_all = np.zeros(len(bsm2_ol_pp.simtime))
co2_prod_all = np.zeros(len(bsm2_ol_pp.simtime))
q_gas_all = np.zeros(len(bsm2_ol_pp.simtime))
heat_yp_uf_all = np.zeros(len(bsm2_ol_pp.simtime))
heat_yt_uf_all = np.zeros(len(bsm2_ol_pp.simtime))
oci_all = np.zeros(len(bsm2_ol_pp.simtime))
ones = np.ones(len(bsm2_ol_pp.simtime))
start = time.perf_counter()
for idx, _ in enumerate(tqdm(bsm2_ol_pp.simtime)):
    bsm2_ol_pp.step(idx)
    pe_flow = np.array(
        [
            asm1init.QINTR,
            asm1init.QR,
            asm1init.QW,
            bsm2_ol_pp.yp_uf_all[idx, 14],
            bsm2_ol_pp.yt_uf_all[idx, 14],
            bsm2_ol_pp.ydw_s_all[idx, 14],
        ]
    )
    pe_flow_all[idx] = pe_flow
    klas = np.array([reginit.KLA1, reginit.KLA2, reginit.KLA3, reginit.KLA4, reginit.KLA5])
    vols = np.array([asm1init.VOL1, asm1init.VOL2, asm1init.VOL3, asm1init.VOL4, asm1init.VOL5, adm1init.V_LIQ])
    sosat = np.array([asm1init.SOSAT1, asm1init.SOSAT2, asm1init.SOSAT3, asm1init.SOSAT4, asm1init.SOSAT5])
    pumpingenergy_all[idx] = performance.pumpingenergy_step(pe_flow, pp_init.PP_PAR[10:16])
    aerationenergy_all[idx] = performance.aerationenergy_step(klas, vols[0:5], sosat)
    mixingenergy_all[idx] = performance.mixingenergy_step(klas, vols, pp_init.PP_PAR[16])
    iqi_all[idx] = performance.qi(bsm2_ol_pp.y_in_all[idx], eqi=False)[0]
    eqi_all[idx] = performance.qi(bsm2_ol_pp.y_eff_all[idx], eqi=True)[0]
    violation_all[idx] = performance.violation_step(bsm2_ol_pp.y_eff_all[idx, SNH], 4)[0][0]
    tss_mass_bsm2_all[idx] = performance.tss_mass_bsm2(
        bsm2_ol_pp.yp_of_all[idx],
        bsm2_ol_pp.yp_uf_all[idx],
        bsm2_ol_pp.yp_internal_all[idx],
        bsm2_ol_pp.y_out1_all[idx],
        bsm2_ol_pp.y_out2_all[idx],
        bsm2_ol_pp.y_out3_all[idx],
        bsm2_ol_pp.y_out4_all[idx],
        bsm2_ol_pp.y_out5_all[idx],
        bsm2_ol_pp.ys_r_all[idx],
        bsm2_ol_pp.ys_was_all[idx],
        bsm2_ol_pp.ys_of_all[idx],
        bsm2_ol_pp.yd_out_all[idx],
        bsm2_ol_pp.yst_out_all[idx],
        bsm2_ol_pp.yst_vol_all[idx],
    )[0]
    y_eff_tss_flow_all[idx] = performance.tss_flow(bsm2_ol_pp.y_eff_all[idx])
    ydw_s_tss_flow_all[idx] = performance.tss_flow(bsm2_ol_pp.ydw_s_all[idx])
    carb = reginit.CARB1 + reginit.CARB2 + reginit.CARB3 + reginit.CARB4 + reginit.CARB5
    added_carbon_mass_all[idx] = performance.added_carbon_mass(carb, reginit.CARBONSOURCECONC)
    ch4_prod_all[idx], h2_prod_all[idx], co2_prod_all[idx], q_gas_all[idx] = performance.gas_production(
        bsm2_ol_pp.yd_out_all[idx], reginit.T_OP
    )
    sludge_flow_comb = (
        bsm2_ol_pp.yp_uf_all[idx] * bsm2_ol_pp.yp_uf_all[idx, 14]
        + bsm2_ol_pp.yt_uf_all[idx] * bsm2_ol_pp.yt_uf_all[idx, 14]
    ) / (bsm2_ol_pp.yp_uf_all[idx, 14] + bsm2_ol_pp.yt_uf_all[idx, 14])
    heat_test = performance.heat_demand_step(sludge_flow_comb, reginit.T_OP)[0]
    heat_yp_uf_all[idx] = performance.heat_demand_step(bsm2_ol_pp.yp_uf_all[idx], reginit.T_OP)[0]
    heat_yt_uf_all[idx] = performance.heat_demand_step(bsm2_ol_pp.yt_uf_all[idx], reginit.T_OP)[0]
    heat = heat_yp_uf_all[idx] + heat_yt_uf_all[idx]
    oci_all[idx] = performance.oci(
        pumpingenergy_all[idx],
        aerationenergy_all[idx],
        mixingenergy_all[idx],
        ydw_s_tss_flow_all[idx],
        added_carbon_mass_all[idx],
        heat,
        ch4_prod_all[idx],
    )
stop = time.perf_counter()
# save bsm2_ol_pp.yp_uf_all and bsm2_ol_pp.yt_uf_all to a npz file
np.savez('bsm2_ol_pp.yp_uf_all.npz', yp_uf_all=bsm2_ol_pp.yp_uf_all)
np.savez('bsm2_ol_pp.yt_uf_all.npz', yt_uf_all=bsm2_ol_pp.yt_uf_all)
# %%
pumpingenergy = np.sum(pumpingenergy_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps * 24  # 24 to get kWh/day
pe_flow_compare = np.sum(pe_flow_all[eval_idx[0] : eval_idx[1]], axis=0)
pumpingenergy_compare = performance.pumpingenergy(pe_flow_compare, pp_init.PP_PAR[10:16], bsm2_ol_pp.timestep[0])
logger.info('Pumping energy = %s \n Pumping energy compare = %s', str(pumpingenergy), str(pumpingenergy_compare))

aerationenergy = np.sum(aerationenergy_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps * 24
aerationenergy_compare = performance.aerationenergy(
    np.outer(ones[eval_idx[0] : eval_idx[1]], klas), vols[0:5], sosat, bsm2_ol_pp.timestep[0], evaltime
)
logger.info('Aeration energy = %s \n Aeration energy compare = %s', str(aerationenergy), str(aerationenergy_compare))

mixingenergy = np.sum(mixingenergy_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps * 24
mixingenergy_compare = performance.mixingenergy(
    np.outer(ones[eval_idx[0] : eval_idx[1]], klas), vols, bsm2_ol_pp.timestep[0], evaltime, pp_init.PP_PAR[16]
)
logger.info('Mixing energy = %s \n Mixing energy compare = %s', str(mixingenergy), str(mixingenergy_compare))

iqi = np.sum(iqi_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps
eqi = np.sum(eqi_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps
logger.info('EQI = %s \n IQI = %s', str(eqi), str(iqi))

violation = np.zeros(2)
violation[0] = np.sum(violation_all[eval_idx[0] : eval_idx[1]]) / 60 / 24  # / 60 / 24 to get violations/day
violation[1] = np.sum(violation_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps * 100  # to get percentage
violation_compare = performance.violation(
    bsm2_ol_pp.y_eff_all[eval_idx[0] : eval_idx[1], SNH], 4, bsm2_ol_pp.timestep[0], evaltime
)
logger.info('Violation step = %s \n Violation compare = %s', str(violation), str(violation_compare))

tot_tss_mass_bsm2 = (
    np.sum(ydw_s_tss_flow_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps
    + (tss_mass_bsm2_all[eval_idx[1]] - tss_mass_bsm2_all[eval_idx[0]]) / (evaltime[-1] - evaltime[0])
)
tot_sludge_prod = (
    (np.sum(y_eff_tss_flow_all[eval_idx[0] : eval_idx[1]]) + np.sum(ydw_s_tss_flow_all[eval_idx[0] : eval_idx[1]]))
    / num_eval_timesteps
    + (tss_mass_bsm2_all[eval_idx[1]] - tss_mass_bsm2_all[eval_idx[0]]) / (evaltime[-1] - evaltime[0])
)
logger.info('Totsludgeprodperd = %s \n TSSproducedperd = %s', str(tot_sludge_prod), str(tot_tss_mass_bsm2))

carb_mass = np.sum(added_carbon_mass_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps
logger.info('carbonmassperd = %s', str(carb_mass))

ch4_prod = np.sum(ch4_prod_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps
h2_prod = np.sum(h2_prod_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps
co2_prod = np.sum(co2_prod_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps
q_gas = np.sum(q_gas_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps
logger.info(
    'Methaneprodperd = %s \n Hydrogenprodperd = %s \n Carbondioxideprodperd = %s \n Qgasav = %s',
    str(ch4_prod),
    str(h2_prod),
    str(co2_prod),
    str(q_gas),
)

heat_demand = (
    np.sum(heat_yp_uf_all[eval_idx[0] : eval_idx[1]] + heat_yt_uf_all[eval_idx[0] : eval_idx[1]])
    / num_eval_timesteps
    * 24
)  # 24 to get kWh/day
heat_demand_compare = performance.heat_demand(
    bsm2_ol_pp.yp_uf_all[eval_idx[0] : eval_idx[1]],
    bsm2_ol_pp.yt_uf_all[eval_idx[0] : eval_idx[1]],
    bsm2_ol_pp.timestep[0],
    evaltime,
)
logger.info('Heatenergyperd = %s \n Heatenergyperd compare = %s', heat_demand, heat_demand_compare)

oci = np.sum(oci_all[eval_idx[0] : eval_idx[1]]) / num_eval_timesteps
logger.info('OCI = %s', str(oci))

logger.info('Dynamic open loop simulation completed after: %s seconds', stop - start)
eval_array = [
    iqi,
    eqi,
    tot_sludge_prod,
    tot_tss_mass_bsm2,
    carb_mass,
    ch4_prod,
    h2_prod,
    co2_prod,
    q_gas,
    heat_demand,
    mixingenergy,
    pumpingenergy,
    aerationenergy,
    oci,
]
eval_par_matlab = np.array(
    [
        8.0174e04,  # IQI kg/d
        1.4753e04,  # EQI kg/d
        4.6529e03,  # Totsludgeprodperd kgSS/d
        3.6767e03,  # TSSproducedperd kgSS/d
        8.0000e02,  # carbonmassperd kgCOD/d
        1.0210e03,  # Methaneprodperd kgCH4/d
        0.0040,  # Hydrogenprodperd kgH2/d
        1.4955e03,  # Carbondioxideprodperd kgCO2/d
        2.6103e03,  # Qgasav m^3/d
        7.4179e03,  # Heatenergyperd kWh/d
        768.0000,  # mixenergyperd kWh/d
        450.7097,  # Pumpingenergy kWh/d
        4000,  # aerationenergy kWh/d
        1.2794e04,  # OCI
    ]
)
logger.info(
    'Effluent difference to MatLab solution: \nIQI: %s\nEQI: %s\nTotsludgeprodperd: %s\nTSSproducedperd: %s\n\
        carbonmassperd: %s\nMethaneprodperd: %s\nHydrogenprodperd: %s\nCarbondioxideprodperd: %s\nQgasav: %s\n\
            Heatenergyperd: %s\nmixenergyperd: %s\nPumpingenergy: %s\naerationenergy: %s\nOCI: %s',
    *eval_par_matlab - eval_array,
)

logger.info(
    'Fraction Effluent / Matlab solution: \nIQI: %s\nEQI: %s\nTotsludgeprodperd: %s\nTSSproducedperd: %s\n\
        carbonmassperd: %s\nMethaneprodperd: %s\nHydrogenprodperd: %s\nCarbondioxideprodperd: %s\nQgasav: %s\n\
            Heatenergyperd: %s\nmixenergyperd: %s\nPumpingenergy: %s\naerationenergy: %s\nOCI: %s',
    *eval_par_matlab / eval_array,
)

# %%
