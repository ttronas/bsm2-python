from matplotlib import pyplot as plt
from tqdm import tqdm
import time

from bsm2_python.bsm2_cl import BSM2CL as BSM2CL_Old
from bsm2_python.bsm2_cl_2 import BSM2CL as BSM2CL_New
from bsm2_python.log import logger


def compare_models():
    # Create objects of both models and correspoding lists
    bsm2_cl_old = BSM2CL_Old(endtime=5, timestep=1 / 60 / 24, tempmodel=False, activate=False)
    bsm2_cl_new = BSM2CL_New(endtime=5, timestep=1 / 60 / 24, tempmodel=False, activate=False)

    kla3_list_old = []
    kla3_list_new = []

    # Create empty plot
    plt.ion()
    fig, ax = plt.subplots(figsize=(10, 5))
    (line_old,) = ax.plot([], [], label='Model Old', linewidth=2, color='b')
    (line_new,) = ax.plot([], [], label='Model New', linewidth=2, color='r', linestyle='--')
    ax.set_xlabel('Time')
    ax.set_ylabel('KLA3_a')
    ax.legend()
    ax.grid(True)
    plt.tight_layout()

    # Running both models
    print('----------Running Old Model----------')
    start_old = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm2_cl_old.simtime)):
        bsm2_cl_old.step(idx)
        kla3_list_old.append(bsm2_cl_old.kla3_a)
        # Update plot
        if idx % 10 == 0:  # Update every 10 iterations
            line_old.set_data(bsm2_cl_old.simtime[: idx + 1], kla3_list_old[: idx + 1])
            ax.relim()
            ax.autoscale_view()
            plt.pause(0.001)
    stop_old = time.perf_counter()
    logger.info('Old Dynamic open loop simulation completed after: %s seconds', stop_old - start_old)

    print('----------Running New Model----------')
    start_new = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm2_cl_new.simtime)):
        bsm2_cl_new.step(idx)
        kla3_list_new.append(bsm2_cl_new.kla3_a)
        # Update plot
        if idx % 10 == 0:
            line_new.set_data(bsm2_cl_new.simtime[: idx + 1], kla3_list_new[: idx + 1])
            ax.relim()
            ax.autoscale_view()
            plt.pause(0.001)
    stop_new = time.perf_counter()
    logger.info('New Dynamic open loop simulation completed after: %s seconds', stop_new - start_new)

    # Final Plot
    line_old.set_data(bsm2_cl_old.simtime, kla3_list_old)
    line_new.set_data(bsm2_cl_new.simtime, kla3_list_new)
    ax.relim()
    ax.autoscale_view()
    plt.ioff()
    plt.show()

    # Displaying difference in runtime
    runtime_bsm2_cl_new = stop_new - start_new
    runtime_bsm2_cl_old = stop_old - start_old

    if runtime_bsm2_cl_new > runtime_bsm2_cl_old:
        runtime_diff = runtime_bsm2_cl_new - runtime_bsm2_cl_old
        logger.info(f'The old model was {runtime_diff} seconds faster than the new model')
    else:
        runtime_diff = runtime_bsm2_cl_old - runtime_bsm2_cl_new
        logger.info(f'The new model was {runtime_diff} seconds faster than the old model')


compare_models()
