---
hide:
  - toc
---

![Splitter](../../../assets/icons/bsm2python/splitter.svg){ align=right }
![Combiner](../../../assets/icons/bsm2python/combiner.svg){ align=right }

### Introduction and Model

The combiner and splitter are simple components used to either combine multiple wastewater flows into a single stream or split one wastewater flow into multiples streams. The resulting streams are assumed to be evenly mixed. Flows are represented in ASM1 (Activated Sludge Model No. 1) format as arrays containing 21 standard parameters:

$$
\left[S_I, S_S, X_I, X_S, X_{BH}, X_{BA}, X_P, S_O, S_{NO}, S_{NH}, S_{ND}, X_{ND}, S_{ALK}, TSS, Q, T, S_{D1}, S_{D2}, S_{D3}, X_{D4}, X_{D5}\right]
$$

The components are defined as follows:

- State variable concentrations of 13 ASM1 components: $[S_I, S_S, X_I, X_S, X_{BH}, X_{BA}, X_P, S_O, S_{NO}, S_{NH}, S_{ND}, X_{ND}, S_{ALK}]$

- TSS: Total suspended solids

- Q: Flow rate

- T: Temperature

- 5 dummy states: $[S_{D1}, S_{D2}, S_{D3}, X_{D4}, X_{D5}]$

For detailed information about the state variable concentrations visit the documentation for the [activated sludge reactor](../activated_sludge_reactor).


### Source code documentation

<span style=
  "color: #0550ae;
  font-weight: bold;
  font-size: .85em;
  background-color: #0550ae1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
class</span> [Combiner](/reference/bsm2_python/bsm2/helpers_bsm2/#bsm2_python.bsm2.helpers_bsm2.Combiner)

<span style=
  "color: #0550ae;
  font-weight: bold;
  font-size: .85em;
  background-color: #0550ae1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
class</span> [Splitter](/reference/bsm2_python/bsm2/helpers_bsm2/#bsm2_python.bsm2.helpers_bsm2.Splitter)
