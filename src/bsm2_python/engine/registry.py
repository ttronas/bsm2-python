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
        def step(self, dt, current_step, inputs): return {"out_main": self.y}
    return InfluentAdapter(y)

@register("effluent")
def make_effluent(node_id: str, params: Dict[str, Any]):
    class EffluentAdapter:
        def __init__(self): 
            self.last = None
        def step(self, dt, current_step, inputs):
            # Store the last input for retrieval
            main_input = inputs.get("in_main")
            if main_input is not None:
                self.last = main_input.copy()
            return {}
    return EffluentAdapter()

@register("combiner")
def make_combiner(node_id: str, params: Dict[str, Any]):
    Combiner = get_combiner()
    impl = Combiner()
    class CombinerAdapter:
        def step(self, dt, current_step, inputs):
            # Use BSM2 Combiner.output which does the right flow combination
            flows = [v for _, v in sorted(inputs.items()) if v is not None]
            if len(flows) == 0:
                return {"out_combined": np.zeros(21)}
            elif len(flows) == 1:
                result = flows[0].copy()
            else:
                # Call the real BSM2 Combiner.output method
                result = impl.output(*flows)
            
            return {"out_combined": result}
    return CombinerAdapter()

@register("splitter")
def make_splitter(node_id: str, params: Dict[str, Any]):
    # Import resolve_value from the correct module
    try:
        from .param_resolver import resolve_value
    except ImportError:
        # Fallback implementation
        def resolve_value(val):
            if isinstance(val, str) and "." in val:
                # Simple fallback - return a default value
                if "QBYPASS" in val:
                    return 3000.0
                elif "QINTR" in val:
                    return 55338.0
                elif "SP_" in val:
                    return 0.5
                return 1.0
            return val
    
    Splitter = get_splitter()
    
    # Handle mode-based splitter configuration - only threshold and split_ratio modes
    mode = params.get("mode", "split_ratio")  # Default to split_ratio mode
    
    if mode == "threshold":
        # BSM2 bypass splitter: Type 2 splitter with flow threshold
        impl = Splitter(sp_type=2)
        threshold = resolve_value(params.get("threshold", 0.0))
        target = params.get("target", "out_b")
        
        class ThresholdSplitterAdapter:
            def __init__(self, impl, threshold, target):
                self.impl = impl
                self.threshold = float(threshold)
                self.target = target
                
            def step(self, dt, current_step, inputs):
                x = inputs.get("in_main")
                if x is None: return {}
                
                # BSM2OL bypass logic: everything above threshold goes to target output
                try:
                    a, b = self.impl.output(x, (0.0, 0.0), self.threshold)
                    return {"out_a": a, "out_b": b}
                except Exception as e:
                    # Fallback for edge cases
                    return {"out_a": x, "out_b": x * 0}
                
        return ThresholdSplitterAdapter(impl, threshold, target)
    
    else:  # mode == "split_ratio" or default
        # Standard splitter with split ratios - handles both regular splitting and recycle logic
        impl = Splitter(sp_type=1)
        splitratio = params.get("splitratio", [0.5, 0.5])
        
        # Support special case for internal recycle via parameters
        qintr = params.get("qintr", None)
        
        # Resolve parameter references in splitratio
        if isinstance(splitratio, list):
            resolved_ratio = []
            for ratio in splitratio:
                resolved_ratio.append(float(resolve_value(ratio)))
            splitratio = tuple(resolved_ratio)
        
        class SplitRatioSplitterAdapter:
            def __init__(self, impl, splitratio, qintr):
                self.impl = impl
                self.splitratio = splitratio
                self.qintr = float(resolve_value(qintr)) if qintr is not None else None
                
            def step(self, dt, current_step, inputs):
                x = inputs.get("in_main")
                if x is None: return {}
                
                # Special handling for reactor recycle if qintr is specified
                if self.qintr is not None:
                    # BSM reactor recycle: split based on internal recycle flow
                    input_flow = x[14]  # Q is at index 14
                    if input_flow <= 0:
                        return {"out_to_settler": x * 0, "out_recycle_to_combiner": x * 0}
                    
                    # Calculate flows: recycle gets fixed qintr, rest goes to settler
                    flow_to_settler = max(input_flow - self.qintr, 0.0)
                    flow_to_recycle = min(self.qintr, input_flow)
                    
                    # Create output streams
                    out_to_settler = x.copy()
                    out_to_settler[14] = flow_to_settler
                    
                    out_to_recycle = x.copy()
                    out_to_recycle[14] = flow_to_recycle
                    
                    return {"out_to_settler": out_to_settler, "out_recycle_to_combiner": out_to_recycle}
                
                else:
                    # Standard split ratio logic
                    try:
                        # Use BSM2 splitter logic with ratios
                        outputs = self.impl.output(x, self.splitratio)
                        result = {}
                        if len(outputs) >= 1:
                            result["out_a"] = outputs[0]
                        if len(outputs) >= 2:
                            result["out_b"] = outputs[1]
                        return result
                    except Exception as e:
                        # Fallback for edge cases
                        return {"out_a": x * 0.5, "out_b": x * 0.5}
                
        return SplitRatioSplitterAdapter(impl, splitratio, qintr)

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
        def step(self, dt, current_step, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            # CRITICAL FIX: Pass the correct current_step instead of hardcoded 0
            y_out = self.impl.output(dt, current_step, y_in)
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
            self.sludge_height = 0.0
            self.ys_tss_internal = np.zeros(10)
        def step(self, dt, current_step, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            # CRITICAL FIX: Pass the correct current_step instead of hardcoded 0
            ras, was, eff, sludge_height, tss_internal = self.impl.output(dt, current_step, y_in)
            
            # Store settler outputs for later retrieval
            self.sludge_height = sludge_height
            self.ys_tss_internal = tss_internal
            
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
        def __init__(self, impl):
            self.impl = impl
        def step(self, dt, current_step, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            # FIXED: Primary clarifier returns 3 outputs
            underflow, overflow, internal = self.impl.output(dt, current_step, y_in)
            return {
                "out_primary_sludge": underflow,
                "out_primary_effluent": overflow
            }
    return PrimClarAdapter(impl)

@register("thickener")
def make_thickener(node_id: str, params: Dict[str, Any]):
    Thickener = get_thickener()
    impl = Thickener(params["THICKENERPAR"])
    class ThickenerAdapter:
        def __init__(self, impl):
            self.impl = impl
        def step(self, dt, current_step, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            underflow, overflow = self.impl.output(y_in)
            return {
                "out_thickened": underflow,
                "out_supernatant": overflow
            }
    return ThickenerAdapter(impl)

@register("digester")
def make_adm1(node_id: str, params: Dict[str, Any]):
    ADM1Reactor = get_adm1_reactor()
    impl = ADM1Reactor(
        params["DIGESTERINIT"], params["DIGESTERPAR"],
        params["INTERFACEPAR"], params["DIM_D"]
    )
    
    # Get the operational temperature parameter from reginit_bsm2
    try:
        import bsm2_python.bsm2.init.reginit_bsm2 as reginit
        t_op = reginit.T_OP  # 35 + 273.15 K (operational temperature)
    except:
        t_op = 308.15  # Fallback: 35°C + 273.15 = 308.15 K
    
    class ADM1Adapter:
        def __init__(self, impl, t_op):
            self.impl = impl
            self.t_op = t_op
        def step(self, dt, current_step, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            # CRITICAL FIX: Pass correct t_op temperature parameter instead of None
            out0, out1, out2 = self.impl.output(dt, current_step, y_in, self.t_op)
            return {"out_digested": out0, "out_gas": out1, "out_liquid": out2}
    return ADM1Adapter(impl, t_op)

@register("dewatering")
def make_dewatering(node_id: str, params: Dict[str, Any]):
    Dewatering = get_dewatering()
    impl = Dewatering(params["DEWATERINGPAR"])
    class DewateringAdapter:
        def __init__(self, impl):
            self.impl = impl
        def step(self, dt, current_step, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            cake, reject = self.impl.output(y_in)
            return {"out_cake": cake, "out_filtrate": reject}
    return DewateringAdapter(impl)

@register("sink")
def make_sink(node_id: str, params: Dict[str, Any]):
    class SinkAdapter:
        def __init__(self):
            self.last = None
        def step(self, dt, current_step, inputs):
            # Store the last input for retrieval but don't output anything
            main_input = inputs.get("in_main")
            if main_input is not None:
                self.last = main_input.copy()
            return {}
    return SinkAdapter()

@register("storage")
def make_storage(node_id: str, params: Dict[str, Any]):
    Storage = get_storage()
    impl = Storage(
        params["VOL_S"], params["ystinit"],
        params.get("tempmodel", False), params.get("activate", False)
    )
    # Get QSTORAGE from parameters or use reginit default
    qstorage = params.get("QSTORAGE", None)
    if qstorage is None:
        try:
            import bsm2_python.bsm2.init.reginit_bsm2 as reginit
            qstorage = reginit.QSTORAGE  # Default is 0
        except:
            qstorage = 0  # Fallback default
    
    class StorageAdapter:
        def __init__(self, impl, qstorage):
            self.impl = impl
            self.qstorage = qstorage
        def step(self, dt, current_step, inputs):
            y_in = inputs.get("in_main")
            if y_in is None: return {}
            out, _ = self.impl.output(dt, current_step, y_in, self.qstorage)
            return {"out_main": out}
    return StorageAdapter(impl, qstorage)