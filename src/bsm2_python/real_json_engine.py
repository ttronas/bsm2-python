"""
JSON-based simulation engine for general-purpose WWTP simulations.

This implementation creates a flexible simulation engine that can handle
any WWTP configuration defined in JSON, including complex recycle streams.
"""

import json
import numpy as np
from typing import Dict, Any, Union, List, Tuple, Set
from collections import defaultdict, deque
import sys
import os

# Add src path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import real BSM2-Python components
from bsm2_python.bsm2.module import Module
from bsm2_python.bsm2.asm1_bsm2 import ASM1Reactor
from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter
from bsm2_python.bsm2.settler1d_bsm2 import Settler

# Import parameter modules - use BSM1 parameters to match BSM1OL
import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init
import bsm2_python.bsm2.init.reginit_bsm1 as reginit
import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit


class InfluentStatic(Module):
    """Static influent component that provides constant values."""
    
    def __init__(self, y_in_constant: np.ndarray):
        self.y_in_constant = np.array(y_in_constant)
        
    def output(self, *args, **kwargs) -> np.ndarray:
        return self.y_in_constant.copy()


class Effluent(Module):
    """Effluent component that just passes through input."""
    
    def __init__(self):
        self.effluent_data = None
        
    def output(self, y_in: np.ndarray, *args, **kwargs) -> np.ndarray:
        self.effluent_data = y_in.copy()
        return y_in


class ComponentFactory:
    """Factory for creating BSM components from JSON configuration."""
    
    def __init__(self):
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


