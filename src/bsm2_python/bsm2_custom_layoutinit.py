"""Initialization file for custom real world wastewater treatment plant layout (N. Hvala et al. 2018).

This file will be executed when running `custom_layout_bsm2.py`.
"""

import numpy as np

import bsm2_python.bsm2.init.adm1init_bsm2 as adm1init
import bsm2_python.bsm2.init.plantperformanceinit_bsm2 as performanceinit
from bsm2_python.bsm2.helpers_bsm2 import PIDParams
from bsm2_python.bsm2.init.asm1init_bsm2 import QIN0
from bsm2_python.bsm2.init.asm1init_bsm2 import QW as QW0

# volumes
VOL_PRIM_CLAR = 9999  # Volume of the primary clarifier (m3)
"""Volume of the primary clarifier [m³]."""


VOL_AS_TOTAL = 39034
"""Total volume of the activated sludge reactor [m³]."""
VOL_REACTOR1 = VOL_AS_TOTAL / 4
"""Volume of the activated sludge reactor 1."""
VOL_REACTOR2 = VOL_AS_TOTAL / 4
"""Volume of the activated sludge reactor 2."""
VOL_REACTOR3 = VOL_AS_TOTAL / 4
"""Volume of the activated sludge reactor 3."""
VOL_REACTOR4 = VOL_AS_TOTAL / 4
"""Volume of the activated sludge reactor 4."""


# VOL_SETTLER_TOTAL = 24000
# """Volume of the secondary settler [m³]."""
AREA_SETTLER = 5714
"""Area of the secondary settlers [m²]."""
HEIGHT_SETTLER = 4.2
"""Height of the secondary settler [m]."""
DIM_SETTLER = np.array([AREA_SETTLER, HEIGHT_SETTLER])
"""Secondary settler dimensions."""


VOL_PRIM_THICKENER = 1850
"""Volume of the primary sludge thickener [m³]."""
VOL_WASTE_THICKENER = 1850
"""Volume of the waste sludge thickener [m³]."""
VOL_SEC_THICKENER = 1850
"""Volume of the secondary sludge thickener [m³]."""


VOL_AD_TOTAL = 14130
"""Volume of the anaerobic digester [m³]."""
VOL_LIQ = (1 - (adm1init.V_GAS / adm1init.V_LIQ)) * VOL_AD_TOTAL  # assumed (TODO: CHECK VALUE)
"""Liquid volume of anaerobic digestor [m³]."""
VOL_GAS = adm1init.V_GAS / adm1init.V_LIQ * VOL_AD_TOTAL  # assumed (TODO: CHECK VALUE)
"""Gas volume of anaerobic digestor [m³]."""
DIM_AD = np.array([VOL_LIQ, VOL_GAS])
"""Reactor dimensions of the anaerobic digestor [m³]."""


# sludge treatment parameters
PRIM_THICKENER_PERC = 3.5  # %TSS in thickener underflow
"""TTS in primary sludge thickener underflow [%]."""
WASTE_THICKENER_PERC = 3  # %TSS in thickener underflow
"""TTS in waste sludge thickener underflow [%]."""
SEC_THICKENER_PERC = 12  # %TSS in thickener underflow; assumed (TODO: CHECK VALUE)
"""TTS in secondary sludge thickener underflow [%]."""

TSS_REMOVAL_PERC = 98  # %TSS removed from the thickener overflow
"""TSS removed from the thickener overflow [%]."""
X_I2TSS = 0.75
"""Conversion factor for particulate inert organic matter to TSS [-]."""
X_S2TSS = 0.75
"""Conversion factor for slowly biodegradable substrate to TSS [-]."""
X_BH2TSS = 0.75
"""Conversion factor for heterotrophic biomass to TSS [-]."""
X_BA2TSS = 0.75
"""Conversion factor for autotrophic biomass to TSS [-]."""
X_P2TSS = 0.75
"""Conversion factor for particulate products to TSS [-]."""

PRIM_THICKENERPAR = np.array([PRIM_THICKENER_PERC, TSS_REMOVAL_PERC, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS])
"""Primary thickener parameters."""
WASTE_THICKENERPAR = np.array([WASTE_THICKENER_PERC, TSS_REMOVAL_PERC, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS])
"""Waste thickener parameters."""
SEC_THICKENERPAR = np.array([SEC_THICKENER_PERC, TSS_REMOVAL_PERC, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS])
"""Secondary thickener parameters."""


