""" """

from importlib.metadata import PackageNotFoundError, version

from bsm2_python.bsm2.adm1_bsm2 import ADM1Reactor
from bsm2_python.bsm2.asm1_bsm2 import ASM1reactor
from bsm2_python.bsm2.dewatering_bsm2 import Dewatering
from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter
from bsm2_python.bsm2.primclar_bsm2 import PrimaryClarifier
from bsm2_python.bsm2.settler1d_bsm2 import Settler
from bsm2_python.bsm2.storage_bsm2 import Storage
from bsm2_python.bsm2.thickener_bsm2 import Thickener
from bsm2_python.bsm2_cl import BSM2CL
from bsm2_python.bsm2_ol import BSM2OL
from bsm2_python.bsm2_olem import BSM2OLEM

__all__ = [
    'BSM2CL',
    'BSM2OL',
    'BSM2OLEM',
    'ADM1Reactor',
    'ASM1reactor',
    'Combiner',
    'Dewatering',
    'PrimaryClarifier',
    'Settler',
    'Splitter',
    'Storage',
    'Thickener',
]

try:
    __version__ = version('bsm2-python')
except PackageNotFoundError:  # pragma: no cover
    __version__ = 'unknown'
finally:
    del version, PackageNotFoundError
