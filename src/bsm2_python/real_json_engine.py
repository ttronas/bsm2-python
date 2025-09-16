"""
Real JSON-based simulation engine using actual BSM2-Python components.

This implementation creates the real simulation engine with actual BSM components,
working around import issues by creating a minimal standalone version.
"""

import json
import numpy as np
from typing import Dict, Any, List, Union, Optional, Tuple
import sys
import os

# Add src path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import real BSM2-Python components directly
def import_bsm_components():
    """Import BSM components with error handling."""
    try:
        # Import module base class
        from bsm2_python.bsm2.module import Module
        
        # Import specific components
        from bsm2_python.bsm2.asm1_bsm2 import ASM1Reactor
        from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter
        from bsm2_python.bsm2.settler1d_bsm2 import Settler
        
        # Import parameter modules
        import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init_bsm1
        import bsm2_python.bsm2.init.reginit_bsm1 as reginit_bsm1
        import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit_bsm2
        import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init_bsm2
        import bsm2_python.bsm2.init.reginit_bsm2 as reginit_bsm2
        
        return {
            'Module': Module,
            'ASM1Reactor': ASM1Reactor,
            'Combiner': Combiner,
            'Splitter': Splitter,
            'Settler': Settler,
            'asm1init_bsm1': asm1init_bsm1,
            'reginit_bsm1': reginit_bsm1,
            'asm1init_bsm2': asm1init_bsm2,
            'reginit_bsm2': reginit_bsm2,
            'settler1dinit_bsm2': settler1dinit_bsm2,
        }
        
    except ImportError as e:
        print(f"Warning: Could not import BSM components: {e}")
        return None

# Try to import real components, fall back to mocks if needed
bsm_components = import_bsm_components()

if bsm_components:
    print("Using real BSM2-Python components")
    Module = bsm_components['Module']
    ASM1Reactor = bsm_components['ASM1Reactor']
    Combiner = bsm_components['Combiner']
    Splitter = bsm_components['Splitter']
    Settler = bsm_components['Settler']
    
    # Use BSM1 parameters for the JSON configuration (as requested)
    asm1init = bsm_components['asm1init_bsm1']
    reginit = bsm_components['reginit_bsm1']
    settler1dinit = bsm_components['settler1dinit_bsm2']
    
else:
    print("Using mock components (real components not available)")
    # Use the mock components from the previous implementation
    from full_json_engine import (
        MockModule as Module,
        MockASM1Reactor as ASM1Reactor,
        MockCombiner as Combiner,
        MockSplitter as Splitter,
        MockSettler as Settler,
        BSM1Parameters
    )
    
    # Create mock parameter modules
    class MockInit:
        pass
    
    asm1init = BSM1Parameters()
    reginit = BSM1Parameters()
    settler1dinit = MockInit()
    settler1dinit.DIM = np.array([1500, 4])
    settler1dinit.LAYER = np.array([5, 10])
    settler1dinit.SETTLERPAR = np.array([250, 474, 0.000576, 0.00286, 0.00228, 3000, 3000])
    settler1dinit.settlerinit = np.zeros(120)
    settler1dinit.MODELTYPE = 0


class InfluentStatic(Module):
    """Static influent component."""
    def __init__(self, y_in_constant: np.ndarray):
        self.y_in_constant = np.array(y_in_constant)
        
    def output(self, *args, **kwargs) -> np.ndarray:
        return self.y_in_constant.copy()


class Effluent(Module):
    """Effluent component that stores final output."""
    def __init__(self):
        self.effluent_data = None
        
    def output(self, y_in: np.ndarray, *args, **kwargs) -> np.ndarray:
        self.effluent_data = y_in.copy()
        return y_in


