"""
Simulation engine for BSM2 wastewater treatment plant simulations.

This module implements Kahn's algorithm for topological sorting with loop detection
and creates a simulation execution order for the connected components.
"""

import asyncio
import numpy as np
import json
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, deque
from datetime import datetime
import sys
from pathlib import Path

# Import BSM2 components
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "src"))

from bsm2_python.bsm2.asm1_bsm2 import ASM1Reactor
from bsm2_python.bsm2.adm1_bsm2 import ADM1Reactor
from bsm2_python.bsm2.primclar_bsm2 import PrimaryClarifier
from bsm2_python.bsm2.settler1d_bsm2 import Settler
from bsm2_python.bsm2.thickener_bsm2 import Thickener
from bsm2_python.bsm2.dewatering_bsm2 import Dewatering
from bsm2_python.bsm2.storage_bsm2 import Storage
from bsm2_python.bsm2.helpers_bsm2 import Splitter, Combiner

from webapp.backend.models import SimulationConfig, ComponentType, SimulationResult


class SimulationEngine:
    """Main simulation engine for BSM2 components"""
    
    def __init__(self, config: SimulationConfig, simulation_id: str):
        self.config = config
        self.simulation_id = simulation_id
        self.status = "created"
        self.progress = 0.0
        self.current_time = 0.0
        self.components = {}
        self.execution_order = []
        self.time_series_data = {}
        self.stop_requested = False
        
        # Parse influent data
        self._setup_influent()
        
        # Initialize components
        self._initialize_components()
        
        # Build execution order using Kahn's algorithm
        self._build_execution_order()
    
    def _setup_influent(self):
        """Setup influent data based on configuration"""
        if self.config.influent.type == "constant":
            # Use constant values or default BSM2 constant influent
            if self.config.influent.constant_values:
                self.influent_data = np.array([self.config.influent.constant_values])
            else:
                # Load default constant influent from BSM2
                import pandas as pd
                const_file = repo_root / "src" / "bsm2_python" / "data" / "constinfluent_bsm2.csv"
                df = pd.read_csv(const_file)
                self.influent_data = df.values
        else:
            # Dynamic influent
            if self.config.influent.file_data:
                self.influent_data = np.array(self.config.influent.file_data)
            else:
                # Load default dynamic influent
                import pandas as pd
                dyn_file = repo_root / "src" / "bsm2_python" / "data" / "dyninfluent_bsm2.csv"
                df = pd.read_csv(dyn_file)
                self.influent_data = df.values
    
    def _initialize_components(self):
        """Initialize all components based on the configuration"""
        for node in self.config.nodes:
            component = self._create_component(node)
            if component:
                self.components[node.id] = {
                    'component': component,
                    'config': node,
                    'inputs': {},
                    'outputs': {},
                    'time_series': defaultdict(list)
                }
    
    def _create_component(self, node):
        """Create a BSM2 component based on node configuration"""
        params = node.parameters
        
        if node.type == ComponentType.ASM1_REACTOR:
            return ASM1Reactor(
                kla=params.get('kla', 240.0),
                volume=params.get('volume', 1333.0),
                activate=params.get('activate', True)
            )
        
        elif node.type == ComponentType.ADM1_REACTOR:
            return ADM1Reactor(
                volume=params.get('volume', 3400.0),
                temperature=params.get('temperature', 35.0)
            )
        
        elif node.type == ComponentType.PRIMARY_CLARIFIER:
            return PrimaryClarifier(
                area=params.get('area', 1500.0),
                height=params.get('height', 4.0)
            )
        
        elif node.type == ComponentType.SETTLER:
            return Settler(
                area=params.get('area', 6000.0),
                height=params.get('height', 4.0)
            )
        
        elif node.type == ComponentType.THICKENER:
            return Thickener(
                area=params.get('area', 250.0)
            )
        
        elif node.type == ComponentType.DEWATERING:
            return Dewatering(
                dry_solids=params.get('dry_solids', 0.25)
            )
        
        elif node.type == ComponentType.STORAGE:
            return Storage(
                volume=params.get('volume', 6000.0)
            )
        
        elif node.type == ComponentType.SPLITTER:
            return Splitter(
                split_ratio=params.get('split_ratio', 0.5)
            )
        
        elif node.type == ComponentType.COMBINER:
            return Combiner()
        
        elif node.type == ComponentType.INFLUENT:
            # Influent is handled separately
            return None
        
        return None
    
    def _build_execution_order(self):
        """Build execution order using Kahn's algorithm with loop handling"""
        # Build adjacency list and in-degree count
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        all_nodes = set()
        
        # Initialize all nodes
        for node in self.config.nodes:
            all_nodes.add(node.id)
            in_degree[node.id] = 0
        
        # Build graph from edges
        for edge in self.config.edges:
            graph[edge.source].append(edge.target)
            in_degree[edge.target] += 1
            all_nodes.add(edge.source)
            all_nodes.add(edge.target)
        
        # Kahn's algorithm
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        execution_order = []
        
        while queue:
            current = queue.popleft()
            execution_order.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles (remaining nodes with in_degree > 0)
        remaining_nodes = [node for node in all_nodes if in_degree[node] > 0]
        
        if remaining_nodes:
            # Handle cycles by processing them once per timestep
            print(f"Warning: Detected cycles involving nodes: {remaining_nodes}")
            # Add remaining nodes to execution order (will iterate only once through loops)
            execution_order.extend(remaining_nodes)
        
        self.execution_order = execution_order
        print(f"Execution order: {self.execution_order}")
    
    async def run_simulation_async(self, websocket=None):
        """Run the simulation asynchronously with progress updates"""
        self.status = "running"
        self.progress = 0.0
        
        # Time parameters
        dt = self.config.timestep  # timestep in days
        end_time = self.config.end_time  # end time in days
        time_steps = int(end_time / dt)
        
        # Initialize time series storage
        time_array = np.linspace(0, end_time, time_steps)
        
        try:
            for step, t in enumerate(time_array):
                if self.stop_requested:
                    break
                
                self.current_time = t
                self.progress = step / time_steps
                
                # Get influent for this timestep
                influent = self._get_influent_at_time(t)
                
                # Execute components in order
                await self._execute_timestep(influent, t, dt)
                
                # Send progress update via WebSocket
                if websocket and step % 10 == 0:  # Send update every 10 steps
                    await websocket.send_json({
                        "type": "progress",
                        "simulation_id": self.simulation_id,
                        "progress": self.progress,
                        "current_time": t,
                        "status": self.status
                    })
                
                # Allow other tasks to run
                await asyncio.sleep(0.001)
            
            self.status = "completed"
            self.progress = 1.0
            
            if websocket:
                await websocket.send_json({
                    "type": "completed",
                    "simulation_id": self.simulation_id,
                    "progress": 1.0,
                    "status": "completed",
                    "results": self.get_results()
                })
        
        except Exception as e:
            self.status = "error"
            if websocket:
                await websocket.send_json({
                    "type": "error",
                    "simulation_id": self.simulation_id,
                    "error": str(e)
                })
            raise
    
    def _get_influent_at_time(self, t):
        """Get influent data at specific time"""
        if self.config.influent.type == "constant":
            return self.influent_data[0]
        else:
            # Interpolate dynamic influent data
            time_col = self.influent_data[:, 0]  # Assuming first column is time
            
            if t <= time_col[0]:
                return self.influent_data[0, 1:]
            elif t >= time_col[-1]:
                return self.influent_data[-1, 1:]
            else:
                # Linear interpolation
                idx = np.searchsorted(time_col, t)
                if idx == 0:
                    return self.influent_data[0, 1:]
                
                t1, t2 = time_col[idx-1], time_col[idx]
                y1, y2 = self.influent_data[idx-1, 1:], self.influent_data[idx, 1:]
                
                alpha = (t - t1) / (t2 - t1)
                return y1 + alpha * (y2 - y1)
    
    async def _execute_timestep(self, influent, t, dt):
        """Execute one timestep of the simulation"""
        # Initialize flows dictionary
        flows = {}
        
        # Set influent for influent nodes
        for node_id in self.execution_order:
            if node_id in self.components:
                node_config = self.components[node_id]['config']
                if node_config.type == ComponentType.INFLUENT:
                    flows[node_id] = {"effluent": influent}
        
        # Execute components in order
        for node_id in self.execution_order:
            if node_id not in self.components:
                continue
                
            component_data = self.components[node_id]
            component = component_data['component']
            
            if component is None:  # Skip influent nodes
                continue
            
            # Get inputs for this component
            inputs = self._get_component_inputs(node_id, flows)
            
            # Execute component
            if inputs:
                outputs = self._execute_component(component, inputs, dt)
                flows[node_id] = outputs
                
                # Store time series data
                component_data['time_series']['time'].append(t)
                for output_name, output_data in outputs.items():
                    component_data['time_series'][output_name].append(output_data.copy() if isinstance(output_data, np.ndarray) else output_data)
    
    def _get_component_inputs(self, node_id, flows):
        """Get inputs for a component based on connected edges"""
        inputs = {}
        
        # Find edges that target this component
        for edge in self.config.edges:
            if edge.target == node_id:
                source_id = edge.source
                source_handle = edge.source_handle
                target_handle = edge.target_handle
                
                if source_id in flows and source_handle in flows[source_id]:
                    inputs[target_handle] = flows[source_id][source_handle]
        
        return inputs
    
    def _execute_component(self, component, inputs, dt):
        """Execute a single component with its inputs"""
        # This is a simplified execution - in reality, you'd need to call
        # the appropriate methods on each component type
        
        # For now, return dummy outputs
        outputs = {}
        
        # Determine outputs based on component type
        if hasattr(component, 'run'):
            # Most BSM2 components have a run method
            try:
                result = component.run(list(inputs.values())[0], dt)
                if isinstance(result, (list, tuple)):
                    if len(result) == 2:
                        outputs = {"effluent": result[0], "sludge": result[1]}
                    else:
                        outputs = {"effluent": result[0]}
                else:
                    outputs = {"effluent": result}
            except Exception as e:
                print(f"Error executing component: {e}")
                # Return dummy output
                input_data = list(inputs.values())[0]
                outputs = {"effluent": input_data}
        else:
            # Fallback for components without run method
            input_data = list(inputs.values())[0]
            outputs = {"effluent": input_data}
        
        return outputs
    
    def get_results(self):
        """Get simulation results in the required format"""
        results = {
            "simulation_id": self.simulation_id,
            "config": self.config.dict(),
            "components": [],
            "metadata": {
                "timestep": self.config.timestep,
                "end_time": self.config.end_time,
                "status": self.status,
                "progress": self.progress
            }
        }
        
        for node_id, component_data in self.components.items():
            if component_data['component'] is not None:  # Skip influent nodes
                component_result = {
                    "component_id": node_id,
                    "component_name": component_data['config'].name,
                    "outputs": {},
                    "time": component_data['time_series'].get('time', [])
                }
                
                # Convert time series data
                for output_name, data_series in component_data['time_series'].items():
                    if output_name != 'time':
                        # Convert numpy arrays to lists for JSON serialization
                        if data_series and isinstance(data_series[0], np.ndarray):
                            component_result["outputs"][output_name] = [
                                arr.tolist() for arr in data_series
                            ]
                        else:
                            component_result["outputs"][output_name] = data_series
                
                results["components"].append(component_result)
        
        return results
    
    def stop(self):
        """Stop the simulation"""
        self.stop_requested = True
        self.status = "stopped"