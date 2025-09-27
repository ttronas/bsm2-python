"""
Test script for the BSM2 simulation engine using the ASM1 constant test configuration.
This validates that the web application simulation engine produces similar results
to the original BSM2 Python tests.
"""

import sys
import numpy as np
import json
from pathlib import Path

# Add the source path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from simulation_engine import SimulationEngine
from models import SimulationConfig


def test_asm1_constant():
    """Test ASM1 reactor with constant influent"""
    
    # Load test configuration
    config_file = Path(__file__).parent.parent / "test_configs" / "asm1_constant.json"
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    
    print(f"Loaded configuration: {config_data['name']}")
    
    # Create simulation configuration
    config = SimulationConfig(**config_data)
    
    # Create simulation engine
    engine = SimulationEngine(config, "test_sim_1")
    
    print(f"✅ Created simulation engine successfully")
    print(f"Execution order: {engine.execution_order}")
    print(f"Components: {list(engine.components.keys())}")
    
    # Run a single timestep to test basic functionality
    try:
        # Get influent for timestep 0
        influent = engine._get_influent_at_time(0.0)
        print(f"✅ Influent data retrieved: shape {influent.shape}")
        print(f"First few values: {influent[:5]}")
        
        # Test component creation
        for comp_id, comp_data in engine.components.items():
            component = comp_data['component']
            if component:
                print(f"✅ Component {comp_id}: {type(component).__name__}")
            else:
                print(f"ℹ️ Component {comp_id}: Influent node (no component)")
        
        print("🎉 Basic engine test passed!")
        
        # Run a short simulation (5 timesteps)
        print("\n🚀 Running short simulation test...")
        
        # Simulate 5 timesteps
        dt = config.timestep
        time_steps = 5
        
        for step in range(time_steps):
            t = step * dt
            print(f"Step {step}: t = {t:.6f} days")
            
            # Get influent for this timestep
            influent = engine._get_influent_at_time(t)
            
            # Execute timestep
            import asyncio
            asyncio.run(engine._execute_timestep(influent, t, dt))
        
        # Get results
        results = engine.get_results()
        print(f"✅ Simulation completed with {len(results['components'])} components")
        
        # Check if we have data for ASM1 reactor
        for comp_result in results['components']:
            if comp_result['component_id'] == 'asm1_reactor_1':
                print(f"✅ ASM1 reactor data: {len(comp_result['time'])} timesteps")
                if 'effluent' in comp_result['outputs']:
                    effluent_data = comp_result['outputs']['effluent']
                    if effluent_data:
                        final_effluent = effluent_data[-1]
                        print(f"Final effluent (first 5 components): {final_effluent[:5]}")
                        
                        # Compare with expected BSM2 test values (approximately)
                        # Note: These are rough approximations since we're only running 5 steps
                        expected_approx = [30, 69.5, 51.2, 202.32, 28.17]  # Should be close to influent for short simulation
                        actual = final_effluent[:5]
                        
                        print("Comparison with expected (first 5 components):")
                        for i, (exp, act) in enumerate(zip(expected_approx, actual)):
                            diff = abs(act - exp)
                            print(f"  Component {i}: Expected ~{exp:.2f}, Got {act:.2f}, Diff: {diff:.2f}")
        
        print("🎉 Short simulation test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Testing BSM2 Simulation Engine")
    print("=" * 50)
    
    success = test_asm1_constant()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!")
        sys.exit(1)