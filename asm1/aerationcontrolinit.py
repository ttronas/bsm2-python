import numpy as np
import pandas as pd

# initial values for sensor:
T90_SO5 = 1     # response time 1 min
min_SO5 = 0
max_SO5 = 10
T_SO5 = T90_SO5 / (60*24) / 3.89
std_SO5 = 0.025

# values for PI controller:
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

# values for KLa actuator:
T90_KLa5 = 4        # response time 4 minutes
T_KLa5 = T90_KLa5 / (60*24) / 3.89


