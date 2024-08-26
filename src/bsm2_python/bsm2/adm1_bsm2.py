import math

import numpy as np
from numba import jit
from scipy.integrate import odeint

from bsm2_python.bsm2.module import Module

# import warnings


indices_components = np.arange(42)
(
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
) = indices_components


class ADM1Reactor(Module):
    """
    Class for ADM1 reactor
    parameters:
    yd0: np.ndarray
        initial values for ADM1 differential equations. initial concentrations of 42 components
        (26 ADM1 components, 9 other gas-related components, Q, T and 5 dummy states)
    digesterpar: np.ndarray
        digester parameters
    interfacepar: np.ndarray
        interface parameters
    dim: np.ndarray
        reactor dimensions
    """

    def __init__(self, yd0, digesterpar, interfacepar, dim):
        self.yd0 = yd0
        self.y_in1 = np.zeros(22)
        self.digesterpar = digesterpar
        self.interfacepar = interfacepar
        self.dim = dim
        self.volume_liq, self.volume_gas = self.dim
        self.t_op = 0.0
        self.temperature = 0.0
        self.yd_out = np.zeros(51)

    def output(self, timestep, step, y_in1, t_op):
        """
        Returns the solved differential equations based on ADM1 model

        Parameters
        ----------
        timestep : float
            Time distance to integrate over
        step : float
            Current time
        y_in1 : np.ndarray(21)
            concentrations of the 21 standard components (13 ASM1 components, TSS, Q, T and 5 dummy states)
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
             SD1, SD2, SD3, XD4, XD5]
        t_op : float
            Operational temperature of digester.
            At the moment very rudimentary implementation! No heat losses / transfer embedded!
        Returns
        -------
        yi_out2 : np.ndarray(35)
            concentrations of the 33 components after ADM2ASM interface
            (21 ASM1 components, 9 other gas-related components, Q, T and 2 dummy states)
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
             SD1, SD2, SD3, XD4, XD5, pH, T_WW]
        yd_out : np.ndarray(51)
            concentrations of the 51 components after the ADM1 reactor
            (35 ADM1 components, 9 other gas-related components, Q, T and 5 dummy states)
            [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
             X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
             Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D, pH, S_H_ion, S_hva, S_hbu,
             S_hpro, S_hac, S_hco3, S_CO2, S_nh3, S_NH4+, S_gas_h2, S_gas_ch4, S_gas_co2,
             p_gas_h2, p_gas_ch4, p_gas_co2, P_gas, q_gas]
        yi_out1 : np.ndarray(33)
            concentrations of the 35 components after ASM2ADM interface.
            (26 ADM1 components, 9 other gas-related components)
            [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
             X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
             Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D]
        """
        self.t_op = t_op
        yd_out = np.zeros(51)

        r = self.digesterpar[77]
        t_base = self.digesterpar[78]
        pk_w_base = self.digesterpar[80]
        p_atm = self.digesterpar[93]
        k_h_h2o_base = self.digesterpar[95]
        k_p = self.digesterpar[99]

        t_eval = np.array([step, step + timestep])  # time interval for odeint

        self.y_in1[:21] = y_in1[:21]

        yi_out1 = asm2adm(self.y_in1, t_op, self.interfacepar)
        # y_out1
        #  0     1     2     3     4     5      6     7     8      9     10    11   12
        # [S_SU, S_AA, S_FA, S_VA, S_BU, S_PRO, S_AC, S_H2, S_CH4, S_IC, S_IN, S_I, X_XC,
        #  13    14    15    16    17    18    19    20     21    22    23   24     25
        #  X_CH, X_PR, X_LI, X_SU, X_AA, X_FA, X_C4, X_PRO, X_AC, X_H2, X_I, S_CAT, S_AN,
        #  26   27   28      29      30      31      32
        #  Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D]
        yd_in = np.zeros(42)
        y_in2 = np.zeros(35)

        # yd_in
        # 0     1     2     3     4     5      6     7     8      9     10    11   12
        # S_SU, S_AA, S_FA, S_VA, S_BU, S_PRO, S_AC, S_H2, S_CH4, S_IC, S_IN, S_I, X_XC,
        # 13    14    15    16    17    18    19     20    21    22   23     24    25
        # X_CH, X_PR, X_LI, X_SU, X_AA, X_FA, X_C4, X_PRO, X_AC, X_H2, X_I, S_CAT, S_AN,
        # 26     27     28      29     30      31     32        33         34         35
        # S_HVA, S_HBU, S_HPRO, S_HAC, S_HCO3, S_NH3, S_GAS_H2, S_GAS_CH4, S_GAS_CO2, Q_D,
        # 36   37      38      39      40      41
        # T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D

        yd_in[:26] = yi_out1[:26]
        yd_in[35:] = yi_out1[26:]
        # [S_SU, S_AA, S_FA, S_VA, S_BU, S_PRO, S_AC, S_H2, S_CH4, S_IC, S_IN, S_I, X_XC, X_CH, X_PR,
        #  X_LI, X_SU, X_AA, X_FA, X_C4, X_PRO, X_AC, X_H2, X_I, S_CAT, S_AN, S_HVA, S_HBU, S_HPRO, S_HAC,
        #  S_HCO3, S_NH3, S_GAS_H2, S_GAS_CH4, S_GAS_CO2, Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D]
        ode = odeint(
            adm1equations,
            self.yd0,
            t_eval,
            tfirst=True,
            args=(yd_in, self.digesterpar, t_op, self.dim),
            rtol=1e-6,
            atol=1e-6,
        )
        yd_int = ode[1]
        # [S_SU, S_AA, S_FA, S_VA, S_BU, S_PRO, S_AC, S_H2, S_CH4, S_IC, S_IN, S_I, X_XC, X_CH, X_PR,
        #  X_LI, X_SU, X_AA, X_FA, X_C4, X_PRO, X_AC, X_H2, X_I, S_CAT, S_AN, S_HVA, S_HBU, S_HPRO, S_HAC,
        #  S_HCO3, S_NH3, S_GAS_H2, S_GAS_CH4, S_GAS_CO2, Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D]
        self.yd0[:] = yd_int[:]  # initial integration values for next integration

        # y = yd_out
        # u = yd_in
        # x : yd_int

        factor = (1.0 / t_base - 1.0 / t_op) / (100.0 * r)
        # k_h_h2 = k_h_h2_base*math.exp(-4180.0*factor)      # T adjustment for K_H_h2
        # k_h_ch4 = k_h_ch4_base*math.exp(-14240.0*factor)   # T adjustment for K_H_ch4
        # k_h_co2 = k_h_co2_base*math.exp(-19410.0*factor)   # T adjustment for K_H_co2
        k_w = 10 ** (-pk_w_base) * math.exp(55900.0 * factor)  # T adjustment for K_w
        p_gas_h2o = k_h_h2o_base * math.exp(
            5290.0 * (1.0 / t_base - 1.0 / t_op)
        )  # T adjustment for water vapour saturation pressure

        yd_out[:S_HVA] = yd_int[:S_HVA]

        yd_out[26] = yd_in[Q_D]  # flow

        yd_out[27] = t_op - 273.15  # Temp = 35 degC

        yd_out[28] = yd_in[S_D1_D]  # Dummy state 1, soluble
        yd_out[29] = yd_in[S_D2_D]  # Dummy state 2, soluble
        yd_out[30] = yd_in[S_D3_D]  # Dummy state 3, soluble
        yd_out[31] = yd_in[X_D4_D]  # Dummy state 1, particulate
        yd_out[32] = yd_in[X_D5_D]  # Dummy state 2, particulate

        p_gas_h2 = yd_int[S_GAS_H2] * r * t_op / 16.0
        p_gas_ch4 = yd_int[S_GAS_CH4] * r * t_op / 64.0
        p_gas_co2 = yd_int[S_GAS_CO2] * r * t_op
        p_gas = p_gas_h2 + p_gas_ch4 + p_gas_co2 + p_gas_h2o
        q_gas = max(k_p * (p_gas - p_atm), 0)

        # procT8 = kLa*(yd_int[S_h2] - 16.0*K_H_h2*p_gas_h2)
        # procT9 = kLa*(yd_int[S_ch4] - 64.0*K_H_ch4*p_gas_ch4)
        # procT10 = kLa*((yd_int[S_IC] - yd_int[S_hco3]) - K_H_co2*p_gas_co2)

        phi = (
            yd_int[S_CAT]
            + (yd_int[S_IN] - yd_int[S_NH3])
            - yd_int[S_HCO3]
            - yd_int[S_HAC] / 64.0
            - yd_int[S_HPRO] / 112.0
            - yd_int[S_HBU] / 160.0
            - yd_int[S_HVA] / 208.0
            - yd_int[S_AN]
        )
        s_h_ion = -phi * 0.5 + 0.5 * np.sqrt(phi**2 + 4.0 * k_w)

        yd_out[33] = -np.log10(s_h_ion)  # pH
        self.y_in1[21] = yd_out[33]  # pH for ASM2ADM interface
        yd_out[34] = s_h_ion
        yd_out[35] = yd_int[S_HVA]
        yd_out[36] = yd_int[S_HBU]
        yd_out[37] = yd_int[S_HPRO]
        yd_out[38] = yd_int[S_HAC]
        yd_out[39] = yd_int[S_HCO3]
        yd_out[40] = yd_int[S_IC] - yd_int[S_HCO3]  # S_CO2
        yd_out[41] = yd_int[S_NH3]
        yd_out[42] = yd_int[S_IN] - yd_int[S_NH3]  # S_NH4+
        yd_out[43] = yd_int[S_GAS_H2]
        yd_out[44] = yd_int[S_GAS_CH4]
        yd_out[45] = yd_int[S_GAS_CO2]
        yd_out[46] = p_gas_h2
        yd_out[47] = p_gas_ch4
        yd_out[48] = p_gas_co2
        yd_out[49] = p_gas  # total head space pressure from H2, CH4, CO2 and H2O
        yd_out[50] = (
            q_gas * p_gas / p_atm
        )  # The output gas flow is recalculated to atmospheric pressure (normalization)

        # [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
        # X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
        # Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D, pH, S_H_ion, S_hva, S_hbu,
        # S_hpro, S_hac, S_hco3, S_CO2, S_nh3, S_NH4+, S_gas_h2, S_gas_ch4, S_gas_co2,
        # p_gas_h2, p_gas_ch4, p_gas_co2, P_gas, q_gas]
        y_in2[:33] = yd_out[:33]
        # [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
        # X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
        # Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D, pH, T_WW]
        y_in2[33] = yd_out[33]  # pH
        y_in2[34] = self.y_in1[15]
        self.temperature = yd_out[27]  # Temperature
        yi_out2 = adm2asm(y_in2, t_op, self.interfacepar)
        if step % 10 == 0:
            pass
        self.yd_out = yd_out

        return yi_out2, yd_out, yi_out1


