import numpy as np

class PlantPerformance:
    def aerationenergy(self, kla, vol, sosat, sampleinterval, evaltime):
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

        ae = sum(sum(sosat * vol * kla)*sampleinterval)/(1.8*1000 * (evaltime[1]-evaltime[0]))
        return ae


    def pumpingenergy(self, flows, pumpfactor, sampleinterval, evaltime):
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

        pe = sum(sum(flows * pumpfactor) * sampleinterval) / (evaltime[1] - evaltime[0])
        return pe


    def mixingenergy(self, kla, vol, sampleinterval, evaltime):
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
        float
            Float value of the aeration energy during the evaluation time in kWh/d
        """

        kla1, kla2, kla3, kla4, kla5 = kla
        me = 0.005 * (len(kla1[kla1 < 20])*vol[0] + len(kla2[kla2 < 20])*vol[1] + len(kla3[kla3 < 20])*vol[2] + len(kla4[kla4 < 20])*vol[3] + len(kla5[kla5 < 20])*vol[4]) * sampleinterval * 24 / (evaltime[1] - evaltime[0])
        return me[0]


    def violation(self, array_eff, limit, sampleinterval, evaltime):
        """Returns the time in days and percentage of time in which a certain component is over the limit value during
        the evaluation time

        Parameters
        ----------
        array_eff: np.ndarray
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
            Array containing the time in days and percentage of time in which a certain component is over the limit value
            during the evaluation time
        """

        violationvalues = np.zeros(2)
        # time in days the component is over the limit value:
        violationvalues[0] = len(array_eff[array_eff > limit]) * sampleinterval
        # percentage of time the component is over the limit value:
        violationvalues[1] = len(array_eff[array_eff > limit]) * sampleinterval / (evaltime[1] - evaltime[0]) * 100
        return violationvalues

