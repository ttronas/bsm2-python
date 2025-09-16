"""JSON-based simulation engine for BSM2-Python models.

This module provides a simulation engine that can parse JSON configuration files
and automatically create and connect BSM components for simulation.
"""

import json
import importlib
from typing import Dict, Any, List, Union, Optional, Tuple
import numpy as np
import sys
import os

# Add paths for direct imports to avoid control library dependency
src_path = os.path.dirname(__file__)
sys.path.insert(0, src_path)

# Import modules directly
from bsm2.module import Module
from bsm2.asm1_bsm2 import ASM1Reactor
from bsm2.helpers_bsm2 import Combiner, Splitter
from bsm2.settler1d_bsm2 import Settler


class ComponentFactory:
    """Factory class for creating BSM2-Python components from JSON configuration."""

    def __init__(self, parameter_modules: Optional[Dict[str, Any]] = None):
        """Initialize the component factory.
        
        Parameters
        ----------
        parameter_modules : Dict[str, Any], optional
            Dictionary of loaded parameter modules. If None, default BSM2 modules are loaded.
        """
        self.parameter_modules = parameter_modules or self._load_default_parameters()
        self.component_map = {
            'influent_static': self._create_influent_static,
            'combiner': self._create_combiner,
            'reactor': self._create_reactor,
            'splitter': self._create_splitter,
            'settler': self._create_settler,
            'effluent': self._create_effluent
        }

    def _load_default_parameters(self) -> Dict[str, Any]:
        """Load default BSM2 parameter modules."""
        modules = {}
        try:
            modules['asm1init'] = importlib.import_module('bsm2.init.asm1init_bsm2')
            modules['reginit'] = importlib.import_module('bsm2.init.reginit_bsm2')
            modules['settler1dinit'] = importlib.import_module('bsm2.init.settler1dinit_bsm2')
        except ImportError as e:
            print(f"Warning: Could not load parameter module: {e}")
        return modules

    def _resolve_parameter(self, param: Union[str, float, int, list]) -> Union[float, int, np.ndarray]:
        """Resolve parameter value from string reference or direct value.
        
        Parameters
        ----------
        param : str, float, int, or list
            Parameter that can be a string reference to module attribute or direct value
            
        Returns
        -------
        float, int, or np.ndarray
            Resolved parameter value
        """
        if isinstance(param, str):
            # Parse module.attribute format
            if '.' in param:
                module_name, attr_name = param.split('.', 1)
                if module_name in self.parameter_modules:
                    module = self.parameter_modules[module_name]
                    if hasattr(module, attr_name):
                        return getattr(module, attr_name)
                    else:
                        raise ValueError(f"Attribute '{attr_name}' not found in module '{module_name}'")
                else:
                    raise ValueError(f"Module '{module_name}' not found in parameter modules")
            else:
                # Try to find in any module
                for module in self.parameter_modules.values():
                    if hasattr(module, param):
                        return getattr(module, param)
                raise ValueError(f"Parameter '{param}' not found in any module")
        elif isinstance(param, list):
            return np.array(param)
        else:
            return param

    def _create_influent_static(self, component_config: Dict[str, Any]) -> 'InfluentStatic':
        """Create a static influent component."""
        params = component_config.get('parameters', {})
        y_in_constant = self._resolve_parameter(params.get('y_in_constant', []))
        return InfluentStatic(y_in_constant)

    def _create_combiner(self, component_config: Dict[str, Any]) -> Combiner:
        """Create a combiner component."""
        return Combiner()

    def _create_reactor(self, component_config: Dict[str, Any]) -> ASM1Reactor:
        """Create an ASM1 reactor component."""
        params = component_config.get('parameters', {})
        
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

    def _create_splitter(self, component_config: Dict[str, Any]) -> Splitter:
        """Create a splitter component."""
        params = component_config.get('parameters', {})
        qintr = self._resolve_parameter(params.get('qintr', 0))
        return Splitter()

    def _create_settler(self, component_config: Dict[str, Any]) -> Settler:
        """Create a settler component."""
        params = component_config.get('parameters', {})
        
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

    def _create_effluent(self, component_config: Dict[str, Any]) -> 'Effluent':
        """Create an effluent component."""
        return Effluent()

    def create_component(self, component_config: Dict[str, Any]) -> Module:
        """Create a component from JSON configuration.
        
        Parameters
        ----------
        component_config : Dict[str, Any]
            Component configuration dictionary
            
        Returns
        -------
        Module
            Created component instance
        """
        component_type = component_config.get('component_type_id', '')
        if component_type in self.component_map:
            return self.component_map[component_type](component_config)
        else:
            raise ValueError(f"Unknown component type: {component_type}")


class InfluentStatic(Module):
    """Static influent component that provides constant values."""
    
    def __init__(self, y_in_constant: np.ndarray):
        """Initialize static influent.
        
        Parameters
        ----------
        y_in_constant : np.ndarray
            Constant influent values (21 components)
        """
        self.y_in_constant = np.array(y_in_constant)
        
    def output(self, *args, **kwargs) -> np.ndarray:
        """Return constant influent values."""
        return self.y_in_constant.copy()


