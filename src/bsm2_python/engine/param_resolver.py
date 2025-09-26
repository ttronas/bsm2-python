from __future__ import annotations
import importlib
import importlib.util
import os
from typing import Any


def resolve_value(val: Any) -> Any:
    """
    Löst Strings wie 'asm1init.KLA1' oder 'settler1dinit.DIM' gegen Module unter bsm2_python.bsm2.init.* auf.
    Andere Typen werden durchgereicht.
    """
    if isinstance(val, str) and "." in val:
        modname, attr = val.split(".", 1)

        try:
            # Pfad zur init-Modulebene ermitteln
            src_dir = os.path.join(os.path.dirname(__file__), "..", "..")

            # bsm1 vs bsm2 Varianten versuchen
            module_filename = f"{modname}_bsm1.py" if modname == "asm1init" else f"{modname}.py"
            module_path = os.path.join(src_dir, "bsm2_python", "bsm2", "init", module_filename)

            if not os.path.exists(module_path):
                module_filename = f"{modname}_bsm2.py"
                module_path = os.path.join(src_dir, "bsm2_python", "bsm2", "init", module_filename)

            if os.path.exists(module_path):
                spec = importlib.util.spec_from_file_location(f"bsm2_python.bsm2.init.{modname}", module_path)
                mod = importlib.util.module_from_spec(spec)
                assert spec.loader is not None
                spec.loader.exec_module(mod)
                return getattr(mod, attr)
            else:
                mod = importlib.import_module(f"bsm2_python.bsm2.init.{modname}")
                return getattr(mod, attr)
        except Exception as e:
            print(f"Warning: Could not resolve {val}: {e}")
            # Sinnvolle Defaults
            if "KLA" in attr:
                return 240.0  # Default KLA
            elif "VOL" in attr:
                return 1000.0  # Default Volumen
            elif "YINIT" in attr:
                import numpy as np
                return np.array([
                    30, 1.15, 51.2, 202.32, 28.17, 0, 0, 2, 0, 31.56,
                    6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0
                ])
            elif "PAR" in attr:
                import numpy as np
                return np.array([4.0, 20.0, 0.67, 0.24, 0.08, 0.04, 2.0, 8.0, 0.5, 0.3])
            elif "CARB" in attr:
                return 0.0
            elif "CARBONSOURCECONC" in attr:
                return 0.0
            elif "Q" in attr:
                return 18446.0
            elif "MODELTYPE" in attr:
                return 0
            elif "DIM" in attr:
                import numpy as np
                return np.array([1.0, 1.0])
            elif "LAYER" in attr:
                import numpy as np
                return np.array([10.0, 10])
            elif "settlerinit" in attr:
                import numpy as np
                return np.zeros(10)
            elif "SETTLERPAR" in attr:
                import numpy as np
                return np.array([0.00013, 0.000576, 2.0, 0.5, 0.00228, 7.0, 4.0, 2.4])
            else:
                return 1.0

    return val


def resolve_params(params: dict) -> dict:
    out = {}
    for k, v in params.items():
        if isinstance(v, list):
            out[k] = [resolve_value(x) for x in v]
        elif isinstance(v, dict):
            out[k] = resolve_params(v)
        else:
            out[k] = resolve_value(v)
    return out