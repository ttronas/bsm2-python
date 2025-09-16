#!/usr/bin/env python3
"""Minimal test script for JSON simulation engine concept."""

import json
import numpy as np
from typing import Dict, Any, List

# Minimal module base class
class Module:
    def __init__(self) -> None:
        pass

    def output(self, *args, **kwargs):
        raise NotImplementedError('The output method must be implemented by the child class.')

# Minimal component implementations for testing
class InfluentStatic(Module):
    def __init__(self, y_in_constant: np.ndarray):
        self.y_in_constant = np.array(y_in_constant)
        
    def output(self, *args, **kwargs) -> np.ndarray:
        return self.y_in_constant.copy()

class Combiner(Module):
    def __init__(self):
        pass
        
    def output(self, *args):
        """Combines multiple arrays in ASM1 format into one array."""
        if not args:
            return np.zeros(21)
        
        out = np.zeros(21)
        for arg in args:
            if len(arg) >= 21:
                # Simple flow-weighted averaging for concentration (indices 0-13)
                if out[14] + arg[14] > 0:
                    out[0:14] = (out[0:14] * out[14] + arg[0:14] * arg[14]) / (out[14] + arg[14])
                    out[15:21] = (out[15:21] * out[14] + arg[15:21] * arg[14]) / (out[14] + arg[14])
                out[14] += arg[14]  # Sum flows
        return out

class MockReactor(Module):
    def __init__(self, kla=0, volume=1000, y0=None, asm1par=None, carb=0, csourceconc=400000, tempmodel=False, activate=False):
        self.kla = kla
        self.volume = volume
        self.y0 = y0 if y0 is not None else np.zeros(21)
        self.asm1par = asm1par if asm1par is not None else np.zeros(24)
        self.carb = carb
        self.csourceconc = csourceconc
        self.tempmodel = tempmodel
        self.activate = activate
        
    def output(self, timestep, step, y_in):
        """Mock reactor that just passes through with minor modifications."""
        y_out = np.array(y_in)
        # Mock some simple transformations
        y_out[1] = max(0, y_out[1] * 0.8)  # Reduce SS slightly
        y_out[7] = min(8.0, y_out[7] + 1.0)  # Add some oxygen
        return y_out

class Effluent(Module):
    def __init__(self):
        self.effluent_data = None
        
    def output(self, y_in: np.ndarray, *args, **kwargs) -> np.ndarray:
        self.effluent_data = y_in.copy()
        return y_in

# Minimal parameter modules for testing
class MockASM1Init:
    VOL1 = 1000
    VOL2 = 1000
    VOL3 = 1000
    VOL4 = 1000
    VOL5 = 1000
    YINIT1 = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])
    YINIT2 = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])
    YINIT3 = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])
    YINIT4 = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])
    YINIT5 = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])
    PAR1 = np.zeros(24)
    PAR2 = np.zeros(24)
    PAR3 = np.zeros(24)
    PAR4 = np.zeros(24)
    PAR5 = np.zeros(24)
    QINTR = 61944  # Internal recycle flow rate

class MockRegInit:
    KLA1 = 0
    KLA2 = 0
    KLA3 = 240
    KLA4 = 240
    KLA5 = 84
    CARB1 = 2
    CARB2 = 0
    CARB3 = 0
    CARB4 = 0
    CARB5 = 0
    CARBONSOURCECONC = 400000

# Minimal factory for testing
class MinimalComponentFactory:
    def __init__(self):
        self.parameter_modules = {
            'asm1init': MockASM1Init(),
            'reginit': MockRegInit()
        }
        
    def _resolve_parameter(self, param):
        """Resolve parameter value from string reference or direct value."""
        if isinstance(param, str):
            if '.' in param:
                module_name, attr_name = param.split('.', 1)
                if module_name in self.parameter_modules:
                    module = self.parameter_modules[module_name]
                    if hasattr(module, attr_name):
                        return getattr(module, attr_name)
                raise ValueError(f"Parameter '{param}' not found")
            else:
                for module in self.parameter_modules.values():
                    if hasattr(module, param):
                        return getattr(module, param)
                raise ValueError(f"Parameter '{param}' not found")
        elif isinstance(param, list):
            return np.array(param)
        else:
            return param
    
    def create_component(self, component_config: Dict[str, Any]) -> Module:
        """Create a component from JSON configuration."""
        component_type = component_config.get('component_type_id', '')
        params = component_config.get('parameters', {})
        
        if component_type == 'influent_static':
            y_in_constant = self._resolve_parameter(params.get('y_in_constant', []))
            return InfluentStatic(y_in_constant)
        elif component_type == 'combiner':
            return Combiner()
        elif component_type == 'reactor':
            kla = self._resolve_parameter(params.get('KLA', 0))
            vol = self._resolve_parameter(params.get('VOL', 1000))
            yinit = self._resolve_parameter(params.get('YINIT', np.zeros(21)))
            par = self._resolve_parameter(params.get('PAR', np.zeros(24)))
            carb = self._resolve_parameter(params.get('CARB', 0))
            carb_conc = self._resolve_parameter(params.get('CARBONSOURCECONC', 400000))
            tempmodel = params.get('tempmodel', False)
            activate = params.get('activate', False)
            
            return MockReactor(
                kla=kla, volume=vol, y0=yinit, asm1par=par,
                carb=carb, csourceconc=carb_conc,
                tempmodel=tempmodel, activate=activate
            )
        elif component_type == 'effluent':
            return Effluent()
        else:
            raise ValueError(f"Unknown component type: {component_type}")