PRIM_CENTRIFUGE_PERC = 6  # %TSS in centrifuge (dewatering) underflow
"""TTS in primary sludge centrifuge underflow [%]."""
WASTE_CENTRIFUGE_PERC = 6  # %TSS in centrifuge (dewatering) underflow
"""TTS in waste sludge centrifuge underflow [%]."""
DEWATERING_CENTRIFUGE_PERC = 25  # %TSS in dewatering centrifuge underflow
"""TTS in dewatering centrifuge underflow [%]."""
SLUDGE_DRYING_PERC = 92  # %TSS in sludge drying (dewatering) underflow
"""TTS in sludge drying underflow [%]."""

TSS_REMOVAL_PERC = 98  # %TSS removed from the dewatering overflow (reject water)
"""Percentage of TSS removed from the influent sludge [%]."""
X_I2TSS = 0.75
"""Conversion factor of inert particulate organic matter X_I to TSS [g(SS) ⋅ g(COD)⁻¹]."""
X_S2TSS = 0.75
"""Conversion factor of slowly biodegradable substrat X_S to TSS [g(SS) ⋅ g(COD)⁻¹]."""
X_BH2TSS = 0.75
"""Conversion factor of heterotrophic biomass X_B,H to TSS [g(SS) ⋅ g(COD)⁻¹]."""
X_BA2TSS = 0.75
"""Conversion factor of autotrophic biomass X_B,A to TSS [g(SS) ⋅ g(COD)⁻¹]."""
X_P2TSS = 0.75
"""Conversion factor of particulate products from biomass decay X_P to TSS [g(SS) ⋅ g(COD)⁻¹]."""

PRIM_CENTRIFUGEPAR = np.array([PRIM_CENTRIFUGE_PERC, TSS_REMOVAL_PERC, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS])
"""Primary centrifuge parameters."""
WASTE_CENTRIFUGEPAR = np.array([WASTE_CENTRIFUGE_PERC, TSS_REMOVAL_PERC, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS])
"""Waste centrifuge parameters."""
DEWATERING_CENTRIFUGEPAR = np.array(
    [DEWATERING_CENTRIFUGE_PERC, TSS_REMOVAL_PERC, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS]
)
"""Dewatering centrifuge parameters."""
SLUDGE_DRYINGPAR = np.array([SLUDGE_DRYING_PERC, TSS_REMOVAL_PERC, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS])
"""Sludge drying parameters."""


# Pumping energy factors
PF_QINTR = 0.004  # kWh/m3, pumping energy factor, internal AS recirculation
"""Pumping energy factor for internal activated sludge recirculation [kWh ⋅ m⁻³]."""
PF_QR = 0.008  # kWh/m3, pumping energy factor, AS sludge recycle
"""Pumping energy factor for external activated sludge recirculation from settler [kWh ⋅ m⁻³]."""
PF_QW = 0.05  # kWh/m3, pumping energy factor, AS wastage flow
"""Pumping energy factor for activated sludge wastage flow [kWh ⋅ m⁻³]."""
PF_QPRIM_CLAR_UF = 0.075  # kWh/m3, pumping energy factor, pumped underflow from primary clarifier
"""Pumping energy factor for pumped underflow from primary clarifier [kWh ⋅ m⁻³]."""
PF_QPRIM_THIC_UF = 0.060  # kWh/m3, pumping energy factor, pumped underflow from thickener
"""Pumping energy factor for pumped underflow from primary thickener [kWh ⋅ m⁻³]."""
PF_QWASTE_THIC_UF = 0.060  # kWh/m3, pumping energy factor, pumped underflow from thickener
"""Pumping energy factor for pumped underflow from waste thickener [kWh ⋅ m⁻³]."""
PF_QSEC_THIC_UF = 0.060  # kWh/m3, pumping energy factor, pumped underflow from thickener
"""Pumping energy factor for pumped underflow from secondary thickener [kWh ⋅ m⁻³]."""
PF_QPRIM_CENTR_UF = 0.004  # kWh/m3, pumping energy factor, pumped underflow from dewatering unit
"""Pumping energy factor for pumped underflow from primary centrifuge unit [kWh ⋅ m⁻³]."""
PF_QWASTE_CENTR_UF = 0.004  # kWh/m3, pumping energy factor, pumped underflow from dewatering unit
"""Pumping energy factor for pumped underflow from waste centrifuge unit [kWh ⋅ m⁻³]."""
PF_QDW_CENTR_UF = 0.004  # kWh/m3, pumping energy factor, pumped underflow from dewatering unit
"""Pumping energy factor for pumped underflow from dewatering centrifuge unit [kWh ⋅ m⁻³]."""
PF_QSL_DRYING_UF = 0.004  # kWh/m3, pumping energy factor, pumped underflow from dewatering unit
"""Pumping energy factor for pumped underflow from sludge drying unit [kWh ⋅ m⁻³]."""

