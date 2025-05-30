"""Initialization file for all states and parameters related to the plant performance.

All parameters and specifications are based on BSM1 model.
This file will be executed when running `bsm2_cl.py`, `bsm2_ol.py` or `bsm2_olem.py`.
"""

import numpy as np

# Effluent pollutant concentration discharge limits
TOTALCODEMAX = 100
"""Effluent concentration limit for total chemical oxygen demand (COD_part + COD_sol) [g(COD) ⋅ m⁻³]."""
TOTALNEMAX = 18
"""Effluent concentration limit for total nitrogen [g(N) ⋅ m⁻³]."""
SNHEMAX = 4
"""Effluent concentration limit for ammonium plus ammonia nitrogen [g(N) ⋅ m⁻³]."""
TSSEMAX = 30
"""Effluent concentration limit for total suspended solids (TSS) [g(SS) ⋅ m⁻³]."""
BOD5EMAX = 10
"""Effluent concentration limit for biochemical oxygen demand (BOD) [g(BOD) ⋅ m⁻³]."""

# Pollutant weighting factors, effluent pollutants
BSS = 2
"""Pollutant weighting factor for suspended solids [-]."""
BCOD = 1
"""Pollutant weighting factor for chemical oxygen demand [-]."""
BNKJ = 30
"""Pollutant weighting factor for total Kjeldahl nitrogen (TKN) [-]."""
BNO = 10
"""Pollutant weighting factor for nitrate and nitrite nitrogen [-]."""
BBOD5 = 2
"""Pollutant weighting factor for biochemical oxygen demand (BOD) [-]."""

# Pumping energy factors
PF_QINTR = 0.004  # kWh/m3, pumping energy factor, internal AS recirculation
"""Pumping energy factor for internal activated sludge recirculation [kWh ⋅ m⁻³]."""
PF_QR = 0.008  # kWh/m3, pumping energy factor, AS sludge recycle
"""Pumping energy factor for activated sludge recycle [kWh ⋅ m⁻³]."""
PF_QW = 0.05  # kWh/m3, pumping energy factor, AS wastage flow
"""Pumping energy factor for activated sludge wastage flow [kWh ⋅ m⁻³]."""
PF_QPU = 0.075  # kWh/m3, pumping energy factor, pumped underflow from primary clarifier
"""Pumping energy factor for pumped underflow from primary clarifier [kWh ⋅ m⁻³]."""
PF_QTU = 0.060  # kWh/m3, pumping energy factor, pumped underflow from thickener
"""Pumping energy factor for pumped underflow from thickener [kWh ⋅ m⁻³]."""
PF_QDO = 0.004  # kWh/m3, pumping energy factor, pumped underflow from dewatering unit
"""Pumping energy factor for pumped underflow from dewatering unit [kWh ⋅ m⁻³]."""

ME_AD_UNIT = 0.005  # kWh/m3, mixing energy factor, for AD unit kW/m3 (Keller and Hartley, 2003)
"""Mixing energy factor for anaerobic digester unit [kWh ⋅ m⁻³]."""

PP_PAR = np.array(
    [
        TOTALCODEMAX,
        TOTALNEMAX,
        SNHEMAX,
        TSSEMAX,
        BOD5EMAX,
        BSS,
        BCOD,
        BNKJ,
        BNO,
        BBOD5,
        PF_QINTR,
        PF_QR,
        PF_QW,
        PF_QPU,
        PF_QTU,
        PF_QDO,
        ME_AD_UNIT,
    ]
)
"""Plant performance parameters."""
