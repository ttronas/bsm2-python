import os
import sys

import numpy as np

import bsm2_python.bsm2.init.adm1init_bsm2 as adm1init
import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit
from bsm2_python.bsm2.init import primclarinit_bsm2 as primclarinit
from bsm2_python.gases.gases import H2O

path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')

SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = np.arange(21)

(
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
) = np.arange(17)


class PlantPerformance:
    """Creates a PlantPerformance object.

    Parameters
    ----------
    pp_par : np.ndarray(17)
        Plant performance parameters. \n
        [TOTALCODEMAX, TOTALNEMAX, SNHEMAX, TSSEMAX, BOD5EMAX, BSS, BCOD,
        BNKJ, BNO, BBOD5, PF_QINTR, PF_QR, PF_QW, PF_QPU, PF_QTU, PF_QDO, ME_AD_UNIT]
    """

    def __init__(self, pp_par):
        self.pp_par = pp_par

    @staticmethod
    def aerationenergy_step(kla, vol, sosat):
        """Returns the aeration energy of the plant during the evaluation time.

        Parameters
        ----------
        kla : np.ndarray
            KLa values of all activated sludge reactor compartments at every time step of the evaluation time [d⁻¹]. \n
            [KLA1, KLA2, KLA3,...]
        vol : np.ndarray
            Volume of each activated sludge reactor compartment [m³]. \n
            [VOL1, VOL2, VOL3,...]
        sosat : np.ndarray
            Oxygen saturation concentration in each activated sludge reactor compartment [%]. \n
            [SOSAT1, SOSAT2, SOSAT3,...]

        Returns
        -------
        aerationenergy : float
            Aeration energy during the evaluation time [kW].
        """

        aerationenergy = sum(sosat * vol * kla) / (1.8 * 1000) / 24
        return aerationenergy

    @staticmethod
    def pumpingenergy_step(flows, pumpfactor):
        """Returns the pumping energy of the plant during the evaluation time.

        Parameters
        ----------
        flows : np.ndarray(6)
            Flow rates at every time step of the evaluation time <br>[m³ ⋅ d⁻¹]. \n
            [Q_INTR, Q_R, Q_W, Q_PU, Q_TU, Q_DO]
        pumpfactor : np.ndarray(6)
            Pumping energy factor for each flow [kWh ⋅ m⁻³]. \n
            [PF_QINTR, PF_QR, PF_QW, PF_QPU, PF_QTU, PF_QDO]

        Returns
        -------
        pe : float
            Pumping energy during the evaluation time [kW].
        """

        # sum of relevant flows * their pumpfactors in kWh/d, divided by 24 to get kW
        pe = sum(flows * pumpfactor) / 24
        return pe

    @staticmethod
    def mixingenergy_step(kla, vol, me_ad):
        """Returns the mixing energy of the plant during the evaluation time.

        Parameters
        ----------
        kla : np.ndarray
            KLa values of all activated sludge reactor compartments at every time step of the evaluation time [d⁻¹]. \n
            [KLA1, KLA2, KLA3,...]
        vol : np.ndarray
            Volume of each activated sludge reactor compartment, including the anaerobic digester unit [m³]. \n
            [VOL1, VOL2, VOL3,..., ADM1_VOL_LIQ]
        me_ad : float
            Mixing energy factor for the anaerobic digester unit <br>
            [kWh ⋅ m⁻³].

        Returns
        -------
        me : float
            Mixing energy during the evaluation time [kW].
        """

        lim = 20
        me_asm = 0.005 * sum((kla[i] < lim) * vol[i] for i in range(len(kla)))
        me_adm = me_ad * vol[5]
        me = me_asm + me_adm
        return me

    def violation_step(self, arr_eff, limit):
        """Returns the time and percentage of time in which a certain component is over the limit value during
        the evaluation time.

        Parameters
        ----------
        arr_eff : float
            Concentration of the component in the effluent at every time step of the evaluation time [g(COMP) ⋅ m⁻³].
        limit : float
            Limit value of the component. Must have the same unit as the component [g(COMP) ⋅ m⁻³].

        Returns
        -------
        violationvalues : bool
            Array containing if a certain component
            is over the limit value during the evaluation time.
        """

        arr_eff = self._reshape_if_float(arr_eff)
        # True if the component is over the limit value:
        violationvalues = np.array([arr_eff > limit])

        return violationvalues[0]

    def advanced_quantities(
        self, arr_eff, components=('kjeldahlN', 'totalN', 'COD', 'BOD5', 'BOD5e', 'X_TSS'), asm1par=asm1init.PAR1
    ):
        """Takes an ASM1 array (single timestep or multiple timesteps) and returns
        advanced quantities of the effluent.

        Currently supports the following components: \n
        - `kjeldahlN`: Total Kjeldahl nitrogen [g(N) ⋅ m⁻³]
        - `totalN`: Total nitrogen [g(N) ⋅ m⁻³]
        - `COD`: Chemical oxygen demand [g(COD) ⋅ m⁻³]
        - `BOD5`: Biological oxygen demand (5 days) [g(BOD) ⋅ m⁻³]
        - `X_TSS`: Total suspended solids [g(SS) ⋅ m⁻³]

        Parameters
        ----------
        arr_eff : np.ndarray(21) or np.ndarray(n, 21)
            Array in ASM1 format. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        components : list[str] (optional)
            List of components to be calculated.
            Defaults to ['kjeldahlN', 'totalN', 'COD', 'BOD5', 'BOD5e', 'X_TSS']
        asm1par : np.ndarray(24)
            Parameters for the activated sludge reactor. \n
            [MU_H, K_S, K_OH, K_NO, B_H, MU_A, K_NH, K_OA, B_A, NY_G, K_A, K_H,K_X, NY_H,
            Y_H, Y_A, F_P, I_XB, I_XP, X_I2TSS, X_S2TSS, X_BH2TSS, X_BA2TSS, X_P2TSS]

        Returns
        -------
        adv_eff : np.ndarray
            Array containing the choosen advanced quantities of the effluent.
        """

        arr_eff = self._reshape_if_1d(arr_eff)
        adv_eff = np.zeros((arr_eff.shape[0], len(components)))

        for idx, component in enumerate(components):
            if component == 'kjeldahlN':
                adv_eff[:, idx] = (
                    arr_eff[:, SNH]
                    + arr_eff[:, SND]
                    + arr_eff[:, XND]
                    + asm1par[17] * (arr_eff[:, XBH] + arr_eff[:, XBA])
                    + asm1par[18] * (arr_eff[:, XP] + arr_eff[:, XI])
                )
            elif component == 'totalN':
                adv_eff[:, idx] = (
                    arr_eff[:, SNH]
                    + arr_eff[:, SND]
                    + arr_eff[:, XND]
                    + asm1par[17] * (arr_eff[:, XBH] + arr_eff[:, XBA])
                    + asm1par[18] * (arr_eff[:, XP] + arr_eff[:, XI])
                    + arr_eff[:, SNO]
                )
            elif component == 'COD':
                adv_eff[:, idx] = (
                    arr_eff[:, SS]
                    + arr_eff[:, SI]
                    + arr_eff[:, XS]
                    + arr_eff[:, XI]
                    + arr_eff[:, XBH]
                    + arr_eff[:, XBA]
                    + arr_eff[:, XP]
                )
            elif component == 'BOD5':
                adv_eff[:, idx] = 0.65 * (
                    arr_eff[:, SS] + arr_eff[:, XS] + (1 - asm1par[16]) * (arr_eff[:, XBH] + arr_eff[:, XBA])
                )
            elif component == 'BOD5e':
                adv_eff[:, idx] = 0.25 * (
                    arr_eff[:, SS] + arr_eff[:, XS] + (1 - asm1par[16]) * (arr_eff[:, XBH] + arr_eff[:, XBA])
                )
            elif component == 'X_TSS':
                adv_eff[:, idx] = 0.75 * (
                    arr_eff[:, XS] + arr_eff[:, XP] + arr_eff[:, XI] + arr_eff[:, XBH] + arr_eff[:, XBA]
                )
            else:
                err = f"Component '{component}' not supported"
                raise ValueError(err)

        return adv_eff

    def iqi(self, y_in):
        """Returns the influent quality index (IQI).

        Parameters
        ----------
        y_in : np.ndarray(21) or np.ndarray(n, 21)
            Array containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) of the influent to BSM1. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]

        Returns
        -------
        iqi : float or np.ndarray
            The value of the influent quality index of the stream <br>
            [kg(Pollution Units) ⋅ d⁻¹].
        """

        y_in = self._reshape_if_1d(y_in)

        adv_quant = self.advanced_quantities(y_in, ('kjeldahlN', 'totalN', 'COD', 'BOD5', 'X_TSS'))
        iqi = (
            (
                self.pp_par[BSS] * y_in[:, TSS]
                + self.pp_par[BCOD] * adv_quant[:, 2]
                + self.pp_par[BNKJ] * adv_quant[:, 0]
                + self.pp_par[BNO] * y_in[:, SNO]
                + self.pp_par[BBOD5] * adv_quant[:, 3]
            )
            * y_in[:, Q]
            / 1000
        )

        return iqi

    def eqi(self, ys_of, y_plant_bp, y_as_bp_c_eff):
        """Returns the effluent quality index (EQI).

        Parameters
        ----------
        ys_of : np.ndarray(21) or np.ndarray(n, 21)
            Array containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) after the fifth ASM reactor. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        y_plant_bp : np.ndarray(21) or np.ndarray(n, 21)
            Array containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) after the plant bypass. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        y_as_bp_c_eff : np.ndarray(21) or np.ndarray(n, 21)
            Array containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) after the ASM bypass. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]

        Returns
        -------
        eqi: float or np.ndarray
            The value of the effluent quality index of the stream <br>[kg(Pollution Units) ⋅ d⁻¹].
        """

        ys_of = self._reshape_if_1d(ys_of)
        y_plant_bp = self._reshape_if_1d(y_plant_bp)
        y_as_bp_c_eff = self._reshape_if_1d(y_as_bp_c_eff)

        y_out5_aq = self.advanced_quantities(ys_of, ('kjeldahlN', 'totalN', 'COD', 'BOD5e', 'X_TSS'))
        y_p_bp_aq = self.advanced_quantities(y_plant_bp, ('kjeldahlN', 'totalN', 'COD', 'BOD5', 'X_TSS'))
        y_bp_as_aq = self.advanced_quantities(y_as_bp_c_eff, ('kjeldahlN', 'totalN', 'COD', 'BOD5', 'X_TSS'))

        qe = ys_of[:, Q] + y_plant_bp[:, Q] + y_as_bp_c_eff[:, Q]
        tsse = (
            ys_of[:, TSS] * ys_of[:, Q]
            + y_plant_bp[:, TSS] * y_plant_bp[:, Q]
            + y_as_bp_c_eff[:, TSS] * y_as_bp_c_eff[:, Q]
        ) / qe
        cod = (
            y_out5_aq[:, 2] * ys_of[:, Q] + y_p_bp_aq[:, 2] * y_plant_bp[:, Q] + y_bp_as_aq[:, 2] * y_as_bp_c_eff[:, Q]
        ) / qe
        nkje = (
            y_out5_aq[:, 0] * ys_of[:, Q] + y_p_bp_aq[:, 0] * y_plant_bp[:, Q] + y_bp_as_aq[:, 0] * y_as_bp_c_eff[:, Q]
        ) / qe
        snoe = (
            ys_of[:, SNO] * ys_of[:, Q]
            + y_plant_bp[:, SNO] * y_plant_bp[:, Q]
            + y_as_bp_c_eff[:, SNO] * y_as_bp_c_eff[:, Q]
        ) / qe
        bod5e = (
            y_out5_aq[:, 3] * ys_of[:, Q] + y_p_bp_aq[:, 3] * y_plant_bp[:, Q] + y_bp_as_aq[:, 3] * y_as_bp_c_eff[:, Q]
        ) / qe

        eqi = (
            (
                self.pp_par[BSS] * tsse
                + self.pp_par[BCOD] * cod
                + self.pp_par[BNKJ] * nkje
                + self.pp_par[BNO] * snoe
                + self.pp_par[BBOD5] * bod5e
            )
            * qe
            / 1000
        )
        return eqi

    def tss_mass(self, y_out, vol):
        """Calculates the total suspended solids (TSS) mass of a reactor.

        Parameters
        ----------
        y_out : np.ndarray
            The effluent of the reactor.
        vol : np.ndarray
            The volume of the reactor [m³].

        Returns
        -------
        tss_mass : float
            Mass of total suspended solids (TSS) [kg].
        """

        y_out = self._reshape_if_1d(y_out)

        tss_mass = y_out[:, TSS] * vol / 1000  # kg

        return tss_mass

    def tss_flow(self, y_out):
        """Calculates the total suspended solids (TSS) flow out of a reactor.

        Parameters
        ----------
        y_out : np.ndarray
            The effluent of the reactor.

        Returns
        -------
        tss_flow : np.ndarray
            Mass flow of total suspende solids (TSS) [kg(SS) ⋅ d⁻¹].
        """

        y_out = self._reshape_if_1d(y_out)
        tss_flow = sum(y_out[:, TSS] * y_out[:, Q]) / 1000  # kg/d

        return tss_flow

    def tss_mass_bsm2(
        self,
        yp_of,
        yp_uf,
        yp_internal,
        y_out1,
        y_out2,
        y_out3,
        y_out4,
        y_out5,
        ys_tss_internal,
        yd_out,
        yst_out,
        yst_vol,
    ):
        """Calculates the sludge production of the BSM2 plant setup.

        Parameters
        ----------
        yp_of : np.ndarray(21)
            Primary clarifier overflow (effluent) concentrations of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        yp_uf : np.ndarray(21)
            Primary clarifier underflow (sludge) concentrations of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states). \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        yp_internal : np.ndarray(21)
            Primary clarifier internal (basically influent) concentrations of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states).
            Only for evaluation purposes. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        y_out1 : np.ndarray(21)
            Concentrations of the 21 components after the first ASM reactor. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        y_out2 : np.ndarray(21)
            Concentrations of the 21 components after the second ASM reactor. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        y_out3 : np.ndarray(21)
            Concentrations of the 21 components after the third ASM reactor. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        y_out4 : np.ndarray(21)
            Concentrations of the 21 components after the fourth ASM reactor. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        y_out5 : np.ndarray(21)
            Concentrations of the 21 components after the fifth ASM reactor. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        ys_tss_internal: np.ndarray(nooflayers)
            Total suspended solids (TSS) concentrations of the internals of the settler [g(TSS) ⋅ m⁻³]. \n
            [TSS_LAY1, TSS_LAY2, TSS_LAY3,...]
        yd_out : np.ndarray(51)
            Concentrations of the 51 components and gas phase parameters after the digester. \n
            [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
            X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
            Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D, pH, S_H_ion, S_hva, S_hbu,
            S_hpro, S_hac, S_hco3, S_CO2, S_nh3, S_NH4+, S_gas_h2, S_gas_ch4, S_gas_co2,
            p_gas_h2, p_gas_ch4, p_gas_co2, P_gas, q_gas]
        yst_out : np.ndarray(21)
            Concentrations of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
            in the effluent of the storage tank. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        yst_vol : float
            Current volume of the storage tank [m³].

        Returns
        -------
        tss_mass : float
            Sludge production [kg ⋅ d⁻¹].
        """

        # reshape if 1D for all input streams
        yp_of = self._reshape_if_1d(yp_of)
        yp_uf = self._reshape_if_1d(yp_uf)
        yp_internal = self._reshape_if_1d(yp_internal)
        y_out1 = self._reshape_if_1d(y_out1)
        y_out2 = self._reshape_if_1d(y_out2)
        y_out3 = self._reshape_if_1d(y_out3)
        y_out4 = self._reshape_if_1d(y_out4)
        y_out5 = self._reshape_if_1d(y_out5)
        ys_tss_internal = self._reshape_if_1d(ys_tss_internal)
        yd_out = self._reshape_if_1d(yd_out)
        yst_out = self._reshape_if_1d(yst_out)

        yst_vol = self._reshape_if_float(yst_vol)

        m_tss_yp_internal = self.tss_mass(yp_internal, primclarinit.VOL_P)
        m_tss_y_out1 = self.tss_mass(y_out1, asm1init.VOL1)
        m_tss_y_out2 = self.tss_mass(y_out2, asm1init.VOL2)
        m_tss_y_out3 = self.tss_mass(y_out3, asm1init.VOL3)
        m_tss_y_out4 = self.tss_mass(y_out4, asm1init.VOL4)
        m_tss_y_out5 = self.tss_mass(y_out5, asm1init.VOL5)
        m_tss_asm1 = m_tss_y_out1 + m_tss_y_out2 + m_tss_y_out3 + m_tss_y_out4 + m_tss_y_out5

        ys_vol = settler1dinit.DIM[0] * settler1dinit.DIM[1]  # assumption: all layers have the same volume
        m_tss_ys_internal = np.sum(ys_tss_internal, axis=1) / settler1dinit.LAYER[1] * ys_vol / 1000  # kg

        m_tss_yd_out = self.tss_mass(yd_out, adm1init.V_LIQ)

        m_tss_yst_out = self.tss_mass(yst_out, yst_vol[0])

        tss_mass = m_tss_yp_internal + m_tss_asm1 + m_tss_ys_internal + m_tss_yd_out + m_tss_yst_out  # + e_load_ydw_s

        tss_mass = self._reshape_if_1_element(tss_mass)

        return tss_mass

    @staticmethod
    def added_carbon_mass(carb, concentration):
        """Calculates the total added carbon mass.

        Parameters
        ----------
        carb : float or np.ndarray
            The carbon flow added to the system <br>[kg(COD) ⋅ d⁻¹].
        concentration : float or np.ndarray
            The concentration of the carbon flow <br>[g(COD) ⋅ m⁻³]. \n
            [CARB_CONC1, CARB_CONC2, CARB_CONC3,...]

        Returns
        -------
        carbon_mass : float or np.ndarray
            The total added carbon mass [kg(COD) ⋅ d⁻¹].
        """
        # if carb is a np.ndarray, sum the rows
        if isinstance(carb, np.ndarray) and carb.ndim == 1:
            carb = np.sum(carb)

        carbon_mass = carb * concentration / 1000

        return carbon_mass

    def gas_production(self, yd_out, t_op, p_atm=1.0130):
        """Calculates the gas production of the digester.

        Parameters
        ----------
        yd_out : np.ndarray(51)
            Concentrations of 51 ADM1 components and
            gas phase parameters after the digester. \n
            [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
            X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
            Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D, pH, S_H_ion, S_hva, S_hbu,
            S_hpro, S_hac, S_hco3, S_CO2, S_nh3, S_NH4+, S_gas_h2, S_gas_ch4, S_gas_co2,
            p_gas_h2, p_gas_ch4, p_gas_co2, P_gas, q_gas]
        p_atm : float
            The atmospheric pressure [bar].
        t_op : float
            Operational temperature of the anaerobic digester [K].

        Returns
        -------
        ch4 : float
            Methane production of the anaerobic digester [kg ⋅ d⁻¹].
        h2 : float
            Hydrogen production of the anaerobic digester [kg ⋅ d⁻¹].
        co2 : float
            Carbon dioxide production of the anaerobic digester [kg ⋅ d⁻¹].
        q_gas : float
            Total gas flow rate of the anaerobic digester [m³ ⋅ d⁻¹].
        """

        r = 0.0831  # kJ/(mol*K)
        yd_out = self._reshape_if_1d(yd_out)
        # bar/bar * bar * g/mol / (kJ/mol) * m^3/d = kg/d
        ch4 = yd_out[:, 47] / yd_out[:, 49] * p_atm * 16 / (r * t_op) * yd_out[:, 50]
        h2 = yd_out[:, 46] / yd_out[:, 49] * p_atm * 2 / (r * t_op) * yd_out[:, 50]
        co2 = yd_out[:, 48] / yd_out[:, 49] * p_atm * 44 / (r * t_op) * yd_out[:, 50]
        q_gas = yd_out[:, 50]
        ch4 = self._reshape_if_1_element(ch4)
        h2 = self._reshape_if_1_element(h2)
        co2 = self._reshape_if_1_element(co2)
        q_gas = self._reshape_if_1_element(q_gas)
        return ch4, h2, co2, q_gas

    def heat_demand_step(self, y_in, t_op):
        """Calculates the heating demand of the sludge flow to the anaerobic digester.

        Parameters
        ----------
        y_in : np.ndarray(21)
            Influent concentrations of the 21 standard components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) before the anaerobic digester. \n
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        t_op : float
            Operational temperature of the anaerobic digester [K].

        Returns
        -------
        heat_demand : np.ndarray
            Heating demand of the sludge flow to the anaerobic digester [kW].
        """

        rho = H2O.rho_l  # kg/m^3 (density of water)
        cp = H2O.cp_l  # kJ/kg*K (specific heat capacity of water)
        y_in = self._reshape_if_1d(y_in)
        flow = y_in[:, 14]
        t = t_op - (y_in[:, 15] + 273.15)
        heat_demand = flow / 86400 * rho * cp * t  # m^3/d / s/d * kg/m^3 * kJ/kg*K * K = kW
        return heat_demand

    def get_t_op(self, heat, yd_in, yd_out, vol_fermenter):
        """Calculates the operating temperature of the anaerobic digestor reactor based on the heat input.

        Parameters
        ----------
        heat : float
            Heat input to the anaerobic digester [kW].
        yd_in : np.ndarray(51)
            Influent concentrations of 51 ADM1 components and
            gas phase parameters before the digester. \n
            [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
            X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
            Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D, pH, S_H_ion, S_hva, S_hbu,
            S_hpro, S_hac, S_hco3, S_CO2, S_nh3, S_NH4+, S_gas_h2, S_gas_ch4, S_gas_co2,
            p_gas_h2, p_gas_ch4, p_gas_co2, P_gas, q_gas]
        yd_out : np.ndarray(51)
            Effluent concentrations of 51 ADM1 components and
            gas phase parameters after the digester. \n
            [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
            X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
            Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D, pH, S_H_ion, S_hva, S_hbu,
            S_hpro, S_hac, S_hco3, S_CO2, S_nh3, S_NH4+, S_gas_h2, S_gas_ch4, S_gas_co2,
            p_gas_h2, p_gas_ch4, p_gas_co2, P_gas, q_gas]
        vol_fermenter : float
            Volume of the anaerobic digester [m³].

        Returns
        -------
        t_op : float
            Operating temperature of the reactor [K].
        """

        yd_in = self._reshape_if_1d(yd_in)
        # kJ/(m^3*K) * m^3 * K = kW
        cp_fermenter = 4.2  # kJ/(m^3*K)
        temp_fermenter = 35  # old_temp
        heat_fermenter = temp_fermenter * vol_fermenter * cp_fermenter  # kJ
        heat_outflow = temp_fermenter * yd_out[Q] * cp_fermenter  # kJ
        heat_inflow = heat  # kJ
        current_heat = heat_fermenter + heat_inflow - heat_outflow  # kJ
        t_op = current_heat / (vol_fermenter * cp_fermenter)

        return t_op

    @staticmethod
    def oci(pe, ae, me, tss, cm, he, mp):
        """Calculates the operational cost index of the plant.

        Parameters
        ----------
        pe : float
            Pumping energy of the plant [kWh ⋅ d⁻¹].
        ae : float
            Aeration energy of the plant [kWh ⋅ d⁻¹].
        me : float
            Mixing energy of the plant [kWh ⋅ d⁻¹].
        tss : float
            Total suspended solids production of the plant [kWh ⋅ d⁻¹].
        cm : float
            Added carbon mass of the plant [kWh ⋅ d⁻¹].
        he : float
            Heating demand of the plant [kWh ⋅ d⁻¹].
        mp : float
            Methane production of the plant [kWh ⋅ d⁻¹].

        Returns
        -------
        oci : float
            Operational cost index of the plant [-].
        """

        tss_cost = 3 * tss
        ae_cost = ae
        me_cost = me
        pe_cost = pe
        cm_cost = 3 * cm
        he_cost = max(0.0, he - 7 * mp)
        mp_income = 6 * mp

        return tss_cost + ae_cost + me_cost + pe_cost + cm_cost + he_cost - mp_income

    @staticmethod
    def _reshape_if_1d(arr):
        """Reshapes the array to 2D if it's 1D.

        Parameters
        ----------
        arr : np.ndarray(n) or np.ndarray(m,n)
            Array to be reshaped.

        Returns
        -------
        arr : np.ndarray(1,n) or np.ndarray(m,n)
            Reshaped array.
        """

        if arr.ndim == 1:
            arr = arr.reshape(1, -1)

        return arr

    @staticmethod
    def _reshape_if_float(fl):
        """Reshapes a float to a 1D numpy array.

        Parameters
        ----------
        fl : int or float or np.ndarray
            Value to be reshaped.

        Returns
        -------
        fl : np.ndarray
            Reshaped value.
        """

        if isinstance(fl, int | float):
            fl = np.array([fl])

        return fl

    @staticmethod
    def _reshape_if_1_element(arr):
        """Reshapes the array to float if it is 1 element.

        Parameters
        ----------
        arr : np.ndarray(1)
            Array with only 1 element.

        Returns
        -------
        arr : float
            Reshaped float value.
        """

        if arr.size == 1:
            arr = arr[0]

        return arr
