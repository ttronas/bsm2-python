---
hide:
  - toc
---

### Introduction and Model

The fermenter serves as an interface between the anaerobic digester and the biogas storage in the energy management system. It represents the anaerobic digester using only parameters necessary for energy calculations.

Biogas production, heat demand and the partial pressure fractions of the biogas mixture are directly taken from the anaerobic digester. The partial pressures are then used to calculate the [composition of the biogas](#composition-of-the-biogas) and its [lower heating value](#lower-heating-value-of-the-biogas).


### Equations

#### Composition of the biogas

| i     | Component      |
| ----- | -------------- |
| CH~4~ | Methane gas    |
| CO~2~ | Carbon dioxide |
| H~2~  | Hydrogen gas   |
| H~2~O | Water vapor    |
| N~2~  | Nitrogen gas   |

$$
x_i = \frac{p_i}{p_{gas}}
$$

For water vapor and nitrogen gas the partial pressure is zero ($p_{H_2O}=p_{N_2}=0$ bar).

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $x_i$ | Mole fraction of the individual gas *i* | - |
| $p_i$ | Partial pressure of individual gas *i* | bar |
| $p_{gas}$ | Total pressure of gas mixture | bar |


#### Lower heating value of the biogas

$$
H_{u,gas} = \frac{p_{H_2} \cdot H_{u,H_2} + p_{CH_4} \cdot H_{u,CH_4}}{p_{gas}}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $H_{u,gas}$ | Lower heating value of the biogas mixture | kWh $\cdot$ Nm^-3^ |
| $H_{u,H_2}$ | Lower heating value of hydrogen gas | kWh $\cdot$ Nm^-3^ |
| $H_{u,CH_4}$ | Lower heating value of methane gas | kWh $\cdot$ Nm^-3^ |
| $p_{H_2}$ | Partial pressure of hydrogen gas | bar |
| $p_{CH_4}$ | Partial pressure of methane gas | bar |
| $p_{gas}$ | Total pressure of gas mixture | bar |


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [fermenter](/reference/bsm2_python/energy_management/fermenter)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [fermenter_init](/reference/bsm2_python/energy_management/init/fermenter_init)
