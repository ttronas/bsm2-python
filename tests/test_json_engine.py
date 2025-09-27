#!/usr/bin/env python3
"""
Minimal test output: only print test results and output arrays.
"""

import sys
import numpy as np
import json

sys.path.insert(0, '/workspaces/bsm2-python/src')

def run_bsm1ol_test():
    from bsm2_python.bsm1_ol import BSM1OL
    y_in = np.array([
        [0.0, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
        [200.1, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
    ])
    bsm1_ol = BSM1OL(data_in=y_in, timestep=15 / (60 * 24), endtime=20, tempmodel=False, activate=False)
    for idx in range(len(bsm1_ol.simtime)):
        bsm1_ol.step(idx)
    return bsm1_ol.ys_eff, bsm1_ol.sludge_height, bsm1_ol.ys_tss_internal

def run_bsm2ol_test():
    from bsm2_python.bsm2_ol import BSM2OL
    bsm2_ol = BSM2OL(endtime=5, timestep=15 / 60 / 24, tempmodel=False, activate=False)
    for idx in range(len(bsm2_ol.simtime)):
        bsm2_ol.step(idx)
    return bsm2_ol.y_eff_all[-1, :], getattr(bsm2_ol, 'sludge_height', 0.0), getattr(bsm2_ol, 'ys_tss_internal', np.zeros(10))

def run_json_bsm1_test():
    from bsm2_python.engine.engine import SimulationEngine
    config_path = '/workspaces/bsm2-python/bsm1_ol_config.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    config['simulation_settings']['steady_endtime'] = 20
    engine = SimulationEngine(config)
    results = engine.simulate()
    return results['effluent'], results['sludge_height'], results['tss_internal']

def run_json_bsm2_test():
    from bsm2_python.engine.engine import SimulationEngine
    config_path = '/workspaces/bsm2-python/bsm2_ol_config.json'
    with open(config_path, 'r') as f:
        config = json.load(f)
    config['simulation_settings']['steady_endtime'] = 5
    engine = SimulationEngine(config)
    results = engine.simulate()
    return results['effluent'], results['sludge_height'], results['tss_internal']

def compare_results(name, class_result, json_result, tolerance=1e-5):
    print(f"\n{name} - Class result:\n{np.array(class_result)}")
    print(f"{name} - JSON result:\n{np.array(json_result)}")
    if class_result is None or json_result is None:
        print(f"{name}: FAIL (None result)")
        return False
    if isinstance(class_result, np.ndarray) and isinstance(json_result, np.ndarray):
        match = np.allclose(class_result, json_result, rtol=tolerance, atol=tolerance)
        print(f"{name}: {'PASS' if match else 'FAIL'} (max diff: {np.max(np.abs(class_result - json_result)):.2e})")
        return match
    elif isinstance(class_result, (int, float)) and isinstance(json_result, (int, float)):
        match = abs(class_result - json_result) < tolerance
        print(f"{name}: {'PASS' if match else 'FAIL'} (diff: {abs(class_result - json_result):.2e})")
        return match
    else:
        print(f"{name}: FAIL (type mismatch)")
        return False

def main():
    overall_success = True

    # BSM1
    try:
        bsm1_effluent, bsm1_sludge_height, bsm1_tss_internal = run_bsm1ol_test()
        json1_effluent, json1_sludge_height, json1_tss_internal = run_json_bsm1_test()
        bsm1_effluent_match = compare_results("BSM1 Effluent", bsm1_effluent, json1_effluent, tolerance=1e-3)
        bsm1_height_match = compare_results("BSM1 Sludge Height", bsm1_sludge_height, json1_sludge_height, tolerance=1e-3)
        bsm1_tss_match = compare_results("BSM1 TSS Internal", bsm1_tss_internal, json1_tss_internal, tolerance=1e-2)
        bsm1_success = bsm1_effluent_match and bsm1_height_match and bsm1_tss_match
        print(f"BSM1 Overall: {'PASS' if bsm1_success else 'FAIL'}")
        overall_success = overall_success and bsm1_success
    except Exception as e:
        print(f"BSM1: FAIL ({e})")
        overall_success = False

    # BSM2
    try:
        bsm2_effluent, bsm2_sludge_height, bsm2_tss_internal = run_bsm2ol_test()
        json2_effluent, json2_sludge_height, json2_tss_internal = run_json_bsm2_test()
        bsm2_effluent_match = compare_results("BSM2 Effluent", bsm2_effluent, json2_effluent)
        bsm2_height_match = compare_results("BSM2 Sludge Height", bsm2_sludge_height, json2_sludge_height)
        bsm2_tss_match = compare_results("BSM2 TSS Internal", bsm2_tss_internal, json2_tss_internal)
        bsm2_success = bsm2_effluent_match and bsm2_height_match and bsm2_tss_match
        print(f"BSM2 Overall: {'PASS' if bsm2_success else 'FAIL'}")
        overall_success = overall_success and bsm2_success
    except Exception as e:
        print(f"BSM2: FAIL ({e})")
        overall_success = False

    print(f"\nFINAL RESULT: {'PASS' if overall_success else 'FAIL'}")
    return 0 if overall_success else 1

if __name__ == "__main__":
    import numpy as np
    import sys
    sys.exit(main())
