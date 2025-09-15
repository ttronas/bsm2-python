"""
Debug script to analyze ADM1 inputs and identify the source of NaN issues.
"""

import json
import numpy as np
import asyncio
import logging
from pathlib import Path

from simulation_engine import SimulationEngine
from models import SimulationConfig, FlowNode, FlowEdge, SimulationSettings

# Set up detailed logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def load_bsm2_config():
    """Load BSM2 config."""
    json_path = Path("predefined_flowsheets/bsm2_ol.json")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    nodes = []
    for node_data in data['nodes']:
        node = FlowNode(
            id=node_data['id'],
            type=node_data['type'],
            position=node_data['position'],
            data=node_data['data']
        )
        nodes.append(node)
    
    edges = []
    for edge_data in data['edges']:
        edge = FlowEdge(
            id=edge_data['id'],
            source=edge_data['source'],
            target=edge_data['target'],
            sourceHandle=edge_data.get('sourceHandle'),
            targetHandle=edge_data.get('targetHandle')
        )
        edges.append(edge)
    
    settings = SimulationSettings(
        timestep=15,  # 15 minutes
        endTime=1,    # Only 1 day for debugging
        outputPath=""
    )
    
    config = SimulationConfig(
        name="BSM2 Debug",
        description="BSM2 debug test",
        nodes=nodes,
        edges=edges,
        settings=settings
    )
    
    return config

async def debug_simulation():
    """Run simulation with detailed debugging."""
    config = load_bsm2_config()
    engine = SimulationEngine()
    
    # Manually trace the execution to understand what's happening
    # Validate configuration
    engine.validate_configuration(config)
    
    # Build components
    components = {}
    influent_nodes = []
    node_map = {node.id: node for node in config.nodes}
    
    for node in config.nodes:
        if node.data.get('componentType') == 'influent':
            influent_nodes.append(node)
        else:
            component = engine.create_bsm2_component(node)
            if component:
                components[node.id] = component
    
    # Load influent data
    influent_params = influent_nodes[0].data.get('parameters', {})
    influent_data = engine.load_influent_data(influent_params)
    
    print(f"Influent data shape: {influent_data.shape}")
    print(f"First influent values: {influent_data[0] if len(influent_data.shape) > 1 else influent_data}")
    
    # Get execution order
    execution_order = engine.topological_sort(config)
    print(f"Execution order: {execution_order}")
    
    # Initialize flows with BSM2 approach
    num_components = len([n for n in config.nodes if n.data.get('componentType') != 'influent'])
    initialized_flows = engine.initialize_component_flows(
        influent_data[0] if len(influent_data.shape) > 1 else influent_data, 
        num_components
    )
    
    print(f"Initialized {len(initialized_flows)} flow copies")
    
    # Simulate first timestep with detailed tracing
    timestep_days = 15 / (24 * 60)  # 15 minutes to days
    component_outputs = {}
    
    # Get influent for first timestep
    current_influent = influent_data[0] if len(influent_data.shape) > 1 else influent_data
    print(f"Current influent: {current_influent}")
    
    # Process influent first
    for influent_node in influent_nodes:
        component_outputs[influent_node.id] = current_influent
        print(f"Set influent {influent_node.id}: {current_influent}")
    
    # Initialize other components
    flow_idx = 0
    for node_id in execution_order:
        if node_id not in [n.id for n in influent_nodes] and node_id not in component_outputs:
            if flow_idx < len(initialized_flows):
                component_outputs[node_id] = initialized_flows[f"flow_{flow_idx}"].copy()
                print(f"Initialized {node_id} with flow_{flow_idx}: {initialized_flows[f'flow_{flow_idx}']}")
                flow_idx += 1
            else:
                component_outputs[node_id] = current_influent.copy()
                print(f"Initialized {node_id} with influent copy: {current_influent}")
    
    # Process each component
    for node_id in execution_order:
        if node_id in [n.id for n in influent_nodes]:
            continue  # Already processed
            
        node = node_map[node_id]
        comp_type = node.data.get('componentType')
        component = components.get(node_id)
        
        print(f"\n--- Processing {node_id} ({comp_type}) ---")
        
        if not component:
            print(f"No component for {node_id}, skipping")
            continue
        
        # Get inputs
        inputs = engine.get_component_inputs(node_id, config, component_outputs)
        print(f"Inputs for {node_id}: {len(inputs)} inputs")
        
        for i, inp in enumerate(inputs):
            print(f"  Input {i}: shape={inp.shape}, NaN={np.any(np.isnan(inp))}, inf={np.any(np.isinf(inp))}")
            if np.any(np.isnan(inp)) or np.any(np.isinf(inp)):
                print(f"    Values: {inp}")
        
        if len(inputs) == 0:
            input_data = current_influent.copy()
            print(f"No inputs, using influent: {input_data}")
        elif len(inputs) == 1:
            input_data = inputs[0]
            print(f"Single input: {input_data}")
        else:
            # Multiple inputs - check if combiner
            if comp_type == 'combiner':
                print(f"Combiner with {len(inputs)} inputs")
                try:
                    input_data = component.output(*inputs)
                    print(f"Combiner output: {input_data}")
                    component_outputs[node_id] = input_data
                    continue
                except Exception as e:
                    print(f"Combiner failed: {e}")
                    input_data = inputs[0]
            else:
                input_data = inputs[0]
        
        # Check input validity
        if np.any(np.isnan(input_data)) or np.any(np.isinf(input_data)):
            print(f"ERROR: Invalid input data for {node_id}: {input_data}")
            return
        
        # Call component
        try:
            print(f"Calling {comp_type} output method...")
            if comp_type == 'adm1-reactor':
                print(f"ADM1 input: {input_data}")
                interface, digester, gas = component.output(timestep_days, 0, input_data, 35.0)
                output = {'liquid': interface, 'gas': gas, 'internal': digester}
                print(f"ADM1 outputs - interface: shape={interface.shape}, NaN={np.any(np.isnan(interface))}")
                print(f"               digester: shape={digester.shape}, NaN={np.any(np.isnan(digester))}")
                print(f"               gas: shape={gas.shape}, NaN={np.any(np.isnan(gas))}")
            elif comp_type == 'thickener':
                uf, of = component.output(input_data)
                output = {'output-0': uf, 'output-1': of}
                print(f"Thickener outputs - uf: {uf}, of: {of}")
            elif comp_type == 'primary-clarifier':
                uf, of, internal = component.output(timestep_days, 0, input_data)
                output = {'effluent': of, 'sludge': uf, 'internal': internal}
                print(f"Primary clarifier outputs - uf: {uf}, of: {of}")
            else:
                output = input_data  # Default
                
            component_outputs[node_id] = output
            print(f"Success: {node_id} output set")
            
        except Exception as e:
            print(f"ERROR: Component {node_id} failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # Special focus on ADM1 combiner
        if node_id == 'combiner-adm1-1':
            print(f"\n*** ADM1 COMBINER ANALYSIS ***")
            print(f"Combiner output: {output}")
            print(f"NaN check: {np.any(np.isnan(output))}")
            print(f"Inf check: {np.any(np.isinf(output))}")
            print(f"Q value: {output[14]}")  # Flow rate
            print(f"All values: {output}")

if __name__ == "__main__":
    asyncio.run(debug_simulation())