"""Initialisation file for all states and parameters related to the aeration control system in reactor 3 to 5

All parameters and specifications are based on BSM1 model.

This file will be executed when running asm1runss_ac.py, asm1run_ac.py, asm1runss_ps.py or asm1run_ps.py.
"""
import sys
import os
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')
from bsm2 import asm1init_bsm2 as asm1init

# maximum possible external carbon flow rate to reactors
carb1_max = 5 
carb2_max = 5
carb3_max = 5
carb4_max = 5
carb5_max = 5

# maximum pump capacities
Qintr_max = 5 * asm1init.Qin0
Qw_max = 0.1 * asm1init.Qin0
Qr_max = 2 * asm1init.Qin0
Qstorage_max = 1500
# time delay for artificial Qw actuator (acts as first-order filter)
QwT = 1/60/24 * 10

KLa3gain = 1.0  # gain for control signal to reactor 3

# values for KLa actuator 3:
T90_KLa3 = 4        # response time 4 minutes
T_KLa3 = T90_KLa3 / (60*24) / 3.89

# initial values for sensor 4:
T90_SO4 = 1     # response time 1 min
min_SO4 = 0
max_SO4 = 10
T_SO4 = T90_SO4 / (60*24) / 3.89
std_SO4 = 0.025

# values for PI controller 4:
kLa4_init = 201.3015557168598
KLa4_min = 0
KLa4_max = 360
KSO4 = 25  # Amplification, 500 in BSM1 book
TiSO4 = 0.002  # I-part time constant (d = 2.88 min)), integral time constant, 0.001 in BSM1 book
TtSO4 = 0.001  # Antiwindup time constant (d), tracking time constant, 0.0002 in BSM1 book
SO4intstate = -321.7493546935257
SO4awstate = 379.05091041032915
SO4ref = 2  # setpoint for controller, mg (-COD)/l
KLa4offset = 120  # reasonable offset value for control around SO4ref
kla4_lim = 201.3015557168598
kla4_calc = 201.3015557168598
useantiwindupSO4 = True  # False=no antiwindup, True=use antiwindup for oxygen control

# values for KLa actuator 4:
T90_KLa4 = 4        # response time 4 minutes
T_KLa4 = T90_KLa4 / (60*24) / 3.89

KLa5gain = 0.5  # gain for control signal to reactor 5

# values for KLa actuator 5:
T90_KLa5 = 4        # response time 4 minutes
T_KLa5 = T90_KLa5 / (60*24) / 3.89
