

# BSM2-base plant documentation

This documentation of BSM2-Python's base class `bsm2_base.py` will guide you through the source code and
help you to better understand the wastewater treatment plant layout of BSM2-Python.


## Initialization

The initialization of the wastewater treatment plant objects and variables takes place in the definition of the `__init__`.

```python title="bsm2_base.py", linenums="73"
--8<-- "bsm2_base.py:73:83"
```

Initialization of the `BSM2Base` object with default parameters, setting up the simulation environment for the BSM2 model.

```python title="bsm2_base.py", linenums="93"
--8<-- "bsm2_base.py:93:94"
```

- Initiates *[Splitter]* `input_splitter` and `bypass_plant`

```python title="bsm2_base.py", linenums="95"
--8<-- "bsm2_base.py:95:105"
```

- Initiates *[Combiner]* `combiner_primclar_pre`
- Initiates *[PrimaryClarifier]* `primclar` with
  initial parameters of <code>[primclarinit_bsm2]</code> and <code>[asm1init_bsm2]</code>
- Initiates *[Combiner]* `combiner_primclar_post`


```python title="bsm2_base.py", linenums="106"
--8<-- "bsm2_base.py:106:158"
```

- Initiates *[Splitter]* `bypass_reactor`
- Initiates *[Combiner]* `combiner_reactor`
- Initiates first, second, third, fourth and fifth *[ASM1Reactor]* `reactor1`, `reactor2`, `reactor3`, `reactor4` and `reactor5` with
  initial parameters of <code>[asm1init_bsm2]</code> and <code>[reginit_bsm2]</code>
- Initiates *[Splitter]* `splitter_reactor`

```python title="bsm2_base.py", linenums="159"
--8<-- "bsm2_base.py:159:170"
```

- Initiates *[Settler]* `settler` with
  initial parameters of <code>[settler1dinit_bsm2]</code> and <code>[asm1init_bsm2]</code>
- Initiates *[Combiner]* `combiner_effluent`

```python title="bsm2_base.py", linenums="171"
--8<-- "bsm2_base.py:171:172"
```

- Initiates *[Thickener]* `thickener` with
  initial parameters of <code>[thickenerinit_bsm2]</code>
- Initiates *[Splitter]* `splitter_thickener`

```python title="bsm2_base.py", linenums="173"
--8<-- "bsm2_base.py:173:176"
```

- Initiates *[Combiner]* `combiner_adm1`
- Initiates *[ADM1Reactor]* `adm1_reactor` with
  initial parameters of <code>[adm1init_bsm2]</code>

```python title="bsm2_base.py", linenums="177"
--8<-- "bsm2_base.py:177:177"
```

- Initiates *[Dewatering]* `dewatering` with
  initial parameters of <code>[dewateringinit_bsm2]</code>

```python title="bsm2_base.py", linenums="178"
--8<-- "bsm2_base.py:178:179"
```

- Initiates *[Storage]* `storage` with
  initial parameters of <code>[storageinit_bsm2]</code>
- Initiates *[Splitter]* `splitter_storage`

---

Initialization of evaluation objects and variables to collect data for later evaluation.

```python title="bsm2_base.py", linenums="181"
--8<-- "bsm2_base.py:181:181"
```

- Initializes a *[PlantPerformance]* object `performance` with
  initial parameters of <code>[plantperformanceinit_bsm2]</code>

```python title="bsm2_base.py", linenums="183"
--8<-- "bsm2_base.py:183:210"
```

Initializes arrays and variables for the wastewater or sludge streams that flow between the wastewater treatment plant objects.

```python title="bsm2_base.py", linenums="212"
--8<-- "bsm2_base.py:212:246"
```

Initializes arrays to collect data from the wastewater or sludge streams that are to be evaluated later.

```python title="bsm2_base.py", linenums="248"
--8<-- "bsm2_base.py:248:248"
```

- Initializes `klas` array with all the K~L~a values for every activated sludge reactor
  with initial parameters of <code>[reginit_bsm2]</code>

```python title="bsm2_base.py", linenums="252"
--8<-- "bsm2_base.py:252:252"
```

