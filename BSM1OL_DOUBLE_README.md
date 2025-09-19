# BSM1OL Double Implementation

This document describes the implementation of `BSM1OLDouble`, which creates two parallel WWTPs connected to one effluent.

## Files Created

### 1. `src/bsm2_python/bsm1_ol_double.py`
Main implementation file containing the `BSM1OLDouble` class that extends `BSM1Base`.

**Key Features:**
- Two complete parallel WWTP systems (each with 5 reactors, combiner, splitter, and settler)
- Input flow is split equally (50/50) between the two WWTPs
- Final effluent combines outputs from both WWTPs
- Independent operation of both WWTPs with separate sludge recycle streams
- Proper energy calculations that sum individual WWTP contributions
- Complete data tracking for both WWTPs

### 2. `bsm1_ol_double_simulation_config.json`
JSON configuration file for the doubled setup, analogous to `bsm1_simulation_config.json`.

**Structure:**
- Input splitter to divide influent between two WWTPs
- Complete node definitions for both WWTP systems
- Final combiner to merge effluents
- Proper edge connections maintaining separation between WWTPs

### 3. `tests/bsm1_ol_double_test.py`
Comprehensive test suite for the new implementation.

**Tests Include:**
- Basic functionality verification
- Flow rate conservation checks
- Parallel operation validation
- Sludge height reasonableness checks

## Architecture

```
Influent → Input Splitter
                    ├─→ WWTP1 (5 Reactors + Settler) ─┐
                    └─→ WWTP2 (5 Reactors + Settler) ─┤
                                                      ├─→ Final Combiner → Effluent
```

### WWTP1 Components:
- `combiner1` → `reactor1_1` → `reactor2_1` → `reactor3_1` → `reactor4_1` → `reactor5_1` → `splitter1` → `settler1`

### WWTP2 Components:
- `combiner2` → `reactor1_2` → `reactor2_2` → `reactor3_2` → `reactor4_2` → `reactor5_2` → `splitter2` → `settler2`

## Usage

```python
from bsm2_python.bsm1_ol_double import BSM1OLDouble
import numpy as np

# Example influent data
y_in = np.array([
    [0.0, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
    [200.1, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
])

# Create and run simulation
bsm1_double = BSM1OLDouble(data_in=y_in, timestep=15/(60*24), endtime=200)

for idx, _ in enumerate(bsm1_double.simtime):
    bsm1_double.step(idx)

# Access results
final_effluent = bsm1_double.final_effluent
wwtp1_effluent = bsm1_double.ys_eff
wwtp2_effluent = bsm1_double.ys_eff_2
```

## Key Implementation Details

### Flow Distribution
- Input flow is split equally (50/50) between WWTPs
- Each WWTP processes half the total influent
- Final effluent combines both WWTP outputs

### Energy Calculations
- Aeration energy: Sum of individual WWTP aeration energies
- Mixing energy: Sum of individual WWTP mixing energies  
- Pumping energy: Accounts for doubled flow rates

### Data Structures
- All original BSM1Base arrays track WWTP1
- New arrays with `_2` suffix track WWTP2
- `final_effluent_all` tracks the combined output

### Recycle Streams
- Each WWTP maintains independent sludge recycle
- No cross-contamination between WWTP systems
- Proper flow balancing within each WWTP

## Testing

Run the test suite:
```bash
python tests/bsm1_ol_double_test.py
```

The tests verify:
- Flow conservation (final effluent = WWTP1 + WWTP2)
- Reasonable sludge heights for both WWTPs
- Proper flow distribution (each WWTP gets ~50% of input)
- Energy scaling compared to single WWTP

## Validation

The implementation has been validated against the original BSM1OL:
- Flow rates are properly conserved
- Energy consumption scales appropriately (~2x for two WWTPs)
- Effluent quality is maintained
- Performance metrics are reasonable