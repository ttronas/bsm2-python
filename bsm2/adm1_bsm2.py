import numpy as np
from scipy.integrate import odeint
from numba import jit
import warnings


indices_components = np.arange(42)
S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc, X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an, S_hva, S_hbu, S_hpro, S_hac, S_hco3, S_nh3, S_gas_h2, S_gas_ch4, S_gas_co2, Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D = indices_components

class ADM1Reactor:
    def __init__(self, yd0, digesterpar, interfacepar, dim):

        self.yd0 = yd0
        self.digesterpar = digesterpar
        self.interfacepar = interfacepar
        self.dim = dim


    def outputs(self, timestep, step, y_in1, T_op):
        """
        Returns the solved differential equations based on ADM1 model

        Parameters
        timestep : float
            Time distance to integrate over
        step : float
            Current time
        y_in1 : np.ndarray(22)
            concentrations of the 21 standard components (13 ASM1 components, TSS, Q, T and 5 dummy states) plus pH in the anaerobic digester
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
             SD1, SD2, SD3, XD4, XD5, pH_adm]
        T_op : float
            Operational temperature of digester. At the moment very rudimentary implementation! No heat losses / transfer embedded!
        """

        yd_out = np.zeros(51)

        f_sI_xc, f_xI_xc, f_ch_xc, f_pr_xc, f_li_xc, N_xc, N_I, N_aa, C_xc, C_sI, C_ch, C_pr, C_li, C_xI, C_su, C_aa, f_fa_li, C_fa, f_h2_su, f_bu_su, f_pro_su, f_ac_su, N_bac, C_bu, C_pro, C_ac, C_bac, Y_su, f_h2_aa, f_va_aa, f_bu_aa, f_pro_aa, f_ac_aa, C_va, Y_aa, Y_fa, Y_c4, Y_pro, C_ch4, Y_ac, Y_h2, k_dis, k_hyd_ch, k_hyd_pr, k_hyd_li, K_S_IN, k_m_su, K_S_su, pH_UL_aa, pH_LL_aa, k_m_aa, K_S_aa, k_m_fa, K_S_fa, K_Ih2_fa, k_m_c4, K_S_c4, K_Ih2_c4, k_m_pro, K_S_pro, K_Ih2_pro, k_m_ac, K_S_ac, K_I_nh3, pH_UL_ac, pH_LL_ac, k_m_h2, K_S_h2, pH_UL_h2, pH_LL_h2, k_dec_Xsu, k_dec_Xaa, k_dec_Xfa, k_dec_Xc4, k_dec_Xpro, k_dec_Xac, k_dec_Xh2, R, T_base, _, pK_w_base, pK_a_va_base, pK_a_bu_base, pK_a_pro_base, pK_a_ac_base, pK_a_co2_base, pK_a_IN_base, k_A_Bva, k_A_Bbu, k_A_Bpro, k_A_Bac, k_A_Bco2, k_A_BIN, P_atm, kLa, K_H_h2o_base, K_H_co2_base, K_H_ch4_base, K_H_h2_base, k_P = self.digesterpar

        t_eval = np.array([step, step+timestep])    # time interval for odeint

        y_out1 = asm2adm(y_in1, T_op, self.interfacepar)
        # [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc, X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an, Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D]
        yd_in = np.zeros(51)
        y_in2 = np.zeros(35)

        yd_in[:S_hva] = y_out1[:26]
        yd_in[Q_D:] = y_out1[26:]

        ode = odeint(adm1equations, self.yd0, t_eval, tfirst=True, args=(yd_in, self.digesterpar, T_op, self.dim))
        yd_int = ode[1]
        # [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc, X_ch, X_pr,
        #  X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an, S_hva, S_hbu, S_hpro, S_hac,
        #  S_hco3, S_nh3, S_gas_h2, S_gas_ch4, S_gas_co2, Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D]
        self.yd0[:] = yd_int[:]  # initial integration values for next integration

        # y = yd_out
        # u = yd_in
        # x : yd_int

        factor = (1.0/T_base - 1.0/T_op)/(100.0*R)
        # K_H_h2 = K_H_h2_base*np.exp(-4180.0*factor)     # T adjustment for K_H_h2
        # K_H_ch4 = K_H_ch4_base*np.exp(-14240.0*factor)  # T adjustment for K_H_ch4
        # K_H_co2 = K_H_co2_base*np.exp(-19410.0*factor)  # T adjustment for K_H_co2
        K_w = 10 ** (-pK_w_base) *np.exp(55900.0*factor) # T adjustment for K_w
        p_gas_h2o = K_H_h2o_base*np.exp(5290.0*(1.0/T_base - 1.0/T_op))  # T adjustment for water vapour saturation pressure

        yd_out[:S_hva] = yd_int[:S_hva]

        yd_out[26] = yd_in[Q_D]  # flow

        yd_out[27] = T_op - 273.15  # Temp = 35 degC

        yd_out[28] = yd_in[S_D1_D]  # Dummy state 1, soluble
        yd_out[29] = yd_in[S_D2_D]  # Dummy state 2, soluble  
        yd_out[30] = yd_in[S_D3_D]  # Dummy state 3, soluble
        yd_out[31] = yd_in[X_D4_D]  # Dummy state 1, particulate
        yd_out[32] = yd_in[X_D5_D]  # Dummy state 2, particulate

        p_gas_h2 = yd_int[S_gas_h2]*R*T_op/16.0
        p_gas_ch4 = yd_int[S_gas_ch4]*R*T_op/64.0
        p_gas_co2 = yd_int[S_gas_co2]*R*T_op
        P_gas = p_gas_h2 + p_gas_ch4 + p_gas_co2 + p_gas_h2o
        q_gas = max(k_P*(P_gas - P_atm), 0)

        # procT8 = kLa*(yd_int[S_h2] - 16.0*K_H_h2*p_gas_h2)
        # procT9 = kLa*(yd_int[S_ch4] - 64.0*K_H_ch4*p_gas_ch4)
        # procT10 = kLa*((yd_int[S_IC] - yd_int[S_hco3]) - K_H_co2*p_gas_co2)
        
        phi = yd_int[S_cat] + (yd_int[S_IN] - yd_int[S_nh3]) - yd_int[S_hco3] - yd_int[S_hac]/64.0 - yd_int[S_hpro]/112.0 - yd_int[S_hbu]/160.0 - yd_int[S_hva]/208.0 - yd_int[S_an]
        S_H_ion = -phi*0.5 + 0.5*np.sqrt(phi*phi + 4.0*K_w)

        yd_out[33] = -np.log10(S_H_ion)  # pH
        yd_out[34] = S_H_ion
        yd_out[35] = yd_int[S_hva]
        yd_out[36] = yd_int[S_hbu]
        yd_out[37] = yd_int[S_hpro]
        yd_out[38] = yd_int[S_hac]
        yd_out[39] = yd_int[S_hco3]
        yd_out[40] = yd_int[S_IC] - yd_int[S_hco3]  # SCO2
        yd_out[41] = yd_int[S_nh3]
        yd_out[42] = yd_int[S_IN] - yd_int[S_nh3]  # SNH4+
        yd_out[43] = yd_int[S_gas_h2]
        yd_out[44] = yd_int[S_gas_ch4]
        yd_out[45] = yd_int[S_gas_co2]
        yd_out[46] = p_gas_h2
        yd_out[47] = p_gas_ch4
        yd_out[48] = p_gas_co2
        yd_out[49] = P_gas  # total head space pressure from H2, CH4, CO2 and H2O
        yd_out[50] = q_gas * P_gas/P_atm  # The output gas flow is recalculated to atmospheric pressure (normalization)

        y_in2[:33] = yd_out[:33]
        # [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
        # X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
        # Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D, pH, T_WW]
        y_in2[33] = yd_out[33]  # pH
        y_in2[34] = yd_out[27]  # Temperature
        y_out2 = adm2asm(y_in2, T_op, self.interfacepar)

        return y_out2, yd_out, y_out1