- Initializes `sludge_height` variable for the continuous signal of sludge blanket level of the *[Settler]* object `settler`

```python title="bsm2_base.py", linenums="254"
--8<-- "bsm2_base.py:254:262"
```

Initializes variables for aeration energy, pumping energy and mixing energy and heat demand that are evaluated later on. Also initializes arrays for the collection of the influent quality index, effluent quality index, operation cost index, performance factors and violation data.

```python title="bsm2_base.py", linenums="264"
--8<-- "bsm2_base.py:264:265"
```

- Defines `y_out5_r[14]`, the flow rate of the internal recirculation after the fifth activated sludge reactor
  with initial parameters of <code>[asm1init_bsm2]</code>

---

## Simulation loop

The simulation loop is defined in the `step` method, where wastewater treatment plant objects are connected with each other through wastewater and sludge streams.

Most wastewater and sludge flows in BSM2 are represented in the ASM1 (Activated Sludge Model No. 1) format as an array, containing 21 standard parameters (concentrations, flow rate, temperature and dummy states) to describe the stream. For more information visit the documentation of the [combiner and splitter](../user_guide/bsm2_python_components/wwt_components/combiner_and_splitter.md).

```python title="bsm2_base.py", linenums="267"
--8<-- "bsm2_base.py:267:267"
```

The `step` method is used for the simulation loop. It simulates one time step of the BSM2 model with the index of the current time step `i`.

```python title="bsm2_base.py", linenums="277"
--8<-- "bsm2_base.py:277:278"
```

These lines set up the current simulation time `step` and the time step size `stepsize` for the `i`&nbsp;th iteration of the simulation.

```python title="bsm2_base.py", linenums="280"
--8<-- "bsm2_base.py:280:280"
```

This ensures that all five reactors are updated with the corresponding oxygen transfer coefficients (`kla` attributes) from the `klas` array.

```python title="bsm2_base.py", linenums="283"
--8<-- "bsm2_base.py:283:283"
```

- Defines the wastewater stream `y_in_timestep` that goes into the plant influent

```python title="bsm2_base.py", linenums="285"
--8<-- "bsm2_base.py:285:286"
```

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.iqi]</code> calculates the influent quality index

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_in_timestep` | Wastewater stream that goes into the plant influent |
    | Output | `iqi` | Influent quality index of the plant influent `y_in_timestep` |

```python title="bsm2_base.py", linenums="288"
--8<-- "bsm2_base.py:288:289"
```

Splitters of type 1 (default) separate streams into multiple by a given split ratio and splitters of type 2 separate single streams into two, if a given flow rate threshold is exceeded.

=== "**Object** *Splitter* `input_splitter`"
    **Method** <code>[Splitter.output]</code>; Splitter after plant influent, that splits when plant influent is overflowing; Type 2 *Splitter* with flow rate threshold of 60000 m³/d from <code>[reginit_bsm2]</code>

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_in_timestep` | Wastewater stream that goes into the plant influent |
    | Output | `yp_in_c` | Wastewater stream that goes to the primary clarifier *[Combiner]* `combiner_primclar_pre` |
    | Output | `y_in_bp` | Bypassed wastewater stream that goes to the *[Splitter]* `bypass_plant` |

=== "**Object** *Splitter* `bypass_plant`"
    **Method** <code>[Splitter.output]</code>; Bypass splitter, that directs the overflow either to the activated sludge system or directly to the plant effluent, in case of an overflowing plant influent (default: activated sludge system); Type 1 *[Splitter]* with split ratio from <code>[reginit_bsm2]</code>

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_in_bp` | Bypassed wastewater stream from the plant influent *[Splitter]* `input_splitter` |
    | Output | `y_plant_bp` | Bypassed wastewater stream that goes to the plant effluent *Combiner* `combiner_effluent` |
    | Output | `y_in_as_c` | Bypassed wastewater stream that goes to activated sludge system *Combiner* `combiner_primclar_post` |

```python title="bsm2_base.py", linenums="290"
--8<-- "bsm2_base.py:290:291"
```

=== "**Object** *Combiner* `combiner_primclar_pre`"
    **Method** <code>[Combiner.output]</code>; Combiner before primary clarifier

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yp_in_c` | Wastewater stream from the plant influent *[Splitter]* `input_splitter` |
    | Input | `yst_sp_p` | Wastewater stream from the wastewater storage *[Splitter]* `splitter_storage` |
    | Input | `yt_sp_p` | Wastewater stream from the thickener *[Splitter]* `splitter_thickener` |
    | Output | `yp_in` | Combined wastewater stream that goes into the *[PrimaryClarifier]* `primclar` |

