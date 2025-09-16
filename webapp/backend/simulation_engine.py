"""
Simulation engine for BSM2 wastewater treatment plant simulations.

This module implements Kahn's algorithm for topological sorting with loop detection
and creates a simulation execution order for the connected components.
Properly integrates with real BSM2-Python modules.
"""

import asyncio
import numpy as np
import json
import pandas as pd
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

# Import BSM2 initialization modules
import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
import bsm2_python.bsm2.init.adm1init_bsm2 as adm1init
import bsm2_python.bsm2.init.primclarinit_bsm2 as primclarinit
import bsm2_python.bsm2.init.settler1dinit_bsm2 as settler1dinit
import bsm2_python.bsm2.init.thickenerinit_bsm2 as thickenerinit
import bsm2_python.bsm2.init.dewateringinit_bsm2 as dewateringinit
import bsm2_python.bsm2.init.storageinit_bsm2 as storageinit
import bsm2_python.bsm2.init.reginit_bsm2 as reginit

from models import SimulationConfig, ComponentType, SimulationResult


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
        """Setup influent data based on configuration using BSM2 format"""
        if self.config.influent.type == "constant":
            # Use constant values or default BSM2 constant influent
            if self.config.influent.constant_values:
                self.influent_data = np.array([self.config.influent.constant_values])
            else:
                # Load default constant influent from BSM2 (first line of dynamic data)
                try:
                    dyn_file = repo_root / "src" / "bsm2_python" / "data" / "dyninfluent_bsm2.csv"
                    df = pd.read_csv(dyn_file)
                    # Take only the first row and remove time column
                    const_data = df.iloc[0, 1:].values  # Skip time column
                    self.influent_data = np.array([const_data])
                except Exception as e:
                    print(f"Warning: Could not load BSM2 influent data: {e}")
                    # Fallback to BSM2 constant influent values
                    # Based on BSM2 documentation: SI, SS, XI, XS, XBH, XBA, XP, SO, SNO, SNH, SND, XND, SALK, TSS, Q, TEMP, SD1, SD2, SD3, XD4, XD5
                    const_influent = np.array([
                        30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0
                    ])
                    self.influent_data = np.array([const_influent])
        else:
            # Dynamic influent
            if self.config.influent.file_data:
                # User provided custom file data
                self.influent_data = np.array(self.config.influent.file_data)
            else:
                # Load default dynamic influent from BSM2
                try:
                    dyn_file = repo_root / "src" / "bsm2_python" / "data" / "dyninfluent_bsm2.csv"
                    df = pd.read_csv(dyn_file)
                    self.influent_data = df.values  # Includes time column
                except Exception as e:
                    print(f"Warning: Could not load BSM2 dynamic influent data: {e}")
                    # Fallback to constant data
                    const_influent = np.array([
                        30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0
                    ])
                    self.influent_data = np.array([const_influent])
        
        print(f"Influent data shape: {self.influent_data.shape}")
        print(f"Influent type: {self.config.influent.type}")
    
    def _initialize_components(self):
        """Initialize all components based on the configuration using _create_copies approach"""
        for node in self.config.nodes:
            component = self._create_component(node)
            if component:
                self.components[node.id] = {
                    'component': component,
                    'config': node,
                    'inputs': {},
                    'outputs': {},
                    'time_series': defaultdict(list),
                    'current_state': None  # Will store current state for components that need it
                }
                
                # Initialize current state for stateful components (equivalent to _create_copies)
                if hasattr(component, 'y0'):
                    self.components[node.id]['current_state'] = component.y0.copy()
                    
        print(f"Initialized {len(self.components)} components")
    
    def _create_component(self, node):
        """Create a BSM2 component based on node configuration using proper BSM2 initialization"""
        params = node.parameters
        
        if node.type == ComponentType.ASM1_REACTOR:
            # Use proper BSM2 ASM1 initialization
            kla = params.get('kla', reginit.KLA3)  # Default from BSM2
            volume = params.get('volume', asm1init.VOL3)  # Default from BSM2
            y_0 = params.get('y_0', asm1init.YINIT3.copy())  # Initial conditions
            asm1par = params.get('asm1par', asm1init.PAR3.copy())  # ASM1 parameters
            carb = params.get('carb', reginit.CARB3)  # Carbon addition
            csourceconc = params.get('csourceconc', reginit.CARBONSOURCECONC)
            tempmodel = params.get('tempmodel', False)
            activate = params.get('activate', True)
            
            # Ensure arrays are properly copied to avoid modifications
            if isinstance(y_0, list):
                y_0 = np.array(y_0)
            if isinstance(asm1par, list):
                asm1par = np.array(asm1par)
                
            return ASM1Reactor(
                kla=kla,
                volume=volume,
                y0=y_0.copy(),
                asm1par=asm1par.copy(),
                carb=carb,
                csourceconc=csourceconc,
                tempmodel=tempmodel,
                activate=activate
            )
        
        elif node.type == ComponentType.ADM1_REACTOR:
            # Use proper BSM2 ADM1 initialization
            volume = params.get('volume', adm1init.VOL_AD)
            y_0 = params.get('y_0', adm1init.YINIT_AD.copy())
            adm1par = params.get('adm1par', adm1init.PAR_AD.copy())
            tempmodel = params.get('tempmodel', False)
            
            if isinstance(y_0, list):
                y_0 = np.array(y_0)
            if isinstance(adm1par, list):
                adm1par = np.array(adm1par)
                
            return ADM1Reactor(
                volume=volume,
                y0=y_0.copy(),
                adm1par=adm1par.copy(),
                tempmodel=tempmodel
            )
        
        elif node.type == ComponentType.PRIMARY_CLARIFIER:
            # Use proper BSM2 Primary Clarifier initialization
            vol_p = params.get('vol_p', primclarinit.VOL_P)
            area_p = params.get('area_p', primclarinit.AREA_P)
            y_0 = params.get('y_0', primclarinit.YINIT_P.copy())
            
            if isinstance(y_0, list):
                y_0 = np.array(y_0)
                
            return PrimaryClarifier(
                vol_p=vol_p,
                area_p=area_p,
                y0=y_0.copy()
            )
        
        elif node.type == ComponentType.SETTLER:
            # Use proper BSM2 Settler initialization  
            vol_s = params.get('vol_s', settler1dinit.VOL_S)
            area_s = params.get('area_s', settler1dinit.AREA_S)
            height_s = params.get('height_s', settler1dinit.HEIGHT_S)
            y_0 = params.get('y_0', settler1dinit.YINIT_S.copy())
            par_s = params.get('par_s', settler1dinit.PAR_S.copy())
            tempmodel = params.get('tempmodel', False)
            
            if isinstance(y_0, list):
                y_0 = np.array(y_0)
            if isinstance(par_s, list):
                par_s = np.array(par_s)
                
            return Settler(
                vol_s=vol_s,
                area_s=area_s,
                height_s=height_s,
                y0=y_0.copy(),
                par_s=par_s.copy(),
                tempmodel=tempmodel
            )
        
        elif node.type == ComponentType.THICKENER:
            # Use proper BSM2 Thickener initialization - only needs THICKENERPAR
            component = Thickener(thickenerinit.THICKENERPAR)
            time_series = {
                'time': [],
                'thickened_sludge': [],
                'supernatant': []
            }
        
        elif node.type == ComponentType.DEWATERING:
            # Use proper BSM2 Dewatering initialization
            dry_solids = params.get('dry_solids', dewateringinit.DRYSOLIDS)
            component = Dewatering(dry_solids=dry_solids)
            time_series = {
                'time': [],
                'solid_stream': [],
                'liquid_stream': []
            }
        
        elif node.type == ComponentType.STORAGE:
            # Use proper BSM2 Storage initialization
            vol_st = params.get('vol_st', storageinit.VOL_ST)
            area_st = params.get('area_st', storageinit.AREA_ST)
            height_st = params.get('height_st', storageinit.HEIGHT_ST)
            y_0 = params.get('y_0', storageinit.YINIT_ST.copy())
            
            if isinstance(y_0, list):
                y_0 = np.array(y_0)
                
            return Storage(
                vol_st=vol_st,
                area_st=area_st,
                height_st=height_st,
                y0=y_0.copy()
            )
        
        elif node.type == ComponentType.SPLITTER:
            # Use BSM2 Splitter - check if it needs specific initialization
            sp_type = params.get('sp_type', 1)  # Default splitter type
            return Splitter(sp_type=sp_type)
        
        elif node.type == ComponentType.COMBINER:
            # Use BSM2 Combiner
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
                    print(f"Set influent flow for {node_id}: shape {influent.shape}")
            else:
                # Handle influent nodes that might not be in components
                for node in self.config.nodes:
                    if node.id == node_id and node.type == ComponentType.INFLUENT:
                        flows[node_id] = {"effluent": influent}
                        print(f"Set influent flow for {node_id}: shape {influent.shape}")
                        break
        
        # Execute components in order
        for node_id in self.execution_order:
            if node_id not in self.components:
                continue
                
            component_data = self.components[node_id]
            component = component_data['component']
            
            print(f"Executing {node_id}: {type(component).__name__ if component else 'Influent'}")
            
            if component is None:  # Skip influent nodes
                continue
            
            # Get inputs for this component
            inputs = self._get_component_inputs(node_id, flows)
            
            # Execute component
            if inputs:
                outputs = self._execute_component(component, inputs, dt, t)
                flows[node_id] = outputs
                
                # Store time series data (this implements the self.*_all equivalent)
                component_data['time_series']['time'].append(t)
                for output_name, output_data in outputs.items():
                    component_data['time_series'][output_name].append(output_data.copy() if isinstance(output_data, np.ndarray) else output_data)
                print(f"  Stored outputs: {list(outputs.keys())}")
            else:
                print(f"Warning: No inputs found for component {node_id}")
    
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
                    print(f"  Input for {node_id}: {target_handle} from {source_id}.{source_handle}")
                else:
                    print(f"  Warning: Missing input for {node_id}: {target_handle} from {source_id}.{source_handle}")
        
        return inputs
    
    def _execute_component(self, component, inputs, dt, current_time):
        """Execute a single component with its inputs using proper BSM2 methods"""
        outputs = {}
        
        # Get the main input (most components have one main input)
        main_input = None
        if inputs:
            main_input = list(inputs.values())[0]
            
        try:
            # Execute based on component type using BSM2 output methods
            if isinstance(component, ASM1Reactor):
                # ASM1 Reactor: output(timestep, step, y_in)
                result = component.output(dt, current_time, main_input)
                outputs = {"effluent": result}
                
            elif isinstance(component, ADM1Reactor):
                # ADM1 Reactor: output(timestep, step, y_in)
                result = component.output(dt, current_time, main_input)
                # ADM1 typically has liquid and gas outputs
                if isinstance(result, tuple) and len(result) == 2:
                    outputs = {"effluent": result[0], "biogas": result[1]}
                else:
                    outputs = {"effluent": result, "biogas": np.zeros_like(result)}
                    
            elif isinstance(component, PrimaryClarifier):
                # Primary Clarifier: output(timestep, step, y_in)
                result = component.output(dt, current_time, main_input)
                if isinstance(result, tuple) and len(result) == 2:
                    outputs = {"effluent": result[0], "sludge": result[1]}
                else:
                    outputs = {"effluent": result}
                    
            elif isinstance(component, Settler):
                # Settler: output(timestep, step, y_in)
                result = component.output(dt, current_time, main_input)
                if isinstance(result, tuple) and len(result) == 2:
                    outputs = {"effluent": result[0], "sludge": result[1]}
                else:
                    outputs = {"effluent": result}
                    
            elif isinstance(component, Thickener):
                # Thickener: output(timestep, step, y_in)
                result = component.output(dt, current_time, main_input)
                if isinstance(result, tuple) and len(result) == 2:
                    outputs = {"thickened_sludge": result[0], "filtrate": result[1]}
                else:
                    outputs = {"thickened_sludge": result}
                    
            elif isinstance(component, Dewatering):
                # Dewatering: output(timestep, step, y_in)
                result = component.output(dt, current_time, main_input)
                if isinstance(result, tuple) and len(result) == 2:
                    outputs = {"dewatered_sludge": result[0], "filtrate": result[1]}
                else:
                    outputs = {"dewatered_sludge": result}
                    
            elif isinstance(component, Storage):
                # Storage: output(timestep, step, y_in)
                result = component.output(dt, current_time, main_input)
                outputs = {"effluent": result}
                
            elif isinstance(component, Splitter):
                # Splitter: split(y_in) - may need special handling
                if hasattr(component, 'split'):
                    result = component.split(main_input)
                    if isinstance(result, tuple) and len(result) == 2:
                        outputs = {"output1": result[0], "output2": result[1]}
                    else:
                        outputs = {"output1": result, "output2": result}
                else:
                    # Fallback: pass through
                    outputs = {"output1": main_input, "output2": main_input}
                    
            elif isinstance(component, Combiner):
                # Combiner: combine multiple inputs
                if len(inputs) >= 2:
                    input_values = list(inputs.values())
                    if hasattr(component, 'combine'):
                        result = component.combine(input_values[0], input_values[1])
                    else:
                        # Simple combination (flow addition)
                        result = input_values[0].copy()
                        result[14] += input_values[1][14]  # Add flows (Q is at index 14)
                        # Weighted average for concentrations
                        total_q = result[14]
                        if total_q > 0:
                            for i in range(14):  # For concentration components
                                result[i] = (input_values[0][i] * input_values[0][14] + 
                                           input_values[1][i] * input_values[1][14]) / total_q
                    outputs = {"combined": result}
                else:
                    # Single input - pass through
                    outputs = {"combined": main_input}
            else:
                # Unknown component type - pass through
                print(f"Warning: Unknown component type {type(component)}")
                outputs = {"effluent": main_input}
                
        except Exception as e:
            print(f"Error executing component {type(component).__name__}: {e}")
            # Return safe fallback output
            if main_input is not None:
                outputs = {"effluent": main_input.copy()}
            else:
                # Create a zero flow
                outputs = {"effluent": np.zeros(21)}  # BSM2 has 21 components
        
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
                    "component_type": component_data['config'].type.value,  # Add component type
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