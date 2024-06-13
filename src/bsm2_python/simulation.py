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

import logging
logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(levelname)-8s %(message)s',
        level=logging.INFO,
        datefmt='%H:%M:%S',
        stream=sys.stdout)
logging.root.setLevel(logging.INFO)

from bsm2_olem import BSM2_OLEM

TOTAL_SIM_STEPS = 35028

logging.info(str(TOTAL_SIM_STEPS) + " sim steps\n")

logging.info("Initialize bsm2\n")

timestep = 15/24/60  # 15 minutes in days
endtime = TOTAL_SIM_STEPS * timestep

tempmodel = False   # if tempmodel is False influent wastewater temperature is just passed through process reactors and settler
                    # if tempmodel is True mass balance for the wastewater temperature is used in process reactors and settler

activate = False    # if activate is False dummy states are 0
                    # if activate is True dummy states are activated

bsm2 = BSM2_OLEM(timestep=timestep, endtime=endtime, tempmodel=tempmodel, activate=activate)

logging.info("Stabilize bsm2\n")

bsm2.stabilize()

logging.info("Start simulation\n")
for i in range(0, TOTAL_SIM_STEPS):
    bsm2.step(i, True)

    if i % 1000 == 0:
        logging.info("timestep: " + str(i) + " of " + str(TOTAL_SIM_STEPS) + "\n")

    if i == TOTAL_SIM_STEPS - 1:
        bsm2.finish_evaluation()
        logging.info("Simulation finished\n")
        break
