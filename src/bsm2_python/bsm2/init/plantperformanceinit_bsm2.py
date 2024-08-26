import numpy as np

# Effluent pollutant concentration discharge limits
TOTALCODEMAX = 100
TOTALNEMAX = 18
SNHEMAX = 4
TSSEMAX = 30
BOD5EMAX = 10

# Pollutant weighting factors, effluent pollutants
BSS = 2
BCOD = 1
BNKJ = 30
BNO = 10
BBOD5 = 2

# Pumping energy factors
PF_QINTR = 0.004  # kWh/m3, pumping energy factor, internal AS recirculation
PF_QR = 0.008  # kWh/m3, pumping energy factor, AS sludge recycle
PF_QW = 0.05  # kWh/m3, pumping energy factor, AS wastage flow
PF_QPU = 0.075  # kWh/m3, pumping energy factor, pumped underflow from primary clarifier
PF_QTU = 0.060  # kWh/m3, pumping energy factor, pumped underflow from thickener
PF_QDO = 0.004  # kWh/m3, pumping energy factor, pumped underflow from dewatering unit

ME_AD_UNIT = 0.005  # kWh/m3, mixing energy factor, for AD unit kW/m3 (Keller and Hartley, 2003)
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