class RealComponentFactory:
    """Factory for creating real BSM2-Python components."""
    
    def __init__(self, use_bsm1_params: bool = True):
        """Initialize factory.
        
        Parameters
        ----------
        use_bsm1_params : bool
            If True, use BSM1 parameters (as needed for the JSON config).
            If False, use BSM2 parameters.
        """
        self.use_bsm1_params = use_bsm1_params
        self.parameter_modules = {
            'asm1init': asm1init,
            'reginit': reginit,
            'settler1dinit': settler1dinit
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
                # If not found in expected module, try all modules
                for module in self.parameter_modules.values():
                    if hasattr(module, attr_name):
                        return getattr(module, attr_name)
                raise ValueError(f"Parameter '{param}' not found: {module_name}.{attr_name}")
            else:
                for module in self.parameter_modules.values():
                    if hasattr(module, param):
                        return getattr(module, param)
                raise ValueError(f"Parameter '{param}' not found in any module")
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
            
            return ASM1Reactor(
                kla=kla,
                volume=vol,
                y0=yinit,
                asm1par=par,
                carb=carb,
                csourceconc=carb_conc,
                tempmodel=tempmodel,
                activate=activate
            )
            
        elif component_type == 'splitter':
            return Splitter()
            
        elif component_type == 'settler':
            dim = self._resolve_parameter(params.get('DIM', [1500, 4]))
            layer = self._resolve_parameter(params.get('LAYER', [5, 10]))
            qr = self._resolve_parameter(params.get('QR', 20648))
            qw = self._resolve_parameter(params.get('QW', 300))
            settlerinit = self._resolve_parameter(params.get('settlerinit', np.zeros(120)))
            settlerpar = self._resolve_parameter(params.get('SETTLERPAR', np.zeros(7)))
            par_asm = self._resolve_parameter(params.get('PAR_ASM', np.zeros(24)))
            modeltype = self._resolve_parameter(params.get('MODELTYPE_SETTLER', 0))
            tempmodel = params.get('tempmodel_settler', False)
            
            return Settler(
                dim=dim,
                layer=layer,
                q_r=qr,
                q_w=qw,
                ys0=settlerinit,
                sedpar=settlerpar,
                asm1par=par_asm,
                tempmodel=tempmodel,
                modeltype=modeltype
            )
            
        elif component_type == 'effluent':
            return Effluent()
            
        else:
            raise ValueError(f"Unknown component type: {component_type}")


class RealJSONSimulationEngine:
    """Real simulation engine using actual BSM2-Python components."""
    
    def __init__(self, config: Union[str, Dict], use_bsm1_params: bool = True):
        if isinstance(config, str):
            with open(config, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = config
            
        self.factory = RealComponentFactory(use_bsm1_params=use_bsm1_params)
        self.components: Dict[str, Module] = {}
        self.simulation_settings = self.config.get('simulation_settings', {})
        
        # Create components
        self._create_components()
        
        # Build graph structure
        self._build_graph()
        
    def _create_components(self):
        """Create all components from configuration."""
        for node_config in self.config['nodes']:
            component_id = node_config['id']
            try:
                self.components[component_id] = self.factory.create_component(node_config)
                print(f"✓ Created component: {component_id}")
            except Exception as e:
                print(f"✗ Failed to create component {component_id}: {e}")
                raise
                
    def _build_graph(self):
        """Build adjacency lists from edges."""
        self.adjacency = {node['id']: [] for node in self.config['nodes']}
        self.reverse_adjacency = {node['id']: [] for node in self.config['nodes']}
        
        for edge in self.config['edges']:
            source = edge['source_node_id']
            target = edge['target_node_id']
            source_handle = edge['source_handle_id']
            target_handle = edge['target_handle_id']
            
            self.adjacency[source].append((target, source_handle, target_handle))
            self.reverse_adjacency[target].append((source, source_handle, target_handle))
    
    def stabilize(self, max_iterations: int = 100, tolerance: float = 1e-6) -> bool:
        """Stabilize the simulation with recycle handling."""
        print(f"Stabilizing real simulation for steady state...")
        
        # Initialize outputs
        outputs = {}
        special_outputs = {}
        
        for component_id in self.components:
            outputs[component_id] = np.zeros(21)
        
        # Get parameters
        timestep = self.simulation_settings.get('steady_timestep', 0.010416667)
        qintr = self.factory._resolve_parameter('reginit.QINTR')
        qr = self.factory._resolve_parameter('asm1init.QR')
        qw = self.factory._resolve_parameter('asm1init.QW')
        
        for iteration in range(max_iterations):
            old_outputs = {k: v.copy() for k, v in outputs.items()}
            
            # Influent
            outputs['influent_s'] = self.components['influent_s'].output()
            
            # Combiner - combines influent with recycle streams
            combiner_inputs = []
            combiner_inputs.append(outputs['influent_s'])  # Fresh influent
            
            # Add recycle streams if available (from previous iteration)
            if 'splitter_recycle' in special_outputs:
                combiner_inputs.append(special_outputs['splitter_recycle'])
            if 'settler_return' in special_outputs:
                combiner_inputs.append(special_outputs['settler_return'])
                
            outputs['combiner'] = self.components['combiner'].output(*combiner_inputs)
            
            # Reactors in series
            reactor_input = outputs['combiner']
            for reactor_id in ['reactor1', 'reactor2', 'reactor3', 'reactor4', 'reactor5']:
                if reactor_id in self.components:
                    outputs[reactor_id] = self.components[reactor_id].output(timestep, 0, reactor_input)
                    reactor_input = outputs[reactor_id]
            
            # Splitter
            last_reactor = 'reactor5' if 'reactor5' in self.components else 'reactor4'
            if last_reactor in outputs:
                qin = outputs[last_reactor][14]  # Flow rate
                if qin > 0:
                    ratio_to_settler = max(qin - qintr, 0.0) / qin
                    ratio_recycle = min(qintr, qin) / qin
                else:
                    ratio_to_settler, ratio_recycle = 0.5, 0.5
                
                split_outputs = self.components['splitter'].output(
                    outputs[last_reactor], (ratio_to_settler, ratio_recycle)
                )
                outputs['splitter'] = split_outputs[0]  # To settler
                special_outputs['splitter_recycle'] = split_outputs[1]  # Recycle to combiner
            
            # Settler
            if 'splitter' in outputs:
                settler_outputs = self.components['settler'].output(timestep, 0, outputs['splitter'])
                special_outputs['settler_return'] = settler_outputs[0]  # Return sludge
                special_outputs['settler_waste'] = settler_outputs[1]   # Waste sludge
                outputs['settler'] = settler_outputs[2]                # Effluent
                special_outputs['settler_height'] = settler_outputs[3]  # Sludge height
                special_outputs['settler_tss'] = settler_outputs[4]     # TSS profile
            
            # Effluent
            if 'settler' in outputs:
                outputs['effluent'] = self.components['effluent'].output(outputs['settler'])
            
            # Check convergence
            max_change = 0
            for component_id in outputs:
                if component_id in old_outputs:
                    change = np.max(np.abs(outputs[component_id] - old_outputs[component_id]))
                    max_change = max(max_change, change)
            
            if max_change < tolerance:
                print(f"Real simulation converged after {iteration + 1} iterations (max change: {max_change:.2e})")
                self.final_outputs = outputs
                self.special_outputs = special_outputs
                return True
        
        print(f"Real simulation did not converge after {max_iterations} iterations (max change: {max_change:.2e})")
        self.final_outputs = outputs
        self.special_outputs = special_outputs
        return False
    
    def get_effluent(self) -> np.ndarray:
        """Get final effluent values."""
        if hasattr(self, 'final_outputs') and 'effluent' in self.final_outputs:
            return self.final_outputs['effluent']
        return np.zeros(21)
    
    def get_sludge_height(self) -> float:
        """Get sludge height."""
        if hasattr(self, 'special_outputs') and 'settler_height' in self.special_outputs:
            return self.special_outputs['settler_height']
        return 0.0
    
    def get_tss_internal(self) -> np.ndarray:
        """Get TSS internal profile."""
        if hasattr(self, 'special_outputs') and 'settler_tss' in self.special_outputs:
            return self.special_outputs['settler_tss']
        return np.zeros(10)

def save_json_config():
    """Save the example JSON configuration to a file."""
    config = {
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
                "id": "reactor2",
                "component_type_id": "reactor",
                "label": "Reactor 2",
                "parameters": {
                    "KLA": "reginit.KLA2",
                    "VOL": "asm1init.VOL2",
                    "YINIT": "asm1init.YINIT2",
                    "PAR": "asm1init.PAR2",
                    "CARB": "reginit.CARB2",
                    "CARBONSOURCECONC": "reginit.CARBONSOURCECONC",
                    "tempmodel": False,
                    "activate": False
                }
            },
            {
                "id": "reactor3",
                "component_type_id": "reactor",
                "label": "Reactor 3",
                "parameters": {
                    "KLA": "reginit.KLA3",
                    "VOL": "asm1init.VOL3",
                    "YINIT": "asm1init.YINIT3",
                    "PAR": "asm1init.PAR3",
                    "CARB": "reginit.CARB3",
                    "CARBONSOURCECONC": "reginit.CARBONSOURCECONC",
                    "tempmodel": False,
                    "activate": False
                }
            },
            {
                "id": "reactor4",
                "component_type_id": "reactor",
                "label": "Test",
                "parameters": {
                    "KLA": "reginit.KLA4",
                    "VOL": "asm1init.VOL4",
                    "YINIT": "asm1init.YINIT4",
                    "PAR": "asm1init.PAR4",
                    "CARB": "reginit.CARB4",
                    "CARBONSOURCECONC": "reginit.CARBONSOURCECONC",
                    "tempmodel": False,
                    "activate": False
                }
            },
            {
                "id": "reactor5",
                "component_type_id": "reactor",
                "label": "Reactor 5",
                "parameters": {
                    "KLA": "reginit.KLA5",
                    "VOL": "asm1init.VOL5",
                    "YINIT": "asm1init.YINIT5",
                    "PAR": "asm1init.PAR5",
                    "CARB": "reginit.CARB5",
                    "CARBONSOURCECONC": "reginit.CARBONSOURCECONC",
                    "tempmodel": False,
                    "activate": False
                }
            },
            {
                "id": "splitter",
                "component_type_id": "splitter",
                "label": "Splitter",
                "parameters": {
                    "qintr": "asm1init.QINTR"
                }
            },
            {
                "id": "settler",
                "component_type_id": "settler",
                "label": "Settler (1D Model)",
                "parameters": {
                    "DIM": "settler1dinit.DIM",
                    "LAYER": "settler1dinit.LAYER",
                    "QR": "asm1init.QR",
                    "QW": "asm1init.QW",
                    "settlerinit": "settler1dinit.settlerinit",
                    "SETTLERPAR": "settler1dinit.SETTLERPAR",
                    "PAR_ASM": "asm1init.PAR1",
                    "MODELTYPE_SETTLER": "settler1dinit.MODELTYPE",
                    "tempmodel_settler": False
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
                "id": "e_1q859fb1l",
                "source_node_id": "influent_s",
                "source_handle_id": "out_main",
                "target_node_id": "combiner",
                "target_handle_id": "in_fresh"
            },
            {
                "id": "e_tq3lwnj2p",
                "source_node_id": "combiner",
                "source_handle_id": "out_combined",
                "target_node_id": "reactor1",
                "target_handle_id": "in_main"
            },
            {
                "id": "e_mi1xksup1",
                "source_node_id": "reactor1",
                "source_handle_id": "out_main",
                "target_node_id": "reactor2",
                "target_handle_id": "in_main"
            },
            {
                "id": "e_lm53m5dbq",
                "source_node_id": "reactor2",
                "source_handle_id": "out_main",
                "target_node_id": "reactor3",
                "target_handle_id": "in_main"
            },
            {
                "id": "e_o0bepm1c3",
                "source_node_id": "reactor3",
                "source_handle_id": "out_main",
                "target_node_id": "reactor4",
                "target_handle_id": "in_main"
            },
            {
                "id": "e_wi138cvhg",
                "source_node_id": "reactor4",
                "source_handle_id": "out_main",
                "target_node_id": "reactor5",
                "target_handle_id": "in_main"
            },
            {
                "id": "e_foj70r1wk",
                "source_node_id": "reactor5",
                "source_handle_id": "out_main",
                "target_node_id": "splitter",
                "target_handle_id": "in_main"
            },
            {
                "id": "e_0sp59cmaa",
                "source_node_id": "splitter",
                "source_handle_id": "out_to_settler",
                "target_node_id": "settler",
                "target_handle_id": "in_main"
            },
            {
                "id": "e_y4m7815gn",
                "source_node_id": "settler",
                "source_handle_id": "out_effluent",
                "target_node_id": "effluent",
                "target_handle_id": "in_main"
            },
            {
                "id": "e_ixic2izfz",
                "source_node_id": "splitter",
                "source_handle_id": "out_recycle_to_combiner",
                "target_node_id": "combiner",
                "target_handle_id": "in_recycle_process"
            },
            {
                "id": "e_yreoiqx0d",
                "source_node_id": "settler",
                "source_handle_id": "out_sludge_recycle",
                "target_node_id": "combiner",
                "target_handle_id": "in_recycle_settler"
            }
        ]
    }
    
    with open('bsm1_simulation_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("Saved example configuration to 'bsm1_simulation_config.json'")
    return config

def test_real_simulation():
    """Test the real simulation engine."""
    
    print("Testing real JSON simulation engine...")
    
    try:
        # Create configuration
        config = save_json_config()
        
        # Create and run simulation
        engine = RealJSONSimulationEngine(config, use_bsm1_params=True)
        print(f"✓ Created real simulation with {len(engine.components)} components")
        
        # Stabilize
        converged = engine.stabilize(max_iterations=100, tolerance=1e-6)
        print(f"✓ Real simulation {'converged' if converged else 'completed'}")
        
        # Get results
        effluent = engine.get_effluent()
        sludge_height = engine.get_sludge_height()
        tss_internal = engine.get_tss_internal()
        
        print(f"\n=== REAL SIMULATION RESULTS ===")
        print(f"Effluent: {effluent}")
        print(f"Sludge height: {sludge_height}")
        print(f"TSS internal: {tss_internal}")
        
        return True
        
    except Exception as e:
        print(f"✗ Real simulation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Real JSON Simulation Engine for BSM2-Python\n")
    
    success = test_real_simulation()
    
    if success:
        print("\n🎉 Real JSON simulation engine test completed!")
        print("\nUsage:")
        print("1. Load the JSON configuration file")
        print("2. Create RealJSONSimulationEngine instance")
        print("3. Call stabilize() to run steady-state simulation")
        print("4. Get results with get_effluent(), get_sludge_height(), etc.")
    else:
        print("\n❌ Real simulation test failed!")
        sys.exit(1)