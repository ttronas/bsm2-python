"""
Test file to compare the original ADM1 test implementation with the JSON-based simulation engine.
This test validates that the simulation engine produces similar results to the reference ADM1 implementation.
"""

import asyncio
import json
import numpy as np
import sys
import os

# Add paths to import modules
sys.path.append('/home/runner/work/bsm2-python/bsm2-python/src')
sys.path.append('/home/runner/work/bsm2-python/bsm2-python/wwtp-simulator/backend')

from simulation_engine import SimulationEngine
from models import SimulationConfig, FlowNode, FlowEdge, SimulationSettings
from bsm2_python.bsm2.adm1_bsm2 import ADM1Reactor
from bsm2_python.bsm2.init import adm1init_bsm2 as adm1init
from bsm2_python.log import logger

def load_adm1_test_config():
    """Load the ADM1 test configuration from JSON."""
    json_path = '/home/runner/work/bsm2-python/bsm2-python/wwtp-simulator/backend/predefined_flowsheets/adm1.json'
    
    with open(json_path, 'r') as f:
        config_data = json.load(f)
    
    # Convert JSON to SimulationConfig objects
    nodes = []
    for node_data in config_data['nodes']:
        node = FlowNode(
            id=node_data['id'],
            type=node_data['type'],
            position=node_data['position'],
            data=node_data['data']
        )
        nodes.append(node)
    
    edges = []
    for edge_data in config_data['edges']:
        edge = FlowEdge(
            id=edge_data['id'],
            source=edge_data['source'],
            target=edge_data['target'],
            sourceHandle=edge_data.get('sourceHandle', 'output-0'),
            targetHandle=edge_data.get('targetHandle', 'input-0')
        )
        edges.append(edge)
    
    settings = SimulationSettings(**config_data['settings'])
    
    config = SimulationConfig(
        name=config_data['name'],
        description=config_data['description'],
        nodes=nodes,
        edges=edges,
        settings=settings
    )
    
    return config

async def test_json_simulation_engine():
    """Test the JSON-based simulation engine with ADM1."""
    logger.info("Starting ADM1 JSON simulation engine test...")
    
    # Load configuration
    config = load_adm1_test_config()
    
    # Create simulation engine
    engine = SimulationEngine()
    
    # Run simulation
    try:
        results = await engine.run_simulation(config)
        logger.info("ADM1 JSON simulation completed successfully")
        
        # Extract ADM1 reactor results
        adm1_component = 'adm1-reactor-1'
        if adm1_component in results['components']:
            adm1_results = results['components'][adm1_component]
            if isinstance(adm1_results, list) and adm1_results:
                # Get the final ADM1 output
                final_result = adm1_results[-1]
                if isinstance(final_result, dict):
                    logger.info(f"ADM1 JSON simulation final result keys: {final_result.keys()}")
                    return results
            
        logger.warning("No suitable ADM1 component found in results")
        logger.info(f"Available components: {list(results['components'].keys())}")
        return results
    
    except Exception as e:
        logger.error(f"ADM1 JSON simulation failed: {e}")
        return None

def test_original_adm1():
    """Test the original ADM1 implementation."""
    logger.info("Starting original ADM1 test...")
    
    try:
        # Create ADM1 reactor with same parameters as test
        adm1_reactor = ADM1Reactor(adm1init.DIGESTERINIT, adm1init.DIGESTERPAR, adm1init.INTERFACEPAR, adm1init.DIM_D)
        
        # Same influent as test
        y_in = np.array([
            28.0665048629843,
            48.9525780251450,
            10361.7145189587,
            20375.0163964256,
            10210.0695779898,
            553.280744847661,
            3204.66026217631,
            0.252251384955929,
            1.68714307465010,
            28.9098125063162,
            4.68341082328394,
            906.093288634802,
            7.15490225533614,
            33528.5561252986,
            178.467454963180,
            14.8580800598190,
            0,
            0,
            0,
            0,
            0,
        ])
        
        timestep = 15 / (60 * 24)
        endtime = 200
        simtime = np.arange(0, endtime, timestep, dtype=float)
        
        y_out2 = np.zeros(21)
        yd_out = np.zeros(51)
        y_out1 = np.zeros(33)
        
        # Run simulation
        for step in simtime:
            y_out2, yd_out, y_out1 = adm1_reactor.output(timestep, step, y_in, adm1init.t_op)
        
        logger.info("Original ADM1 simulation completed successfully")
        logger.info(f"Original ADM1 final y_out2 (ADM2ASM): {y_out2}")
        logger.info(f"Original ADM1 final yd_out (digester): {yd_out}")
        logger.info(f"Original ADM1 final y_out1 (ASM2ADM): {y_out1}")
        
        return {
            'y_out2': y_out2,  # ADM2ASM output
            'yd_out': yd_out,  # Digester output
            'y_out1': y_out1   # ASM2ADM output
        }
    
    except Exception as e:
        logger.error(f"Original ADM1 simulation failed: {e}")
        return None

def compare_results(json_results, original_results):
    """Compare results from both simulation approaches."""
    if not json_results or not original_results:
        logger.error("Cannot compare - one or both simulations failed")
        return
    
    logger.info("\n" + "="*50)
    logger.info("ADM1 COMPARISON RESULTS")
    logger.info("="*50)
    
    # Compare ADM1 reactor results
    if 'adm1-reactor-1' in json_results['components']:
        adm1_results = json_results['components']['adm1-reactor-1']
        if adm1_results and isinstance(adm1_results, list):
            final_result = adm1_results[-1]
            if isinstance(final_result, dict):
                # Compare available outputs
                for key in ['adm2asm', 'digester', 'asm2adm']:
                    if key in final_result:
                        json_output = np.array(final_result[key])
                        
                        # Map to original output
                        if key == 'adm2asm':
                            original_output = original_results['y_out2']
                        elif key == 'digester':
                            original_output = original_results['yd_out']
                        elif key == 'asm2adm':
                            original_output = original_results['y_out1']
                        else:
                            continue
                        
                        # Calculate differences
                        diff = np.abs(json_output - original_output)
                        max_diff = np.max(diff)
                        rel_diff = diff / (np.abs(original_output) + 1e-10)
                        max_rel_diff = np.max(rel_diff)
                        
                        logger.info(f"\n{key.upper()} OUTPUT COMPARISON:")
                        logger.info(f"Maximum absolute difference: {max_diff:.6f}")
                        logger.info(f"Maximum relative difference: {max_rel_diff:.6f}")
                        logger.info(f"Original final values: {original_output}")
                        logger.info(f"JSON final values: {json_output}")
                        
                        # Check if results are close
                        if np.allclose(json_output, original_output, rtol=0.1, atol=1.0):
                            logger.info(f"✅ {key} Results are reasonably close!")
                        else:
                            logger.warning(f"❌ {key} Results differ significantly")
    else:
        logger.warning("No ADM1 reactor component found in JSON results")
        logger.info(f"Available components: {list(json_results['components'].keys())}")

async def main():
    """Main test function."""
    logger.info("Starting ADM1 simulation engine comparison test")
    
    # Test original ADM1
    original_results = test_original_adm1()
    
    # Test JSON simulation engine
    json_results = await test_json_simulation_engine()
    
    # Compare results
    compare_results(json_results, original_results)
    
    logger.info("\nADM1 Test completed.")

if __name__ == "__main__":
    asyncio.run(main())