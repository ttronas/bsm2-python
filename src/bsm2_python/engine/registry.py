from __future__ import annotations
from typing import Dict, Any, Callable, List
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
    output_handles: List[str] = list(params.get("__output_handles__", []))
    if not output_handles:
        output_handles = ["out_a", "out_b"]

    raw_mode = params.get("mode")
    fallback_threshold = params.get("q_bypass")
    if fallback_threshold is None:
        fallback_threshold = params.get("qintr")

    if raw_mode is None and fallback_threshold is not None:
        mode = "threshold"
    else:
        mode = str(raw_mode).lower() if raw_mode is not None else "split_ratio"
    if mode not in {"split_ratio", "threshold"}:
        mode = "split_ratio"

    split_ratio_spec = params.get("split_ratio")
    if split_ratio_spec is None:
        split_ratio_spec = params.get("fractions")

    threshold_spec = params.get("threshold")
    target_handle = params.get("target")

    if mode == "threshold" and threshold_spec is None and fallback_threshold is not None:
        threshold_spec = [fallback_threshold]
        if target_handle is None:
            target_handle = output_handles[-1]

    class SplitterAdapter:
        def __init__(self):
            self.node_id = node_id
            self.mode = mode
            self.output_handles = output_handles
            self.target_handle = target_handle
            self.split_ratio_spec = self._to_list(split_ratio_spec)
            self.threshold_spec = self._to_list(threshold_spec)
            self.threshold_mapping = self._map_thresholds()

        @staticmethod
        def _is_blank(value: Any) -> bool:
            return value is None or (isinstance(value, str) and value.strip() == "")

        @staticmethod
        def _to_list(value: Any) -> List[Any]:
            if value is None:
                return []
            if isinstance(value, np.ndarray):
                return value.tolist()
            if isinstance(value, (list, tuple)):
                return list(value)
            return [value]

        def _coerce_float(self, value: Any) -> float | None:
            if self._is_blank(value):
                return None
            if isinstance(value, (int, float, np.floating, np.integer)):
                numeric = float(value)
            elif isinstance(value, str):
                try:
                    numeric = float(value.strip())
                except ValueError as exc:
                    raise ValueError(f"Splitter '{self.node_id}': cannot parse '{value}' as a number.") from exc
            else:
                try:
                    numeric = float(value)
                except Exception as exc:  # noqa: BLE001
                    raise ValueError(f"Splitter '{self.node_id}': cannot convert '{value}' to float.") from exc
            if numeric < 0 or np.isnan(numeric):
                raise ValueError(f"Splitter '{self.node_id}': values must be non-negative numbers.")
            return numeric

        def _map_thresholds(self) -> List[Any]:
            count = len(self.output_handles)
            mapped = ["" for _ in range(count)]
            specs = list(self.threshold_spec)
            if not specs:
                return mapped

            if self.target_handle and self.target_handle in self.output_handles and specs:
                idx = self.output_handles.index(self.target_handle)
                mapped[idx] = specs.pop(0)

            for idx in range(len(mapped)):
                if mapped[idx] == "" and specs:
                    mapped[idx] = specs.pop(0)

            return mapped

        def _compute_split_ratio_flows(self, total_flow: float) -> List[float]:
            count = len(self.output_handles)
            if count == 0:
                return []

            specs = list(self.split_ratio_spec)
            if len(specs) < count:
                specs.extend(["" for _ in range(count - len(specs))])
            elif len(specs) > count:
                specs = specs[:count]

            flows = [0.0] * count
            explicit: List[tuple[int, float]] = []
            blank_indices: List[int] = []

            for idx, spec in enumerate(specs):
                numeric = self._coerce_float(spec)
                if numeric is None:
                    blank_indices.append(idx)
                else:
                    explicit.append((idx, numeric))

            if not explicit and blank_indices:
                share = total_flow / len(blank_indices) if blank_indices else 0.0
                for idx in blank_indices:
                    flows[idx] = share
                return flows

            ratio_sum = sum(value for _, value in explicit)
            scale = 1.0
            if ratio_sum > 1.0 and ratio_sum > 0:
                scale = 1.0 / ratio_sum

            assigned = 0.0
            for idx, value in explicit:
                ratio = max(value * scale, 0.0)
                flows[idx] = ratio * total_flow
                assigned += flows[idx]

            remaining = max(total_flow - assigned, 0.0)
            if blank_indices:
                share = remaining / len(blank_indices) if remaining > 0 else 0.0
                for idx in blank_indices:
                    flows[idx] = share
            elif remaining > 0 and explicit:
                last_idx = explicit[-1][0]
                flows[last_idx] += remaining

            return flows

        def _compute_threshold_flows(self, total_flow: float) -> List[float]:
            count = len(self.output_handles)
            if count == 0:
                return []

            mapped = list(self.threshold_mapping)
            if len(mapped) < count:
                mapped.extend(["" for _ in range(count - len(mapped))])
            elif len(mapped) > count:
                mapped = mapped[:count]

            flows = [0.0] * count
            remaining = max(total_flow, 0.0)
            blank_indices: List[int] = []

            for idx, spec in enumerate(mapped):
                numeric = self._coerce_float(spec)
                if numeric is None:
                    blank_indices.append(idx)
                    continue
                take = min(numeric, remaining)
                flows[idx] = take
                remaining = max(remaining - take, 0.0)

            for idx in blank_indices:
                if remaining <= 0:
                    break
                flows[idx] = remaining
                remaining = 0.0

            return flows

        def step(self, dt, current_step, inputs):
            x = inputs.get("in_main")
            if x is None:
                return {}

            total_flow = float(x[14]) if len(x) > 14 else 0.0
            total_flow = max(total_flow, 0.0)

            if self.mode == "threshold":
                flows = self._compute_threshold_flows(total_flow)
            else:
                flows = self._compute_split_ratio_flows(total_flow)

            outputs: Dict[str, np.ndarray] = {}
            for handle, flow in zip(self.output_handles, flows):
                stream = x.copy()
                stream[14] = flow
                outputs[handle] = stream

            return outputs

    return SplitterAdapter()

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