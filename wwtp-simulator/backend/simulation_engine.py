"""
Simulation Engine for WWTP Simulator.

This module handles the integration with BSM2-Python library,
builds simulation models from frontend configurations,
and executes simulations.
"""

import asyncio
import numpy as np
import logging
from typing import Dict, List, Callable, Optional, Any, Tuple
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
    from bsm2_python.bsm2.plantperformance import PlantPerformance
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
        self.component_registry = {
            'influent': self._create_influent,
            'asm1-reactor': self._create_asm1_reactor,
            'adm1-reactor': self._create_adm1_reactor,
            'primary-clarifier': self._create_primary_clarifier,
            'settler': self._create_settler,
            'thickener': self._create_thickener,
            'dewatering': self._create_dewatering,
            'storage-tank': self._create_storage,
            'combiner': self._create_combiner,
            'splitter': self._create_splitter,
        }
        
        # Default influent data (BSM2 standard)
        self.default_influent = self._create_default_influent()
    
    def validate_configuration(self, config: SimulationConfig) -> bool:
        """Validate a simulation configuration."""
        if not BSM2_AVAILABLE:
            raise ComponentValidationError("BSM2-Python library not available")
        
        if not config.nodes:
            raise ComponentValidationError("No components in configuration")
        
        if not config.edges:
            raise ComponentValidationError("No connections in configuration")
        
        # Validate component types
        for node in config.nodes:
            component_type = node.data.get('componentType')
            if component_type not in self.component_registry:
                raise ComponentValidationError(f"Unknown component type: {component_type}")
        
        # Validate connections
        node_ids = {node.id for node in config.nodes}
        for edge in config.edges:
            if edge.source not in node_ids:
                raise ComponentValidationError(f"Source node not found: {edge.source}")
            if edge.target not in node_ids:
                raise ComponentValidationError(f"Target node not found: {edge.target}")
        
        # Check for cycles (basic check)
        if self._has_cycles(config):
            raise ComponentValidationError("Circular connections detected")
        
        return True
    
    async def run_simulation(
        self, 
        config: SimulationConfig,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> Dict[str, Any]:
        """Run a simulation with the given configuration."""
        if not BSM2_AVAILABLE:
            raise SimulationError("BSM2-Python library not available")
        
        try:
            # Build simulation model
            components, connections = await self._build_simulation_model(config)
            
            if progress_callback:
                progress_callback(10.0)
            
            # Create time vector
            timestep_days = config.settings.timestep / (24 * 60)  # Convert minutes to days
            num_steps = int(config.settings.endTime / timestep_days)
            time_vector = np.linspace(0, config.settings.endTime, num_steps)
            
            if progress_callback:
                progress_callback(20.0)
            
            # Initialize storage for results
            results = {}
            for edge in config.edges:
                results[edge.id] = {
                    'timestep': [],
                    'values': []
                }
            
            # Run simulation
            await self._execute_simulation(
                components, connections, time_vector, results, progress_callback
            )
            
            if progress_callback:
                progress_callback(100.0)
            
            return results
            
        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise SimulationError(f"Simulation execution failed: {str(e)}")
    
    async def _build_simulation_model(
        self, config: SimulationConfig
    ) -> Tuple[Dict[str, Any], List[Dict]]:
        """Build the simulation model from configuration."""
        components = {}
        
        # Create components
        for node in config.nodes:
            component_type = node.data.get('componentType')
            parameters = node.data.get('parameters', {})
            
            if component_type in self.component_registry:
                component = self.component_registry[component_type](parameters)
                components[node.id] = {
                    'component': component,
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
        """Simulate a single timestep."""
        # For now, generate mock data for each edge
        # In a full implementation, this would:
        # 1. Calculate influent for each component based on connections
        # 2. Run each component's simulation step
        # 3. Store outputs in results
        
        for connection in connections:
            edge_id = connection['id']
            
            # Generate realistic mock data
            base_flow = 20000  # m3/d
            daily_variation = np.sin(time * 2 * np.pi) * 0.2 + 1
            flow = base_flow * daily_variation + np.random.normal(0, base_flow * 0.05)
            
            # Create full BSM2 state vector
            state = np.zeros(21)
            state[Q] = max(0, flow)  # Flow rate
            state[TSS] = 300 + np.random.normal(0, 30)  # Total suspended solids
            state[SO] = 2 + np.random.normal(0, 0.5)  # Dissolved oxygen
            state[TEMP] = 15 + np.sin(time * 2 * np.pi / 365) * 10  # Temperature
            state[SS] = 200 + np.random.normal(0, 20)  # Soluble substrate
            state[SNH] = 30 + np.random.normal(0, 5)  # Ammonium nitrogen
            state[SNO] = 10 + np.random.normal(0, 2)  # Nitrate nitrogen
            
            # Ensure non-negative values
            state = np.maximum(state, 0)
            
            # Store results
            results[edge_id]['timestep'].append(time)
            results[edge_id]['values'].append(state.tolist())
    
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
        
        # Load the first line from BSM2 dynamic influent data
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'bsm2_python', 'data', 'dyninfluent_bsm2.csv')
        
        try:
            # Try to load from the actual BSM2 data file
            data = np.loadtxt(data_path, delimiter=',', max_rows=1)
            if len(data) >= 22:
                constant_data = data[1:]  # Skip time column
                constant_data[Q] = self.flow_rate  # Use user-specified flow rate
                return constant_data
        except (FileNotFoundError, OSError):
            # Fall back to default values
            pass
        
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
        
        data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'bsm2_python', 'data', 'dyninfluent_bsm2.csv')
        
        try:
            # Load the full BSM2 dynamic influent data
            data = np.loadtxt(data_path, delimiter=',')
            return data
        except (FileNotFoundError, OSError):
            # Fall back to creating synthetic dynamic data
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