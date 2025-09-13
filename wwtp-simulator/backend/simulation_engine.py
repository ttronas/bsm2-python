"""
Simulation Engine for WWTP Simulator.

This module handles the integration with BSM2-Python library,
builds simulation models from frontend configurations,
and executes simulations using actual BSM2-Python components.
"""

import asyncio
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple, Callable
from models import SimulationConfig, FlowNode, FlowEdge, ComponentValidationError, SimulationError

# Import BSM2-Python components
try:
    from bsm2_python.bsm2.asm1_bsm2 import ASM1Reactor
    from bsm2_python.bsm2.adm1_bsm2 import ADM1Reactor
    from bsm2_python.bsm2.primclar_bsm2 import PrimaryClarifier
    from bsm2_python.bsm2.settler1d_bsm2 import Settler
    from bsm2_python.bsm2.thickener_bsm2 import Thickener
    from bsm2_python.bsm2.dewatering_bsm2 import Dewatering
    from bsm2_python.bsm2.storage_bsm2 import Storage
    from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter
    import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
    import bsm2_python.bsm2.init.adm1init_bsm2 as adm1init
    import bsm2_python.bsm2.init.primclarinit_bsm2 as primclarinit
    import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit
    import bsm2_python.bsm2.init.thickenerinit_bsm2 as thickenerinit
    import bsm2_python.bsm2.init.dewateringinit_bsm2 as dewateringinit
    import bsm2_python.bsm2.init.storageinit_bsm2 as storageinit
    BSM2_AVAILABLE = True
except ImportError as e:
    logging.warning(f"BSM2-Python not available: {e}")
    BSM2_AVAILABLE = False

logger = logging.getLogger(__name__)
# Set debug level for more verbose output when debugging NaN issues
logger.setLevel(logging.DEBUG)

# BSM2 variable indices
SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5 = range(21)