# 0     1     2     3     4     5      6     7     8      9     10    11   12    13    
# S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc, X_ch, 
# 14    15    16    17    18    19    20     21    22    23   24     25    26     27
# X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an, S_hva, S_hbu, 
# 28      29     30      31     32        33         34         35   36   37      38      39      40      41    
# S_hpro, S_hac, S_hco3, S_nh3, S_gas_h2, S_gas_ch4, S_gas_co2, Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D

def adm1equations(t, yd, yd_in, digesterpar, T_op, dim):
    """Returns an array containing the differential equations based on ASM1

    Parameters
    ----------
    t : np.ndarray
        Time interval for integration, needed for the solver
    yd : np.ndarray
        Solution of the differential equations, needed for the solver
    yd_in : np.ndarray
        Reactor inlet concentrations of 42 components (26 ADM1 components, 9 other gas-related components, Q, T and 5 dummy states)
        [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc, X_ch, X_pr,
         X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an, S_hva, S_hbu, S_hpro, S_hac,
         S_hco3, S_nh3, S_gas_h2, S_gas_ch4, S_gas_co2, Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D]
    digesterpar : np.ndarray
        Digester parameters
    T_op : float
        Operating temperature
    dim : np.ndarray
        Reactor dimensions

    Returns
    -------
    np.ndarray
        Array containing the differential values dy of yd_in based on ADM1
    """
    # u = yd_in
    # x = yd
    # dx = dyd
    dyd = np.zeros(42)
    ydtemp = np.zeros(42)
    inhib = np.zeros(6)
    
    
    f_sI_xc, f_xI_xc, f_ch_xc, f_pr_xc, f_li_xc, N_xc, N_I, N_aa, C_xc, C_sI, C_ch, C_pr, C_li, C_xI, C_su, C_aa, f_fa_li, C_fa, f_h2_su, f_bu_su, f_pro_su, f_ac_su, N_bac, C_bu, C_pro, C_ac, C_bac, Y_su, f_h2_aa, f_va_aa, f_bu_aa, f_pro_aa, f_ac_aa, C_va, Y_aa, Y_fa, Y_c4, Y_pro, C_ch4, Y_ac, Y_h2, k_dis, k_hyd_ch, k_hyd_pr, k_hyd_li, K_S_IN, k_m_su, K_S_su, pH_UL_aa, pH_LL_aa, k_m_aa, K_S_aa, k_m_fa, K_S_fa, K_Ih2_fa, k_m_c4, K_S_c4, K_Ih2_c4, k_m_pro, K_S_pro, K_Ih2_pro, k_m_ac, K_S_ac, K_I_nh3, pH_UL_ac, pH_LL_ac, k_m_h2, K_S_h2, pH_UL_h2, pH_LL_h2, k_dec_Xsu, k_dec_Xaa, k_dec_Xfa, k_dec_Xc4, k_dec_Xpro, k_dec_Xac, k_dec_Xh2, R, T_base, _, pK_w_base, pK_a_va_base, pK_a_bu_base, pK_a_pro_base, pK_a_ac_base, pK_a_co2_base, pK_a_IN_base, k_A_Bva, k_A_Bbu, k_A_Bpro, k_A_Bac, k_A_Bco2, k_A_BIN, P_atm, kLa, K_H_h2o_base, K_H_co2_base, K_H_ch4_base, K_H_h2_base, k_P = digesterpar

    V_liq, V_gas = dim

    ydtemp[:] = yd[:]
    ydtemp[ydtemp < 0.0] = 0.0

    eps = 1.0e-6

    factor = (1.0/T_base - 1.0/T_op)/(100.0*R)
    K_w = 10 ** -pK_w_base * np.exp(55900.0 * factor)  # T adjustment for K_w
    K_a_va = 10 ** -pK_a_va_base
    K_a_bu = 10 ** -pK_a_bu_base
    K_a_pro = 10 ** -pK_a_pro_base
    K_a_ac = 10 ** -pK_a_ac_base
    K_a_co2 = 10 ** -pK_a_co2_base * np.exp(7646.0 * factor)  # T adjustment for K_a_co2
    K_a_IN = 10 ** -pK_a_IN_base * np.exp(51965.0 * factor)  # T adjustment for K_a_IN

    K_H_h2 = K_H_h2_base * np.exp(-4180.0 * factor)  # T adjustment for K_H_h2
    K_H_ch4 = K_H_ch4_base * np.exp(-14240.0 * factor)  # T adjustment for K_H_ch4
    K_H_co2 = K_H_co2_base * np.exp(-19410.0 * factor)  # T adjustment for K_H_co2
    p_gas_h2o = K_H_h2o_base * np.exp(5290.0 * (1.0/T_base - 1.0/T_op))  # T adjustment for water vapour saturation pressure
    
    phi = ydtemp[S_cat] + (ydtemp[S_IN] - ydtemp[S_nh3]) - ydtemp[S_hco3] - ydtemp[S_hac]/64.0 - ydtemp[S_hpro]/112.0 - ydtemp[S_hbu]/160.0 - ydtemp[S_hva]/208.0 - ydtemp[S_an]
    S_H_ion = -phi*0.5 + 0.5*np.sqrt(phi*phi + 4.0*K_w)  # SH+
    pH_op = -np.log10(S_H_ion)  # pH

    p_gas_h2 = ydtemp[S_gas_h2]*R*T_op/16.0
    p_gas_ch4 = ydtemp[S_gas_ch4]*R*T_op/64.0
    p_gas_co2 = ydtemp[S_gas_co2]*R*T_op
    P_gas = p_gas_h2 + p_gas_ch4 + p_gas_co2 + p_gas_h2o

    q_gas = max(k_P*(P_gas-P_atm), 0)

    # Hill function on SH+ used within BSM2, ADM1 Workshop, Copenhagen 2005.
    pHLim_aa = 10 ** (-(pH_UL_aa + pH_LL_aa)/2.0)
    pHLim_ac = 10 ** (-(pH_UL_ac + pH_LL_ac)/2.0)
    pHLim_h2 = 10 ** (-(pH_UL_h2 + pH_LL_h2)/2.0)
    n_aa = 3.0 / (pH_UL_aa - pH_LL_aa)
    n_ac = 3.0 / (pH_UL_ac - pH_LL_ac)
    n_h2 = 3.0 / (pH_UL_h2 - pH_LL_h2)
    I_pH_aa = pHLim_aa ** n_aa / (S_H_ion ** n_aa + pHLim_aa ** n_aa)
    I_pH_ac = pHLim_ac ** n_ac / (S_H_ion ** n_ac + pHLim_ac ** n_ac)
    I_pH_h2 = pHLim_h2 ** n_h2 / (S_H_ion ** n_h2 + pHLim_h2 ** n_h2)

    I_IN_lim = 1.0/(1.0 + K_S_IN/ydtemp[S_IN])
    I_h2_fa = 1.0/(1.0 + ydtemp[S_h2]/K_Ih2_fa)
    I_h2_c4 = 1.0/(1.0 + ydtemp[S_h2]/K_Ih2_c4)
    I_h2_pro = 1.0/(1.0 + ydtemp[S_h2]/K_Ih2_pro)
    I_nh3 = 1.0/(1.0 + ydtemp[S_nh3]/K_I_nh3)

    inhib[0] = I_pH_aa * I_IN_lim
    inhib[1] = inhib[0] * I_h2_fa
    inhib[2] = inhib[0] * I_h2_c4
    inhib[3] = inhib[0] * I_h2_pro
    inhib[4] = I_pH_ac * I_IN_lim * I_nh3
    inhib[5] = I_pH_h2 * I_IN_lim


    proc1 = k_dis*ydtemp[X_xc]
    proc2 = k_hyd_ch*ydtemp[X_ch]
    proc3 = k_hyd_pr*ydtemp[X_pr]
    proc4 = k_hyd_li*ydtemp[X_li]
    proc5 = k_m_su*ydtemp[S_su]/(K_S_su+ydtemp[S_su])*ydtemp[X_su]*inhib[0]
    proc6 = k_m_aa*ydtemp[S_aa]/(K_S_aa+ydtemp[S_aa])*ydtemp[X_aa]*inhib[0]
    proc7 = k_m_fa*ydtemp[S_fa]/(K_S_fa+ydtemp[S_fa])*ydtemp[X_fa]*inhib[1]
    proc8 = k_m_c4*ydtemp[S_va]/(K_S_c4+ydtemp[S_va])*ydtemp[X_c4]*ydtemp[S_va]/(ydtemp[S_va]+ydtemp[S_bu]+eps)*inhib[2]
    proc9 = k_m_c4*ydtemp[S_bu]/(K_S_c4+ydtemp[S_bu])*ydtemp[X_c4]*ydtemp[S_bu]/(ydtemp[S_va]+ydtemp[S_bu]+eps)*inhib[2]
    proc10 = k_m_pro*ydtemp[S_pro]/(K_S_pro+ydtemp[S_pro])*ydtemp[X_pro]*inhib[3]
    proc11 = k_m_ac*ydtemp[S_ac]/(K_S_ac+ydtemp[S_ac])*ydtemp[X_ac]*inhib[4]
    proc12 = k_m_h2*ydtemp[S_h2]/(K_S_h2+ydtemp[S_h2])*ydtemp[X_h2]*inhib[5]
    proc13 = k_dec_Xsu*ydtemp[X_su]
    proc14 = k_dec_Xaa*ydtemp[X_aa]
    proc15 = k_dec_Xfa*ydtemp[X_fa]
    proc16 = k_dec_Xc4*ydtemp[X_c4]
    proc17 = k_dec_Xpro*ydtemp[X_pro]
    proc18 = k_dec_Xac*ydtemp[X_ac]
    proc19 = k_dec_Xh2*ydtemp[X_h2]

    procA4 = k_A_Bva*(ydtemp[S_hva]*(K_a_va+S_H_ion)-K_a_va*ydtemp[S_va])
    procA5 = k_A_Bbu*(ydtemp[S_hbu]*(K_a_bu+S_H_ion)-K_a_bu*ydtemp[S_bu])
    procA6 = k_A_Bpro*(ydtemp[S_hpro]*(K_a_pro+S_H_ion)-K_a_pro*ydtemp[S_pro])
    procA7 = k_A_Bac*(ydtemp[S_hac]*(K_a_ac+S_H_ion)-K_a_ac*ydtemp[S_ac])
    procA10 = k_A_Bco2*(ydtemp[S_hco3]*(K_a_co2+S_H_ion)-K_a_co2*ydtemp[S_IC])
    procA11 = k_A_BIN*(ydtemp[S_nh3]*(K_a_IN+S_H_ion)-K_a_IN*ydtemp[S_IN])

    procT8 = kLa*(ydtemp[S_h2]-16.0*K_H_h2*p_gas_h2)
    procT9 = kLa*(ydtemp[S_ch4]-64.0*K_H_ch4*p_gas_ch4)
    procT10 = kLa*((ydtemp[S_IC]-ydtemp[S_hco3])-K_H_co2*p_gas_co2)

    stoich1 = -C_xc + f_sI_xc * C_sI + f_ch_xc * C_ch + f_pr_xc * C_pr + f_li_xc * C_li + f_xI_xc * C_xI
    stoich2 = -C_ch + C_su
    stoich3 = -C_pr + C_aa
    stoich4 = -C_li + (1.0 - f_fa_li) * C_su + f_fa_li * C_fa
    stoich5 = -C_su + (1.0 - Y_su) * (f_bu_su * C_bu + f_pro_su * C_pro + f_ac_su * C_ac) + Y_su * C_bac
    stoich6 = -C_aa + (1.0 - Y_aa) * (f_va_aa * C_va + f_bu_aa * C_bu + f_pro_aa * C_pro + f_ac_aa * C_ac) + Y_aa * C_bac
    stoich7 = -C_fa + (1.0 - Y_fa) * 0.7 * C_ac + Y_fa * C_bac
    stoich8 = -C_va + (1.0 - Y_c4) * 0.54 * C_pro + (1.0 - Y_c4) * 0.31 * C_ac + Y_c4 * C_bac
    stoich9 = -C_bu + (1.0 - Y_c4) * 0.8 * C_ac + Y_c4 * C_bac
    stoich10 = -C_pro + (1.0 - Y_pro) * 0.57 * C_ac + Y_pro * C_bac
    stoich11 = -C_ac + (1.0 - Y_ac) * C_ch4 + Y_ac * C_bac
    stoich12 = (1.0 - Y_h2) * C_ch4 + Y_h2 * C_bac
    stoich13 = -C_bac + C_xc

    reac1 = proc2 + (1.0 - f_fa_li) * proc4 - proc5
    reac2 = proc3 - proc6
    reac3 = f_fa_li * proc4 - proc7
    reac4 = (1.0 - Y_aa) * f_va_aa * proc6 - proc8
    reac5 = (1.0 - Y_su) * f_bu_su * proc5 + (1.0 - Y_aa) * f_bu_aa * proc6 - proc9
    reac6 = (1.0 - Y_su) * f_pro_su * proc5 + (1.0 - Y_aa) * f_pro_aa * proc6 + (1.0 - Y_c4) * 0.54 * proc8 - proc10
    reac7 = (1.0 - Y_su) * f_ac_su * proc5 + (1.0 - Y_aa) * f_ac_aa * proc6 + (1.0 - Y_fa) * 0.7 * proc7 + (1.0 - Y_c4) * 0.31 * proc8 + (1.0 - Y_c4) * 0.8 * proc9 + (1.0 - Y_pro) * 0.57 * proc10 - proc11
    reac8 = (1.0 - Y_su) * f_h2_su * proc5 + (1.0 - Y_aa) * f_h2_aa * proc6 + (1.0 - Y_fa) * 0.3 * proc7 + (1.0 - Y_c4) * 0.15 * proc8 + (1.0 - Y_c4) * 0.2 * proc9 + (1.0 - Y_pro) * 0.43 * proc10 - proc12 - procT8
    reac9 = (1.0 - Y_ac) * proc11 + (1.0 - Y_h2) * proc12 - procT9
    reac10 = -stoich1 * proc1 - stoich2 * proc2 - stoich3 * proc3 - stoich4 * proc4 - stoich5 * proc5 - stoich6 * proc6 - stoich7 * proc7 - stoich8 * proc8 - stoich9 * proc9 - stoich10 * proc10 - stoich11 * proc11 - stoich12 * proc12 - stoich13 * proc13 - stoich13 * proc14 - stoich13 * proc15 - stoich13 * proc16 - stoich13 * proc17 - stoich13 * proc18 - stoich13 * proc19 - procT10
    reac11 = (N_xc - f_xI_xc * N_I - f_sI_xc * N_I - f_pr_xc * N_aa) * proc1 - Y_su * N_bac * proc5 + (N_aa - Y_aa * N_bac) * proc6 - Y_fa * N_bac * proc7 - Y_c4 * N_bac * proc8 - Y_c4 * N_bac * proc9 - Y_pro * N_bac * proc10 - Y_ac * N_bac * proc11 - Y_h2 * N_bac * proc12 + (N_bac - N_xc) * (proc13 + proc14 + proc15 + proc16 + proc17 + proc18 + proc19)
    reac12 = f_sI_xc * proc1
    reac13 = -proc1 + proc13 + proc14 + proc15 + proc16 + proc17 + proc18 + proc19
    reac14 = f_ch_xc * proc1 - proc2
    reac15 = f_pr_xc * proc1 - proc3
    reac16 = f_li_xc * proc1 - proc4
    reac17 = Y_su * proc5 - proc13
    reac18 = Y_aa * proc6 - proc14
    reac19 = Y_fa * proc7 - proc15
    reac20 = Y_c4 * proc8 + Y_c4 * proc9 - proc16
    reac21 = Y_pro * proc10 - proc17
    reac22 = Y_ac * proc11 - proc18
    reac23 = Y_h2 * proc12 - proc19
    reac24 = f_xI_xc * proc1

    dyd[S_su] = 1.0/V_liq*(yd_in[S_su]*(yd_in[S_su]-yd[S_su]))+reac1
    dyd[S_aa] = 1.0/V_liq*(yd_in[S_aa]*(yd_in[S_aa]-yd[S_aa]))+reac2
    dyd[S_fa] = 1.0/V_liq*(yd_in[S_fa]*(yd_in[S_fa]-yd[S_fa]))+reac3
    dyd[S_va] = 1.0/V_liq*(yd_in[S_va]*(yd_in[S_va]-yd[S_va]))+reac4
    dyd[S_bu] = 1.0/V_liq*(yd_in[S_bu]*(yd_in[S_bu]-yd[S_bu]))+reac5
    dyd[S_pro] = 1.0/V_liq*(yd_in[S_pro]*(yd_in[S_pro]-yd[S_pro]))+reac6
    dyd[S_ac] = 1.0/V_liq*(yd_in[S_ac]*(yd_in[S_ac]-yd[S_ac]))+reac7
    dyd[S_h2] = 1.0/V_liq*(yd_in[S_h2]*(yd_in[S_h2]-yd[S_h2]))+reac8
    dyd[S_ch4] = 1.0/V_liq*(yd_in[S_ch4]*(yd_in[S_ch4]-yd[S_ch4]))+reac9
    dyd[S_IC] = 1.0/V_liq*(yd_in[S_IC]*(yd_in[S_IC]-yd[S_IC]))+reac10
    dyd[S_IN] = 1.0/V_liq*(yd_in[S_IN]*(yd_in[S_IN]-yd[S_IN]))+reac11
    dyd[S_I] = 1.0/V_liq*(yd_in[S_I]*(yd_in[S_I]-yd[S_I]))+reac12
    dyd[X_xc] = 1.0/V_liq*(yd_in[X_xc]*(yd_in[X_xc]-yd[X_xc]))+reac13
    dyd[X_ch] = 1.0/V_liq*(yd_in[X_ch]*(yd_in[X_ch]-yd[X_ch]))+reac14
    dyd[X_pr] = 1.0/V_liq*(yd_in[X_pr]*(yd_in[X_pr]-yd[X_pr]))+reac15
    dyd[X_li] = 1.0/V_liq*(yd_in[X_li]*(yd_in[X_li]-yd[X_li]))+reac16
    dyd[X_su] = 1.0/V_liq*(yd_in[X_su]*(yd_in[X_su]-yd[X_su]))+reac17
    dyd[X_aa] = 1.0/V_liq*(yd_in[X_aa]*(yd_in[X_aa]-yd[X_aa]))+reac18
    dyd[X_fa] = 1.0/V_liq*(yd_in[X_fa]*(yd_in[X_fa]-yd[X_fa]))+reac19
    dyd[X_c4] = 1.0/V_liq*(yd_in[X_c4]*(yd_in[X_c4]-yd[X_c4]))+reac20
    dyd[X_pro] = 1.0/V_liq*(yd_in[X_pro]*(yd_in[X_pro]-yd[X_pro]))+reac21
    dyd[X_ac] = 1.0/V_liq*(yd_in[X_ac]*(yd_in[X_ac]-yd[X_ac]))+reac22
    dyd[X_h2] = 1.0/V_liq*(yd_in[X_h2]*(yd_in[X_h2]-yd[X_h2]))+reac23
    dyd[X_I] = 1.0/V_liq*(yd_in[X_I]*(yd_in[X_I]-yd[X_I]))+reac24

    dyd[S_cat] = 1.0/V_liq*(yd_in[S_cat]*(yd_in[S_cat]-yd[S_cat]))
    dyd[S_an] = 1.0/V_liq*(yd_in[S_an]*(yd_in[S_an]-yd[S_an]))

    dyd[S_hva] = -procA4
    dyd[S_hbu] = -procA5
    dyd[S_hpro] = -procA6
    dyd[S_hac] = -procA7
    dyd[S_hco3] = -procA10
    dyd[S_nh3] = -procA11

    dyd[S_gas_h2] = -ydtemp[S_gas_h2]*q_gas/V_gas+procT8*V_liq/V_gas
    dyd[S_gas_ch4] = -ydtemp[S_gas_ch4]*q_gas/V_gas+procT9*V_liq/V_gas
    dyd[S_gas_co2] = -ydtemp[S_gas_co2]*q_gas/V_gas+procT10*V_liq/V_gas

    dyd[Q_D] = 0
    dyd[T_D] = 0

    # Dummy states for future use
    dyd[S_D1_D] = 0
    dyd[S_D2_D] = 0
    dyd[S_D3_D] = 0
    dyd[X_D4_D] = 0
    dyd[X_D5_D] = 0

    return dyd

