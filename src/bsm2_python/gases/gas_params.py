from typing import ClassVar


class GasParams:
    """
    Class containing the physical properties of gases used in the model.
    """

    O2: ClassVar[dict] = {
        'mole': 0.032,  # kg/mol
        'rho_l': 24.0,  # kg/m3
        'rho_norm': 1.429,  # kg/m3
        'cp': 0.912,  # kJ/kg/K from https://www.chemie.de/lexikon/Spezifische_W%C3%A4rmekapazit%C3%A4t.html
        'kappa': 1.40,
        # from https://www.powderprocess.net/Tools_html/Data_Diagrams/Tools_isentropic_coefficients.html
    }
    H2O: ClassVar[dict] = {
        'mole': 0.018,  # kg/mol
        'rho_l': 1000,  # kg/m³
        'cp_l': 4.186,  # kJ/kg/K
        'h_evap_5bar': 2104.09,  # kJ/kg
        'h_evap_10bar': 2014.9,  # kJ/kg
        'h_8bar': 2652.23,  # kJ/kg
        'kappa': 1.33,
        # from https://www.powderprocess.net/Tools_html/Data_Diagrams/Tools_isentropic_coefficients.html
    }
    H2: ClassVar[dict] = {
        'h_o': 3.542,  # kWh/Nm^3 upper (german: "oberer") heating value
        'h_u': 2.994,  # kWh/Nm^3 lower (german: "unterer") heating value
        'mole': 0.002016,  # kg/mol
        'rho_norm': 0.08988,  # kg/Nm^3
        'cp': 14.4,  # kJ/kg/K from https://www.chemie.de/lexikon/Spezifische_W%C3%A4rmekapazit%C3%A4t.html
        'kappa': 1.41,
        # from https://www.powderprocess.net/Tools_html/Data_Diagrams/Tools_isentropic_coefficients.html
        # "v_dot": o2_sun["cons"]*8760*2
        # Nm^3/a minimum H2 production of electrolyzer **per year!** in order to meet the O2 demand
    }

    CH4: ClassVar[dict] = {
        'h_o': 11.06,  # kWh/Nm^3
        'h_u': 9.97,  # kWh/Nm^3
        'rho_norm': 0.72,  # kg/Nm^3
        'mole': 0.016,  # kg/mol
        'cp': 2.226,  # kJ/kg/K
        'kappa': 1.31,
        # from https://www.powderprocess.net/Tools_html/Data_Diagrams/Tools_isentropic_coefficients.html
    }

    CO2: ClassVar[dict] = {
        'rho_norm': 1.98,  # kg/Nm^3
        'cp': 0.846,  # kJ/kg/K
        'mole': 0.0441,  # kg/mol
        'kappa': 1.30,
        # from https://www.powderprocess.net/Tools_html/Data_Diagrams/Tools_isentropic_coefficients.html
    }

    N2: ClassVar[dict] = {
        'mole': 0.0147,  # kg/mol
        'rho_norm': 1.25,  # kg/Nm^3
        'cp': 1.04,  # kJ/kg/K
        'kappa': 1.40,
        # from https://www.powderprocess.net/Tools_html/Data_Diagrams/Tools_isentropic_coefficients.html
    }

    BIOGAS: ClassVar[dict] = {'ch4_frac': 0.6}  # fraction of CH4 in Biogas
    BIOGAS['co2_frac'] = 1 - BIOGAS['ch4_frac']


GAS_PARAMS = GasParams()