class SimulationEngine:
    """Engine for running BSM2-based wastewater treatment plant simulations."""
    
    def __init__(self):
        """Initialize the simulation engine."""
        self.bsm2_components = {}
        self.influent_data = None
        
    def validate_configuration(self, config: SimulationConfig) -> bool:
        """Validate a simulation configuration."""
        if not BSM2_AVAILABLE:
            raise ComponentValidationError("BSM2-Python library not available")
        
        if not config.nodes:
            raise ComponentValidationError("No components in configuration")
        
        # Validate component types
        valid_types = ['influent', 'asm1-reactor', 'adm1-reactor', 'primary-clarifier', 
                      'settler', 'thickener', 'dewatering', 'storage-tank', 'combiner', 'splitter']
        for node in config.nodes:
            component_type = node.data.get('componentType')
            if component_type not in valid_types:
                raise ComponentValidationError(f"Unknown component type: {component_type}")
        
        # Validate connections
        if config.edges:
            node_ids = {node.id for node in config.nodes}
            for edge in config.edges:
                if edge.source not in node_ids:
                    raise ComponentValidationError(f"Source node not found: {edge.source}")
                if edge.target not in node_ids:
                    raise ComponentValidationError(f"Target node not found: {edge.target}")
        
        # Note: Cycles are allowed and necessary in BSM2 (e.g., recycle streams)
        return True
    
    def load_influent_data(self, influent_params: Dict) -> np.ndarray:
        """Load influent data based on component parameters."""
        if influent_params.get('influent_type') == 'constant':
            # Load first line from BSM2 dynamic influent data
            bsm2_data_path = '/home/runner/work/bsm2-python/bsm2-python/src/bsm2_python/data/dyninfluent_bsm2.csv'
            try:
                data = np.loadtxt(bsm2_data_path, delimiter=',')
                if data.shape[1] >= 22:  # time + 21 state variables
                    # Use first data line
                    first_line = data[0, 1:22]  # Skip time column, take 21 variables
                    return first_line
            except Exception as e:
                logger.warning(f"Could not load BSM2 data: {e}")
            
        elif influent_params.get('influent_type') == 'dynamic':
            # Load full BSM2 dynamic data or custom CSV
            bsm2_data_path = '/home/runner/work/bsm2-python/bsm2-python/src/bsm2_python/data/dyninfluent_bsm2.csv'
            try:
                data = np.loadtxt(bsm2_data_path, delimiter=',')
                if data.shape[1] >= 22:  # time + 21 state variables
                    return data[:, 1:22]  # Skip time column, return all timesteps
            except Exception as e:
                logger.warning(f"Could not load BSM2 dynamic data: {e}")
        
        # Default BSM2 influent values (constant)
        return np.array([30, 69.5, 51.2, 202.3, 28.2, 0, 0, 0, 0, 31.6, 16, 6.95, 7, 125.6, 20959, 15, 0, 0, 0, 0, 0])
    
    def create_bsm2_component(self, node: FlowNode):
        """Create BSM2-Python component instance based on node configuration."""
        comp_type = node.data.get('componentType')
        params = node.data.get('parameters', {})
        
        try:
            if comp_type == 'influent':
                # Influent is handled separately in simulation loop
                return None
                
            elif comp_type == 'asm1-reactor':
                # Create ASM1 reactor using BSM2-Python
                volume = params.get('volume', 1000)
                kla = params.get('kla', 10)
                
                reactor = ASM1Reactor(
                    kla, volume, asm1init.YINIT1, asm1init.PAR1, 
                    False, 0.0, tempmodel=False, activate=False
                )
                return reactor
                
            elif comp_type == 'adm1-reactor':
                # Create ADM1 reactor
                reactor = ADM1Reactor(
                    adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, 
                    adm1init.INTERFACEPAR, adm1init.DIM_D
                )
                return reactor
                
            elif comp_type == 'primary-clarifier':
                # Create primary clarifier
                clarifier = PrimaryClarifier(
                    primclarinit.VOL_P, primclarinit.YINIT1, primclarinit.PAR_P,
                    asm1init.PAR1, primclarinit.XVECTOR_P, tempmodel=False, activate=False
                )
                return clarifier
                
            elif comp_type == 'settler':
                # Create settler
                settler = Settler(
                    settler1dinit.DIM, settler1dinit.LAYER, 
                    asm1init.QR, asm1init.QW, settler1dinit.settlerinit,
                    settler1dinit.SETTLERPAR, asm1init.PAR1, False, settler1dinit.MODELTYPE
                )
                return settler
                
            elif comp_type == 'thickener':
                # Create thickener
                thickener = Thickener(thickenerinit.THICKENERPAR)
                return thickener
                
            elif comp_type == 'dewatering':
                # Create dewatering unit
                dewatering = Dewatering(dewateringinit.DEWATERINGPAR)
                return dewatering
                
            elif comp_type == 'storage-tank':
                # Create storage tank
                volume = params.get('volume', 500)
                storage = Storage(volume, storageinit.ystinit, False, False)
                return storage
                
            elif comp_type == 'combiner':
                # Create combiner
                return Combiner()
                
            elif comp_type == 'splitter':
                # Create splitter with proper type based on node configuration
                node_label = node.data.get('label', '')
                
                if 'Input Splitter' in node_label:
                    # Input splitter is type 2 (flow threshold)
                    return Splitter(sp_type=2)
                else:
                    # Default type 1 splitter
                    return Splitter()
                
        except Exception as e:
            logger.error(f"Failed to create BSM2 component {comp_type}: {e}")
            return None
            
        return None
    
    def topological_sort(self, config: SimulationConfig) -> List[str]:
        """Perform topological sorting to determine component execution order."""
        # Build adjacency list
        graph = {node.id: [] for node in config.nodes}
        in_degree = {node.id: 0 for node in config.nodes}
        
        for edge in config.edges:
            graph[edge.source].append(edge.target)
            in_degree[edge.target] += 1
        
        # Kahn's algorithm for topological sorting
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Handle cycles (recycle streams) - add remaining nodes
        remaining = [node_id for node_id, degree in in_degree.items() if degree > 0]
        result.extend(remaining)
        
        return result
    
    def get_component_inputs(self, node_id: str, config: SimulationConfig, component_outputs: Dict[str, Any]) -> List[np.ndarray]:
        """Get inputs for a component based on its connections."""
        inputs = []
        
        # Find all edges targeting this node
        input_edges = [edge for edge in config.edges if edge.target == node_id]
        
        if not input_edges:
            return inputs
        
        # Sort by target handle to maintain input order
        input_edges.sort(key=lambda e: e.targetHandle if hasattr(e, 'targetHandle') else 'input-0')
        
        for edge in input_edges:
            source_id = edge.source
            source_handle = getattr(edge, 'sourceHandle', 'output-0')
            
            if source_id in component_outputs:
                output_data = component_outputs[source_id]
                
                # Handle different output types (single output vs multiple outputs)
                if isinstance(output_data, dict):
                    # Multiple named outputs
                    handle_key = source_handle.replace('output-', '').replace('effluent', 'effluent').replace('sludge', 'sludge').replace('recycle', 'recycle')
                    if handle_key in output_data:
                        inputs.append(output_data[handle_key])
                    elif 'output' in output_data:
                        inputs.append(output_data['output'])
                    else:
                        # Use first available output
                        inputs.append(list(output_data.values())[0])
                elif isinstance(output_data, (list, tuple)):
                    # Multiple indexed outputs
                    output_idx = int(source_handle.replace('output-', '')) if 'output-' in source_handle else 0
                    if output_idx < len(output_data):
                        inputs.append(output_data[output_idx])
                    else:
                        inputs.append(output_data[0] if output_data else np.zeros(21))
                else:
                    # Single output
                    inputs.append(output_data)
            else:
                # Default to zeros if source not found
                inputs.append(np.zeros(21))
        
        return inputs

    def initialize_component_flows(self, influent_data: np.ndarray) -> np.ndarray:
        """Initialize component flows with influent values but set Q to a small value to avoid loops."""
        # Create a copy of influent data
        initial_flow = influent_data.copy()
        # Set flow rate (Q) to a very small value (1.0) to initialize recycle loops
        # This follows the BSM2 pattern of initializing flows before solving loops
        initial_flow[Q] = 1.0  # Very small flow to avoid division by zero but enable proper initialization
        return initial_flow

    async def run_simulation(
        self, 
        config: SimulationConfig,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Dict[str, Any]:
        """Run a simulation with the given configuration using BSM2-Python components."""
        if not BSM2_AVAILABLE:
            raise SimulationError("BSM2-Python library not available")
        
        try:
            # Validate configuration
            self.validate_configuration(config)
            
            if progress_callback:
                progress_callback(10.0)
            
            # Build BSM2 components
            components = {}
            influent_nodes = []
            node_map = {node.id: node for node in config.nodes}
            
            for node in config.nodes:
                if node.data.get('componentType') == 'influent':
                    influent_nodes.append(node)
                else:
                    component = self.create_bsm2_component(node)
                    if component:
                        components[node.id] = component
            
            # Load influent data
            if influent_nodes:
                influent_params = influent_nodes[0].data.get('parameters', {})
                influent_data = self.load_influent_data(influent_params)
            else:
                # Default influent if none specified
                influent_data = self.load_influent_data({'influent_type': 'constant'})
            
            # Prepare time vector
            timestep_days = config.settings.timestep / (24 * 60)  # Convert minutes to days
            end_time_days = config.settings.endTime
            time_steps = int(end_time_days / timestep_days)
            
            if len(influent_data.shape) == 1:
                # Constant influent - repeat for all timesteps
                influent_data = np.tile(influent_data, (time_steps, 1))
            elif len(influent_data.shape) == 2:
                # Dynamic influent - use as is or interpolate
                if influent_data.shape[0] < time_steps:
                    # Repeat last value if needed
                    last_row = influent_data[-1:, :]
                    additional_rows = np.tile(last_row, (time_steps - influent_data.shape[0], 1))
                    influent_data = np.vstack([influent_data, additional_rows])
                elif influent_data.shape[0] > time_steps:
                    # Truncate if too long
                    influent_data = influent_data[:time_steps, :]
            
            if progress_callback:
                progress_callback(30.0)
            
            # Get component execution order through topology sorting
            execution_order = self.topological_sort(config)
            
            # Initialize result storage
            results = {
                'time': np.arange(0, time_steps) * timestep_days,
                'influent': influent_data,
                'components': {},
                'success': True,
                'message': 'Simulation completed using BSM2-Python components'
            }
            
            # Initialize component outputs storage for each timestep
            all_component_results = {node_id: [] for node_id in execution_order}
            
            if progress_callback:
                progress_callback(50.0)
            
            # Initialize component flows with small values to avoid NaN issues in recycle loops
            initial_flow = self.initialize_component_flows(influent_data[0] if len(influent_data) > 0 else np.zeros(21))
            
            # Run simulation timestep by timestep (like BSM2_base.py step method)
            for i in range(time_steps):
                step_time = i * timestep_days
                stepsize = timestep_days
                
                # Current timestep component outputs
                component_outputs = {}
                
                # Get influent data for current timestep
                current_influent = influent_data[i] if i < len(influent_data) else influent_data[-1]
                
                # Process influent nodes first
                for influent_node in influent_nodes:
                    component_outputs[influent_node.id] = current_influent
                
                # Initialize all non-influent nodes with initial flow to avoid NaN in loops
                for node_id in execution_order:
                    if node_id not in [n.id for n in influent_nodes] and node_id not in component_outputs:
                        component_outputs[node_id] = initial_flow.copy()
                
                # Iterative solution for recycle streams (up to 5 iterations to ensure convergence)
                for iteration in range(5):
                    prev_outputs = component_outputs.copy()
                    
                    # Process components in topological order
                    for node_id in execution_order:
                        if node_id in [n.id for n in influent_nodes]:
                            continue  # Already processed influent
                        
                        node = node_map[node_id]
                        comp_type = node.data.get('componentType')
                        component = components.get(node_id)
                        
                        if not component:
                            continue
                        
                        try:
                            # Get inputs for this component
                            inputs = self.get_component_inputs(node_id, config, component_outputs)
                            
                            if not inputs:
                                # No inputs, use initialized flow
                                input_data = initial_flow.copy()
                            elif len(inputs) == 1:
                                input_data = inputs[0]
                            else:
                                # Multiple inputs - combine them (for combiners)
                                if comp_type == 'combiner' and hasattr(component, 'output'):
                                    try:
                                        input_data = component.output(*inputs)
                                        component_outputs[node_id] = input_data
                                        continue
                                    except Exception as e:
                                        logger.warning(f"Combiner {node_id} error at timestep {i}, iteration {iteration}: {e}")
                                        # Use first valid input if combiner fails
                                        input_data = next((inp for inp in inputs if not np.any(np.isnan(inp))), initial_flow.copy())
                                else:
                                    input_data = inputs[0]  # Use first input for other components
                            
                            # Validate input data - replace NaN/inf with initial flow
                            if np.any(np.isnan(input_data)) or np.any(np.isinf(input_data)):
                                logger.warning(f"Invalid input data for {node_id} at timestep {i}, iteration {iteration}, using initial flow")
                                input_data = initial_flow.copy()
                            
                            # Call BSM2-Python component's output method
                            if hasattr(component, 'output'):
                                if comp_type == 'asm1-reactor':
                                    output = component.output(stepsize, step_time, input_data)
                                elif comp_type == 'adm1-reactor':
                                    # ADM1 returns (interface, digester, gas) - add more verbose error handling
                                    try:
                                        interface, digester, gas = component.output(stepsize, step_time, input_data, 35.0)
                                        output = {'liquid': interface, 'gas': gas, 'internal': digester}
                                    except Exception as e:
                                        logger.error(f"ADM1 reactor {node_id} failed at timestep {i}, iteration {iteration}: {e}")
                                        logger.debug(f"ADM1 input data: {input_data}")
                                        logger.debug(f"ADM1 stepsize: {stepsize}, step_time: {step_time}")
                                        # Use previous output or initial flow
                                        if node_id in prev_outputs:
                                            output = prev_outputs[node_id]
                                        else:
                                            output = {'liquid': initial_flow.copy(), 'gas': np.zeros(51), 'internal': np.zeros(51)}
                                elif comp_type == 'primary-clarifier':
                                    # Primary clarifier returns (underflow, overflow, internal)
                                    uf, of, internal = component.output(stepsize, step_time, input_data)
                                    output = {'effluent': of, 'sludge': uf, 'internal': internal}
                                elif comp_type == 'settler':
                                    # Settler returns (recycle, waste, overflow, tss_internal)
                                    recycle, waste, overflow, _, tss = component.output(stepsize, step_time, input_data)
                                    output = {'recycle': recycle, 'sludge': waste, 'effluent': overflow}
                                elif comp_type == 'thickener':
                                    # Thickener returns (underflow, overflow)
                                    uf, of = component.output(input_data)
                                    output = {'output-0': uf, 'output-1': of}
                                elif comp_type == 'dewatering':
                                    # Dewatering returns (solid, liquid)
                                    solid, liquid = component.output(input_data)
                                    output = {'output-0': solid, 'output-1': liquid}
                                elif comp_type == 'storage-tank':
                                    # Storage tank returns (output, volume)
                                    out, vol = component.output(stepsize, step_time, input_data, 0)
                                    output = out
                                elif comp_type == 'splitter':
                                    # BSM2 splitter - handle different types properly
                                    node_label = node.data.get('label', '')
                                    
                                    if 'Input Splitter' in node_label:
                                        # Type 2 splitter - uses flow threshold
                                        # Everything below 60000 goes to first output, above goes to second
                                        out1, out2 = component.output(input_data, (0.0, 0.0), float(60000))
                                        output = [out1, out2]
                                    else:
                                        # Type 1 splitter with fixed ratio
                                        split_ratio = node.data.get('parameters', {}).get('split_ratio', 0.5)
                                        if split_ratio == 0.0:
                                            # All to first output
                                            out1, out2 = component.output(input_data, (1.0, 0.0))
                                        else:
                                            # Regular split
                                            out1, out2 = component.output(input_data, (1 - split_ratio, split_ratio))
                                        output = [out1, out2]
                                else:
                                    output = component.output(input_data)
                            else:
                                output = input_data
                            
                            # Validate output - replace NaN/inf with previous output or initial flow
                            if isinstance(output, (list, tuple)):
                                validated_output = []
                                for j, out in enumerate(output):
                                    if np.any(np.isnan(out)) or np.any(np.isinf(out)):
                                        logger.warning(f"Invalid output {j} from {node_id} at timestep {i}, iteration {iteration}")
                                        if node_id in prev_outputs and isinstance(prev_outputs[node_id], (list, tuple)) and j < len(prev_outputs[node_id]):
                                            validated_output.append(prev_outputs[node_id][j])
                                        else:
                                            validated_output.append(initial_flow.copy())
                                    else:
                                        validated_output.append(out)
                                output = validated_output
                            elif isinstance(output, dict):
                                for key, val in output.items():
                                    if np.any(np.isnan(val)) or np.any(np.isinf(val)):
                                        logger.warning(f"Invalid output {key} from {node_id} at timestep {i}, iteration {iteration}")
                                        if node_id in prev_outputs and isinstance(prev_outputs[node_id], dict) and key in prev_outputs[node_id]:
                                            output[key] = prev_outputs[node_id][key]
                                        else:
                                            output[key] = initial_flow.copy()
                            else:
                                if np.any(np.isnan(output)) or np.any(np.isinf(output)):
                                    logger.warning(f"Invalid output from {node_id} at timestep {i}, iteration {iteration}")
                                    if node_id in prev_outputs:
                                        output = prev_outputs[node_id]
                                    else:
                                        output = initial_flow.copy()
                            
                            component_outputs[node_id] = output
                            
                        except Exception as e:
                            logger.error(f"Error in component {node_id} at timestep {i}, iteration {iteration}: {e}")
                            logger.debug(f"Component type: {comp_type}")
                            if node_id in prev_outputs:
                                component_outputs[node_id] = prev_outputs[node_id]
                            else:
                                component_outputs[node_id] = initial_flow.copy()
                
                # Store results for this timestep
                for node_id in execution_order:
                    if node_id in component_outputs:
                        all_component_results[node_id].append(component_outputs[node_id])
                    else:
                        all_component_results[node_id].append(current_influent)
                
                # Update progress
                if progress_callback and i % max(1, time_steps // 20) == 0:
                    progress = 50.0 + (i / time_steps) * 45.0
                    progress_callback(progress)
            
            # Store all results
            results['components'] = all_component_results
            
            if progress_callback:
                progress_callback(100.0)
            
            return results
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise SimulationError(f"Simulation failed: {str(e)}")