def asm2adm(y_in1, T_op, interfacepar):
    """
    converts ASM1 flows to ADM1 flows
    New version (no 3) of the ASM1 to ADM1 interface based on discussions
    within the IWA TG BSM community during 2002-2006. Now also including charge balancing and temperature dependency for applicable parameters.
    Model parameters are defined in adm1init_bsm2.m
    
    Parameters
    ----------
    y_in1 : np.ndarray(22)
        concentrations of the 21 standard components (13 ASM1 components, TSS, Q, T and 5 dummy states) plus pH in the anaerobic digester
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
         SD1, SD2, SD3, XD4, XD5, pH_adm]
    T_op : float
        TODO: Check if T_op is working properly (especially with changing temperature)
        Temperature in K
        If temperature control of AD is used then the operational temperature
        of the ADM1 should also be an input rather than a defined parameter.
        Temperature in the ADM1 and the ASM1 to ADM1 and the ADM1 to ASM1 
        interfaces should be identical at every time instant.
    interfacepar : np.ndarray(23)
        23 parameters needed for ASM1 to ADM1 interface

    Returns
    -------
    y_out1 : np.ndarray(33)
        output of 33 ADM1 components (26 ADM1 components, Q, T and 5 dummy states)
        [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
         X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
         Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D]

    """
    CODequiv, fnaa, fnxc, fnbac, fxni, fsni, fsni_adm, frlixs, frlibac, frxs_adm, fdegrade_adm, frxs_as, fdegrade_as, R, T_base, _, pK_w_base, pK_a_va_base, pK_a_bu_base, pK_a_pro_base, pK_a_ac_base, pK_a_co2_base, pK_a_IN_base = interfacepar

    # y = y_out1
    # u = y_in1
    y_out1 = np.zeros(33)
    y_in1_temp = np.zeros(22)
    y_in1_temp2 = np.zeros(22)

    pH_adm = y_in1[21]

    factor = (1.0/T_base - 1.0/T_op)/(100.0*R)
    pK_w = pK_w_base - np.log10(np.exp(55900.0*factor))
    pK_a_co2 = pK_a_co2_base - np.log10(np.exp(7646.0*factor))
    pK_a_IN = pK_a_IN_base - np.log10(np.exp(51965.0*factor))
    alfa_va = 1.0/208.0*(-1.0/(1.0 + np.power(10, pK_a_va_base - pH_adm)))
    alfa_bu = 1.0/160.0*(-1.0/(1.0 + np.power(10, pK_a_bu_base - pH_adm)))
    alfa_pro = 1.0/112.0*(-1.0/(1.0 + np.power(10, pK_a_pro_base - pH_adm)))
    alfa_ac = 1.0/64.0*(-1.0/(1.0 + np.power(10, pK_a_ac_base - pH_adm)))
    alfa_co2 = -1.0/(1.0 + np.power(10, pK_a_co2 - pH_adm))
    alfa_IN = (np.power(10, pK_a_IN - pH_adm))/(1.0 + np.power(10, pK_a_IN - pH_adm))
    alfa_NH = 1.0/14000.0  # convert mgN/l into kmoleN/m3
    alfa_alk = -0.001  # convert moleHCO3/m3 into kmoleHCO3/m3
    alfa_NO = -1.0/14000.0  # convert mgN/l into kmoleN/m3
    
    # Let CODdemand be the COD demand of available electron 
    # acceptors prior to the anaerobic digester, i.e. oxygen and nitrate
    CODdemand = y_in1[7] + CODequiv*y_in1[8]

    # if extreme detail was used then some extra NH4 would be transformed
    # into N bound in biomass and some biomass would be formed when
    # removing the CODdemand (based on the yield). But on a total COD balance 
    # approach the below is correct (neglecting the N need for biomass growth)
    # The COD is reduced in a hierarchical approach in the order: 
    # 1) SS; 2) XS; 3) XBH; 4) XBA. It is no real improvement to remove SS and add
    # biomass. The net result is the same.

    if CODdemand > y_in1[1]:  # check if COD demand can be fulfilled by SS
        remaina = CODdemand - y_in1[1]
        y_in1_temp[1] = 0.0
        if remaina > y_in1[3]:  # check if COD demand can be fulfilled by XS
            remainb = remaina - y_in1[3]
            y_in1_temp[3] = 0.0
            if remainb > y_in1[4]:  # check if COD demand can be fulfilled by XBH
                remainc = remainb - y_in1[4]
                y_in1_temp[9] = y_in1_temp[9] + y_in1[4]*fnbac
                y_in1_temp[4] = 0.0
                if remainc > y_in1[5]:  # check if COD demand can be fulfilled by XBA
                    remaind = remainc - y_in1[5]
                    y_in1_temp[9] = y_in1_temp[9] + y_in1[5]*fnbac
                    y_in1_temp[5] = 0.0
                    y_in1_temp[7] = remaind
                    # if here we are in trouble, carbon shortage: an error printout should be given
                    # and execution stopped
                else:  # reduced all COD demand by use of SS, XS, XBH and XBA
                    y_in1_temp[5] = y_in1[5] - remainc
                    y_in1_temp[9] = y_in1_temp[9] + remainc*fnbac
            else:  # reduced all COD demand by use of SS, XS and XBH
                y_in1_temp[4] = y_in1[4] - remainb
                y_in1_temp[9] = y_in1_temp[9] + remainb*fnbac
        else:  # reduced all COD demand by use of SS and XS
            y_in1_temp[3] = y_in1[3] - remaina
    else:  # reduced all COD demand by use of SS
        y_in1_temp[1] = y_in1[1] - CODdemand

    # SS becomes part of amino acids when transformed into ADM
    # and any remaining SS is mapped to monosacharides (no N contents)
    # Enough SND must be available for mapping to amino acids

    sorgn = y_in1[10]/fnaa  # Saa COD equivalent to SND

    if sorgn >= y_in1_temp[1]:  # not all SND-N in terms of COD fits into amino acids
        y_out1[1] = y_in1_temp[1]  # map all SS COD into Saa
        y_in1_temp[10] = y_in1_temp[10] - y_in1_temp[1]*fnaa  # excess SND
        y_in1_temp[1] = 0.0  # all SS used
    else:  # all SND-N fits into amino acids
        y_out1[1] = sorgn  # map all SND related COD into Saa
        y_in1_temp[1] = y_in1_temp[1] - sorgn  # excess SS, which will become sugar in ADM1 i.e. no nitrogen association
        y_in1_temp[10] = 0.0  # all SND used

    # XS becomes part of Xpr (proteins) when transformed into ADM
    # and any remaining XS is mapped to Xch and Xli (no N contents)
    # Enough XND must be available for mapping to Xpr

    xorgn = y_in1[11]/fnaa  # Xpr COD equivalent to XND

    if xorgn >= y_in1_temp[3]:  # not all XND-N in terms of COD fits into Xpr
        xprtemp = y_in1_temp[3]  # map all XS COD into Spr
        y_in1_temp[11] = y_in1_temp[11] - y_in1_temp[3]*fnaa  # excess XND
        y_in1_temp[3] = 0.0  # all XS used
        xlitemp = 0.0
        xchtemp = 0.0
    else:  # all XND-N fits into Xpr
        xprtemp = xorgn  # map all XND related COD into Xpr
        xlitemp = frlixs*(y_in1_temp[3] - xorgn)  # part of XS COD not associated with N
        xchtemp = (1.0 - frlixs)*(y_in1_temp[3] - xorgn)  # part of XS COD not associated with N
        y_in1_temp[3] = 0.0  # all XS used
        y_in1_temp[11] = 0.0  # all XND used

    # Biomass becomes part of Xpr and XI when transformed into ADM
    # and any remaining XBH and XBA is mapped to Xch and Xli (no N contents)
    # Remaining XND-N can be used as nitrogen source to form Xpr

    biomass = y_in1_temp[4] + y_in1_temp[5]
    biomass_nobio = biomass*(1.0 - frxs_adm)  # part which is mapped to XI
    biomass_bioN = (biomass*fnbac - biomass_nobio*fxni)
    if biomass_bioN < 0.0:
        raise ValueError('Not enough biomass N to map the requested inert part')
    if (biomass_bioN/fnaa) <= (biomass - biomass_nobio):
        xprtemp2 = biomass_bioN/fnaa  # all biomass N used
        remainCOD = biomass - biomass_nobio - xprtemp2
        if (y_in1_temp[11]/fnaa) > remainCOD:  # use part of remaining XND-N to form proteins
            xprtemp2 = xprtemp2 + remainCOD
            y_in1_temp[11] = y_in1_temp[11] - remainCOD*fnaa
            remainCOD = 0.0
            y_in1_temp[4] = 0.0
            y_in1_temp[5] = 0.0
        else:  # use all remaining XND-N to form proteins
            xprtemp2 = xprtemp2 + y_in1_temp[11]/fnaa
            remainCOD = remainCOD - y_in1_temp[11]/fnaa
            y_in1_temp[11] = 0.0
        xlitemp2 = frlibac*remainCOD  # part of the COD not associated with N
        xchtemp2 = (1.0 - frlibac)*remainCOD  # part of the COD not associated with N
    else:
        xprtemp2 = biomass - biomass_nobio  # all biomass COD used
        y_in1_temp[11] = y_in1_temp[11] + biomass*fnbac - biomass_nobio*fxni - xprtemp2*fnaa  # any remaining N in XND
        xlitemp2 = 0.0
        xchtemp2 = 0.0
    y_in1_temp[4] = 0.0
    y_in1_temp[5] = 0.0

    # direct mapping of XI and XP to ADM1 XI (if fdegrade_adm = 0)
    # assumption: same N content in both ASM1 and ADM1 particulate inerts

    inertX = (1-fdegrade_adm)*(y_in1_temp[2] + y_in1_temp[6])

    # special case: IF part of XI and XP in the ASM can be degraded in the AD
    # we have no knowledge about the contents so we put it in as composites (Xc)
    # we need to keep track of the associated nitrogen
    # N content which may be different, take first from XI&XP-N, then XND-N, then SND-N,
    # then SNH. A similar principle could be used for other states.

    xc = 0.0
    xlitemp3 = 0.0
    xchtemp3 = 0.0
    if fdegrade_adm > 0:
        noninertX = fdegrade_adm*(y_in1_temp[2] + y_in1_temp[6])
        if fxni < fnxc:  # N in XI&XP(ASM) not enough
            xc = noninertX*fxni/fnxc
            noninertX = noninertX - noninertX*fxni/fnxc
            if y_in1_temp[11] < (noninertX*fnxc):  # N in XND not enough
                xc = xc + y_in1_temp[11]/fnxc
                noninertX = noninertX - y_in1_temp[11]/fnxc
                y_in1_temp[11] = 0.0
                if y_in1_temp[10] < (noninertX*fnxc):  # N in SND not enough
                    xc = xc + y_in1_temp[10]/fnxc
                    noninertX = noninertX - y_in1_temp[10]/fnxc
                    y_in1_temp[10] = 0.0
                    if y_in1_temp[9] < (noninertX*fnxc):  # N in SNH not enough
                        xc = xc + y_in1_temp[9]/fnxc
                        noninertX = noninertX - y_in1_temp[9]/fnxc
                        y_in1_temp[9] = 0.0
                        warnings.warn('Nitrogen shortage when converting biodegradable XI&XP')
                        # Putting remaining XI&XP as lipids (50%) and carbohydrates (50%)
                        xlitemp3 = 0.5*noninertX
                        xchtemp3 = 0.5*noninertX
                        noninertX = 0.0
                    else:  # N in SNH enough for mapping
                        xc = xc + noninertX
                        y_in1_temp[9] = y_in1_temp[9] - noninertX*fnxc
                        noninertX = 0.0
                else:  # N in SND enough for mapping
                    xc = xc + noninertX
                    y_in1_temp[10] = y_in1_temp[10] - noninertX*fnxc
                    noninertX = 0.0
            else:  # N in XND enough for mapping
                xc = xc + noninertX
                y_in1_temp[11] = y_in1_temp[11] - noninertX*fnxc
                noninertX = 0.0
        else:  # N in XI&XP(ASM) enough for mapping
            xc = xc + noninertX
            y_in1_temp[11] = y_in1_temp[11] + noninertX*(fxni-fnxc)  # put remaining N as XND
            noninertX = 0

    # Mapping of ASM SI to ADM1 SI
    # N content may be different, take first from SI-N, then SND-N, then XND-N,
    # then SNH. Similar principle could be used for other states.

    inertS = 0.0
    if fsni < fsni_adm:  # N in SI(ASM) not enough
        inertS = y_in1_temp[0]*fsni/fsni_adm
        y_in1_temp[0] = y_in1_temp[0] - y_in1_temp[0]*fsni/fsni_adm
        if y_in1_temp[10] < (y_in1_temp[0]*fsni_adm):  # N in SND not enough
            inertS = inertS + y_in1_temp[10]/fsni_adm
            y_in1_temp[0] = y_in1_temp[0] - y_in1_temp[10]/fsni_adm
            y_in1_temp[10] = 0.0
            if y_in1_temp[11] < (y_in1_temp[0]*fsni_adm):  # N in XND not enough
                inertS = inertS + y_in1_temp[11]/fsni_adm
                y_in1_temp[0] = y_in1_temp[0] - y_in1_temp[11]/fsni_adm
                y_in1_temp[11] = 0.0
                if y_in1_temp[9] < (y_in1_temp[0]*fsni_adm):  # N in SNH not enough
                    inertS = inertS + y_in1_temp[9]/fsni_adm
                    y_in1_temp[0] = y_in1_temp[0] - y_in1_temp[9]/fsni_adm
                    y_in1_temp[9] = 0.0
                    warnings.warn('Nitrogen shortage when converting SI')
                    # Putting remaining SI as monosacharides
                    y_in1_temp[1] = y_in1_temp[1] + y_in1_temp[0]
                    y_in1_temp[0] = 0.0
                else:  # N in SNH enough for mapping
                    inertS = inertS + y_in1_temp[0]
                    y_in1_temp[9] = y_in1_temp[9] - y_in1_temp[0]*fsni_adm
                    y_in1_temp[0] = 0.0
            else:  # N in XND enough for mapping
                inertS = inertS + y_in1_temp[0]
                y_in1_temp[11] = y_in1_temp[11] - y_in1_temp[0]*fsni_adm
                y_in1_temp[0] = 0.0
        else:  # N in SND enough for mapping
            inertS = inertS + y_in1_temp[0]
            y_in1_temp[10] = y_in1_temp[10] - y_in1_temp[0]*fsni_adm
            y_in1_temp[0] = 0.0
    else:  # N in SI(ASM) enough for mapping
        inertS = inertS + y_in1_temp[0]
        y_in1_temp[10] = y_in1_temp[10] + y_in1_temp[0]*(fsni-fsni_adm)  # put remaining N as SND
        y_in1_temp[0] = 0.0

    # Define the outputs including charge balance

    y_out1[0] = y_in1_temp[1]/1000.0
    y_out1[1] = y_out1[1]/1000.0
    y_out1[10] = (y_in1_temp[9] + y_in1_temp[10] + y_in1_temp[11])/14000.0
    y_out1[11] = inertS/1000.0
    y_out1[12] = xc/1000.0
    y_out1[13] = (xchtemp + xchtemp2 + xchtemp3)/1000.0
    y_out1[14] = (xprtemp + xprtemp2)/1000.0
    y_out1[15] = (xlitemp + xlitemp2 + xlitemp3)/1000.0
    y_out1[23] = (biomass_nobio + inertX)/1000.0
    y_out1[26] = y_in1[14]  # flow rate
    y_out1[27] = T_op - 273.15  # temperature, degC
    y_out1[28] = y_in1[16]  # dummy state
    y_out1[29] = y_in1[17]  # dummy state
    y_out1[30] = y_in1[18]  # dummy state
    y_out1[31] = y_in1[19]  # dummy state
    y_out1[32] = y_in1[20]  # dummy state

    # charge balance, output S_IC
    y_out1[9] = ((y_in1_temp2[8]*alfa_NO + y_in1_temp2[9]*alfa_NH + y_in1_temp2[12]*alfa_alk) - (y_out1[3]*alfa_va + y_out1[4]*alfa_bu + y_out1[5]*alfa_pro + y_out1[6]*alfa_ac + y_out1[10]*alfa_IN))/alfa_co2

    # calculate anions and cations based on full charge balance including H+ and OH-
    ScatminusSan = y_out1[3]*alfa_va + y_out1[4]*alfa_bu + y_out1[5]*alfa_pro + y_out1[6]*alfa_ac + y_out1[10]*alfa_IN + y_out1[9]*alfa_co2 + pow(10, (-pK_w + pH_adm)) - pow(10, -pH_adm)

    if ScatminusSan > 0:
        y_out1[24] = ScatminusSan
        y_out1[25] = 0.0
    else:
        y_out1[24] = 0.0
        y_out1[25] = -1.0*ScatminusSan

    # Finally there should be a input-output mass balance check here of COD and N

    return y_out1

