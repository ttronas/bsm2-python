"""
This file initiates parameter values and sets initial conditions for the model implementation of adm1_bsm2.py.
Note that some of the parameter values deviate from the values given in the ADM1-STR (Batstone et al., 2002).
The state values are based on BSM2 technical report.
"""

import numpy as np

S_SU = 0.0124  # monosacharides (kg COD/m3)
S_AA = 0.0055  # amino acids (kg COD/m3)
S_FA = 0.1074  # long chain fatty acids (LCFA) (kg COD/m3)
S_VA = 0.0123  # total valerate (kg COD/m3)
S_BU = 0.0140  # total butyrate (kg COD/m3)
S_PRO = 0.0176  # total propionate (kg COD/m3)
S_AC = 0.0893  # total acetate (kg COD/m3)
S_H2 = 2.5055e-7  # hydrogen gas (kg COD/m3)
S_CH4 = 0.0555  # methane gas (kg COD/m3)
S_IC = 0.0951  # inorganic carbon (kmole C/m3)
S_IN = 0.0945  # inorganic nitrogen (kmole N/m3)
S_I = 0.1309  # soluble inerts (kg COD/m3)
X_XC = 0.1079  # composites (kg COD/m3)
X_CH = 0.0205  # carbohydrates (kg COD/m3)
X_PR = 0.0842  # proteins (kg COD/m3)
X_LI = 0.0436  # lipids (kg COD/m3)
X_SU = 0.3122  # sugar degraders (kg COD/m3)
X_AA = 0.9317  # amino acid degraders (kg COD/m3)
X_FA = 0.3384  # LCFA degraders (kg COD/m3)
X_C4 = 0.3258  # valerate and butyrate degraders (kg COD/m3)
X_PRO = 0.1011  # propionate degraders (kg COD/m3)
X_AC = 0.6772  # acetate degraders (kg COD/m3)
X_H2 = 0.2848  # hydrogen degraders (kg COD/m3)
X_I = 17.2162  # particulate inerts (kg COD/m3)
S_CAT = 3.5659e-43  # cations (metallic ions, strong base) (kmole/m3)
S_AN = 0.0052  # anions (metallic ions, strong acid) (kmole/m3)
S_HVA = 0.0123  # is actually Sva-
S_HBU = 0.0140  # is actually Sbu-
S_HPRO = 0.0175  # is actually Spro-
S_HAC = 0.0890  # is actually Sac-
S_HCO3 = 0.0857
S_NH3 = 0.0019
S_GAS_H2 = 1.1032e-5
S_GAS_CH4 = 1.6535
S_GAS_CO2 = 0.0135
Q_D = 178.4674  # influent flow rate (m3/d)
T_D = 35  # temperature (°C)
S_D1_D = 0
S_D2_D = 0
S_D3_D = 0
X_D4_D = 0
X_D5_D = 0

S_H_ION = 5.4562e-8

# used by all three ADM implementations, adm1_ODE, adm1_DAE1 and adm1_DAE2.
DIGESTERINIT = np.array(
    [
        S_SU,
        S_AA,
        S_FA,
        S_VA,
        S_BU,
        S_PRO,
        S_AC,
        S_H2,
        S_CH4,
        S_IC,
        S_IN,
        S_I,
        X_XC,
        X_CH,
        X_PR,
        X_LI,
        X_SU,
        X_AA,
        X_FA,
        X_C4,
        X_PRO,
        X_AC,
        X_H2,
        X_I,
        S_CAT,
        S_AN,
        S_HVA,
        S_HBU,
        S_HPRO,
        S_HAC,
        S_HCO3,
        S_NH3,
        S_GAS_H2,
        S_GAS_CH4,
        S_GAS_CO2,
        Q_D,
        T_D,
        S_D1_D,
        S_D2_D,
        S_D3_D,
        X_D4_D,
        X_D5_D,
    ]
)
# The following initial conditions are not used due to convergence duration -
# it would take around a year to reach steady state.
# DIGESTERINIT = np.ones(42)

# used by both DAE ADM implementations, adm1_DAE1 and adm1_DAE2.
# PHSOLVINIT = np.array([S_H_ion, S_hva, S_hbu, S_hpro, S_hac, S_hco3, S_nh3])
PHSOLVINIT = np.ones(7)

# used by one DAE ADM implementation, adm1_DAE2.
# SH2SOLVINIT = S_h2
SH2SOLVINIT = 0

