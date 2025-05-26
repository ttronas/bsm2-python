---
hide:
  - toc
---

### Introduction

The economics module evaluates the expenditures and revenues of the energy management system (EMS) for a simulation.

The expenditures of the EMS are divided into capital expenditures (CapEx) and operating expenditures (OpEx). [CapEx](#capital-expenditures-capex) covers debt payments for acquisition costs, while [OpEx](#operating-expenditures-opex) covers ongoing expenses for operating, maintenance, insurance and staff salaries. The [total expenditures](#total-expenditures) for the EMS are calculated by adding up CapEx and OpEx. [Revenues](#revenues) for the EMS are generated, when CHP units produce excess electricity that is sold to the power grid.


### Equations

#### Capital expenditures (CapEx)

$$
C_{CapEx} = \frac{ANF}{8760 \frac{h}{a} / \Delta t} \cdot C_{purch} \cdot f
$$

$$
ANF = \frac{(1 + i)^n \cdot i}{(1 + i)^n - 1}
$$

$$
C_{purch} = C_{chps} + C_{boilers} + C_{storage} + C_{compressor} + C_{flare} + C_{cooler}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $C_{CapEx}$ | Capital expenditures for a single simulation step | € |
| $C_{purch}$ | Total purchase costs for equipment | € |
| $C_{i}$ | Individual purchase costs for equipment | € |
| $ANF$ | Annuity factor | a^-1^ |
| $i$ | Bank interest rate | a^-1^ |
| $n$ | Payback time in years | - |
| $\Delta t$ | Time difference of a simulation time step | h |
| $f$ | Factor (15%) for additional costs due to planning, permit, certificate and reserve | € |


#### Operating expenditures (OpEx)

$$
C_{OpEx} = C_{electr} + C_{maint} + C_{insur} + C_{staff}
$$

$$
C_{electr} = P_{el,demand} \cdot p_{el,price} \cdot \Delta t
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $C_{OpEx}$ | Operating expenditures for a single simulation step | € |
| $C_{electr}$ | Total electricity costs of the EMS for electricity purchased from the power grid | € |
| $C_{maint}$ | Total maintenance costs | € |
| $C_{insur}$ | Total insurance costs | € |
| $C_{staff}$ | Total costs due to staff salaries | € |
| $P_{el,demand}$ | Power demand of EMS for a single simulation step | kW |
| $p_{el,price}$ | Electricity purchase price | € $\cdot$ kWh^-1^ |
| $\Delta t$ | Time difference of a simulation time step | h |


#### Total expenditures

$$
C_{total} = C_{CapEx} + C_{OpEx}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $C_{total}$ | Total expenditures of the EMS for a single simulation step | € $\cdot$ h^-1^ |
| $C_{CapEx}$ | Capital expenditures | € $\cdot$ h^-1^ |
| $C_{OpEx}$ | Operating expenditures | € $\cdot$ h^-1^ |


#### Revenues

$$
R_{electr} = P_{el,excess} \cdot p_{el,price} \cdot \Delta t
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $R_{electr}$ | Revenue of the EMS for sold electricity to power grid (for single simulation step) | € $\cdot$ h^-1^ |
| $P_{el,excess}$ | Excess power of the EMS for a single simulation step | kW |
| $p_{el,price}$ | Electricity selling price | € $\cdot$ kWh^-1^ |
| $\Delta t$ | Time difference of a simulation time step | h |


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [economics](/reference/bsm2_python/energy_management/economics)
