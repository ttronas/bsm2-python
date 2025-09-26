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
class HandleDC:
    id: str
    position: int = 0

@dataclass
class NodeDC:
    id: str
    component_type_id: str
    label: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    input_handles: List[HandleDC] = field(default_factory=list)
    output_handles: List[HandleDC] = field(default_factory=list)
    in_edges: List[EdgeRef] = field(default_factory=list)
    out_edges: List[EdgeRef] = field(default_factory=list)
    instance: Any = None  # Adapter mit step(dt, inputs) -> outputs

    def has_input_handle(self, handle_id: str) -> bool:
        """Check if this node has an input handle with the given ID."""
        return any(h.id == handle_id for h in self.input_handles)

    def has_output_handle(self, handle_id: str) -> bool:
        """Check if this node has an output handle with the given ID."""
        return any(h.id == handle_id for h in self.output_handles)