@jit(nopython=True, cache=True)
def adm1equations(t, yd, yd_in, digesterpar, t_op, dim):
    """Returns an array containing the differential equations based on ASM1

    Parameters
    ----------
    t : np.ndarray
        Time interval for integration, needed for the solver
    yd : np.ndarray
        Solution of the differential equations, needed for the solver
    yd_in : np.ndarray
        Reactor inlet concentrations of 42 components
        (26 ADM1 components, 9 other gas-related components, Q, T and 5 dummy states)
        [S_SU, S_AA, S_FA, S_VA, S_BU, S_PRO, S_AC, S_H2, S_CH4, S_IC, S_IN, S_I, X_XC, X_CH, X_PR,
         X_LI, X_SU, X_AA, X_FA, X_C4, X_PRO, X_AC, X_H2, X_I, S_CAT, S_AN, S_HVA, S_HBU, S_HPRO, S_HAC,
         S_HCO3, S_NH3, S_GAS_H2, S_GAS_CH4, S_GAS_CO2, Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D]
    digesterpar : np.ndarray
        Digester parameters
    t_op : float
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
    dyd = np.zeros_like(yd)
    ydtemp = np.zeros_like(yd)
    inhib = np.zeros(6)

    (
        f_si_xc,
        f_xi_xc,
        f_ch_xc,
        f_pr_xc,
        f_li_xc,
        n_xc,
        n_i,
        n_aa_c,
        c_xc,
        c_si,
        c_ch,
        c_pr,
        c_li,
        c_xi,
        c_su,
        c_aa,
        f_fa_li,
        c_fa,
        f_h2_su,
        f_bu_su,
        f_pro_su,
        f_ac_su,
        n_bac,
        c_bu,
        c_pro,
        c_ac,
        c_bac,
        y_su,
        f_h2_aa,
        f_va_aa,
        f_bu_aa,
        f_pro_aa,
        f_ac_aa,
        c_va,
        y_aa,
        y_fa,
        y_c4,
        y_pro,
        c_ch4,
        y_ac,
        y_h2,
        k_dis,
        k_hyd_ch,
        k_hyd_pr,
        k_hyd_li,
        k_s_in,
        k_m_su,
        k_s_su,
        ph_ul_aa,
        ph_ll_aa,
        k_m_aa,
        k_s_aa,
        k_m_fa,
        k_s_fa,
        k_ih2_fa,
        k_m_c4,
        k_s_c4,
        k_ih2_c4,
        k_m_pro,
        k_s_pro,
        k_ih2_pro,
        k_m_ac,
        k_s_ac,
        k_i_nh3,
        ph_ul_ac,
        ph_ll_ac,
        k_m_h2,
        k_s_h2,
        ph_ul_h2,
        ph_ll_h2,
        k_dec_xsu,
        k_dec_xaa,
        k_dec_xfa,
        k_dec_xc4,
        k_dec_xpro,
        k_dec_xac,
        k_dec_xh2,
        r,
        t_base,
        _,
        pk_w_base,
        pk_a_va_base,
        pk_a_bu_base,
        pk_a_pro_base,
        pk_a_ac_base,
        pk_a_co2_base,
        pk_a_in_base,
        k_a_bva,
        k_a_bbu,
        k_a_bpro,
        k_a_bac,
        k_a_bco2,
        k_a_bin,
        p_atm,
        kla,
        k_h_h2o_base,
        k_h_co2_base,
        k_h_ch4_base,
        k_h_h2_base,
        k_p,
    ) = digesterpar

    v_liq, v_gas = dim

    ydtemp[:] = yd[:]
    ydtemp[ydtemp < 0.0] = 0.0

    eps = 1.0e-6

    factor = (1.0 / t_base - 1.0 / t_op) / (100.0 * r)
    k_w = 10**-pk_w_base * math.exp(55900.0 * factor)  # T adjustment for K_w
    k_a_va = 10**-pk_a_va_base
    k_a_bu = 10**-pk_a_bu_base
    k_a_pro = 10**-pk_a_pro_base
    k_a_ac = 10**-pk_a_ac_base
    k_a_co2 = 10**-pk_a_co2_base * math.exp(7646.0 * factor)  # T adjustment for K_a_co2
    k_a_in = 10**-pk_a_in_base * math.exp(51965.0 * factor)  # T adjustment for K_a_IN

    k_h_h2 = k_h_h2_base * math.exp(-4180.0 * factor)  # T adjustment for K_H_h2
    k_h_ch4 = k_h_ch4_base * math.exp(-14240.0 * factor)  # T adjustment for K_H_ch4
    k_h_co2 = k_h_co2_base * math.exp(-19410.0 * factor)  # T adjustment for K_H_co2
    p_gas_h2o = k_h_h2o_base * math.exp(
        5290.0 * (1.0 / t_base - 1.0 / t_op)
    )  # T adjustment for water vapour saturation pressure

    phi = (
        ydtemp[S_CAT]
        + (ydtemp[S_IN] - ydtemp[S_NH3])
        - ydtemp[S_HCO3]
        - ydtemp[S_HAC] / 64.0
        - ydtemp[S_HPRO] / 112.0
        - ydtemp[S_HBU] / 160.0
        - ydtemp[S_HVA] / 208.0
        - ydtemp[S_AN]
    )
    s_h_ion = -phi * 0.5 + 0.5 * np.sqrt(phi * phi + 4.0 * k_w)  # SH+
    # pH_op = -np.log10(S_H_ion)  # pH

    p_gas_h2 = ydtemp[S_GAS_H2] * r * t_op / 16.0
    p_gas_ch4 = ydtemp[S_GAS_CH4] * r * t_op / 64.0
    p_gas_co2 = ydtemp[S_GAS_CO2] * r * t_op
    p_gas = p_gas_h2 + p_gas_ch4 + p_gas_co2 + p_gas_h2o

    q_gas = max(k_p * (p_gas - p_atm), 0)

    # Hill function on SH+ used within BSM2, ADM1 Workshop, Copenhagen 2005.
    phlim_aa = 10 ** (-(ph_ul_aa + ph_ll_aa) / 2.0)
    phlim_ac = 10 ** (-(ph_ul_ac + ph_ll_ac) / 2.0)
    phlim_h2 = 10 ** (-(ph_ul_h2 + ph_ll_h2) / 2.0)
    n_aa = 3.0 / (ph_ul_aa - ph_ll_aa)
    n_ac = 3.0 / (ph_ul_ac - ph_ll_ac)
    n_h2 = 3.0 / (ph_ul_h2 - ph_ll_h2)
    i_ph_aa = phlim_aa**n_aa / (s_h_ion**n_aa + phlim_aa**n_aa)
    i_ph_ac = phlim_ac**n_ac / (s_h_ion**n_ac + phlim_ac**n_ac)
    i_ph_h2 = phlim_h2**n_h2 / (s_h_ion**n_h2 + phlim_h2**n_h2)

    i_in_lim = 1.0 / (1.0 + k_s_in / ydtemp[S_IN])
    i_h2_fa = 1.0 / (1.0 + ydtemp[S_H2] / k_ih2_fa)
    i_h2_c4 = 1.0 / (1.0 + ydtemp[S_H2] / k_ih2_c4)
    i_h2_pro = 1.0 / (1.0 + ydtemp[S_H2] / k_ih2_pro)
    i_nh3 = 1.0 / (1.0 + ydtemp[S_NH3] / k_i_nh3)

    inhib[0] = i_ph_aa * i_in_lim
    inhib[1] = inhib[0] * i_h2_fa
    inhib[2] = inhib[0] * i_h2_c4
    inhib[3] = inhib[0] * i_h2_pro
    inhib[4] = i_ph_ac * i_in_lim * i_nh3
    inhib[5] = i_ph_h2 * i_in_lim

    proc1 = k_dis * ydtemp[X_XC]
    proc2 = k_hyd_ch * ydtemp[X_CH]
    proc3 = k_hyd_pr * ydtemp[X_PR]
    proc4 = k_hyd_li * ydtemp[X_LI]
    proc5 = k_m_su * ydtemp[S_SU] / (k_s_su + ydtemp[S_SU]) * ydtemp[X_SU] * inhib[0]
    proc6 = k_m_aa * ydtemp[S_AA] / (k_s_aa + ydtemp[S_AA]) * ydtemp[X_AA] * inhib[0]
    proc7 = k_m_fa * ydtemp[S_FA] / (k_s_fa + ydtemp[S_FA]) * ydtemp[X_FA] * inhib[1]
    proc8 = (
        k_m_c4
        * ydtemp[S_VA]
        / (k_s_c4 + ydtemp[S_VA])
        * ydtemp[X_C4]
        * ydtemp[S_VA]
        / (ydtemp[S_VA] + ydtemp[S_BU] + eps)
        * inhib[2]
    )
    proc9 = (
        k_m_c4
        * ydtemp[S_BU]
        / (k_s_c4 + ydtemp[S_BU])
        * ydtemp[X_C4]
        * ydtemp[S_BU]
        / (ydtemp[S_VA] + ydtemp[S_BU] + eps)
        * inhib[2]
    )
    proc10 = k_m_pro * ydtemp[S_PRO] / (k_s_pro + ydtemp[S_PRO]) * ydtemp[X_PRO] * inhib[3]
    proc11 = k_m_ac * ydtemp[S_AC] / (k_s_ac + ydtemp[S_AC]) * ydtemp[X_AC] * inhib[4]
    proc12 = k_m_h2 * ydtemp[S_H2] / (k_s_h2 + ydtemp[S_H2]) * ydtemp[X_H2] * inhib[5]
    proc13 = k_dec_xsu * ydtemp[X_SU]
    proc14 = k_dec_xaa * ydtemp[X_AA]
    proc15 = k_dec_xfa * ydtemp[X_FA]
    proc16 = k_dec_xc4 * ydtemp[X_C4]
    proc17 = k_dec_xpro * ydtemp[X_PRO]
    proc18 = k_dec_xac * ydtemp[X_AC]
    proc19 = k_dec_xh2 * ydtemp[X_H2]

    proca4 = k_a_bva * (ydtemp[S_HVA] * (k_a_va + s_h_ion) - k_a_va * ydtemp[S_VA])
    proca5 = k_a_bbu * (ydtemp[S_HBU] * (k_a_bu + s_h_ion) - k_a_bu * ydtemp[S_BU])
    proca6 = k_a_bpro * (ydtemp[S_HPRO] * (k_a_pro + s_h_ion) - k_a_pro * ydtemp[S_PRO])
    proca7 = k_a_bac * (ydtemp[S_HAC] * (k_a_ac + s_h_ion) - k_a_ac * ydtemp[S_AC])
    proca10 = k_a_bco2 * (ydtemp[S_HCO3] * (k_a_co2 + s_h_ion) - k_a_co2 * ydtemp[S_IC])
    proca11 = k_a_bin * (ydtemp[S_NH3] * (k_a_in + s_h_ion) - k_a_in * ydtemp[S_IN])

    proct8 = kla * (ydtemp[S_H2] - 16.0 * k_h_h2 * p_gas_h2)
    proct9 = kla * (ydtemp[S_CH4] - 64.0 * k_h_ch4 * p_gas_ch4)
    proct10 = kla * ((ydtemp[S_IC] - ydtemp[S_HCO3]) - k_h_co2 * p_gas_co2)

    stoich1 = -c_xc + f_si_xc * c_si + f_ch_xc * c_ch + f_pr_xc * c_pr + f_li_xc * c_li + f_xi_xc * c_xi
    stoich2 = -c_ch + c_su
    stoich3 = -c_pr + c_aa
    stoich4 = -c_li + (1.0 - f_fa_li) * c_su + f_fa_li * c_fa
    stoich5 = -c_su + (1.0 - y_su) * (f_bu_su * c_bu + f_pro_su * c_pro + f_ac_su * c_ac) + y_su * c_bac
    stoich6 = (
        -c_aa + (1.0 - y_aa) * (f_va_aa * c_va + f_bu_aa * c_bu + f_pro_aa * c_pro + f_ac_aa * c_ac) + y_aa * c_bac
    )
    stoich7 = -c_fa + (1.0 - y_fa) * 0.7 * c_ac + y_fa * c_bac
    stoich8 = -c_va + (1.0 - y_c4) * 0.54 * c_pro + (1.0 - y_c4) * 0.31 * c_ac + y_c4 * c_bac
    stoich9 = -c_bu + (1.0 - y_c4) * 0.8 * c_ac + y_c4 * c_bac
    stoich10 = -c_pro + (1.0 - y_pro) * 0.57 * c_ac + y_pro * c_bac
    stoich11 = -c_ac + (1.0 - y_ac) * c_ch4 + y_ac * c_bac
    stoich12 = (1.0 - y_h2) * c_ch4 + y_h2 * c_bac
    stoich13 = -c_bac + c_xc

    reac1 = proc2 + (1.0 - f_fa_li) * proc4 - proc5
    reac2 = proc3 - proc6
    reac3 = f_fa_li * proc4 - proc7
    reac4 = (1.0 - y_aa) * f_va_aa * proc6 - proc8
    reac5 = (1.0 - y_su) * f_bu_su * proc5 + (1.0 - y_aa) * f_bu_aa * proc6 - proc9
    reac6 = (1.0 - y_su) * f_pro_su * proc5 + (1.0 - y_aa) * f_pro_aa * proc6 + (1.0 - y_c4) * 0.54 * proc8 - proc10
    reac7 = (
        (1.0 - y_su) * f_ac_su * proc5
        + (1.0 - y_aa) * f_ac_aa * proc6
        + (1.0 - y_fa) * 0.7 * proc7
        + (1.0 - y_c4) * 0.31 * proc8
        + (1.0 - y_c4) * 0.8 * proc9
        + (1.0 - y_pro) * 0.57 * proc10
        - proc11
    )
    reac8 = (
        (1.0 - y_su) * f_h2_su * proc5
        + (1.0 - y_aa) * f_h2_aa * proc6
        + (1.0 - y_fa) * 0.3 * proc7
        + (1.0 - y_c4) * 0.15 * proc8
        + (1.0 - y_c4) * 0.2 * proc9
        + (1.0 - y_pro) * 0.43 * proc10
        - proc12
        - proct8
    )
    reac9 = (1.0 - y_ac) * proc11 + (1.0 - y_h2) * proc12 - proct9
    reac10 = (
        -stoich1 * proc1
        - stoich2 * proc2
        - stoich3 * proc3
        - stoich4 * proc4
        - stoich5 * proc5
        - stoich6 * proc6
        - stoich7 * proc7
        - stoich8 * proc8
        - stoich9 * proc9
        - stoich10 * proc10
        - stoich11 * proc11
        - stoich12 * proc12
        - stoich13 * proc13
        - stoich13 * proc14
        - stoich13 * proc15
        - stoich13 * proc16
        - stoich13 * proc17
        - stoich13 * proc18
        - stoich13 * proc19
        - proct10
    )
    reac11 = (
        (n_xc - f_xi_xc * n_i - f_si_xc * n_i - f_pr_xc * n_aa_c) * proc1
        - y_su * n_bac * proc5
        + (n_aa_c - y_aa * n_bac) * proc6
        - y_fa * n_bac * proc7
        - y_c4 * n_bac * proc8
        - y_c4 * n_bac * proc9
        - y_pro * n_bac * proc10
        - y_ac * n_bac * proc11
        - y_h2 * n_bac * proc12
        + (n_bac - n_xc) * (proc13 + proc14 + proc15 + proc16 + proc17 + proc18 + proc19)
    )
    reac12 = f_si_xc * proc1
    reac13 = -proc1 + proc13 + proc14 + proc15 + proc16 + proc17 + proc18 + proc19
    reac14 = f_ch_xc * proc1 - proc2
    reac15 = f_pr_xc * proc1 - proc3
    reac16 = f_li_xc * proc1 - proc4
    reac17 = y_su * proc5 - proc13
    reac18 = y_aa * proc6 - proc14
    reac19 = y_fa * proc7 - proc15
    reac20 = y_c4 * proc8 + y_c4 * proc9 - proc16
    reac21 = y_pro * proc10 - proc17
    reac22 = y_ac * proc11 - proc18
    reac23 = y_h2 * proc12 - proc19
    reac24 = f_xi_xc * proc1

    dyd[S_SU] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_SU] - yd[S_SU])) + reac1
    dyd[S_AA] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_AA] - yd[S_AA])) + reac2
    dyd[S_FA] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_FA] - yd[S_FA])) + reac3
    dyd[S_VA] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_VA] - yd[S_VA])) + reac4
    dyd[S_BU] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_BU] - yd[S_BU])) + reac5
    dyd[S_PRO] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_PRO] - yd[S_PRO])) + reac6
    dyd[S_AC] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_AC] - yd[S_AC])) + reac7
    dyd[S_H2] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_H2] - yd[S_H2])) + reac8
    dyd[S_CH4] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_CH4] - yd[S_CH4])) + reac9
    dyd[S_IC] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_IC] - yd[S_IC])) + reac10
    dyd[S_IN] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_IN] - yd[S_IN])) + reac11
    dyd[S_I] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_I] - yd[S_I])) + reac12
    dyd[X_XC] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_XC] - yd[X_XC])) + reac13
    dyd[X_CH] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_CH] - yd[X_CH])) + reac14
    dyd[X_PR] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_PR] - yd[X_PR])) + reac15
    dyd[X_LI] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_LI] - yd[X_LI])) + reac16
    dyd[X_SU] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_SU] - yd[X_SU])) + reac17
    dyd[X_AA] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_AA] - yd[X_AA])) + reac18
    dyd[X_FA] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_FA] - yd[X_FA])) + reac19
    dyd[X_C4] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_C4] - yd[X_C4])) + reac20
    dyd[X_PRO] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_PRO] - yd[X_PRO])) + reac21
    dyd[X_AC] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_AC] - yd[X_AC])) + reac22
    dyd[X_H2] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_H2] - yd[X_H2])) + reac23
    dyd[X_I] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[X_I] - yd[X_I])) + reac24

    dyd[S_CAT] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_CAT] - yd[S_CAT]))
    dyd[S_AN] = 1.0 / v_liq * (yd_in[Q_D] * (yd_in[S_AN] - yd[S_AN]))
    dyd[S_HVA] = -proca4
    dyd[S_HBU] = -proca5
    dyd[S_HPRO] = -proca6
    dyd[S_HAC] = -proca7
    dyd[S_HCO3] = -proca10
    dyd[S_NH3] = -proca11

    dyd[S_GAS_H2] = -ydtemp[S_GAS_H2] * q_gas / v_gas + proct8 * v_liq / v_gas
    dyd[S_GAS_CH4] = -ydtemp[S_GAS_CH4] * q_gas / v_gas + proct9 * v_liq / v_gas
    dyd[S_GAS_CO2] = -ydtemp[S_GAS_CO2] * q_gas / v_gas + proct10 * v_liq / v_gas

    dyd[Q_D] = 0
    dyd[T_D] = 0

    # Dummy states for future use
    dyd[S_D1_D] = 0
    dyd[S_D2_D] = 0
    dyd[S_D3_D] = 0
    dyd[X_D4_D] = 0
    dyd[X_D5_D] = 0
    if np.isnan(dyd).any():
        err = 'ADM1 equations: NaN value in dyd'
        raise ValueError(err)
    return dyd


@jit(nopython=True, cache=True)
def asm2adm(y_in1, t_op, interfacepar):
    """
    Converts ASM1 flows to ADM1 flows
    New version (no 3) of the ASM1 to ADM1 interface based on discussions
    within the IWA TG BSM community during 2002-2006. Now also including
    charge balancing and temperature dependency for applicable parameters.
    Model parameters are defined in adm1init_bsm2.m

    Parameters
    ----------
    y_in1 : np.ndarray(22)
        concentrations of the 21 standard components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        plus pH in the anaerobic digester
        [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
         SD1, SD2, SD3, XD4, XD5, pH_adm]
    t_op : float
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
        [S_SU, S_AA, S_FA, S_VA, S_BU, S_PRO, S_AC, S_H2, S_CH4, S_IC, S_IN, S_I, X_XC,
         X_CH, X_PR, X_LI, X_SU, X_AA, X_FA, X_C4, X_PRO, X_AC, X_H2, X_I, S_CAT, S_AN,
         Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D]

    """
    (
        codequiv,
        fnaa,
        fnxc,
        fnbac,
        fxni,
        fsni,
        fsni_adm,
        frlixs,
        frlibac,
        frxs_adm,
        fdegrade_adm,
        _,
        _,
        r,
        t_base,
        _,
        pk_w_base,
        pk_a_va_base,
        pk_a_bu_base,
        pk_a_pro_base,
        pk_a_ac_base,
        pk_a_co2_base,
        pk_a_in_base,
    ) = interfacepar

    # y = y_out1
    # u = y_in1
    y_out1 = np.zeros(33)
    y_in1_temp = np.zeros(22)
    y_in1_temp2 = np.zeros(22)

    y_in1_temp[:] = y_in1[:]
    y_in1_temp2[:] = y_in1[:]

    ph_adm = y_in1[21]

    factor = (1.0 / t_base - 1.0 / t_op) / (100.0 * r)
    pk_w = pk_w_base - np.log10(math.exp(55900.0 * factor))
    pk_a_co2 = pk_a_co2_base - np.log10(math.exp(7646.0 * factor))
    pk_a_in = pk_a_in_base - np.log10(math.exp(51965.0 * factor))
    alfa_va = 1.0 / 208.0 * (-1.0 / (1.0 + np.power(10, pk_a_va_base - ph_adm)))
    alfa_bu = 1.0 / 160.0 * (-1.0 / (1.0 + np.power(10, pk_a_bu_base - ph_adm)))
    alfa_pro = 1.0 / 112.0 * (-1.0 / (1.0 + np.power(10, pk_a_pro_base - ph_adm)))
    alfa_ac = 1.0 / 64.0 * (-1.0 / (1.0 + np.power(10, pk_a_ac_base - ph_adm)))
    alfa_co2 = -1.0 / (1.0 + np.power(10, pk_a_co2 - ph_adm))
    alfa_in = (np.power(10, pk_a_in - ph_adm)) / (1.0 + np.power(10, pk_a_in - ph_adm))
    alfa_nh = 1.0 / 14000.0  # convert mgN/l into kmoleN/m3
    alfa_alk = -0.001  # convert moleHCO3/m3 into kmoleHCO3/m3
    alfa_no = -1.0 / 14000.0  # convert mgN/l into kmoleN/m3

    # Let CODdemand be the COD demand of available electron
    # acceptors prior to the anaerobic digester, i.e. oxygen and nitrate
    coddemand = y_in1[7] + codequiv * y_in1[8]

    # if extreme detail was used then some extra NH4 would be transformed
    # into N bound in biomass and some biomass would be formed when
    # removing the CODdemand (based on the yield). But on a total COD balance
    # approach the below is correct (neglecting the N need for biomass growth)
    # The COD is reduced in a hierarchical approach in the order:
    # 1) SS; 2) XS; 3) XBH; 4) XBA. It is no real improvement to remove SS and add
    # biomass. The net result is the same.

    if coddemand > y_in1[1]:  # check if COD demand can be fulfilled by SS
        remaina = coddemand - y_in1[1]
        y_in1_temp[1] = 0.0
        if remaina > y_in1[3]:  # check if COD demand can be fulfilled by XS
            remainb = remaina - y_in1[3]
            y_in1_temp[3] = 0.0
            if remainb > y_in1[4]:  # check if COD demand can be fulfilled by XBH
                remainc = remainb - y_in1[4]
                y_in1_temp[9] += y_in1[4] * fnbac
                y_in1_temp[4] = 0.0
                if remainc > y_in1[5]:  # check if COD demand can be fulfilled by XBA
                    remaind = remainc - y_in1[5]
                    y_in1_temp[9] += y_in1[5] * fnbac
                    y_in1_temp[5] = 0.0
                    y_in1_temp[7] = remaind
                    # if here we are in trouble, carbon shortage: an error printout should be given
                    # and execution stopped
                else:  # reduced all COD demand by use of SS, XS, XBH and XBA
                    y_in1_temp[5] = y_in1[5] - remainc
                    y_in1_temp[9] += remainc * fnbac
            else:  # reduced all COD demand by use of SS, XS and XBH
                y_in1_temp[4] = y_in1[4] - remainb
                y_in1_temp[9] += remainb * fnbac
        else:  # reduced all COD demand by use of SS and XS
            y_in1_temp[3] = y_in1[3] - remaina
    else:  # reduced all COD demand by use of SS
        y_in1_temp[1] = y_in1[1] - coddemand

    # SS becomes part of amino acids when transformed into ADM
    # and any remaining SS is mapped to monosacharides (no N contents)
    # Enough SND must be available for mapping to amino acids

    sorgn = y_in1[10] / fnaa  # Saa COD equivalent to SND

    if sorgn >= y_in1_temp[1]:  # not all SND-N in terms of COD fits into amino acids
        y_out1[1] = y_in1_temp[1]  # map all SS COD into Saa
        y_in1_temp[10] -= y_in1_temp[1] * fnaa  # excess SND
        y_in1_temp[1] = 0.0  # all SS used
    else:  # all SND-N fits into amino acids
        y_out1[1] = sorgn  # map all SND related COD into Saa
        y_in1_temp[1] -= sorgn  # excess SS, which will become sugar in ADM1 i.e. no nitrogen association
        y_in1_temp[10] = 0.0  # all SND used

    # XS becomes part of Xpr (proteins) when transformed into ADM
    # and any remaining XS is mapped to Xch and Xli (no N contents)
    # Enough XND must be available for mapping to Xpr

    xorgn = y_in1[11] / fnaa  # Xpr COD equivalent to XND

    if xorgn >= y_in1_temp[3]:  # not all XND-N in terms of COD fits into Xpr
        xprtemp = y_in1_temp[3]  # map all XS COD into Spr
        y_in1_temp[11] -= y_in1_temp[3] * fnaa  # excess XND
        y_in1_temp[3] = 0.0  # all XS used
        xlitemp = 0.0
        xchtemp = 0.0
    else:  # all XND-N fits into Xpr
        xprtemp = xorgn  # map all XND related COD into Xpr
        xlitemp = frlixs * (y_in1_temp[3] - xorgn)  # part of XS COD not associated with N
        xchtemp = (1.0 - frlixs) * (y_in1_temp[3] - xorgn)  # part of XS COD not associated with N
        y_in1_temp[3] = 0.0  # all XS used
        y_in1_temp[11] = 0.0  # all XND used

    # Biomass becomes part of Xpr and XI when transformed into ADM
    # and any remaining XBH and XBA is mapped to Xch and Xli (no N contents)
    # Remaining XND-N can be used as nitrogen source to form Xpr

    biomass = y_in1_temp[4] + y_in1_temp[5]
    biomass_nobio = biomass * (1.0 - frxs_adm)  # part which is mapped to XI
    biomass_bion = biomass * fnbac - biomass_nobio * fxni
    if biomass_bion < 0.0:
        err = 'Not enough biomass N to map the requested inert part'
        raise ValueError(err)
    if (biomass_bion / fnaa) <= (biomass - biomass_nobio):
        xprtemp2 = biomass_bion / fnaa  # all biomass N used
        remaincod = biomass - biomass_nobio - xprtemp2
        if (y_in1_temp[11] / fnaa) > remaincod:  # use part of remaining XND-N to form proteins
            xprtemp2 += remaincod
            y_in1_temp[11] -= remaincod * fnaa
            remaincod = 0.0
            y_in1_temp[4] = 0.0
            y_in1_temp[5] = 0.0
        else:  # use all remaining XND-N to form proteins
            xprtemp2 += y_in1_temp[11] / fnaa
            remaincod -= y_in1_temp[11] / fnaa
            y_in1_temp[11] = 0.0
        xlitemp2 = frlibac * remaincod  # part of the COD not associated with N
        xchtemp2 = (1.0 - frlibac) * remaincod  # part of the COD not associated with N
    else:
        xprtemp2 = biomass - biomass_nobio  # all biomass COD used
        y_in1_temp[11] += biomass * fnbac - biomass_nobio * fxni - xprtemp2 * fnaa  # any remaining N in XND
        xlitemp2 = 0.0
        xchtemp2 = 0.0
    y_in1_temp[4] = 0.0
    y_in1_temp[5] = 0.0

    # direct mapping of XI and XP to ADM1 XI (if fdegrade_adm = 0)
    # assumption: same N content in both ASM1 and ADM1 particulate inerts

    inertx = (1 - fdegrade_adm) * (y_in1_temp[2] + y_in1_temp[6])

    # special case: IF part of XI and XP in the ASM can be degraded in the AD
    # we have no knowledge about the contents so we put it in as composites (Xc)
    # we need to keep track of the associated nitrogen
    # N content which may be different, take first from XI&XP-N, then XND-N, then SND-N,
    # then SNH. A similar principle could be used for other states.

    xc = 0.0
    xlitemp3 = 0.0
    xchtemp3 = 0.0
    if fdegrade_adm > 0:
        noninertx = fdegrade_adm * (y_in1_temp[2] + y_in1_temp[6])
        if fxni < fnxc:  # N in XI&XP(ASM) not enough
            xc = noninertx * fxni / fnxc
            noninertx -= noninertx * fxni / fnxc
            if y_in1_temp[11] < (noninertx * fnxc):  # N in XND not enough
                xc += y_in1_temp[11] / fnxc
                noninertx -= y_in1_temp[11] / fnxc
                y_in1_temp[11] = 0.0
                if y_in1_temp[10] < (noninertx * fnxc):  # N in SND not enough
                    xc += y_in1_temp[10] / fnxc
                    noninertx -= y_in1_temp[10] / fnxc
                    y_in1_temp[10] = 0.0
                    if y_in1_temp[9] < (noninertx * fnxc):  # N in SNH not enough
                        xc += y_in1_temp[9] / fnxc
                        noninertx -= y_in1_temp[9] / fnxc
                        y_in1_temp[9] = 0.0
                        # warnings.warn('Nitrogen shortage when converting biodegradable XI&XP')
                        # print('Nitrogen shortage when converting biodegradable XI&XP')
                        # Putting remaining XI&XP as lipids (50%) and carbohydrates (50%)
                        xlitemp3 = 0.5 * noninertx
                        xchtemp3 = 0.5 * noninertx
                        noninertx = 0.0
                    else:  # N in SNH enough for mapping
                        xc += noninertx
                        y_in1_temp[9] -= noninertx * fnxc
                        noninertx = 0.0
                else:  # N in SND enough for mapping
                    xc += noninertx
                    y_in1_temp[10] -= noninertx * fnxc
                    noninertx = 0.0
            else:  # N in XND enough for mapping
                xc += noninertx
                y_in1_temp[11] -= noninertx * fnxc
                noninertx = 0.0
        else:  # N in XI&XP(ASM) enough for mapping
            xc += noninertx
            y_in1_temp[11] += noninertx * (fxni - fnxc)  # put remaining N as XND
            noninertx = 0

    # Mapping of ASM SI to ADM1 SI
    # N content may be different, take first from SI-N, then SND-N, then XND-N,
    # then SNH. Similar principle could be used for other states.

    inerts = 0.0
    if fsni < fsni_adm:  # N in SI(ASM) not enough
        inerts = y_in1_temp[0] * fsni / fsni_adm
        y_in1_temp[0] -= y_in1_temp[0] * fsni / fsni_adm
        if y_in1_temp[10] < (y_in1_temp[0] * fsni_adm):  # N in SND not enough
            inerts += y_in1_temp[10] / fsni_adm
            y_in1_temp[0] -= y_in1_temp[10] / fsni_adm
            y_in1_temp[10] = 0.0
            if y_in1_temp[11] < (y_in1_temp[0] * fsni_adm):  # N in XND not enough
                inerts += y_in1_temp[11] / fsni_adm
                y_in1_temp[0] -= y_in1_temp[11] / fsni_adm
                y_in1_temp[11] = 0.0
                if y_in1_temp[9] < (y_in1_temp[0] * fsni_adm):  # N in SNH not enough
                    inerts += y_in1_temp[9] / fsni_adm
                    y_in1_temp[0] -= y_in1_temp[9] / fsni_adm
                    y_in1_temp[9] = 0.0
                    # warnings.warn('Nitrogen shortage when converting SI')
                    # print('Nitrogen shortage when converting SI')  # TODO: Uncomment this. for debugging only
                    # Putting remaining SI as monosacharides
                    y_in1_temp[1] += y_in1_temp[0]
                    y_in1_temp[0] = 0.0
                else:  # N in SNH enough for mapping
                    inerts += y_in1_temp[0]
                    y_in1_temp[9] -= y_in1_temp[0] * fsni_adm
                    y_in1_temp[0] = 0.0
            else:  # N in XND enough for mapping
                inerts += y_in1_temp[0]
                y_in1_temp[11] -= y_in1_temp[0] * fsni_adm
                y_in1_temp[0] = 0.0
        else:  # N in SND enough for mapping
            inerts += y_in1_temp[0]
            y_in1_temp[10] -= y_in1_temp[0] * fsni_adm
            y_in1_temp[0] = 0.0
    else:  # N in SI(ASM) enough for mapping
        inerts += y_in1_temp[0]
        y_in1_temp[10] += y_in1_temp[0] * (fsni - fsni_adm)  # put remaining N as SND
        y_in1_temp[0] = 0.0

    # Define the outputs including charge balance

    y_out1[0] = y_in1_temp[1] / 1000.0
    y_out1[1] /= 1000.0
    y_out1[10] = (y_in1_temp[9] + y_in1_temp[10] + y_in1_temp[11]) / 14000.0
    y_out1[11] = inerts / 1000.0
    y_out1[12] = xc / 1000.0
    y_out1[13] = (xchtemp + xchtemp2 + xchtemp3) / 1000.0
    y_out1[14] = (xprtemp + xprtemp2) / 1000.0
    y_out1[15] = (xlitemp + xlitemp2 + xlitemp3) / 1000.0
    y_out1[23] = (biomass_nobio + inertx) / 1000.0
    y_out1[26] = y_in1[14]  # flow rate
    y_out1[27] = t_op - 273.15  # temperature, degC
    y_out1[28] = y_in1[16]  # dummy state
    y_out1[29] = y_in1[17]  # dummy state
    y_out1[30] = y_in1[18]  # dummy state
    y_out1[31] = y_in1[19]  # dummy state
    y_out1[32] = y_in1[20]  # dummy state

    # charge balance, output S_IC
    y_out1[9] = (
        (y_in1_temp2[8] * alfa_no + y_in1_temp2[9] * alfa_nh + y_in1_temp2[12] * alfa_alk)
        - (
            y_out1[3] * alfa_va
            + y_out1[4] * alfa_bu
            + y_out1[5] * alfa_pro
            + y_out1[6] * alfa_ac
            + y_out1[10] * alfa_in
        )
    ) / alfa_co2

    # calculate anions and cations based on full charge balance including H+ and OH-
    scatminussan = (
        y_out1[3] * alfa_va
        + y_out1[4] * alfa_bu
        + y_out1[5] * alfa_pro
        + y_out1[6] * alfa_ac
        + y_out1[10] * alfa_in
        + y_out1[9] * alfa_co2
        + pow(10, (-pk_w + ph_adm))
        - pow(10, -ph_adm)
    )

    if scatminussan > 0:
        y_out1[24] = scatminussan
        y_out1[25] = 0.0
    else:
        y_out1[24] = 0.0
        y_out1[25] = -1.0 * scatminussan

    # Finally there should be a input-output mass balance check here of COD and N

    return y_out1


@jit(nopython=True, cache=True)
def adm2asm(y_in2, t_op, interfacepar):
    """
    Converts ADM1 flows to ASM1 flows
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
    t_op : float
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
    (
        _,
        fnaa,
        fnxc,
        fnbac,
        fxni,
        fsni,
        fsni_adm,
        _,
        _,
        _,
        _,
        frxs_as,
        fdegrade_as,
        r,
        t_base,
        _,
        _,
        pk_a_va_base,
        pk_a_bu_base,
        pk_a_pro_base,
        pk_a_ac_base,
        pk_a_co2_base,
        pk_a_in_base,
    ) = interfacepar

    # y = y_out2
    # u = y_in2
    y_out2 = np.zeros(21)
    y_in2_temp = np.zeros(35)

    y_in2_temp[:] = y_in2[:]

    ph_adm = y_in2[33]

    factor = (1.0 / t_base - 1.0 / t_op) / (100.0 * r)
    # pK_w = pK_w_base - np.log10(math.exp(55900.0*factor))
    pk_a_co2 = pk_a_co2_base - np.log10(math.exp(7646.0 * factor))
    pk_a_in = pk_a_in_base - np.log10(math.exp(51965.0 * factor))
    alfa_va = 1.0 / 208.0 * (-1.0 / (1.0 + np.power(10, pk_a_va_base - ph_adm)))
    alfa_bu = 1.0 / 160.0 * (-1.0 / (1.0 + np.power(10, pk_a_bu_base - ph_adm)))
    alfa_pro = 1.0 / 112.0 * (-1.0 / (1.0 + np.power(10, pk_a_pro_base - ph_adm)))
    alfa_ac = 1.0 / 64.0 * (-1.0 / (1.0 + np.power(10, pk_a_ac_base - ph_adm)))
    alfa_co2 = -1.0 / (1.0 + np.power(10, pk_a_co2 - ph_adm))
    alfa_in = (np.power(10, pk_a_in - ph_adm)) / (1.0 + np.power(10, pk_a_in - ph_adm))
    alfa_nh = 1.0 / 14000.0  # convert mgN/l into kmoleN/m3
    alfa_alk = -0.001  # convert moleHCO3/m3 into kmoleHCO3/m3
    alfa_no = -1.0 / 14000.0  # convert mgN/l into kmoleN/m3

    # Biomass becomes part of XS and XP when transformed into ASM
    # Assume Npart of formed XS to be fnxc and Npart of XP to be fxni
    # Remaining N goes into the ammonia pool (also used as source if necessary)

    biomass = 1000.0 * (
        y_in2_temp[16]
        + y_in2_temp[17]
        + y_in2_temp[18]
        + y_in2_temp[19]
        + y_in2_temp[20]
        + y_in2_temp[21]
        + y_in2_temp[22]
    )
    biomass_nobio = biomass * (1.0 - frxs_as)  # part which is mapped to XP
    biomass_bion = biomass * fnbac - biomass_nobio * fxni
    remaincod = 0.0
    if biomass_bion < 0.0:
        # warnings.warn('Not enough biomass N to map the requested inert part of biomass')
        # print('Not enough biomass N to map the requested inert part of biomass')
        # We map as much as we can, and the remains go to XS!
        xptemp = biomass * fnbac / fxni
        biomass_nobio = xptemp
        biomass_bion = 0.0
    else:
        xptemp = biomass_nobio
    if (biomass_bion / fnxc) <= (biomass - biomass_nobio):
        xstemp = biomass_bion / fnxc  # all biomass N used
        remaincod = biomass - biomass_nobio - xstemp
        if (y_in2_temp[10] * 14000.0 / fnaa) >= remaincod:  # use part of remaining S_IN to form XS
            xstemp += remaincod
        else:
            raise ValueError('Not enough nitrogen to map the requested XS part of biomass')
            # System failure!
    else:
        xstemp = biomass - biomass_nobio  # all biomass COD used

    y_in2_temp[10] = (
        y_in2_temp[10] + biomass * fnbac / 14000.0 - xptemp * fxni / 14000.0 - xstemp * fnxc / 14000.0
    )  # any remaining N in S_IN
    y_out2[3] = (
        y_in2_temp[12] + y_in2_temp[13] + y_in2_temp[14] + y_in2_temp[15]
    ) * 1000.0 + xstemp  # Xs = sum all X except Xi, + biomass as handled above
    y_out2[6] = xptemp  # inert part of biomass

    # mapping of inert XI in AD into XI and possibly XS in AS
    # assumption: same N content in both ASM1 and ADM1 particulate inerts
    # special case: if part of XI in AD can be degraded in AS
    # we have no knowledge about the contents so we put it in as part substrate (XS)
    # we need to keep track of the associated nitrogen
    # N content may be different, take first from XI-N then S_IN,
    # Similar principle could be used for other states.

    inertx = (1.0 - fdegrade_as) * y_in2_temp[23] * 1000.0
    xstemp2 = 0.0
    noninertx = 0.0
    if fdegrade_as > 0.0:
        noninertx = fdegrade_as * y_in2_temp[23] * 1000.0
        if fxni < fnxc:  # N in XI(AD) not enough
            xstemp2 = noninertx * fxni / fnxc
            noninertx -= noninertx * fxni / fnxc
            if (y_in2_temp[10] * 14000.0) < (noninertx * fnxc):  # N in SNH not enough
                xstemp2 += (y_in2_temp[10] * 14000.0) / fnxc
                noninertx -= (y_in2_temp[10] * 14000.0) / fnxc
                y_in2_temp[10] = 0.0
                # warnings.warn('Nitrogen shortage when converting biodegradable XI')
                # print('Nitrogen shortage when converting biodegradable XI')
                # Mapping what we can to XS and putting remaining XI back into XI of ASM
                inertx += noninertx
            else:  # N in S_IN enough for mapping
                xstemp2 += noninertx
                y_in2_temp[10] -= noninertx * fnxc / 14000.0
                noninertx = 0.0
        else:  # N in XI(AD) enough for mapping
            xstemp2 += noninertx
            y_in2_temp[10] += noninertx * (fxni - fnxc) / 14000.0  # put remaining N as S_IN
            noninertx = 0

    y_out2[2] = inertx  # Xi = Xi*fdegrade_AS + possibly nonmappable XS
    y_out2[3] += xstemp2  # extra added XS (biodegradable XI)

    # Mapping of ADM SI to ASM1 SI
    # It is assumed that this mapping will be 100% on COD basis
    # N content may be different, take first from SI-N then from S_IN.
    # Similar principle could be used for other states.

    inerts = 0.0
    if fsni_adm < fsni:  # N in SI(AD) not enough
        inerts = y_in2_temp[11] * fsni_adm / fsni
        y_in2_temp[11] -= y_in2_temp[11] * fsni_adm / fsni
        if (y_in2_temp[10] * 14.0) < (y_in2_temp[11] * fsni):  # N in S_IN not enough
            inerts += y_in2_temp[10] * 14.0 / fsni
            y_in2_temp[11] -= y_in2_temp[10] * 14.0 / fsni
            y_in2_temp[10] = 0.0
            raise ValueError('Not enough nitrogen to map the requested inert part of SI')
            # System failure: nowhere to put SI
        else:  # N in S_IN enough for mapping
            inerts += y_in2_temp[11]
            y_in2_temp[10] -= y_in2_temp[11] * fsni / 14.0
            y_in2_temp[11] = 0.0
    else:  # N in SI(AD) enough for mapping
        inerts += y_in2_temp[11]
        y_in2_temp[10] += y_in2_temp[11] * (fsni_adm - fsni) / 14.0  # put remaining N as S_IN
        y_in2_temp[11] = 0.0

    y_out2[0] = inerts * 1000.0  # Si = Si

    # Define the outputs including charge balance

    # nitrogen in biomass, composites, proteins
    # Xnd is the nitrogen part of Xs in ASM1. Therefore Xnd should be based on the
    # same variables as constitutes Xs, ie AD biomass (part not mapped to XP), xc and xpr if we assume
    # there is no nitrogen in carbohydrates and lipids. The N content of Xi is
    # not included in Xnd in ASM1 and should in my view not be included.

    y_out2[11] = fnxc * (xstemp + xstemp2) + fnxc * 1000.0 * y_in2_temp[12] + fnaa * 1000.0 * y_in2_temp[14]

    # Snd is the nitrogen part of Ss in ASM1. Therefore Snd should be based on the
    # same variables as constitutes Ss, and we assume
    # there is only nitrogen in the amino acids. The N content of Si is
    # not included in Snd in ASM1 and should in my view not be included.

    y_out2[10] = fnaa * 1000.0 * y_in2_temp[1]

    # sh2 and sch4 assumed to be stripped upon reentry to ASM side

    y_out2[1] = (
        y_in2_temp[0] + y_in2_temp[1] + y_in2_temp[2] + y_in2_temp[3] + y_in2_temp[4] + y_in2_temp[5] + y_in2_temp[6]
    ) * 1000.0  # Ss = sum all S except Sh2, Sch4, Si, Sic, Sin

    y_out2[9] = y_in2_temp[10] * 14000.0  # Snh = S_IN including adjustments above

    y_out2[13] = 0.75 * (y_out2[2] + y_out2[3] + y_out2[4] + y_out2[5] + y_out2[6])
    y_out2[14] = y_in2_temp[26]  # flow rate
    y_out2[15] = y_in2[34]  # temperature, degC, should be equal to AS temperature into the AD/AS interface
    y_out2[16] = y_in2_temp[28]  # dummy state
    y_out2[17] = y_in2_temp[29]  # dummy state
    y_out2[18] = y_in2_temp[30]  # dummy state
    y_out2[19] = y_in2_temp[31]  # dummy state
    y_out2[20] = y_in2_temp[32]  # dummy state

    # charge balance, output S_alk (molHCO3/m3)
    y_out2[12] = (
        y_in2[3] * alfa_va
        + y_in2[4] * alfa_bu
        + y_in2[5] * alfa_pro
        + y_in2[6] * alfa_ac
        + y_in2[9] * alfa_co2
        + y_in2[10] * alfa_in
        - y_out2[8] * alfa_no
        - y_out2[9] * alfa_nh
    ) / alfa_alk

    # Finally there should be a input-output mass balance check here of COD and N
    return y_out2
