---
hide:
  - toc
---

![Biogas storage](../../assets/icons/bsm2python/biogas-storage.svg){ align=right }

### Introduction and Model

The biogas storage temporarily retains sewage gas produced from the anaerobic digester, holding it until it is needed by components of the energy management system, such as combined heat and power (CHP) units or boilers. Sewage gas typically contains 60-70% methane gas with the remainder primarily consisting of carbon dioxide. 

The implementation assumes a non-reactive storage tank with variable volume and complete mixing. The gas composition of the stored biogas depends on the composition of the influent gas stream. The tank's behavior depends upon the influent flow rate from the anaerobic digester, the available storage volume and the outflow rate due to demand from CHP units and boilers. The influent flow to the biogas storage can either be bypassed to the flare if the storage tank is full or stored if there is sufficient capacity. The following cases are assumed:

- Full (100%): When the tank is at maximum capacity, the influent flow is automatically bypassed to the flare.
- Partial capacity (0-100%): When the tank has available capacity, the influent flow is stored.
- Empty (0%): When the tank is empty, the influent flow is stored as well.


### Source code documentation

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [storage](/reference/bsm2_python/energy_management/storage)

<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span> [storage_init](/reference/bsm2_python/energy_management/init/storage_init)
