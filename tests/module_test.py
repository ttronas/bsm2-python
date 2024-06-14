import numpy as np
import pytest

from bsm2_python.bsm2.module import Module as BSM2Module
from bsm2_python.gas_management.module import Module as GasManagementModule


class TestBSM2Module:
    @classmethod
    def test_bsm2_output_raises_not_implemented_error(cls):
        module = BSM2Module()
        with pytest.raises(NotImplementedError):
            module.output()


class TestGasManagementModule:
    @pytest.fixture
    @classmethod
    def module(cls):
        return GasManagementModule()

    @classmethod
    def test_initial_values(cls, module):
        assert module.global_time == 0.0
        assert module.runtime == 0.0
        assert module.load == 0.0
        assert module.total_maintenance_time == 0.0
        assert module.remaining_maintenance_time == 0.0
        assert module.time_since_last_maintenance == 0.0
        assert not module.under_maintenance
        assert module.maintenance_cost_per_hour == 0.0
        assert module.mttf == 0.0
        assert module.mttr == 0.0
        assert isinstance(module.products, np.ndarray)
        assert isinstance(module.consumption, np.ndarray)

    @classmethod
    def test_load_setter(cls, module):
        module.load = 0.5
        assert module.load == 0.5

    @classmethod
    def test_total_maintenance_time_setter(cls, module):
        module.total_maintenance_time = 10.0
        assert module.total_maintenance_time == 10.0

    @classmethod
    def test_remaining_maintenance_time_setter(cls, module):
        module.remaining_maintenance_time = 5.0
        assert module.remaining_maintenance_time == 5.0
        assert module.under_maintenance

        module.remaining_maintenance_time = 0.0
        assert module.remaining_maintenance_time == 0.0
        assert not module.under_maintenance

        module.remaining_maintenance_time = -1.0
        assert module.remaining_maintenance_time == 0.0
        assert not module.under_maintenance

    @classmethod
    def test_under_maintenance_setter(cls, module):
        module.under_maintenance = True
        assert module.under_maintenance

        module.under_maintenance = False
        assert not module.under_maintenance

    @classmethod
    def test_check_failure(cls, module):
        with pytest.raises(NotImplementedError):
            module.check_failure()

    @classmethod
    def test_produce(cls, module):
        with pytest.raises(NotImplementedError):
            module.produce()

    @classmethod
    def test_consume(cls, module):
        with pytest.raises(NotImplementedError):
            module.consume()

    @classmethod
    def test_maintain(cls, module):
        module.remaining_maintenance_time = 10.0
        module.maintain(5.0)
        assert module.remaining_maintenance_time == 5.0

    @classmethod
    def test_calculate_maintenance_time(cls, module):
        with pytest.raises(NotImplementedError):
            module.calculate_maintenance_time()

    @classmethod
    def test_report_status(cls, module):
        status = module.report_status()
        assert isinstance(status, np.ndarray)
        assert len(status) == 4

    @classmethod
    def test_step_without_maintenance(cls, module):
        module.check_failure = lambda: False
        module.produce = lambda: np.array([1, 2, 3])
        module.consume = lambda: np.array([4, 5, 6])

        module.step(1.0)
        assert module.global_time == 1.0
        assert module.runtime == 1.0
        assert np.all(module.products == np.array([1, 2, 3]))
        assert np.all(module.consumption == np.array([4, 5, 6]))

    @classmethod
    def test_step_with_maintenance(cls, module):
        module.remaining_maintenance_time = 2.0
        module.calculate_maintenance_time = lambda: module.remaining_maintenance_time - 1.0
        module.check_failure = lambda: module.remaining_maintenance_time > 0.0
        module.produce = lambda: np.array([1, 2, 3])
        module.consume = lambda: np.array([4, 5, 6])

        module.step(1.0)
        assert module.global_time == 1.0
        assert module.runtime == 0.0
        assert module.remaining_maintenance_time == 1.0
        assert module.under_maintenance
        assert np.all(module.products == np.zeros_like(module.products))
        assert np.all(module.consumption == np.zeros_like(module.consumption))

        module.step(1.0)
        assert module.global_time == 2.0
        assert module.runtime == 0.0
        assert module.remaining_maintenance_time == 0.0
        assert not module.under_maintenance
        assert np.all(module.products == np.zeros_like(module.products))
        assert np.all(module.consumption == np.zeros_like(module.consumption))

        module.step(1.0)
        assert module.global_time == 3.0
        assert module.runtime == 1.0
        assert module.remaining_maintenance_time == 0.0
        assert not module.under_maintenance
        assert module.time_since_last_maintenance == 1.0
        assert np.all(module.products == np.array([1, 2, 3]))
        assert np.all(module.consumption == np.array([4, 5, 6]))