F_SI_XC = 0.1
F_XI_XC = 0.2
F_CH_XC = 0.2
F_PR_XC = 0.2
F_LI_XC = 0.3
N_XC = 0.0376 / 14.0
N_I = 0.06 / 14.0
N_AA = 0.007
C_XC = 0.02786
C_SI = 0.03
C_CH = 0.0313
C_PR = 0.03
C_LI = 0.022
C_XI = 0.03
C_SU = 0.0313
C_AA = 0.03
F_FA_LI = 0.95
C_FA = 0.0217
F_H2_SU = 0.19
F_BU_SU = 0.13
F_PRO_SU = 0.27
F_AC_SU = 0.41
N_BAC = 0.08 / 14.0
C_BU = 0.025
C_PRO = 0.0268
C_AC = 0.0313
C_BAC = 0.0313
Y_SU = 0.1
F_H2_AA = 0.06
F_VA_AA = 0.23
F_BU_AA = 0.26
F_PRO_AA = 0.05
F_AC_AA = 0.40
C_VA = 0.024
Y_AA = 0.08
Y_FA = 0.06
Y_C4 = 0.06
Y_PRO = 0.04
C_CH4 = 0.0156
Y_AC = 0.05
Y_H2 = 0.06
K_DIS = 0.5
K_HYD_CH = 10.0
K_HYD_PR = 10.0
K_HYD_LI = 10.0
K_S_IN = 1.0e-4
K_M_SU = 30.0
K_S_SU = 0.5
PH_UL_AA = 5.5
PH_LL_AA = 4.0
K_M_AA = 50.0
K_S_AA = 0.3
K_M_FA = 6.0
K_S_FA = 0.4
K_IH2_FA = 5.0e-6
K_M_C4 = 20.0
K_S_C4 = 0.2
K_IH2_C4 = 1.0e-5
K_M_PRO = 13.0
K_S_PRO = 0.1
K_IH2_PRO = 3.5e-6
K_M_AC = 8.0
K_S_AC = 0.15
K_I_NH3 = 0.0018
PH_UL_AC = 7.0
PH_LL_AC = 6.0
K_M_H2 = 35.0
K_S_H2 = 7.0e-6
PH_UL_H2 = 6.0
PH_LL_H2 = 5.0
K_DEC_XSU = 0.02
K_DEC_XAA = 0.02
K_DEC_XFA = 0.02
K_DEC_XC4 = 0.02
K_DEC_XPRO = 0.02
K_DEC_XAC = 0.02
K_DEC_XH2 = 0.02
R = 0.083145  # universal gas constant dm3*bar/(mol*K) = 8.3145 J/(mol*K)
T_BASE = 298.15  # 25 degC = 298.15 K
t_op = 308.15  # operational temperature of AD and interfaces, 35 degC. Can be changed in the code.
PK_W_BASE = 14.0
PK_A_VA_BASE = 4.86
PK_A_BU_BASE = 4.82
PK_A_PRO_BASE = 4.88
PK_A_AC_BASE = 4.76
PK_A_CO2_BASE = 6.35
PK_A_IN_BASE = 9.25
K_A_BVA = 1.0e10  # 1e8 according to STR
K_A_BBU = 1.0e10  # 1e8 according to STR
K_A_BPRO = 1.0e10  # 1e8 according to STR
K_A_BAC = 1.0e10  # 1e8 according to STR
K_A_BCO2 = 1.0e10  # 1e8 according to STR
K_A_BIN = 1.0e10  # 1e8 according to STR
P_ATM = 1.013  # bar
K_LA = 200.0
K_H_H2O_BASE = 0.0313
K_H_CO2_BASE = 0.035
K_H_CH4_BASE = 0.0014
K_H_H2_BASE = 7.8e-4
K_P = 5.0e4

