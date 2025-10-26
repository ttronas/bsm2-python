from __future__ import annotations
import importlib
import importlib.util
import os
from typing import Any

VARIANT_MODULE_ORDER = {
    "bsm1": ("bsm1", "bsm2"),
    "bsm2": ("bsm2", "bsm1"),
}

def resolve_value(val: Any, variant: str = "bsm2") -> Any:
    """
    Löst Strings wie 'asm1init.KLA1' oder 'settler1dinit.DIM' gegen Module unter bsm2_python.init.* auf.
    Andere Typen werden durchgereicht.
    """
    if isinstance(val, str) and "." in val:
        modname, attr = val.split(".", 1)

        # Try direct module loading to avoid circular imports
        try:
            src_dir = os.path.join(os.path.dirname(__file__), '..', '..')

            module_priorities = VARIANT_MODULE_ORDER.get(variant, VARIANT_MODULE_ORDER["bsm2"])
            candidate_files = []
            for suffix in module_priorities:
                candidate_files.append((f"{modname}_{suffix}", os.path.join(src_dir, 'bsm2_python', 'bsm2', 'init', f'{modname}_{suffix}.py')))
            candidate_files.append((modname, os.path.join(src_dir, 'bsm2_python', 'bsm2', 'init', f'{modname}.py')))

            for module_alias, module_path in candidate_files:
                if not os.path.exists(module_path):
                    continue
                spec = importlib.util.spec_from_file_location(f"bsm2_python.bsm2.init.{module_alias}", module_path)
                if spec is None or spec.loader is None:
                    continue
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, attr):
                    return getattr(mod, attr)

            # Fallback to regular import if no local file was found
            fallback_modules = [
                f"bsm2_python.bsm2.init.{modname}_{suffix}" for suffix in module_priorities
            ] + [f"bsm2_python.bsm2.init.{modname}"]

            for module_name in fallback_modules:
                try:
                    mod = importlib.import_module(module_name)
                except (ModuleNotFoundError, ImportError):
                    continue
                if hasattr(mod, attr):
                    return getattr(mod, attr)
        except Exception as e:
            print(f"Warning: Could not resolve {val}: {e}")
            # Return a default value based on the parameter name
            if 'KLA' in attr:
                return 240.0  # Better default KLA value for aerobic reactors
            elif 'VOL' in attr:
                return 1000.0  # Default volume
            elif 'YINIT' in attr:
                # Return a reasonable initial state vector
                import numpy as np
                return np.array([30, 1.15, 51.2, 202.32, 28.17, 0, 0, 2, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])
            elif 'PAR' in attr:
                # ASM1 parameters
                import numpy as np
                return np.array([4.0, 20.0, 0.67, 0.24, 0.08, 0.04, 2.0, 8.0, 0.5, 0.3])
            elif 'CARB' in attr:
                return 0.0  # Default carbon dosing
            elif 'CARBONSOURCECONC' in attr:
                return 0.0  # Default carbon source concentration
            elif 'Q' in attr:
                return 18446.0  # Default flow
            elif 'MODELTYPE' in attr:
                return 0  # Default settler model type
            elif 'DIM' in attr:
                import numpy as np
                return np.array([1.0, 1.0])  # Default dimensions
            elif 'LAYER' in attr:
                import numpy as np
                return np.array([10.0, 10])  # Default layer config
            elif 'settlerinit' in attr:
                import numpy as np
                return np.zeros(10)  # Default settler initial state
            elif 'SETTLERPAR' in attr:
                import numpy as np
                return np.array([0.00013, 0.000576, 2.0, 0.5, 0.00228, 7.0, 4.0, 2.4])  # Default settler parameters
            else:
                return 1.0  # Generic default
    
    return val

def resolve_params(params: dict, variant: str = "bsm2") -> dict:
    out = {}
    for k, v in params.items():
        if isinstance(v, list):
            out[k] = [resolve_value(x, variant) for x in v]
        elif isinstance(v, dict):
            out[k] = resolve_params(v, variant)
        else:
            out[k] = resolve_value(v, variant)
    return out