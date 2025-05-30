---
hide:
  - toc
---

![Cooler](../../../assets/icons/bsm2python/cooler.svg){ align=right }

### Introduction and Model

The cooler releases excess heat from the heating network to maintain the optimal operating temperature for the anaerobic digester.

The cooler is implemented as a black box model, as its internal workings are not considered critical and are too complex to model in detail. The [heat release](#heat-release) of the cooler depends on the heat surplus $\dot Q_{heat}$ of the heating network. The following cases are assumed:

- High heat surplus ($\dot Q_{heat} \ge \dot Q_{heat,max}$): Cooler is fully utilized ($k_{load} = 1$)

- Partial heat surplus ($0 \lt \dot Q_{heat} \lt \dot Q_{heat,max}$): Cooler is partially utilized ($0 \lt k_{load} \lt 1$)

- No heat surplus ($\dot Q_{heat} = 0$): Cooler is not utilized ($k_{load} = 0$)


### Equations

#### Heat release

$$
\dot Q_{heat} = k_{load} \cdot \dot Q_{heat,max}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $\dot Q_{heat}$ | Heat release of the cooler | kW |
| $k_{load}$ | Utilization rate of the cooler | - |
| $\dot Q_{heat,max}$ | Maximum heat uptake power | kW |


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [cooler](/reference/bsm2_python/energy_management/cooler)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [cooler_init](/reference/bsm2_python/energy_management/init/cooler_init)