=== "**Object** *PrimaryClarifier* `primclar`"
    **Method** <code>[PrimaryClarifier.output]</code>; Separates wastewater into two streams - primary effluent (overflow) and primary sludge (underflow); Further information in the [Primary Clarifier documentation]

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yp_in` | Combined wastewater stream from the plant influent *[Combiner]* `combiner_primclar_pre` |
    | Output | `yp_uf` | Primary sludge (underflow) that goes to the anaerobic digester *[Combiner]* `combiner_adm1` |
    | Output | `yp_of` | Primary effluent (overflow) that goes to the activated sludge system *[Combiner]* `combiner_primclar_post` |
    | - | `yp_internal` | Internal wastewater for evaluation purposes |

```python title="bsm2_base.py", linenums="292"
--8<-- "bsm2_base.py:292:293"
```

=== "**Object** *Combiner* `combiner_primclar_post`"
    **Method** <code>[Combiner.output]</code>; Combiner after primary clarifier

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yp_of` | Primary effluent (overflow) from the *[PrimaryClarifier]* `primclar` |
    | Input | `y_in_as_c` | Bypassed wastewater stream from the plant influent *[Splitter]* `bypass_plant` |
    | Output | `y_c_as_bp` | Wastewater stream that goes to the *[Splitter]* `bypass_reactor` |

=== "**Object** *Splitter* `bypass_reactor`"
    **Method** <code>[Splitter.output]</code>; Bypass splitter before activated sludge system, that bypasses the entire primary clarifier effluent to the plant effluent if activated (default: not activated); Type 1 *[Splitter]* with split ratio from <code>[reginit_bsm2]</code>

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_c_as_bp` | Combined wastewater stream from the post primary clarifier *[Splitter]* `combiner_primclar_post` |
    | Output | `y_bp_as` | Wastewater stream that goes to the activated sludge system *[Combiner]* `combiner_reactor` |
    | Output | `y_as_bp_c_eff` | Bypassed wastewater stream that goes to the plant effluent *[Combiner]* `combiner_effluent` |

```python title="bsm2_base.py", linenums="295"
--8<-- "bsm2_base.py:295:301"
```

=== "**Object** *Combiner* `combiner_reactor`"
    **Method** <code>[Combiner.output]</code>; Combiner before activated sludge system

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `ys_r` | Returned sludge stream from the *Settler* `settler` |
    | Input | `y_bp_as` | Wastewater stream from the post primary clarifier *[Splitter]* `combiner_primclar_post` |
    | Input | `yst_sp_as` | Wastewater stream from wastewater storage *[Splitter]* `splitter_storage` |
    | Input | `yt_sp_as` | Wastewater stream from the thickener *[Splitter]* `splitter_thickener` |
    | Input | `y_out5_r` | Wastewater stream from the post activated sludge system *[Splitter]* `splitter_reactor` |
    | Output | `y_in1` | Wastewater stream that goes into the first *[ASM1Reactor]* `reactor1` |

=== "**Object** *ASM1Reactor* `reactor1`"
    **Method** <code>[ASM1Reactor.output]</code>; Activated sludge reactor with anoxic conditions (K~L~a = 0) for removal of nitrogen (denitrification); Further information in the [Activated Sludge Reactor documentation]

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_in1` | Combined wastewater stream from the *[Combiner]* `combiner_reactor` |
    | Output | `y_out1` | Wastewater stream that goes into the second *[ASM1Reactor]* `reactor2` |