# Test configuration
test_config = {
    "simulation_settings": {
        "mode": "steady",
        "steady_timestep": 0.010416667,
        "steady_endtime": 200
    },
    "global_options": {
        "tempmodel": False,
        "activate": False
    },
    "nodes": [
        {
            "id": "influent_s",
            "component_type_id": "influent_static",
            "label": "Influent (Static)",
            "parameters": {
                "y_in_constant": [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0]
            }
        },
        {
            "id": "combiner",
            "component_type_id": "combiner",
            "label": "Combiner",
            "parameters": {}
        },
        {
            "id": "reactor1",
            "component_type_id": "reactor",
            "label": "Reactor 1",
            "parameters": {
                "KLA": "reginit.KLA1",
                "VOL": "asm1init.VOL1",
                "YINIT": "asm1init.YINIT1",
                "PAR": "asm1init.PAR1",
                "CARB": "reginit.CARB1",
                "CARBONSOURCECONC": "reginit.CARBONSOURCECONC",
                "tempmodel": False,
                "activate": False
            }
        },
        {
            "id": "effluent",
            "component_type_id": "effluent",
            "label": "Effluent",
            "parameters": {}
        }
    ],
    "edges": [
        {
            "id": "e_1",
            "source_node_id": "influent_s",
            "source_handle_id": "out_main",
            "target_node_id": "combiner",
            "target_handle_id": "in_fresh"
        },
        {
            "id": "e_2",
            "source_node_id": "combiner",
            "source_handle_id": "out_combined",
            "target_node_id": "reactor1",
            "target_handle_id": "in_main"
        },
        {
            "id": "e_3",
            "source_node_id": "reactor1",
            "source_handle_id": "out_main",
            "target_node_id": "effluent",
            "target_handle_id": "in_main"
        }
    ]
}

def test_minimal_simulation():
    """Test the minimal simulation engine."""
    print("Testing minimal simulation engine...")
    
    try:
        # Create factory
        factory = MinimalComponentFactory()
        print("✓ Factory created")
        
        # Create components
        components = {}
        for node_config in test_config['nodes']:
            component_id = node_config['id']
            components[component_id] = factory.create_component(node_config)
            print(f"✓ Created component: {component_id}")
        
        # Build adjacency lists
        adjacency = {node['id']: [] for node in test_config['nodes']}
        reverse_adjacency = {node['id']: [] for node in test_config['nodes']}
        
        for edge in test_config['edges']:
            source = edge['source_node_id']
            target = edge['target_node_id']
            adjacency[source].append(target)
            reverse_adjacency[target].append(source)
        
        print("✓ Graph built")
        
        # Simple execution order (topological sort for DAG)
        execution_order = []
        remaining = set(components.keys())
        
        while remaining:
            ready = [node for node in remaining 
                    if not reverse_adjacency[node] or 
                    all(src not in remaining for src in reverse_adjacency[node])]
            
            if not ready:
                ready = [next(iter(remaining))]  # Break cycle
            
            for node in ready:
                execution_order.append(node)
                remaining.remove(node)
        
        print(f"✓ Execution order: {execution_order}")
        
        # Run simulation
        outputs = {}
        for component_id in execution_order:
            component = components[component_id]
            
            if component_id == 'influent_s':
                outputs[component_id] = component.output()
            elif component_id == 'combiner':
                inputs = [outputs[src] for src in reverse_adjacency[component_id] if src in outputs]
                outputs[component_id] = component.output(*inputs)
            elif component_id == 'reactor1':
                inputs = [outputs[src] for src in reverse_adjacency[component_id] if src in outputs]
                if inputs:
                    timestep = test_config['simulation_settings']['steady_timestep']
                    outputs[component_id] = component.output(timestep, 0, inputs[0])
                else:
                    outputs[component_id] = np.zeros(21)
            elif component_id == 'effluent':
                inputs = [outputs[src] for src in reverse_adjacency[component_id] if src in outputs]
                if inputs:
                    outputs[component_id] = component.output(inputs[0])
                else:
                    outputs[component_id] = np.zeros(21)
        
        print("✓ Simulation completed")
        
        # Show results
        for component_id, output in outputs.items():
            print(f"  {component_id}: {output[:5]}... (first 5 values)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parameter_resolution():
    """Test parameter resolution."""
    print("\nTesting parameter resolution...")
    
    try:
        factory = MinimalComponentFactory()
        
        # Test direct value
        result = factory._resolve_parameter(42.0)
        print(f"✓ Direct value: {result}")
        
        # Test array
        result = factory._resolve_parameter([1, 2, 3])
        print(f"✓ Array: {result}")
        
        # Test string resolution
        result = factory._resolve_parameter("reginit.KLA1")
        print(f"✓ String resolution: {result}")
        
        # Test string resolution with array
        result = factory._resolve_parameter("asm1init.YINIT1")
        print(f"✓ Array parameter: shape {result.shape}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Minimal JSON Simulation Engine\n")
    
    success = True
    success &= test_parameter_resolution()
    success &= test_minimal_simulation()
    
    if success:
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
        exit(1)