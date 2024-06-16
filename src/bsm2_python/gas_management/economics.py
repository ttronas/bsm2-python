import csv
import os

import numpy as np

from bsm2_python.gas_management.boiler import Boiler
from bsm2_python.gas_management.chp import CHP
from bsm2_python.gas_management.compressor import Compressor
from bsm2_python.gas_management.cooler import Cooler
from bsm2_python.gas_management.fermenter import Fermenter
from bsm2_python.gas_management.flare import Flare
from bsm2_python.gas_management.heat_net import HeatNet
from bsm2_python.gas_management.storage import BiogasStorage

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
            data = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)
            for price in data:
                prices.append(price[0])
            self.electricity_prices = np.array(prices).astype(np.float64)
        self.cum_cash_flow = 0

    @staticmethod
    def calculate_debt_payment_timestep(time_diff: float, investment: float):
        return investment * ANNUITY / (HOURS_IN_YEAR / time_diff)

    def get_debt_payment(self, time_diff: float):  # additional to existing wwtp -> electrolyzer, methanation, storages
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
        return 0

    def get_total_capex(self, time_diff: float):
        return self.get_debt_payment(time_diff)

    def get_total_opex(self, time_diff: float):
        return (
            self.get_maintenance_costs(time_diff) + self.get_insurance_costs(time_diff) + self.get_staff_cost(time_diff)
        )

    def get_income(self, net_electricity_wwtp, step, time_diff):
        income = 0
        if net_electricity_wwtp < 0 and self.electricity_prices[step] > 0:
            income = -net_electricity_wwtp * self.electricity_prices[step] * time_diff
        elif net_electricity_wwtp > 0 and self.electricity_prices[step] < 0:
            income = net_electricity_wwtp * -self.electricity_prices[step] * time_diff
        self.cum_cash_flow += income
        return income

    def get_expenditures(self, net_electricity_wwtp, step, time_diff):
        expenditure_capex = self.get_total_capex(time_diff)
        expenditure_opex = self.get_total_opex(time_diff)
        expenditure_electricity = 0
        if net_electricity_wwtp > 0 and self.electricity_prices[step] > 0:
            expenditure_electricity = net_electricity_wwtp * self.electricity_prices[step] * time_diff
        elif net_electricity_wwtp < 0 and self.electricity_prices[step] < 0:
            expenditure_electricity = net_electricity_wwtp * self.electricity_prices[step] * time_diff
        self.cum_cash_flow -= expenditure_capex + expenditure_opex + expenditure_electricity
        return expenditure_capex + expenditure_opex + expenditure_electricity
