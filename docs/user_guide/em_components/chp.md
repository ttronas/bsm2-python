---
hide:
  - toc
---

![CHP](../../assets/icons/bsm2python/chp.svg){ align=right }

### Introduction and Model

The combined heat and power (CHP) unit utilizes sewage gas from the biogas storage to primarily generate electricity, which is used to power the aeration system of the activated sludge reactor. Additionally, the thermal energy produced during the process, which would otherwise be wasted, is recovered and utilized to maintain the necessary operating temperature of the anaerobic digester.

The CHP unit is implemented as a black box model, as its internal workings are not considered critical and are too complex to model in detail. The [electrical and thermal power generation](#electrical-and-thermal-power) is calculated with defined efficiencies at the current utilization of the CHP unit. The [biogas consumption](#biogas-consumption) of the CHP unit is calculated with the current utilization and the lower heating value of the biogas. The utilization rate $k_{load}$ of the CHP is depended on the storage fill level of the biogas storage and can vary between a defined minimum utilization of 54% and 100%. The following cases are assumed:

- Storage fill level ($\gt$ 50%): CHP is fully utilized ($k_{load} = 1$)

- Storage fill level ($\gt$ 35%): CHP is partially utilized ($0.54 \ge k_{load} \lt 1$)

- Storage fill level ($\le$ 35%): CHP is not utilized ($k_{load} = 0$)

To avoid sudden changes of the utilization, the CHP cannot adjust its utilization again for 6 hours after a change.
Also, the CHP unit has a certain failure rate, after which a short maintenance break is required in order to be operational again.


### Equations

#### Electrical and thermal power

$$
P_{el} = P_{gas,max} \cdot k_{load} \cdot \eta_{el}(k_{load})
$$

$$
P_{th} = P_{gas,max} \cdot k_{load} \cdot \eta_{th}(k_{load})
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $P_{el}$ | Electrical power generation | kW |
| $P_{th}$ | Thermal power generation | kW |
| $P_{gas,max}$ | Maximum gas uptake power | kW |
| $k_{load}$ | Utilization rate of the CHP unit | - |
| $\eta_{el}(k_{load})$ | Electrical efficiency at current utilization rate $k_{load}$ | - |
| $\eta_{th}(k_{load})$ | Thermal efficiency at current utilization rate $k_{load}$ | - |


#### Biogas consumption

$$
\dot V_{gas} = \frac{P_{gas,max} \cdot k_{load}}{H_{u,gas}}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $\dot V_{gas}$ | Biogas consumption of the CHP unit | Nm^3^ $\cdot$ h^-1^ |
| $P_{gas,max}$ | Maximum gas uptake power | kW |
| $k_{load}$ | Utilization rate of the CHP unit | - |
| $H_{u,gas}$ | Lower heating value of the biogas | kWh $\cdot$ Nm^-3^ |


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [storage](/reference/bsm2_python/energy_management/chp)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [storage_init](/reference/bsm2_python/energy_management/init/chp_init)
