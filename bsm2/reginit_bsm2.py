# Copyright: Ulf Jeppsson, IEA, Lund University, Lund, Sweden

# control of bypassing options in BSM2
Qbypass = 60000  # type 2, everything above 60000 m3/d bypassed for primary clarifier
Qbypassplant = 1  # type 1, all of this is also bypassed the AS system
QbypassAS = 0  # type 1, none of primary effluent bypassed for AS
Qthickener2AS = 0  # type 1, none of thickener effluent to AS, all to primary
Qstorage2AS = 0  # type 1, none of storage tank effluent to AS, all to primary

# Default KLa (oxygen transfer coefficient) values for AS reactors:
KLa1 = 0
KLa2 = 0
KLa3 = 120
KLa4 = 120
KLa5 = 60

# external carbon flow rates for reactor 1 to 5:
carb1 = 2
carb2 = 0
carb3 = 0
carb4 = 0
carb5 = 0
# external carbon source concentration = 400000 mg COD / L from BSM1
carbonsourceconc = 400000

# Default output pumping from storage tank
Qstorage = 0

# Default closed loop control of Qw
Qw_high = 450
Qw_low = 300

# to be used for a Qintr controller of BSM1 type, should then be
# sensorinit_bsm2 since it is an rudimentary 'actuator model' similar to QwT
# QintrT = T*10

# operating temperature of anaerobic digester
T_op = 35 + 273.15  # operational temperature of AD and interfaces
