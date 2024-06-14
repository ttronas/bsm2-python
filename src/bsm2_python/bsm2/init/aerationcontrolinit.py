"""Initialisation file for all states and parameters related to the aeration control system in reactor 3 to 5

All parameters and specifications are based on BSM1 model.

This file will be executed when running asm1runss_ac.py, asm1run_ac.py, asm1runss_ps.py or asm1run_ps.py.
"""

import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init

# maximum possible external carbon flow rate to reactors
CARB1_MAX = 5
CARB2_MAX = 5
CARB3_MAX = 5
CARB4_MAX = 5
CARB5_MAX = 5

# maximum pump capacities
QINTR_MAX = 5 * asm1init.QIN0
QW_MAX = 0.1 * asm1init.QIN0
QR_MAX = 2 * asm1init.QIN0
QSTORAGE_MAX = 1500
# time delay for artificial Qw actuator (acts as first-order filter)
QWT = 1 / 60 / 24 * 10

KLA3GAIN = 1.0  # gain for control signal to reactor 3

# values for KLa actuator 3:
T90_KLA3 = 4  # REsponse time 4 minutes
T_KLA3 = T90_KLA3 / (60 * 24) / 3.89

# initial values for sensor 4:
T90_SO4 = 1  # Response time 1 min
MIN_SO4 = 0
MAX_SO4 = 10
T_SO4 = T90_SO4 / (60 * 24) / 3.89
STD_SO4 = 0.025

# values for PI controller 4:
KLA4_INIT = 201.3015557168598
KLA4_MIN = 0
KLA4_MAX = 360
KSO4 = 25  # Amplification, 500 in BSM1 book
TISO4 = 0.002  # I-part time constant (d = 2.88 min)), integral time constant, 0.001 in BSM1 book
TTSO4 = 0.001  # Antiwindup time constant (d), tracking time constant, 0.0002 in BSM1 book
SO4INTSTATE = -321.7493546935257
SO4AWSTATE = 379.05091041032915
SO4REF = 2  # setpoint for controller, mg (-COD)/l
KLA4OFFSET = 120  # reasonable offset value for control around SO4ref
KLA4_LIM = 201.3015557168598
KLA4_CALC = 201.3015557168598
USEANTIWINDUPSO4 = True  # False=no antiwindup, True=use antiwindup for oxygen control

# values for KLa actuator 4:
T90_KLA4 = 4  # Response time 4 minutes
T_KLA4 = T90_KLA4 / (60 * 24) / 3.89

KLA5GAIN = 0.5  # gain for control signal to reactor 5

# values for KLa actuator 5:
T90_KLA5 = 4  # Response time 4 minutes
T_KLA5 = T90_KLA5 / (60 * 24) / 3.89
