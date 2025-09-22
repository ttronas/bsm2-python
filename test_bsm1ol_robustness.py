#!/usr/bin/env python3
"""
Test to check if BSM1OL has division by zero issues with the same high flow rates.
"""

import sys
import os
import numpy as np
import warnings

# Add paths
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python')
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src')

def test_bsm1ol_robustness():
    """Test if BSM1OL can handle the high flow rates without errors."""
    
    from bsm2_python.bsm1_ol import BSM1OL
    
    # Same influent data as used in JSON engine test
    y_in = np.array([
        [0.0, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
        [20.1, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
    ])
    
    print("🧪 TESTING BSM1OL ROBUSTNESS WITH HIGH FLOW RATES")
    print("="*70)
    
    try:
        # Create BSM1OL with same parameters as JSON test  
        bsm1_ol = BSM1OL(data_in=y_in, timestep=15 / (60 * 24), endtime=20, tempmodel=False, activate=False)
        
        print(f"BSM1OL created successfully")
        print(f"Simulation steps: {len(bsm1_ol.simtime)}")
        
        # Count warnings and errors
        error_count = 0
        warning_count = 0
        
        # Capture warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            # Run the full simulation
            for idx in range(len(bsm1_ol.simtime)):
                try:
                    bsm1_ol.step(idx)
                    if idx < 5:  # Show flow rates for first few steps
                        combiner_flow = bsm1_ol.y_in1[14] if hasattr(bsm1_ol, 'y_in1') and bsm1_ol.y_in1 is not None else 0
                        print(f"Step {idx+1}: Combiner flow = {combiner_flow:.1f} m³/d")
                except Exception as e:
                    error_count += 1
                    print(f"❌ ERROR at step {idx+1}: {e}")
                    if "division by zero" in str(e):
                        print("  → Division by zero error!")
                    break
                    
        warning_count = len(w)
        if warning_count > 0:
            print(f"\n⚠️  Warnings generated: {warning_count}")
            for warning in w[:5]:  # Show first 5 warnings
                print(f"  - {warning.message}")
                
        if error_count == 0:
            print(f"\n✅ BSM1OL completed {len(bsm1_ol.simtime)} steps WITHOUT errors")
            print(f"Final combiner flow: {bsm1_ol.y_in1[14]:.1f} m³/d")
            print(f"Final effluent: {bsm1_ol.ys_eff[:5]}")
            return True
        else:
            print(f"\n❌ BSM1OL failed with {error_count} errors")
            return False
            
    except Exception as e:
        print(f"❌ BSM1OL creation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_bsm1ol_robustness()
    
    print(f"\n" + "="*70)
    print("🏁 CONCLUSION:")
    if success:
        print("✅ BSM1OL handles 92,230 m³/d flow rates WITHOUT division by zero errors")
        print("  → This suggests my JSON engine has different numerical handling")
        print("  → Need to investigate differences in how components process high flows")
    else:
        print("❌ BSM1OL ALSO has division by zero errors with high flow rates")
        print("  → This confirms the issue is fundamental to BSM1 with these parameters")
        print("  → Both implementations encounter the same numerical limitation")