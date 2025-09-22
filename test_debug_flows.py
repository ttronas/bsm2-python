#!/usr/bin/env python3
"""
Debug test for the JSON engine with flow initialization fixes.
"""

import sys
import os
import numpy as np
import json

# Add paths
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python')
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src')

def test_debug_json_engine():
    """Test the JSON engine with debug output."""
    
    from bsm2_python.engine.engine import SimulationEngine
    
    print("🧪 Testing debug JSON engine with simple configuration...")
    
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
    
    try:
        engine = SimulationEngine(simple_config)
        results = engine.simulate()
        print(f"✓ Simple configuration success: {results['effluent'][:5]}")
        return True
    except Exception as e:
        print(f"❌ Simple configuration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bsm1_debug():
    """Test the BSM1 configuration with debug output."""
    
    from bsm2_python.engine.engine import SimulationEngine
    
    print("\n🧪 Testing BSM1 configuration with debug output...")
    
    # Load BSM1 configuration
    config_path = '/home/runner/work/bsm2-python/bsm2-python/bsm1_simulation_config.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Set very short simulation for debugging
    config['simulation_settings'] = config.get('simulation_settings', {})
    config['simulation_settings']['steady_endtime'] = 0.1  # Very short
    
    try:
        engine = SimulationEngine(config)
        results = engine.simulate()
        print(f"✓ BSM1 configuration success: {results['effluent'][:5] if results['effluent'] is not None else 'None'}")
        return True
    except Exception as e:
        print(f"❌ BSM1 configuration failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        if "division by zero" in str(e):
            print("   → This is the division by zero error we're investigating")
        elif "flow" in str(e).lower():
            print("   → This appears to be a flow-related error")
        return False

if __name__ == "__main__":
    print("🔍 DEBUG: Testing JSON engine with flow initialization fixes")
    print("="*70)
    
    success1 = test_debug_json_engine()
    success2 = test_bsm1_debug() if success1 else False
    
    print("\n" + "="*70)
    print("🏁 DEBUG SUMMARY:")
    print(f"   Simple config: {'✓ PASS' if success1 else '❌ FAIL'}")
    print(f"   BSM1 config:   {'✓ PASS' if success2 else '❌ FAIL'}")
    
    if success1:
        print("\n✓ The engine architecture and flow initialization are working!")
        if not success2:
            print("⚠ BSM1 configuration needs parameter fine-tuning")
    else:
        print("\n❌ Basic engine functionality needs fixing")