#!/usr/bin/env python3
import sys
import os
import importlib.util
import numpy as np

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, src_path)

# Import specific modules without triggering the full package load
def load_module(module_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

try:
    # Manually load Module base class
    module_path = os.path.join(src_path, 'bsm2_python/bsm2/module.py')
    module_module = load_module(module_path, 'bsm2_python.bsm2.module')
    Module = module_module.Module
    print("✓ Module loaded")
    
    # Load helpers manually
    helpers_path = os.path.join(src_path, 'bsm2_python/bsm2/helpers_bsm2.py')
    helpers_module = load_module(helpers_path, 'bsm2_python.bsm2.helpers_bsm2')
    Combiner = helpers_module.Combiner
    Splitter = helpers_module.Splitter
    print("✓ Combiner, Splitter loaded")
    
    # Load asm1init manually
    asm1init_path = os.path.join(src_path, 'bsm2_python/bsm2/init/asm1init_bsm1.py')
    asm1init_module = load_module(asm1init_path, 'bsm2_python.bsm2.init.asm1init_bsm1')
    print(f"✓ asm1init loaded, KLA1={asm1init_module.KLA1}")
    
    # Test our engine modules
    from bsm2_python.engine.param_resolver import resolve_value, resolve_params
    from bsm2_python.engine.nodes import NodeDC, EdgeRef
    from bsm2_python.engine.scheduler import schedule, build_graph
    print("✓ All engine modules loaded")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()