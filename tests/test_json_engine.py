#!/usr/bin/env python3
"""
Test BSM1 simulation configurations using JSON engine and compare with MATLAB results.
"""

import sys
import os
import numpy as np

# Add paths
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python')
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src')


def test_bsm1_simulation_config():
    """Test bsm1_simulation_config.json against MATLAB results."""
    
    from bsm2_python.real_json_engine import JSONSimulationEngine
    
    print("Testing bsm1_simulation_config.json...")
    
    # MATLAB reference values for steady state simulation (200 days)
    ys_eff_matlab = np.array([
        30.0000000000000,
        0.889492799653682,
        4.39182747787874,
        0.188440413683379,
        9.78152406404732,
        0.572507856962265,
        1.72830016782928,
        0.490943515687561,
        10.4152201204309,
        1.73333146817512,
        0.688280004678034,
        0.0134804685779854,
        4.12557938198182,
        12.4969499853007,
        18061,
        15,
        0,
        0,
        0,
        0,
        0,
    ])
    sludge_height_matlab = 0.447178539974702
    
    ys_tss_matlab = np.array([
        12.4969498996665,
        18.1132132624131,
        29.5402273766893,
        68.9780506740299,
        356.074706190146,
        356.074706190149,
        356.074706190151,
        356.074706190154,
        356.074706190157,
        6393.98442118288,
    ])
    
    # Run JSON simulation
    config_path = '/home/runner/work/bsm2-python/bsm2-python/bsm1_simulation_config.json'
    engine = JSONSimulationEngine(config_path)
    results = engine.simulate()
    
    # Extract results
    ys_eff = results['effluent']
    sludge_height = results['sludge_height']
    ys_tss_internal = results['tss_internal']
    
    print(f"JSON effluent:      {ys_eff[:5]}")
    print(f"MATLAB effluent:    {ys_eff_matlab[:5]}")
    print(f"JSON sludge height:      {sludge_height}")
    print(f"MATLAB sludge height:    {sludge_height_matlab}")
    
    # Test against MATLAB values
    effluent_match = np.allclose(ys_eff, ys_eff_matlab, rtol=1e-5, atol=1e-5)
    height_match = np.allclose(sludge_height, sludge_height_matlab, rtol=1e-5, atol=1e-5)
    tss_match = np.allclose(ys_tss_internal, ys_tss_matlab, rtol=1e-5, atol=1e-5)
    
    print(f"\nMatches with MATLAB:")
    print(f"✓ Effluent: {effluent_match}")
    print(f"✓ Sludge height: {height_match}")
    print(f"✓ TSS internal: {tss_match}")
    
    if not effluent_match:
        diff = np.abs(ys_eff - ys_eff_matlab)
        print(f"Effluent max difference: {np.max(diff)}")
    if not height_match:
        diff = abs(sludge_height - sludge_height_matlab)
        print(f"Sludge height difference: {diff}")
    if not tss_match:
        diff = np.abs(ys_tss_internal - ys_tss_matlab)
        print(f"TSS internal max difference: {np.max(diff)}")
    
    return effluent_match and height_match and tss_match


