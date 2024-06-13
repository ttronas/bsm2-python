"""
Adjusts KLA values based on electricity prices and ammonia concentration in the effluent
"""
import os
import numpy as np
import csv

class ControllerOxygen:
    def __init__(
        self,
        timestep: float,
        price_percentile: float,
        klas_init: np.ndarray,
        KLA_reduction: float,
        S_NH_threshold: float,
    ):
        """
        Creates a Controller object.

        Parameters
        ----------
        timestep : float
            Time step of the simulation in fraction of a day
        electricity_prices : np.ndarray
            Electricity prices in €/MWh
        price_percentile : float
            Percentile of electricity prices used to adjust KLA values
        KLA_reduction : float
            Reduction factor for KLA values
        S_NH_threshold : float
            Maximum value of ammonia concentration in the effluent
        """
        self.timestep = timestep
        self.price_percentile = price_percentile
        self.klas_init = klas_init
        self.KLA_reduction = KLA_reduction
        self.S_NH_threshold = S_NH_threshold
        self.steps_per_day = round(1 / timestep)
        self.is_price_in_percentile = np.full(self.steps_per_day, False)
        path_name = os.path.dirname(__file__)
        with open(path_name + '/data/electricity_prices_2023.csv', encoding='utf-8-sig') as f:
            prices = []
            data = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)
            for price in data:
                prices.append(price[0])
            self.electricity_prices = np.array(prices).astype(np.float64)

    def get_klas(self, step: int, S_NH_reactors: np.ndarray):
        """
        Returns the KLA values for the reactor compartments.
        """
        step_in_day = step % self.steps_per_day
        # get hours with the highest electricity prices
        if step_in_day == 0:
            electricity_prices_day = self.electricity_prices[step: step + self.steps_per_day]
            steps_in_percentile = round(self.steps_per_day * (1 - self.price_percentile))
            indices_percentile = np.argpartition(electricity_prices_day, -steps_in_percentile)[-steps_in_percentile:]
            for i in range(self.steps_per_day):
                self.is_price_in_percentile[i] = i in indices_percentile

        klas = np.zeros(len(self.klas_init))
        for i, S_NH in enumerate(S_NH_reactors):
            if S_NH < self.S_NH_threshold and self.is_price_in_percentile[step_in_day]:
                klas[i] = self.klas_init[i] * self.KLA_reduction
            else:
                klas[i] = self.klas_init[i]

        return klas
