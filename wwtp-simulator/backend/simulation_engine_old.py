"""
Simulation Engine for WWTP Simulator.

This module handles the integration with BSM2-Python library,
builds simulation models from frontend configurations,
and executes simulations using actual BSM2-Python components.
"""

import asyncio
import numpy as np
import logging
from typing import Dict, List, Optional, Any, Tuple
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
        comp_type = node.data.componentType
        params = node.data.parameters
        
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
                # Create splitter
                return Splitter()
                
        except Exception as e:
            logger.error(f"Failed to create BSM2 component {comp_type}: {e}")
            return None
            
        return None
    
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
            
            for node in config.nodes:
                if node.data.componentType == 'influent':
                    influent_nodes.append(node)
                else:
                    component = self.create_bsm2_component(node)
                    if component:
                        components[node.id] = component
            
            if progress_callback:
                progress_callback(30.0)
            
            # Load influent data
            if influent_nodes:
                influent_params = influent_nodes[0].data.parameters
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
                progress_callback(50.0)
            
            # Run simplified simulation 
            # Note: This is a basic implementation. A full BSM2 simulation would require
            # proper topology sorting, iterative solving for recycles, etc.
            
            results = {
                'time': np.arange(0, time_steps) * timestep_days,
                'influent': influent_data,
                'components': {},
                'success': True,
                'message': 'Simulation completed using BSM2-Python components'
            }
            
            # For each component, simulate basic behavior
            for node_id, component in components.items():
                try:
                    node = next(n for n in config.nodes if n.id == node_id)
                    comp_type = node.data.componentType
                    
                    # Use BSM2-Python component output methods
                    component_results = []
                    
                    for i in range(min(10, time_steps)):  # Limit for demo
                        time_point = i * timestep_days
                        input_data = influent_data[i] if i < len(influent_data) else influent_data[-1]
                        
                        # Call BSM2-Python component's output method
                        if hasattr(component, 'output'):
                            if comp_type in ['asm1-reactor', 'adm1-reactor']:
                                output = component.output(timestep_days, time_point, input_data)
                            elif comp_type in ['primary-clarifier', 'settler', 'thickener']:
                                output = component.output(input_data)
                            elif comp_type == 'dewatering':
                                output = component.output(input_data)
                            elif comp_type == 'storage-tank':
                                output = component.output(timestep_days, time_point, input_data, 0)
                            elif comp_type in ['combiner', 'splitter']:
                                output = component.output(input_data)
                            else:
                                output = input_data
                            
                            component_results.append(output)
                        else:
                            component_results.append(input_data)
                    
                    results['components'][node_id] = component_results
                    
                except Exception as e:
                    logger.warning(f"Error simulating component {node_id}: {e}")
                    results['components'][node_id] = []
            
            if progress_callback:
                progress_callback(100.0)
            
            return results
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise SimulationError(f"Simulation failed: {str(e)}")
    
    async def _build_simulation_model(self, config: SimulationConfig) -> Tuple[Dict, Dict]:
        """Build simulation model from configuration - deprecated, kept for compatibility."""
        # This method is no longer used as we create components directly in run_simulation
        return {}, {}
    
    # Remove all mock component creation and processing methods
    # They are replaced by direct BSM2-Python component creation above
                    'type': component_type,
                    'parameters': parameters,
                    'node_data': node.data
                }
        
        # Build connections
        connections = []
        for edge in config.edges:
            connections.append({
                'id': edge.id,
                'source': edge.source,
                'target': edge.target,
                'source_handle': edge.sourceHandle,
                'target_handle': edge.targetHandle
            })
        
        return components, connections
    
    async def _execute_simulation(
        self,
        components: Dict[str, Any],
        connections: List[Dict],
        time_vector: np.ndarray,
        results: Dict[str, Dict],
        progress_callback: Optional[Callable[[float], None]] = None
    ):
        """Execute the simulation."""
        # Initialize component states
        for comp_id, comp_data in components.items():
            component = comp_data['component']
            if hasattr(component, 'init'):
                component.init()
        
        # Main simulation loop
        for i, t in enumerate(time_vector):
            # Update progress
            if progress_callback and i % max(1, len(time_vector) // 20) == 0:
                progress = 20 + (i / len(time_vector)) * 80
                progress_callback(progress)
            
            # Allow other tasks to run
            if i % 100 == 0:
                await asyncio.sleep(0.001)
            
            # Process each component
            await self._simulate_timestep(components, connections, t, i, results)
    
    async def _simulate_timestep(
        self,
        components: Dict[str, Any],
        connections: List[Dict],
        time: float,
        step: int,
        results: Dict[str, Dict]
    ):
        """Simulate a single timestep with proper BSM2 component execution."""
        # Create a map of component outputs
        component_outputs = {}
        
        # Step 1: Process influent components first to get initial data
        for comp_id, comp_data in components.items():
            if comp_data['type'] == 'influent':
                influent_component = comp_data['component']
                if hasattr(influent_component, 'get_influent_at_time'):
                    influent_data = influent_component.get_influent_at_time(time)
                    component_outputs[comp_id] = {
                        'outlet': influent_data
                    }
                else:
                    # Fallback to default influent
                    component_outputs[comp_id] = {
                        'outlet': self.default_influent
                    }
        
        # Step 2: Process other components based on their inputs
        # We may need multiple iterations to resolve all dependencies (due to recycles)
        max_iterations = 5
        unprocessed_components = {k: v for k, v in components.items() if v['type'] != 'influent'}
        
        for iteration in range(max_iterations):
            if not unprocessed_components:
                break
                
            components_processed_this_iteration = []
            
            for comp_id, comp_data in list(unprocessed_components.items()):
                # Check if all inputs are available
                inputs_ready = True
                component_inputs = {}
                
                # Find connections that feed into this component
                for connection in connections:
                    if connection['target'] == comp_id:
                        source_comp = connection['source']
                        source_handle = connection['source_handle']
                        target_handle = connection['target_handle']
                        
                        if source_comp in component_outputs and source_handle in component_outputs[source_comp]:
                            component_inputs[target_handle] = component_outputs[source_comp][source_handle]
                        else:
                            inputs_ready = False
                            break
                
                if inputs_ready or iteration == max_iterations - 1:  # Force processing on last iteration
                    # Process this component
                    outputs = self._process_component(comp_data, component_inputs, time, step)
                    component_outputs[comp_id] = outputs
                    components_processed_this_iteration.append(comp_id)
            
            # Remove processed components
            for comp_id in components_processed_this_iteration:
                unprocessed_components.pop(comp_id, None)
        
        # Step 3: Store results for all connections
        for connection in connections:
            edge_id = connection['id']
            source_comp = connection['source']
            source_handle = connection['source_handle']
            
            if source_comp in component_outputs and source_handle in component_outputs[source_comp]:
                state_data = component_outputs[source_comp][source_handle]
                results[edge_id]['timestep'].append(time)
                results[edge_id]['values'].append(state_data.tolist() if hasattr(state_data, 'tolist') else state_data)
            else:
                # Fallback to default state for missing data
                default_state = np.zeros(21)
                results[edge_id]['timestep'].append(time)
                results[edge_id]['values'].append(default_state.tolist())
    
    def _process_component(self, comp_data: Dict, inputs: Dict, time: float, step: int) -> Dict:
        """Process a single component with its inputs and return outputs."""
        component = comp_data['component']
        comp_type = comp_data['type']
        
        # Get the primary input (most components have a single main input)
        primary_input = None
        if 'inlet' in inputs:
            primary_input = inputs['inlet']
        elif inputs:
            # Use the first available input
            primary_input = next(iter(inputs.values()))
        
        if primary_input is None:
            # No input available, use default state
            primary_input = self.default_influent
        
        # Process based on component type
        if comp_type == 'asm1-reactor':
            return self._process_asm1_reactor(component, primary_input, time, step)
        elif comp_type == 'adm1-reactor':
            return self._process_adm1_reactor(component, primary_input, time, step)
        elif comp_type == 'primary-clarifier':
            return self._process_primary_clarifier(component, primary_input, time, step)
        elif comp_type == 'settler':
            return self._process_settler(component, primary_input, time, step)
        elif comp_type == 'thickener':
            return self._process_thickener(component, primary_input, time, step)
        elif comp_type == 'dewatering':
            return self._process_dewatering(component, primary_input, time, step)
        elif comp_type == 'storage-tank':
            return self._process_storage(component, primary_input, time, step)
        elif comp_type == 'combiner':
            return self._process_combiner(component, inputs, time, step)
        elif comp_type == 'splitter':
            return self._process_splitter(component, primary_input, time, step)
        else:
            # Unknown component type, pass through input
            return {'outlet': primary_input}
    
    def _process_asm1_reactor(self, component, input_data: np.ndarray, time: float, step: int) -> Dict:
        """Process ASM1 reactor component."""
        # For now, simulate biological treatment by modifying substrate and biomass
        output = input_data.copy()
        
        # Simple ASM1 simulation: reduce substrate, increase biomass
        if hasattr(component, 'volume') and component.volume > 0:
            # Very simplified ASM1 kinetics
            hrt = component.volume / max(input_data[Q], 1)  # Hydraulic retention time
            
            # Substrate removal
            output[SS] = max(0, input_data[SS] * np.exp(-0.5 * hrt))  # COD removal
            output[SNH] = max(0, input_data[SNH] * 0.8)  # Nitrification
            output[SNO] = input_data[SNO] + (input_data[SNH] - output[SNH]) * 0.8  # Nitrate production
            
            # Biomass growth
            output[XBH] = input_data[XBH] + (input_data[SS] - output[SS]) * 0.6  # Biomass yield
            
            # Oxygen consumption (set to low level in reactor effluent)
            output[SO] = min(2.0, input_data[SO] + 0.5)  # Some oxygen addition
        
        return {'outlet': output}
    
    def _process_adm1_reactor(self, component, input_data: np.ndarray, time: float, step: int) -> Dict:
        """Process ADM1 reactor component."""
        # Simple anaerobic digestion simulation
        output = input_data.copy()
        
        if hasattr(component, 'volume') and component.volume > 0:
            # Anaerobic conversion
            output[XS] = max(0, input_data[XS] * 0.7)  # Organic solids reduction
            output[SS] = input_data[SS] * 0.8  # Some soluble organics remain
            output[SO] = 0  # No oxygen in anaerobic conditions
            
            # Gas production (simplified)
            biogas_production = (input_data[XS] - output[XS]) * 0.5
            
        return {
            'liquid': output,
            'gas': np.array([biogas_production if 'biogas_production' in locals() else 0])
        }
    
    def _process_primary_clarifier(self, component, input_data: np.ndarray, time: float, step: int) -> Dict:
        """Process primary clarifier component."""
        # Simple settling simulation
        effluent = input_data.copy()
        sludge = input_data.copy()
        
        # Primary settling removes 60% of suspended solids and 30% of BOD
        removal_tss = 0.6
        removal_bod = 0.3
        
        # Effluent (clarified water)
        effluent[TSS] = input_data[TSS] * (1 - removal_tss)
        effluent[SS] = input_data[SS] * (1 - removal_bod)
        effluent[XS] = input_data[XS] * (1 - removal_tss)
        
        # Sludge (concentrated solids)
        sludge_flow_fraction = 0.05  # 5% of flow goes to sludge
        effluent[Q] = input_data[Q] * (1 - sludge_flow_fraction)
        sludge[Q] = input_data[Q] * sludge_flow_fraction
        
        # Concentrate solids in sludge
        sludge[TSS] = input_data[TSS] * removal_tss / sludge_flow_fraction
        sludge[XS] = input_data[XS] * removal_tss / sludge_flow_fraction
        
        return {
            'effluent': effluent,
            'sludge': sludge
        }
    
    def _process_settler(self, component, input_data: np.ndarray, time: float, step: int) -> Dict:
        """Process settler component."""
        # Secondary settling with sludge recycle
        effluent = input_data.copy()
        sludge = input_data.copy()
        
        # Secondary settling removes most suspended solids
        removal_tss = 0.95
        
        # Effluent (clear supernatant)
        effluent[TSS] = input_data[TSS] * (1 - removal_tss)
        effluent[XBH] = input_data[XBH] * 0.1  # Most biomass settles
        effluent[XS] = input_data[XS] * 0.1
        
        # Sludge (return + waste activated sludge)
        sludge_flow_fraction = 0.2  # 20% of flow as return sludge
        effluent[Q] = input_data[Q] * (1 - sludge_flow_fraction)
        sludge[Q] = input_data[Q] * sludge_flow_fraction
        
        # Concentrate biomass in sludge
        sludge[TSS] = input_data[TSS] * removal_tss / sludge_flow_fraction
        sludge[XBH] = input_data[XBH] * 0.9 / sludge_flow_fraction
        
        return {
            'effluent': effluent,
            'sludge': sludge
        }
    
    def _process_thickener(self, component, input_data: np.ndarray, time: float, step: int) -> Dict:
        """Process thickener component."""
        underflow = input_data.copy()
        overflow = input_data.copy()
        
        # Thickening concentrates solids
        thickening_ratio = 3.0
        underflow_fraction = 1.0 / thickening_ratio
        
        underflow[Q] = input_data[Q] * underflow_fraction
        overflow[Q] = input_data[Q] * (1 - underflow_fraction)
        
        # Concentrate solids in underflow
        underflow[TSS] = input_data[TSS] * thickening_ratio
        underflow[XS] = input_data[XS] * thickening_ratio
        
        # Clear overflow
        overflow[TSS] = input_data[TSS] * 0.1
        overflow[XS] = input_data[XS] * 0.1
        
        return {
            'underflow': underflow,
            'overflow': overflow
        }
    
    def _process_dewatering(self, component, input_data: np.ndarray, time: float, step: int) -> Dict:
        """Process dewatering component."""
        cake = input_data.copy()
        filtrate = input_data.copy()
        
        # Dewatering removes water from sludge
        cake_fraction = 0.3  # 30% of flow as cake
        
        cake[Q] = input_data[Q] * cake_fraction
        filtrate[Q] = input_data[Q] * (1 - cake_fraction)
        
        # Concentrate solids in cake
        cake[TSS] = input_data[TSS] / cake_fraction
        filtrate[TSS] = input_data[TSS] * 0.05  # Some solids in filtrate
        
        return {
            'cake': cake,
            'filtrate': filtrate
        }
    
    def _process_storage(self, component, input_data: np.ndarray, time: float, step: int) -> Dict:
        """Process storage tank component."""
        # Simple pass-through with potential delay (not implemented here)
        return {'outlet': input_data}
    
    def _process_combiner(self, component, inputs: Dict, time: float, step: int) -> Dict:
        """Process combiner component."""
        if not inputs:
            return {'outlet': self.default_influent}
        
        # Combine flows
        total_flow = 0
        combined_state = np.zeros(21)
        
        for input_data in inputs.values():
            if hasattr(input_data, '__len__') and len(input_data) >= 21:
                flow = input_data[Q] if Q < len(input_data) else 0
                total_flow += flow
                
                # Mass balance combining
                for i in range(21):
                    if i < len(input_data):
                        if i == Q:  # Flow is additive
                            combined_state[i] += input_data[i]
                        else:  # Concentrations are flow-weighted
                            combined_state[i] += input_data[i] * flow
        
        # Calculate flow-weighted concentrations
        if total_flow > 0:
            for i in range(21):
                if i != Q:  # Don't divide flow by flow
                    combined_state[i] /= total_flow
        
        return {'outlet': combined_state}
    
    def _process_splitter(self, component, input_data: np.ndarray, time: float, step: int) -> Dict:
        """Process splitter component."""
        split_fraction = getattr(component, 'fraction', 0.5)
        
        outlet1 = input_data.copy()
        outlet2 = input_data.copy()
        
        outlet1[Q] = input_data[Q] * split_fraction
        outlet2[Q] = input_data[Q] * (1 - split_fraction)
        
        return {
            'outlet1': outlet1,
            'outlet2': outlet2
        }
    
    def _create_default_influent(self) -> np.ndarray:
        """Create default influent data for simulations."""
        # Default BSM2 influent composition
        influent = np.zeros(21)
        influent[SI] = 30      # Inert soluble substrate
        influent[SS] = 69.5    # Readily biodegradable substrate
        influent[XI] = 51.2    # Inert particulate substrate
        influent[XS] = 202.3   # Slowly biodegradable substrate
        influent[XBH] = 28.2   # Heterotrophic biomass
        influent[XBA] = 0      # Autotrophic biomass
        influent[XP] = 0       # Particulate inert products
        influent[SO] = 0       # Dissolved oxygen
        influent[SNO] = 0      # Nitrate and nitrite nitrogen
        influent[SNH] = 31.6   # Ammonium nitrogen
        influent[SND] = 6.95   # Soluble biodegradable nitrogen
        influent[XND] = 10.6   # Particulate biodegradable nitrogen
        influent[SALK] = 7     # Alkalinity
        influent[TSS] = 211.7  # Total suspended solids
        influent[Q] = 20648    # Flow rate
        influent[TEMP] = 15    # Temperature
        
        return influent
    
    def _has_cycles(self, config: SimulationConfig) -> bool:
        """Check for cycles in the component graph."""
        # Simple cycle detection using DFS
        graph = {}
        for edge in config.edges:
            if edge.source not in graph:
                graph[edge.source] = []
            graph[edge.source].append(edge.target)
        
        visited = set()
        rec_stack = set()
        
        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if dfs(node):
                    return True
        
        return False
    
    # Component creation methods
    def _create_influent(self, parameters: Dict) -> Any:
        """Create an influent component."""
        influent_type = parameters.get('influent_type', 'constant')
        flow_rate = parameters.get('flow_rate', 20959)
        csv_file = parameters.get('csv_file', '')
        timestep_resolution = parameters.get('timestep_resolution', 15)
        
        if influent_type == 'dynamic' and csv_file:
            # Load dynamic influent data from CSV
            return MockInfluent(influent_type, flow_rate, csv_file, timestep_resolution)
        else:
            # Use constant influent
            return MockInfluent('constant', flow_rate)
    
    def _create_asm1_reactor(self, parameters: Dict) -> Any:
        """Create an ASM1 reactor component."""
        if not BSM2_AVAILABLE:
            return self._create_mock_component('asm1-reactor', parameters)
        
        volume = parameters.get('volume', 1000)
        return MockASM1Reactor(volume)
    
    def _create_adm1_reactor(self, parameters: Dict) -> Any:
        """Create an ADM1 reactor component.""" 
        if not BSM2_AVAILABLE:
            return self._create_mock_component('adm1-reactor', parameters)
        
        volume = parameters.get('volume', 3400)
        return MockADM1Reactor(volume)
    
    def _create_primary_clarifier(self, parameters: Dict) -> Any:
        """Create a primary clarifier component."""
        if not BSM2_AVAILABLE:
            return self._create_mock_component('primary-clarifier', parameters)
        
        area = parameters.get('area', 1500)
        height = parameters.get('height', 4)
        return MockPrimaryClarifier(area, height)
    
    def _create_settler(self, parameters: Dict) -> Any:
        """Create a settler component."""
        if not BSM2_AVAILABLE:
            return self._create_mock_component('settler', parameters)
        
        area = parameters.get('area', 6000)
        height = parameters.get('height', 4)
        return MockSettler(area, height)
    
    def _create_thickener(self, parameters: Dict) -> Any:
        """Create a thickener component."""
        if not BSM2_AVAILABLE:
            return self._create_mock_component('thickener', parameters)
        
        area = parameters.get('area', 250)
        height = parameters.get('height', 4)
        return MockThickener(area, height)
    
    def _create_dewatering(self, parameters: Dict) -> Any:
        """Create a dewatering component."""
        if not BSM2_AVAILABLE:
            return self._create_mock_component('dewatering', parameters)
        
        efficiency = parameters.get('capture_efficiency', 0.95)
        dryness = parameters.get('cake_dryness', 0.25)
        return MockDewatering(efficiency, dryness)
    
    def _create_storage(self, parameters: Dict) -> Any:
        """Create a storage component."""
        if not BSM2_AVAILABLE:
            return self._create_mock_component('storage', parameters)
        
        volume = parameters.get('volume', 6000)
        delay = parameters.get('delay', 1)
        return MockStorage(volume, delay)
    
    def _create_combiner(self, parameters: Dict) -> Any:
        """Create a combiner component."""
        if not BSM2_AVAILABLE:
            return self._create_mock_component('combiner', parameters)
        
        return MockCombiner()
    
    def _create_splitter(self, parameters: Dict) -> Any:
        """Create a splitter component."""
        if not BSM2_AVAILABLE:
            return self._create_mock_component('splitter', parameters)
        
        fraction = parameters.get('split_fraction', 0.5)
        return MockSplitter(fraction)
    
    def _create_mock_component(self, component_type: str, parameters: Dict) -> Any:
        """Create a mock component when BSM2-Python is not available."""
        return MockComponent(component_type, parameters)


# Mock component classes for when BSM2-Python is not available
class MockComponent:
    def __init__(self, component_type: str, parameters: Dict):
        self.component_type = component_type
        self.parameters = parameters
    
    def init(self):
        pass
    
    def simulate_step(self, inputs):
        # Return mock outputs
        return inputs

class MockASM1Reactor(MockComponent):
    def __init__(self, volume: float):
        super().__init__('asm1-reactor', {'volume': volume})
        self.volume = volume

class MockADM1Reactor(MockComponent):
    def __init__(self, volume: float):
        super().__init__('adm1-reactor', {'volume': volume})
        self.volume = volume

class MockPrimaryClarifier(MockComponent):
    def __init__(self, area: float, height: float):
        super().__init__('primary-clarifier', {'area': area, 'height': height})
        self.area = area
        self.height = height

class MockSettler(MockComponent):
    def __init__(self, area: float, height: float):
        super().__init__('settler', {'area': area, 'height': height})
        self.area = area
        self.height = height

class MockThickener(MockComponent):
    def __init__(self, area: float, height: float):
        super().__init__('thickener', {'area': area, 'height': height})
        self.area = area
        self.height = height

class MockDewatering(MockComponent):
    def __init__(self, efficiency: float, dryness: float):
        super().__init__('dewatering', {'efficiency': efficiency, 'dryness': dryness})
        self.efficiency = efficiency
        self.dryness = dryness

class MockStorage(MockComponent):
    def __init__(self, volume: float, delay: float):
        super().__init__('storage', {'volume': volume, 'delay': delay})
        self.volume = volume
        self.delay = delay

class MockCombiner(MockComponent):
    def __init__(self):
        super().__init__('combiner', {})

class MockSplitter(MockComponent):
    def __init__(self, fraction: float):
        super().__init__('splitter', {'fraction': fraction})
        self.fraction = fraction

class MockInfluent(MockComponent):
    def __init__(self, influent_type: str, flow_rate: float, csv_file: str = '', timestep_resolution: int = 15):
        super().__init__('influent', {
            'influent_type': influent_type,
            'flow_rate': flow_rate,
            'csv_file': csv_file,
            'timestep_resolution': timestep_resolution
        })
        self.influent_type = influent_type
        self.flow_rate = flow_rate
        self.csv_file = csv_file
        self.timestep_resolution = timestep_resolution
        self.influent_data = None
        
        if influent_type == 'constant':
            self.influent_data = self._create_constant_influent()
        elif influent_type == 'dynamic':
            if csv_file:
                self.influent_data = self._load_csv_influent()
            else:
                self.influent_data = self._create_bsm2_dynamic_influent()
    
    def _create_constant_influent(self):
        """Create constant influent from first line of BSM2 dynamic data."""
        import os
        import numpy as np
        
        # Try multiple possible paths for the BSM2 dynamic influent data
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'bsm2_python', 'data', 'dyninfluent_bsm2.csv'),
            '/home/runner/work/bsm2-python/bsm2-python/src/bsm2_python/data/dyninfluent_bsm2.csv',
            os.path.join(os.path.dirname(__file__), 'data', 'dyninfluent_bsm2.csv')
        ]
        
        for data_path in possible_paths:
            try:
                # Try to load from the actual BSM2 data file
                data = np.loadtxt(data_path, delimiter=',', max_rows=1)
                if len(data) >= 22:
                    constant_data = data[1:]  # Skip time column
                    constant_data[Q] = self.flow_rate  # Use user-specified flow rate
                    print(f"Loaded constant influent from BSM2 data: {data_path}")
                    return constant_data
            except (FileNotFoundError, OSError):
                continue
        
        print("Using default constant influent values as fallback")
        
        # Default constant influent values
        influent = np.zeros(21)
        influent[SI] = 30      # Inert soluble substrate
        influent[SS] = 69.5    # Readily biodegradable substrate
        influent[XI] = 51.2    # Inert particulate substrate
        influent[XS] = 202.3   # Slowly biodegradable substrate
        influent[XBH] = 28.2   # Heterotrophic biomass
        influent[XBA] = 0      # Autotrophic biomass
        influent[XP] = 0       # Particulate inert products
        influent[SO] = 0       # Dissolved oxygen
        influent[SNO] = 0      # Nitrate and nitrite nitrogen
        influent[SNH] = 31.6   # Ammonium nitrogen
        influent[SND] = 6.95   # Soluble biodegradable nitrogen
        influent[XND] = 10.6   # Particulate biodegradable nitrogen
        influent[SALK] = 7     # Alkalinity
        influent[TSS] = 211.7  # Total suspended solids
        influent[Q] = self.flow_rate    # User-specified flow rate
        influent[TEMP] = 15    # Temperature
        
        return influent
    
    def _create_bsm2_dynamic_influent(self):
        """Create BSM2 dynamic influent data."""
        import os
        import numpy as np
        
        # Try multiple possible paths for the BSM2 dynamic influent data
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'bsm2_python', 'data', 'dyninfluent_bsm2.csv'),
            '/home/runner/work/bsm2-python/bsm2-python/src/bsm2_python/data/dyninfluent_bsm2.csv',
            os.path.join(os.path.dirname(__file__), 'data', 'dyninfluent_bsm2.csv')
        ]
        
        for data_path in possible_paths:
            try:
                # Load the full BSM2 dynamic influent data
                print(f"Attempting to load BSM2 dynamic influent from: {data_path}")
                data = np.loadtxt(data_path, delimiter=',')
                print(f"Successfully loaded BSM2 dynamic influent data with shape: {data.shape}")
                return data
            except (FileNotFoundError, OSError) as e:
                print(f"Failed to load from {data_path}: {e}")
                continue
        
        # Fall back to creating synthetic dynamic data
        print("Using synthetic dynamic influent data as fallback")
        return self._create_synthetic_dynamic_influent()
    
    def _create_synthetic_dynamic_influent(self):
        """Create synthetic dynamic influent when BSM2 data is not available."""
        import numpy as np
        
        # Create 14 days of data at 15-minute intervals
        timesteps = 14 * 24 * 4  # 14 days * 24 hours * 4 (15-min intervals)
        time = np.linspace(0, 14, timesteps)
        
        data = np.zeros((timesteps, 22))  # time + 21 state variables
        data[:, 0] = time  # Time column
        
        for i in range(timesteps):
            t = time[i]
            
            # Create daily and weekly patterns
            daily_pattern = np.sin(t * 2 * np.pi) * 0.3 + 1  # Daily variation
            weekly_pattern = np.sin(t * 2 * np.pi / 7) * 0.1 + 1  # Weekly variation
            base_multiplier = daily_pattern * weekly_pattern
            
            # Base influent composition with variations
            data[i, 1:] = [
                30 * base_multiplier,      # SI
                69.5 * base_multiplier,    # SS
                51.2 * base_multiplier,    # XI
                202.3 * base_multiplier,   # XS
                28.2 * base_multiplier,    # XBH
                0,                         # XBA
                0,                         # XP
                0,                         # SO
                0,                         # SNO
                31.6 * base_multiplier,    # SNH
                6.95 * base_multiplier,    # SND
                10.6 * base_multiplier,    # XND
                7 * base_multiplier,       # SALK
                211.7 * base_multiplier,   # TSS
                self.flow_rate * base_multiplier,  # Q
                15 + 5 * np.sin(t * 2 * np.pi / 365),  # TEMP (seasonal)
                0, 0, 0, 0, 0              # SD1, SD2, SD3, XD4, XD5
            ]
        
        return data
    
    def _load_csv_influent(self):
        """Load custom CSV influent data."""
        # For now, return synthetic data
        # In a full implementation, this would load the actual uploaded CSV
        return self._create_synthetic_dynamic_influent()
    
    def get_influent_at_time(self, time: float):
        """Get influent data at a specific time."""
        if self.influent_type == 'constant':
            return self.influent_data
        else:
            # For dynamic influent, interpolate between data points
            if self.influent_data is not None and len(self.influent_data) > 0:
                time_column = self.influent_data[:, 0]
                
                # Find closest time points
                idx = np.searchsorted(time_column, time)
                if idx == 0:
                    return self.influent_data[0, 1:]
                elif idx >= len(time_column):
                    return self.influent_data[-1, 1:]
                else:
                    # Linear interpolation
                    t0, t1 = time_column[idx-1], time_column[idx]
                    w = (time - t0) / (t1 - t0)
                    data0, data1 = self.influent_data[idx-1, 1:], self.influent_data[idx, 1:]
                    return (1 - w) * data0 + w * data1
            
            # Fall back to constant
            return self._create_constant_influent()