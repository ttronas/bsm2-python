# Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden
"""Initialisation file for bypass control, KLa values and carbon flows related to the activated sludge reactors 1-5.

All parameters and specifications are based on BSM1 model.
This file will be executed when running `bsm2_cl.py`, `bsm2_ol.py` or `bsm2_olem.py`.
"""

# control of bypassing options in BSM2
QBYPASS = 60000  # type 2, everything above 60000 m3/d bypassed for primary clarifier
"""Flow rate threshold for bypassing (type 2 splitter). Everything above this value is bypassed to the effluent [m^3^ $\cdot$ d^-1^]."""
QBYPASSPLANT = 1  # type 1, all of this is also bypassed the AS system
"""If 1, all of the bypass flow also bypasses the activated sludge reactor system."""
QBYPASSAS = 0  # type 1, none of primary effluent bypassed for AS
"""If 1, none of the primary clarifier effluent bypasses the activated sludge reactor system."""
QTHICKENER2AS = 0  # type 1, none of thickener effluent to AS, all to primary
"""If 1, none of the thickener effluent goes to the activated sludge reactor system, all goes to the primary clarifier."""
QSTORAGE2AS = 0  # type 1, none of storage tank effluent to AS, all to primary
"""If 1, none of the storage tank effluent goes to the activated sludge reactor system, all goes to the primary clarifier."""

# Default KLa (oxygen transfer coefficient) values for AS reactors in d^-1:
KLA1 = 0
"""Default K~L~a (oxygen transfer coefficient) value for reactor 1 [d^-1^]."""
KLA2 = 0
"""Default K~L~a (oxygen transfer coefficient) value for reactor 2 [d^-1^]."""
KLA3 = 120
"""Default K~L~a (oxygen transfer coefficient) value for reactor 3 [d^-1^]."""
KLA4 = 120
"""Default K~L~a (oxygen transfer coefficient) value for reactor 4 [d^-1^]."""
KLA5 = 60
"""Default K~L~a (oxygen transfer coefficient) value for reactor 5 [d^-1^]."""

# external carbon flow rates for reactor 1 to 5 in kg COD / d:
CARB1 = 2
"""External carbon flow rate to reactor 1 [kg(COD) $\cdot$ d^-1^]."""
CARB2 = 0
"""External carbon flow rate to reactor 2 [kg(COD) $\cdot$ d^-1^]."""
CARB3 = 0
"""External carbon flow rate to reactor 3 [kg(COD) $\cdot$ d^-1^]."""
CARB4 = 0
"""External carbon flow rate to reactor 4 [kg(COD) $\cdot$ d^-1^]."""
CARB5 = 0
"""External carbon flow rate to reactor 5 [kg(COD) $\cdot$ d^-1^]."""
# external carbon source concentration = 400000 mg COD / L from BSM1
CARBONSOURCECONC = 400000  # mg COD / L
"""External carbon source concentration [g(COD) $\cdot$ m^-3^]."""

# Default output pumping from storage tank
QSTORAGE = 0
"""Default flow rate from storage tank [m^3^ $\cdot$ d^-1^]."""

# Default closed loop control of Qw
QW_HIGH = 450
"""Upper limit flow rate for waste sludge Q~W~ [m^3^ $\cdot$ d^-1^]."""
QW_LOW = 300
"""Lower limit flow rate for waste sludge Q~W~ [m^3^ $\cdot$ d^-1^]."""

# to be used for a Qintr controller of BSM1 type, should then be
# sensorinit_bsm2 since it is an rudimentary 'actuator model' similar to QwT
# QintrT = T*10

# operating temperature of anaerobic digester
T_OP = 35 + 273.15  # operational temperature of AD and interfaces
"""Operational temperature of the anaerobic digester [K]."""
