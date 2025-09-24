from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List

@dataclass
class EdgeRef:
    id: str
    source_node_id: str
    source_handle_id: str
    target_node_id: str
    target_handle_id: str

@dataclass
class NodeDC:
    id: str
    component_type_id: str
    label: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    in_edges: List[EdgeRef] = field(default_factory=list)
    out_edges: List[EdgeRef] = field(default_factory=list)
    instance: Any = None  # Adapter mit step(dt, inputs) -> outputs