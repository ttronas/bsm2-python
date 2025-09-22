#!/usr/bin/env python3
"""
Test the new advanced JSON engine with a simple configuration.
"""
import sys
import os
import numpy as np
import json

# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Import our engine
sys.path.append(os.path.join(src_path, 'bsm2_python', 'engine'))

from engine import SimulationEngine

# Create a simple test configuration
test_config = {
    "nodes": [
        {
            "id": "influent",
            "component_type_id": "influent_static",
            "parameters": {
                "y_in_constant": [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0]
            }
        },
        {
            "id": "effluent",
            "component_type_id": "effluent",
            "parameters": {}
        }
    ],
    "edges": [
        {
            "id": "edge1",
            "source_node_id": "influent",
            "source_handle_id": "out_main",
            "target_node_id": "effluent",
            "target_handle_id": "in_main"
        }
    ]
}

try:
    print("Creating SimulationEngine with test configuration...")
    engine = SimulationEngine(test_config)
    print("✓ Engine created successfully")
    
    print("Testing simulation step...")
    engine.step_steady(0.01)
    print("✓ Step executed successfully")
    
    print("Testing edge values...")
    print(f"Edge values: {list(engine.edge_values.keys())}")
    if engine.edge_values:
        first_edge = list(engine.edge_values.keys())[0]
        print(f"First edge value: {engine.edge_values[first_edge][:5]}...")
    
    print("✓ All tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()