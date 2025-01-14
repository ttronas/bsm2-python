---
hide:
  - toc
---

![Thickener](../../assets/icons/bsm2python/thickener.svg){ align=right }

### Introduction and Model

The thickener reduces the volume of wasted sludge from the settler before sludge digestion, separating the stream into residual effluent (overflow) and thickened sludge (underflow). The implementation is based on an idealized thickener unit with no volume, as the thickener is not considered a critical component. A defined amount of total solids are removed (98&nbsp;%) from the influent stream and directed to the underflow, while the remaining solids will leave with the overflow. The underflow is assumed to have a fixed sludge concentration of 7&nbsp;%. With these two constraints, the model calculates the flow rate for the underflow. Mass balances are then used to calculate the concentrations and the flow rate for the overflow. The model does not alter the concentrations of soluble components as they pass through the thickener.


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [thickener_bsm2](/reference/bsm2_python/bsm2/thickener_bsm2)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [thickenerinit_bsm2](/reference/bsm2_python/bsm2/init/thickenerinit_bsm2)


[^1]: [Benchmarking of Control Strategies for Wastewater Treatment Plants](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf), chap. 4.2.4.3 Thickener
[^2]: [Benchmark Simulation Model no. 2 (BSM2)](http://iwa-mia.org/wp-content/uploads/2022/09/TR3_BSM_TG_Tech_Report_no_3_BSM2_General_Description.pdf), chap. 5.1 Thickener