=== "**Object** *ASM1Reactor* `reactor2`"
    **Method** <code>[ASM1Reactor.output]</code>; Activated sludge reactor with anoxic conditions (K~L~a = 0) for denitrification; Further information in the [Activated Sludge Reactor documentation]

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_out1` | Wastewater stream from the first *[ASM1Reactor]* `reactor1` |
    | Output | `y_out2` | Wastewater stream that goes into the third *[ASM1Reactor]* `reactor3` |

=== "**Object** *ASM1Reactor* `reactor3`"
    **Method** <code>[ASM1Reactor.output]</code>; Activated sludge reactor with aerobic conditions (K~L~a = 120) for carbon decomposition and nitrification; Further information in the [Activated Sludge Reactor documentation]

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_out2` | Wastewater stream from the second *[ASM1Reactor]* `reactor2` |
    | Output | `y_out3` | Wastewater stream that goes into the fourth *[ASM1Reactor]* `reactor4` |

=== "**Object** *ASM1Reactor* `reactor4`"
    **Method** <code>[ASM1Reactor.output]</code>; Activated sludge reactor with aerobic conditions (K~L~a = 120) for carbon decomposition and nitrification; Further information in the [Activated Sludge Reactor documentation]

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_out3` | Wastewater stream from the third *[ASM1Reactor]* `reactor3` |
    | Output | `y_out4` | Wastewater stream that goes into the fifth *[ASM1Reactor]* `reactor5` |

=== "**Object** *ASM1Reactor* `reactor5`"
    **Method** <code>[ASM1Reactor.output]</code>; Activated sludge reactor with aerobic conditions (K~L~a = 60) for carbon decomposition and nitrification; Further information in the [Activated Sludge Reactor documentation]

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_out4` | Wastewater stream from the fourth *[ASM1Reactor]* `reactor4` |
    | Output | `y_out5` | Wastewater stream that goes to the post activated sludge *[Splitter]* `splitter_reactor` |

=== "**Object** *Splitter* `splitter_reactor`"
    **Method** <code>[Splitter.output]</code>; Splitter after activated sludge system, for internal sludge recirculation; Type 1 Splitter with split ratio from `qintr`

    | I/O (21) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_out5` | Wastewater stream from the fifth *[ASM1Reactor]* `reactor5` | 
    | Output | `ys_in` | Wastewater stream that goes into the *[Settler]* `settler` |
    | Output | `y_out5_r` | Internal recirculation stream that goes back to the activated sludge system *[Combiner]* `combiner_reactor` |

```python title="bsm2_base.py", linenums="303"
--8<-- "bsm2_base.py:303:303"
```

=== "**Object** *Settler* `settler`"
    **Method** <code>[Settler.output]</code>; Separates wastewater into two streams - effluent (overflow) and sludge (underflow); Further information in the [Settler documentation]

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `ys_in` | Wastewater stream from the post activated sludge *[Splitter]* `splitter_reactor` |
    | Output | `ys_r` | Returned sludge stream that goes to the activated sludge system *[Combiner]* `combiner_reactor` |
    | Output | `ys_was` | Waste sludge stream that goes into the *[Thickener]* `thickener` |
    | Output | `ys_of` | Wastewater stream that goes to the plant effluent *[Combiner]* `combiner_effluent` |
    | Output | `_` | Sludge height for evaluation purposes (not used) |
    | Output | `ys_tss_internal` | Internal total suspended solids (TSS) states of the settler for evaluation purposes |

```python title="bsm2_base.py", linenums="305"
--8<-- "bsm2_base.py:305:308"
```

=== "**Object** *Combiner* `combiner_effluent`"
    **Method** <code>[Combiner.output]</code>; Combiner before the plant effluent

    | I/O (27) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_plant_bp` | Bypassed wastewater stream from the plant influent *[Splitter]* `bypass_plant` |
    | Input | `y_as_bp_c_eff` | Bypassed wastewater stream from the pre activated sludge system *[Splitter]* `bypass_reactor` |
    | Input | `ys_of` | Wastewater stream from the *[Settler]* `settler` |
    | Output | `y_eff` | Wastewater stream that goes in the plant effluent |

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.eqi]</code> calculates the effluent quality index

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `ys_of` | Wastewater stream from the *[Settler]* `settler` |
    | Input | `y_plant_bp` | Bypassed wastewater stream from the plant influent *[Splitter]* `bypass_plant` |
    | Input | `y_as_bp_c_eff` | Bypassed wastewater stream from the pre activated sludge system *[Splitter]* `bypass_reactor` |
    | Output | `eqi` | Effluent quality index of the plant effluent |

