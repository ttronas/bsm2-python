"""Test file for BSM1OLDouble model (two parallel WWTPs connected to one effluent)"""

import time

import numpy as np
from tqdm import tqdm

from bsm2_python.bsm1_ol_double import BSM1OLDouble
from bsm2_python.log import logger

tempmodel = False  # if False influent wastewater temperature is just passed through process reactors and settler
# if True mass balance for the wastewater temperature is used in process reactors and settler

activate = False  # if False dummy states are 0
# if True dummy states are activated


def test_bsm1_ol_double():
    """Test BSM1OLDouble with two parallel WWTPs."""
    # CONSTINFLUENT from BSM2:
    y_in = np.array(
        [
            [0.0, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
            [
                200.1,
                30,
                69.5,
                51.2,
                202.32,
                28.17,
                0,
                0,
                0,
                0,
                31.56,
                6.95,
                10.59,
                7,
                211.2675,
                18446,
                15,
                0,
                0,
                0,
                0,
                0,
            ],
        ]
    )
    bsm1_ol_double = BSM1OLDouble(data_in=y_in, timestep=15 / (60 * 24), endtime=50, tempmodel=tempmodel, activate=activate)

    start = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm1_ol_double.simtime)):
        bsm1_ol_double.step(idx)

    stop = time.perf_counter()

    logger.info('BSM1OLDouble simulation completed after: %s seconds', stop - start)
    logger.info('Final Effluent at t = %s d: \\n %s', bsm1_ol_double.endtime, bsm1_ol_double.final_effluent)
    logger.info('WWTP1 Effluent at t = %s d: \\n %s', bsm1_ol_double.endtime, bsm1_ol_double.ys_eff)
    logger.info('WWTP2 Effluent at t = %s d: \\n %s', bsm1_ol_double.endtime, bsm1_ol_double.ys_eff_2)
    logger.info('WWTP1 Sludge height at t = %s d: \\n %s', bsm1_ol_double.endtime, bsm1_ol_double.sludge_height)
    logger.info('WWTP2 Sludge height at t = %s d: \\n %s', bsm1_ol_double.endtime, bsm1_ol_double.sludge_height_2)

    # Test that final effluent flow rate is approximately equal to the sum of individual WWTP flows
    final_flow = bsm1_ol_double.final_effluent[14]
    wwtp1_flow = bsm1_ol_double.ys_eff[14] 
    wwtp2_flow = bsm1_ol_double.ys_eff_2[14]
    combined_flow = wwtp1_flow + wwtp2_flow
    
    logger.info('Final effluent flow rate: %s', final_flow)
    logger.info('WWTP1 + WWTP2 flow rate: %s', combined_flow)
    logger.info('Flow rate difference: %s', abs(final_flow - combined_flow))
    
    # Verify that the flows are approximately equal (within tolerance)
    assert abs(final_flow - combined_flow) < 1e-6, f"Flow rates don't match: {final_flow} vs {combined_flow}"
    
    # Verify that each WWTP gets approximately half the input flow
    original_flow = y_in[0, 15]  # Q is at index 14, but y_in includes time at index 0
    expected_wwtp_flow = original_flow / 2
    
    logger.info('Original input flow: %s', original_flow)
    logger.info('Expected per-WWTP flow: %s', expected_wwtp_flow)
    
    # Allow some tolerance for recycle flows affecting the final effluent flows
    assert abs(wwtp1_flow - expected_wwtp_flow) < expected_wwtp_flow * 0.2, f"WWTP1 flow deviates too much: {wwtp1_flow} vs {expected_wwtp_flow}"
    assert abs(wwtp2_flow - expected_wwtp_flow) < expected_wwtp_flow * 0.2, f"WWTP2 flow deviates too much: {wwtp2_flow} vs {expected_wwtp_flow}"
    
    # Verify that both WWTPs have reasonable sludge heights (not zero, not extreme)
    assert 0 < bsm1_ol_double.sludge_height < 10, f"WWTP1 sludge height unreasonable: {bsm1_ol_double.sludge_height}"
    assert 0 < bsm1_ol_double.sludge_height_2 < 10, f"WWTP2 sludge height unreasonable: {bsm1_ol_double.sludge_height_2}"
    
    logger.info('BSM1OLDouble test passed successfully!')


def test_bsm1_ol_double_short():
    """Short test for BSM1OLDouble - just a few steps to verify basic functionality."""
    # CONSTINFLUENT from BSM2:
    y_in = np.array(
        [
            [0.0, 30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0],
            [
                1.1,
                30,
                69.5,
                51.2,
                202.32,
                28.17,
                0,
                0,
                0,
                0,
                31.56,
                6.95,
                10.59,
                7,
                211.2675,
                18446,
                15,
                0,
                0,
                0,
                0,
                0,
            ],
        ]
    )
    bsm1_ol_double = BSM1OLDouble(data_in=y_in, timestep=15 / (60 * 24), endtime=1, tempmodel=tempmodel, activate=activate)

    # Run just a few steps
    for idx in range(min(10, len(bsm1_ol_double.simtime))):
        bsm1_ol_double.step(idx)

    logger.info('BSM1OLDouble short test completed successfully!')


if __name__ == "__main__":
    test_bsm1_ol_double_short()
    test_bsm1_ol_double()