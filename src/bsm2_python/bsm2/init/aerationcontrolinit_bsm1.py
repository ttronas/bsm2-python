"""Initialisation file for all states and parameters related to the aeration control system in reactor 3 to 5

All parameters and specifications are based on BSM1 model.

This file will be executed when running `bsm1_cl.py`.
"""

import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init
from bsm2_python.bsm2.helpers_bsm2 import PIDParams

# maximum possible external carbon flow rate to reactors
CARB1_MAX = 5
"""Maximum possible external carbon flow rate to reactor 1 [m³ ⋅ d⁻¹]."""
CARB2_MAX = 5
"""Maximum possible external carbon flow rate to reactor 2 [m³ ⋅ d⁻¹]."""
CARB3_MAX = 5
"""Maximum possible external carbon flow rate to reactor 3 [m³ ⋅ d⁻¹]."""
CARB4_MAX = 5
"""Maximum possible external carbon flow rate to reactor 4 [m³ ⋅ d⁻¹]."""
CARB5_MAX = 5
"""Maximum possible external carbon flow rate to reactor 5 [m³ ⋅ d⁻¹]."""

# maximum pump capacities
QINTR_MAX = 5 * asm1init.QIN0
"""Maximum pump capacity for internal recirculation rate Q_intr [m³ ⋅ d⁻¹]."""
QINTR_MIN = 0
"""Minimum pump capacity for internal recirculation rate Q_intr [m³ ⋅ d⁻¹]."""
QW_MAX = 0.1 * asm1init.QIN0
"""Maximum pump capacity for waste sludge flow rate Q_w [m³ ⋅ d⁻¹]."""
QR_MAX = 2 * asm1init.QIN0
"""Maximum pump capacity for return sludge flow rate Q_r [m³ ⋅ d⁻¹]."""
QSTORAGE_MAX = 1500
"""Maximum pump capacity for outlet flow rate of the storage tank Q_st,out [m³ ⋅ d⁻¹]."""
QWT = 1 / 60 / 24 * 10  # time delay for artificial Qw actuator (acts as first-order filter)
"""Time delay for artificial Q_w actuator (acts as first-order filter) [d]."""

# initial values for SNO2 sensor:
T90_SNO2 = 10  # Response time 10 min
"""Response time t_r for nitrate sensor [min]."""
MIN_SNO2 = 0  # Lower measuring limit of the nitrate sensor [g(N) ⋅ m⁻³].
"""Lower measuring limit of the nitrate sensor [g(N) ⋅ m⁻³]."""
MAX_SNO2 = 10  # Upper measuring limit of the nitrate sensor [g(N) ⋅ m⁻³].
"""Upper measuring limit of the nitrate sensor [g(N) ⋅ m⁻³]."""
T_SNO2 = T90_SNO2 / (60 * 24) / 11.7724
"""Integral part time constant *τ* of transfer function for nitrate sensor [d]."""
STD_SNO2 = 0.025  # Standard deviation for adding measurement noise for nitrate sensor [-].
"""Standard deviation for adding measurement noise for nitrate sensor [-]."""

# values for PI QINTR controller
KQINTR = 10000  # Amplification [-]
"""Amplification constant for Q_intr controller [-]."""
TIQINTR = 0.025  # I-part time constant (d = 36 min), 0.05 in BSM1 book
"""Integral part time constant *τ* for Q_intr controller [d]."""
TTQINTR = 0.015  # Antiwindup time constant (d), tracking time constant, 0.03 in BSM1 book
"""Integral part time constant *τ* of 'antiwindup' for Q_intr controller [d]."""
TDQINTR = 0  # as it is a PI controller, the Differential term is set to 0
"""Differential part time constant *τ* for Q_intr controller [d]."""
QINTRINTSTATE = 0
"""Initial integration value for nitrate concentration of Q_intr controller [g(N) ⋅ m⁻³]."""
SNO2AWSTATE = 0
"""Initial integration value for 'antiwindup' nitrate concentration of Q_intr controller [g(N) ⋅ m⁻³]."""
SNO2REF = 1  # setpoint for controller [g(N) ⋅ m⁻³]
"""Set point for nitrate concentration controller [g(N) ⋅ m⁻³]."""
QINTROFFSET = (
    18500  # reasonable offset value for control around SNO2ref (= controller output if the rest is turned off)
)
"""Reasonable offset value for Q_intr controller around S_NO2^ref [m³ ⋅ d⁻¹]."""
USEANTIWINDUPSNO2 = True  # False=no antiwindup, True=use antiwindup for QINTR control
"""Boolean value to use 'antiwindup' for QINTR controller."""
KFEEDFORWARD = 0  # Feedforward gain of QIN to QINTR. 0 means no feedforward.
"""Feedforward gain of QIN to QINTR [-]."""
QFFREF = 3
QINTRT = 0.001

