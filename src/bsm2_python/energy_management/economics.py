import csv
import os

import numpy as np

from bsm2_python.energy_management.boiler import Boiler
from bsm2_python.energy_management.chp import CHP
from bsm2_python.energy_management.compressor import Compressor
from bsm2_python.energy_management.cooler import Cooler
from bsm2_python.energy_management.fermenter import Fermenter
from bsm2_python.energy_management.flare import Flare
from bsm2_python.energy_management.heat_net import HeatNet
from bsm2_python.energy_management.storage import BiogasStorage

path_name = os.path.dirname(__file__)

TAX_RATE = 0.25
DEBT_RATIO = 1
BANK_INTEREST_RATE = 0.035
PAYBACK_TIME = 20
ANNUITY = (
    BANK_INTEREST_RATE * ((1 + BANK_INTEREST_RATE) ** PAYBACK_TIME) / (((1 + BANK_INTEREST_RATE) ** PAYBACK_TIME) - 1)
)
MAINTENANCE_COST = 0.01  # % of investment costs
MAINTENANCE_PV = 0.02  # % of investment costs
INSURANCE_COST = 0.005  # % of investment costs
STAFF_COST = 80000  # €/a per person
HOURS_IN_YEAR = 8760
planning_permit_certificate = 0.1  # Planung, Genehmigung, Gutachten 10% CAPEX, source: eta excel
reserve = 0.05  # 5% CAPEX, source: eta excel


