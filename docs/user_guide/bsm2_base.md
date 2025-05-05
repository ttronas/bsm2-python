

# BSM2-base plant documentation

This documentation of BSM2-Python's base class `bsm2_base.py` will guide you through the source code and
help you to better understand the wastewater treatment plant layout of BSM2-Python.


### Initialization

Initialization of wastewater treatment plant objects.

<div class="annotate" markdown>

```python title="bsm2_base.py", linenums="79"
--8<-- "bsm2_base.py:79:81"
```

- Initiates *Splitter* `input_splitter` and `bypass_plant` (1)

```python title="bsm2_base.py", linenums="82"
--8<-- "bsm2_base.py:82:92"
```

- Initiates *Combiner* `combiner_primclar_pre` (6)
- Initiates *PrimaryClarifier* `primclar` (11) with
  initial parameters of `primclarinit` (12) and `asm1init` (14)
- Initiates *Combiner* `combiner_primclar_post` (7)


```python title="bsm2_base.py", linenums="93"
--8<-- "bsm2_base.py:93:145"
```

- Initiates *Splitter* `bypass_reactor` (2)
- Initiates *Combiner* `combiner_reactor` (8)
- Initiates first, second, third, fourth and fifth *ASM1Reactor* `reactor1`, `reactor2`, `reactor3`, `reactor4` and `reactor5` (13) with
  initial parameters of `asm1init` (15) and `reginit` (17)
- Initiates *Splitter* `splitter_reactor` (3)

```python title="bsm2_base.py", linenums="146"
--8<-- "bsm2_base.py:146:157"
```

- Initiates *Settler* `settler` (18) with
  initial parameters of `settler1dinit` (19) and `asm1init` (16)
- Initiates *Combiner* `combiner_effluent` (9)

```python title="bsm2_base.py", linenums="158"
--8<-- "bsm2_base.py:158:159"
```

- Initiates *Thickener* `thickener` (20) with
  initial parameters of `thickenerinit` (21)
- Initiates *Splitter* `splitter_thickener` (4)

```python title="bsm2_base.py", linenums="160"
--8<-- "bsm2_base.py:160:163"
```

- Initiates *Combiner* `combiner_adm1` (10)
- Initiates *ADM1Reactor* `adm1_reactor` (22) with
  initial parameters of `adm1init` (23)

```python title="bsm2_base.py", linenums="164"
--8<-- "bsm2_base.py:164:164"
```

- Initiates *Dewatering* `dewatering` (24) with
  initial parameters of `dewateringinit` (25)

```python title="bsm2_base.py", linenums="165"
--8<-- "bsm2_base.py:165:166"
```

- Initiates *Storage* `storage` (26) with
  initial parameters of `storageinit` (27)
- Initiates *Splitter* `splitter_storage` (5)

</div>

1.  *[Splitter class]*
2.  *[Splitter class]*
3.  *[Splitter class]*
4.  *[Splitter class]*
5.  *[Splitter class]*
6.  *[Combiner class]*
7.  *[Combiner class]*
8.  *[Combiner class]*
9.  *[Combiner class]*
10.  *[Combiner class]*
11.  *[PrimaryClarifier class]*
12.  Initialization file of the primary clarifier *[primclarinit_bsm2]*
13.  *[ASM1Reactor class]*
14.  Initialization file of the activated sludge reactor system *[asm1init_bsm2]*
15.  Initialization file of the activated sludge reactor system *[asm1init_bsm2]*
16.  Initialization file of the activated sludge reactor system *[asm1init_bsm2]*
17.  Initialization file for bypass control, K~L~a values and carbon flows *[reginit_bsm2]*
18.  *[Settler class]*
19.  Initialization file of the settler *[settler1dinit_bsm2]*
20.  *[Thickener class]*
21.  Initialization file of the thickener *[thickenerinit_bsm2]*
22.  *[ADM1Reactor class]*
23.  Initialization file of the anaerobic digester *[adm1init_bsm2]*
24.  *[Dewatering class]*
25.  Initialization file of the dewatering unit *[dewateringinit_bsm2]*
26.  *[Storage class]*
27.  Initialization file of the wastewater storage *[storageinit_bsm2]*

