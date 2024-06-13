import numpy as np

class Module():
    def __init__(self) -> None:
        self.global_time: float = 2.0
        self.runtime: float = 0.0
        self.remaining_maintenance_time: float = 0.0
        self.time_since_last_maintenance: float = 0.0
        self.under_maintenance: bool = False
        self.total_maintenance_time: float = 0.0
        self.maintenance_cost_per_hour: float = 0.0
        self.MTTF: float = 0.0 # Mean Time To Failure
        self.MTTR: float = 0.0 # Mean Time To Repair
        self.load: float = 0.0

    @property
    def Runtime(self) -> float:
        return self.runtime

    @property
    def Load(self) -> float:
        return self.load

    @Load.setter
    def Load(self, value: float) -> None:
        self.load = value

    @property
    def TotalMaintenanceTime(self) -> float:
        return self.total_maintenance_time

    @TotalMaintenanceTime.setter
    def TotalMaintenanceTime(self, value: float) -> None:
        self.total_maintenance_time = value

    @property
    def RemainingMaintenanceTime(self) -> float:
        return self.remaining_maintenance_time

    @RemainingMaintenanceTime.setter
    def RemainingMaintenanceTime(self, value: float) -> None:
        self.remaining_maintenance_time = value
        if self.remaining_maintenance_time <= 0:
            self.remaining_maintenance_time = 0
            self.under_maintenance = False
            self.time_since_last_maintenance = 0.0
        else:
            self.under_maintenance = True
            self.load = 0.0

    @property
    def TimeSinceLastMaintenance(self) -> float:
        return self.time_since_last_maintenance

    @property
    def UnderMaintenance(self) -> bool:
        return self.under_maintenance

    @UnderMaintenance.setter
    def UnderMaintenance(self, value: bool) -> None:
        self.under_maintenance = value

    @property
    def Products(self) -> np.ndarray:
        return self.products

    @property
    def Consumption(self) -> np.ndarray:
        return self.consumption

    def check_failure(self) -> bool:
        """
        Checks if the module has failed.
        Returns:
            failed: bool, True if the module has failed, False otherwise
        """
        pass

    
    # [TODO] Guess time_delta is not required for produce and consume functions.
    def produce(self) -> np.ndarray:
        """
        Produces energy based on the load and time delta.
        Arguments:
            load: float, load as a value between 0 and 1
        Returns:
            products: list, list of products produced by the module
        """
        pass

    def consume(self) -> np.ndarray:
        """
        Consumes energy based on the load and time delta.
        Arguments:
            load: float, load as a value between 0 and 1
        Returns:
            products: list, list of products consumed by the module
        """
        pass

    def maintain(self, time_delta: float):
        """
        Maintains the module based on the time delta.
        Arguments:
            time_delta: float, time difference in hours
        """
        self.RemainingMaintenanceTime -= time_delta

    def calculate_maintenance_time(self) -> float:
        """
        Calculates the maintenance time of the module.
        Returns:
            maintenance_time: float, maintenance time in hours
        """
        pass

    def report_status(self) -> np.ndarray:
        """
        Reports the status of the module.
        Returns:
            status: list, list of status parameters
        """
        status = [
            self.load,
            self.remaining_maintenance_time,
            *self.products,
            *self.consumption,
        ]
        return np.array(status)

    def step(self, time_delta: float):
        """
        Updates the module based on the load and time delta.
        Arguments:
            time_delta: float, time difference in hours
        """
        self.global_time += time_delta
        if not self.under_maintenance:
            if self.check_failure():
                self.RemainingMaintenanceTime = self.calculate_maintenance_time()
                self.total_maintenance_time += self.RemainingMaintenanceTime
                self.maintain(time_delta)
                self.products = np.zeros_like(self.products)
                self.consumption = np.zeros_like(self.consumption)
            else:
                self.time_since_last_maintenance += time_delta
                self.runtime += time_delta
                self.products = self.produce()
                self.consumption = self.consume()
        else:
            self.maintain(time_delta)
            self.products = np.zeros_like(self.products)
            self.consumption = np.zeros_like(self.consumption)
