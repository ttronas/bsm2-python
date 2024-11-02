"""This is the source code folder (bsm2_python) of the Benchmark Simulation Model No. 2 in Python.

This folder contains sub folders that include source code from different projects:

- **BSM2 project folders**: bsm2
- **Kläffizient project folders**: data, energy_management, gases

The following shows the folder structure for the source code:

<pre>
src/
└── bsm2_python/
    ├── bsm2/
    │   └── init
    ├── data
    ├── energy_management/
    │   └── init
    └── gases
</pre>
"""

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