---

### Simulation loop

In the simulation loop wastewater treatment plant objects are connected with each other through wastewater and sludge streams.

Most wastewater and sludge flows in BSM2 are represented in the ASM1 (Activated Sludge Model No. 1) format as an array, containing 21 standard parameters (concentrations, flow rate, temperature and dummy states) to describe the stream.

<div class="annotate" markdown>

```python title="bsm2_base.py", linenums="304"
--8<-- "bsm2_base.py:304:309"
```

- `y_in_timestep`: Wastewater stream that goes into the plant influent
- `iqi`: Influent quality index of the plant influent for evaluation of the wastewater purity (40)

```python title="bsm2_base.py", linenums="310"
--8<-- "bsm2_base.py:310:311"
```

Splitters of type 1 (default) separate streams into multiple by a given split ratio and splitters of type 2 separate single streams into two, if a given flow rate threshold is exceeded.

=== "**Object** *Splitter* `input_splitter`"
    Splitter after plant influent, that splits when plant influent is overflowing; Type 2 *Splitter* with flow rate threshold of 60000 m³/d (1)

    | Input/Output (18) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_in_timestep` | Wastewater stream that goes into the plant influent |
    | Output | `yp_in_c` | Wastewater stream that goes to the primary clarifier *Combiner* `combiner_primclar_pre` |
    | Output | `y_in_bp` | Bypassed wastewater stream that goes to the *Splitter* `bypass_plant` |

=== "**Object** *Splitter* `bypass_plant`"
    Bypass splitter, that directs the overflow either to the activated sludge system or directly to the plant effluent, in case of an overflowing plant influent (default: activated sludge system); Type 1 *Splitter* with split ratio (2)

    | Input/Output (19) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_in_bp` | Bypassed wastewater stream from the plant influent *Splitter* `input_splitter` |
    | Output | `y_plant_bp` | Bypassed wastewater stream that goes to the plant effluent *Combiner* `combiner_effluent` |
    | Output | `y_in_as_c` | Bypassed wastewater stream that goes to activated sludge system *Combiner* `combiner_primclar_post` |

```python title="bsm2_base.py", linenums="312"
--8<-- "bsm2_base.py:312:313"
```

=== "**Object** *Combiner* `combiner_primclar_pre`"
    Combiner before primary clarifier

    | Input/Output (24) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yp_in_c` | Wastewater stream from the plant influent *Splitter* `input_splitter` |
    | Input | `yst_sp_p` | Wastewater stream from the wastewater storage *Splitter* `splitter_storage` |
    | Input | `yt_sp_p` | Wastewater stream from the thickener *Splitter* `splitter_thickener` |
    | Output | `yp_in` | Combined wastewater stream that goes into the *PrimaryClarifier* `primclar` |

=== "**Object** *PrimaryClarifier* `primclar`"
    Separates wastewater into two streams - primary effluent (overflow) and primary sludge (underflow) (3)

    | Input/Output (29) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yp_in` | Combined wastewater stream from the plant influent *Combiner* `combiner_primclar_pre` |
    | Output | `yp_uf` | Primary sludge (underflow) that goes to the anaerobic digester *Combiner* `combiner_adm1` |
    | Output | `yp_of` | Primary effluent (overflow) that goes to the activated sludge system *Combiner* `combiner_primclar_post` |
    | - | `yp_internal` | Internal wastewater for evaluation purposes |

```python title="bsm2_base.py", linenums="314"
--8<-- "bsm2_base.py:314:315"
```

