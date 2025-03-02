"""Initialisation file for all states and parameters related to the aeration control system `aerationcontrol.py` in reactor 3 to 5.

All parameters and specifications are based on BSM1 model.
This file will be executed when running `bsm2_cl.py`.
"""

import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init

# maximum possible external carbon flow rate to reactors
CARB1_MAX = 5
"""Maximum possible external carbon flow rate to reactor 1 [kg(COD) $\cdot$ d^-1^]."""
CARB2_MAX = 5
"""Maximum possible external carbon flow rate to reactor 2 [kg(COD) $\cdot$ d^-1^]."""
CARB3_MAX = 5
"""Maximum possible external carbon flow rate to reactor 3 [kg(COD) $\cdot$ d^-1^]."""
CARB4_MAX = 5
"""Maximum possible external carbon flow rate to reactor 4 [kg(COD) $\cdot$ d^-1^]."""
CARB5_MAX = 5
"""Maximum possible external carbon flow rate to reactor 5 [kg(COD) $\cdot$ d^-1^]."""

# maximum pump capacities
QINTR_MAX = 5 * asm1init.QIN0
"""Maximum pump capacity for internal recirculation QINTR [m^3^ $\cdot$ d^-1^]."""
QW_MAX = 0.1 * asm1init.QIN0
"""Maximum pump capacity for waste sludge QW [m^3^ $\cdot$ d^-1^]."""
QR_MAX = 2 * asm1init.QIN0
"""Maximum pump capacity for sludge return QR [m^3^ $\cdot$ d^-1^]."""
QSTORAGE_MAX = 1500
"""Maximum pump capacity for storage flow rate QSTORAGE [m^3^ $\cdot$ d^-1^]."""
QWT = 1 / 60 / 24 * 10 # time delay for artificial Qw actuator (acts as first-order filter)
"""Time delay for artificial Qw actuator (acts as first-order filter)."""

KLA3GAIN = 1.0  # gain for control signal to reactor 3
"""Gain for control signal to reactor 3."""

# values for KLa actuator 3:
T90_KLA3 = 4  # Response time 4 minutes
"""Response time [min] for KLa actuator 3."""
T_KLA3 = T90_KLA3 / (60 * 24) / 3.89
"""Time constant for KLa actuator 3."""

# initial values for sensor 4:
T90_SO4 = 1  # Response time 1 min
"""Response time [min] for oxygen sensor 4."""
MIN_SO4 = 0
"""Lower measuring limit of the oxygen sensor 4."""
MAX_SO4 = 10
""""Upper measuring limit of the oxygen sensor 4."""
T_SO4 = T90_SO4 / (60 * 24) / 3.89
"""Time constant of transfer function for sensor 4."""
STD_SO4 = 0.025
"""Standard deviation for adding measurement noise for sensor 4."""

# values for PI controller 4:
KLA4_INIT = 201.3015557168598
"""Initial value for PI controller 4."""
KLA4_MIN = 0
"""Minimum value for PI controller 4."""
KLA4_MAX = 360
"""Maximum value for PI controller 4."""
KSO4 = 25  # Amplification, 500 in BSM1 book
"""Amplification constant for PI controller 4."""
TISO4 = 0.002  # I-part time constant (d = 2.88 min)), integral time constant, 0.001 in BSM1 book
"""Integral part time constant for PI controller 4."""
TTSO4 = 0.001  # Antiwindup time constant (d), tracking time constant, 0.0002 in BSM1 book
"""Antiwindup time constant for PI controller 4."""
SO4INTSTATE = -321.7493546935257
"""Initial integration value of PI controller 4."""
SO4AWSTATE = 379.05091041032915
"""Initial integration value for antiwindup of PI controller 4."""
SO4REF = 2  # setpoint for controller, mg (-COD)/l
"""Setpoint for controller 4 [mg (-COD) $\cdot$ l^-1^]."""
KLA4OFFSET = 120  # reasonable offset value for control around SO4ref
"""Reasonable offset value for PI controller 4 around SO4ref."""
KLA4_LIM = 201.3015557168598
"""Kla value after adjusting to upper and lower limit for PI controller 4."""
KLA4_CALC = 201.3015557168598
"""Kla value calculated from PI control."""
USEANTIWINDUPSO4 = True  # False=no antiwindup, True=use antiwindup for oxygen control
"""Boolean value to use antiwindup for PI controller 4."""

# values for KLa actuator 4:
T90_KLA4 = 4  # Response time 4 minutes
"""Response time [min] for KLa actuator 4."""
T_KLA4 = T90_KLA4 / (60 * 24) / 3.89
"""Time constant for KLa actuator 4."""

KLA5GAIN = 0.5  # gain for control signal to reactor 5
"""Gain for control signal to reactor 5."""

# values for KLa actuator 5:
T90_KLA5 = 4  # Response time 4 minutes
"""Response time [min] for KLa actuator 5."""
T_KLA5 = T90_KLA5 / (60 * 24) / 3.89
"""Time constant for KLa actuator 5."""
