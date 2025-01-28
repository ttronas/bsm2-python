---
hide:
  - toc
---

![Flare](../../assets/icons/bsm2python/flare.svg){ align=right }

### Introduction and Model

The flare burns excess sewage gas from the biogas storage, when the storage tank's full capacity is reached.

The flare is implemented as a black box model, as its internal workings are not considered critical and are too complex to model in detail. The utilization rate $k_{load}$ of the flare depends on the biogas surplus $\dot V_{gas}$ of the biogas storage tank. The following cases are assumed:

- High gas surplus ($\dot V_{gas} \ge \dot V_{gas,max}$): Flare is fully utilized ($k_{load} = 1$)

- Partial gas surplus ($\dot V_{gas,max} \gt \dot V_{gas} \gt 0$): Flare is partially utilized ($0 \lt k_{load} \lt 1$)

- No gas surplus ($\dot V_{gas} = 0$): Flare is not utilized ($k_{load} = 0$)


### Equations

#### Utilization rate

$$
k_{load} = \frac{\dot V_{gas}}{\dot V_{gas,max}}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $k_{load}$ | Utilization rate of the flare | - |
| $\dot V_{gas}$ | Biogas consumption of the flare | Nm^3^ $\cdot$ h^-1^ |
| $\dot V_{gas,max}$ | Maximum gas uptake flow | Nm^3^ $\cdot$ h^-1^ |


#### Biogas consumption

$$
P_{gas} = k_{load} \cdot P_{gas,max}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $P_{gas}$ | Biogas consumption of the flare | kW |
| $k_{load}$ | Utilization rate of the flare | - |
| $P_{gas,max}$ | Maximum gas uptake power | kW |


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [flare](/reference/bsm2_python/energy_management/flare)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [flare_init](/reference/bsm2_python/energy_management/init/flare_init)