```python title="bsm2_base.py", linenums="310"
--8<-- "bsm2_base.py:310:313"
```

=== "**Object** *Thickener* `thickener`"
    **Method** <code>[Thickener.output]</code>; Separates the stream into residual effluent (overflow) and thickened sludge (underflow); Further information in the [Thickener documentation]

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `ys_was` | Waste sludge stream from the *Settler* `settler` |
    | Output | `yt_uf` | Thickened sludge (underflow) that goes to the anaerobic digester *[Combiner]* `combiner_adm1` |
    | Output | `yt_of` | Residual effluent (overflow) that goes to the post thickener *[Splitter]* `splitter_thickener` |

=== "**Object** *Splitter* `splitter_thickener`"
    **Method** <code>[Splitter.output]</code>; Splitter after thickener, that directs the entire flow either to the primary clarifier or to the activated sludge system (default: primary clarifier); Type 1 Splitter with split ratio from <code>[reginit_bsm2]</code>

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yt_of` | Residual effluent (overflow) from the *[Thickener]* `thickener` |
    | Output | `yt_sp_p` | Residual effluent (overflow) that goes to the pre primary clarifier *[Combiner]* `combiner_primclar_pre`
    | Output | `yt_sp_as` | Residual effluent (overflow) that goes to the pre activated sludge system *[Combiner]* `combiner_reactor` |

```python title="bsm2_base.py", linenums="315"
--8<-- "bsm2_base.py:315:316"
```

=== "**Object** *Combiner* `combiner_adm1`"
    **Method** <code>[Combiner.output]</code>; Combiner before anaerobic digester

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yt_uf` | Thickened sludge (underflow) from the *[Thickener]* `thickener` |
    | Input | `yp_uf` | Primary sludge (underflow) from the *[PrimaryClarifier]* `primclar` |
    | Output | `yd_in` | Combined sludge stream that goes into the *[ADM1Reactor]* `adm1_reactor` |

=== "**Object** *ADM1Reactor* `adm1_reactor`"
    **Method** <code>[ADM1Reactor.output]</code>; Breaks down sewage sludge to produce methane gas; Further information in the [Anaerobic Digester documentation]

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yd_in` | Combined sludge stream from the anaerobic digester *[Combiner]* `combiner_adm1` |
    | Output | `yi_out2` | Fermented sludge stream (ASM1 format) that goes into the *[Dewatering]* `dewatering` |
    | Output | `yd_out` | Fermented sludge stream (ADM1 format) for evaluation purposes |
    | Output | `_` | Combined sludge stream (turned in ADM1 format) from the anaerobic digester *[Combiner]* `combiner_adm1` (not used) |

```python title="bsm2_base.py", linenums="317"
--8<-- "bsm2_base.py:317:322"
```

=== "**Object** *Dewatering* `dewatering`"
    **Method** <code>[Dewatering.output]</code>; Separates the stream into reject wastewater (overflow) and dewatered/waste sludge (underflow); Further information in the [Dewatering documentation]

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yi_out2` | Fermented sludge stream from the *[ADM1Reactor]* `adm1_reactor` |
    | Output | `ydw_s` | Dewatered/waste sludge (underflow) that leaves the plant |
    | Output | `ydw_r` | Reject wastewater (overflow) that goes into the *[Storage]* `storage` |

=== "**Object** *Storage* `storage`"
    **Method** <code>[Storage.output]</code>; Holds reject wastewater before recycling it back to either primary clarifier or the activated sludge system; Further information in the [Storage documentation]

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `ydw_r` | Reject wastewater (overflow) from the *[Dewatering]* `dewatering` |
    | Output | `yst_out` | Stored wastewater that goes to the post storage *[Splitter]* `splitter_storage` |
    | Output | `yst_vol` | Volume of the storage tank for evaluation purposes |

