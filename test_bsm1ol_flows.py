#!/usr/bin/env python3
"""
Test to check the actual flow rates in BSM1OL class implementation.
This will help determine if the 92,230 m³/d flow rate is expected or wrong.
"""

import sys
import os
import numpy as np

# Add paths
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python')
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src')

def check_bsm1ol_flow_rates():
    """Check the actual flow rates in BSM1OL during simulation."""
    
    from bsm2_python.bsm1_ol import BSM1OL
    
    # Same influent data as used in JSON engine test
    y_in = np.array([
        [0.0, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
        [20.1, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
    ])
    
    print("🔍 CHECKING BSM1OL FLOW RATES")
    print("="*60)
    
    # Create BSM1OL with same parameters as JSON test
    bsm1_ol = BSM1OL(data_in=y_in, timestep=15 / (60 * 24), endtime=20, tempmodel=False, activate=False)
    
    print(f"Initial influent flow rate: {y_in[0][15]:.1f} m³/d")  # Q is at index 15 in the full array
    
    # Let's check the internal flow rates after a few steps
    for i in range(3):  # Check first 3 steps
        print(f"\n--- STEP {i+1} ---")
        
        # Get the current influent for this step
        y_in_timestep = bsm1_ol.y_in[i] if i < len(bsm1_ol.y_in) else bsm1_ol.y_in[-1]
        print(f"Input influent flow (y_in): Q={y_in_timestep[14]:.1f} m³/d")  # Q is at index 14 in y_in (without time)
        
        # Before step - check initial recycle values
        if hasattr(bsm1_ol, 'ys_out') and bsm1_ol.ys_out is not None:
            print(f"Settler recycle flow (ys_out): Q={bsm1_ol.ys_out[14]:.1f} m³/d")
        else:
            print("Settler recycle flow (ys_out): Not initialized yet")
            
        if hasattr(bsm1_ol, 'y_out5_r') and bsm1_ol.y_out5_r is not None:
            print(f"Process recycle flow (y_out5_r): Q={bsm1_ol.y_out5_r[14]:.1f} m³/d")
        else:
            print("Process recycle flow (y_out5_r): Not initialized yet")
        
        # Perform the step
        bsm1_ol.step(i)
        
        # After step - check what flows were combined
        if hasattr(bsm1_ol, 'y_in1') and bsm1_ol.y_in1 is not None:
            print(f"COMBINER OUTPUT (y_in1): Q={bsm1_ol.y_in1[14]:.1f} m³/d")
        
        # Check reactor outputs
        for reactor_num in range(1, 6):
            attr_name = f'y_out{reactor_num}'
            if hasattr(bsm1_ol, attr_name):
                reactor_output = getattr(bsm1_ol, attr_name)
                if reactor_output is not None:
                    print(f"Reactor {reactor_num} output: Q={reactor_output[14]:.1f} m³/d")
    
    print(f"\n" + "="*60)
    print("🏁 BSM1OL FLOW ANALYSIS COMPLETE")
    
    # Return the combiner input flow rate for comparison
    final_combiner_flow = bsm1_ol.y_in1[14] if hasattr(bsm1_ol, 'y_in1') and bsm1_ol.y_in1 is not None else 0
    return final_combiner_flow

if __name__ == "__main__":
    flow_rate = check_bsm1ol_flow_rates()
    print(f"\n📊 FINAL RESULT:")
    print(f"BSM1OL combiner flow rate: {flow_rate:.1f} m³/d")
    print(f"JSON engine combiner flow rate: 92,230 m³/d")
    print(f"Match: {'✅ YES' if abs(flow_rate - 92230) < 1000 else '❌ NO'}")