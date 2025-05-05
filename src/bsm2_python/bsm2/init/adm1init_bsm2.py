"""This file initiates parameter values and sets initial conditions for the model implementation of `adm1_bsm2.py`.

Note that some of the parameter values deviate from the values given in the ADM1-STR (Batstone et al., 2002).
The state values are based on BSM2 technical report.
"""

import numpy as np

S_SU = 0.0124  # monosaccharides (kg COD/m3)
"""Monosaccharides [kg(COD) ⋅ m⁻³]."""
S_AA = 0.0055  # amino acids (kg COD/m3)
"""Amino acids [kg(COD) ⋅ m⁻³]."""
S_FA = 0.1074  # long chain fatty acids (LCFA) (kg COD/m3)
"""Long chain fatty acids (LCFA) [kg(COD) ⋅ m⁻³]."""
S_VA = 0.0123  # total valerate (kg COD/m3)
"""Total valerate [kg(COD) ⋅ m⁻³]."""
S_BU = 0.0140  # total butyrate (kg COD/m3)
"""Total butyrate [kg(COD) ⋅ m⁻³]."""
S_PRO = 0.0176  # total propionate (kg COD/m3)
"""Total propionate [kg(COD) ⋅ m⁻³]."""
S_AC = 0.0893  # total acetate (kg COD/m3)
"""Total acetate [kg(COD) ⋅ m⁻³]."""
S_H2 = 2.5055e-7  # hydrogen gas (kg COD/m3)
"""Hydrogen gas [kg(COD) ⋅ m⁻³]."""
S_CH4 = 0.0555  # methane gas (kg COD/m3)
"""Methane gas [kg(COD) ⋅ m⁻³]."""
S_IC = 0.0951  # inorganic carbon (kmole C/m3)
"""Inorganic carbon [kmol(C) ⋅ m⁻³]."""
S_IN = 0.0945  # inorganic nitrogen (kmole N/m3)
"""Inorganic nitrogen [kmol(N) ⋅ m⁻³]."""
S_I = 0.1309  # soluble inerts (kg COD/m3)
"""Soluble inerts [kg(COD) ⋅ m⁻³]."""
X_XC = 0.1079  # composites (kg COD/m3)
"""Composites [kg(COD) ⋅ m⁻³]."""
X_CH = 0.0205  # carbohydrates (kg COD/m3)
"""Carbohydrates [kg(COD) ⋅ m⁻³]."""
X_PR = 0.0842  # proteins (kg COD/m3)
"""Proteins [kg(COD) ⋅ m⁻³]."""
X_LI = 0.0436  # lipids (kg COD/m3)
"""Lipids [kg(COD) ⋅ m⁻³]."""
X_SU = 0.3122  # sugar degraders (kg COD/m3)
"""Sugar degraders [kg(COD) ⋅ m⁻³]."""
X_AA = 0.9317  # amino acid degraders (kg COD/m3)
"""Amino acid degraders [kg(COD) ⋅ m⁻³]."""
X_FA = 0.3384  # LCFA degraders (kg COD/m3)
"""LCFA degraders [kg(COD) ⋅ m⁻³]."""
X_C4 = 0.3258  # valerate and butyrate degraders (kg COD/m3)
"""Valerate and butyrate degraders [kg(COD) ⋅ m⁻³]."""
X_PRO = 0.1011  # propionate degraders (kg COD/m3)
"""Propionate degraders [kg(COD) ⋅ m⁻³]."""
X_AC = 0.6772  # acetate degraders (kg COD/m3)
"""Acetate degraders [kg(COD) ⋅ m⁻³]."""
X_H2 = 0.2848  # hydrogen degraders (kg COD/m3)
"""Hydrogen degraders [kg(COD) ⋅ m⁻³]."""
X_I = 17.2162  # particulate inerts (kg COD/m3)
"""Particulate inerts [kg(COD) ⋅ m⁻³]."""
S_CAT = 3.5659e-43  # cations (metallic ions, strong base) (kmole/m3)
"""Cations (metallic ions, strong base) [kmol ⋅ m⁻³]."""
S_AN = 0.0052  # anions (metallic ions, strong acid) (kmole/m3)
"""Anions (metallic ions, strong acid) [kmol ⋅ m⁻³]."""
S_HVA = 0.0123  # is actually Sva-
"""Is actually valeric acid S_va⁻ [kg(COD) ⋅ m⁻³]."""
S_HBU = 0.0140  # is actually Sbu-
"""Is actually butyric acid S_bu⁻ [kg(COD) ⋅ m⁻³]."""
S_HPRO = 0.0175  # is actually Spro-
"""Is actually propanoic acid S_pro⁻ [kg(COD) ⋅ m⁻³]."""
S_HAC = 0.0890  # is actually Sac-
"""Is actually acetic acid S_ac⁻ [kg(COD) ⋅ m⁻³]."""
S_HCO3 = 0.0857
"""Carbonate [kg(COD) ⋅ m⁻³]."""
S_NH3 = 0.0019
"""Ammonia [kg(COD) ⋅ m⁻³]."""
S_GAS_H2 = 1.1032e-5
"""Hydrogen gas (gaseous) [kg(COD) ⋅ m⁻³]."""
S_GAS_CH4 = 1.6535
"""Methane gas (gaseous) [kg(COD) ⋅ m⁻³]."""
S_GAS_CO2 = 0.0135
"""Carbon dioxide (gaseous) [kg(COD) ⋅ m⁻³]."""
Q_D = 178.4674  # influent flow rate (m3/d)
"""Influent flow rate [m³ ⋅ d⁻¹]."""
T_D = 35  # temperature (°C)
"""Temperature [°C]."""
S_D1_D = 0
"""Dummy state 1 [-]."""
S_D2_D = 0
"""Dummy state 2 [-]."""
S_D3_D = 0
"""Dummy state 3 [-]."""
X_D4_D = 0
"""Dummy state 4 [-]."""
X_D5_D = 0
"""Dummy state 5 [-]."""

