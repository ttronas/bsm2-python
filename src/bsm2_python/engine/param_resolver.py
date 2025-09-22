# src/bsm2_python/engine/param_resolver.py
from __future__ import annotations
import importlib
from typing import Any

def resolve_value(val: Any) -> Any:
    """
    Löst Strings wie 'asm1init.KLA1' oder 'settler1dinit.DIM' gegen Module unter bsm2_python.bsm2.init.* auf.
    Andere Typen werden durchgereicht.
    """
    if isinstance(val, str) and "." in val:
        modname, attr = val.split(".", 1)
        try:
            # Try the BSM1 init modules first for backwards compatibility
            if modname == "asm1init":
                mod = importlib.import_module("bsm2_python.bsm2.init.asm1init_bsm1")
            elif modname == "settler1dinit":
                mod = importlib.import_module("bsm2_python.bsm2.init.settler1dinit_bsm2")
            else:
                # Try the generic pattern
                mod = importlib.import_module(f"bsm2_python.bsm2.init.{modname}")
            return getattr(mod, attr)
        except (ModuleNotFoundError, AttributeError):
            # Fallback: try other variations
            try:
                mod = importlib.import_module(f"bsm2_python.init.{modname}")
                return getattr(mod, attr)
            except (ModuleNotFoundError, AttributeError):
                raise ValueError(f"Could not resolve parameter: {val}")
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