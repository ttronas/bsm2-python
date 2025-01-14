---
hide:
  - toc
---

![Wastewater storage](https://gitlab.rrze.fau.de/evt/klaeffizient/bsm2-python/-/raw/doc_new2/docs/assets/.icons/bsm2python/wastewater-storage.svg){ align=right }
<!-- TODO: change link to main branch before merging -->

### Introduction and Model

The wastewater storage holds reject wastewater from the dewatering unit before recycling it back into the wastewater treatment process, either at the primary clarifier influent or effluent. The implementation assumes a non-reactive storage tank with variable volume and complete mixing. The tank's behaviour depends upon the flow rate from the dewatering unit, the available storage volume and the destination of the stored reject water. The influent flow to the storage tank can either be bypassed if the storage tank is nearly full or stored if there is sufficient capacity. The following cases are assumed:

- If the tank volume is $\ge$ 90% of total capacity, the influent flow is automatically bypassed.
- If the tank volume is between 10% and 90% of total capacity, the influent flow is automatically stored.
- If the tank volume is $\le$ 10% of total capacity, the influent flow is also automatically stored.


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [storage_bsm2](/reference/bsm2_python/bsm2/storage_bsm2)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [storageinit_bsm2](/reference/bsm2_python/bsm2/init/storageinit_bsm2)

[^1]: [Benchmarking of Control Strategies for Wastewater Treatment Plants](https://iwaponline.com/ebooks/book-pdf/650794/wio9781780401171.pdf), chap. 4.2.4.5 Reject water storage tank
[^2]: [Benchmark Simulation Model no. 2 (BSM2)](http://iwa-mia.org/wp-content/uploads/2022/09/TR3_BSM_TG_Tech_Report_no_3_BSM2_General_Description.pdf), chap. 6. Modeling of the reject water storage tank