=== "**Object** *Combiner* `combiner_primclar_post`"
    Combiner after primary clarifier

    | Input/Output (25) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yp_of` | Primary effluent (overflow) from the *PrimaryClarifier* `primclar` |
    | Input | `y_in_as_c` | Bypassed wastewater stream from the plant influent *Splitter* `bypass_plant` |
    | Output | `y_c_as_bp` | Wastewater stream that goes to the *Splitter* `bypass_reactor` |

=== "**Object** *Splitter* `bypass_reactor`"
    Bypass splitter before activated sludge system, that bypasses the entire primary clarifier effluent to the plant effluent if activated (default: not activated); Type 1 *Splitter* with split ratio (4)

    | Input/Output (20) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_c_as_bp` | Combined wastewater stream from the post primary clarifier *Splitter* `combiner_primclar_post` |
    | Output | `y_bp_as` | Wastewater stream that goes to the activated sludge system *Combiner* `combiner_reactor` |
    | Output | `y_as_bp_c_eff` | Bypassed wastewater stream that goes to the plant effluent *Combiner* `combiner_effluent` |

```python title="bsm2_base.py", linenums="317"
--8<-- "bsm2_base.py:317:325"
```

=== "**Object** *Combiner* `combiner_reactor`"
    Combiner before activated sludge system

    | Input/Output (26) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `ys_r` | Returned sludge stream from the *Settler* `settler` |
    | Input | `y_bp_as` | Wastewater stream from the post primary clarifier *Splitter* `combiner_primclar_post` |
    | Input | `yst_sp_as` | Wastewater stream from wastewater storage *Splitter* `splitter_storage` |
    | Input | `yt_sp_as` | Wastewater stream from the thickener *Splitter* `splitter_thickener` |
    | Input | `y_out5_r` | Wastewater stream from the post activated sludge system *Splitter* `splitter_reactor` |
    | Output | `y_in1` | Wastewater stream that goes into the first *ASM1Reactor* `reactor1` |

=== "**Object** *ASM1Reactor* `reactor1`"
    Activated sludge reactor with anoxic conditions (K~L~a = 0) for removal of nitrogen (denitrification) (5)

    | Input/Output (30) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_in1` | Combined wastewater stream from the *Combiner* `combiner_reactor` |
    | Output | `y_out1` | Wastewater stream that goes into the second *ASM1Reactor* `reactor2` |

=== "**Object** *ASM1Reactor* `reactor2`"
    Activated sludge reactor with anoxic conditions (K~L~a = 0) for denitrification (6)

    | Input/Output (31) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_out1` | Wastewater stream from the first *ASM1Reactor* `reactor1` |
    | Output | `y_out2` | Wastewater stream that goes into the third *ASM1Reactor* `reactor3` |

=== "**Object** *ASM1Reactor* `reactor3`"
    Activated sludge reactor with aerobic conditions (K~L~a = 120) for carbon decomposition and nitrification (7)

    | Input/Output (32) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_out2` | Wastewater stream from the second *ASM1Reactor* `reactor2` |
    | Output | `y_out3` | Wastewater stream that goes into the fourth *ASM1Reactor* `reactor4` |

=== "**Object** *ASM1Reactor* `reactor4`"
    Activated sludge reactor with aerobic conditions (K~L~a = 120) for carbon decomposition and nitrification (8)

    | Input/Output (33) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_out3` | Wastewater stream from the third *ASM1Reactor* `reactor3` |
    | Output | `y_out4` | Wastewater stream that goes into the fifth *ASM1Reactor* `reactor5` |

=== "**Object** *ASM1Reactor* `reactor5`"
    Activated sludge reactor with aerobic conditions (K~L~a = 60) for carbon decomposition and nitrification (9)

    | Input/Output (34) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_out4` | Wastewater stream from the fourth *ASM1Reactor* `reactor4` |
    | Output | `y_out5` | Wastewater stream that goes to the post activated sludge *Splitter* `splitter_reactor` |

=== "**Object** *Splitter* `splitter_reactor`"
    Splitter after activated sludge system, for internal sludge recirculation; Type 1 Splitter with split ratio (10)

    | Input/Output (21) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_out5` | Wastewater stream from the fifth *ASM1Reactor* `reactor5` | 
    | Output | `ys_in` | Wastewater stream that goes into the *Settler* `settler` |
    | Output | `y_out5_r` | Internal recirculation stream that goes back to the activated sludge system *Combiner* `combiner_reactor` |