PID_QINTR_PARAMS: PIDParams = {
    'k': KQINTR,
    't_i': TIQINTR,
    't_d': TDQINTR,
    't_t': TTQINTR,
    'offset': QINTROFFSET,
    'min_value': QINTR_MIN,
    'max_value': QINTR_MAX,
    'setpoint': SNO2REF,
    'aw_init': SNO2AWSTATE,
    'use_antiwindup': USEANTIWINDUPSNO2,
}
# initial values for sensor 3:
T90_SO3 = 1  # Response time 1 min
"""Response time t_r for oxygen sensor 3 [min]."""
MIN_SO3 = 0
"""Lower measuring limit of the oxygen sensor 3 [g(O₂) ⋅ m⁻³]."""
MAX_SO3 = 10
""""Upper measuring limit of the oxygen sensor 3 [g(O₂) ⋅ m⁻³]."""
T_SO3 = T90_SO3 / (60 * 24) / 3.89
"""Integral part time constant *τ* of transfer function for sensor 3 [d]."""
STD_SO3 = 0.025
"""Standard deviation for adding measurement noise for sensor 3 [-]."""

# values for PI controller 3:
KLA3_INIT = 201.3015557168598
"""Initial value for PI controller 3 [d⁻¹]."""
KLA3_MIN = 0
"""Lower limit of the adjustable KLa value for PI controller 3 [d⁻¹]."""
KLA3_MAX = 360
"""Upper limit of the adjustable KLa value for PI controller 3 [d⁻¹]."""
KSO3 = 25  # Amplification, 500 in BSM1 book
"""Amplification constant for PI controller 3 [-]."""
TISO3 = 0.002  # I-part time constant (d = 2.88 min)), integral time constant, 0.001 in BSM1 book
"""Integral part time constant *τ* for PI controller 3 [d]."""
TTSO3 = 0.001  # Antiwindup time constant (d), tracking time constant, 0.0002 in BSM1 book
"""Integral part time constant *τ* of 'antiwindup' for PI controller 3 [d]."""
TDSO3 = 0  # as it is a PI controller, the Differential term is set to 0
"""Differential part time constant *τ* for PI controller 3 [d]."""
SO3INTSTATE = 0
"""Initial integration value for saturated oxygen concentration of PI controller 3 [g(O₂) ⋅ m⁻³]."""
SO3AWSTATE = 0
"""Initial integration value for 'antiwindup' saturated oxygen concentration of PI controller 3 <br>
[g(O₂) ⋅ m⁻³]."""
SO3REF = 2  # setpoint for controller, mg (-COD)/l
"""Set point for oxygen concentration controller 3 [g(O₂) ⋅ m⁻³]."""
KLA3OFFSET = 144  # reasonable offset value for control around SO4ref
"""Reasonable offset value for PI controller 3 around S_O^ref [d⁻¹]."""
KLA3_LIM = 0
"""KLa value after adjusting to upper and lower limit for PI controller 3 [d⁻¹]."""
KLA3_CALC = 0
"""KLa value calculated from PI control [d⁻¹]."""
USEANTIWINDUPSO3 = True  # False=no antiwindup, True=use antiwindup for oxygen control
"""Boolean value to use 'antiwindup' for PI controller 3."""

