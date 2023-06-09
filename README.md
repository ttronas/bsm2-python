# ASM-Python

This is a Python implementation of ASM1 and ASM3 in parts of BSM1 layout.
Description of BSM1 can be found [here](http://iwa-mia.org/wp-content/uploads/2018/01/BSM_TG_Tech_Report_no_1_BSM1_General_Description.pdf).


## Installation
To run the project, in addition to the Python scripts, the following packages must be installed: `numpy`, `csv`, `pandas`, `time`, `scipy.integrate`, `numba`, `scipy`.
You can simply execute any `*runss*.py` file to see some standard results on a steady state (ss) dataset.
For dynamic results, make sure to run a ss file first to equilibrate the reactors before.

## File Descriptions
- `asm1.py`, `asm3.py`: 
Files containing equations of Activated Sludge Model No. 1 and 3. With the class ASMxreactor, a reactor unit can be created as an object in which the equations are solved with the method output.
- `settler1d_asm1.py`, `settler1d_asm3.py`:
Files containing equations of a 10-layer one dimensional settler model. With the class Settler, the settler can be created as an object in which the equations are solved with the method outputs. For a simulation based on ASM1, number of layers can be chosen flexibly.
- `aerationcontrol.py`:
Files containing equations of PI controller of aeration, which maintains oxygen at a certain setpoint in reactor unit. With the class PIaeration, the PI controller can be created as an object which determines the KLa value for adjusting the oxygen with the method output. For a non-ideal system, two extra objects to delay the signals can be added with the classes Oxygensensor and KLaactuator. In case of Oxygensensor, the method measureSO gives the measured oxygen value in the reactor unit. For KLaactuator, the method real_actuator returns the delayed KLa value.
- `average_asm1.py`, `average_asm3.py`:
Files containing the function averages which returns average values of the components during a certain evaluation time.
- `plantperformance.py`:
File containing equations to determine energy consumption (pumping, aeration and mixing energy) and effluent quality during the evaluation time. In case of effluent quality, the method violation returns the time in days and percentage of time in which a certain component is over the limit.
- `asm1init.py`, `asm3init.py`, `settler1dinit_asm1.py`, `settler1dinit_asm3.py`, `aerationcontrolinit.py`: 
Files containing values for all parameters and states to run the simulation in BSM1 layout.
- `asm1runss.py`, `asm1run.py`, `asm3runss.py`, `asm3run.py`:
When running these files, the BSM1 plant without any control strategy (Openloop) can be simulated in steady state (ss) or as dynamic system.
- `asm1runss_ac.py`, `asm1run_ac.py`:
When running these files, the BSM1 plant with aeration control in reactor unit 5 can be simulated in steady state (ss) or as dynamic system.
- `asm1runss_ps.py`, `asm1run_ps.py`:
When running these files, the BSM1 plant with aeration control in reactor unit 3, 4 and 5 can be simulated in steady state (ss) or as dynamic system. The script also contains 7 different scenarios for flexible aeration. In scenario 1, no flexible aeration is adjusted.

## Usage
In case of ASM1, you can choose between three different configurations of the plant: without any control, with aeration control in tank 5 (ac) and with aeration control in tank 3, 4 and 5 (ps). The chosen BSM1 plant must be brought into a steady-state condition with the steady state file (ss). The results are saved as csv file and serve as the initial state for any dynamic simulation. When nothing is changed, every dynamic simulation can be started from this point. Three input files for different weather conditions from BSM1 can be used for the dynamic simulation. The results of the simulation are saved as csv files. 
With tempmodel and activate, differential equations for temperature and additional components can be added. 
If you want to create your own plant layout, use the `run` files as template. Put your own parameters and values in extra `init` files. 

## Support
If you find any issues inside the repo, don't hesitate to raise an Issue.

## Roadmap
In the future, this repo will aim to contain a complete description of BSM1.
Missing for BSM1:
- Alternative standard control (internal return should be determined via nitrate value).
- Determine some indices, EQI or similar.
- Determine energy required by external carbon stream

After implementing an ADM and other components, the BSM2 can also be described.


## Authors and acknowledgment
Thanks to Maike Böhm for first implementing the ASM in Python in her Masters Thesis.

## License
This project is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Project status
As I am maintaining this repo in my free time, don't expect rapid development. However, if any Issues are popping up, I will try to fix them in time.