class Effluent(Module):
    """Effluent component that just passes through input."""
    
    def __init__(self):
        self.effluent_data = None
        
    def output(self, y_in: np.ndarray, *args, **kwargs) -> np.ndarray:
        """Store and return effluent data."""
        self.effluent_data = y_in.copy()
        return y_in


class SimulationGraph:
    """Graph representation of the simulation with cycle detection and execution order."""
    
    def __init__(self, nodes: List[Dict], edges: List[Dict]):
        """Initialize simulation graph.
        
        Parameters
        ----------
        nodes : List[Dict]
            List of node configurations
        edges : List[Dict]
            List of edge configurations
        """
        self.nodes = {node['id']: node for node in nodes}
        self.edges = edges
        self.adjacency = self._build_adjacency()
        self.reverse_adjacency = self._build_reverse_adjacency()
        
    def _build_adjacency(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Build adjacency list with edge information."""
        adj = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            source = edge['source_node_id']
            target = edge['target_node_id']
            source_handle = edge['source_handle_id']
            target_handle = edge['target_handle_id']
            adj[source].append((target, source_handle, target_handle))
        return adj
    
    def _build_reverse_adjacency(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Build reverse adjacency list for input tracking."""
        rev_adj = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            source = edge['source_node_id']
            target = edge['target_node_id']
            source_handle = edge['source_handle_id']
            target_handle = edge['target_handle_id']
            rev_adj[target].append((source, source_handle, target_handle))
        return rev_adj
    
    def detect_cycles(self) -> List[List[str]]:
        """Detect cycles in the graph using DFS."""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node, path):
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            
            if node in visited:
                return
                
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor, _, _ in self.adjacency[node]:
                dfs(neighbor, path.copy())
            
            rec_stack.remove(node)
        
        for node in self.nodes:
            if node not in visited:
                dfs(node, [])
        
        return cycles
    
    def get_execution_order_with_cycles(self) -> Tuple[List[str], List[List[str]]]:
        """Get execution order considering cycles (recycle streams).
        
        Returns
        -------
        Tuple[List[str], List[List[str]]]
            Execution order and detected cycles
        """
        cycles = self.detect_cycles()
        
        # For nodes in cycles, we need special handling
        cycle_nodes = set()
        for cycle in cycles:
            cycle_nodes.update(cycle)
        
        # Start with nodes that have no inputs or only inputs from cycle nodes
        execution_order = []
        remaining_nodes = set(self.nodes.keys())
        
        while remaining_nodes:
            # Find nodes that can be executed (all inputs satisfied or only cycle inputs)
            ready_nodes = []
            for node in remaining_nodes:
                inputs = self.reverse_adjacency[node]
                if not inputs:  # No inputs
                    ready_nodes.append(node)
                else:
                    # Check if all non-cycle inputs are satisfied
                    non_cycle_inputs_satisfied = True
                    for input_node, _, _ in inputs:
                        if input_node in remaining_nodes and input_node not in cycle_nodes:
                            non_cycle_inputs_satisfied = False
                            break
                    if non_cycle_inputs_satisfied:
                        ready_nodes.append(node)
            
            if not ready_nodes:
                # If no nodes are ready, pick one from remaining (cycle breaking)
                ready_nodes = [next(iter(remaining_nodes))]
            
            for node in ready_nodes:
                execution_order.append(node)
                remaining_nodes.remove(node)
        
        return execution_order, cycles