=== "**Object** *Splitter* `splitter_storage`"
    **Method** <code>[Splitter.output]</code>; Splitter after wastewater storage, that directs the entire flow either to the primary clarifier or to the activated sludge system (default: primary clarifier); Type 1 Splitter with split ratio from <code>[reginit_bsm2]</code>

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yst_out` | Stored wastewater from the *[Storage]* `storage` |
    | Output | `yst_sp_p` | Stored wastewater that goes to the pre primary clarifier *[Combiner]* `combiner_primclar_pre` |
    | Output | `yst_sp_as` | Stored wastewater that goes to the activated sludge system *[Combiner]* `combiner_reactor` |

In the simulation loop data is also collected from each time step to evaluate the plant performance and wastewater treatment parameters.

```python title="bsm2_base.py", linenums="324"
--8<-- "bsm2_base.py:324:333"
```

- Initializes `vol` array with the volume for each activated sludge reactor and the anaerobic digester

```python title="bsm2_base.py", linenums="334"
--8<-- "bsm2_base.py:334:338"
```

- Initializes `sosat` array with the saturated oxygen concentrations for each activated sludge reactor

- Initializes `flows` array with all flow rates that are operated by a pump

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.aerationenergy_step]</code> evaluates the aeration energy of the plant during the evaluation time

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `klas` | Array with all the K~L~a values for the activated sludge reactors |
    | Input | `vol[0:5]` | Array with all the volumes of the activated sludge reactors |
    | Input | `sosat` | Array with the saturated oxygen concentrations for the activated sludge reactors |
    | Output | `ae` | Aeration energy during the evaluation time |

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.pumpingenergy_step]</code> evaluates the pumping energy of the plant during the evaluation time

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `flows` | Array with all the K~L~a values for the activated sludge reactors |
    | Input | `pp_init.PP_PAR[10:16]` | Array with the pumping energy factors for the individual flows from <code>[plantperformanceinit_bsm2]</code> |
    | Output | `pe` | Pumping energy during the evaluation time |

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.mixingenergy_step]</code> evaluates the mixing energy of the plant during the evaluation time

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `klas` | Array with all the K~L~a values for the activated sludge reactors and the anaerobic digester |
    | Input | `vol` | Array with the volume for each activated sludge reactor and the anaerobic digester |
    | Input | `pp_init.PP_PAR[16]` | Mixing energy factor for anaerobic digester unit from <code>[plantperformanceinit_bsm2]</code> |
    | Output | `me` | Pumping energy during the evaluation time |

```python title="bsm2_base.py", linenums="340"
--8<-- "bsm2_base.py:340:353"
```

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.tss_mass_bsm2]</code> calculates the sludge production of the BSM2 plant setup

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yp_of` | Primary clarifier overflow (effluent) concentrations |
    | Input | `yp_uf` | Primary clarifier underflow (sludge) concentrations |
    | Input | `yp_internal` | Primary clarifier internal (basically influent) concentrations |
    | Input | `y_out1` | Concentrations of the 21 components after the first ASM reactor |
    | Input | `y_out2` | Concentrations of the 21 components after the second ASM reactor |
    | Input | `y_out3` | Concentrations of the 21 components after the third ASM reactor |
    | Input | `y_out4` | Concentrations of the 21 components after the fourth ASM reactor |
    | Input | `y_out5` | Concentrations of the 21 components after the fifth ASM reactor |
    | Input | `ys_tss_internal` | Total suspended solids (TSS) concentrations of the internals of the settler |
    | Input | `yd_out` | Concentrations of the 51 components and gas phase parameters after the digester |
    | Input | `yst_out` | Concentrations of the 21 components in the effluent of the storage tank |
    | Input | `yst_vol` | Current volume of the storage tank |
    | Output | `tss_mass` | Sludge production of the BSM2 plant setup |