DIGESTERPAR = np.array(
    [
        F_SI_XC,
        F_XI_XC,
        F_CH_XC,
        F_PR_XC,
        F_LI_XC,
        N_XC,
        N_I,
        N_AA,
        C_XC,
        C_SI,
        C_CH,
        C_PR,
        C_LI,
        C_XI,
        C_SU,
        C_AA,
        F_FA_LI,
        C_FA,
        F_H2_SU,
        F_BU_SU,
        F_PRO_SU,
        F_AC_SU,
        N_BAC,
        C_BU,
        C_PRO,
        C_AC,
        C_BAC,
        Y_SU,
        F_H2_AA,
        F_VA_AA,
        F_BU_AA,
        F_PRO_AA,
        F_AC_AA,
        C_VA,
        Y_AA,
        Y_FA,
        Y_C4,
        Y_PRO,
        C_CH4,
        Y_AC,
        Y_H2,
        K_DIS,
        K_HYD_CH,
        K_HYD_PR,
        K_HYD_LI,
        K_S_IN,
        K_M_SU,
        K_S_SU,
        PH_UL_AA,
        PH_LL_AA,
        K_M_AA,
        K_S_AA,
        K_M_FA,
        K_S_FA,
        K_IH2_FA,
        K_M_C4,
        K_S_C4,
        K_IH2_C4,
        K_M_PRO,
        K_S_PRO,
        K_IH2_PRO,
        K_M_AC,
        K_S_AC,
        K_I_NH3,
        PH_UL_AC,
        PH_LL_AC,
        K_M_H2,
        K_S_H2,
        PH_UL_H2,
        PH_LL_H2,
        K_DEC_XSU,
        K_DEC_XAA,
        K_DEC_XFA,
        K_DEC_XC4,
        K_DEC_XPRO,
        K_DEC_XAC,
        K_DEC_XH2,
        R,
        T_BASE,
        t_op,
        PK_W_BASE,
        PK_A_VA_BASE,
        PK_A_BU_BASE,
        PK_A_PRO_BASE,
        PK_A_AC_BASE,
        PK_A_CO2_BASE,
        PK_A_IN_BASE,
        K_A_BVA,
        K_A_BBU,
        K_A_BPRO,
        K_A_BAC,
        K_A_BCO2,
        K_A_BIN,
        P_ATM,
        K_LA,
        K_H_H2O_BASE,
        K_H_CO2_BASE,
        K_H_CH4_BASE,
        K_H_H2_BASE,
        K_P,
    ]
)

V_LIQ = 3400  # m3, size of BSM2 AD
V_GAS = 300  # m3, size of BSM2 AD

DIM_D = np.array([V_LIQ, V_GAS])

# parameters for ASM2ADM and ADM2ASM interfaces
# could be put it their own initialisation file
COD_EQUIV = 40.0 / 14.0
FNAA = N_AA * 14.0  # fraction of N in amino acids and Xpr as in ADM1 report
FNXC = N_XC * 14.0  # N content of composite material based on BSM2
FNBAC = N_BAC * 14.0  # N content of biomass based on BSM1, same in AS and AD
FXNI = N_I * 14.0  # N content of inerts XI and XP, same in AS and AD
FSNI = 0.0  # N content of SI, assumed zero in ASM1 and BSM1
FSNI_ADM = N_I * 14.0  # N content of SI in the AD system
# fnbac, fxni and fsni are adjusted to fit the benchmark values of iXB=0.08 and
# iXP=0.06 in the AS.
FRLIXS = 0.7  # lipid fraction of non-nitrogenous XS in BSM2
FRLIBAC = 0.4  # lipid fraction of non-nitrogenous biomass in BSM2
FRXS_ADM = 0.68  # anaerobically degradable fraction of AS biomass in BSM2
FDEGRADE_ADM = 0  # amount of AS XI and XP degradable in AD, zero in BSM2
FRXS_AS = 0.79  # aerobically degradable fraction of AD biomass in BSM2
FDEGRADE_AS = 0  # amount of AD XI and XP degradable in AS, zero in BSM2

PH_ADM_INIT = 7.0  # initial value of pH in ADM to be used by interfaces for the first sample

INTERFACEPAR = np.array(
    [
        COD_EQUIV,
        FNAA,
        FNXC,
        FNBAC,
        FXNI,
        FSNI,
        FSNI_ADM,
        FRLIXS,
        FRLIBAC,
        FRXS_ADM,
        FDEGRADE_ADM,
        FRXS_AS,
        FDEGRADE_AS,
        R,
        T_BASE,
        t_op,
        PK_W_BASE,
        PK_A_VA_BASE,
        PK_A_BU_BASE,
        PK_A_PRO_BASE,
        PK_A_AC_BASE,
        PK_A_CO2_BASE,
        PK_A_IN_BASE,
    ]
)

# parameters for the pHdelay function
PHINIT = PH_ADM_INIT
PHTIMECONST = 0.01
