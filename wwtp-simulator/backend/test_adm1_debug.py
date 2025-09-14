"""
Minimal test to debug the ADM1 reactor issue.
This focuses specifically on understanding what input the ADM1 reactor expects.
"""

import numpy as np
import logging
from pathlib import Path

# Import BSM2-Python components
from bsm2_python.bsm2.adm1_bsm2 import ADM1Reactor
from bsm2_python.bsm2.helpers_bsm2 import Combiner
import bsm2_python.bsm2.init.adm1init_bsm2 as adm1init

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_adm1_minimal():
    """Test ADM1 reactor with minimal setup."""
    
    # Load BSM2 influent data
    bsm2_data_path = '/home/runner/work/bsm2-python/bsm2-python/src/bsm2_python/data/dyninfluent_bsm2.csv'
    influent_data = np.loadtxt(bsm2_data_path, delimiter=',')
    y_in_first = influent_data[0, 1:22]  # First line, skip time, take 21 variables
    
    print(f"BSM2 influent first line: {y_in_first}")
    print(f"Influent shape: {y_in_first.shape}")
    print(f"Influent NaN check: {np.any(np.isnan(y_in_first))}")
    print(f"Influent inf check: {np.any(np.isinf(y_in_first))}")
    
    # Create ADM1 reactor
    adm1_reactor = ADM1Reactor(
        adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, 
        adm1init.INTERFACEPAR, adm1init.DIM_D
    )
    
    # Test 1: Try ADM1 with influent data directly
    try:
        print("\n=== Test 1: ADM1 with influent data ===")
        stepsize = 15 / 60 / 24  # 15 minutes in days
        step_time = 0.0
        temp = 35.0
        
        print(f"Input to ADM1: {y_in_first}")
        print(f"Input shape: {y_in_first.shape}")
        print(f"Stepsize: {stepsize}, Step time: {step_time}, Temp: {temp}")
        
        interface, digester, gas = adm1_reactor.output(stepsize, step_time, y_in_first, temp)
        
        print(f"ADM1 interface output: {interface}")
        print(f"ADM1 digester output: {digester}")
        print(f"ADM1 gas output: {gas}")
        print(f"Interface NaN: {np.any(np.isnan(interface))}")
        print(f"Digester NaN: {np.any(np.isnan(digester))}")
        print(f"Gas NaN: {np.any(np.isnan(gas))}")
        
    except Exception as e:
        print(f"Test 1 failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Try with zeros
    try:
        print("\n=== Test 2: ADM1 with zeros ===")
        zero_input = np.zeros(21)
        interface, digester, gas = adm1_reactor.output(stepsize, step_time, zero_input, temp)
        print(f"Zero input - Interface NaN: {np.any(np.isnan(interface))}")
        print(f"Zero input - Digester NaN: {np.any(np.isnan(digester))}")
        print(f"Zero input - Gas NaN: {np.any(np.isnan(gas))}")
    except Exception as e:
        print(f"Test 2 failed: {e}")
    
    # Test 3: Try with small values
    try:
        print("\n=== Test 3: ADM1 with small values ===")
        small_input = y_in_first.copy()
        small_input[14] = 1.0  # Set Q to 1
        interface, digester, gas = adm1_reactor.output(stepsize, step_time, small_input, temp)
        print(f"Small input - Interface NaN: {np.any(np.isnan(interface))}")
        print(f"Small input - Digester NaN: {np.any(np.isnan(digester))}")
        print(f"Small input - Gas NaN: {np.any(np.isnan(gas))}")
    except Exception as e:
        print(f"Test 3 failed: {e}")
    
    # Test 4: Test combiner behavior
    try:
        print("\n=== Test 4: Combiner behavior ===")
        combiner = Combiner()
        
        # Create two flows to combine
        flow1 = y_in_first.copy()
        flow1[14] = 500.0  # Q = 500
        flow2 = y_in_first.copy() 
        flow2[14] = 300.0  # Q = 300
        
        combined = combiner.output(flow1, flow2)
        print(f"Combined flow: {combined}")
        print(f"Combined Q: {combined[14]}")
        print(f"Combined NaN: {np.any(np.isnan(combined))}")
        
        # Now try ADM1 with combined flow
        interface, digester, gas = adm1_reactor.output(stepsize, step_time, combined, temp)
        print(f"ADM1 with combined input - Interface NaN: {np.any(np.isnan(interface))}")
        print(f"ADM1 with combined input - Digester NaN: {np.any(np.isnan(digester))}")
        print(f"ADM1 with combined input - Gas NaN: {np.any(np.isnan(gas))}")
        
    except Exception as e:
        print(f"Test 4 failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_adm1_minimal()