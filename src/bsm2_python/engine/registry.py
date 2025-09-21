# src/bsm2_python/engine/registry.py
from __future__ import annotations
from typing import Dict, Any, Callable
import numpy as np

# Import real BSM2 components
from bsm2_python.bsm2.asm1_bsm2 import ASM1Reactor
from bsm2_python.bsm2.settler1d_bsm2 import Settler
from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter

# Gemeinsame Adapter-Schnittstelle:
#   obj.step(dt, inputs) -> outputs
#   inputs: {handle_id: vector}
#   outputs: {handle_id: vector}

Factory = Callable[[str, Dict[str, Any]], Any]

REGISTRY: Dict[str, Factory] = {}

def register(kind: str):
    def deco(fn: Factory):
        REGISTRY[kind] = fn
        return fn
    return deco

@register("influent_static")
def make_influent(node_id: str, params: Dict[str, Any]):
    class InfluentAdapter:
        def __init__(self, y):
            self.y = np.array(y, dtype=float)  # konstante 21D-Zusammensetzung
        def step(self, dt, inputs):
            return {"out_main": self.y.copy()}
    return InfluentAdapter(params["y_in_constant"])

@register("combiner")
def make_combiner(node_id: str, params: Dict[str, Any]):
    class CombinerAdapter:
        def __init__(self):
            self.combiner = Combiner()
        def step(self, dt, inputs):
            # sammle alle vorhandenen Eingänge
            input_streams = []
            handles = []
            for handle, stream in inputs.items():
                if stream is not None:
                    input_streams.append(stream)
                    handles.append(handle)
            
            if len(input_streams) == 0:
                return {"out_combined": np.zeros(21)}
            elif len(input_streams) == 1:
                result = input_streams[0]
            elif len(input_streams) == 2:
                result = self.combiner.output(input_streams[0], input_streams[1])
            elif len(input_streams) == 3:
                result = self.combiner.output(input_streams[0], input_streams[1], input_streams[2])
            else:
                # Handle more inputs by combining pairwise
                result = input_streams[0]
                for stream in input_streams[1:]:
                    result = self.combiner.output(result, stream)
            
            return {"out_combined": result}
    return CombinerAdapter()

@register("splitter")
def make_splitter(node_id: str, params: Dict[str, Any]):
    qintr = params.get("qintr", 55338)  # Default value from asm1init_bsm1
    class SplitterAdapter:
        def __init__(self, qintr):
            self.qintr = float(qintr)
            self.splitter = Splitter()
        def step(self, dt, inputs):
            x = inputs.get("in_main")
            if x is None:
                x = np.zeros(21)
            
            # Calculate flow split exactly like BSM1Base: 
            # max(total_flow - internal_recycle, 0.0), internal_recycle
            total_flow = x[14] if len(x) > 14 else 18446  # Q component
            to_settler_flow = max(total_flow - self.qintr, 0.0)
            
            # Use real BSM2 splitter component with exact same parameters as BSM1Base
            stream1, stream2 = self.splitter.output(x, (to_settler_flow, self.qintr))
            
            return {
                "out_to_settler": stream1,
                "out_recycle_to_combiner": stream2
            }
    return SplitterAdapter(qintr)

@register("reactor")
def make_reactor(node_id: str, params: Dict[str, Any]):
    class ReactorAdapter:
        def __init__(self, kla, volume, yinit, par, carb, csourceconc, tempmodel, activate):
            self.reactor = ASM1Reactor(
                kla=float(kla),
                volume=float(volume),
                y0=np.array(yinit, dtype=float),
                asm1par=np.array(par, dtype=float),
                carb=float(carb),
                csourceconc=float(csourceconc),
                tempmodel=tempmodel,
                activate=activate
            )
        def step(self, dt, inputs):
            x = inputs.get("in_main")
            if x is None:
                x = np.zeros(21)
            
            # Handle both single dt and (stepsize, step) tuple
            if isinstance(dt, tuple):
                stepsize, step = dt
            else:
                stepsize, step = dt, 0.0
            
            # Call the real BSM2 ASM1Reactor component 
            result = self.reactor.output(stepsize, step, x)  # stepsize, step, y_in
            return {"out_main": result}
    
    return ReactorAdapter(
        kla=params.get("KLA", 0),
        volume=params.get("VOL", 1000),
        yinit=params.get("YINIT", np.ones(21)),
        par=params.get("PAR", np.zeros(24)),
        carb=params.get("CARB", 0),
        csourceconc=params.get("CARBONSOURCECONC", 400000),
        tempmodel=params.get("tempmodel", False),
        activate=params.get("activate", False)
    )

@register("settler")
def make_settler(node_id: str, params: Dict[str, Any]):
    class SettlerAdapter:
        def __init__(self, dim, layer, qr, qw, settlerinit, settlerpar, par_asm, tempmodel, modeltype):
            self.settler = Settler(
                dim=np.array(dim, dtype=float),
                layer=np.array(layer, dtype=int),
                q_r=float(qr),
                q_w=float(qw),
                ys0=np.array(settlerinit, dtype=float),
                sedpar=np.array(settlerpar, dtype=float),
                asm1par=np.array(par_asm, dtype=float),
                tempmodel=tempmodel,
                modeltype=int(modeltype)
            )
        def step(self, dt, inputs):
            x = inputs.get("in_main")
            if x is None:
                x = np.zeros(21)
            
            # Handle both single dt and (stepsize, step) tuple
            if isinstance(dt, tuple):
                stepsize, step = dt
            else:
                stepsize, step = dt, 0.0
            
            # Call the real BSM2 Settler component
            result = self.settler.output(stepsize, step, x)  # stepsize, step, y_in
            
            # result is a tuple: (return_sludge, waste_sludge, effluent, sludge_height, tss_internal)
            return_sludge, waste_sludge, effluent, sludge_height, tss_internal = result
            
            return {
                "out_sludge_recycle": return_sludge,
                "out_waste_sludge": waste_sludge,
                "out_effluent": effluent,
                "_sludge_height": sludge_height,  # Internal state
                "_tss_internal": tss_internal    # Internal state
            }
    
    return SettlerAdapter(
        dim=params.get("DIM", [1500, 4]),
        layer=params.get("LAYER", [5, 10]),
        qr=params.get("QR", 18446),
        qw=params.get("QW", 385),
        settlerinit=params.get("settlerinit", np.zeros(120)),
        settlerpar=params.get("SETTLERPAR", np.zeros(7)),
        par_asm=params.get("PAR_ASM", np.zeros(24)),
        tempmodel=params.get("tempmodel_settler", False),
        modeltype=params.get("MODELTYPE_SETTLER", 0)
    )

@register("effluent")
def make_effluent(node_id: str, params: Dict[str, Any]):
    class EffluentAdapter:
        def __init__(self): 
            self.last = None
        def step(self, dt, inputs):
            self.last = inputs.get("in_main")
            return {"out_final": self.last} if self.last is not None else {}
    return EffluentAdapter()