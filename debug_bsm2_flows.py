#!/usr/bin/env python3
"""
Debug BSM2 flow routing to identify why JSON engine produces different results.
"""

import sys
import os
import numpy as np
import json

# Add paths
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python')
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src')

def debug_bsm2_class_step():
    """Debug one step of BSM2OL class to understand flow routing."""
    
    from bsm2_python.bsm2_ol import BSM2OL
    
    # Run just one step and track all intermediate flows
    bsm2_ol = BSM2OL(endtime=1, timestep=15 / 60 / 24, tempmodel=False, activate=False)
    
    print("🔍 BSM2OL Class - Flow Tracing (Step 1)")
    print("="*60)
    
    # Step through first timestep
    bsm2_ol.step(0)
    
    print(f"Influent: {bsm2_ol.y_in[0][:5]}")
    print(f"Primary clarifier effluent: {bsm2_ol.yp_of[:5]}")
    print(f"Reactor 1 output: {bsm2_ol.y_out1[:5]}")
    print(f"Reactor 5 output: {bsm2_ol.y_out5[:5]}")
    print(f"Settler input: Q={bsm2_ol.y_out5[14]}")
    print(f"Settler effluent: {bsm2_ol.ys_of[:5]}")
    print(f"Final effluent: {bsm2_ol.y_eff[:5]}")
    
    return bsm2_ol

def debug_bsm2_json_step():
    """Debug one step of JSON BSM2 engine to compare flows."""
    
    from bsm2_python.engine.engine import SimulationEngine
    
    # Load BSM2 configuration
    config_path = '/home/runner/work/bsm2-python/bsm2-python/bsm2_ol_simulation_config.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Set very short endtime for debugging
    config['simulation_settings']['steady_endtime'] = 0.1
    
    print("🔍 JSON BSM2 Engine - Flow Tracing")
    print("="*60)
    
    # Create engine with debug output
    engine = SimulationEngine(config)
    
    # Run single step with debug
    engine.step_steady(engine.plan["stages"])
    
    # Look at key flow values
    print("\nKey Edge Values after 1 step:")
    for edge_id, value in engine.edge_values.items():
        if value is not None:
            print(f"  {edge_id}: Q={value[14]:.1f}, first 3 components: {value[:3]}")
    
    return engine

def compare_splitter_behavior():
    """Compare how splitters work in class vs JSON implementation."""
    
    print("🔍 SPLITTER COMPARISON")
    print("="*60)
    
    # Test simple splitter behavior
    from bsm2_python.bsm2.helpers_bsm2 import Splitter
    
    test_input = np.array([30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0])
    
    print(f"Test input: Q={test_input[14]}, first 3: {test_input[:3]}")
    
    # Test BSM2 main splitter (internal recycle)
    splitter = Splitter()
    
    # This mimics the BSM2 splitter logic with QINTR
    import bsm2_python.bsm2.init.asm1init_bsm2 as asm1init
    qintr = asm1init.QINTR
    print(f"QINTR (internal recycle): {qintr}")
    
    # Simulate BSM2 splitter behavior: flow_to_settler = max(total_flow - qintr, 0), recycle = qintr
    total_flow = test_input[14]
    flow_to_settler = max(total_flow - qintr, 0.0)
    recycle_flow = float(qintr)
    
    print(f"Total flow: {total_flow}")
    print(f"Flow to settler: {flow_to_settler}")
    print(f"Recycle flow: {recycle_flow}")
    
    # This reveals potential issue: if total flow < QINTR, we get zero to settler!
    if total_flow < qintr:
        print("⚠️  WARNING: Total flow less than QINTR - this could cause issues!")

def main():
    """Debug BSM2 flow routing differences."""
    
    print("🔧 BSM2 FLOW ROUTING DEBUG")
    print("="*60)
    
    # 1. Debug class implementation
    try:
        bsm2_class = debug_bsm2_class_step()
        print("✓ BSM2 class debug completed")
    except Exception as e:
        print(f"❌ BSM2 class debug failed: {e}")
        return
    
    print("\n" + "="*60)
    
    # 2. Debug JSON implementation  
    try:
        bsm2_json = debug_bsm2_json_step()
        print("✓ BSM2 JSON debug completed")
    except Exception as e:
        print(f"❌ BSM2 JSON debug failed: {e}")
        return
    
    print("\n" + "="*60)
    
    # 3. Compare splitter behavior
    compare_splitter_behavior()
    
    print("\n" + "="*60)
    print("🎯 FLOW ROUTING ANALYSIS")
    print("="*60)
    
    print("The BSM2 configuration in the JSON engine is missing several critical components:")
    print("1. Bypass splitters (input_splitter, bypass_plant, bypass_reactor)")
    print("2. Complex flow thresholds (QBYPASS = 60000 m³/d)")
    print("3. Multiple recycle pathways through thickeners")
    print("4. Flow splitting logic that depends on actual flow rates vs thresholds")
    print()
    print("The JSON config treats BSM2 like a simple BSM1 with extra components,")
    print("but BSM2 has a much more complex flow routing architecture.")

if __name__ == "__main__":
    main()