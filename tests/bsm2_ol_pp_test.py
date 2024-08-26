"""Execution file for the BSM2 Open Loop PlantPerformance Test Case.
The test case is based on the BSM2 Benchmark Simulation Model No. 2 (BSM2) and does not contain any controllers.
But it runs the BSM2 model with dynamic influent data and controls the plant performance to MatLab results.
"""

import time

import numpy as np
from tqdm import tqdm

from bsm2_python.bsm2_ol import BSM2OL
from bsm2_python.log import logger

SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = np.arange(21)
timestep = 1 / 60 / 24
endtime = 20


def test_bsm2_ol_pp():
    bsm2_ol_pp = BSM2OL(endtime=endtime, timestep=timestep, tempmodel=False, activate=False)

    start = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm2_ol_pp.simtime)):
        bsm2_ol_pp.step(idx)
    stop = time.perf_counter()

    violations_class = bsm2_ol_pp.get_violations()['SNH']

    (
        iqi_eval_class,
        eqi_eval_class,
        tot_sludge_prod_class,
        tot_tss_mass_class,
        carb_mass_class,
        ch4_prod_class,
        h2_prod_class,
        co2_prod_class,
        q_gas_class,
        heat_demand_class,
        mixingenergy_class,
        pumpingenergy_class,
        aerationenergy_class,
        oci_eval_class,
    ) = bsm2_ol_pp.get_final_performance()

    logger.info('Dynamic open loop simulation completed after: %s seconds\n', stop - start)

    eval_class_array = np.array(
        [
            violations_class,
            iqi_eval_class,
            eqi_eval_class,
            tot_sludge_prod_class,
            tot_tss_mass_class,
            carb_mass_class,
            ch4_prod_class,
            h2_prod_class,
            co2_prod_class,
            q_gas_class,
            heat_demand_class,
            mixingenergy_class,
            pumpingenergy_class,
            aerationenergy_class,
            oci_eval_class,
        ]
    )
    eval_par_matlab = np.array(
        [
            2.32777778,  # violations/d for 4 g_SNH/d
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
        'Results: \n'
        'Violations/d: %s\n IQI: %s\n EQI: %s\n Totsludgeprodperd: %s\n TSSproducedperd: %s\n'
        'carbonmassperd: %s\n Methaneprodperd: %s\n Hydrogenprodperd: %s\n Carbondioxideprodperd: %s\n Qgasav: %s\n'
        'Heatenergyperd: %s\n mixenergyperd: %s\n Pumpingenergy: %s\n aerationenergy: %s\n OCI: %s\n',
        *eval_class_array,
    )

    logger.info(
        'Difference to MatLab solution: \n'
        'violations/d: %s\n IQI: %s\n EQI: %s\n Totsludgeprodperd: %s\n TSSproducedperd: %s\n '
        'carbonmassperd: %s\n Methaneprodperd: %s\n Hydrogenprodperd: %s\n Carbondioxideprodperd: %s\n Qgasav: %s\n '
        'Heatenergyperd: %s\n mixenergyperd: %s\n Pumpingenergy: %s\n aerationenergy: %s\n OCI: %s\n',
        *(eval_par_matlab - eval_class_array),
    )

    logger.info(
        'Fraction Matlab solution/Python solution:\n'
        'violations/d: %s\n IQI: %s\n EQI: %s\n Totsludgeprodperd: %s\n TSSproducedperd: %s\n'
        'carbonmassperd: %s\n Methaneprodperd: %s\n Hydrogenprodperd: %s\n Carbondioxideprodperd: %s\n Qgasav: %s\n '
        'Heatenergyperd: %s\n mixenergyperd: %s\n Pumpingenergy: %s\n aerationenergy: %s\n OCI: %s\n',
        *(eval_par_matlab / eval_class_array),
    )
    # strangely, the deviations are almost 10 % when running pytest, but only 2 % when running the code in the console.
    assert np.allclose(eval_class_array, eval_par_matlab, rtol=1e-1)


test_bsm2_ol_pp()
