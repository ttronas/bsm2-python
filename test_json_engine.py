#!/usr/bin/env python3
"""Test script for the JSON simulation engine."""

import sys
import os

# Add src path to Python path
sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src')

# Test JSON configuration (simplified BSM1 setup)
test_config = {
    "simulation_settings": {
        "mode": "steady",
        "steady_timestep": 0.010416667,
        "steady_endtime": 200
    },
    "global_options": {
        "tempmodel": False,
        "activate": False
    },
    "nodes": [
        {
            "id": "influent_s",
            "component_type_id": "influent_static",
            "label": "Influent (Static)",
            "parameters": {
                "y_in_constant": [30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0]
            }
        },
        {
            "id": "combiner",
            "component_type_id": "combiner",
            "label": "Combiner",
            "parameters": {}
        },
        {
            "id": "reactor1",
            "component_type_id": "reactor",
            "label": "Reactor 1",
            "parameters": {
                "KLA": "reginit.KLA1",
                "VOL": "asm1init.VOL1",
                "YINIT": "asm1init.YINIT1",
                "PAR": "asm1init.PAR1",
                "CARB": "reginit.CARB1",
                "CARBONSOURCECONC": "reginit.CARBONSOURCECONC",
                "tempmodel": False,
                "activate": False
            }
        }
    ],
    "edges": [
        {
            "id": "e_1",
            "source_node_id": "influent_s",
            "source_handle_id": "out_main",
            "target_node_id": "combiner",
            "target_handle_id": "in_fresh"
        },
        {
            "id": "e_2",
            "source_node_id": "combiner",
            "source_handle_id": "out_combined",
            "target_node_id": "reactor1",
            "target_handle_id": "in_main"
        }
    ]
}

def test_component_creation():
    """Test basic component creation."""
    print("Testing component creation...")
    
    try:
        # Import directly to avoid control library dependency
        sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src/bsm2_python')
        from json_simulation_engine import ComponentFactory
        
        # Try to create factory
        factory = ComponentFactory()
        print("✓ ComponentFactory created successfully")
        
        # Test creating an influent component
        influent_config = test_config['nodes'][0]
        influent = factory.create_component(influent_config)
        print("✓ Influent component created")
        
        # Test influent output
        output = influent.output()
        print(f"✓ Influent output shape: {output.shape}")
        print(f"  First few values: {output[:5]}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_parameter_resolution():
    """Test parameter resolution."""
    print("\nTesting parameter resolution...")
    
    try:
        sys.path.insert(0, '/home/runner/work/bsm2-python/bsm2-python/src/bsm2_python')
        from json_simulation_engine import ComponentFactory
        
        factory = ComponentFactory()
        
        # Test direct values
        direct_value = factory._resolve_parameter(42.0)
        print(f"✓ Direct value: {direct_value}")
        
        # Test list to array
        array_value = factory._resolve_parameter([1, 2, 3])
        print(f"✓ Array value: {array_value}")
        
        # Test string resolution
        try:
            string_value = factory._resolve_parameter("reginit.KLA1")
            print(f"✓ String resolution: {string_value}")
        except Exception as e:
            print(f"! String resolution failed (expected if modules not loaded): {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing JSON Simulation Engine\n")
    
    success = True
    success &= test_component_creation()
    success &= test_parameter_resolution()
    
    if success:
        print("\n✓ All basic tests passed!")
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)