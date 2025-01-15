---
hide:
  - toc
---

![Settler](../../assets/icons/bsm2python/settler.svg){ align=right }

### Introduction and Model

The settler is a secondary clarifier that uses a settling process to separate the treated wastewater after the activated sludge reactor into two streams - effluent (overflow) and sludge (underflow). The implementation is based on the Takács model (1991), which represents the settler as a 10-layer system. This model simulates the solids profile throughout the settling column, including the underflow and overflow suspended solids concentrations under steady-state and dynamic conditions. The layers are numbered from the bottom (layer 1) with the sixth layer being designated as the feeding layer. Solids are removed from the settler both from layer 1 (underflow) and layer 10 (overflow). In each layer a mass balance accounts for the [solids flux](#solids-flux) - settling of particulate components due to gravity and the transportation through the liquid flow - into and out of the layer. The particle settling velocity inside each layer is calculated through the [double-exponential settling velocity function](#double-exponential-settling-velocity-function).

In the mass balances the total suspended solids (TSS) value is used instead of the individual particulate ASM state variables. To convert the calculated TSS values back into particulate ASM state variables for the underflow and overflow streams, it is assumed that the particulate fraction in the overflow and underflow are the same as in the influent fractions.

<figure markdown="span">
  ![Settler flowchart](../../assets/images/settler_flowchart.drawio.svg)
  <figcaption markdown="1">Schematic model of a 10-layer settler[^1]</figcaption>
</figure>


### Equations

#### Solids flux

$$
J_s = \nu_s(X_{sc}) \cdot X_{sc}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $J_s$  | Solids flux due to gravity in layer $j$ | g $\cdot$ m^-2^ $\cdot$ d^-1^ |
| $\nu_s(X_{sc})$ | Settling velocity in layer $j$ | m $\cdot$ d^-1^ |
| $X_{sc}$ | Solids concentration in layer $j$ | g $\cdot$ m^-3^ |


#### Double-exponential settling velocity function

$$
\nu_{sj} = \nu_o e^{-r_h X_j^*} - \nu_o e^{-r_p X_j^*} \quad \text{with} \quad 0 \le \nu_{sj} \le \nu'_o
$$

The first term $(\nu_o e^{-r_h X_j^*})$ reflects the settling velocity of the large, well flocculating particles and 
the second term $(\nu_o e^{-r_p X_j^*})$ is a velocity correction factor to account for the smaller, slowly settling particles.

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $\nu_{sj}$ | Settling velocity in layer $j$ | m $\cdot$ d^-1^ |
| $\nu_o$ | Maximum theoretical settling velocity | m $\cdot$ d^-1^ |
| $\nu_o'$ | Maximum practical settling velocity | m $\cdot$ d^-1^ |
| $r_h$ | Settling parameter associated with the hindered settling component of settling velocity equation | m^3^ $\cdot$ g^-1^ |
| $r_p$ | Settling parameter associated with the low concentration and slowly settling component of the suspension | m^3^ $\cdot$ g^-1^ |
| $X_j^*$ | Solids concentration in layer $j$ | g $\cdot$ m^-3^ |

**Limiting condition:**

$$
X_j^* = X_j - X_{min} \quad \text{with} \quad X_{min} = f_{ns} \cdot X_{in}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $X_j$ | Suspended solids concentration in layer $j$ | g $\cdot$ m^-3^ |
| $X_{min}$ | Minimum attainable suspended solids concentration | g $\cdot$ m^-3^ |
| $X_{in}$ | Mixed liquor suspended solids concentration entering the settling tank | g $\cdot$ m^-3^ |
| $f_{ns}$ | Non-settleable fraction of $X_{in}$ | - |


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [settler1d_bsm2](/reference/bsm2_python/bsm2/settler1d_bsm2)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [settler1dinit_bsm2](/reference/bsm2_python/bsm2/init/settler1dinit_bsm2)


[^1]: [Benchmarking of Control Strategies for Wastewater Treatment Plants](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf), chap. 4.2.4.2 Secondary clarifier
[^2]: [Benchmark Simulation Model no. 2 (BSM2)](http://iwa-mia.org/wp-content/uploads/2022/09/TR3_BSM_TG_Tech_Report_no_3_BSM2_General_Description.pdf), chap. 2.3.3 Secondary clarifier
[^3]: [A dynamic model of the clarification-thickening process, Takács et al. (1991)](https://www.sciencedirect.com/science/article/pii/004313549190066Y)