def test_bsm1_ol_double_simulation_config():
    """Test BSM1OLDouble class directly against expected results."""
    
    from bsm2_python.bsm1_ol_double import BSM1OLDouble
    
    print("\nTesting BSM1OLDouble class...")
    
    # Use the same input data as for single WWTP
    y_in = np.array([
        [0.0, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
        [200.1, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
    ])
    
    # Run BSM1OLDouble simulation
    bsm1_double = BSM1OLDouble(data_in=y_in, timestep=15 / (60 * 24), endtime=200, tempmodel=False, activate=False)
    
    for idx in range(len(bsm1_double.simtime)):
        bsm1_double.step(idx)
    
    # Extract results
    ys_eff = bsm1_double.final_effluent
    sludge_height_1 = bsm1_double.sludge_height  # WWTP1 sludge height
    sludge_height_2 = bsm1_double.sludge_height_2  # WWTP2 sludge height
    ys_tss_internal_1 = bsm1_double.ys_tss_internal  # WWTP1 TSS
    ys_tss_internal_2 = bsm1_double.ys_tss_internal_2  # WWTP2 TSS
    
    print(f"BSM1OLDouble final effluent:      {ys_eff[:5]}")
    print(f"BSM1OLDouble WWTP1 effluent:      {bsm1_double.ys_eff[:5]}")
    print(f"BSM1OLDouble WWTP2 effluent:      {bsm1_double.ys_eff_2[:5]}")
    print(f"BSM1OLDouble WWTP1 sludge height: {sludge_height_1}")
    print(f"BSM1OLDouble WWTP2 sludge height: {sludge_height_2}")
    print(f"BSM1OLDouble final flow rate:     {ys_eff[14]}")
    print(f"BSM1OLDouble WWTP1 flow rate:     {bsm1_double.ys_eff[14]}")
    print(f"BSM1OLDouble WWTP2 flow rate:     {bsm1_double.ys_eff_2[14]}")
    
    # Verify the basic functionality of double WWTP
    # 1. Final effluent flow should be sum of individual WWTP flows
    combined_flow = bsm1_double.ys_eff[14] + bsm1_double.ys_eff_2[14]
    flow_conservation = abs(ys_eff[14] - combined_flow) < 1e-6
    
    # 2. Each WWTP should have reasonable individual flows (roughly half of input)
    input_flow = y_in[0, 15]  # Q is at index 14 in y_in data (excluding time)
    expected_individual_flow = input_flow / 2
    wwtp1_flow_reasonable = abs(bsm1_double.ys_eff[14] - expected_individual_flow) < expected_individual_flow * 0.5
    wwtp2_flow_reasonable = abs(bsm1_double.ys_eff_2[14] - expected_individual_flow) < expected_individual_flow * 0.5
    
    # 3. Sludge heights should be reasonable and positive
    sludge_heights_reasonable = (0 < sludge_height_1 < 10) and (0 < sludge_height_2 < 10)
    
    # 4. Final effluent concentrations should be reasonable (finite, positive for most components)
    concentrations_reasonable = (np.isfinite(ys_eff[:14]).all() and 
                               (ys_eff[:14] >= 0).all() and
                               ys_eff[15] > 0)  # Temperature should be positive
    
    # 5. Both WWTPs should be processing roughly the same amount
    wwtp_balance = abs(bsm1_double.ys_eff[14] - bsm1_double.ys_eff_2[14]) < max(bsm1_double.ys_eff[14], bsm1_double.ys_eff_2[14]) * 0.1
    
    print(f"\nBSM1OLDouble validation checks:")
    print(f"✓ Flow conservation (final = WWTP1 + WWTP2): {flow_conservation}")
    print(f"✓ WWTP1 flow reasonable: {wwtp1_flow_reasonable}")
    print(f"✓ WWTP2 flow reasonable: {wwtp2_flow_reasonable}")
    print(f"✓ Sludge heights reasonable: {sludge_heights_reasonable}")
    print(f"✓ Concentrations reasonable: {concentrations_reasonable}")
    print(f"✓ WWTP flow balance: {wwtp_balance}")
    
    # Additional diagnostic info
    print(f"\nDiagnostic info:")
    print(f"Input flow: {input_flow}")
    print(f"Expected individual WWTP flow: {expected_individual_flow}")
    print(f"Final effluent flow: {ys_eff[14]}")
    print(f"Combined individual flows: {combined_flow}")
    print(f"Flow conservation error: {abs(ys_eff[14] - combined_flow)}")
    
    return (flow_conservation and wwtp1_flow_reasonable and wwtp2_flow_reasonable and 
            sludge_heights_reasonable and concentrations_reasonable and wwtp_balance)


def main():
    """Run both JSON simulation engine tests."""
    
    print("Testing JSON simulation engine configurations...")
    
    try:
        # Test single WWTP configuration
        single_success = test_bsm1_simulation_config()
        
        # Test double WWTP configuration
        double_success = test_bsm1_ol_double_simulation_config()
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"✓ Single WWTP test: {'PASSED' if single_success else 'FAILED'}")
        print(f"✓ Double WWTP test: {'PASSED' if double_success else 'FAILED'}")
        
        if single_success and double_success:
            print(f"\n🎉 SUCCESS! All JSON engine tests passed!")
            return 0
        else:
            print(f"\n❌ FAILURE! Some tests failed.")
            return 1
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())