---
hide:
  - toc
---

![Boiler](../../assets/icons/bsm2python/boiler.svg){ align=right }

### Introduction and Model

The boiler utilizes sewage gas from the biogas storage to heat the anaerobic digester and maintain its necessary operating temperature. It serves as a secondary heat generator that is only operated if the heat supply from the CHPs is insufficient.

The boiler is implemented as a black box model, as its internal workings are not considered critical and are too complex to model in detail. The [thermal power generation](#thermal-power) is calculated with defined efficiencies at the current utilization of the boiler. The [biogas consumption](#biogas-consumption) of the boiler is calculated with the current utilization and the lower heating value of the biogas. The utilization rate $k_{load}$ of the boiler is depended on the heat demand of the anaerobic digester and can vary between a defined minimum utilization of 30% and 100%. The following cases are assumed:

- High heat demand ($P_{th,demand} \ge P_{th,max}$): Boiler is used at maximum utilization ($k_{load} = 1$)

- Partial heat demand ($P_{th,max} \gt P_{th,demand} \ge P_{th,min}$): Boiler is partially utilized ($0.30 \le k_{load} \lt 1$)

- Low heat demand ($P_{th,demand} \lt P_{th,min}$): Boiler is used at minimum utilization ($k_{load} = 0.30$)

- No heat demand ($P_{th,demand} = 0$): Boiler is not utilized ($k_{load} = 0$)


### Equations

#### Thermal power

$$
P_{th} = P_{th,max} \cdot k_{load} \cdot \eta_{th}(k_{load})
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $P_{th}$ | Thermal power generation | kW |
| $P_{th,max}$ | Maximum generation of thermal energy | kW |
| $k_{load}$ | Utilization rate of the boiler | - |
| $\eta_{th}(k_{load})$ | Thermal efficiency at current utilization rate $k_{load}$ | - |


#### Biogas consumption

$$
\dot V_{gas} = \frac{P_{th,max} \cdot k_{load}}{H_{u,gas}}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $\dot V_{gas}$ | Biogas consumption of the boiler | Nm^3^ $\cdot$ h^-1^ |
| $P_{th,max}$ | Maximum generation of thermal energy | kW |
| $k_{load}$ | Utilization rate of the boiler | - |
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
mod</span> [boiler](/reference/bsm2_python/energy_management/boiler)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [boiler_init](/reference/bsm2_python/energy_management/init/boiler_init)