```python title="bsm2_base.py", linenums="354"
--8<-- "bsm2_base.py:354:355"
```

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.tss_flow]</code> calculates the total suspended solids (TSS) flow out of a reactor

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `ydw_s` | Waste sludge (underflow) concentrations of the dewatering unit |
    | Output | `ydw_s_tss_flow` | Total suspended solids (TSS) flow of the dewatering waste sludge stream |

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.tss_flow]</code> calculates the total suspended solids (TSS) flow out of a reactor

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_eff` | Effluent wastewater stream |
    | Output | `y_eff_tss_flow` | Total suspended solids (TSS) flow of the effluent stream |

```python title="bsm2_base.py", linenums="356"
--8<-- "bsm2_base.py:356:357"
```

- Calculates float variable `carb` with the sum of external carbon flow rate that goes into the activated sludge system from <code>[reginit_bsm2]</code>

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.added_carbon_mass]</code> calculates the total added carbon mass

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `carb` | Sum of external carbon flow rate that goes in AS system |
    | Input | `reginit.CARBONSOURCECONC` | External carbon source concentration from <code>[reginit_bsm2]</code> |
    | Output | `added_carbon_mass` | Total carbon mass added into the AS system |

```python title="bsm2_base.py", linenums="358"
--8<-- "bsm2_base.py:358:359"
```

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.heat_demand_step]</code> calculates the heating demand of the sludge flow to the anaerobic digester

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yd_in` | Sludge stream that goes into the anaerobic digester |
    | Input | `reginit.T_OP` | Operating temperature of the anaerobic digester from <code>[reginit_bsm2]</code> |
    | Output | `heat_demand` | Heat demand of the sludge flow that goes into the anaerobic digester |

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.gas_production]</code> calculates the gas production of the anaerobic digester

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yd_out` | Sludge stream that goes out of the anaerobic digester |
    | Input | `reginit.T_OP` | Operating temperature of the anaerobic digester from <code>[reginit_bsm2]</code> |
    | Output | `ch4_prod` | Methane production of the anaerobic digester |
    | Output | `h2_prod` | Hydrogen production of the anaerobic digester |
    | Output | `co2_prod` | Carbon dioxide production of the anaerobic digester |
    | Output | `q_gas` | Total gas flow rate of the anaerobic digester |

```python title="bsm2_base.py", linenums="362"
--8<-- "bsm2_base.py:362:370"
```

=== "**Object** *PlantPerformance* `performance`"
    **Method** <code>[PlantPerformance.oci]</code> calculates the operational cost index of the plant

    | I/O | Variable | Description |
    |--------------|----------|-------------|
    | Input | `pe * 24` | Pumping energy of the BSM2 plant setup |
    | Input | `ae * 24` | Aeration energy of the BSM2 plant setup |
    | Input | `me * 24` | Mixing energy of the BSM2 plant setup |
    | Input | `ydw_s_tss_flow` | Total suspended solids (TSS) flow of the dewatering waste sludge stream |
    | Input | `added_carbon_mass` | Total carbon mass added into the AS system |
    | Input | `heat_demand * 24` | Heat demand of the sludge flow that goes into the anaerobic digester |
    | Input | `ch4_prod` | Methane production of the anaerobic digester |
    | Input | `q_gas` | Total gas flow rate of the anaerobic digester |
    | Output | `oci_all[i]` | Operational cost index of the plant for a timestep (value is collected for each time step) |

```python title="bsm2_base.py", linenums="372"
--8<-- "bsm2_base.py:372:385"
```

- Collects all performance values for each time step in `perf_factors_all` array. Values are used to calculate the exact performance values at the end of the simulation.

```python title="bsm2_base.py", linenums="387"
--8<-- "bsm2_base.py:387:422"
```

Collecting data for the current time step in arrays.

---

Also see the full source code<br>
<span style=
  "color: #5cad0f;
  font-weight: bold;
  font-size: .85em;
  background-color: #5cad0f1a;
  padding: 0 .3em;
  border-radius: .1rem;
  margin-right: 0.2rem;">
mod</span><code>[bsm2_base.py]</code>


--8<-- "bsm2_links.txt"
