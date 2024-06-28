import os
import sys

import numpy as np

import bsm2_python.bsm2.init.adm1init_bsm2 as adm1init
import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit
from bsm2_python.bsm2.init import primclarinit_bsm2 as primclarinit

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
    def __init__(self, pp_par, simtime, evaltime):
        """
        Creates a PlantPerformance object.

        Parameters
        ----------
        pp_par : np.ndarray
            Plant performance parameters
            [TOTALCODEMAX, TOTALNEMAX, SNHEMAX, TSSEMAX, BOD5EMAX, BSS, BCOD,
            BNKJ, BNO, BBOD5, PF_QINTR, PF_QR, PF_QW, PF_QPU, PF_QTU, PF_QDO, ME_AD_UNIT]
        simtime : np.ndarray
            Time steps of the simulation
        evaltime : np.ndarray
            Starting and end point of the evaluation time in days
        """
        self.pp_par = pp_par
        self.simtime = simtime
        self.evaltime = evaltime

    def aerationenergy(self, kla, vol, sosat, timestep, evaltime=None):
        """
        Calculates the aeration energy.

        Parameters
        ----------
        kla : np.ndarray
            KLa in each reactor compartment at every time step of the evaluation time
        vol : np.ndarray
            Volume of the reactor in each reactor compartment
        sosat : np.ndarray
            Oxygen saturation concentration in each reactor compartment
        timestep : float
            Time step size of the simulation
        evaltime : np.ndarray
            Starting and end point of the evaluation time in days.
            If None, the previously defined evaluation time will be used.

        Returns
        -------
        float
            Aeration energy in kWh/d
        """
        if evaltime is None:
            evaltime = self.evaltime

        aerationenergy = sum(sum(sosat * vol * kla) * timestep) / (1.8 * 1000 * (evaltime[1] - evaltime[0]))

        return aerationenergy

    @staticmethod
    def aerationenergy_step(kla, vol, sosat):
        """Returns the aeration energy of the plant during the evaluation time

        Parameters
        ----------
        kla : np.ndarray
            KLa values of all reactor compartments at every time step of the evaluation time
        vol : np.ndarray
            Volume of each reactor compartment
        sosat : np.ndarray
            Saturation concentration of Oxygen in each reactor compartment

        Returns
        -------
        float
            Float value of the aeration energy during the evaluation time in kW
        """

        aerationenergy = sum(sosat * vol * kla) / (1.8 * 1000) / 24
        return aerationenergy

    def pumpingenergy(self, flows, pumpfactor, timestep, evaltime=None):
        """
        Calculates the pumping energy.

        Parameters
        ----------
        flows : np.ndarray
            Values of Qintr, Qr and Qw at every time step of the evaluation time
        pumpfactor : np.ndarray
            Weighting factor of each flow
        timestep : float
            Time step size of the simulation
        evaltime : np.ndarray
            Starting and end point of the evaluation time in days.
            If None, the previously defined evaluation time will be used.

        Returns
        -------
        float
            Pumping energy in kWh/d
        """
        if flows.shape != pumpfactor.shape:
            err = f'Shapes of flows and pumpfactor do not match: {flows.shape} and {pumpfactor.shape}'
            raise ValueError(err)
        if evaltime is None:
            evaltime = self.evaltime

        pumpingenergy = np.sum(flows * pumpfactor * timestep) / (evaltime[1] - evaltime[0])

        return pumpingenergy

    @staticmethod
    def pumpingenergy_step(flows, pumpfactor):
        """Returns the pumping energy of the plant during the evaluation time

        Parameters
        ----------
        flows : np.ndarray
            Values of Qintr, Qr and Qw at every time step of the evaluation time
        pumpfactor : np.ndarray
            Weighting factor of each flow

        Returns
        -------
        float
            Float value of the mixing energy during the evaluation time in kW
        """

        # sum of relevant flows * their pumpfactors in kWh/d, divided by 24 to get kW
        pe = sum(flows * pumpfactor) / 24
        return pe

    @staticmethod
    def mixingenergy_step(kla, vol, me_ad):
        """Returns the mixing energy of the plant during the evaluation time

        Parameters
        ----------
        kla : np.ndarray
            KLa values of all reactor compartments at every time step of the evaluation time
        vol : np.ndarray
            Volume of each reactor compartment, including the AD unit
        me_ad : float
            Mixing energy factor for the AD unit in kW/m3
        Returns
        -------
        float
            Float value of the aeration energy during the evaluation time in kW
        """
        lim = 20
        me_asm = 0.005 * sum((kla[i] < lim) * vol[i] for i in range(len(kla)))
        me_adm = me_ad * vol[5]
        me = me_asm + me_adm
        return me

    @staticmethod
    def mixingenergy(kla, vol, timestep, evaltime, me_ad):
        """Returns the mixing energy of the plant during the evaluation time

        Parameters
        ----------
        kla : np.ndarray
            KLa values of all reactor compartments at every time step of the evaluation time
        vol : np.ndarray
            Volume of each reactor compartment, including the AD unit
        timestep : int or float
            Time step of the evaluation time in days
        evaltime : np.ndarray
            Starting and end point of the evaluation time in days
        me_ad : float
            Mixing energy factor for the AD unit in kW/m3

        Returns
        -------
        float
            Float value of the aeration energy during the evaluation time in kWh/d
        """

        kla1, kla2, kla3, kla4, kla5 = kla[0], kla[1], kla[2], kla[3], kla[4]
        lim = 20
        me_asm = (
            0.005
            * (
                len(kla1[kla1 < lim]) * vol[0]
                + len(kla2[kla2 < lim]) * vol[1]
                + len(kla3[kla3 < lim]) * vol[2]
                + len(kla4[kla4 < lim]) * vol[3]
                + len(kla5[kla5 < lim]) * vol[4]
            )
            * timestep
            * 24
        )

        me_adm = 24 * me_ad * vol[5]

        me = (me_asm + me_adm) / (evaltime[1] - evaltime[0])

        return me

    @staticmethod
    def violation(arr_eff, limit, timestep, evaltime):
        """Returns the time in days and percentage of time in which a certain component is over the limit value during
        the evaluation time

        Parameters
        ----------
        arr_eff: np.ndarray
            Concentration of the component in the effluent at every time step of the evaluation time
        limit: int or float
            limit value of the component
        timestep : int or float
            Time step of the evaluation time in days
        evaltime : np.ndarray
            Starting and end point of the evaluation time in days

        Returns
        -------
        np.ndarray
            Array containing the time in days and percentage of time in which
            a certain component is over the limit value during the evaluation time
        """

        violationvalues = np.zeros(2)
        # time in days the component is over the limit value:
        violationvalues[0] = len(arr_eff[arr_eff > limit]) * timestep
        # percentage of time the component is over the limit value:
        violationvalues[1] = len(arr_eff[arr_eff > limit]) * timestep / (evaltime[1] - evaltime[0]) * 100
        return violationvalues

    def violation_step(self, arr_eff, limit):
        """Returns the time in days and percentage of time in which a certain component is over the limit value during
        the evaluation time

        Parameters
        ----------
        arr_eff: np.ndarray
            Concentration of the component in the effluent at every time step of the evaluation time
        limit: int or float
            limit value of the component
        timestep : int or float
            Time step of the evaluation time in days

        Returns
        -------
        np.ndarray
            Array containing the time in days and a boolean if a certain component
            is over the limit value during the evaluation time
        """
        arr_eff = self._reshape_if_float(arr_eff)
        # True if the component is over the limit value:
        violationvalues = np.array([arr_eff > limit])

        return violationvalues

    def advanced_quantities(
        self, arr_eff, components=('kjeldahlN', 'totalN', 'COD', 'BOD5', 'BOD5e', 'X_TSS'), asm1par=asm1init.PAR1
    ):
        """
        Takes an ASM1 array (single timestep or multiple timesteps) and returns
        advanced quantities of the effluent.
        Currently supports the following components:
        - `kjeldahlN`: Kjeldahl nitrogen
        - `totalN`: Total nitrogen
        - `COD`: Chemical oxygen demand
        - `BOD5`: Biological oxygen demand (5 days)

        Parameters
        ----------
        arr_eff : np.ndarray((,21) | (n, 21))
            Array in ASM1 format
        components : List[str] (optional)
            List of components to be calculated. Defaults to ['kjeldahlN', 'totalN', 'COD', 'BOD5e', 'X_TSS']
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

    def qi(self, y_in, *, eqi=False):
        """Returns the quality index of a stream

        Parameters
        ----------
        y_in: np.ndarray(21)
            Array containing the values of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        eqi: bool
            If True, returns the effluent quality index.
            If False, returns the influent quality index. Defaults to False.
            Only difference: eqi uses the BOD5e instead of BOD5.
            Should be used when water passed the activated sludge stages.

        Returns
        -------
        qi: int or float
            the value of the quality index of the stream
        """

        bod5 = 'BOD5' if not eqi else 'BOD5e'

        y_in = self._reshape_if_1d(y_in)

        adv_quant = self.advanced_quantities(y_in, ('kjeldahlN', 'totalN', 'COD', bod5, 'X_TSS'))
        qi = (
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

        return qi

    def tss_mass(self, y_out, vol):
        """
        Calculates the TSS mass of a reactor.

        Parameters
        ----------
        y_out : np.ndarray
            The effluent of the reactor
        vol : np.ndarray
            The volume of the reactor / m^3

        Returns
        -------
        np.ndarray
            The TSS mass / kg
        """
        y_out = self._reshape_if_1d(y_out)

        tss_mass = y_out[:, TSS] * vol / 1000  # kg

        return tss_mass

    def tss_flow(self, y_out):
        """
        Calculates the TSS flow out of a reactor.

        Parameters
        ----------
        y_out : np.ndarray
            The effluent of the reactor

        Returns
        -------
        np.ndarray
            The TSS flow / kg/d
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
        ys_r,
        ys_was,
        ys_of,
        yd_out,
        yst_out,
        yst_vol,
    ):
        """
        Calculates the sludge production of the BSM2 plant setup"""
        variables = [
            yp_of,
            yp_uf,
            yp_internal,
            y_out1,
            y_out2,
            y_out3,
            y_out4,
            y_out5,
            ys_r,
            ys_was,
            ys_of,
            yd_out,
            yst_out,
        ]
        for i in range(len(variables)):
            variables[i] = self._reshape_if_1d(variables[i])

        m_tss_yp_internal = self.tss_mass(yp_internal, primclarinit.VOL_P)

        m_tss_y_out1 = self.tss_mass(y_out1, asm1init.VOL1)
        m_tss_y_out2 = self.tss_mass(y_out2, asm1init.VOL2)
        m_tss_y_out3 = self.tss_mass(y_out3, asm1init.VOL3)
        m_tss_y_out4 = self.tss_mass(y_out4, asm1init.VOL4)
        m_tss_y_out5 = self.tss_mass(y_out5, asm1init.VOL5)
        m_tss_asm1 = m_tss_y_out1 + m_tss_y_out2 + m_tss_y_out3 + m_tss_y_out4 + m_tss_y_out5

        ys_vol = (settler1dinit.DIM[0] * settler1dinit.DIM[1]) / 10
        y_settler = ys_r + ys_was + ys_of
        m_tss_y_settler = self.tss_mass(y_settler, ys_vol)

        m_tss_yd_out = self.tss_mass(yd_out, adm1init.V_LIQ)

        m_tss_yst_out = self.tss_mass(yst_out, yst_vol[0])

        # e_load_y_eff = self.tss_flow(y_eff)

        tss_mass = m_tss_yp_internal + m_tss_asm1 + m_tss_y_settler + m_tss_yd_out + m_tss_yst_out  # + e_load_ydw_s

        return tss_mass

    @staticmethod
    def added_carbon_mass(carb, concentration):
        """
        Calculates the added carbon mass.

        Parameters
        ----------
        carb : float | np.ndarray
            The carbon flow added to the system / m^3/d
        concentration : np.ndarray
            The concentration of the carbon flow / mgCOD/L

        Returns
        -------
        np.ndarray
            The added carbon mass / kgCOD/d
        """
        # if carb is a np.ndarray, sum the rows
        if isinstance(carb, np.ndarray) and carb.ndim == 1:
            carb = np.sum(carb)

        carbon_mass = carb * concentration / 1000

        return carbon_mass

    def gas_production(self, yd_out, t_op, p_atm=1.0130):
        """
        Calculates the gas production of the digester

        Parameters
        ----------
        yd_out : np.ndarray
            concentrations of 51 ADM1 components and
            gas phase parameters after the digester
            [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
             X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
             Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D, pH, S_H_ion, S_hva, S_hbu,
             S_hpro, S_hac, S_hco3, S_CO2, S_nh3, S_NH4+, S_gas_h2, S_gas_ch4, S_gas_co2,
             p_gas_h2, p_gas_ch4, p_gas_co2, P_gas, q_gas]
        p_atm : float
            The atmospheric pressure / bar
        t_op : np.ndarray
            The operating temperature / K

        Returns
        -------
        np.ndarray
            methane production / kg/d
        np.ndarray
            hydrogen production / kg/d
        np.ndarray
            carbon dioxide production / kg/d
        np.ndarray
            total gas flow rate / m^3/d
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

    def heat_demand_step(self, y_uf, t_op):
        """
        Calculates the heating demand of the sludge flow

        Parameters
        ----------
        y_uf : np.ndarray
            The sludge flow of a reactor
        t_op : np.ndarray
            The operating temperature of the reactor
        Returns
        -------
        np.ndarray
            The heating demand / kW
        """
        rho = 1000  # kg/m^3 (density of water)
        cp = 4.186  # kJ/kg*K (specific heat capacity of water)
        y_uf = self._reshape_if_1d(y_uf)
        flow = y_uf[:, 14]
        t = t_op - (y_uf[:, 15] + 273.15)
        heat_demand = flow / 24 / 60 * rho * cp * t  # m^3/s * kg/m^3 * kJ/kg*K * K = kW

        return heat_demand

    @staticmethod
    def heat_demand(primary_clarifier_yuf, thickener_yuf, step_time, evaltime):
        """Returns the net heating energy demand per day

        Parameters
        ----------
        primary_clarifier_yuf: np.ndarray(len(simtime),21)
            Under flow of Primary Clarifier unite containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        thickner_yuf: np.ndarray(len(simtime),21)
            Under flow of thickner unite containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        step_time : int or float
            Time step of the evaluation time in days

        evaltime : np.ndarray
            Starting and end point of the evaluation time in days

        Returns
        -------
        Heatenergyperd: int or float
            The net heating energy demand per day
        """

        totalt = evaltime[1] - evaltime[0]

        ro = 1000  # Water density in kg/m3
        cp = 4.186  # Specific heat capacity for water in Ws/gC

        tdigesterin = (
            np.multiply(primary_clarifier_yuf[:, 14], primary_clarifier_yuf[:, 15])
            + np.multiply(thickener_yuf[:, 14], thickener_yuf[:, 15])
        ) / (primary_clarifier_yuf[:, 14] + thickener_yuf[:, 14])
        qad = primary_clarifier_yuf[:, 14] + thickener_yuf[:, 14]  # Ref. page 67 technical documentation
        heatpower = np.multiply((35 - tdigesterin), qad) * ro * cp / 86400  # kW
        heatenergyperd = 24 * sum(heatpower * step_time) / totalt

        return heatenergyperd

    @staticmethod
    def oci(pe, ae, me, tss, cm, he, mp):
        """
        Calculates the operational cost index of the plant

        Parameters
        ----------
        pe : np.ndarray
            The pumping energy of the plant / kW
        ae : np.ndarray
            The aeration energy of the plant / kW
        me : np.ndarray
            The mixing energy of the plant / kW
        tss : np.ndarray
            The total suspended solids production of the plant / kg/d
        cm : np.ndarray
            The added carbon mass of the plant / kg/d
        he : np.ndarray
            The heating demand of the plant / kW
        mp : np.ndarray
            The methane production of the plant / kg/d
        """
        oci = 3 * tss + ae + me + pe + 3 * cm + max(0, he - 7 * mp) - 6 * mp
        return oci

    # TODO: Add doci (dynamic oci) for varying power prices

    @staticmethod
    def _reshape_if_1d(arr):
        """
        Reshapes the array to 2D if it is 1D.

        Parameters
        ----------
        arr : np.ndarray
            Array to be reshaped.
            Can be of shape (n,) or (m,n)

        Returns
        -------
        np.ndarray
            Reshaped array of shape (1,n) or (m,n)
        """
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)

        return arr

    @staticmethod
    def _reshape_if_float(fl):
        """
        Reshapes a float to a 1D numpy array

        Parameters
        ----------
        fl : int | float | np.ndarray
            value to be reshaped

        Returns
        -------
        np.ndarray
            Reshaped value
        """
        if isinstance(fl, int | float):
            fl = np.array([fl])

        return fl

    @staticmethod
    def _reshape_if_1_element(arr):
        """
        Reshapes the array to float if it is 1 element.
        """
        if arr.size == 1:
            arr = arr[0]

        return arr
