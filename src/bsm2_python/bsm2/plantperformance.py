import numpy as np

import bsm2_python.bsm2.asm1init_bsm2 as asm1init

indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components


class PlantPerformance:
    """
    Creates a PlantPerformance object.
    """

    def __init__(self):
        pass

    # TODO: Make the function also callable from within the simulation loop (i.e. only for one timestep).
    # Currently, it is only callable after the simulation.
    @staticmethod
    def aerationenergy(kla, vol, sosat, sampleinterval, evaltime):
        """
        Returns the aeration energy of the plant during the evaluation time.

        Parameters
        ----------
        kla : np.ndarray
            KLa values of all reactor compartments at every time step of the evaluation time.
        vol : np.ndarray
            Volume of each reactor compartment.
        sosat : np.ndarray
            Saturation concentration of oxygen in each reactor compartment.
        sampleinterval : int or float
            Time step of the evaluation time, in days.
        evaltime : np.ndarray
            Starting and end point of the evaluation time, in days.

        Returns
        -------
        ae : float
            Float value of the aeration energy during the evaluation time, in kWh/d.
        """

        ae = sum(sum(sosat * vol * kla) * sampleinterval) / (1.8 * 1000 * (evaltime[1] - evaltime[0]))
        return ae

    # TODO: Make the function also callable from within the simulation loop (i.e. only for one timestep).
    # Currently, it is only callable after the simulation.
    @staticmethod
    def pumpingenergy(flows, pumpfactor, sampleinterval, evaltime):
        """
        Returns the pumping energy of the plant during the evaluation time.

        Parameters
        ----------
        flows : np.ndarray
            Values of Qintr, Qr and Qw at every time step of the evaluation time.
        pumpfactor : np.ndarray
            Weighting factor of each flow.
        sampleinterval : int or float
            Time step of the evaluation time, in days.
        evaltime : np.ndarray
            Starting and end point of the evaluation time, in days.

        Returns
        -------
        pe : float
            Float value of the mixing energy during the evaluation time, in kWh/d.
        """

        pe = sum(sum(flows * pumpfactor) * sampleinterval) / (evaltime[1] - evaltime[0])
        return pe

    # TODO: Make the function also callable from within the simulation loop (i.e. only for one timestep).
    # Currently, it is only callable after the simulation.
    @staticmethod
    def mixingenergy(kla, vol, sampleinterval, evaltime):
        """
        Returns the mixing energy of the plant during the evaluation time.

        Parameters
        ----------
        kla : np.ndarray
            KLa values of all reactor compartments at every time step of the evaluation time.
        vol : np.ndarray
            Volume of each reactor compartment.
        sampleinterval : int or float
            Time step of the evaluation time, in days.
        evaltime : np.ndarray
            Starting and end point of the evaluation time, in days.

        Returns
        -------
        me : float
            Float value of the aeration energy during the evaluation time, in kWh/d.
        """

        kla1, kla2, kla3, kla4, kla5 = kla
        lim = 20
        me = (
            0.005
            * (
                len(kla1[kla1 < lim]) * vol[0]
                + len(kla2[kla2 < lim]) * vol[1]
                + len(kla3[kla3 < lim]) * vol[2]
                + len(kla4[kla4 < lim]) * vol[3]
                + len(kla5[kla5 < lim]) * vol[4]
            )
            * sampleinterval
            * 24
            / (evaltime[1] - evaltime[0])
        )
        return me[0]

    # TODO: Make the function also callable from within the simulation loop (i.e. only for one timestep).
    # Currently, it is only callable after the simulation.
    @staticmethod
    def violation(arr_eff, limit, sampleinterval, evaltime):
        """
        Returns the time in days and percentage of time in which a certain component is over the limit value during
        the evaluation time.

        Parameters
        ----------
        arr_eff : np.ndarray
            Concentration of the component in the effluent at every time step of the evaluation time.
        limit : int or float
            Limit value of the component.
        sampleinterval : int or float
            Time step of the evaluation time, in days.
        evaltime : np.ndarray
            Starting and end point of the evaluation time, in days.

        Returns
        -------
        violationvalues : np.ndarray(2)
            Array containing the time in days and percentage of time in which
            a certain component is over the limit value during the evaluation time.
        """

        violationvalues = np.zeros(2)
        # time in days the component is over the limit value:
        violationvalues[0] = len(arr_eff[arr_eff > limit]) * sampleinterval
        # percentage of time the component is over the limit value:
        violationvalues[1] = len(arr_eff[arr_eff > limit]) * sampleinterval / (evaltime[1] - evaltime[0]) * 100
        return violationvalues

    @staticmethod
    def advanced_quantities(arr_eff, components=('kjeldahlN', 'totalN', 'COD', 'BOD5'), asm1par=asm1init.PAR1):
        """
        Takes an ASM1 array (single timestep or multiple timesteps) and returns
        advanced quantities of the effluent.
        Currently supports the following components: \n
        - `kjeldahlN`: Kjeldahl nitrogen
        - `totalN`: Total nitrogen
        - `COD`: Chemical oxygen demand
        - `BOD5`: Biological oxygen demand (5 days)

        Parameters
        ----------
        arr_eff : np.ndarray((21, n))
            Array in ASM1 format.
        components : Tuple[str] (optional)
            Tuple of components to be calculated.
            Defaults to (`kjeldahlN`, `totalN`, `COD`, `BOD5`).

        Returns
        -------
        adv_eff : np.ndarray
            Advanced quantities of the effluent.
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
                adv_eff[idx] = 0.25 * (arr_eff[SS] + arr_eff[XS] + (1 - asm1par[16]) * (arr_eff[XBH] + arr_eff[XBA]))
            else:
                err_msg = f"Component '{component}' not supported"
                raise ValueError(err_msg)

        return adv_eff

    @staticmethod
    def air_flow(kla, temp, vol, h):
        """
        Calculates the air flow rate in each reactor compartment.

        Parameters
        ----------
        kla : float
            KLa values of each reactor compartment, in 1/d.
        temp : float
            Temperature in each reactor compartment, in °C.
        vol : float
            Volume of each reactor compartment, in m³.
        h : float
            Height of each reactor compartment, in m.

        Returns
        -------
        air_flow : float
            Air flow rate in each reactor compartment in m³/d
        """
        f_s_st = 1  # salinity aeration factor
        kla_20 = kla * 1.024 ** (20 - temp)
        beta_st = 1  # salinity saturation factor
        c_s_20 = 9.09  # mg/l from DIN EN ISO 5814
        alpha = 0.75
        ssote = 6.5  # %/m from DWA-M 229-1
        sotr = (vol * f_s_st * kla_20 * beta_st * c_s_20) / 1000 / alpha
        #       m³           * 1/d              * gO2/m³  / g/kg = kgO2/d
        oxygen_conc = 0.3  # kg/m³ in air
        air_flow = (100 * sotr) / (h * oxygen_conc * ssote)
        #            %  * kgO2/d/ (m * kg/m³       * %/m   = m³/d
        return air_flow