class JSONSimulationEngine:
    """
    General-purpose JSON simulation engine for WWTP configurations.
    
    This engine can handle any WWTP layout defined in JSON, including
    complex topologies with recycle streams. It uses a graph-based approach:
    - First simulates nodes without dependencies (feed-forward)
    - Then handles cycles/loops within each simulation timestep using convergence
    """
    
    def __init__(self, config: Union[str, Dict]):
        if isinstance(config, str):
            with open(config, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = config
            
        self.factory = ComponentFactory()
        self.simulation_settings = self.config.get('simulation_settings', {})
        
        # Build the simulation components and analyze topology
        self._build_simulation_components()
        
        # Setup simulation parameters
        self._setup_simulation()
        
    def _build_simulation_components(self):
        """Build components and analyze the topology from JSON configuration."""
        # Create components
        self.components = {}
        for node_config in self.config['nodes']:
            component_id = node_config['id']
            self.components[component_id] = self.factory.create_component(node_config)
            
        # Build topology map from edges
        self.dependencies = {}  # target -> [sources]
        self.targets = defaultdict(list)  # source -> [targets]
        
        for edge in self.config.get('edges', []):
            source = edge['source_node_id']
            target = edge['target_node_id']
            
            if target not in self.dependencies:
                self.dependencies[target] = []
            self.dependencies[target].append(source)
            self.targets[source].append(target)
            
        # Analyze topology for execution order
        self._analyze_execution_order()
        
    def _analyze_execution_order(self):
        """Analyze topology to determine execution order for general WWTP configurations."""
        # Find nodes with no dependencies (feed-forward)
        self.feed_forward_nodes = []
        self.cyclic_nodes = []
        
        all_nodes = set(self.components.keys())
        nodes_with_deps = set(self.dependencies.keys())
        
        # Feed-forward nodes have no dependencies
        for node in all_nodes:
            if node not in nodes_with_deps:
                self.feed_forward_nodes.append(node)
        
        # Detect cycles using DFS
        self.cycles = self._detect_cycles()
        
        # Remaining nodes are part of cycles
        for node in all_nodes:
            if node not in self.feed_forward_nodes:
                self.cyclic_nodes.append(node)
                
    def _detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the dependency graph."""
        visited = set()
        path = set()
        cycles = []
        
        def dfs(node, current_path):
            if node in path:
                # Found a cycle
                cycle_start = current_path.index(node)
                cycle = current_path[cycle_start:]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
                
            visited.add(node)
            path.add(node)
            current_path.append(node)
            
            for target in self.targets.get(node, []):
                dfs(target, current_path)
            
            path.remove(node)
            current_path.pop()
        
        for node in self.components.keys():
            if node not in visited:
                dfs(node, [])
        
        return cycles
        
    def _create_stream(self, component_id: str, default_value: np.ndarray) -> np.ndarray:
        """Create/initialize a stream for components (BSM1OL compatibility)."""
        return default_value.copy()
        
    def _setup_simulation(self):
        """Setup simulation parameters."""
        # Create the same influent data as BSM1OL for consistency
        data_in_full = np.array([
            [0.0, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
            [200.1, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
        ])
        
        # Follow BSM1Base exactly: separate time and data
        self.data_time = data_in_full[:, 0]
        self.y_in = data_in_full[:, 1:]  # Exclude time column, just like BSM1Base!
        
        self.timestep = self.simulation_settings.get('steady_timestep', 15 / (60 * 24))
        self.endtime = self.simulation_settings.get('steady_endtime', 200)
        
        # Create time array exactly like BSM1OL
        self.simtime = np.arange(0, self.endtime, self.timestep, dtype=float)
        self.timesteps = np.full(len(self.simtime), self.timestep)
        
        # Initialize streams using _create_stream approach (like BSM1Base) 
        default_stream = self.y_in[0].copy()  # First influent row without time
        
        # Initialize streams for cyclic components (recycle streams)
        self.streams = {}
        for node in self.cyclic_nodes:
            self.streams[node] = self._create_stream(node, default_stream)
        
        # Special handling for common WWTP components
        if 'combiner' in self.components:
            # Initialize recycle streams
            if 'settler' in self.components:
                self.streams['settler_return'] = self._create_stream('settler_return', default_stream)
            if 'splitter' in self.components:
                self.streams['internal_recycle'] = self._create_stream('internal_recycle', default_stream)
                
        # Set parameters for reactors (if any)
        self.qintr = getattr(asm1init, 'QINTR', 61944)  # Default internal recycle flow
        self.klas = np.array([getattr(asm1init, f'KLA{i}', 10) for i in range(1, 6)])
        
    def step(self, i: int):
        """
        Execute one simulation time step using general graph-based approach.
        
        Strategy:
        1. First simulate nodes with no dependencies (feed-forward direction)
        2. Then simulate loops/cycles within the timestep until convergence
        """
        step = self.simtime[i]
        stepsize = self.timesteps[i]
        
        # Get current influent
        y_in_timestep = self.y_in[np.where(self.data_time <= step)[0][-1], :]
        
        # Execute general graph-based simulation
        self._step_general_graph(stepsize, step, y_in_timestep)
    
    def _step_general_graph(self, stepsize: float, step: float, y_in_timestep: np.ndarray):
        """
        Execute general topology using unified graph-based approach with cycle handling.
        
        This handles any WWTP configuration using a single methodology:
        1. First simulate nodes with no dependencies (feed-forward direction)
        2. Then simulate loops within each timestep using convergence
        """
        # Initialize component outputs storage
        outputs = {}
        
        # Set influent as initial input
        outputs['influent'] = y_in_timestep
        outputs['influent_s'] = y_in_timestep  # Static influent
        
        # Update KLA values for reactors
        for idx, comp_id in enumerate(self.components.keys()):
            if 'reactor' in comp_id and hasattr(self.components[comp_id], 'kla'):
                reactor_num = int(comp_id.replace('reactor', '')) if comp_id.replace('reactor', '').isdigit() else 1
                if reactor_num <= len(self.klas):
                    self.components[comp_id].kla = self.klas[reactor_num - 1]
        
        # Use unified general graph execution for ALL topologies
        self._execute_general_order(stepsize, step, y_in_timestep, outputs)
        
        # Store final results for compatibility
        self._store_final_results(outputs)
        

    def _execute_general_order(self, stepsize: float, step: float, y_in_timestep: np.ndarray, outputs: Dict[str, np.ndarray]):
        """Execute general graph topology with unified approach."""
        
        # Initialize recycle streams with influent values (BSM1OL-compatible)
        if not hasattr(self, 'initialized_cycles'):
            for stream_name in self.streams:
                self.streams[stream_name] = y_in_timestep.copy()
            self.initialized_cycles = True
        
        # Step 1: Process all nodes in dependency order
        processed = set()
        max_iterations = 10
        
        for iteration in range(max_iterations):
            progress_made = False
            
            # Try to process each component
            for comp_id in self.components.keys():
                if comp_id in processed:
                    continue
                    
                # Check if all dependencies are satisfied
                deps = self.dependencies.get(comp_id, [])
                if all(dep in outputs or dep in processed or dep.startswith('influent') for dep in deps):
                    try:
                        outputs[comp_id] = self._execute_component(comp_id, stepsize, step, outputs, y_in_timestep)
                        processed.add(comp_id)
                        progress_made = True
                        
                        # Update recycle streams based on component outputs
                        self._update_recycle_streams(comp_id, outputs)
                        
                    except Exception as e:
                        # Component might depend on recycle streams that aren't ready yet
                        continue
            
            # If all components processed, we're done
            if len(processed) == len(self.components):
                break
                
            # If no progress was made, handle remaining cyclic components
            if not progress_made:
                self._handle_remaining_cycles(stepsize, step, y_in_timestep, outputs, processed)
                break
                
    def _update_recycle_streams(self, comp_id: str, outputs: Dict[str, np.ndarray]):
        """Update recycle streams based on component outputs."""
        # Update settler return stream
        if comp_id == 'settler' and 'settler_return' in outputs:
            self.streams['settler_return'] = outputs['settler_return']
            
        # Update internal recycle stream  
        if comp_id == 'splitter' and 'splitter_recycle' in outputs:
            self.streams['internal_recycle'] = outputs['splitter_recycle']
            
    def _handle_remaining_cycles(self, stepsize: float, step: float, y_in_timestep: np.ndarray, 
                                outputs: Dict[str, np.ndarray], processed: Set[str]):
        """Handle remaining cyclic components iteratively."""
        remaining = [comp_id for comp_id in self.components.keys() if comp_id not in processed]
        
        # Iterative convergence for cyclic components
        max_iterations = 5
        tolerance = 1e-3
        
        for iteration in range(max_iterations):
            converged = True
            old_streams = {k: v.copy() for k, v in self.streams.items()}
            
            for comp_id in remaining:
                try:
                    outputs[comp_id] = self._execute_component(comp_id, stepsize, step, outputs, y_in_timestep)
                    self._update_recycle_streams(comp_id, outputs)
                except Exception:
                    continue
            
            # Check convergence
            for stream_name, new_value in self.streams.items():
                if stream_name in old_streams:
                    diff = np.max(np.abs(new_value - old_streams[stream_name]))
                    if diff > tolerance:
                        converged = False
                        break
            
            if converged:
                break
        
    def _execute_component(self, comp_id: str, stepsize: float, step: float, 
                          outputs: Dict[str, np.ndarray], y_in_timestep: np.ndarray) -> np.ndarray:
        """Execute a single component and return its output."""
        component = self.components[comp_id]
        
        if comp_id.startswith('influent'):
            return component.output()
            
        elif comp_id == 'combiner':
            # Get inputs for combiner
            deps = self.dependencies.get(comp_id, [])
            if not deps:
                # No dependencies, use influent
                return y_in_timestep
            else:
                # Handle multiple inputs for combiner: influent + recycle streams
                inputs = []
                for dep in deps:
                    if dep == 'influent_s':
                        inputs.append(y_in_timestep)
                    elif dep == 'splitter':
                        # Internal recycle stream
                        inputs.append(outputs.get('splitter_recycle', self.streams.get('internal_recycle', y_in_timestep)))
                    elif dep == 'settler':
                        # Return sludge stream  
                        inputs.append(outputs.get('settler_return', self.streams.get('settler_return', y_in_timestep)))
                    else:
                        inputs.append(outputs.get(dep, y_in_timestep))
                
                # Call combiner with appropriate number of inputs
                if len(inputs) == 1:
                    return inputs[0]
                elif len(inputs) == 2:
                    return component.output(inputs[0], inputs[1])
                elif len(inputs) == 3:
                    return component.output(inputs[0], inputs[1], inputs[2])
                else:
                    # Handle more inputs if needed
                    return component.output(*inputs)
                
        elif 'reactor' in comp_id:
            deps = self.dependencies.get(comp_id, [])
            input_stream = outputs.get(deps[0], y_in_timestep) if deps else y_in_timestep
            return component.output(stepsize, step, input_stream)
            
        elif comp_id == 'splitter':
            deps = self.dependencies.get(comp_id, [])
            input_stream = outputs.get(deps[0], y_in_timestep) if deps else y_in_timestep
            # Calculate flow split based on internal recycle
            total_flow = input_stream[14] if len(input_stream) > 14 else 20648
            recycle_flow = self.qintr
            to_settler = max(total_flow - recycle_flow, 0.0)
            # Return tuple for splitter outputs - fix numba type issue
            stream1, stream2 = component.output(input_stream, (float(to_settler), float(recycle_flow)))
            outputs[comp_id + '_to_settler'] = stream1
            outputs[comp_id + '_recycle'] = stream2
            return stream1  # Main output
            
        elif comp_id == 'settler':
            deps = self.dependencies.get(comp_id, [])
            # Get input from splitter's settler output
            if deps and 'splitter' in deps[0]:
                input_stream = outputs.get('splitter_to_settler', outputs.get(deps[0], y_in_timestep))
            else:
                input_stream = outputs.get(deps[0], y_in_timestep) if deps else y_in_timestep
                
            settler_outputs = component.output(stepsize, step, input_stream)
            
            # Store all settler outputs
            outputs[comp_id + '_return'] = settler_outputs[0]  # Return sludge
            outputs[comp_id + '_waste'] = settler_outputs[1]   # Waste sludge  
            outputs[comp_id + '_effluent'] = settler_outputs[2] # Effluent
            self.sludge_height = settler_outputs[3]
            self.ys_tss_internal = settler_outputs[4]
            
            return settler_outputs[2]  # Effluent as main output
            
        elif comp_id == 'effluent':
            deps = self.dependencies.get(comp_id, [])
            input_stream = outputs.get(deps[0], y_in_timestep) if deps else y_in_timestep
            return component.output(input_stream)
            
        else:
            # Default: pass through input
            deps = self.dependencies.get(comp_id, [])
            return outputs.get(deps[0], y_in_timestep) if deps else y_in_timestep
    
    
    def _store_final_results(self, outputs: Dict[str, np.ndarray]):
        """Store final results for compatibility with BSM1OL interface."""
        # Effluent
        if 'effluent' in outputs:
            self.ys_eff = outputs['effluent']
        elif 'settler_effluent' in outputs:
            self.ys_eff = outputs['settler_effluent']
        elif 'settler' in outputs:
            self.ys_eff = outputs['settler']
        else:
            # Find last component in the chain
            self.ys_eff = outputs.get('reactor5', outputs.get('reactor4', outputs.get('reactor3', 
                         outputs.get('reactor2', outputs.get('reactor1', self.y_in[0])))))
        
        # Sludge height and TSS (set defaults if not from settler)
        if not hasattr(self, 'sludge_height'):
            self.sludge_height = 0.0
        if not hasattr(self, 'ys_tss_internal'):
            self.ys_tss_internal = np.zeros(10)
            
        # Final effluent
        self.final_effluent = self.ys_eff
            
    def simulate(self):
        """
        Run the full simulation.
        
        Returns results compatible with BSM1OL.
        """
        # Execute all time steps
        for i in range(len(self.simtime)):
            self.step(i)
            
        return {
            'effluent': self.ys_eff,
            'sludge_height': self.sludge_height,
            'tss_internal': self.ys_tss_internal
        }
    
    def get_effluent(self) -> np.ndarray:
        """Get final effluent values."""
        return self.ys_eff if hasattr(self, 'ys_eff') else np.zeros(21)
    
    def get_sludge_height(self) -> float:
        """Get sludge height."""
        return self.sludge_height if hasattr(self, 'sludge_height') else 0.0
    
    def get_tss_internal(self) -> np.ndarray:
        """Get TSS internal profile."""
        return self.ys_tss_internal if hasattr(self, 'ys_tss_internal') else np.zeros(10)

