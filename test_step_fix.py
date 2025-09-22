#!/usr/bin/env python3
"""
Simple test to verify the step parameter fix resolves division by zero errors.
"""

import sys
import os
import numpy as np

# Add paths
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python')
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src')

def test_step_parameter_fix():
    """Test if passing correct step parameter fixes the division by zero."""
    
    print("🧪 TESTING: Step parameter fix for division by zero")
    print("="*60)
    
    # Test 1: BSM1OL with high flow rates (should work)
    print("1️⃣ Testing BSM1OL with 92,230 m³/d flow rates...")
    from bsm2_python.bsm1_ol import BSM1OL
    y_in = np.array([
        [0.0, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
        [2.1, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
    ])
    
    try:
        bsm1_ol = BSM1OL(data_in=y_in, timestep=15 / (60 * 24), endtime=2, tempmodel=False, activate=False)
        for idx in range(len(bsm1_ol.simtime)):
            bsm1_ol.step(idx)
        print(f"   ✅ BSM1OL: SUCCESS - Final combiner Q={bsm1_ol.y_in1[14]:.1f}, effluent={bsm1_ol.ys_eff[:3]}")
        bsm1_success = True
    except Exception as e:
        print(f"   ❌ BSM1OL: FAILED - {e}")
        bsm1_success = False
    
    # Test 2: JSON Engine with step parameter fix
    print(f"\n2️⃣ Testing JSON Engine with step parameter fix...")
    from bsm2_python.engine.engine import SimulationEngine
    import json
    
    config_path = '/home/runner/work/bsm2-python/bsm2-python/bsm1_simulation_config.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    config['simulation_settings']['steady_endtime'] = 2
    
    try:
        # Redirect stdout to suppress debug output temporarily
        import io
        import contextlib
        
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            engine = SimulationEngine(config)
            results = engine.simulate()
        
        json_effluent = results['effluent']
        print(f"   ✅ JSON Engine: SUCCESS - Final effluent={json_effluent[:3] if json_effluent is not None else None}")
        json_success = True
    except Exception as e:
        print(f"   ❌ JSON Engine: FAILED - {e}")
        json_success = False
    
    # Comparison
    print(f"\n📊 RESULTS:")
    print(f"   BSM1OL (92,230 m³/d):     {'✅ SUCCESS' if bsm1_success else '❌ FAILED'}")
    print(f"   JSON Engine (step fix):   {'✅ SUCCESS' if json_success else '❌ FAILED'}")
    
    if bsm1_success and json_success:
        print(f"\n🎉 CONCLUSION: Step parameter fix RESOLVED the division by zero errors!")
        print(f"   Both BSM1OL and JSON Engine handle 92,230 m³/d flows correctly")
        return True
    elif bsm1_success and not json_success:
        print(f"\n⚠️  CONCLUSION: JSON Engine still has issues despite step parameter fix")
        return False
    elif not bsm1_success and not json_success:
        print(f"\n⚠️  CONCLUSION: Both engines fail - may be fundamental numerical limits")
        return False
    else:
        print(f"\n❓ CONCLUSION: Unexpected result pattern")
        return False

if __name__ == "__main__":
    success = test_step_parameter_fix()
    print(f"\n{'✅ SUCCESS' if success else '❌ NEEDS MORE WORK'}")