PID_KLA3_PARAMS: PIDParams = {
    'k': KSO3,
    't_i': TISO3,
    't_d': TDSO3,
    't_t': TTSO3,
    'offset': KLA3OFFSET,
    'min_value': KLA3_MIN,
    'max_value': KLA3_MAX,
    'setpoint': SO3REF,
    'aw_init': SO3AWSTATE,
    'use_antiwindup': USEANTIWINDUPSO3,
}

# values for KLa actuator 3:
T90_KLA3 = 4  # Response time 4 minutes
"""Response time t_r for KLa actuator 3 [min]."""
T_KLA3 = T90_KLA3 / (60 * 24) / 3.89
"""Integral part time constant *τ* for KLa actuator 3 [d]."""

# initial values for sensor 4:
T90_SO4 = 1  # Response time 1 min
"""Response time t_r for oxygen sensor 4 [min]."""
MIN_SO4 = 0
"""Lower measuring limit of the oxygen sensor 4 [g(O₂) ⋅ m⁻³]."""
MAX_SO4 = 10
""""Upper measuring limit of the oxygen sensor 4 [g(O₂) ⋅ m⁻³]."""
T_SO4 = T90_SO4 / (60 * 24) / 3.89
"""Integral part time constant *τ* of transfer function for sensor 4 [d]."""
STD_SO4 = 0.025
"""Standard deviation for adding measurement noise for sensor 4 [-]."""

# values for PI controller 4:
KLA4_INIT = 201.3015557168598
"""Initial value for PI controller 4 [d⁻¹]."""
KLA4_MIN = 0
"""Lower limit of the adjustable KLa value for PI controller 4 [d⁻¹]."""
KLA4_MAX = 360
"""Upper limit of the adjustable KLa value for PI controller 4 [d⁻¹]."""
KSO4 = 25  # Amplification, 500 in BSM1 book
"""Amplification constant for PI controller 4 [-]."""
TISO4 = 0.002  # I-part time constant (d = 2.88 min)), integral time constant, 0.001 in BSM1 book
"""Integral part time constant *τ* for PI controller 4 [d]."""
TTSO4 = 0.001  # Antiwindup time constant (d), tracking time constant, 0.0002 in BSM1 book
"""Integral part time constant *τ* of 'antiwindup' for PI controller 4 [d]."""
TDSO4 = 0  # as it is a PI controller, the Differential term is set to 0
"""Differential part time constant *τ* for PI controller 4 [d]."""
SO4INTSTATE = 0
"""Initial integration value for saturated oxygen concentration of PI controller 4 [g(O₂) ⋅ m⁻³]."""
SO4AWSTATE = 0
"""Initial integration value for 'antiwindup' saturated oxygen concentration of PI controller 4 <br>
[g(O₂) ⋅ m⁻³]."""
SO4REF = 2  # setpoint for controller, mg (-COD)/l
"""Set point for oxygen concentration controller 4 [g(O₂) ⋅ m⁻³]."""
KLA4OFFSET = 144  # reasonable offset value for control around SO4ref
"""Reasonable offset value for PI controller 4 around S_O^ref [d⁻¹]."""
KLA4_LIM = 0
"""KLa value after adjusting to upper and lower limit for PI controller 4 [d⁻¹]."""
KLA4_CALC = 0
"""KLa value calculated from PI control [d⁻¹]."""
USEANTIWINDUPSO4 = True  # False=no antiwindup, True=use antiwindup for oxygen control
"""Boolean value to use 'antiwindup' for PI controller 4."""

PID_KLA4_PARAMS: PIDParams = {
    'k': KSO4,
    't_i': TISO4,
    't_d': TDSO4,
    't_t': TTSO4,
    'offset': KLA4OFFSET,
    'min_value': KLA4_MIN,
    'max_value': KLA4_MAX,
    'setpoint': SO4REF,
    'aw_init': SO4AWSTATE,
    'use_antiwindup': USEANTIWINDUPSO4,
}

