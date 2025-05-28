"""This is the source code folder of the Benchmark Simulation Model No. 2 in Python. <br>
The source code is structured as follows:

<pre>
src/
└─── <span style="color:#4cae4f">bsm2_python</span>/
     |      └─ Root folder of the project code
     │         Contains pre-defined plant layouts and controllers
     ├── bsm2/
     │   │  └─ All modules for the BSM2 plant layouts
     │   └─── init
     │        └─ Initialization files for the BSM2 plant layouts
     ├── data
     │   └─ Standard datasets for influent data
     │      and sensor noise
     ├── energy_management/
     │   │  └─ Modules for the energy management side of the BSM2 plant
     │   └─── init
     │        └─ Initialization files for the gas management side
     └── gases
         └─ Modules for the physical properties of the gases
</pre>
"""

from importlib.metadata import PackageNotFoundError, version

from bsm2_python.bsm1_base import BSM1Base
from bsm2_python.bsm1_ol import BSM1OL
from bsm2_python.bsm1_ps import BSM1PS
from bsm2_python.bsm2_base import BSM2Base
from bsm2_python.bsm2_cl import BSM2CL
from bsm2_python.bsm2_ol import BSM2OL
from bsm2_python.bsm2_olem import BSM2OLEM

__all__ = ['BSM1OL', 'BSM1PS', 'BSM2CL', 'BSM2OL', 'BSM2OLEM', 'BSM1Base', 'BSM2Base']

try:
    __version__ = version('bsm2-python')
except PackageNotFoundError:  # pragma: no cover
    __version__ = 'unknown'
finally:
    del version, PackageNotFoundError
