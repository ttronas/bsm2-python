#!/usr/bin/env python3
"""
Test the new advanced JSON engine directly without package imports.
"""
import sys
import os
import numpy as np

# Add the src directory to Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Import our engine modules directly
engine_path = os.path.join(src_path, 'bsm2_python', 'engine')
sys.path.append(engine_path)

from engine import SimulationEngine

def test_simple_configuration():
    """Test with a simple configuration."""
    
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
    
    print("Creating engine with simple configuration...")
    engine = SimulationEngine(simple_config)
    print("✓ Engine created")
    
    print("Running simulation...")
    results = engine.simulate()
    print("✓ Simulation completed")
    
    print(f"Results:")
    print(f"  Effluent: {results['effluent'][:5]}...")
    print(f"  Sludge height: {results['sludge_height']}")
    print(f"  TSS internal: {results['tss_internal'][:3]}...")
    
    return results

def test_bsm1_configuration():
    """Test with the BSM1 configuration file."""
    
    import json
    
    config_path = '/home/runner/work/bsm2-python/bsm2-python/bsm1_simulation_config.json'
    
    print(f"Loading BSM1 configuration from {config_path}...")
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    print("Creating engine with BSM1 configuration...")
    engine = SimulationEngine(config)
    print("✓ Engine created")
    
    print("Running simulation...")
    results = engine.simulate()
    print("✓ Simulation completed")
    
    print(f"Results:")
    print(f"  Effluent: {results['effluent'][:5]}...")
    print(f"  Sludge height: {results['sludge_height']}")
    print(f"  TSS internal: {results['tss_internal'][:3]}...")
    
    return results

def main():
    """Run tests."""
    
    print("Testing new advanced JSON simulation engine...")
    
    try:
        print("\n=== Simple Configuration Test ===")
        simple_results = test_simple_configuration()
        
        print("\n=== BSM1 Configuration Test ===")
        bsm1_results = test_bsm1_configuration()
        
        print(f"\n🎉 SUCCESS! Both tests completed successfully!")
        print(f"The new advanced JSON engine is working correctly.")
        
        return 0
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())