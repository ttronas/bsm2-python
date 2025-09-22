#!/usr/bin/env python3
"""
Test the new flow initialization approach - only tear edges initialized, others start with zeros.
"""

import sys
import os
import numpy as np
import json

# Add paths
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python')
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src')

def test_new_flow_approach():
    """Test the new flow initialization approach."""
    
    from bsm2_python.engine.engine import SimulationEngine
    
    print("🧪 Testing NEW flow initialization approach:")
    print("   - Only tear edges initialized with _create_copies equivalent")
    print("   - Other edges start with zeros")
    
    # Load BSM1 configuration
    config_path = '/home/runner/work/bsm2-python/bsm2-python/bsm1_simulation_config.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Very short simulation for testing
    config['simulation_settings']['steady_endtime'] = 1.0  # 1 day instead of 0.1
    
    try:
        engine = SimulationEngine(config)
        results = engine.simulate()
        print(f"✓ NEW approach SUCCESS: {results['effluent'][:5] if results['effluent'] is not None else 'None'}")
        return True
    except Exception as e:
        print(f"❌ NEW approach failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Check if it's still a division by zero
        if "division by zero" in str(e):
            print("   → Still getting division by zero errors")
            print("   → Need further debugging")
        elif "flow" in str(e).lower():
            print("   → Flow-related error")
        else:
            print("   → Different error type - may be progress!")
            
        return False

if __name__ == "__main__":
    print("🔍 TESTING: New flow initialization approach")
    print("="*60)
    
    success = test_new_flow_approach()
    
    print("\n" + "="*60)
    print("🏁 TEST RESULT:")
    if success:
        print("✓ New approach solved the numerical issues!")
    else:
        print("❌ New approach didn't resolve the issues")
        print("   Further debugging needed as suggested in the comment")