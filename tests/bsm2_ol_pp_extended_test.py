import logging
import time

import numpy as np
from tqdm import tqdm

import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
import bsm2_python.bsm2.init.reginit_bsm2 as reginit
from bsm2_python.bsm2.plantperformance_extended import PlantPerformance
from bsm2_python.bsm2_ol_PP import BSM2OLPP
from bsm2_python.log import logger


def test_bsm2_ol_pp():
    plant = BSM2OLPP(endtime=20, timestep=1 / 60 / 24, tempmodel=False, activate=False)
    start = time.perf_counter()
    for idx, _ in enumerate(tqdm(plant.simtime)):
        plant.step(idx)
    stop = time.perf_counter()

    performance = PlantPerformance()

    # Defining the start and end day for calculation
    starting_day = 15
    end_day = 20

    # Calculate the absolute differences from start day and end day
    differences_start = np.abs(plant.IQI_all[:, 1] - starting_day)
    differences_end = np.abs(plant.IQI_all[:, 1] - end_day)

    # If you need all indices that are equally close to start day and end day
    closest_indices_start = np.where(differences_start == np.min(differences_start))[0]
    closest_indices_end = np.where(differences_end == np.min(differences_end))[0]

    # EQI and IQI calculation
    totalt = plant.IQI_all[closest_indices_end[0], 1] - plant.IQI_all[closest_indices_start[0], 1]
    iqi = np.sum(plant.IQI_all[closest_indices_start[0] : closest_indices_end[0], 0]) / totalt
    eqi = np.sum(plant.EQI_all[closest_indices_start[0] : closest_indices_end[0], 0]) / totalt
    logger.info('EQI = ', eqi, ' IQI = ', iqi)

    # Total TSS and Sludge production per day
    totsludgeprodperd, tssproducedperd = performance.sludge_production(
        plant.y_out1_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.y_out2_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.y_out3_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.y_out4_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.y_out5_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.ys_r_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.ys_was_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.ys_of_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.yp_internal_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.yd_out_all[
            closest_indices_start[0] : closest_indices_end[0], :
        ],  # FIXME: yd_out_all is not what we want (it needs to be yi_out2 to make sense for index [13])
        plant.yst_out_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.yst_vol_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.ydw_s_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.timestep[0],
        [starting_day, end_day],
    )

    logger.info('Totsludgeprodperd = ', totsludgeprodperd, 'TSSproducedperd = ', tssproducedperd)

    # Total carbon mass production per day
    carbonmassperd = performance.carbon_source(
        len(plant.y_in_all[closest_indices_start[0] : closest_indices_end[0], :]),
        plant.timestep[0],
        [starting_day, end_day],
    )
    logger.info('carbonmassperd = ', carbonmassperd)

    # Methane, Hydrogen, Carbon dioxide and total gas flow rate calculation
    methaneprodperd, hydrogenprodperd, carbondioxideprodperd, qgasav = performance.gas_production(
        plant.yd_out_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.timestep[0],
        [starting_day, plant.endtime],
    )
    logger.info(
        'Methaneprodperd = ',
        methaneprodperd,
        'Hydrogenprodperd = ',
        hydrogenprodperd,
        'Carbondioxideprodperd = ',
        carbondioxideprodperd,
        'Qgasav = ',
        qgasav,
    )

    # Total consume heat per day
    heatenergyperd = performance.heating_energy(
        plant.yp_uf_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.yt_uf_all[closest_indices_start[0] : closest_indices_end[0], :],
        plant.timestep[0],
        [starting_day, end_day],
    )
    logger.info('Heatenergyperd = ', heatenergyperd)

    # Mixing energy calculations
    kla1 = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * reginit.KLA1
    kla2 = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * reginit.KLA2
    kla3 = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * reginit.KLA3
    kla4 = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * reginit.KLA4
    kla5 = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * reginit.KLA5

    kla = [kla1, kla2, kla3, kla4, kla5]
    vol = [asm1init.VOL1, asm1init.VOL2, asm1init.VOL3, asm1init.VOL4, asm1init.VOL5]

    me, mixenergyperd = performance.mixingenergy(kla, vol, plant.timestep[0], [starting_day, end_day])

    logger.info('mixenergyreac = ', me, 'mixenergyperd = ', mixenergyperd)

    # Pumping energy calculation
    qintr = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * asm1init.QINTR
    qrflow = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * asm1init.QR
    qwflow = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * asm1init.QW
    quprimaryflow = plant.yp_uf_all[closest_indices_start[0] : closest_indices_end[0], 14]
    quthickenerflow = plant.yt_uf_all[closest_indices_start[0] : closest_indices_end[0], 14]
    qodewateringflow = plant.ydw_s_all[closest_indices_start[0] : closest_indices_end[0], 14]

    pf_qintr = 0.004  # kWh/m3, pumping energy factor, internal AS recirculation
    pf_qr = 0.008  # kWh/m3, pumping energy factor, AS sludge recycle
    pf_qw = 0.05  # kWh/m3, pumping energy factor, AS wastage flow
    pf_qpu = 0.075  # kWh/m3, pumping energy factor, pumped underflow from primary clarifier
    pf_qtu = 0.060  # kWh/m3, pumping energy factor, pumped underflow from thickener
    pf_qdo = 0.004  # kWh/m3, pumping energy factor, pumped underflow from dewatering unit

    flow = np.array(
        [sum(qintr), sum(qrflow), sum(qwflow), sum(quprimaryflow), sum(quthickenerflow), sum(qodewateringflow)]
    )
    pumpfactor = np.array([pf_qintr, pf_qr, pf_qw, pf_qpu, pf_qtu, pf_qdo])

    pump_energy = performance.pumpingenergy(flow, pumpfactor, plant.timestep[0], [starting_day, end_day])

    logger.info('Pumpingenergy = ', pump_energy)

    # Aeration energy per day
    kla1 = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * reginit.KLA1
    kla2 = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * reginit.KLA2
    kla3 = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * reginit.KLA3
    kla4 = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * reginit.KLA4
    kla5 = np.ones(len(plant.y_eff_all[closest_indices_start[0] : closest_indices_end[0], 0])) * reginit.KLA5

    kla = [kla1, kla2, kla3, kla4, kla5]

    aerationenergy = performance.aerationenergy(
        kla,
        np.array([asm1init.VOL1, asm1init.VOL2, asm1init.VOL3, asm1init.VOL4, asm1init.VOL5]),
        np.array([asm1init.SOSAT1, asm1init.SOSAT2, asm1init.SOSAT3, asm1init.SOSAT4, asm1init.SOSAT5]),
        plant.timestep[0],
        [starting_day, end_day],
    )

    logger.info('aerationenergy', aerationenergy)

    # OCI calculation
    oci = performance.oci(
        tssproducedperd, aerationenergy, mixenergyperd, pump_energy, carbonmassperd, methaneprodperd, heatenergyperd
    )
    logger.info('OCI = ', oci)

    eval_array = [
        iqi,
        eqi,
        totsludgeprodperd,
        tssproducedperd,
        carbonmassperd,
        methaneprodperd,
        hydrogenprodperd,
        carbondioxideprodperd,
        qgasav,
        heatenergyperd,
        mixenergyperd,
        pump_energy,
        aerationenergy,
        oci,
    ]

    logging.info('Dynamic open loop simulation completed after: %s seconds', stop - start)
    logging.info('Effluent at t = %s d: \n%s', plant.endtime, eval_array)

    # Values from 50 days dynamic simulation in Matlab (bsm2_ol_test.slx):
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

    logging.info(
        'Effluent difference to MatLab solution: \nIQI: %s\nEQI: \
        %s\nTotsludgeprodperd: %s\nTSSproducedperd: %s\ncarbonmassperd: %s\nMethaneprodperd: \
            %s\nHydrogenprodperd: %s\nCarbondioxideprodperd: %s\nQgasav: %s\nHeatenergyperd: \
                %s\nmixenergyperd: %s\nPumpingenergy: %s\naerationenergy: %s\nOCI: %s',
        *eval_par_matlab - eval_array,
    )

    assert np.allclose(eval_array, eval_par_matlab, rtol=25e-2, atol=1e0)


test_bsm2_ol_pp()
