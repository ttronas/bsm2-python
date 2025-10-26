# BSM1/BSM2 Parameter Detection System

## Overview

The BSM2-Python engine automatically detects whether a configuration is for BSM1 or BSM2 and loads the appropriate variant-specific parameters. This allows the same configuration structure to work with different parameter sets depending on the detected model variant.

## How It Works

### 1. Variant Detection

The `SimulationEngine` automatically detects the variant using the `_detect_variant()` method with the following strategy (in priority order):

1. **Filename Detection**: Check if the config filename contains "bsm1" or "bsm2"
   - Example: `bsm1_ol_config.json` → BSM1
   - Example: `bsm2_ol_config.json` → BSM2

2. **Explicit Metadata**: Check the configuration for explicit variant specification
   ```json
   {
     "meta": {
       "variant": "bsm1"
     }
   }
   ```

3. **Component Analysis**: Detect BSM2-specific components
   - Components like `digester`, `primary_clarifier`, `thickener`, `dewatering`, `storage` indicate BSM2
   - If any BSM2-specific component is found, the variant is BSM2

4. **Default**: If none of the above match, defaults to BSM1

### 2. Parameter Resolution

Once the variant is detected, parameter strings like `"asm1init.KLA3"` are resolved to actual values using the `resolve_value()` function in `param_resolver.py`.

**Module Priority Order:**
- **BSM1**: Tries `module_bsm1.py` first, then falls back to `module_bsm2.py`
- **BSM2**: Tries `module_bsm2.py` first, then falls back to `module_bsm1.py`

**Example:**
```python
# For BSM1 config:
"asm1init.KLA3" → Resolves to 240 (from asm1init_bsm1.py)

# For BSM2 config:
"reginit.KLA3" → Resolves to 120 (from reginit_bsm2.py)
```

## Parameter File Structure

Parameters are organized in variant-specific init files under `src/bsm2_python/bsm2/init/`:

- `asm1init_bsm1.py` - BSM1-specific ASM1 parameters
- `asm1init_bsm2.py` - BSM2-specific ASM1 parameters
- `reginit_bsm1.py` - BSM1-specific reactor parameters
- `reginit_bsm2.py` - BSM2-specific reactor parameters
- `settler1dinit_bsm2.py` - Settler parameters (common to both)
- etc.

## Key Differences Between BSM1 and BSM2

### Oxygen Transfer Coefficients (KLA)
- **BSM1**: Higher aeration rates
  - KLA3 = 240 d⁻¹
  - KLA4 = 240 d⁻¹
  - KLA5 = 84 d⁻¹

- **BSM2**: Lower aeration rates
  - KLA3 = 120 d⁻¹
  - KLA4 = 120 d⁻¹
  - KLA5 = 60 d⁻¹

### Internal Recirculation
- **BSM1**: `QINTR = 3 * QIN0 = 55,338 m³/d`
- **BSM2**: Uses bypass control with `QBYPASS = 60,000 m³/d`

### Additional Components
- **BSM1**: Simple layout with 5 reactors + settler
- **BSM2**: Extended layout with:
  - Primary clarifier
  - Thickener
  - Anaerobic digester (ADM1)
  - Dewatering
  - Storage tank

## Example Configurations

### BSM1 Configuration Excerpt
```json
{
  "id": "reactor3",
  "component_type_id": "reactor",
  "parameters": {
    "KLA": "asm1init.KLA3",
    "VOL": "asm1init.VOL3",
    "YINIT": "asm1init.YINIT3",
    "PAR": "asm1init.PAR3"
  }
}
```
When loaded with BSM1 detection, `"asm1init.KLA3"` resolves to `240`.

### BSM2 Configuration Excerpt
```json
{
  "id": "reactor3",
  "component_type_id": "reactor",
  "parameters": {
    "KLA": "reginit.KLA3",
    "VOL": "asm1init.VOL3",
    "YINIT": "asm1init.YINIT3",
    "PAR": "asm1init.PAR3"
  }
}
```
When loaded with BSM2 detection, `"reginit.KLA3"` resolves to `120`.

## Testing

The parameter detection system is tested in `tests/test_json_engine.py`:
- BSM1 test verifies correct parameter loading for BSM1 configuration
- BSM2 test verifies correct parameter loading for BSM2 configuration
- Results are compared against reference implementations to ensure accuracy

## Implementation Files

- **`src/bsm2_python/engine/engine.py`**: Contains `_detect_variant()` method
- **`src/bsm2_python/engine/param_resolver.py`**: Contains `resolve_value()` and module priority logic
- **`src/bsm2_python/bsm2/init/*_bsm1.py`**: BSM1-specific parameters
- **`src/bsm2_python/bsm2/init/*_bsm2.py`**: BSM2-specific parameters

## Adding New Parameters

To add variant-specific parameters:

1. Create/update the appropriate init file (e.g., `mymodule_bsm1.py`, `mymodule_bsm2.py`)
2. Define your parameters in the file
3. Reference them in your JSON config as `"mymodule.PARAMETER_NAME"`
4. The parameter resolver will automatically load the correct variant

Example:
```python
# In mymodule_bsm1.py
MY_PARAM = 100

# In mymodule_bsm2.py
MY_PARAM = 200
```

Then in your config:
```json
{
  "parameters": {
    "my_value": "mymodule.MY_PARAM"
  }
}
```

The value will be 100 for BSM1 configs and 200 for BSM2 configs.
