# Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden

# control of bypassing options in BSM2
QBYPASS = 60000  # type 2, everything above 60000 m3/d bypassed for primary clarifier
QBYPASSPLANT = 1  # type 1, all of this is also bypassed the AS system
QBYPASSAS = 0  # type 1, none of primary effluent bypassed for AS
QTHICKENER2AS = 0  # type 1, none of thickener effluent to AS, all to primary
QSTORAGE2AS = 0  # type 1, none of storage tank effluent to AS, all to primary

# Default KLa (oxygen transfer coefficient) values for AS reactors in d^-1:
KLA1 = 0
KLA2 = 0
KLA3 = 120
KLA4 = 120
KLA5 = 60

# external carbon flow rates for reactor 1 to 5 in kg COD / d:
CARB1 = 2
CARB2 = 0
CARB3 = 0
CARB4 = 0
CARB5 = 0
# external carbon source concentration = 400000 mg COD / L from BSM1
CARBONSOURCECONC = 400000  # mg COD / L

# Default output pumping from storage tank
QSTORAGE = 0

# Default closed loop control of Qw
QW_HIGH = 450
QW_LOW = 300

# to be used for a Qintr controller of BSM1 type, should then be
# sensorinit_bsm2 since it is an rudimentary 'actuator model' similar to QwT
# QintrT = T*10

# operating temperature of anaerobic digester
T_OP = 35 + 273.15  # operational temperature of AD and interfaces
