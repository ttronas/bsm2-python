from __future__ import annotations
from typing import Dict, Any, Callable
import numpy as np
import sys
import os
import importlib.util

# Lazy loading of BSM2 components to avoid circular imports
_components_cache = {}

def _lazy_load_component(module_path, class_name):
    """Lazy load BSM2 components to avoid circular imports."""
    cache_key = f"{module_path}.{class_name}"
    if cache_key not in _components_cache:
        try:
            # Get the full path relative to the src directory
            src_dir = os.path.join(os.path.dirname(__file__), '..', '..')
            full_path = os.path.join(src_dir, module_path.replace('.', os.sep) + '.py')
            
            spec = importlib.util.spec_from_file_location(module_path, full_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            _components_cache[cache_key] = getattr(module, class_name)
        except Exception as e:
            print(f"Warning: Could not load {class_name} from {module_path}: {e}")
            # Return a mock class for now
            class MockComponent:
                def __init__(self, *args, **kwargs):
                    self.args = args
                    self.kwargs = kwargs
                def output(self, *args): return np.zeros(21)
                def outputs(self, *args): return np.zeros(21), np.zeros(21)
            _components_cache[cache_key] = MockComponent
    
    return _components_cache[cache_key]

def get_asm1_reactor():
    return _lazy_load_component('bsm2_python.bsm2.asm1_bsm2', 'ASM1Reactor')

def get_combiner():
    return _lazy_load_component('bsm2_python.bsm2.helpers_bsm2', 'Combiner')

def get_splitter():
    return _lazy_load_component('bsm2_python.bsm2.helpers_bsm2', 'Splitter')

def get_settler():
    return _lazy_load_component('bsm2_python.bsm2.settler1d_bsm2', 'Settler')

def get_primary_clarifier():
    return _lazy_load_component('bsm2_python.bsm2.primclar_bsm2', 'PrimaryClarifier')

def get_thickener():
    return _lazy_load_component('bsm2_python.bsm2.thickener_bsm2', 'Thickener')

def get_adm1_reactor():
    return _lazy_load_component('bsm2_python.bsm2.adm1_bsm2', 'ADM1Reactor')

def get_dewatering():
    return _lazy_load_component('bsm2_python.bsm2.dewatering_bsm2', 'Dewatering')

def get_storage():
    return _lazy_load_component('bsm2_python.bsm2.storage_bsm2', 'Storage')

Factory = Callable[[str, Dict[str, Any]], Any]
REGISTRY: Dict[str, Factory] = {}

def register(kind: str):
    def deco(fn: Factory):
        REGISTRY[kind] = fn
        return fn
    return deco

# Hilfsfunktion: sichere Vektor-Addition
def _sum_vectors(values):
    acc = None
    for v in values:
        if v is None: continue
        acc = v if acc is None else acc + v
    return acc

@register("influent_static")
def make_influent(node_id: str, params: Dict[str, Any]):
    y = np.array(params["y_in_constant"], dtype=float)
    class InfluentAdapter:
        def __init__(self, y): self.y = y
        def step(self, dt, inputs): return {"out_main": self.y}
    return InfluentAdapter(y)

@register("effluent")
def make_effluent(node_id: str, params: Dict[str, Any]):
    class EffluentAdapter:
        def __init__(self): self.last = None
        def step(self, dt, inputs):
            self.last = inputs.get("in_main")
            return {}
    return EffluentAdapter()

@register("combiner")
def make_combiner(node_id: str, params: Dict[str, Any]):
    Combiner = get_combiner()
    impl = Combiner()
    class CombinerAdapter:
        def step(self, dt, inputs):
            # Reicht alle vorhandenen Eingänge an Combiner weiter
            # Erwartet Summation über beliebige Anzahl Ströme
            flows = [v for _, v in sorted(inputs.items())]
            y = _sum_vectors(flows)
            # Falls Combiner eine Methode erfordert, hier anpassen
            return {"out_combined": y}
    return CombinerAdapter()

@register("splitter")
def make_splitter(node_id: str, params: Dict[str, Any]):
    Splitter = get_splitter()
    impl = Splitter()
    fractions = params.get("fractions", (0.5, 0.5))
    q_bypass = params.get("q_bypass", None)
    class SplitterAdapter:
        def __init__(self, impl, fractions, q_bypass):
            self.impl = impl
            self.fractions = fractions
            self.q_bypass = q_bypass
        def step(self, dt, inputs):
            x = inputs.get("in_main")
            if x is None: return {}
            # Splitter returns a list, not tuple
            result_list = self.impl.output(x, self.fractions, self.q_bypass or 0)
            if len(result_list) >= 2:
                a, b = result_list[0], result_list[1]
            else:
                a, b = result_list[0] if result_list else x, x
            # Map to different output handles
            return {"out_to_settler": a, "out_recycle_to_combiner": b}
    return SplitterAdapter(impl, fractions, q_bypass)

@register("reactor")
def make_asm1reactor(node_id: str, params: Dict[str, Any]):
    ASM1Reactor = get_asm1_reactor()
    impl = ASM1Reactor(
        params["KLA"], params["VOL"], params["YINIT"], params["PAR"],
        params["CARB"], params["CARBONSOURCECONC"],
        tempmodel=params.get("tempmodel", False),
        activate=params.get("activate", False),
    )
    class ReactorAdapter:
        def __init__(self, impl):
            self.impl = impl
        def step(self, dt, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            y_out = self.impl.output(dt, 0, y_in)  # (dt, step, y_in) — step wird außerhalb geführt
            return {"out_main": y_out}
    return ReactorAdapter(impl)

@register("settler")
def make_settler(node_id: str, params: Dict[str, Any]):
    Settler = get_settler()
    impl = Settler(
        params["DIM"], params["LAYER"], params["QR"], params["QW"],
        params["settlerinit"], params["SETTLERPAR"], params["PAR_ASM"],
        params.get("tempmodel_settler", False), params["MODELTYPE_SETTLER"]
    )
    class SettlerAdapter:
        def __init__(self, impl):
            self.impl = impl
        def step(self, dt, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            ras, was, eff, sludge_height, tss_internal = self.impl.output(dt, 0, y_in)
            return {
                "out_sludge_recycle": ras,
                "out_sludge_waste": was,
                "out_effluent": eff
            }
    return SettlerAdapter(impl)

@register("primary_clarifier")
def make_primaryclar(node_id: str, params: Dict[str, Any]):
    PrimaryClarifier = get_primary_clarifier()
    impl = PrimaryClarifier(
        params["VOL_P"], params["YINIT"], params["PAR_P"], params["PAR_ASM"],
        params["XVECTOR_P"], tempmodel=params.get("tempmodel", False),
        activate=params.get("activate", False)
    )
    class PrimClarAdapter:
        def step(self, dt, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            underflow, overflow = impl.outputs(dt, 0, y_in)
            return {
                "out_primary_sludge": underflow,
                "out_primary_effluent": overflow
            }
    return PrimClarAdapter()

@register("thickener")
def make_thickener(node_id: str, params: Dict[str, Any]):
    Thickener = get_thickener()
    impl = Thickener(params["THICKENERPAR"])
    class ThickenerAdapter:
        def step(self, dt, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            underflow, overflow = impl.outputs(y_in)
            return {
                "out_thickened": underflow,
                "out_supernatant": overflow
            }
    return ThickenerAdapter()

@register("digester")
def make_adm1(node_id: str, params: Dict[str, Any]):
    ADM1Reactor = get_adm1_reactor()
    impl = ADM1Reactor(
        params["DIGESTERINIT"], params["DIGESTERPAR"],
        params["INTERFACEPAR"], params["DIM_D"]
    )
    class ADM1Adapter:
        def step(self, dt, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            out0, out1, out2 = impl.outputs(dt, 0, y_in, None)
            return {"out_digested": out0, "out_gas": out1, "out_liquid": out2}
    return ADM1Adapter()

@register("dewatering")
def make_dewatering(node_id: str, params: Dict[str, Any]):
    Dewatering = get_dewatering()
    impl = Dewatering(params["DEWATERINGPAR"])
    class DewateringAdapter:
        def step(self, dt, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            cake, reject = impl.outputs(y_in)
            return {"out_cake": cake, "out_filtrate": reject}
    return DewateringAdapter()

@register("storage")
def make_storage(node_id: str, params: Dict[str, Any]):
    Storage = get_storage()
    impl = Storage(
        params["VOL_S"], params["ystinit"],
        params.get("tempmodel", False), params.get("activate", False)
    )
    qstorage = params.get("QSTORAGE", None)
    class StorageAdapter:
        def __init__(self, qstorage): self.qstorage = qstorage
        def step(self, dt, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            out, _ = impl.output(dt, 0, y_in, self.qstorage)
            return {"out_main": out}
    return StorageAdapter(qstorage)