"""This is the source code folder of the Benchmark Simulation Model No. 2 in Python. <br>
The sub folders include source code from both the BSM2 and Kläffizient project.

The following graph shows the folder structure for the source code:

<pre>
src/
└── <span style="color:#4cae4f">bsm2_python</span>/ 
    ├── bsm2/               (BSM2)
    │   └── init
    ├── data                (BSM2 & Kläff)
    ├── energy_management/  (Kläff)
    │   └── init
    └── gases               (Kläff)
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
