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
    import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init_bsm2
    import bsm2_python.bsm2.init.asm1init_bsm1 as asm1init_bsm1
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
logger.setLevel(logging.DEBUG)  # Increase to DEBUG to see ADM1 details

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
    
    def detect_simulation_type(self, config: SimulationConfig) -> str:
        """Detect if this is a BSM1 or BSM2 simulation based on configuration name/description."""
        name_lower = config.name.lower()
        desc_lower = config.description.lower()
        
        if 'bsm1' in name_lower or 'bsm1' in desc_lower:
            return 'BSM1'
        elif 'bsm2' in name_lower or 'bsm2' in desc_lower:
            return 'BSM2'
        else:
            # Default to BSM2 for backwards compatibility
            return 'BSM2'
    
    def create_bsm2_component(self, node: FlowNode, simulation_type: str = 'BSM2'):
        """Create BSM2-Python component instance based on node configuration."""
        comp_type = node.data.get('componentType')
        params = node.data.get('parameters', {})
        
        try:
            if comp_type == 'influent':
                # Influent is handled separately in simulation loop
                return None
                
            elif comp_type == 'asm1-reactor':
                # Create ASM1 reactor using appropriate initialization based on simulation type
                volume = params.get('volume', 1000)
                kla = params.get('kla', 10)
                
                # Select initialization files based on simulation type
                if simulation_type == 'BSM1':
                    asm1init = asm1init_bsm1
                    logger.info(f"Creating ASM1 reactor {node.id} with BSM1 initialization")
                else:
                    asm1init = asm1init_bsm2
                    logger.info(f"Creating ASM1 reactor {node.id} with BSM2 initialization")
                
                # Use custom parameters if provided, otherwise use defaults
                yinit = params.get('yinit', asm1init.YINIT1)
                par = params.get('parameters_asm1', asm1init.PAR1)
                carb = params.get('carb', False)
                carbonsource_conc = params.get('carbonsource_conc', 0.0)
                
                reactor = ASM1Reactor(
                    kla, volume, yinit, par, 
                    carb, carbonsource_conc, tempmodel=False, activate=False
                )
                return reactor
                
            elif comp_type == 'adm1-reactor':
                # Create ADM1 reactor
                reactor = ADM1Reactor(
                    adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, 
                    adm1init.INTERFACEPAR, adm1init.DIM_D
                )
                return reactor
                
            elif comp_type == 'settler':
                # Create settler - use appropriate ASM1 init based on simulation type
                if simulation_type == 'BSM1':
                    asm1init = asm1init_bsm1
                else:
                    asm1init = asm1init_bsm2
                    
                settler = Settler(
                    settler1dinit.DIM, settler1dinit.LAYER, 
                    asm1init.QR, asm1init.QW, settler1dinit.settlerinit,
                    settler1dinit.SETTLERPAR, asm1init.PAR1, False, settler1dinit.MODELTYPE
                )
                return settler
                
            elif comp_type == 'primary-clarifier':
                # Create primary clarifier - use appropriate ASM1 init based on simulation type
                if simulation_type == 'BSM1':
                    asm1init = asm1init_bsm1
                else:
                    asm1init = asm1init_bsm2
                    
                clarifier = PrimaryClarifier(
                    primclarinit.VOL_P, primclarinit.YINIT1, primclarinit.PAR_P,
                    asm1init.PAR1, primclarinit.XVECTOR_P, tempmodel=False, activate=False
                )
                return clarifier
                
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
    
    def bsm2_topology_sort(self, config: SimulationConfig) -> List[str]:
        """Perform BSM2-specific topology sorting to match BSM2_base.py execution order.
        
        This method attempts to follow the exact execution sequence from BSM2_base.py step() method:
        1. Input splitter
        2. Bypass plant splitter  
        3. Primary clarifier pre-combiner
        4. Primary clarifier
        5. Primary clarifier post-combiner
        6. Bypass reactor splitter
        7. Reactor combiner
        8. Reactors 1-5 in sequence
        9. Reactor splitter
        10. Settler
        11. Effluent combiner
        12. Thickener
        13. Thickener splitter
        14. ADM1 combiner
        15. ADM1 reactor
        16. Dewatering
        17. Storage
        18. Storage splitter
        """
        # Create node map for easy lookup
        node_map = {node.id: node for node in config.nodes}
        
        # Define BSM2-specific execution priorities based on component types and labels
        bsm2_order = []
        
        # Phase 1: Input processing
        for node in config.nodes:
            if node.data.get('componentType') == 'influent':
                bsm2_order.append(node.id)
        
        # Phase 2: Input splitting and bypass
        for node in config.nodes:
            comp_type = node.data.get('componentType')
            label = node.data.get('label', '').lower()
            if comp_type == 'splitter' and 'input' in label:
                bsm2_order.append(node.id)
        
        for node in config.nodes:
            comp_type = node.data.get('componentType')
            label = node.data.get('label', '').lower()
            if comp_type == 'splitter' and 'bypass' in label and 'plant' in label:
                bsm2_order.append(node.id)
        
        # Phase 3: Primary clarifier section
        for node in config.nodes:
            comp_type = node.data.get('componentType')
            label = node.data.get('label', '').lower()
            if comp_type == 'combiner' and 'primary' in label and 'pre' in label:
                bsm2_order.append(node.id)
        
        for node in config.nodes:
            if node.data.get('componentType') == 'primary-clarifier':
                bsm2_order.append(node.id)
        
        for node in config.nodes:
            comp_type = node.data.get('componentType')
            label = node.data.get('label', '').lower()
            if comp_type == 'combiner' and 'primary' in label and 'post' in label:
                bsm2_order.append(node.id)
        
        # Phase 4: Reactor section
        for node in config.nodes:
            comp_type = node.data.get('componentType')
            label = node.data.get('label', '').lower()
            if comp_type == 'splitter' and 'bypass' in label and 'reactor' in label:
                bsm2_order.append(node.id)
        
        for node in config.nodes:
            comp_type = node.data.get('componentType')
            label = node.data.get('label', '').lower()
            if comp_type == 'combiner' and 'reactor' in label:
                bsm2_order.append(node.id)
        
        # Add reactors in sequence (1-5)
        for i in range(1, 6):
            for node in config.nodes:
                comp_type = node.data.get('componentType')
                label = node.data.get('label', '').lower()
                if comp_type == 'asm1-reactor' and f'reactor {i}' in label:
                    bsm2_order.append(node.id)
        
        # Reactor splitter
        for node in config.nodes:
            comp_type = node.data.get('componentType')
            label = node.data.get('label', '').lower()
            if comp_type == 'splitter' and 'reactor' in label and 'bypass' not in label:
                bsm2_order.append(node.id)
        
        # Phase 5: Settler
        for node in config.nodes:
            if node.data.get('componentType') == 'settler':
                bsm2_order.append(node.id)
        
        # Phase 6: Effluent
        for node in config.nodes:
            comp_type = node.data.get('componentType')
            label = node.data.get('label', '').lower()
            if comp_type == 'combiner' and 'effluent' in label:
                bsm2_order.append(node.id)
        
        # Phase 7: Sludge treatment
        for node in config.nodes:
            if node.data.get('componentType') == 'thickener':
                bsm2_order.append(node.id)
        
        for node in config.nodes:
            comp_type = node.data.get('componentType')
            label = node.data.get('label', '').lower()
            if comp_type == 'splitter' and 'thickener' in label:
                bsm2_order.append(node.id)
        
        for node in config.nodes:
            comp_type = node.data.get('componentType')
            label = node.data.get('label', '').lower()
            if comp_type == 'combiner' and 'adm1' in label:
                bsm2_order.append(node.id)
        
        for node in config.nodes:
            if node.data.get('componentType') == 'adm1-reactor':
                bsm2_order.append(node.id)
        
        for node in config.nodes:
            if node.data.get('componentType') == 'dewatering':
                bsm2_order.append(node.id)
        
        for node in config.nodes:
            if node.data.get('componentType') == 'storage-tank':
                bsm2_order.append(node.id)
        
        for node in config.nodes:
            comp_type = node.data.get('componentType')
            label = node.data.get('label', '').lower()
            if comp_type == 'splitter' and 'storage' in label:
                bsm2_order.append(node.id)
        
        # Add any remaining nodes not yet included
        all_node_ids = {node.id for node in config.nodes}
        remaining_nodes = all_node_ids - set(bsm2_order)
        bsm2_order.extend(remaining_nodes)
        
        logger.info(f"BSM2 topology order: {bsm2_order}")
        return bsm2_order

    def topological_sort(self, config: SimulationConfig) -> List[str]:
        """Perform topological sorting to determine component execution order."""
        # Try BSM2-specific ordering first
        bsm2_order = self.bsm2_topology_sort(config)
        if len(bsm2_order) == len(config.nodes):
            return bsm2_order
        
        # Fallback to standard topological sort
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

    def _create_copies(self, in_arr: np.ndarray, n_copies: int = 1) -> List[np.ndarray]:
        """Create copies of input arrays following BSM2_base.py pattern.
        
        This method replicates the _create_copies functionality from BSM2_base.py
        to properly initialize component flows with influent composition.
        
        Parameters
        ----------
        in_arr : np.ndarray(21)
            BSM2 state array to be copied. 
            [SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP,
            SD1, SD2, SD3, XD4, XD5]
        n_copies : int (optional)
            Number of copies to create. Default is 1.

        Returns
        -------
        out : List[np.ndarray(21)]
            List of copied BSM2 state arrays.
        """
        out = [np.copy(in_arr) for _ in range(n_copies)]
        return out

    def initialize_component_flows(self, influent_data: np.ndarray, num_components: int) -> Dict[str, np.ndarray]:
        """Initialize component flows using BSM2_base.py _create_copies approach.
        
        This method follows the exact pattern used in BSM2_base.py to initialize
        all intermediate flows with the influent composition, maintaining proper
        mass balance while enabling recycle loop convergence.
        """
        # Create copies of influent data for each component that needs initialization
        # This preserves the influent composition across all components at startup
        copies = self._create_copies(influent_data, num_components)
        
        # Return a dictionary for easy component access
        initialized_flows = {}
        for i, copy in enumerate(copies):
            initialized_flows[f"flow_{i}"] = copy
            
        return initialized_flows

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
            
            # Detect simulation type (BSM1 or BSM2)
            simulation_type = self.detect_simulation_type(config)
            logger.info(f"Detected simulation type: {simulation_type}")
            
            for node in config.nodes:
                if node.data.get('componentType') == 'influent':
                    influent_nodes.append(node)
                else:
                    component = self.create_bsm2_component(node, simulation_type)
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
            
            # Initialize component flows using BSM2_base.py _create_copies approach
            # This creates proper copies of influent data for all components to maintain mass balance
            num_components = len([n for n in config.nodes if n.data.get('componentType') != 'influent'])
            initialized_flows = self.initialize_component_flows(
                influent_data[0] if len(influent_data) > 0 else np.zeros(21), 
                num_components
            )
            
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
                
                # Initialize ALL component outputs with influent composition following BSM2_base.py pattern
                # This ensures proper mass balance and avoids extreme concentrations during first iteration
                for node_id in execution_order:
                    if node_id not in [n.id for n in influent_nodes]:
                        # Initialize all non-influent components with influent composition
                        # This matches BSM2_base.py where all intermediate flows start as influent copies
                        component_outputs[node_id] = current_influent.copy()
                        
                        # For components with multiple outputs, initialize all outputs
                        node = node_map[node_id]
                        comp_type = node.data.get('componentType')
                        
                        if comp_type in ['splitter', 'primary-clarifier', 'settler', 'thickener', 'dewatering', 'adm1-reactor']:
                            # These components have multiple outputs - initialize all with influent composition
                            if comp_type == 'splitter':
                                component_outputs[node_id] = [current_influent.copy(), current_influent.copy()]
                            elif comp_type == 'primary-clarifier':
                                component_outputs[node_id] = {
                                    'effluent': current_influent.copy(), 
                                    'sludge': current_influent.copy(), 
                                    'internal': current_influent.copy()
                                }
                            elif comp_type == 'settler':
                                component_outputs[node_id] = {
                                    'recycle': current_influent.copy(),
                                    'sludge': current_influent.copy(), 
                                    'effluent': current_influent.copy()
                                }
                            elif comp_type == 'thickener':
                                component_outputs[node_id] = {
                                    'output-0': current_influent.copy(),
                                    'output-1': current_influent.copy()
                                }
                            elif comp_type == 'dewatering':
                                component_outputs[node_id] = {
                                    'output-0': current_influent.copy(),
                                    'output-1': current_influent.copy()
                                }
                            elif comp_type == 'adm1-reactor':
                                component_outputs[node_id] = {
                                    'adm2asm': current_influent.copy(),
                                    'digester': current_influent.copy(),
                                    'asm2adm': current_influent.copy()
                                }
                
                # Iterative solution for recycle streams (up to 10 iterations to ensure convergence)
                # First iteration: Only process influent and initialize all other outputs as influent composition
                # Subsequent iterations: Process components normally to converge recycle streams
                for iteration in range(10):
                    prev_outputs = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in component_outputs.items()}
                    
                    # Process components in topological order
                    for node_id in execution_order:
                        if node_id in [n.id for n in influent_nodes]:
                            continue  # Already processed influent
                        
                        # For the first iteration, keep all non-influent components as influent composition
                        # This prevents artificial concentration buildup during initialization
                        if iteration == 0:
                            # Skip processing non-influent components in first iteration
                            # They remain initialized as influent composition
                            continue
                        
                        node = node_map[node_id]
                        comp_type = node.data.get('componentType')
                        component = components.get(node_id)
                        
                        if not component:
                            continue
                        
                        try:
                            # Get inputs for this component
                            inputs = self.get_component_inputs(node_id, config, component_outputs)
                            
                            if not inputs:
                                # No inputs, use current influent composition (maintaining BSM2 pattern)
                                input_data = current_influent.copy()
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
                                        # Use current influent composition if combiner fails (maintains mass balance)
                                        input_data = next((inp for inp in inputs if not np.any(np.isnan(inp))), current_influent.copy())
                                else:
                                    input_data = inputs[0]  # Use first input for other components
                            
                            # Check for invalid input data - do not replace, let it fail to identify issues
                            if np.any(np.isnan(input_data)) or np.any(np.isinf(input_data)):
                                logger.error(f"Invalid input data for {node_id} at timestep {i}, iteration {iteration}: {input_data}")
                                raise SimulationError(f"Component {node_id} received invalid input data (NaN/inf) at timestep {i}")
                            
                            # Call BSM2-Python component's output method
                            if hasattr(component, 'output'):
                                if comp_type == 'asm1-reactor':
                                    output = component.output(stepsize, step_time, input_data)
                                elif comp_type == 'adm1-reactor':
                                    # ADM1 returns (yi_out2/ADM2ASM, yd_out/digester, yi_out1/ASM2ADM) - add more verbose error handling
                                    try:
                                        if logger.level <= logging.DEBUG and iteration == 0:
                                            logger.debug(f"ADM1 reactor {node_id} at timestep {i}, iteration {iteration}")
                                            logger.debug(f"ADM1 input data: {input_data}")
                                            logger.debug(f"ADM1 input NaN check: {np.any(np.isnan(input_data))}")
                                            logger.debug(f"ADM1 input inf check: {np.any(np.isinf(input_data))}")
                                        
                                        adm2asm, digester, asm2adm = component.output(stepsize, step_time, input_data, 308.15)  # 35°C in Kelvin
                                        
                                        if logger.level <= logging.DEBUG and iteration == 0:
                                            logger.debug(f"ADM1 output adm2asm shape: {adm2asm.shape}, NaN: {np.any(np.isnan(adm2asm))}")
                                            logger.debug(f"ADM1 output digester shape: {digester.shape}, NaN: {np.any(np.isnan(digester))}")
                                            logger.debug(f"ADM1 output asm2adm shape: {asm2adm.shape}, NaN: {np.any(np.isnan(asm2adm))}")
                                        
                                        output = {'adm2asm': adm2asm, 'digester': digester, 'asm2adm': asm2adm}
                                    except Exception as e:
                                        logger.error(f"ADM1 reactor {node_id} failed at timestep {i}, iteration {iteration}: {e}")
                                        logger.debug(f"ADM1 input data: {input_data}")
                                        logger.debug(f"ADM1 stepsize: {stepsize}, step_time: {step_time}")
                                        # Do not hide the error - let it propagate to identify the underlying issue
                                        raise SimulationError(f"ADM1 reactor {node_id} failed: {e}")
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
                            
                            # Check for invalid output - do not replace, let it fail to identify issues
                            if isinstance(output, (list, tuple)):
                                for j, out in enumerate(output):
                                    if np.any(np.isnan(out)) or np.any(np.isinf(out)):
                                        logger.error(f"Invalid output {j} from {node_id} at timestep {i}, iteration {iteration}: {out}")
                                        raise SimulationError(f"Component {node_id} produced invalid output {j} (NaN/inf) at timestep {i}")
                            elif isinstance(output, dict):
                                for key, val in output.items():
                                    if np.any(np.isnan(val)) or np.any(np.isinf(val)):
                                        logger.error(f"Invalid output {key} from {node_id} at timestep {i}, iteration {iteration}: {val}")
                                        raise SimulationError(f"Component {node_id} produced invalid output {key} (NaN/inf) at timestep {i}")
                            else:
                                if np.any(np.isnan(output)) or np.any(np.isinf(output)):
                                    logger.error(f"Invalid output from {node_id} at timestep {i}, iteration {iteration}: {output}")
                                    raise SimulationError(f"Component {node_id} produced invalid output (NaN/inf) at timestep {i}")
                            
                            component_outputs[node_id] = output
                            
                        except Exception as e:
                            logger.error(f"Error in component {node_id} at timestep {i}, iteration {iteration}: {e}")
                            logger.debug(f"Component type: {comp_type}")
                            # Do not hide the error - let it propagate to identify the underlying issue
                            raise SimulationError(f"Component {node_id} failed: {e}")
                    
                    # Check for convergence (compare changes between iterations)
                    converged = True
                    for node_id in component_outputs:
                        if node_id in prev_outputs:
                            curr_out = component_outputs[node_id]
                            prev_out = prev_outputs[node_id]
                            
                            # Handle different output types for convergence check
                            if isinstance(curr_out, np.ndarray) and isinstance(prev_out, np.ndarray):
                                if not np.allclose(curr_out, prev_out, rtol=1e-6, atol=1e-8):
                                    converged = False
                                    break
                            elif isinstance(curr_out, dict) and isinstance(prev_out, dict):
                                for key in curr_out:
                                    if key in prev_out:
                                        if isinstance(curr_out[key], np.ndarray) and isinstance(prev_out[key], np.ndarray):
                                            if not np.allclose(curr_out[key], prev_out[key], rtol=1e-6, atol=1e-8):
                                                converged = False
                                                break
                                if not converged:
                                    break
                            elif isinstance(curr_out, (list, tuple)) and isinstance(prev_out, (list, tuple)):
                                for j, (curr_item, prev_item) in enumerate(zip(curr_out, prev_out)):
                                    if isinstance(curr_item, np.ndarray) and isinstance(prev_item, np.ndarray):
                                        if not np.allclose(curr_item, prev_item, rtol=1e-6, atol=1e-8):
                                            converged = False
                                            break
                                if not converged:
                                    break
                    
                    if converged and iteration > 0:
                        if logger.level <= logging.DEBUG:
                            logger.debug(f"Converged after {iteration + 1} iterations at timestep {i}")
                        break
                else:
                    if logger.level <= logging.DEBUG:
                        logger.debug(f"Did not converge within 10 iterations at timestep {i}")
                
                
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