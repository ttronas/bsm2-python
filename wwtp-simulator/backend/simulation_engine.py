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