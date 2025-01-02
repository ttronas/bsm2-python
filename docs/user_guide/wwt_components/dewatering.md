---
hide:
  - toc
---

![Dewatering](https://gitlab.rrze.fau.de/evt/klaeffizient/bsm2-python/-/raw/doc_new2/docs/assets/.icons/bsm2python/dewatering.svg){ align=right }
<!-- TODO: change link to main branch before merging -->

### Introduction and Model

The dewatering unit reduces the volume of sludge from the sludge digestion before disposal, separating the stream into reject wastewater (overflow) and dewatered sludge (underflow). The implementation is based on an idealized dewatering unit with no volume, as the dewatering unit is not considered a critical component. A defined amount of total solids are removed (98&nbsp;%) from the influent sludge stream and directed to the underflow, while the remaining solids will leave with the overflow. The underflow is assumed to have a fixed sludge concentration of 28&nbsp;%. With these two constrains, the model calculates the flow rate for the underflow. Mass balances are then used to calculate the concentrations and the flow rate for the overflow. The model does not alter the concentrations of soluble components as they pass through the dewatering unit.


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [dewatering_bsm2](/reference/bsm2_python/bsm2/dewatering_bsm2)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [dewateringinit_bsm2](/reference/bsm2_python/bsm2/init/dewateringinit_bsm2)


[^1]: [Benchmarking of Control Strategies for Wastewater Treatment Plants](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf), chap. 4.2.4.4 Dewatering unit