class JSONSimulationEngine:
    """Main simulation engine that parses JSON configuration and runs simulations."""
    
    def __init__(self, config: Union[str, Dict], parameter_modules: Optional[Dict[str, Any]] = None):
        """Initialize simulation engine.
        
        Parameters
        ----------
        config : str or Dict
            JSON configuration file path or configuration dictionary
        parameter_modules : Dict[str, Any], optional
            Custom parameter modules to use instead of defaults
        """
        if isinstance(config, str):
            with open(config, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = config
            
        self.factory = ComponentFactory(parameter_modules)
        self.components: Dict[str, Module] = {}
        self.graph = SimulationGraph(self.config['nodes'], self.config['edges'])
        self.execution_order, self.cycles = self.graph.get_execution_order_with_cycles()
        
        # Create components
        self._create_components()
        
        # Initialize simulation settings
        self.simulation_settings = self.config.get('simulation_settings', {})
        self.global_options = self.config.get('global_options', {})
        
    def _create_components(self):
        """Create all components from configuration."""
        for node_config in self.config['nodes']:
            component_id = node_config['id']
            self.components[component_id] = self.factory.create_component(node_config)
    
    def _get_component_inputs(self, component_id: str, outputs: Dict[str, np.ndarray]) -> List[np.ndarray]:
        """Get inputs for a component from previous outputs."""
        inputs = []
        for source_id, source_handle, target_handle in self.graph.reverse_adjacency[component_id]:
            if source_id in outputs:
                inputs.append(outputs[source_id])
            else:
                # Initialize with zeros for cycle handling
                inputs.append(np.zeros(21))
        return inputs
    
    def stabilize(self, max_iterations: int = 100, tolerance: float = 1e-6) -> bool:
        """Stabilize the simulation by iterating until convergence.
        
        Parameters
        ----------
        max_iterations : int
            Maximum number of iterations
        tolerance : float
            Convergence tolerance
            
        Returns
        -------
        bool
            True if converged, False otherwise
        """
        print(f"Stabilizing simulation with {len(self.cycles)} cycles detected...")
        
        # Initialize outputs
        outputs = {}
        for component_id in self.components:
            outputs[component_id] = np.zeros(21)
        
        # Iterate until convergence
        for iteration in range(max_iterations):
            old_outputs = {k: v.copy() for k, v in outputs.items()}
            
            # Execute components in order
            for component_id in self.execution_order:
                component = self.components[component_id]
                inputs = self._get_component_inputs(component_id, outputs)
                
                if component_id == 'influent_s':
                    # Influent doesn't need inputs
                    outputs[component_id] = component.output()
                elif component_id == 'combiner':
                    # Combiner needs multiple inputs
                    if inputs:
                        outputs[component_id] = component.output(*inputs)
                    else:
                        outputs[component_id] = np.zeros(21)
                elif component_id in ['reactor1', 'reactor2', 'reactor3', 'reactor4', 'reactor5']:
                    # Reactors need timestep, step, and input
                    if inputs:
                        timestep = self.simulation_settings.get('steady_timestep', 0.010416667)
                        step = 0  # For steady state
                        outputs[component_id] = component.output(timestep, step, inputs[0])
                    else:
                        outputs[component_id] = np.zeros(21)
                elif component_id == 'splitter':
                    # Splitter needs input and split ratios
                    if inputs:
                        # Get qintr parameter for split calculation
                        qintr = self.factory._resolve_parameter('asm1init.QINTR')
                        qin = inputs[0][14]  # Flow rate is at index 14
                        if qin > 0:
                            ratio_to_settler = max(qin - qintr, 0.0) / qin
                            ratio_recycle = min(qintr, qin) / qin
                        else:
                            ratio_to_settler, ratio_recycle = 0.5, 0.5
                        split_outputs = component.output(inputs[0], (ratio_to_settler, ratio_recycle))
                        # Store both outputs - we'll handle this better in the graph
                        outputs[component_id] = split_outputs[0]  # to settler
                        outputs[component_id + '_recycle'] = split_outputs[1]  # recycle
                    else:
                        outputs[component_id] = np.zeros(21)
                        outputs[component_id + '_recycle'] = np.zeros(21)
                elif component_id == 'settler':
                    # Settler needs timestep, step, and input
                    if inputs:
                        timestep = self.simulation_settings.get('steady_timestep', 0.010416667)
                        step = 0
                        settler_outputs = component.output(timestep, step, inputs[0])
                        outputs[component_id] = settler_outputs[0]  # sludge return
                        outputs[component_id + '_effluent'] = settler_outputs[2]  # effluent
                    else:
                        outputs[component_id] = np.zeros(21)
                        outputs[component_id + '_effluent'] = np.zeros(21)
                elif component_id == 'effluent':
                    # Effluent just stores the final output
                    if inputs:
                        outputs[component_id] = component.output(inputs[0])
                    else:
                        outputs[component_id] = np.zeros(21)
                else:
                    # Generic component
                    if inputs:
                        outputs[component_id] = component.output(inputs[0])
                    else:
                        outputs[component_id] = np.zeros(21)
            
            # Check convergence
            max_change = 0
            for component_id in outputs:
                if component_id in old_outputs:
                    change = np.max(np.abs(outputs[component_id] - old_outputs[component_id]))
                    max_change = max(max_change, change)
            
            if max_change < tolerance:
                print(f"Converged after {iteration + 1} iterations")
                return True
                
        print(f"Did not converge after {max_iterations} iterations")
        return False
    
    def simulate(self) -> Dict[str, np.ndarray]:
        """Run the simulation.
        
        Returns
        -------
        Dict[str, np.ndarray]
            Final outputs from all components
        """
        mode = self.simulation_settings.get('mode', 'steady')
        
        if mode == 'steady':
            # For steady state, just stabilize
            if self.stabilize():
                outputs = {}
                for component_id in self.components:
                    component = self.components[component_id]
                    inputs = self._get_component_inputs(component_id, outputs)
                    
                    if component_id == 'influent_s':
                        outputs[component_id] = component.output()
                    elif component_id == 'effluent' and hasattr(component, 'effluent_data'):
                        outputs[component_id] = component.effluent_data
                    else:
                        # Use last computed output
                        if hasattr(component, 'y_out'):
                            outputs[component_id] = component.y_out
                        else:
                            outputs[component_id] = np.zeros(21)
                
                return outputs
        else:
            raise NotImplementedError(f"Simulation mode '{mode}' not implemented yet")
        
        return {}