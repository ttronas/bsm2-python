from bsm2_python.bsm2.adm1_bsm2 import ADM1Reactor


class ADM1Performance:
    def __init__(self, adm1_obj: ADM1Reactor):
        self.dim = adm1_obj.dim
        self.hydrogen_concentration = 0
        self.methane_concentration = 0
        self.carbon_dioxide_concentration = 0

    def energy_consumption(self, t_new, t_old, rho_h2o=997, cp_h2o=4182):
        """
        Energy needed to heat up the reactor from t_old to t_new.

        Parameters
        ----------
        t_new : float
            The new temperature of the reactor.
        t_old : float
            The old temperature of the reactor.
        rho_h2o : float
            The density of water in kg/m3.
        cp_h2o : float
            The specific heat capacity of water in J/kgK.

        Returns
        -------
        float
            Energy needed to heat up the reactor [kWh].
        """
        vol_reactor = self.dim[0]
        # Q = mcΔT
        heat_in_joules = rho_h2o * vol_reactor * cp_h2o * (t_new - t_old)
        heat_in_kwh = heat_in_joules / (3600 * 1000)  # Convert from joules to kilowatts

        return heat_in_kwh

    def reactor_temperature(self, heat_in_kwh, t_old, rho_h2o=997, cp_h2o=4182):
        """
        Calculate the temperature of the reactor after the energy is added to the reactor.

        Parameters
        ----------
        heat_in_kwh : float
            Energy needed to heat up the reactor [kWh].
        t_old : float
            The old temperature of the reactor.
        rho_h2o : float
            The density of water in kg/m3.
        cp_h2o : float
            The specific heat capacity of water in J/kgK.

        Returns
        -------
        float
            The new temperature of the reactor.
        """
        vol_reactor = self.dim[0]
        t_new = t_old + (heat_in_kwh * 3600 * 1000) / (rho_h2o * vol_reactor * cp_h2o)
        return t_new

    def biogas_productions(self, hydrogen_concentration, methane_concentration, carbon_dioxide_concentration):
        """
        Calculate the total biogas production from the ADM1 reactor based on the last output.
        Parameters
        ----------
        hydrogen_concentration mol/m3: float
            Hydrogen concentration in the biogas.
        methane_concentration mol/m3: float
            Methane concentration in the biogas.
        carbon_dioxide_concentration mol/m3 : float
            Carbon dioxide concentration in the biogas.


        Returns
        -------
        float
            Total biogas production in terms of kwh
        """
        # convert the concentration to kg/m3
        hydrogen_concentration = hydrogen_concentration * 2.016 / 1000
        methane_concentration = methane_concentration * 16.04 / 1000
        carbon_dioxide_concentration = carbon_dioxide_concentration * 44.01 / 1000
        # calculate the total energy in the biogas
        self.hydrogen_concentration = hydrogen_concentration
        self.methane_concentration = methane_concentration
        self.carbon_dioxide_concentration = carbon_dioxide_concentration
        methane_lhv = 890  # [kWh/kg]
        hydrogen_lhv = 33  # [kWh/kg]
        total_energy_kwh = (
            self.hydrogen_concentration * hydrogen_lhv + self.methane_concentration * methane_lhv
        ) * self.dim[1]
        return total_energy_kwh