```python title="bsm2_base.py", linenums="327"
--8<-- "bsm2_base.py:327:327"
```

=== "**Object** *Settler* `settler`"
    Separates wastewater into two streams - effluent (overflow) and sludge (underflow) (11)

    | Input/Output (35) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `ys_in` | Wastewater stream from the post activated sludge *Splitter* `splitter_reactor` |
    | Output | `ys_r` | Returned sludge stream that goes to the activated sludge system *Combiner* `combiner_reactor` |
    | Output | `ys_was` | Waste sludge stream that goes into the *Thickener* `thickener` |
    | Output | `ys_of` | Wastewater stream that goes to the plant effluent *Combiner* `combiner_effluent` |
    | Output | `_` | Sludge height for evaluation purposes (not used) |
    | Output | `ys_tss_internal` | Internal total suspended solids (TSS) states of the settler for evaluation purposes |

```python title="bsm2_base.py", linenums="329"
--8<-- "bsm2_base.py:329:332"
```

- `eqi`: Effluent quality index of the plant effluent for evaluation of the wastewater purity (41)

=== "**Object** *Combiner* `combiner_effluent`"
    Combiner before the plant effluent

    | Input/Output (27) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `y_plant_bp` | Bypassed wastewater stream from the plant influent *Splitter* `bypass_plant` |
    | Input | `y_as_bp_c_eff` | Bypassed wastewater stream from the pre activated sludge system *Splitter* `bypass_reactor` |
    | Input | `ys_of` | Wastewater stream from the *Settler* `settler` |
    | Output | `y_eff` | Wastewater stream that goes in the plant effluent |

```python title="bsm2_base.py", linenums="334"
--8<-- "bsm2_base.py:334:337"
```

=== "**Object** *Thickener* `thickener`"
    Separates the stream into residual effluent (overflow) and thickened sludge (underflow) (12)

    | Input/Output (36) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `ys_was` | Waste sludge stream from the *Settler* `settler` |
    | Output | `yt_uf` | Thickened sludge (underflow) that goes to the anaerobic digester *Combiner* `combiner_adm1` |
    | Output | `yt_of` | Residual effluent (overflow) that goes to the post thickener *Splitter* `splitter_thickener` |

=== "**Object** *Splitter* `splitter_thickener`"
    Splitter after thickener, that directs the entire flow either to the primary clarifier or to the activated sludge system (default: primary clarifier); Type 1 Splitter with split ratio (13)

    | Input/Output (22) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yt_of` | Residual effluent (overflow) from the *Thickener* `thickener` |
    | Output | `yt_sp_p` | Residual effluent (overflow) that goes to the pre primary clarifier *Combiner* `combiner_primclar_pre`
    | Output | `yt_sp_as` | Residual effluent (overflow) that goes to the pre activated sludge system *Combiner* `combiner_reactor` |

```python title="bsm2_base.py", linenums="339"
--8<-- "bsm2_base.py:339:340"
```

=== "**Object** *Combiner* `combiner_adm1`"
    Combiner before anaerobic digester

    | Input/Output (28) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yt_uf` | Thickened sludge (underflow) from the *Thickener* `thickener` |
    | Input | `yp_uf` | Primary sludge (underflow) from the *PrimaryClarifier* `primclar` |
    | Output | `yd_in` | Combined sludge stream that goes into the *ADM1Reactor* `adm1_reactor` |

=== "**Object** *ADM1Reactor* `adm1_reactor`"
    Breaks down sewage sludge to produce methane gas (14)

    | Input/Output (37) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yd_in` | Combined sludge stream from the anaerobic digester *Combiner* `combiner_adm1` |
    | Output | `yi_out2` | Fermented sludge stream (ASM1 format) that goes into the *Dewatering* `dewatering` |
    | Output | `yd_out` | Fermented sludge stream (ADM1 format) for evaluation purposes |
    | Output | `_` | Combined sludge stream (turned in ADM1 format) from the anaerobic digester *Combiner* `combiner_adm1` (not used) |

```python title="bsm2_base.py", linenums="341"
--8<-- "bsm2_base.py:341:346"
```

=== "**Object** *Dewatering* `dewatering`"
    Separates the stream into reject wastewater (overflow) and dewatered/waste sludge (underflow) (15)

    | Input/Output (38) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yi_out2` | Fermented sludge stream from the *ADM1Reactor* `adm1_reactor` |
    | Output | `ydw_s` | Dewatered/waste sludge (underflow) that leaves the plant |
    | Output | `ydw_r` | Reject wastewater (overflow) that goes into the *Storage* `storage` |

