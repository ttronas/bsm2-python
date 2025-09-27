"""
Test file to compare the original BSM1_ol implementation with the JSON-based simulation engine.
This test validates that the simulation engine produces similar results to the reference BSM1 implementation.
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
from bsm2_python.bsm1_ol import BSM1OL
from bsm2_python.log import logger

def load_bsm1_test_config():
    """Load the BSM1 test configuration from JSON."""
    json_path = '/home/runner/work/bsm2-python/bsm2-python/wwtp-simulator/backend/predefined_flowsheets/bsm1_ol.json'
    
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
    """Test the JSON-based simulation engine with BSM1."""
    logger.info("Starting BSM1 JSON simulation engine test...")
    
    # Load configuration
    config = load_bsm1_test_config()
    
    # Create simulation engine
    engine = SimulationEngine()
    
    # Run simulation with short duration for testing
    config.settings.endTime = 1  # 1 day for quick test
    config.settings.timestep = 15  # 15 minutes
    
    try:
        results = await engine.run_simulation(config)
        logger.info("BSM1 JSON simulation completed successfully")
        
        # Extract effluent results (should be from settler effluent)
        effluent_component = 'settler-1'
        if effluent_component in results['components']:
            effluent_results = results['components'][effluent_component]
            if isinstance(effluent_results, list) and effluent_results:
                # Get the final effluent output
                final_result = effluent_results[-1]
                if isinstance(final_result, dict) and 'effluent' in final_result:
                    final_effluent = final_result['effluent']
                    logger.info(f"BSM1 JSON simulation final effluent: {final_effluent}")
                    return results
            
        logger.warning("No suitable effluent component found in BSM1 results")
        logger.info(f"Available components: {list(results['components'].keys())}")
        return results
    
    except Exception as e:
        logger.error(f"BSM1 JSON simulation failed: {e}")
        return None

def test_original_bsm1_ol():
    """Test the original BSM1_ol implementation."""
    logger.info("Starting original BSM1_ol test...")
    
    try:
        # Create BSM1OL instance with same parameters
        bsm1_ol = BSM1OL(endtime=1, timestep=15 / 60 / 24, tempmodel=False, activate=False)
        
        # Run simulation
        for idx, _ in enumerate(bsm1_ol.simtime):
            bsm1_ol.step(idx)
        
        logger.info("Original BSM1_ol simulation completed successfully")
        logger.info(f"Original BSM1_ol final effluent: {bsm1_ol.ys_eff}")
        
        return {
            'time': bsm1_ol.simtime,
            'effluent': bsm1_ol.ys_eff,
            'influent': bsm1_ol.y_in_all
        }
    
    except Exception as e:
        logger.error(f"Original BSM1_ol simulation failed: {e}")
        return None

def compare_results(json_results, original_results):
    """Compare results from both simulation approaches."""
    if not json_results or not original_results:
        logger.error("Cannot compare - one or both simulations failed")
        return
    
    logger.info("\n" + "="*50)
    logger.info("BSM1 COMPARISON RESULTS")
    logger.info("="*50)
    
    # Compare final effluent values
    if 'settler-1' in json_results['components']:
        settler_results = json_results['components']['settler-1']
        if settler_results and isinstance(settler_results, list):
            final_result = settler_results[-1]
            if isinstance(final_result, dict) and 'effluent' in final_result:
                json_final = final_result['effluent']
                original_final = original_results['effluent']
                
                logger.info(f"JSON final effluent shape: {np.array(json_final).shape}")
                logger.info(f"Original final effluent shape: {np.array(original_final).shape}")
                
                if isinstance(json_final, (list, np.ndarray)) and len(json_final) >= 21:
                    json_final = np.array(json_final)[:21]  # Take first 21 components
                    original_final = np.array(original_final)[:21]
                    
                    # Calculate differences
                    diff = np.abs(json_final - original_final)
                    max_diff = np.max(diff)
                    rel_diff = diff / (np.abs(original_final) + 1e-10)
                    max_rel_diff = np.max(rel_diff)
                    
                    logger.info(f"Maximum absolute difference: {max_diff:.6f}")
                    logger.info(f"Maximum relative difference: {max_rel_diff:.6f}")
                    logger.info(f"Original final values: {original_final}")
                    logger.info(f"JSON final values: {json_final}")
                    logger.info(f"Absolute differences: {diff}")
                    
                    # Check if results are close
                    if np.allclose(json_final, original_final, rtol=0.1, atol=1.0):
                        logger.info("✅ BSM1 Results are reasonably close!")
                    else:
                        logger.warning("❌ BSM1 Results differ significantly")
                else:
                    logger.warning(f"JSON final effluent format unexpected: {type(json_final)}, {json_final}")
    else:
        logger.warning("No settler component found in JSON results")
        logger.info(f"Available components: {list(json_results['components'].keys())}")

async def main():
    """Main test function."""
    logger.info("Starting BSM1 simulation engine comparison test")
    
    # Test original BSM1_ol
    original_results = test_original_bsm1_ol()
    
    # Test JSON simulation engine
    json_results = await test_json_simulation_engine()
    
    # Compare results
    compare_results(json_results, original_results)
    
    logger.info("\nBSM1 Test completed.")

if __name__ == "__main__":
    asyncio.run(main())