S_H_ION = 5.4562e-8
"""Hydrogen ion [kg(COD) ⋅ m⁻³]."""

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
"""Initial values for ADM1 differential equations."""
# The following initial conditions are not used due to convergence duration -
# it would take around a year to reach steady state.
# DIGESTERINIT = np.ones(42)

# used by both DAE ADM implementations, adm1_DAE1 and adm1_DAE2.
# PHSOLVINIT = np.array([S_H_ion, S_hva, S_hbu, S_hpro, S_hac, S_hco3, S_nh3])
PHSOLVINIT = np.ones(7)
"""Initial concentrations of 7 components for pH solver. \n
[S_H_ION, S_HVA, S_HBU, S_HPRO, S_HAC, S_HCO3, S_NH3]
"""

# used by one DAE ADM implementation, adm1_DAE2.
# SH2SOLVINIT = S_h2
SH2SOLVINIT = 0
"""Initial concentration of S_H₂."""

F_SI_XC = 0.1
"""Fraction of composites to S_I by disintegration [-]."""
F_XI_XC = 0.2
"""Fraction of composites to X_I by disintegration [-]."""
F_CH_XC = 0.2
"""Fraction of composites to X_CH by disintegration [-]."""
F_PR_XC = 0.2
"""Fraction of composites to X_PR by disintegration [-]."""
F_LI_XC = 0.3
"""Fraction of composites to X_LI by disintegration [-]."""
N_XC = 0.0376 / 14.0
"""Nitrogen content of composites X_C [kmol(N) ⋅ kg(COD)⁻¹]."""
N_I = 0.06 / 14.0
"""Nitrogen content of inerts S_I_ and X_I [kmol(N) ⋅ kg(COD)⁻¹]."""
N_AA = 0.007
"""Nitrogen content of S_AA [kmol(N) ⋅ kg(COD)⁻¹]."""
C_XC = 0.02786
"""Carbon content of X_C [kmol(C) ⋅ kg(COD)⁻¹]."""
C_SI = 0.03
"""Carbon content of S_I [kmol(C) ⋅ kg(COD)⁻¹]."""
C_CH = 0.0313
"""Carbon content of S_CH [kmol(C) ⋅ kg(COD)⁻¹]."""
C_PR = 0.03
"""Carbon content of S_PR [kmol(C) ⋅ kg(COD)⁻¹]."""
C_LI = 0.022
"""Carbon content of S_LI [kmol(C) ⋅ kg(COD)⁻¹]."""
C_XI = 0.03
"""Carbon content of X_I [kmol(C) ⋅ kg(COD)⁻¹]."""
C_SU = 0.0313
"""Carbon content of S_SU [kmol(C) ⋅ kg(COD)⁻¹]."""
C_AA = 0.03
"""Carbon content of S_AA [kmol(C) ⋅ kg(COD)⁻¹]."""
F_FA_LI = 0.95
"""Yield (catabolism only) of S_FA on X_LI [-]."""
C_FA = 0.0217
"""Carbon content of S_FA [kmol(C) ⋅ kg(COD)⁻¹]."""
F_H2_SU = 0.19
"""Yield (catabolism only) of S_H2 on S_SU [-]."""
F_BU_SU = 0.13
"""Yield (catabolism only) of S_BU on S_SU [-]."""
F_PRO_SU = 0.27
"""Yield (catabolism only) of S_PRO on S_SU [-]."""
F_AC_SU = 0.41
"""Yield (catabolism only) of S_AC on S_SU [-]."""
N_BAC = 0.08 / 14.0
"""Nitrogen content of biomass [kmol(N) ⋅ kg(COD)⁻¹]."""
C_BU = 0.025
"""Carbon content of S_BU [kmol(C) ⋅ kg(COD)⁻¹]."""
C_PRO = 0.0268
"""Carbon content of S_PRO [kmol(C) ⋅ kg(COD)⁻¹]."""
C_AC = 0.0313
"""Carbon content of S_AC [kmol(C) ⋅ kg(COD)⁻¹]."""
C_BAC = 0.0313
"""Carbon content of biomass [kmol(C) ⋅ kg(COD)⁻¹]."""
Y_SU = 0.1
"""Yield of biomass, sugar degraders [-]."""
F_H2_AA = 0.06
"""Yield (catabolism only) of S_H2 on S_AA [-]."""
F_VA_AA = 0.23
"""Yield (catabolism only) of S_VA on S_AA [-]."""
F_BU_AA = 0.26
"""Yield (catabolism only) of S_BU on S_AA [-]."""
F_PRO_AA = 0.05
"""Yield (catabolism only) of S_PRO on S_AA [-]."""
F_AC_AA = 0.40
"""Yield (catabolism only) of S_AC on S_AA [-]."""
C_VA = 0.024
"""Carbon content of S_VA [kmol(C) ⋅ kg(COD)⁻¹]."""
Y_AA = 0.08
"""Yield of biomass, amino acid degraders [-]."""
Y_FA = 0.06
"""Yield of biomass, long chain fatty acid degraders [-]."""
Y_C4 = 0.06
"""Yield of biomass, valerate and butyrate degraders [-]."""
Y_PRO = 0.04
"""Yield of biomass, propionate degraders [-]."""
C_CH4 = 0.0156
"""Carbon content of S_CH4 [kmol(C) ⋅ kg(COD)⁻¹]."""
Y_AC = 0.05
"""Yield of biomass, acetate degraders [-]."""
Y_H2 = 0.06
"""Yield of biomass, hydrogen degraders [-]."""
K_DIS = 0.5
"""Disintegration rate [d⁻¹]."""
K_HYD_CH = 10.0
"""Hydrolysis rate of X_CH [d⁻¹]."""
K_HYD_PR = 10.0
"""Hydrolysis rate of X_PR [d⁻¹]."""
K_HYD_LI = 10.0
"""Hydrolysis rate of X_LI [d⁻¹]."""
K_S_IN = 1.0e-4
"""Inhibition parameter for inorganic nitrogen [kmol(N) ⋅ m⁻³]."""
K_M_SU = 30.0
"""Monod maximum specific uptake rate for uptake of sugars [d⁻¹]."""
K_S_SU = 0.5
"""Half saturation value for uptake of sugars [kg(COD) ⋅ m⁻³]."""
PH_UL_AA = 5.5
"""Upper limit of pH for uptake rate of amino acids [-]."""
PH_LL_AA = 4.0
"""Lower limit of pH for uptake rate of amino acids [-]."""
K_M_AA = 50.0
"""Monod maximum specific uptake rate for uptake of amino acids [d⁻¹]."""
K_S_AA = 0.3
"""Half saturation value for uptake of amino acids [kg(COD) ⋅ m⁻³]."""
K_M_FA = 6.0
"""Monod maximum specific uptake rate for uptake of LCFA [d⁻¹]."""
K_S_FA = 0.4
"""Half saturation value for uptake of LCFA [kg(COD) ⋅ m⁻³]."""
K_IH2_FA = 5.0e-6
"""50% inhibitory concentration of H₂ on LCFA uptake [kg(COD) ⋅ m⁻³]."""
K_M_C4 = 20.0
"""Monod maximum specific uptake rate for uptake of valerate and butyrate [d⁻¹]."""
K_S_C4 = 0.2
"""Half saturation value for uptake of valerate and butyrate [kg(COD) ⋅ m⁻³]."""
K_IH2_C4 = 1.0e-5
"""50% inhibitory concentration of H₂ on valerate and butyrate uptake [kg(COD) ⋅ m⁻³]."""
K_M_PRO = 13.0
"""Monod maximum specific uptake rate for uptake of propionate [d⁻¹]."""
K_S_PRO = 0.1
"""Half saturation value for uptake of propionate [kg(COD) ⋅ m⁻³]."""
K_IH2_PRO = 3.5e-6
"""50% inhibitory concentration of H₂ on propionate uptake [kg(COD) ⋅ m⁻³]."""
K_M_AC = 8.0
"""Monod maximum specific uptake rate for uptake of acetate [d⁻¹]."""
K_S_AC = 0.15
"""Half saturation value for uptake of acetate [kg(COD) ⋅ m⁻³]."""
K_I_NH3 = 0.0018
"""50% inhibitory concentration of NH₃ on acetate uptake [kg(COD) ⋅ m⁻³]."""
PH_UL_AC = 7.0
"""Upper limit of pH for uptake rate of acetate [-]."""
PH_LL_AC = 6.0
"""Lower limit of pH for uptake rate of acetate [-]."""
K_M_H2 = 35.0
"""Monod maximum specific uptake rate for uptake of hydrogen [d⁻¹]."""
K_S_H2 = 7.0e-6
"""Half saturation value for uptake of hydrogen [kg(COD) ⋅ m⁻³]."""
PH_UL_H2 = 6.0
"""Upper limit of pH for uptake rate of hydrogen [-]."""
PH_LL_H2 = 5.0
"""Lower limit of pH for uptake rate of hydrogen [-]."""
K_DEC_XSU = 0.02
"""Decay rate of X_SU [d⁻¹]."""
K_DEC_XAA = 0.02
"""Decay rate of X_AA [d⁻¹]."""
K_DEC_XFA = 0.02
"""Decay rate of X_FA [d⁻¹]."""
K_DEC_XC4 = 0.02
"""Decay rate of X_C4 [d⁻¹]."""
K_DEC_XPRO = 0.02
"""Decay rate of X_PRO [d⁻¹]."""
K_DEC_XAC = 0.02
"""Decay rate of X_AC [d⁻¹]."""
K_DEC_XH2 = 0.02
"""Decay rate of X_H2 [d⁻¹]."""
R = 0.083145  # universal gas constant dm3*bar/(mol*K) = 8.3145 J/(mol*K)
"""Universal gas constant [dm³ ⋅ bar ⋅ (mol ⋅ K)⁻¹] = 8.3145 [J ⋅ (mol ⋅ K)⁻¹]."""
T_BASE = 298.15  # 25 degC = 298.15 K
"""Base temperature (=25°C) [K]."""
t_op = 308.15  # operational temperature of AD and interfaces, 35 degC. Can be changed in the code.
"""Operational temperature of anaerobic digester and interfaces (=35°C) [K]."""
PK_W_BASE = 14.0
"""Parameter for calculation of K_W [-]."""
PK_A_VA_BASE = 4.86
"""Acid-base equilibrium constant for valerate [kmol ⋅ m⁻³]."""
PK_A_BU_BASE = 4.82
"""Acid-base equilibrium constant for butyrate [kmol ⋅ m⁻³]."""
PK_A_PRO_BASE = 4.88
"""Acid-base equilibrium constant for propionate [kmol ⋅ m⁻³]."""
PK_A_AC_BASE = 4.76
"""Acid-base equilibrium constant for acetate [kmol ⋅ m⁻³]."""
PK_A_CO2_BASE = 6.35
"""Acid-base equilibrium constant for inorganic carbon [kmol ⋅ m⁻³]."""
PK_A_IN_BASE = 9.25
"""Acid-base equilibrium constant for inorganic nitrogen [kmol ⋅ m⁻³]."""
K_A_BVA = 1.0e10  # 1e8 according to STR
"""Acid-base kinetic parameter for valerate [m³ ⋅ (kmol ⋅ d)⁻¹]."""
K_A_BBU = 1.0e10  # 1e8 according to STR
"""Acid-base kinetic parameter for butyrate [m³ ⋅ (kmol ⋅ d)⁻¹]."""
K_A_BPRO = 1.0e10  # 1e8 according to STR
"""Acid-base kinetic parameter for propionate [m³ ⋅ (kmol ⋅ d)⁻¹]."""
K_A_BAC = 1.0e10  # 1e8 according to STR
"""Acid-base kinetic parameter for acetate [m³ ⋅ (kmol ⋅ d)⁻¹]."""
K_A_BCO2 = 1.0e10  # 1e8 according to STR
"""Acid-base kinetic parameter for inorganic carbon [m³ ⋅ (kmol ⋅ d)⁻¹]."""
K_A_BIN = 1.0e10  # 1e8 according to STR
"""Acid-base kinetic parameter for inorganic nitrogen [m³ ⋅ (kmol ⋅ d)⁻¹]."""
P_ATM = 1.013  # bar
"""Atmospheric pressure [bar]."""
K_LA = 200.0
"""Transfer coefficient for gases [d⁻¹]."""
K_H_H2O_BASE = 0.0313
"""Henry's law coefficient for water vapor [kmol ⋅ m⁻³ ⋅ bar⁻¹]."""
K_H_CO2_BASE = 0.035
"""Henry's law coefficient for carbon dioxide [kmol ⋅ m⁻³ ⋅ bar⁻¹]."""
K_H_CH4_BASE = 0.0014
"""Henry's law coefficient for methane [kmol ⋅ m⁻³ ⋅ bar⁻¹]."""
K_H_H2_BASE = 7.8e-4
"""Henry's law coefficient for hydrogen [kmol ⋅ m⁻³ ⋅ bar⁻¹]."""
K_P = 5.0e4
"""Compensation factor for overpressure in the head space of the ADM [m³ ⋅ (bar ⋅ d)⁻¹]. \n
Must be adjusted if physical or operational conditions (volume, load etc.) of the ADM are changed."""

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
"""Digester parameters."""