class Economics:
    def __init__(
        self,
        chps: list[CHP],
        boilers: list[Boiler],
        biogas_storage: BiogasStorage,
        biogas_compressor: Compressor,
        fermenter: Fermenter,
        flare: Flare,
        heat_net: HeatNet,
        cooler: Cooler,
    ):
        """
        A class that represents the economic aspects of the energy management.

        Parameters
        ----------
        chps : list[CHP]
            A list of CHPs in the system
        boilers : list[Boiler]
            A list of boilers in the system
        biogas_storage : BiogasStorage
            The biogas storage in the system
        biogas_compressor : Compressor
            The biogas compressor in the system
        fermenter : Fermenter
            The fermenter in the system
        flare : Flare
            The flare in the system
        heat_net : HeatNet
            The heat net in the system
        cooler : Cooler
            The cooler in the system
        """
        self.chps = chps
        self.boilers = boilers
        self.biogas_storage = biogas_storage
        self.biogas_compressor = biogas_compressor
        self.fermenter = fermenter
        self.flare = flare
        self.heat_net = heat_net
        self.cooler = cooler
        with open(path_name + '/../data/electricity_prices_2023.csv', encoding='utf-8-sig') as f:
            prices = []
            price_times = []
            data = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)
            for price in data:
                prices.append(price[1])
                price_times.append(price[0])
            self.electricity_prices = np.array(prices).astype(np.float64)
            self.price_times = np.array(price_times).astype(np.float64)
        self.cum_cash_flow = 0

    @staticmethod
    def calculate_debt_payment_timestep(time_diff: float, investment: float):
        """
        Calculates the debt payment for a specific investment in the current timestep.

        Parameters
        ----------
        time_diff : float
            The time difference between the timesteps [h]
        investment : float
            The investment costs [€]

        Returns
        -------
        float
            The debt payment for the timestep [€]
        """
        return investment * ANNUITY / (HOURS_IN_YEAR / time_diff)

    def get_debt_payment(self, time_diff: float):
        """
        Returns the debt payment for the current timestep.

        Parameters
        ----------
        time_diff : float
            The time difference between the timesteps [h]

        Returns
        -------
        float
            The total debt payment for the timestep [€]
        """
        payment_chps = np.sum([self.calculate_debt_payment_timestep(time_diff, chp.capex) for chp in self.chps])
        payment_boilers = np.sum(
            [self.calculate_debt_payment_timestep(time_diff, boiler.capex) for boiler in self.boilers]
        )
        payment_biogas_storage = self.calculate_debt_payment_timestep(time_diff, self.biogas_storage.capex)
        payment_biogas_compressor = self.calculate_debt_payment_timestep(time_diff, self.biogas_compressor.capex)
        payment_flare = self.calculate_debt_payment_timestep(time_diff, self.flare.capex)
        payment_cooler = self.calculate_debt_payment_timestep(time_diff, self.cooler.capex)

        investment_total = (
            np.sum([chp.capex for chp in self.chps])
            + np.sum([boiler.capex for boiler in self.boilers])
            + self.biogas_storage.capex
            + self.biogas_compressor.capex
            + self.flare.capex
            + self.cooler.capex
        )
        payment_planning = self.calculate_debt_payment_timestep(
            time_diff, planning_permit_certificate * investment_total
        )
        payment_reserve = self.calculate_debt_payment_timestep(time_diff, reserve * investment_total)

        return (
            payment_chps
            + payment_boilers
            + payment_biogas_storage
            + payment_biogas_compressor
            + payment_flare
            + payment_cooler
            + payment_planning
            + payment_reserve
        )

    def get_maintenance_costs(self, time_diff: float):
        """
        Returns the maintenance costs for the current timestep.

        Parameters
        ----------
        time_diff : float
            The time difference between the timesteps [h]

        Returns
        -------
        float
            The total maintenance costs for the timestep [€]
        """
        maintenance_chps = np.sum([chp.capex * MAINTENANCE_COST / (HOURS_IN_YEAR / time_diff) for chp in self.chps])
        maintenance_boilers = np.sum(
            [boiler.capex * MAINTENANCE_COST / (HOURS_IN_YEAR / time_diff) for boiler in self.boilers]
        )
        maintenance_biogas_storage = self.biogas_storage.capex * MAINTENANCE_COST / (HOURS_IN_YEAR / time_diff)
        maintenance_biogas_compressor = self.biogas_compressor.capex * MAINTENANCE_COST / (HOURS_IN_YEAR / time_diff)
        maintenance_flare = self.flare.capex * MAINTENANCE_COST / (HOURS_IN_YEAR / time_diff)
        maintenance_cooler = self.cooler.capex * MAINTENANCE_COST / (HOURS_IN_YEAR / time_diff)

        total_maintenance = (
            maintenance_chps
            + maintenance_boilers
            + maintenance_biogas_storage
            + maintenance_biogas_compressor
            + maintenance_flare
            + maintenance_cooler
        )

        return total_maintenance

    def get_insurance_costs(self, time_diff: float):
        """
        Returns the insurance costs for the current timestep.

        Parameters
        ----------
        time_diff : float
            The time difference between the timesteps [h]

        Returns
        -------
        float
            The total insurance costs for the timestep [€]
        """
        insurance_chps = np.sum([chp.capex * INSURANCE_COST / (HOURS_IN_YEAR / time_diff) for chp in self.chps])
        insurance_boilers = np.sum(
            [boiler.capex * INSURANCE_COST / (HOURS_IN_YEAR / time_diff) for boiler in self.boilers]
        )
        insurance_biogas_storage = self.biogas_storage.capex * INSURANCE_COST / (HOURS_IN_YEAR / time_diff)
        insurance_biogas_compressor = self.biogas_compressor.capex * INSURANCE_COST / (HOURS_IN_YEAR / time_diff)
        insurance_flare = self.flare.capex * INSURANCE_COST / (HOURS_IN_YEAR / time_diff)
        insurance_cooler = self.cooler.capex * INSURANCE_COST / (HOURS_IN_YEAR / time_diff)

        total_insurance = (
            insurance_chps
            + insurance_boilers
            + insurance_biogas_storage
            + insurance_biogas_compressor
            + insurance_flare
            + insurance_cooler
        )

        return total_insurance

    @staticmethod
    def get_staff_cost(time_diff: float):
        """
        Returns the staff costs for the current timestep.
        (Currently not implemented)

        Parameters
        ----------
        time_diff : float
            The time difference between the timesteps [h]

        Returns
        -------
        float
            The total staff costs for the timestep [€]
        """
        return 0

    def get_total_capex(self, time_diff: float):
        """
        Returns the total capital expenditure for the current timestep by calling all capex related functions.

        Parameters
        ----------
        time_diff : float
            The time difference between the timesteps [h]

        Returns
        -------
        float
            The total capital expenditure for the timestep [€]
        """
        if time_diff == 0:
            return 0
        return self.get_debt_payment(time_diff)

    def get_total_opex(self, time_diff: float):
        """
        Returns the total operational expenditure for the current timestep by calling all opex related functions.

        Parameters
        ----------
        time_diff : float
            The time difference between the timesteps [h]

        Returns
        -------
        float
            The total operational expenditure for the timestep [€]
        """
        if time_diff == 0:
            return 0

        return (
            self.get_maintenance_costs(time_diff) + self.get_insurance_costs(time_diff) + self.get_staff_cost(time_diff)
        )

    def get_income(self, net_electricity_wwtp, simtime, idx):
        """
        Returns the income for the current timestep.

        Parameters
        ----------
        net_electricity_wwtp : float
            The electricity bought from the grid minus the electricity sold to the grid [kWh]
        simtime : np.ndarray
            The simulation time array [h]
        idx : int
            The simulation time index

        Returns
        -------
        float
            The income for the timestep [€]
        """
        income = 0
        time_diff = simtime[idx] if idx == 0 else simtime[idx] - simtime[idx - 1]

        el_price_idx = np.argmin(np.abs(self.price_times - simtime[idx]))
        if net_electricity_wwtp < 0 and self.electricity_prices[el_price_idx] > 0:
            income = -net_electricity_wwtp * self.electricity_prices[el_price_idx] * time_diff
        elif net_electricity_wwtp > 0 and self.electricity_prices[el_price_idx] < 0:
            income = net_electricity_wwtp * -self.electricity_prices[el_price_idx] * time_diff
        self.cum_cash_flow += income
        return income

    def get_expenditures(self, net_electricity_wwtp, simtime, idx):
        """
        Returns the expenditures for the current timestep.

        Parameters
        ----------
        net_electricity_wwtp : float
            The electricity bought from the grid minus the electricity sold to the grid [kWh]
        simtime : np.ndarray
            The simulation time array [h]
        idx : int
            The simulation time index

        Returns
        -------
        float
            The expenditures for the timestep [€]
        """
        time_diff = simtime[idx] if idx == 0 else simtime[idx] - simtime[idx - 1]
        el_price_idx = np.argmin(np.abs(self.price_times - simtime[idx]))
        expenditure_capex = self.get_total_capex(time_diff)
        expenditure_opex = self.get_total_opex(time_diff)
        expenditure_electricity = 0
        if net_electricity_wwtp > 0 and self.electricity_prices[el_price_idx] > 0:
            expenditure_electricity = net_electricity_wwtp * self.electricity_prices[el_price_idx] * time_diff
        elif net_electricity_wwtp < 0 and self.electricity_prices[el_price_idx] < 0:
            expenditure_electricity = net_electricity_wwtp * self.electricity_prices[el_price_idx] * time_diff
        self.cum_cash_flow -= expenditure_capex + expenditure_opex + expenditure_electricity
        return expenditure_capex + expenditure_opex + expenditure_electricity
