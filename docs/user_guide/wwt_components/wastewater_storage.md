---
hide:
  - toc
---

![Wastewater storage](https://gitlab.rrze.fau.de/evt/klaeffizient/bsm2-python/-/raw/doc_new2/docs/assets/.icons/bsm2python/wastewater-storage.svg){ align=right }
<!-- TODO: change link to main branch before merging -->

### Introduction and Model

The wastewater storage...

The reject water from the dewatering unit can be recycled to a non-reactive storage tank prior to being recycled to the process stream. The storage tank behaviour depends upon the flow rate from the dewatering unit, the available storage volume and the fate of the stored reject water. It is assumed that the effluent flow from the storage tank will be equal to the influent flow if the tank is full, equal to a defined pumped flow if less than full and equal to the influent flow if completely empty. The effluent flow should not exceed a reasonable rate, to avoid unrealistic instantaneous emptying of the tank and the flow is directed to either
the primary clarifier influent or effluent as defined by the user.


This implements a simple storage tank of variable volume with complete mix.

No biological reactions. Dummy states are included.

`tempmodel` defines how temperature changes in the input affect the liquid temperature.
It also defines rules for a potential necessary bypass of the storage tank.

`activate` used to activate dummy states. See documentation by Dr Marie-Noelle Pons.

If liquid volume > 90% of total volume then automatically bypass flow.
If liquid volume < 10% of total volume then automatically input flow.
Storage output and automatic bypass streams are joined in a Combiner afterwards.


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
