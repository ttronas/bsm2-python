"""A Module class that represents a generic gas management module."""

import numpy as np


class Module:
    def __init__(self) -> None:
        """
        A class that represents a generic gas management module.
        Contains the step method that is called in each time step.

        Children classes should implement the following methods:
        - check_failure
        - produce
        - consume
        - calculate_maintenance_time

        """
        self.global_time: float = 0.0
        self._runtime: float = 0.0
        self._remaining_maintenance_time: float = 0.0
        self._time_since_last_maintenance: float = 0.0
        self._under_maintenance: bool = False
        self._total_maintenance_time: float = 0.0
        self.maintenance_cost_per_hour: float = 0.0
        self.mttf: float = 0.0  # Mean Time To Failure
        self.mttr: float = 0.0  # Mean Time To Repair
        self._load: float = 0.0
        self._products: np.ndarray = np.array([0.0])
        self._consumption: np.ndarray = np.array([0.0])

    @property
    def runtime(self) -> float:
        return self._runtime

    @property
    def load(self) -> float:
        return self._load

    @load.setter
    def load(self, value: float) -> None:
        self._load = value

    @property
    def total_maintenance_time(self) -> float:
        return self._total_maintenance_time

    @total_maintenance_time.setter
    def total_maintenance_time(self, value: float) -> None:
        self._total_maintenance_time = value

    @property
    def remaining_maintenance_time(self) -> float:
        return self._remaining_maintenance_time

    @remaining_maintenance_time.setter
    def remaining_maintenance_time(self, value: float) -> None:
        self._remaining_maintenance_time = value
        if self._remaining_maintenance_time <= 0:
            self._remaining_maintenance_time = 0
            self._under_maintenance = False
            self._time_since_last_maintenance = 0.0
        else:
            self._under_maintenance = True
            self.load = 0.0

    @property
    def time_since_last_maintenance(self) -> float:
        return self._time_since_last_maintenance

    @property
    def under_maintenance(self) -> bool:
        return self._under_maintenance

    @under_maintenance.setter
    def under_maintenance(self, value: bool) -> None:
        self._under_maintenance = value

    @property
    def products(self) -> np.ndarray:
        return self._products

    @property
    def consumption(self) -> np.ndarray:
        return self._consumption

    def check_failure(self):
        """
        Checks if the module has failed.
        Returns:
            failed: bool, True if the module has failed, False otherwise
        """
        raise NotImplementedError('The check_failure method must be implemented by the child class.')

    def produce(self) -> np.ndarray:
        """
        Produces energy based on the load and time delta.
        Arguments:
            load: float, load as a value between 0 and 1
        Returns:
            products: list, list of products produced by the module
        """
        raise NotImplementedError('The produce method must be implemented by the child class.')

    def consume(self) -> np.ndarray:
        """
        Consumes energy based on the load and time delta.
        Arguments:
            load: float, load as a value between 0 and 1
        Returns:
            products: list, list of products consumed by the module
        """
        raise NotImplementedError('The consume method must be implemented by the child class.')

    def maintain(self, time_delta: float):
        """
        Maintains the module based on the time delta.
        Arguments:
            time_delta: float, time difference in hours
        """
        self.remaining_maintenance_time -= time_delta

    def calculate_maintenance_time(self) -> float:
        """
        Calculates the maintenance time of the module.
        Returns:
            maintenance_time: float, maintenance time in hours
        """
        raise NotImplementedError('The calculate_maintenance_time method must be implemented by the child class.')

    def report_status(self) -> np.ndarray:
        """
        Reports the status of the module.
        Returns:
            status: list, list of status parameters
        """
        status = [
            self.load,
            self._remaining_maintenance_time,
            *self._products,
            *self._consumption,
        ]
        return np.array(status)

    def step(self, time_delta: float):
        """
        Updates the module based on the load and time delta.
        Arguments:
            time_delta: float, time difference in hours
        """
        self.global_time += time_delta
        if not self._under_maintenance:
            if self.check_failure():
                self.remaining_maintenance_time = self.calculate_maintenance_time()
                self._total_maintenance_time += self.remaining_maintenance_time
                self.maintain(time_delta)
                self._products = np.zeros_like(self.products)
                self._consumption = np.zeros_like(self.consumption)
            else:
                self._time_since_last_maintenance += time_delta
                self._runtime += time_delta
                self._products = self.produce()
                self._consumption = self.consume()
        else:
            self.maintain(time_delta)
            self._products = np.zeros_like(self.products)
            self._consumption = np.zeros_like(self.consumption)