V_LIQ = 3400  # m3, size of BSM2 AD
"""Liquid volume of anaerobic digestor [m³]."""
V_GAS = 300  # m3, size of BSM2 AD
"""Gas volume of anaerobic digestor [m³]."""

DIM_D = np.array([V_LIQ, V_GAS])
"""Reactor dimensions of the anaerobic digestor [m³]."""

# parameters for ASM2ADM and ADM2ASM interfaces
# could be put it their own initialization file
COD_EQUIV = 40.0 / 14.0
"""COD equivalent of nitrate and nitrite nitrogen [g(O₂) ⋅ g(N)⁻¹]."""
FNAA = N_AA * 14.0  # fraction of N in amino acids and Xpr as in ADM1 report
"""Fraction of N in amino acids and X_pr as in ADM1 report [-]."""
FNXC = N_XC * 14.0  # N content of composite material based on BSM2
"""N content of composite material based on BSM2 [-]."""
FNBAC = N_BAC * 14.0  # N content of biomass based on BSM1, same in AS and AD
"""N content of biomass based on BSM1, same in AS and AD [-]."""
FXNI = N_I * 14.0  # N content of inerts XI and XP, same in AS and AD
"""N content of inerts X_I and X_P, same in AS and AD."""
FSNI = 0.0  # N content of SI, assumed zero in ASM1 and BSM1
""""N content of S_I, assumed zero in ASM1 and BSM1."""
FSNI_ADM = N_I * 14.0  # N content of SI in the AD system
"""N content of S_I in the AD system."""
# fnbac, fxni and fsni are adjusted to fit the benchmark values of iXB=0.08 and
# iXP=0.06 in the AS.
FRLIXS = 0.7  # lipid fraction of non-nitrogenous XS in BSM2
"""Lipid fraction of non-nitrogenous X_S in BSM2."""
FRLIBAC = 0.4  # lipid fraction of non-nitrogenous biomass in BSM2
"""Lipid fraction of non-nitrogenous biomass in BSM2."""
FRXS_ADM = 0.68  # anaerobically degradable fraction of AS biomass in BSM2
"""Anaerobically degradable fraction of AS biomass in BSM2."""
FDEGRADE_ADM = 0  # amount of AS XI and XP degradable in AD, zero in BSM2
"""Amount of AS X_I and X_P degradable in AD, zero in BSM2."""
FRXS_AS = 0.79  # aerobically degradable fraction of AD biomass in BSM2
"""Aerobically degradable fraction of AD biomass in BSM2."""
FDEGRADE_AS = 0  # amount of AD XI and XP degradable in AS, zero in BSM2
"""Amount of AD X_I and X_P degradable in AS, zero in BSM2."""

PH_ADM_INIT = 7.0  # initial value of pH in ADM to be used by interfaces for the first sample
"""Initial value of pH in ADM to be used by interfaces for the first sample."""

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
"""Interface parameters needed for ASM2ADM and ADM2ASM interfaces."""

# parameters for the pHdelay function
PHINIT = PH_ADM_INIT
"""Initial value of pH in ADM."""
PHTIMECONST = 0.01
"""Time constant for pH function."""
