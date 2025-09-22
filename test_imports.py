#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Test imports directly without the main package
try:
    import numpy as np
    print("✓ numpy imported")
    
    # Test individual BSM2 components
    from bsm2_python.bsm2.module import Module
    print("✓ Module imported")
    
    # Try to import the specific components
    from bsm2_python.bsm2.helpers_bsm2 import Combiner, Splitter
    print("✓ Combiner, Splitter imported")
    
    from bsm2_python.bsm2.init import asm1init_bsm1
    print("✓ asm1init imported")
    
    # Test parameter resolution
    from bsm2_python.engine.param_resolver import resolve_value, resolve_params
    print("✓ param_resolver imported")
    
    test_val = resolve_value("asm1init.KLA1")
    print(f"✓ param resolution test: asm1init.KLA1 = {test_val}")
    
    # Test registry without ASM1Reactor for now
    from bsm2_python.engine.nodes import NodeDC, EdgeRef
    print("✓ nodes imported")
    
    from bsm2_python.engine.scheduler import schedule, build_graph
    print("✓ scheduler imported")
    
    print("\nAll basic imports successful!")
    
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()