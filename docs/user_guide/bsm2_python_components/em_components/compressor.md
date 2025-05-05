---
hide:
  - toc
---

### Introduction and Model

The compressor increases the pressure of the biogas from the anaerobic digester, reducing its volume to prepare it for the biogas storage.

The compressor is implemented as a black box model, as its internal workings are not considered critical and are too complex to model in detail. The [power consumption](#power-consumption) of the compressor is calculated with the [maximum electrical power uptake](#maximum-electrical-power-uptake) and the current utilization of the compressor. The utilization rate $k_{load}$ depends on the gas flow $\dot V_{gas}$ of the anaerobic digester. The following cases are assumed:

- Gas flow ($0 \lt \dot V_{gas} \le \dot V_{gas,max}$): Compressor is utilized ($0 \lt k_{load} \le 1$)

- No gas flow ($\dot Q_{gas} = 0$): Compressor is not utilized ($k_{load} = 0$)


### Equations

#### Power consumption

$$
P_{el} = k_{load} \cdot P_{el,max}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $P_{el}$ | Power consumption of the compressor | kW |
| $k_{load}$ | Utilization rate of the compressor | - |
| $P_{el,max}$ | Maximum electrical power uptake | kW |


#### Maximum electrical power uptake

$$
P_{el,max} = \frac{1}{3600} \cdot \frac{c_{p,gas} \cdot (t_{gas} + 273,15) \cdot \dot V_{gas,max} \cdot \rho_{gas} \cdot \left( \left( \frac{p_{out}}{p_{in}} \right)^{\frac{\kappa - 1}{\kappa}} - 1 \right)}{\eta}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $P_{el,max}$ | Power consumption of the compressor | kW |
| $c_{p,gas}$ | Specific heat capacity of the biogas  | kJ $\cdot$ kg^-1^ $\cdot$ K^-1^ |
| $t_{gas}$ | Input temperature of the biogas | °C |
| $\dot V_{gas,max}$ | Maximum gas flow uptake | Nm^3^ $\cdot$ h^-1^ |
| $\rho_{gas}$ | Density of the biogas | kg $\cdot$ Nm^-3^ |
| $p_{out}$ | Pressure of the biogas storage | bar |
| $p_{in}$ | Pressure of the influent biogas | bar |
| $\kappa$ | Isotropic exponent of the biogas | - |
| $\eta$ | Electrical efficiency of the compressor | - |


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [compressor](/reference/bsm2_python/energy_management/compressor)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [compressor_init](/reference/bsm2_python/energy_management/init/compressor_init)
