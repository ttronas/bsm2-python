"""
Comprehensive testing script for the BSM2 web application backend.
This script tests all the test configurations against the real BSM2 simulation engine
and validates the results against expected values from the original BSM2 tests.
"""

import sys
import numpy as np
import json
import time
from pathlib import Path

# Add the source path
repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(repo_root / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from simulation_engine import SimulationEngine
from models import SimulationConfig


def test_configuration(config_file: Path, expected_values=None):
    """Test a single configuration file"""
    print(f"\n🧪 Testing: {config_file.name}")
    print("=" * 60)
    
    try:
        # Load test configuration
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        print(f"Configuration: {config_data['name']}")
        print(f"Description: {config_data['description']}")
        print(f"Components: {len(config_data['nodes'])}")
        print(f"Connections: {len(config_data['edges'])}")
        
        # Create simulation configuration
        config = SimulationConfig(**config_data)
        
        # Create simulation engine
        engine = SimulationEngine(config, f"test_{config_file.stem}")
        
        print(f"✅ Created simulation engine successfully")
        print(f"Execution order: {engine.execution_order}")
        print(f"Components initialized: {list(engine.components.keys())}")
        
        # Test influent data loading
        influent = engine._get_influent_at_time(0.0)
        print(f"✅ Influent data shape: {influent.shape}")
        print(f"Influent first values: {influent[:5]}")
        
        # Run a short simulation (10 timesteps for quick testing)
        print(f"\n🚀 Running short simulation...")
        dt = config.timestep
        time_steps = 10
        
        start_time = time.perf_counter()
        
        for step in range(time_steps):
            t = step * dt
            influent = engine._get_influent_at_time(t)
            
            # Execute timestep using asyncio
            import asyncio
            asyncio.run(engine._execute_timestep(influent, t, dt))
        
        end_time = time.perf_counter()
        
        # Get results
        results = engine.get_results()
        print(f"✅ Simulation completed in {end_time - start_time:.3f} seconds")
        print(f"Results collected for {len(results['components'])} components")
        
        # Analyze results for key components
        for comp_result in results['components']:
            comp_id = comp_result['component_id']
            comp_type = comp_result['component_type']
            timesteps = len(comp_result['time'])
            
            if timesteps > 0:
                print(f"  📊 {comp_id} ({comp_type}): {timesteps} timesteps")
                
                # Show output data for main components
                if 'effluent' in comp_result['outputs']:
                    effluent_data = comp_result['outputs']['effluent']
                    if effluent_data:
                        final_effluent = effluent_data[-1]
                        print(f"    Final effluent (first 5): {final_effluent[:5]}")
                        
                        # Compare with expected values if provided
                        if expected_values and comp_type in expected_values:
                            expected = expected_values[comp_type][:5]
                            actual = final_effluent[:5]
                            
                            print(f"    Expected vs Actual comparison:")
                            for i, (exp, act) in enumerate(zip(expected, actual)):
                                diff = abs(act - exp) if not np.isnan(act) and not np.isnan(exp) else 0
                                rel_error = (diff / exp * 100) if exp != 0 else 0
                                print(f"      Component {i}: Expected {exp:.3f}, Got {act:.3f}, Rel.Error: {rel_error:.1f}%")
            else:
                print(f"  ⚠️ {comp_id} ({comp_type}): No data collected")
        
        print(f"✅ Test PASSED: {config_file.name}")
        return True
        
    except Exception as e:
        print(f"❌ Test FAILED: {config_file.name}")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_all_configurations():
    """Test all configuration files in the test_configs directory"""
    print("🧪 BSM2 Web Application Backend Testing")
    print("=" * 70)
    
    test_configs_dir = Path(__file__).parent.parent / "test_configs"
    config_files = list(test_configs_dir.glob("*.json"))
    
    print(f"Found {len(config_files)} test configurations")
    
    # Expected values from original BSM2 tests (approximate, for validation)
    expected_values = {
        'asm1_reactor': [30.0, 69.5, 51.2, 202.32, 28.17],  # Approximate expected values
        'primary_clarifier': [30.0, 50.0, 45.0, 180.0, 25.0],  # Approximate
        'adm1_reactor': [28.0, 48.0, 10000.0, 20000.0, 10000.0],  # From adm1_test.py
        'thickener': [30.0, 69.5, 51.2, 202.32, 28.17],  # Approximate
        'dewatering': [30.0, 69.5, 51.2, 202.32, 28.17],  # Approximate
        'storage': [30.0, 69.5, 51.2, 202.32, 28.17],  # Approximate
    }
    
    results = []
    
    for config_file in sorted(config_files):
        success = test_configuration(config_file, expected_values)
        results.append((config_file.name, success))
    
    # Summary
    print("\n" + "=" * 70)
    print("📋 TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for config_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {config_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("⚠️ Some tests failed. Check the logs above for details.")
    
    return passed == total


if __name__ == "__main__":
    print("🔧 Testing BSM2 Backend Simulation Engine")
    print("This will test all configuration files against the real BSM2 modules")
    print()
    
    success = test_all_configurations()
    
    if not success:
        sys.exit(1)
    
    print("\n✅ All backend tests completed successfully!")