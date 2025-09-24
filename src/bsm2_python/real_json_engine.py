"""
Advanced JSON-based simulation engine for general-purpose WWTP simulations.

This implementation uses the new engine architecture with graph scheduling,
parameter resolution, and component adapters.
"""

import sys
import os

# Add engine path for imports
engine_path = os.path.join(os.path.dirname(__file__), 'engine')
sys.path.insert(0, engine_path)

from engine import SimulationEngine

class JSONSimulationEngine:
    """
    Advanced JSON simulation engine for WWTP configurations.
    
    This engine can handle any WWTP layout defined in JSON, using
    a sophisticated graph-based approach with cycle detection and
    proper scheduling.
    """
    
    def __init__(self, config):
        if isinstance(config, str):
            # Load from file
            import json
            with open(config, 'r') as f:
                config_data = json.load(f)
        else:
            config_data = config
            
        # Create the advanced engine
        self.engine = SimulationEngine(config_data)
        
    def simulate(self):
        """Run simulation and return results compatible with the old engine."""
        return self.engine.simulate()
        
    def get_effluent(self):
        """Get final effluent values."""
        return getattr(self.engine, 'ys_eff', None)
    
    def get_sludge_height(self):
        """Get sludge height."""
        return getattr(self.engine, 'sludge_height', 0.0)
    
    def get_tss_internal(self):
        """Get TSS internal profile."""
        return getattr(self.engine, 'ys_tss_internal', None)