PP_PAR = np.array(
    [
        performanceinit.TOTALCODEMAX,
        performanceinit.TOTALNEMAX,
        performanceinit.SNHEMAX,
        performanceinit.TSSEMAX,
        performanceinit.BOD5EMAX,
        performanceinit.BSS,
        performanceinit.BCOD,
        performanceinit.BNKJ,
        performanceinit.BNO,
        performanceinit.BBOD5,
        PF_QINTR,
        PF_QR,
        PF_QW,
        PF_QPRIM_CLAR_UF,
        PF_QPRIM_THIC_UF,
        PF_QWASTE_THIC_UF,
        PF_QSEC_THIC_UF,
        PF_QPRIM_CENTR_UF,
        PF_QWASTE_CENTR_UF,
        PF_QDW_CENTR_UF,
        PF_QSL_DRYING_UF,
        performanceinit.ME_AD_UNIT,
    ]
)
"""Plant performance parameters."""


# activated sludge configuration
Q_INFLUENT_AVG = 82561
"""Flow rate of the average influent [m³ ⋅ d⁻¹]."""

INT_RECIRC = 4 * Q_INFLUENT_AVG
"""Internal recirculation flow rate in the activated sludge system [m³ ⋅ d⁻¹]."""
EXTERNAL_RECYCLE = 1.6 * Q_INFLUENT_AVG
"""External recirculation flow rate from settler to the activated sludge system [m³ ⋅ d⁻¹]."""

QR = EXTERNAL_RECYCLE
"""Flow rate of sludge return for the settler [m³ ⋅ d⁻¹]."""
QW = (QW0 / QIN0) * Q_INFLUENT_AVG  # assumed (TODO: CHECK VALUE)
"""Flow rate of waste sludge for the settler [m³ ⋅ d⁻¹]."""


KLA_ANAEROBIC = 0
"""Default KLa (oxygen transfer coefficient) value for anaerobic reactor [d⁻¹]."""
KLA_ANOXIC = 0
"""Default KLa (oxygen transfer coefficient) value for anoxic reactor [d⁻¹]."""
KLA_AEROBIC = 120  # assumed (TODO: CHECK VALUE)
"""Default KLa (oxygen transfer coefficient) value for aerobic reactor [d⁻¹]."""

DO_AEROBIC = 1.5
"""Dissolved oxygen aerobic reactor [g(O₂) ⋅ m⁻³]."""

CARB1 = 0  # no external carbon input due to internal recirculation
"""External carbon flow rate to reactor 1 [kg(COD) ⋅ d⁻¹]."""
CARB2 = CARB1
"""External carbon flow rate to reactor 2 [kg(COD) ⋅ d⁻¹]."""
CARB3 = CARB1
"""External carbon flow rate to reactor 3 [kg(COD) ⋅ d⁻¹]."""
CARB4 = CARB1
"""External carbon flow rate to reactor 4 [kg(COD) ⋅ d⁻¹]."""
CARBONSOURCECONC = 400000  # mg COD / L
"""External carbon source concentration [g(COD) ⋅ m⁻³]."""


# PID controller
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
SO4AWSTATE = 379.05091041032915
"""Initial integration value for 'antiwindup' saturated oxygen concentration of PI controller 4 <br>
[g(O₂) ⋅ m⁻³]."""
SO4REF = DO_AEROBIC  # setpoint for controller [g(O₂) ⋅ m⁻³] or [mg(O₂) ⋅ L⁻¹]
"""Set point for oxygen concentration controller 4 [g(O₂) ⋅ m⁻³]."""
KLA4OFFSET = 120  # reasonable offset value for control around SO4ref
"""Reasonable offset value for PI controller 4 around S_O^ref [d⁻¹]."""
USEANTIWINDUPSO4 = True  # False=no antiwindup, True=use antiwindup for oxygen control
"""Boolean value to use 'antiwindup' for PI controller 4."""

PID4_PARAMS: PIDParams = {
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
