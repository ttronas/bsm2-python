#!/usr/bin/env python3
"""
Test comparing JSON simulation engine with BSM1OL to ensure exact match.
"""

import sys
import os
import numpy as np

# Add paths
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python')
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src')

def run_bsm1ol_test():
    """Run the original BSM1OL test."""
    
    from bsm2_python.bsm1_ol import BSM1OL
    
    # Exact same test as in bsm1_ol_test.py
    y_in = np.array([
        [0.0, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
        [200.1, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
    ])
    
    bsm1_ol = BSM1OL(data_in=y_in, timestep=15 / (60 * 24), endtime=200, tempmodel=False, activate=False)
    
    for idx in range(len(bsm1_ol.simtime)):
        bsm1_ol.step(idx)
    
    return bsm1_ol.ys_eff, bsm1_ol.sludge_height, bsm1_ol.ys_tss_internal

def run_json_engine_test():
    """Run the JSON simulation engine test."""
    
    from bsm2_python.real_json_engine import JSONSimulationEngine
    
    # Use the existing bsm1_simulation_config.json file
    config_path = '/home/runner/work/bsm2-python/bsm2-python/bsm1_simulation_config.json'
    
    engine = JSONSimulationEngine(config_path)
    results = engine.simulate()
    
    return results['effluent'], results['sludge_height'], results['tss_internal']

def main():
    """Compare BSM1OL with JSON engine results."""
    
    print("Comparing JSON simulation engine with BSM1OL...")
    
    try:
        # Run both simulations
        print("Running BSM1OL simulation...")
        bsm1_effluent, bsm1_sludge_height, bsm1_tss_internal = run_bsm1ol_test()
        
        print("Running JSON engine simulation...")
        json_effluent, json_sludge_height, json_tss_internal = run_json_engine_test()
        
        # Compare results
        print(f"\n=== COMPARISON RESULTS ===")
        print(f"BSM1OL effluent:      {bsm1_effluent[:5]}")
        print(f"JSON engine effluent: {json_effluent[:5]}")
        print(f"BSM1OL sludge height:      {bsm1_sludge_height}")
        print(f"JSON engine sludge height: {json_sludge_height}")
        
        # Check for exact match with appropriate numerical tolerance
        effluent_match = np.allclose(bsm1_effluent, json_effluent, rtol=1e-8, atol=1e-8)
        height_match = np.allclose(bsm1_sludge_height, json_sludge_height, rtol=1e-8, atol=1e-8)
        tss_match = np.allclose(bsm1_tss_internal, json_tss_internal, rtol=1e-5, atol=1e-5)
        
        print(f"\nExact matches:")
        print(f"✓ Effluent: {effluent_match}")
        print(f"✓ Sludge height: {height_match}")
        print(f"✓ TSS internal: {tss_match}")
        
        if effluent_match and height_match and tss_match:
            print(f"\n🎉 SUCCESS! JSON engine exactly matches BSM1OL results!")
            return 0
        else:
            print(f"\n❌ FAILURE! Results do not match exactly.")
            
            # Show differences
            if not effluent_match:
                diff = np.abs(bsm1_effluent - json_effluent)
                print(f"Effluent max difference: {np.max(diff)}")
            if not height_match:
                diff = abs(bsm1_sludge_height - json_sludge_height)
                print(f"Sludge height difference: {diff}")
            if not tss_match:
                diff = np.abs(bsm1_tss_internal - json_tss_internal)
                print(f"TSS internal max difference: {np.max(diff)}")
                
            return 1
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())