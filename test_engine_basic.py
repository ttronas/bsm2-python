#!/usr/bin/env python3
"""
Simplified test to debug imports and get the engine working.
"""
import sys
import os

# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Try a different approach - import modules individually and avoid full package loading
import numpy as np

# Import our engine modules directly
sys.path.append(os.path.join(src_path, 'bsm2_python', 'engine'))

from scheduler import schedule, build_graph
from param_resolver import resolve_value, resolve_params  
from nodes import NodeDC, EdgeRef

print("✓ Engine modules imported successfully")

# Test a simple configuration
test_config = {
    "nodes": [
        {"id": "node1", "component_type_id": "influent_static"},
        {"id": "node2", "component_type_id": "effluent"}
    ],
    "edges": [
        {
            "id": "edge1",
            "source_node_id": "node1", 
            "target_node_id": "node2",
            "source_handle_id": "out",
            "target_handle_id": "in"
        }
    ]
}

# Test the scheduler
print("Testing scheduler...")
plan = schedule(test_config)
print(f"✓ Scheduler worked: {plan}")

print("All basic tests passed!")