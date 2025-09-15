"""
Test comparison between JSON parsing simulation engine and original BSM2_ol implementation.

This test loads the BSM2 open loop configuration from JSON and compares the results
with the original BSM2_ol test case implementation to identify any differences.
"""

import json
import numpy as np
import time
import logging
from tqdm import tqdm
from pathlib import Path

# Import original BSM2 implementation
from bsm2_python.bsm2_ol import BSM2OL

# Import our simulation engine
from simulation_engine import SimulationEngine
from models import SimulationConfig, FlowNode, FlowEdge, SimulationSettings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

def load_bsm2_json_config():
    """Load the BSM2 open loop configuration from JSON."""
    json_path = Path("predefined_flowsheets/bsm2_ol.json")
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Convert JSON to models
    nodes = []
    for node_data in data['nodes']:
        node = FlowNode(
            id=node_data['id'],
            type=node_data['type'],
            position=node_data['position'],
            data=node_data['data']
        )
        nodes.append(node)
    
    edges = []
    for edge_data in data['edges']:
        edge = FlowEdge(
            id=edge_data['id'],
            source=edge_data['source'],
            target=edge_data['target'],
            sourceHandle=edge_data.get('sourceHandle'),
            targetHandle=edge_data.get('targetHandle')
        )
        edges.append(edge)
    
    settings = SimulationSettings(
        timestep=15,  # 15 minutes
        endTime=50,   # 50 days
        outputPath=""
    )
    
    config = SimulationConfig(
        name="BSM2 Open Loop Test",
        description="BSM2 open loop test case for comparison",
        nodes=nodes,
        edges=edges,
        settings=settings
    )
    
    return config

def run_original_bsm2():
    """Run the original BSM2_ol implementation."""
    logger.info("Running original BSM2_ol implementation...")
    
    bsm2_ol = BSM2OL(endtime=50, timestep=15 / 60 / 24, tempmodel=False, activate=False)
    
    start = time.perf_counter()
    for idx, _ in enumerate(tqdm(bsm2_ol.simtime, desc="Original BSM2")):
        bsm2_ol.step(idx)
    stop = time.perf_counter()
    
    logger.info(f'Original BSM2 simulation completed after: {stop - start:.2f} seconds')
    logger.info(f'Final effluent: {bsm2_ol.y_eff_all[-1, :]}')
    
    return {
        'time': bsm2_ol.simtime,
        'effluent': bsm2_ol.y_eff_all,
        'influent': bsm2_ol.y_in_all,
        'reactor1': bsm2_ol.y_out1_all,
        'reactor2': bsm2_ol.y_out2_all,
        'reactor3': bsm2_ol.y_out3_all,
        'reactor4': bsm2_ol.y_out4_all,
        'reactor5': bsm2_ol.y_out5_all,
        'settler_recycle': bsm2_ol.ys_r_all,
        'settler_waste': bsm2_ol.ys_was_all,
        'settler_effluent': bsm2_ol.ys_of_all,
        'primary_uf': bsm2_ol.yp_uf_all,
        'primary_of': bsm2_ol.yp_of_all,
        'thickener_uf': bsm2_ol.yt_uf_all,
        'adm1_out': bsm2_ol.yi_out2_all,
        'storage_out': bsm2_ol.yst_out_all,
        'dewatering_s': bsm2_ol.ydw_s_all,
        'simulation_time': stop - start
    }

async def run_json_simulation():
    """Run our JSON-based simulation engine."""
    logger.info("Running JSON parsing simulation engine...")
    
    config = load_bsm2_json_config()
    engine = SimulationEngine()
    
    start = time.perf_counter()
    try:
        results = await engine.run_simulation(config)
        stop = time.perf_counter()
        
        logger.info(f'JSON simulation completed after: {stop - start:.2f} seconds')
        
        return {
            'success': results['success'],
            'time': results['time'],
            'influent': results['influent'],
            'components': results['components'],
            'simulation_time': stop - start
        }
    except Exception as e:
        stop = time.perf_counter()
        logger.error(f'JSON simulation failed after: {stop - start:.2f} seconds: {e}')
        return {
            'success': False,
            'error': str(e),
            'simulation_time': stop - start
        }

def compare_results(original_results, json_results):
    """Compare the results from both implementations."""
    logger.info("\n=== COMPARISON RESULTS ===")
    
    if not json_results['success']:
        logger.error(f"JSON simulation failed: {json_results['error']}")
        return
    
    # Compare simulation times
    logger.info(f"Original simulation time: {original_results['simulation_time']:.2f}s")
    logger.info(f"JSON simulation time: {json_results['simulation_time']:.2f}s")
    
    # Compare final effluent values
    original_final_effluent = original_results['effluent'][-1, :]
    
    # Find effluent component in JSON results
    json_effluent = None
    for comp_id, comp_data in json_results['components'].items():
        if 'effluent' in comp_id.lower() or 'combiner' in comp_id.lower():
            json_effluent = comp_data[-1] if isinstance(comp_data[-1], np.ndarray) else np.array(comp_data[-1])
            break
    
    if json_effluent is not None:
        logger.info(f"\nOriginal final effluent: {original_final_effluent}")
        logger.info(f"JSON final effluent: {json_effluent}")
        
        # Calculate differences
        abs_diff = np.abs(original_final_effluent - json_effluent)
        rel_diff = abs_diff / (np.abs(original_final_effluent) + 1e-10) * 100
        
        logger.info(f"Absolute differences: {abs_diff}")
        logger.info(f"Relative differences (%): {rel_diff}")
        
        # Check if they match within tolerance
        if np.allclose(original_final_effluent, json_effluent, rtol=0.3, atol=1.0):
            logger.info("✅ Results match within tolerance!")
        else:
            logger.warning("❌ Results do not match!")
            
        # Show largest differences
        max_diff_idx = np.argmax(abs_diff)
        logger.info(f"Largest absolute difference: component {max_diff_idx}, diff={abs_diff[max_diff_idx]:.6f}")
        
        max_rel_idx = np.argmax(rel_diff)
        logger.info(f"Largest relative difference: component {max_rel_idx}, diff={rel_diff[max_rel_idx]:.2f}%")
    else:
        logger.error("Could not find effluent data in JSON results")
    
    # Compare component structure
    logger.info(f"\nOriginal components: {len(original_results)} variables")
    logger.info(f"JSON components: {len(json_results['components'])} components")
    
    # List JSON components
    logger.info("\nJSON components found:")
    for comp_id, comp_data in json_results['components'].items():
        if isinstance(comp_data, list) and len(comp_data) > 0:
            sample = comp_data[0]
            if isinstance(sample, np.ndarray):
                logger.info(f"  {comp_id}: {len(comp_data)} timesteps, shape {sample.shape}")
            elif isinstance(sample, dict):
                logger.info(f"  {comp_id}: {len(comp_data)} timesteps, keys {list(sample.keys())}")
            else:
                logger.info(f"  {comp_id}: {len(comp_data)} timesteps, type {type(sample)}")

if __name__ == "__main__":
    import asyncio
    
    # Run both simulations
    original_results = run_original_bsm2()
    json_results = asyncio.run(run_json_simulation())
    
    # Compare results
    compare_results(original_results, json_results)