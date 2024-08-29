"""
Adjusts KLA values based on electricity prices and ammonia concentration in the effluent
"""

import csv
import math
import os

import numpy as np


class Controller:
    def __init__(
        self,
        price_percentile: float,
        klas_init: np.ndarray,
        kla_reduction: float,
        s_nh_threshold: float,
        elec_price_path: str | None = None,
    ):
        """
        Creates a Controller object.

        Parameters
        ----------
        price_percentile : float
            Percentile of electricity prices used to adjust KLA values (aeration reduction at prices above the
            percentile, e.g. 0.9 -> aerate less when electricity prices are in the top 10%)
        klas_init : np.ndarray
            Initial KLA values for the reactor compartments [1/d]
        kla_reduction : float
            Reduction factor for KLA values
        s_nh_threshold : float
            Maximum value of ammonia concentration in the effluent [g/m3]
        """
        self.price_percentile = price_percentile
        self.klas_init = klas_init
        self.kla_reduction = kla_reduction
        self.s_nh_threshold = s_nh_threshold
        self.is_price_in_percentile: list[float] = []
        path_name = os.path.dirname(__file__)
        if elec_price_path is None:
            self.elec_price_path = path_name + '/data/electricity_prices_2023.csv'
        else:
            self.elec_price_path = elec_price_path
        with open(self.elec_price_path, encoding='utf-8-sig') as f:
            prices = []
            price_times = []
            data = np.array(list(csv.reader(f, delimiter=','))).astype(np.float64)
            for price in data:
                prices.append(price[1])
                price_times.append(price[0])
            self.electricity_prices = np.array(prices).astype(np.float64)
            self.price_times = np.array(price_times).astype(np.float64)

    def get_klas(self, step_simtime: float, s_nh_eff: np.ndarray):
        """
        Calculates and returns the KLA values for the reactor compartments based on electricity prices and ammonia
        concentration.

        Parameters
        ----------
        step_simtime : int
            Current timestamp in the simtime of the simulation
        s_nh_eff : float
            Ammonia concentration in the plant effluent [g/m3]

        Returns
        -------
        np.ndarray
            KLA values for the reactor compartments [1/d]
            [kla_reactor1, kla_reactor2, ...]
        """
        # necessary to deal with floating point errors
        eps = 1e-8
        step_day_start = np.where(self.price_times - math.floor(step_simtime + eps) <= 0)[0][-1]
        step_day_end = np.where(self.price_times - math.floor(step_simtime + eps + 1) <= 0)[0][-1]
        steps_day = step_day_end - step_day_start
        step_in_day = np.where(self.price_times - (step_simtime + eps) <= 0)[0][-1] - step_day_start

        # get hours with the highest electricity prices at start of day
        if step_in_day == 0:
            self.is_price_in_percentile.clear()
            electricity_prices_day = self.electricity_prices[step_day_start:step_day_end]
            steps_in_percentile = round(steps_day * (1 - self.price_percentile))
            indices_percentile = np.argpartition(electricity_prices_day, -steps_in_percentile)[-steps_in_percentile:]
            for i, _ in enumerate(electricity_prices_day):
                self.is_price_in_percentile.append(i in indices_percentile)
            # add one more step to the end of the day to avoid index out of bounds
            self.is_price_in_percentile.append(False)

        if self.s_nh_threshold > s_nh_eff and self.is_price_in_percentile[step_in_day]:
            klas = self.klas_init * self.kla_reduction
        else:
            klas = self.klas_init

        return klas
