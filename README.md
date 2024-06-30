# BSM2-Python

A Python implementation of the Benchmark Simulation Model 2 (BSM2) plant layout according to the [IWA](http://iwa-mia.org/) standard.
A description of BSM2 can be found [here](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf).

## To-Do:
- [x] Lukas: Write parent class for all BSM2 objects (e.g. methods `stabilize` or `simulate`)
- [ ] Lukas: Import different plant setups - including BSM2OLEM (BSM2 open loop with energy management)
- [x] Lukas: Write simple controller (focusing on kla and gas management control based on electricity prices)
- [ ] Nick: Write docs!
- [ ] Lukas: Mind the TODOs in the code and fix them. Afterwards, you can delete them.
- [ ] Lukas: Insert the PlantPerformance class in bsm2_ol and bsm2_cl as well (just as in bsm2_olem) so that we have a consistent structure

## Installation
To run the project, build it yourself via `hatch build`.
See the [Contribution Guide](CONTRIBUTING.md) for more details on how to install `hatch`.
Then you can install it to arbitrary environments via `pip install dist/bsm2_python<version-hash>.whl`
You could then do:
```python
import numpy as np
from tqdm import tqdm
from bsm2_python import BSM2OL

bsm2_ol = BSM2OL()

for idx, _ in enumerate(tqdm(bsm2_ol.simtime)):
    klas = np.concatenate((np.zeros((2,)), np.random.choice([0, 60, 120], 3)))
    bsm2_ol.step(idx, klas)

print(bsm2_ol.y_eff_all)
```
This will print out the results of the BSM2 Open Loop model for a random aeration control strategy over 609 days of simulation.

There is also a fully functional Docker image available in the [GitLab Container Registry](gitlab.rrze.fau.de:4567/evt/klaeffizient/bsm2-python).
It is a dev container and can be used to run the tests and do active development.

## Project structure
The project is structured as follows:
```
bsm2-python
├───docs
│   └────Documentation of the project
├───notebooks
|   └────Jupyter notebooks as explanatory examples
├───src
│   └────bsm2_python
│        |      └─Root folder of the project code
│        │        Contains pre-defined plant layouts and controllers
│        ├───bsm2
│        │   │  └─All modules for the BSM2 plant layouts
│        │   └───init
│        │       └─Initialisation files for the BSM2 plant layouts
│        └───data
│        │      └─Standard datasets for influent data
│        │        and sensor noise
│        └───gas_management
│            │  └─Modules for the gas management side of the BSM2 plant
│            └───init
│                └─Initialisation files for the gas management side
└───tests
    |  └─Unit tests for the BSM2 components in both
    │    steady state and dynamic mode
    └───simulink_files
         └─Reference files for validation purposes
```
## Usage
At the moment, you can choose between four different configurations of the plant:
1. BSM2OL: BSM2 without any control (dynamic or static influent data - you choose)
2. BSM2CL: BSM2 with aeration control in tanks 3-5
3. and a custom plant setup with completely free configurable setup. with aeration control in tank 3, 4 and 5

The results are saved inside the objects and can be accessed via calling the attribute names. For the plant effluent, just call `bsm2.y_eff_all`.
With `tempmodel` and `activate`, differential equations for temperature dependency and additional components can be added.
If you want to create your own plant layout, use the `bsm2_xx.py` files as template. Put your own parameters and values in separate `init` files.

## Support
Your help is highly appreciated! Please read through the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on our code of conduct, and the process for submitting pull requests to us.
If you find any issues inside the repo, don't hesitate to raise an Issue.


## Roadmap
In the future, this repo will be extended by the following features:
- [ ] Faster computation through Rust-based backend
- [ ] Support of more experimental tools, e.g. photovoltaics, methanation or electrolysis


## Authors and acknowledgment
Thanks to Maike Böhm for first implementing the ASM in Python in her Masters Thesis.
Thanks as well to Lukas Meier for implementing the Gas management side of the BSM2 plant.


The development of this package was done in the context of the [KLÄFFIZIENT] project. The project is funded by the German Federal Ministry for Economic Affairs and Climate Action ([BMWK]) and is part of the 7th Energy Research Program of the Federal Government.

## License
This project is licensed under [BSD 3 Clause](LICENSE.txt).

## Project status
As we are maintaining this repo in our free time, don't expect rapid development. However, if any Issues are popping up, we will try to fix them in time.


[KLÄFFIZIENT]: https://www.evt.tf.fau.de/forschung/schwerpunktekarl/ag-energiesysteme/bmwi-projekt-klaeffizient/
[BMWK]: http://bmwk.de/
