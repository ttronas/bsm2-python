# BSM2-Python

A Python implementation of the Benchmark Simulation Model 2 (BSM2) plant layout according to the [IWA](http://iwa-mia.org/) standard.
A description of BSM2 can be found [here](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf).

## To-Do:
- [ ] Nick: Write docs!

## Installation
### Easy way
To run the project, install the latest release via pypi:
`pip install bsm2_python`
### Build from source
If you want the bleeding edge version from the repo, build it yourself via `hatch build`.
See the [Contribution Guide](CONTRIBUTING.md) for more details on how to install `hatch` (or simply use the [Docker image](#docker)).
Then you can install it to arbitrary environments via `pip install dist/bsm2_python<version-hash>.whl`

## Quickstart
### Run default model
You could then use the following convenience function:
```python
from bsm2_python import BSM2OL

# initialise the BSM2 Open Loop model
bsm2_ol = BSM2OL()

# run the simulation
bsm2_ol.simulate()

```
This will run the BSM2 Open Loop model for the default 609 days of simulation time.
It will then plot IQI, EQI and OCI values for the effluent over the last few days of simulation.
Further, relevant data will be saved to `data/output_evaluation.csv` for further analysis.

### Run with custom aeration
You can also run the BSM2 models with your own aeration control - this example selects a random kla value for each reactor every timestep.
The final performance is then saved in the `oci` variable:
```python
import numpy as np
from bsm2_python import BSM2OL
from tqdm import tqdm


bsm2_ol = BSM2OL()

# The kla values to choose from
select_klas = np.array([0, 60, 120, 180, 240])

for idx, _ in enumerate(tqdm(bsm2_ol.simtime)):
    # select random klas for all five ASM1 reactors
    klas = np.random.choice(select_klas, 5)

    # make a step in the simulation with the specified kla values
    bsm2_ol.step(idx, klas)


oci = bsm2_ol.get_final_performance()[-1]
```

### Run Closed Loop simulation with custom DO setpoint
You can also run the BSM2 Closed Loop model with your own dissolved oxygen (SO4) setpoints.
Please note: The Closed Loop model runs with a resolution of 1 minute for the sake of sensor stability, so it might take a while to run the simulation.
```python
from bsm2_python import BSM2CL
from tqdm import tqdm


bsm2_cl = BSM2CL()

# The custom DO setpoint for the BSM2 default aeration control
so4_ref = 1.5

for idx, _ in enumerate(tqdm(bsm2_cl.simtime)):
    bsm2_cl.step(idx, so4_ref)

# get the final performance of the plant
oci = bsm2_cl.get_final_performance()[-1]

```

### Run with energy management model
We introduced a simple energy management model (including CHPs, Boilers, Flares and a small techno-economic analysis) that can be used to simulate the energy consumption and production of the plant.
```python
from bsm2_python import BSM2OLEM

bsm2_olem = BSM2OLEM()

bsm2_olem.simulate()

# get the cumulated cash flow of the plant
cash_flow = bsm2_olem.economics.cum_cash_flow
```

### And much more...
You can also implement your own plant layout. Lots of classes are available to choose from. See the [Documentation](docs/) for more information.
The [`tests`](tests/) folder contains a lot of examples on how to use the plant layouts.

## Docker
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

## Citation
If you use this package in your research, please cite it as follows:
```
@article{miederer2024bsm2python,
    title={Energy Management Model for Wastewater Treatment Plants},
    author={Jonas Miederer and Lukas Meier and Nora Elhaus and Simon Markthaler and J{\"u}rgen Karl},
    journal={Journal of Energy Conversion and Management},
    year={2024}
}
