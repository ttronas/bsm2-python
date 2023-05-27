"""Initialisation file for all states and parameters related to the aeration control system in reactor 3 to 5

All parameters and specifications are based on BSM1 model.

This file will be executed when running asm1runss_ac.py, asm1run_ac.py, asm1runss_ps.py or asm1run_ps.py.
"""


# initial values for sensor 3:
T90_SO3 = 1     # response time 1 min
min_SO3 = 0
max_SO3 = 10
T_SO3 = T90_SO3 / (60*24) / 3.89
std_SO3 = 0.025

# values for PI controller 3:
KLa3_min = 0
KLa3_max = 360
KSO3 = 25
TiSO3 = 0.002
TtSO3 = 0.001
SO3intstate = 0
SO3awstate = 0
SO3ref = 2
KLa3offset = 144
kla3_lim = 0
kla3_calc = 0

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
KLa4_min = 0
KLa4_max = 360
KSO4 = 25
TiSO4 = 0.002
TtSO4 = 0.001
SO4intstate = 0
SO4awstate = 0
SO4ref = 2
KLa4offset = 144
kla4_lim = 0
kla4_calc = 0

# values for KLa actuator 4:
T90_KLa4 = 4        # response time 4 minutes
T_KLa4 = T90_KLa4 / (60*24) / 3.89

# initial values for sensor 5:
T90_SO5 = 1     # response time 1 min
min_SO5 = 0
max_SO5 = 10
T_SO5 = T90_SO5 / (60*24) / 3.89
std_SO5 = 0.025

# values for PI controller 5:
KLa5_min = 0
KLa5_max = 360
KSO5 = 25
TiSO5 = 0.002
TtSO5 = 0.001
SO5intstate = 0
SO5awstate = 0
SO5ref = 2
KLa5offset = 144
kla_lim = 0
kla_calc = 0

# values for KLa actuator 5:
T90_KLa5 = 4        # response time 4 minutes
T_KLa5 = T90_KLa5 / (60*24) / 3.89