# values for KLa actuator 4:
T90_KLA4 = 4  # Response time 4 minutes
"""Response time t_r for KLa actuator 4 [min]."""
T_KLA4 = T90_KLA4 / (60 * 24) / 3.89
"""Integral part time constant *τ* for KLa actuator 4 [d]."""

# initial values for sensor 5:
T90_SO5 = 1  # Response time 1 min
"""Response time t_r for oxygen sensor 5 [min]."""
MIN_SO5 = 0
"""Lower measuring limit of the oxygen sensor 5 [g(O₂) ⋅ m⁻³]."""
MAX_SO5 = 10
""""Upper measuring limit of the oxygen sensor 5 [g(O₂) ⋅ m⁻³]."""
T_SO5 = T90_SO5 / (60 * 24) / 3.89
"""Integral part time constant *τ* of transfer function for sensor 5 [d]."""
STD_SO5 = 0.025
"""Standard deviation for adding measurement noise for sensor 5 [-]."""

# values for PI controller 5:
KLA5_INIT = 201.3015557168598
"""Initial value for PI controller 5 [d⁻¹]."""
KLA5_MIN = 0
"""Lower limit of the adjustable KLa value for PI controller 5 [d⁻¹]."""
KLA5_MAX = 360
"""Upper limit of the adjustable KLa value for PI controller 5 [d⁻¹]."""
KSO5 = 25  # Amplification, 500 in BSM1 book
"""Amplification constant for PI controller 5 [-]."""
TISO5 = 0.002  # I-part time constant (d = 2.88 min)), integral time constant, 0.001 in BSM1 book
"""Integral part time constant *τ* for PI controller 5 [d]."""
TTSO5 = 0.001  # Antiwindup time constant (d), tracking time constant, 0.0002 in BSM1 book
"""Integral part time constant *τ* of 'antiwindup' for PI controller 5 [d]."""
TDSO5 = 0  # as it is a PI controller, the Differential term is set to 0
"""Differential part time constant *τ* for PI controller 5 [d]."""
SO5INTSTATE = 0
"""Initial integration value for saturated oxygen concentration of PI controller 5 [g(O₂) ⋅ m⁻³]."""
SO5AWSTATE = 0
"""Initial integration value for 'antiwindup' saturated oxygen concentration of PI controller 5 <br>
[g(O₂) ⋅ m⁻³]."""
SO5REF = 2  # setpoint for controller, mg (-COD)/l
"""Set point for oxygen concentration controller 5 [g(O₂) ⋅ m⁻³]."""
KLA5OFFSET = 144  # reasonable offset value for control around SO4ref
"""Reasonable offset value for PI controller 5 around S_O^ref [d⁻¹]."""
KLA5_LIM = 0
"""KLa value after adjusting to upper and lower limit for PI controller 5 [d⁻¹]."""
KLA5_CALC = 0
"""KLa value calculated from PI control [d⁻¹]."""
USEANTIWINDUPSO5 = True  # False=no antiwindup, True=use antiwindup for oxygen control
"""Boolean value to use 'antiwindup' for PI controller 5."""

PID_KLA5_PARAMS: PIDParams = {
    'k': KSO5,
    't_i': TISO5,
    't_d': TDSO5,
    't_t': TTSO5,
    'offset': KLA5OFFSET,
    'min_value': KLA5_MIN,
    'max_value': KLA5_MAX,
    'setpoint': SO5REF,
    'aw_init': SO5AWSTATE,
    'use_antiwindup': USEANTIWINDUPSO5,
}

# values for KLa actuator 5:
T90_KLA5 = 4  # Response time 4 minutes
"""Response time t_r for KLa actuator 5 [min]."""
T_KLA5 = T90_KLA5 / (60 * 24) / 3.89
"""Integral part time constant *τ* for KLa actuator 5 [d]."""
