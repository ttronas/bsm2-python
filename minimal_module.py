"""Minimal module for testing without control dependencies."""

class Module:
    """A class that represents a generic bsm2 module."""

    def __init__(self) -> None:
        pass

    def output(self, *args, **kwargs):
        raise NotImplementedError('The output method must be implemented by the child class.')