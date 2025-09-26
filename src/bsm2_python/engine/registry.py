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
    # Neue, deklarative Parameter (rückwärtskompatibel)
    mode = params.get("mode", None)
    fractions = params.get("fractions", None)     # z. B. ["", reginit.QBYPASSPLANT] oder [0.7, 0.3]
    threshold = params.get("threshold", None)     # z. B. reginit.QBYPASS
    target = params.get("target", None)           # "out_a", "out_b" oder benannte Handles
    # Legacy-Unterstützung
    q_bypass = params.get("q_bypass", None)       # alt: Bypass-Schwelle
    qintr = params.get("qintr", None)             # alt: interne Rezirkulation

    # BSM2-Implementierung bleibt verfügbar, wird aber für neue Modi nicht benötigt
    Splitter = get_splitter()
    impl = Splitter()

    class SplitterAdapter:
        def __init__(self, mode, fractions, threshold, target, q_bypass, qintr):
            self.mode = mode
            self.fractions = fractions
            self.threshold = threshold
            self.target = target
            self.q_bypass = q_bypass
            self.qintr = float(qintr) if qintr is not None else None

        @staticmethod
        def _mk_out(x: np.ndarray, Qv: float) -> np.ndarray:
            y = x.copy()
            y[14] = max(float(Qv), 0.0)
            return y

        @staticmethod
        def _target_pair(target: str):
            # Wähle passende Handle-Namen-Paare abhängig vom Zielhandle
            if target in ("out_a", "out_b", None):
                return ("out_a", "out_b")
            if target in ("out_to_settler", "out_recycle_to_combiner"):
                return ("out_to_settler", "out_recycle_to_combiner")
            # Fallback auf Standard
            return ("out_a", "out_b")

        def step(self, dt, current_step, inputs):
            x = inputs.get("in_main")
            if x is None:
                return {}

            Q = float(x[14])

            # 0) Legacy: Bypass via BSM2-Hilfsfunktion
            if self.q_bypass is not None:
                # Erwartet fractions und q_bypass (ältere Configs)
                a, b = impl.output(x, self.fractions or (0.5, 0.5), float(self.q_bypass))
                return {"out_a": a, "out_b": b}

            # 1) Neue Schwellenwert-Logik: Überschuss über threshold geht auf 'target'
            if self.mode == "threshold" and self.threshold is not None:
                T = float(self.threshold)
                t1, t2 = self._target_pair(self.target or "out_b")

                # FIXED: For reactor recycle, flow up to threshold goes to recycle, rest to settler
                if self.target == "out_recycle_to_combiner":
                    # This is the reactor splitter: first T flow goes to recycle, rest to settler
                    Q_recycle = min(T, Q)
                    Q_settler = Q - Q_recycle
                    return {
                        "out_to_settler": self._mk_out(x, Q_settler),
                        "out_recycle_to_combiner": self._mk_out(x, Q_recycle),
                    }
                else:
                    # Standard threshold: excess over T goes to target
                    if (self.target or t2) == t1:
                        # Überschuss auf t1
                        Q1 = max(Q - T, 0.0)
                        Q2 = Q - Q1
                    else:
                        # Überschuss auf t2
                        Q2 = max(Q - T, 0.0)
                        Q1 = Q - Q2

                    return {
                        t1: self._mk_out(x, Q1),
                        t2: self._mk_out(x, Q2),
                    }

            # 2) Neue Verhältnis-/Sollstrom-Logik
            if self.mode == "split_ratio" and isinstance(self.fractions, (list, tuple)) and len(self.fractions) >= 2:
                fa, fb = self.fractions[0], self.fractions[1]

                if fa == "" and isinstance(fb, (int, float)):
                    Qb = min(float(fb), Q)
                    Qa = Q - Qb
                elif fb == "" and isinstance(fa, (int, float)):
                    Qa = min(float(fa), Q)
                    Qb = Q - Qa
                else:
                    if isinstance(fa, (int, float)) and 0.0 <= float(fa) <= 1.0:
                        Qa = Q * float(fa)
                        Qb = Q - Qa
                    elif isinstance(fb, (int, float)) and 0.0 <= float(fb) <= 1.0:
                        Qb = Q * float(fb)
                        Qa = Q - Qb
                    elif isinstance(fa, (int, float)):
                        Qa = min(float(fa), Q)
                        Qb = Q - Qa
                    elif isinstance(fb, (int, float)):
                        Qb = min(float(fb), Q)
                        Qa = Q - Qb
                    else:
                        Qa = 0.5 * Q
                        Qb = Q - Qa

                return {
                    "out_a": self._mk_out(x, Qa),
                    "out_b": self._mk_out(x, Qb),
                }

            # 3) Legacy: interne Rezirkulation (z. B. Reaktor-Ausgang)
            if self.qintr is not None:
                flow_to_recycle = min(self.qintr, Q)
                flow_to_settler = Q - flow_to_recycle
                return {
                    "out_to_settler": self._mk_out(x, flow_to_settler),
                    "out_recycle_to_combiner": self._mk_out(x, flow_to_recycle),
                }

            # 4) Legacy/Fallback: feste fractions oder 50/50
            if isinstance(self.fractions, (list, tuple)) and len(self.fractions) >= 2:
                fa = float(self.fractions[0])
                if 0.0 <= fa <= 1.0:
                    Qa = Q * fa
                else:
                    Qa = min(fa, Q)
                Qb = Q - Qa
            else:
                Qa = 0.5 * Q
                Qb = Q - Qa

            return {"out_a": self._mk_out(x, Qa), "out_b": self._mk_out(x, Qb)}

    return SplitterAdapter(mode, fractions, threshold, target, q_bypass, qintr)

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
            # IMPORTANT: Ensure thickener outputs are only ASM1 (21 elements)
            underflow_21 = underflow[:21] if len(underflow) > 21 else underflow
            overflow_21 = overflow[:21] if len(overflow) > 21 else overflow
            return {
                "out_thickened": underflow_21,
                "out_supernatant": overflow_21
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
            # IMPORTANT: Ensure liquid output is only ASM1 (21 elements) not ADM1+ASM1 (51 elements)
            liquid_output = out2[:21] if len(out2) > 21 else out2
            return {"out_digested": out0, "out_gas": out1, "out_liquid": liquid_output}
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
            # IMPORTANT: Ensure dewatering outputs are only ASM1 (21 elements)
            cake_21 = cake[:21] if len(cake) > 21 else cake
            reject_21 = reject[:21] if len(reject) > 21 else reject
            return {"out_cake": cake_21, "out_filtrate": reject_21}
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
            # IMPORTANT: Ensure storage output is only ASM1 (21 elements)
            storage_output = out[:21] if len(out) > 21 else out
            return {"out_main": storage_output}
    return StorageAdapter(impl, qstorage)