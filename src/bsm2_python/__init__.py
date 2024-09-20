""" """

from importlib.metadata import PackageNotFoundError, version

from bsm2_python.bsm2_base import BSM2Base
from bsm2_python.bsm2_cl import BSM2CL
from bsm2_python.bsm2_ol import BSM2OL
from bsm2_python.bsm2_olem import BSM2OLEM

__all__ = ['BSM2CL', 'BSM2OL', 'BSM2OLEM', 'BSM2Base']

try:
    __version__ = version('bsm2-python')
except PackageNotFoundError:  # pragma: no cover
    __version__ = 'unknown'
finally:
    del version, PackageNotFoundError
