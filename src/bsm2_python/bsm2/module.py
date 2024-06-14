"""A generic Module for all bsm2 modules."""

import numpy as np


class Module:
    def __init__(self) -> None:
        """
        A class that represents a generic bsm2 module.

        Children classes should implement the following methods:
        - output
        """

    def output(self, *args, **kwargs) -> np.ndarray | tuple[np.ndarray, np.ndarray]:
        raise NotImplementedError('The output method must be implemented by the child class.')
