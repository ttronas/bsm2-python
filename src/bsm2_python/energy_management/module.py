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
        self.load_change_time: float = 0.0
        self._remaining_load_change_time: float = 0.0
        self._previous_load: float = 0.0
        self._ready_to_change_load: bool = True
        self._load: float = 0.0
        self._products: np.ndarray = np.array([0.0])
        self._consumption: np.ndarray = np.array([0.0])

    @property
    def runtime(self) -> float:
        """
        Return the runtime of the module.

        Returns
        -------
        float
            Runtime of the module [hours]
        """
        return self._runtime

    @property
    def load(self) -> float:
        """
        Return the load of the module.

        Returns
        -------
        float
            Load of the module
        """
        return self._load

    @load.setter
    def load(self, value: float) -> None:
        """
        Sets the load of the module.

        Parameters
        ----------
        value : float
            Load of the module
        """
        self._load = value

    @property
    def total_maintenance_time(self) -> float:
        """
        Return the total maintenance time of the module.

        Returns
        -------
        float
            Total maintenance time of the module [hours]
        """
        return self._total_maintenance_time

    @total_maintenance_time.setter
    def total_maintenance_time(self, value: float) -> None:
        """
        Sets the total maintenance time of the module.

        Parameters
        ----------
        value : float
            Total maintenance time of the module [hours]
        """
        self._total_maintenance_time = value

    @property
    def remaining_maintenance_time(self) -> float:
        """
        Return the remaining maintenance time of the module.

        Returns
        -------
        float
            Remaining maintenance time of the module [hours]
        """
        return self._remaining_maintenance_time

    @remaining_maintenance_time.setter
    def remaining_maintenance_time(self, value: float) -> None:
        """
        Sets the remaining maintenance time and the maintenance status of the module.
        """
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
        """
        Return the time since the last maintenance of the module.

        Returns
        -------
        float
            Time since the last maintenance of the module [hours]
        """
        return self._time_since_last_maintenance

    @property
    def under_maintenance(self) -> bool:
        """
        Return the maintenance status of the module.

        Returns
        -------
        bool
            True if the module is under maintenance, False otherwise
        """
        return self._under_maintenance

    @under_maintenance.setter
    def under_maintenance(self, value: bool) -> None:
        """
        Sets maintenance status of the module.

        Parameters
        ----------
        value : bool
            Maintenance status of the module
        """
        self._under_maintenance = value

    @property
    def ready_to_change_load(self) -> bool:
        """
        Return weather the module is ready to change load.

        Returns
        -------
        bool
            True if the module is ready to change load, False otherwise
        """
        return self._ready_to_change_load

    @property
    def products(self) -> np.ndarray:
        """
        Returns the products of the module.

        Returns
        -------
        np.ndarray
            Products of the module
            [products]
        """
        return self._products

    @property
    def consumption(self) -> np.ndarray:
        """
        Returns the consumption of the module.

        Returns
        -------
        np.ndarray
            Consumption of the module
            [consumption]
        """
        return self._consumption

    def check_failure(self):
        """
        Checks if the module has failed.

        Returns
        -------
        bool
            True if the module has failed, False otherwise
        """
        raise NotImplementedError('The check_failure method must be implemented by the child class.')

    def check_load_change(self):
        """
        Checks if the module has changed its load in the previous timestep.

        Returns
        -------
        bool
            True if the module has been shut down, False otherwise
        """
        return self._load != self._previous_load

    def reduce_remaining_load_change_time(self, time_delta: float):
        """
        Reduces the remaining load change time based on the time delta.

        Parameters
        ----------
        time_delta : float
            time difference [hours]
        """
        self._remaining_load_change_time = max(self._remaining_load_change_time - time_delta, 0)

    def check_ready_for_load_change(self):
        """
        Checks if the module is ready to change load.

        Returns
        -------
        bool
            True if the module is ready to change load, False otherwise
        """
        return self._remaining_load_change_time <= 0

    def produce(self) -> np.ndarray:
        """
        Produces energy based on the load and time delta.

        Returns
        -------
        np.ndarray
            Production of the module at the current load
            [production]
        """
        raise NotImplementedError('The produce method must be implemented by the child class.')

    def consume(self) -> np.ndarray:
        """
        Consumes energy based on the load and time delta.

        Returns
        -------
        np.ndarray
            Consumption of the module at the current load
            [consumption]
        """
        raise NotImplementedError('The consume method must be implemented by the child class.')

    def maintain(self, time_delta: float):
        """
        Maintains the module based on the time delta.

        Parameters
        ----------
        time_delta : float
            time difference [hours]
        """
        self.remaining_maintenance_time -= time_delta

    def calculate_maintenance_time(self) -> float:
        """
        Calculates the maintenance time of the module.

        Returns
        -------
        float
            Time it takes to maintain the module
        """
        raise NotImplementedError('The calculate_maintenance_time method must be implemented by the child class.')

    def report_status(self) -> np.ndarray:
        """
        Reports the status of the module.

        Returns
        -------
        np.ndarray
            Status of the module
            [load, remaining maintenance time, products, consumption]
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

        Parameters
        ----------
        time_delta : float
            time difference [hours]
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
        if self.check_load_change():
            self._remaining_load_change_time = self.load_change_time
        self.reduce_remaining_load_change_time(time_delta)
        self._ready_to_change_load = self.check_ready_for_load_change()
        self._previous_load = self._load
