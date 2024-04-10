
from bsm2.adm1_bsm2 import ADM1Reactor

class ADM1Performance:
    def __init__(self, adm1_obj:ADM1Reactor):
        self.dim = adm1_obj.dim


    def energy_consumption(self, T_new, T_old ,rho_H2O=997, cp_H2O=4182):
        """
        Energy needed to heat up the reactor from T_old to T_new.
        Returns the energy consumption of the reactor in kW.
        """
        vol_reactor = self.dim[0]
        #Q = mcΔT
        heat_in_joules = (rho_H2O * vol_reactor * cp_H2O * (T_new - T_old))
        heat_in_kWh = heat_in_joules / (3600 * 1000)  # Convert from joules to kilowatts

        return heat_in_kWh


    def reactor_temperature(self, heat_in_kWh, T_old, rho_H2O=997, cp_H2O=4182):
        """
        Calculate the temperature of the reactor after the energy is added to the reactor.
        """
        vol_reactor = self.dim[0]
        T_new = T_old + (heat_in_kWh * 3600 * 1000) / (rho_H2O * vol_reactor * cp_H2O)
        return T_new



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
        #convert the concentration to kg/m3
        hydrogen_concentration = hydrogen_concentration * 2.016 /1000
        methane_concentration = methane_concentration * 16.04 / 1000
        carbon_dioxide_concentration = carbon_dioxide_concentration * 44.01 / 1000
        # calculate the total energy in the biogas
        self.hydrogen_concentration = hydrogen_concentration 
        self.methane_concentration = methane_concentration
        self.carbon_dioxide_concentration = carbon_dioxide_concentration
        methane_LHV= 890 # [kWh/kg]
        Hydrogen_LHV= 33 #[kWh/kg] 
        total_energy_kwh = (self.hydrogen_concentration * Hydrogen_LHV + self.methane_concentration * methane_LHV) * self.dim[1]
        return total_energy_kwh