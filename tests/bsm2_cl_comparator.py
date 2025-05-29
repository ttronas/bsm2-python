import time

import matplotlib.pyplot as plt
from tqdm import tqdm

from bsm2_python.bsm2_cl import BSM2CL
from bsm2_python.log import logger


def compare_bsm2_cl():
    # Creating BMS2CL objects with different timesteps
    bsm2_cl_1 = BSM2CL(endtime=5, timestep=1 / 60 / 24, tempmodel=False, activate=False)
    bsm2_cl_2 = BSM2CL(endtime=5, timestep=2 / 60 / 24, tempmodel=False, activate=False)
    bsm2_cl_3 = BSM2CL(endtime=5, timestep=3 / 60 / 24, tempmodel=False, activate=False)

    # Creating a list of KLA3 values for each object
    kla3_list1 = []
    kla3_list2 = []
    kla3_list3 = []

    # Running the simulation for each object
    logger.info('-----Simulating with timestep 1/60/24-----')
    start1 = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm2_cl_1.simtime)):
        bsm2_cl_1.step(idx)
        kla3_list1.append(bsm2_cl_1.kla3_a)
    stop1 = time.perf_counter()
    logger.info('Dynamic open loop simulation completed after: %s seconds', stop1 - start1)

    logger.info('-----Simulating with timestep 2/60/24-----')
    start2 = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm2_cl_2.simtime)):
        bsm2_cl_2.step(idx)
        kla3_list2.append(bsm2_cl_2.kla3_a)
    stop2 = time.perf_counter()
    logger.info('Dynamic open loop simulation completed after: %s seconds', stop2 - start2)

    logger.info('-----Simulating with timestep 3/60/24-----')
    start3 = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm2_cl_3.simtime)):
        bsm2_cl_3.step(idx)
        kla3_list3.append(bsm2_cl_3.kla3_a)
    stop3 = time.perf_counter()
    logger.info(f'Dynamic loop simulation completed after: {stop3 - start3} seconds')

    # Plotting the KLA3 values for each object
    plt.figure(figsize=(10, 5))
    plt.xlabel('Time')
    plt.ylabel('KLA3')
    plt.title(label='KLA3 values for different timesteps')
    plt.plot(bsm2_cl_1.simtime, kla3_list1, label='1/60/24', color='blue', linestyle='-')
    plt.plot(bsm2_cl_2.simtime, kla3_list2, label='2/60/24', color='orange', linestyle='--')
    plt.plot(bsm2_cl_3.simtime, kla3_list3, label='3/60/24', color='green', linestyle='-.')
    plt.legend()
    plt.grid()
    plt.show()


compare_bsm2_cl()
