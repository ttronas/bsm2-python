import sys
import os
import numpy as np
path_name = os.path.dirname(__file__)
sys.path.append(path_name + '/..')
import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init

indices_components = np.arange(21)
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = indices_components


class PlantPerformance:
    def __init__(self):
        """
        Creates a PlantPerformance object.
        """

    def aerationenergy(self, kla, vol, sosat):
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

        ae = sum(sosat * vol * kla) / (1.8 * 1000) / 24
        return ae

    def pumpingenergy(self, flows, pumpfactor):
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

    def mixingenergy(self, kla, vol):
        """Returns the mixing energy of the plant during the evaluation time

        Parameters
        ----------
        kla : np.ndarray
            KLa values of all reactor compartments at every time step of the evaluation time
        vol : np.ndarray
            Volume of each reactor compartment

        Returns
        -------
        float
            Float value of the aeration energy during the evaluation time in kW
        """

        me = 24 * 0.005 * np.sum((kla[i] < 20) * vol[i] for i in range(len(kla))).item() / 24

        return me

    def violation(self, arr_eff, limit, sampleinterval, evaltime):
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

    def advanced_quantities(self, arr_eff, components=['kjeldahlN', 'totalN', 'COD', 'BOD5'], asm1par=asm1init.PAR1):
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
        arr_eff : np.ndarray((21, n))
            Array in ASM1 format
        components : List[str] (optional)
            List of components to be calculated. Defaults to ['kjeldahlN', 'totalN', 'COD', 'BOD5']
        """
        if np.ndim(arr_eff) == 1:
            adv_eff = np.zeros((len(components), 1))
        else:
            adv_eff = np.zeros((len(components), arr_eff.shape[1]))

        for idx, component in enumerate(components):
            if component == 'kjeldahlN':
                adv_eff[idx] = arr_eff[SNH] + arr_eff[SND] + arr_eff[XND] + \
                    asm1par[17] * (arr_eff[XBH] + arr_eff[XBA]) + \
                    asm1par[18] * (arr_eff[XP] + arr_eff[XI])
            elif component == 'totalN':
                adv_eff[idx] = arr_eff[SNH] + arr_eff[SND] + arr_eff[XND] + \
                    asm1par[17] * (arr_eff[XBH] + arr_eff[XBA]) + \
                    asm1par[18] * (arr_eff[XP] + arr_eff[XI]) + arr_eff[SNO]
            elif component == 'COD':
                adv_eff[idx] = arr_eff[SS] + arr_eff[SI] + arr_eff[XS] + arr_eff[XI] + \
                    arr_eff[XBH] + arr_eff[XBA] + arr_eff[XP]
            elif component == 'BOD5':
                adv_eff[idx] = 0.25 * (arr_eff[SS] + arr_eff[XS] + (1-asm1par[16]) * (arr_eff[XBH] + arr_eff[XBA]))
            else:
                raise ValueError(f'Component \'{component}\' not supported')

        return adv_eff