def adm2asm(y_in2, T_op, interfacepar):
    """
    converts ADM1 flows to ASM1 flows
    New version (no 3) of the ADM1 to ASM1 interface based on discussions
    within the IWA TG BSM community during 2002-2006. Now also including charge
    balancing and temperature dependency for applicable parameters.
    Model parameters are defined in adm1init_bsm2.m
    
    Parameters
    ----------
    y_in2 : np.ndarray(35)
        concentrations of the 33 ADM1 components (26 ADM1 components, Q, T and 5 dummy states)
        plus pH in the anaerobic digester and wastewater temperature into the **ASM2ADM** interface
        [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
        X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
        Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D, pH, T_WW]
    T_op : float
        TODO: Check if T_op is working properly (especially with changing temperature)
        If temperature control of AD is used then the operational temperature
        of the ADM1 should also be an input rather than a defined parameter.
        Temperature in the ADM1 and the ASM1 to ADM1 and the ADM1 to ASM1 
        interfaces should be identical at every time instant.
    interfacepar : np.ndarray(23)
        23 parameters needed for ADM1 to ASM1 interface

    Returns
    -------
    y_out2 : np.ndarray(21)
        output of the 21 standard components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, T_WW,
         SD1, SD2, SD3, XD4, XD5]
    """
    CODequiv, fnaa, fnxc, fnbac, fxni, fsni, fsni_adm, frlixs, frlibac, frxs_adm, fdegrade_adm, frxs_as, fdegrade_as, R, T_base, _, pK_w_base, pK_a_va_base, pK_a_bu_base, pK_a_pro_base, pK_a_ac_base, pK_a_co2_base, pK_a_IN_base = interfacepar

    # y = y_out2
    # u = y_in2
    y_out2 = np.zeros(21)
    y_in2_temp = np.zeros(35)

    y_in2_temp[:] = y_in2[:]

    pH_adm = y_in2[33]

    factor = (1.0/T_base - 1.0/T_op)/(100.0*R)
    pK_w = pK_w_base - np.log10(np.exp(55900.0*factor))
    pK_a_co2 = pK_a_co2_base - np.log10(np.exp(7646.0*factor))
    pK_a_IN = pK_a_IN_base - np.log10(np.exp(51965.0*factor))
    alfa_va = 1.0/208.0*(-1.0/(1.0 + np.power(10, pK_a_va_base - pH_adm)))
    alfa_bu = 1.0/160.0*(-1.0/(1.0 + np.power(10, pK_a_bu_base - pH_adm)))
    alfa_pro = 1.0/112.0*(-1.0/(1.0 + np.power(10, pK_a_pro_base - pH_adm)))
    alfa_ac = 1.0/64.0*(-1.0/(1.0 + np.power(10, pK_a_ac_base - pH_adm)))
    alfa_co2 = -1.0/(1.0 + np.power(10, pK_a_co2 - pH_adm))
    alfa_IN = (np.power(10, pK_a_IN - pH_adm))/(1.0 + np.power(10, pK_a_IN - pH_adm))
    alfa_NH = 1.0/14000.0  # convert mgN/l into kmoleN/m3
    alfa_alk = -0.001  # convert moleHCO3/m3 into kmoleHCO3/m3
    alfa_NO = -1.0/14000.0  # convert mgN/l into kmoleN/m3


    # Biomass becomes part of XS and XP when transformed into ASM
    # Assume Npart of formed XS to be fnxc and Npart of XP to be fxni
    # Remaining N goes into the ammonia pool (also used as source if necessary)

    biomass = 1000.0*(y_in2_temp[16] + y_in2_temp[17] + y_in2_temp[18] + y_in2_temp[19] + y_in2_temp[20] + y_in2_temp[21] + y_in2_temp[22])
    biomass_nobio = biomass*(1.0 - frxs_as)   # part which is mapped to XP
    biomass_bioN = (biomass*fnbac - biomass_nobio*fxni)
    remainCOD = 0.0
    if biomass_bioN < 0.0:
        warnings.warn('Not enough biomass N to map the requested inert part of biomass')
        # We map as much as we can, and the remains go to XS!
        XPtemp = biomass*fnbac/fxni
        biomass_nobio = XPtemp
        biomass_bioN = 0.0
    else:
        XPtemp = biomass_nobio
    if (biomass_bioN/fnxc) <= (biomass - biomass_nobio):
        XStemp = biomass_bioN/fnxc        # all biomass N used
        remainCOD = biomass - biomass_nobio - XStemp
        if (y_in2_temp[10]*14000.0/fnaa) >= remainCOD:  # use part of remaining S_IN to form XS
            XStemp = XStemp + remainCOD
        else:
            raise ValueError('Not enough nitrogen to map the requested XS part of biomass')
            # System failure!
    else:
        XStemp = biomass - biomass_nobio  # all biomass COD used

    y_in2_temp[10] = y_in2_temp[10] + biomass*fnbac/14000.0 - XPtemp*fxni/14000.0 - XStemp*fnxc/14000.0  # any remaining N in S_IN
    y_out2[3] = (y_in2_temp[12] + y_in2_temp[13] + y_in2_temp[14] + y_in2_temp[15])*1000.0 + XStemp  # Xs = sum all X except Xi, + biomass as handled above
    y_out2[6] = XPtemp  # inert part of biomass

    # mapping of inert XI in AD into XI and possibly XS in AS
    # assumption: same N content in both ASM1 and ADM1 particulate inerts
    # special case: if part of XI in AD can be degraded in AS
    # we have no knowledge about the contents so we put it in as part substrate (XS)
    # we need to keep track of the associated nitrogen
    # N content may be different, take first from XI-N then S_IN,
    # Similar principle could be used for other states.

    inertX = (1.0-fdegrade_as)*y_in2_temp[23]*1000.0
    XStemp2 = 0.0
    noninertX = 0.0
    if fdegrade_as > 0.0:
        noninertX = fdegrade_as*y_in2_temp[23]*1000.0
        if fxni < fnxc:  # N in XI(AD) not enough
            XStemp2 = noninertX*fxni/fnxc
            noninertX = noninertX - noninertX*fxni/fnxc
            if (y_in2_temp[10]*14000.0) < (noninertX*fnxc):  # N in SNH not enough
                XStemp2 = XStemp2 + (y_in2_temp[10]*14000.0)/fnxc
                noninertX = noninertX - (y_in2_temp[10]*14000.0)/fnxc
                y_in2_temp[10] = 0.0
                warnings.warn('Nitrogen shortage when converting biodegradable XI')
                # Mapping what we can to XS and putting remaining XI back into XI of ASM
                inertX = inertX + noninertX
            else:  # N in S_IN enough for mapping
                XStemp2 = XStemp2 + noninertX
                y_in2_temp[10] = y_in2_temp[10] - noninertX*fnxc/14000.0
                noninertX = 0.0
        else:  # N in XI(AD) enough for mapping
            XStemp2 = XStemp2 + noninertX
            y_in2_temp[10] = y_in2_temp[10] + noninertX*(fxni - fnxc)/14000.0  # put remaining N as S_IN
            noninertX = 0

    y_out2[2] = inertX  # Xi = Xi*fdegrade_AS + possibly nonmappable XS
    y_out2[3] = y_out2[3] + XStemp2  # extra added XS (biodegradable XI)

    # Mapping of ADM SI to ASM1 SI
    # It is assumed that this mapping will be 100% on COD basis
    # N content may be different, take first from SI-N then from S_IN.
    # Similar principle could be used for other states.

    inertS = 0.0
    if fsni_adm < fsni:  # N in SI(AD) not enough
        inertS = y_in2_temp[11]*fsni_adm/fsni
        y_in2_temp[11] = y_in2_temp[11] - y_in2_temp[11]*fsni_adm/fsni
        if (y_in2_temp[10]*14.0) < (y_in2_temp[11]*fsni):  # N in S_IN not enough
            inertS = inertS + y_in2_temp[10]*14.0/fsni
            y_in2_temp[11] = y_in2_temp[11] - y_in2_temp[10]*14.0/fsni
            y_in2_temp[10] = 0.0
            raise ValueError('Not enough nitrogen to map the requested inert part of SI')
            # System failure: nowhere to put SI
        else:  # N in S_IN enough for mapping
            inertS = inertS + y_in2_temp[11]
            y_in2_temp[10] = y_in2_temp[10] - y_in2_temp[11]*fsni/14.0
            y_in2_temp[11] = 0.0
    else:  # N in SI(AD) enough for mapping
        inertS = inertS + y_in2_temp[11]
        y_in2_temp[10] = y_in2_temp[10] + y_in2_temp[11]*(fsni_adm - fsni)/14.0  # put remaining N as S_IN
        y_in2_temp[11] = 0.0

    y_out2[0] = inertS*1000.0  # Si = Si

    # Define the outputs including charge balance

    # nitrogen in biomass, composites, proteins
    # Xnd is the nitrogen part of Xs in ASM1. Therefore Xnd should be based on the
    # same variables as constitutes Xs, ie AD biomass (part not mapped to XP), xc and xpr if we assume
    # there is no nitrogen in carbohydrates and lipids. The N content of Xi is
    # not included in Xnd in ASM1 and should in my view not be included.

    y_out2[11] = fnxc*(XStemp + XStemp2) + fnxc*1000.0*y_in2_temp[12] + fnaa*1000.0*y_in2_temp[14]

    # Snd is the nitrogen part of Ss in ASM1. Therefore Snd should be based on the
    # same variables as constitutes Ss, and we assume
    # there is only nitrogen in the amino acids. The N content of Si is
    # not included in Snd in ASM1 and should in my view not be included.

    y_out2[10] = fnaa*1000.0*y_in2_temp[1]

    # sh2 and sch4 assumed to be stripped upon reentry to ASM side

    y_out2[1] = (y_in2_temp[0] + y_in2_temp[1] + y_in2_temp[2] + y_in2_temp[3] + y_in2_temp[4] + y_in2_temp[5] + y_in2_temp[6])*1000.0  # Ss = sum all S except Sh2, Sch4, Si, Sic, Sin

    y_out2[9] = y_in2_temp[10]*14000.0  # Snh = S_IN including adjustments above

    y_out2[13] = 0.75*(y_out2[2] + y_out2[3] + y_out2[4] + y_out2[5] + y_out2[6])
    y_out2[14] = y_in2_temp[26]  # flow rate
    y_out2[15] = y_in2[34]  # temperature, degC, should be equal to AS temperature into the AD/AS interface
    y_out2[16] = y_in2_temp[28]  # dummy state
    y_out2[17] = y_in2_temp[29]  # dummy state
    y_out2[18] = y_in2_temp[30]  # dummy state
    y_out2[19] = y_in2_temp[31]  # dummy state
    y_out2[20] = y_in2_temp[32]  # dummy state

    # charge balance, output S_alk (molHCO3/m3)
    y_out2[12] = (y_in2[3]*alfa_va + y_in2[4]*alfa_bu + y_in2[5]*alfa_pro + y_in2[6]*alfa_ac + y_in2[9]*alfa_co2 + y_in2[10]*alfa_IN - y_out2[8]*alfa_NO - y_out2[9]*alfa_NH)/alfa_alk

    # Finally there should be a input-output mass balance check here of COD and N