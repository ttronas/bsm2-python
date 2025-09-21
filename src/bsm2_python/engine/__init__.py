# src/bsm2_python/engine/__init__.py
"""
General-purpose simulation engine for WWTP configurations.

This engine implements a graph-based approach with SCC detection and cycle handling.
"""

from .engine import SimulationEngine
from .scheduler import schedule
from .param_resolver import resolve_params, resolve_value
from .registry import REGISTRY, register

__all__ = ['SimulationEngine', 'schedule', 'resolve_params', 'resolve_value', 'REGISTRY', 'register']