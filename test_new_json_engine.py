#!/usr/bin/env python3
"""
Test comparing the new advanced JSON simulation engine.
This version avoids problematic imports by focusing only on the engine.
"""

import sys
import os
import numpy as np

# Add paths
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python')
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src')

def run_json_engine_test():
    """Run the JSON simulation engine test."""
    
    from bsm2_python.real_json_engine import JSONSimulationEngine
    
    # Use the existing bsm1_simulation_config.json file
    config_path = '/home/runner/work/bsm2-python/bsm2-python/bsm1_simulation_config.json'
    
    engine = JSONSimulationEngine(config_path)
    results = engine.simulate()
    
    return results['effluent'], results['sludge_height'], results['tss_internal']

def run_simple_test():
    """Test the JSON engine with a simple configuration."""
    
    from bsm2_python.real_json_engine import JSONSimulationEngine
    
    # Simple test configuration
    simple_config = {
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
    
    engine = JSONSimulationEngine(simple_config)
    results = engine.simulate()
    
    return results['effluent'], results['sludge_height'], results['tss_internal']

def main():
    """Test the new JSON engine."""
    
    print("Testing new advanced JSON simulation engine...")
    
    try:
        print("Running simple test...")
        simple_effluent, simple_sludge_height, simple_tss_internal = run_simple_test()
        
        print(f"✓ Simple test completed:")
        print(f"  Effluent: {simple_effluent[:5]}...")
        print(f"  Sludge height: {simple_sludge_height}")
        print(f"  TSS internal: {simple_tss_internal[:3]}...")
        
        print("\nRunning BSM1 configuration test...")
        json_effluent, json_sludge_height, json_tss_internal = run_json_engine_test()
        
        print(f"✓ BSM1 configuration test completed:")
        print(f"  Effluent: {json_effluent[:5]}...")
        print(f"  Sludge height: {json_sludge_height}")
        print(f"  TSS internal: {json_tss_internal[:3]}...")
        
        print(f"\n🎉 SUCCESS! New advanced JSON engine is working!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())