=== "**Object** *Storage* `storage`"
    Holds reject wastewater before recycling it back to either primary clarifier or the activated sludge system (16)

    | Input/Output (39) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `ydw_r` | Reject wastewater (overflow) from the *Dewatering* `dewatering` |
    | Output | `yst_out` | Stored wastewater that goes to the post storage *Splitter* `splitter_storage` |
    | Output | `yst_vol` | Volume of the storage tank for evaluation purposes |

=== "**Object** *Splitter* `splitter_storage`"
    Splitter after wastewater storage, that directs the entire flow either to the primary clarifier or to the activated sludge system (default: primary clarifier); Type 1 Splitter with split ratio (17)

    | Input/Output (23) | Variable | Description |
    |--------------|----------|-------------|
    | Input | `yst_out` | Stored wastewater from the *Storage* `storage` |
    | Output | `yst_sp_p` | Stored wastewater that goes to the pre primary clarifier *Combiner* `combiner_primclar_pre` |
    | Output | `yst_sp_as` | Stored wastewater that goes to the activated sludge system *Combiner* `combiner_reactor` |

</div>

1.  Threshold from initialization file *[reginit_bsm2]*
2.  Bypass control from initialization file *[reginit_bsm2]*
3.  Further information in the [Primary Clarifier documentation]
4.  Bypass control from initialization file *[reginit_bsm2]*
5.  Further information in the [Activated Sludge Reactor documentation]
6.  Further information in the [Activated Sludge Reactor documentation]
7.  Further information in the [Activated Sludge Reactor documentation]
8.  Further information in the [Activated Sludge Reactor documentation]
9.  Further information in the [Activated Sludge Reactor documentation]
10.  Split ratio from initialization file *[asm1init_bsm2]*
11.  Further information in the [Settler documentation]
12.  Further information in the [Thickener documentation]
13.  Split control from initialization file *[reginit_bsm2]*
14.  Further information in the [Anaerobic Digester documentation]
15.  Further information in the [Dewatering documentation]
16.  Further information in the [Storage documentation]
17.  Split control from initialization file *[reginit_bsm2]*
18.  Also see method *[Splitter.output]*
19.  Also see method *[Splitter.output]*
20.  Also see method *[Splitter.output]*
21.  Also see method *[Splitter.output]*
22.  Also see method *[Splitter.output]*
23.  Also see method *[Splitter.output]*
24.  Also see method *[Combiner.output]*
25.  Also see method *[Combiner.output]*
26.  Also see method *[Combiner.output]*
27.  Also see method *[Combiner.output]*
28.  Also see method *[Combiner.output]*
29.  Also see method *[PrimaryClarifier.output]*
30.  Also see method *[ASM1Reactor.output]*
31.  Also see method *[ASM1Reactor.output]*
32.  Also see method *[ASM1Reactor.output]*
33.  Also see method *[ASM1Reactor.output]*
34.  Also see method *[ASM1Reactor.output]*
35.  Also see method *[Settler.output]*
36.  Also see method *[Thickener.output]*
37.  Also see method *[ADM1Reactor.output]*
38.  Also see method *[Dewatering.output]*
39.  Also see method *[Storage.output]*
40.  See method *[PlantPerformance.iqi]*
41.  See method *[PlantPerformance.eqi]*

---

### Evaluation

Evaluation of plant performance and wastewater treatment parameters.

```python title="bsm2_base.py", linenums="348"
--8<-- "bsm2_base.py:348:409"
```

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
