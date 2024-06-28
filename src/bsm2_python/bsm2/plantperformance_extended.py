import os
import sys

import numpy as np

import bsm2_python.bsm2.init.adm1init_bsm2 as adm1init
import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
import bsm2_python.bsm2.init.reginit_bsm2 as reginit
import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit
from bsm2_python.bsm2.init import primclarinit_bsm2 as primclarinit

path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')
indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components


class PlantPerformance:
    def __init__(self):
        """
        Creates a PlantPerformance object.
        """
        # Effluent pollutant concentration discharge limits
        self.totalCODemax = 100
        self.totalNemax = 18
        self.SNHemax = 4
        self.TSSemax = 30
        self.BOD5emax = 10

        # Pollutant weighting factors, effluent pollutants
        self.BSS = 2
        self.BCOD = 1
        self.BNKj = 30
        self.BNO = 10
        self.BBOD5 = 2

        # Pumping energy factors
        self.PF_Qintr = 0.004  # kWh/m3, pumping energy factor, internal AS recirculation
        self.PF_Qr = 0.008  # kWh/m3, pumping energy factor, AS sludge recycle
        self.PF_Qw = 0.05  # kWh/m3, pumping energy factor, AS wastage flow
        self.PF_Qpu = 0.075  # kWh/m3, pumping energy factor, pumped underflow from primary clarifier
        self.PF_Qtu = 0.060  # kWh/m3, pumping energy factor, pumped underflow from thickener
        self.PF_Qdo = 0.004  # kWh/m3, pumping energy factor, pumped underflow from dewatering unit

    @staticmethod
    def aerationenergy(kla, vol, sosat, sampleinterval, evaltime):
        """Returns the aeration energy of the plant during the evaluation time

        Parameters
        ----------
        kla : np.ndarray
            KLa values of all reactor compartments at every time step of the evaluation time
        vol : np.ndarray
            Volume of each reactor compartment
        sosat : np.ndarray
            Saturation concentration of Oxygen in each reactor compartment
        sampleinterval : int or float
            Time step of the evaluation time in days
        evaltime : np.ndarray
            Starting and end point of the evaluation time in days

        Returns
        -------
        float
            Float value of the aeration energy during the evaluation time in kWh/d
        """
        kla1, kla2, kla3, kla4, kla5 = kla

        kla1newvec = sosat[0] * vol[0] * kla1
        kla2newvec = sosat[1] * vol[1] * kla2
        kla3newvec = sosat[2] * vol[2] * kla3
        kla4newvec = sosat[3] * vol[3] * kla4
        kla5newvec = sosat[4] * vol[4] * kla5

        airenergyvec = (kla1newvec + kla2newvec + kla3newvec + kla4newvec + kla5newvec) / (1.8 * 1000)
        airenergy = sum(airenergyvec * sampleinterval)
        airenergyperd = airenergy / (evaltime[1] - evaltime[0])

        # ae = sum(sum(sosat * vol * kla)*sampleinterval)/(1.8*1000 * (evaltime[1]-evaltime[0]))

        # ae = np.sum(sosat * vol * kla*sampleinterval)/(1.8*1000 * (evaltime[1]-evaltime[0]))

        return airenergyperd

    @staticmethod
    def pumpingenergy(flows, pumpfactor, sampleinterval, evaltime):
        """Returns the pumping energy of the plant during the evaluation time

        Parameters
        ----------
        flows : np.ndarray
            Values of Qintr, Qr and Qw at every time step of the evaluation time
        pumpfactor : np.ndarray
            Weighting factor of each flow
        sampleinterval : int or float
            Time step of the evaluation time in days
        evaltime : np.ndarray
            Starting and end point of the evaluation time in days

        Returns
        -------
        float
            Float value of the mixing energy during the evaluation time in kWh/d
        """

        # pe = sum(sum(flows * pumpfactor) * sampleinterval) / (evaltime[1] - evaltime[0])

        pe = np.sum(flows * pumpfactor * sampleinterval) / (evaltime[1] - evaltime[0])

        return pe

    @staticmethod
    def mixingenergy(kla, vol, sampleinterval, evaltime):
        """Returns the mixing energy of the plant during the evaluation time

        Parameters
        ----------
        kla : np.ndarray
            KLa values of all reactor compartments at every time step of the evaluation time
        vol : np.ndarray
            Volume of each reactor compartment
        sampleinterval : int or float
            Time step of the evaluation time in days
        evaltime : np.ndarray
            Starting and end point of the evaluation time in days

        Returns
        -------
        me: float
            Float value of the aeration energy during the evaluation time in kWh/d
        mixenergyperd: int or float
            total mixing energy during the evaluation time in kWh/d
        """
        totalt = evaltime[1] - evaltime[0]

        kla1, kla2, kla3, kla4, kla5 = kla
        limit = 20
        me = (
            0.005
            * (
                len(kla1[kla1 < limit]) * vol[0]
                + len(kla2[kla2 < limit]) * vol[1]
                + len(kla3[kla3 < limit]) * vol[2]
                + len(kla4[kla4 < limit]) * vol[3]
                + len(kla5[kla5 < limit]) * vol[4]
            )
            * sampleinterval
            * 24
        )

        mixenergyunitad = 0.005  # 0.01 kW/m3 (Keller and Hartley, 2003)
        v_liq = adm1init.V_LIQ
        mixenergyad = 24 * mixenergyunitad * v_liq * totalt

        mixenergy = me + mixenergyad
        mixenergyperd = mixenergy / totalt

        return me, mixenergyperd

    @staticmethod
    def violation(arr_eff, limit, sampleinterval, evaltime):
        """Returns the time in days and percentage of time in which a certain component is over the limit value during
        the evaluation time

        Parameters
        ----------
        arr_eff: np.ndarray
            Concentration of the component in the effluent at every time step of the evaluation time
        limit: int or float
            limit value of the component
        sampleinterval : int or float
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
        violationvalues[0] = len(arr_eff[arr_eff > limit]) * sampleinterval
        # percentage of time the component is over the limit value:
        violationvalues[1] = len(arr_eff[arr_eff > limit]) * sampleinterval / (evaltime[1] - evaltime[0]) * 100
        return violationvalues

    @staticmethod
    def advanced_quantities(arr_eff, components=('kjeldahlN', 'totalN', 'COD', 'BOD5', 'X_TSS'), asm1par=asm1init.PAR1):
        """
        Takes an ASM1 array (single timestep or multiple timesteps) and returns
        advanced quantities of the effluent.
        Currently supports the following components:
        - `kjeldahlN`: Kjeldahl nitrogen
        - `totalN`: Total nitrogen
        - `COD`: Chemical oxygen demand
        - `BOD5`: Biological oxygen demand (5 days)
        - `X_TSS`:

        Parameters
        ----------
        arr_eff : np.ndarray((21, n))
            Array in ASM1 format
        components : List[str] (optional)
            List of components to be calculated. Defaults to ['kjeldahlN', 'totalN', 'COD', 'BOD5', 'X_TSS']
        """
        if np.ndim(arr_eff) == 1:
            adv_eff = np.zeros((len(components), 1))
        else:
            adv_eff = np.zeros((len(components), arr_eff.shape[1]))

        for idx, component in enumerate(components):
            if component == 'kjeldahlN':
                adv_eff[idx] = (
                    arr_eff[SNH]
                    + arr_eff[SND]
                    + arr_eff[XND]
                    + asm1par[17] * (arr_eff[XBH] + arr_eff[XBA])
                    + asm1par[18] * (arr_eff[XP] + arr_eff[XI])
                )
            elif component == 'totalN':
                adv_eff[idx] = (
                    arr_eff[SNH]
                    + arr_eff[SND]
                    + arr_eff[XND]
                    + asm1par[17] * (arr_eff[XBH] + arr_eff[XBA])
                    + asm1par[18] * (arr_eff[XP] + arr_eff[XI])
                    + arr_eff[SNO]
                )
            elif component == 'COD':
                adv_eff[idx] = (
                    arr_eff[SS] + arr_eff[SI] + arr_eff[XS] + arr_eff[XI] + arr_eff[XBH] + arr_eff[XBA] + arr_eff[XP]
                )
            elif component == 'BOD5':
                adv_eff[idx] = 0.65 * (arr_eff[SS] + arr_eff[XS] + (1 - asm1par[16]) * (arr_eff[XBH] + arr_eff[XBA]))
            elif component == 'X_TSS':
                adv_eff[idx] = 0.75 * (arr_eff[XS] + arr_eff[XP] + arr_eff[XI] + arr_eff[XBH] + arr_eff[XBA])
            else:
                err = f"Component '{component}' not supported"
                raise ValueError(err)

        return adv_eff

    def iqi(self, con_flow, step_time):
        """Returns the quality index based on the in put stream data

        Parameters
        ----------
        con_flow: np.ndarray(21)
            Influent array containing the values of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        sampleinterval : int or float
            Time step of the evaluation time in days


        Returns
        -------
        IQI: int or float
            the value of the quality index of the influent stream
        """

        # totalt = evaltime[1] - evaltime[0]

        imp_component = self.advanced_quantities(con_flow)

        tss = con_flow[13]
        cod = imp_component[2]
        snkj = imp_component[0]
        sno = con_flow[8]
        bod5 = imp_component[3]

        q = con_flow[14] * step_time

        iqivec = (self.BSS * tss + self.BCOD * cod + self.BNKj * snkj + self.BNO * sno + self.BBOD5 * bod5) * q

        iqi = iqivec / (1000)

        return iqi

    def eqi(self, con_flow, step_time):
        """Returns the quality index based on the in put stream data

        Parameters
        ----------
        con_flow: np.ndarray(21)
            Effluent array containing the values of the 21 components (13 ASM1 components, TSS, Q, T and 5 dummy states)
        sampleinterval : int or float
            Time step of the evaluation time in days


        Returns
        -------
        QI: int or float
            the value of the quality index of the effluent stream
        """

        # totalt = evaltime[1] - evaltime[0]

        imp_component = self.advanced_quantities(con_flow)

        tss = con_flow[13]
        cod = imp_component[2]
        snkj = imp_component[0]
        sno = con_flow[8]
        bod5 = imp_component[3] * (0.25 / 0.65)

        q = con_flow[14] * step_time

        eqivec = (self.BSS * tss + self.BCOD * cod + self.BNKj * snkj + self.BNO * sno + self.BBOD5 * bod5) * q

        eqi = eqivec / (1000)

        return eqi

    @staticmethod
    def sludge_production(
        y_out1_all,
        y_out2_all,
        y_out3_all,
        y_out4_all,
        y_out5_all,
        ys_r_all,
        ys_was_all,
        ys_of_all,
        yp_internal_all,
        yd_out_all,
        yst_out_all,
        yst_vol_all,
        ydw_s_all,
        y_eff_all,
        step_time,
        evaltime,
    ):
        """
        Returns the total sludge and TSS production per day

        Parameters
        ----------
        reactor1_out_all = np.ndarray(len(simtime), 21)
            Output array of reactor 1 containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        reactor2_out_all = np.ndarray(len(simtime),21)
            Output array of reactor 2 containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        reactor3_out_all = np.ndarray(len(simtime),21)
            Output array of reactor 3 containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        reactor4_out_all = np.ndarray(len(simtime),21)
            Output array of reactor 4 containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        reactor5_out_all = np.ndarray(len(simtime),21)
            Output array of reactor 5 containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        settler_yret_all = np.ndarray(len(simtime),21)
            Return stream of settler unite containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        settler_ywas_all = np.ndarray(len(simtime),21)
            Waste stream of settler unite containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        settler_yeff_all = np.ndarray(len(simtime),21)
            Effluent stream of settler unite containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        primaryClarifier_yuf_all = np.ndarray(len(simtime),21)
            Under flow of Primary Clarifier unite containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        primaryClarifier_yof_all = np.ndarray(len(simtime),21)
            Under flow of Primary Clarifier unite containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        yd_out_digester_all = np.ndarray(len(simtime),21)
            Output flow of digestor unite containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        storage_out_all = np.ndarray(len(simtime),21)
            Output flow of storage unite containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        storage_out_volrate_all = np.ndarray(len(simtime),2)
            Updated volume flow rate of output stream of storage unite,
            it contains to variable time and flow rate at all time steps

        dewatering_sludge_all = np.ndarray(len(simtime),21)
            Output flow of dewatering unite containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        y_eff_all = np.ndarray(len(simtime),21)
            Effluent stream containing the values of the 21 components
            (13 ASM1 components, TSS, Q, T and 5 dummy states) at all time steps

        step_time : int or float
            Time step of the evaluation time in days
        evaltime : np.ndarray
            Starting and end point of the evaluation time in days

        Returns
        -------
        Totsludgeprodperd: int or float
            the value of the total sludge produced per day

        TSSproducedperd: int or float
            the value of the total TSS produced per day
        """

        totalt = evaltime[1] - evaltime[0]

        tss_reactors_start = (
            y_out1_all[0, 13] * asm1init.VOL1
            + y_out2_all[0, 13] * asm1init.VOL2
            + y_out3_all[0, 13] * asm1init.VOL3
            + y_out4_all[0, 13] * asm1init.VOL4
            + y_out5_all[0, 13] * asm1init.VOL5
        ) / 1000

        tss_reactors_end = (
            y_out1_all[-1, 13] * asm1init.VOL1
            + y_out2_all[-1, 13] * asm1init.VOL2
            + y_out3_all[-1, 13] * asm1init.VOL3
            + y_out4_all[-1, 13] * asm1init.VOL4
            + y_out5_all[-1, 13] * asm1init.VOL5
        ) / 1000

        tss_settler_start = (
            (ys_r_all[0, 13] + ys_was_all[0, 13] + ys_of_all[0, 13])
            * ((settler1dinit.DIM[0] * settler1dinit.DIM[1]) / 10)
            / 1000
        )
        tss_settler_end = (
            (ys_r_all[-1, 13] + ys_was_all[-1, 13] + ys_of_all[-1, 13])
            * ((settler1dinit.DIM[0] * settler1dinit.DIM[1]) / 10)
            / 1000
        )

        tss_primary_start = (yp_internal_all[0, 13]) * primclarinit.VOL_P / 1000
        tss_primary_end = (yp_internal_all[-1, 13]) * primclarinit.VOL_P / 1000

        tss_digester_start = yd_out_all[0, 13] * adm1init.V_LIQ / 1000
        tss_digester_end = yd_out_all[-1, 13] * adm1init.V_LIQ / 1000

        tss_storage_start = yst_out_all[0, 13] * yst_vol_all[0, 0] / 1000
        tss_storage_end = yst_out_all[-1, 13] * yst_vol_all[-1, 0] / 1000

        tss_sludgeconc = ydw_s_all[:, 13] / 1000  # kg/m3
        qsludgeflow = ydw_s_all[:, 14]  # m3/d

        tss_sludgevec = np.multiply(tss_sludgeconc, qsludgeflow) * step_time
        tss_produced = (
            sum(tss_sludgevec)
            + tss_reactors_end
            + tss_settler_end
            + tss_primary_end
            + tss_digester_end
            + tss_storage_end
            - tss_reactors_start
            - tss_settler_start
            - tss_primary_start
            - tss_digester_start
            - tss_storage_start
        )

        tss_producedperd = tss_produced / totalt

        tss_evec = np.multiply(y_eff_all[:, 13], y_eff_all[:, 14]) * step_time
        tss_eload = sum(tss_evec)

        totsludgeprodperd = tss_produced / totalt + tss_eload / (1000 * totalt)

        return totsludgeprodperd, tss_producedperd

    @staticmethod
    def carbon_source(num_step, step_time, evaltime):
        """Returns the carbone source value per day

        Parameters
        ----------
        num_step: int or float
            number of time step
        step_time : int or float
            Time step of the evaluation time in days
        evaltime : np.ndarray
            Starting and end point of the evaluation time in days

        Returns
        -------
        carbonmassperd: int or float
            The value of the carbon source per day
        """

        totalt = evaltime[1] - evaltime[0]

        ones = np.ones(num_step)

        carbon1 = reginit.CARB1
        carbon2 = reginit.CARB2
        carbon3 = reginit.CARB3
        carbon4 = reginit.CARB4
        carbon5 = reginit.CARB5

        # carbon1 = 2
        # carbon2 = 0
        # carbon3 = 0
        # carbon4 = 0
        # carbon5 = 0

        carbon1vec = carbon1 * ones
        carbon2vec = carbon2 * ones
        carbon3vec = carbon3 * ones
        carbon4vec = carbon4 * ones
        carbon5vec = carbon5 * ones

        carbonsourceconc = reginit.CARBONSOURCECONC

        qcarbon = carbon1vec + carbon2vec + carbon3vec + carbon4vec + carbon5vec
        carbonmass = qcarbon * carbonsourceconc / 1000
        qcarbon = sum(qcarbon * step_time)  # m3
        carbonmass = sum(carbonmass * step_time)  # kg COD
        carbonmassperd = carbonmass / totalt  # for OCI

        return carbonmassperd

    @staticmethod
    def gas_production(digester_ydout, step_time, evaltime, p_atm=1.0130, t_op=308.15):
        """Returns the production of Methane, Hydrogen and Carbondioxide per day

        Parameters
        ----------
        digester_ydout: np.array (51)
            concentrations of 51 ADM1 components and
            gas phase parameters after the digester
            [S_su, S_aa, S_fa, S_va, S_bu, S_pro, S_ac, S_h2, S_ch4, S_IC, S_IN, S_I, X_xc,
             X_ch, X_pr, X_li, X_su, X_aa, X_fa, X_c4, X_pro, X_ac, X_h2, X_I, S_cat, S_an,
             Q_D, T_D, S_D1_D, S_D2_D, S_D3_D, X_D4_D, X_D5_D, pH, S_H_ion, S_hva, S_hbu,
             S_hpro, S_hac, S_hco3, S_CO2, S_nh3, S_NH4+, S_gas_h2, S_gas_ch4, S_gas_co2,
             p_gas_h2, p_gas_ch4, p_gas_co2, P_gas, q_gas]

        step_time : int or float
            Time step of the evaluation time in days

        evaltime : np.ndarray
            Starting and end point of the evaluation time in days

        P_atam: int or float
            atmospheric pressure, default 1.0130 atm

        T_op: int or float
            operation temperature, default 308.15 K


        Returns
        -------
        Methaneprodperd: int or float
            Methane production per day

        Hydrogenprodperd: int or float
            Hydrogen production per day

        Carbondioxideprodperd: int or float
            Carbon production per day

        Qgasav: int or float
            Total gas production per day
        """

        totalt = evaltime[1] - evaltime[0]

        r = 0.0831

        methanevec = (digester_ydout[:, 47] / digester_ydout[:, 49]) * p_atm * 16 / (r * t_op)
        methaneflowvec = np.multiply(methanevec, digester_ydout[:, 50])
        methaneprod = sum(methaneflowvec * step_time)
        methaneprodperd = methaneprod / totalt  # kg CH4/d

        hydrogenvec = (digester_ydout[:, 46] / digester_ydout[:, 49]) * p_atm * 2 / (r * t_op)
        hydrogenflowvec = np.multiply(hydrogenvec, digester_ydout[:, 50])
        hydrogenprod = sum(hydrogenflowvec * step_time)
        hydrogenprodperd = hydrogenprod / totalt  # kg H2/d

        carbondioxidevec = (digester_ydout[:, 48] / digester_ydout[:, 49]) * p_atm * 44 / (r * t_op)
        carbondioxideflow = np.multiply(carbondioxidevec, digester_ydout[:, 50])
        carbondioxideprod = sum(carbondioxideflow * step_time)
        carbondioxideprodperd = carbondioxideprod / totalt  # kg CO2/d

        qgas = digester_ydout[:, 50] * step_time
        qgastot = sum(qgas)
        qgasav = qgastot / totalt

        return methaneprodperd, hydrogenprodperd, carbondioxideprodperd, qgasav

    @staticmethod
    def heating_energy(primary_clarifier_yuf, thickener_yuf, step_time, evaltime):
        """Returns the net heating energy demand per day

        Parameters
        ----------
        primaryClarifier_yuf: np.ndarray(len(simtime),21)
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
    def oci(
        tss_producedperd,
        airenergyperd,
        mixenergyperd,
        pumpenergyperd,
        carbonmassperd,
        methaneprodperd,
        heatenergyperd,
    ):
        """Returns the net heating energy demand per day

        Parameters
        ----------
        TSSproducedperd: int or float
            Total TSS produced per day

        airenergyperd: int or float
            Total airation energy consumed per day

        airenergyperd: int or float
            Total mixing energy consumed per day

        pumpenergyperd: int or float
            Total pumping energy consumed per day

        carbonmassperd: int or float
            Total addtional carbon per day

        Methaneprodperd: int or float
            Total methane produced per day

        Heatenergyperd: int or float
            Total methane produced per day


        Returns
        -------
        OCI: int or float
            Operational Cost Index per day
        """

        # - Operational Cost Index (OCI) = 1 * pumpenergyperd
        #                         + 1 * airenergyperd
        #                         + 1 * mixenergyperd
        #                           3 * TSSproducedperd
        #                         + 3 * carbonmassperd
        #                         - 6 * Methaneproducedperd
        #                         + max(0,Heatenergyperd-7*Methaneproducedperd)

        tss_cost = 3 * tss_producedperd
        airenergycost = 1 * airenergyperd
        mixenergycost = 1 * mixenergyperd
        pumpenergycost = 1 * pumpenergyperd
        carbonmasscost = 3 * carbonmassperd
        energyfrommethaneperdcost = 6 * methaneprodperd
        heatenergycost = max(0, heatenergyperd - 7 * methaneprodperd)

        oci = (
            tss_cost
            + airenergycost
            + mixenergycost
            + pumpenergycost
            + carbonmasscost
            - energyfrommethaneperdcost
            + heatenergycost
        )

        return oci
