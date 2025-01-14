---
hide:
  - toc
---

![Primary clarifier](https://gitlab.rrze.fau.de/evt/klaeffizient/bsm2-python/-/raw/doc_new2/docs/assets/.icons/bsm2python/primary-clarifier.svg){ align=right }
<!-- TODO: change link to main branch before merging -->

### Introduction and Model

The primary clarifier separates wastewater into two streams - primary effluent (overflow) and primary sludge (underflow) - through a settling process. The implementation is based on the Otterpohl model (1995), which represents the primary clarifier as a single homogeneous tank that accounts for hydraulic retention time and concentration smoothing within the clarifier. This tank is separated into the overflow and underflow stream through a mass balance and an empirical separation approach, that produces reasonable concentrations of particulate material in both streams. The [empirical separation equation](#cod-removal-efficiency), dependent on the hydraulic retention time, is used to calculate the [state variable concentrations](#primary-effluent-concentration-of-each-state-variable) in the effluent stream. The state variable concentrations in the sludge stream are determined by using a mass balance for each component. The flow rates for over- and underflow are calculated through a mass balance, where the sludge flow rate is assumed to be proportional to the influent sludge flow rate.

<figure markdown="span">
  ![Primary clarifier flowchart](../../assets/images/primary_clarifier_flowchart.drawio.svg)
  <figcaption markdown="1">Flowchart of the Otterpohl model[^1]<br>(pu: primary underflow; po: primary overflow; pc: primary clarifier)</figcaption>
</figure>


### Equations

#### COD removal efficiency

$$
\eta_{COD_p}(\mathrm{t}) = f_{corr}(2.88 f_x - 0.118) - (1.45 + 6.15 ln( t_h(\mathrm{t}) \cdot 24 \cdot 60))
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $\eta_{COD_p}$ | COD (chemical oxygen demand) removal efficiency in percent | - |
| $f_{corr}$ | Dimensionless correction factor for the COD removal efficiency | - |
| $f_x$  | Mean fraction of particulate COD | - |
| $t_h(\mathrm{t})$ | Hydraulic retention time | d |


#### Primary effluent concentration of each state variable

$$
f_i = 1 - \frac{\eta_{COD_p}}{100} f_{SX,i}
$$

| Symbol | Description | Unit |
| ------ | ----------- | ---- |
| $f_i$  | Primary effluent concentration of each state variable in percent | - |
| $f_{SX,i}$ | Structural factor defining the fraction of particulate matter of each | - |

- $f_{SX,i} = 0$ for all soluble components

- $0 < f_{SX,i} \ll 1$ for all particulate fractions

- In the benchmark case, all the particulate state factors are set to 1.


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [primclar_bsm2](/reference/bsm2_python/bsm2/primclar_bsm2)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [primclarinit_bsm2](/reference/bsm2_python/bsm2/init/primclarinit_bsm2)


[^1]: [Benchmarking of Control Strategies for Wastewater Treatment Plants](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf), chap. 4.2.4.1 Primary clarifier
[^2]: [Benchmark Simulation Model no. 2 (BSM2)](http://iwa-mia.org/wp-content/uploads/2022/09/TR3_BSM_TG_Tech_Report_no_3_BSM2_General_Description.pdf), chap. 4. Modeling of the primary clarifier
