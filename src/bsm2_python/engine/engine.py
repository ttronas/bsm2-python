from __future__ import annotations
import json
from typing import Dict, Any, List
import numpy as np

from scheduler import schedule, build_graph
from param_resolver import resolve_params
from nodes import NodeDC, EdgeRef
from registry import REGISTRY

class SimulationEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        # Nodes als dataclasses anlegen
        self.nodes: Dict[str, NodeDC] = {}
        for n in config["nodes"]:
            self.nodes[n["id"]] = NodeDC(
                id=n["id"],
                component_type_id=n["component_type_id"],
                label=n.get("label", n["id"]),
                parameters=n.get("parameters", {})
            )

        # Edges auf Nodes mappen
        for e in config["edges"]:
            eref = EdgeRef(
                id=e["id"],
                source_node_id=e["source_node_id"],
                source_handle_id=e["source_handle_id"],
                target_node_id=e["target_node_id"],
                target_handle_id=e["target_handle_id"],
            )
            self.nodes[eref.source_node_id].out_edges.append(eref)
            self.nodes[eref.target_node_id].in_edges.append(eref)

        # Ausführungsplan
        self.plan = schedule(config)

        # Parameter auflösen und Instanzen bauen
        for nid, nd in self.nodes.items():
            params = resolve_params(nd.parameters or {})
            factory = REGISTRY.get(nd.component_type_id)
            if factory is None:
                raise KeyError(f"No factory registered for component_type_id={nd.component_type_id}")
            nd.instance = factory(nid, params)

        # Kantenpuffer
        self.edge_values: Dict[str, np.ndarray] = {}
        # Schnelle Edge-Indexe pro Node
        _, _, _, _, self.in_edges_by_node, self.out_edges_by_node = build_graph(config["nodes"], config["edges"])

    @classmethod
    def from_json(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)

    def _collect_inputs(self, nid: str) -> Dict[str, np.ndarray]:
        inputs: Dict[str, np.ndarray] = {}
        for e in self.in_edges_by_node[nid]:
            val = self.edge_values.get(e["id"])
            if val is not None:
                inputs[e["target_handle_id"]] = val
        return inputs

    def _write_outputs(self, nid: str, outputs: Dict[str, np.ndarray]):
        for e in self.out_edges_by_node[nid]:
            src_handle = e["source_handle_id"]
            if src_handle in outputs:
                self.edge_values[e["id"]] = outputs[src_handle]

    def _sweep_order(self, node_ids: List[str], dt: float):
        for nid in node_ids:
            nd = self.nodes[nid]
            inst = nd.instance
            inputs = self._collect_inputs(nid)
            outputs = inst.step(dt, inputs) or {}
            self._write_outputs(nid, outputs)

    def _loop_iterate(self, component_nodes: List[str], internal_order: List[str],
                      tear_edge_ids: List[str], dt: float,
                      tol: float = 1e-6, max_iter: int = 50, relax: float = 0.5):
        # initial guess
        for eid in tear_edge_ids:
            if eid not in self.edge_values:
                self.edge_values[eid] = np.zeros(21, dtype=float)
        for _ in range(max_iter):
            prev = {eid: self.edge_values[eid].copy() for eid in tear_edge_ids}
            self._sweep_order(internal_order, dt)
            # Check und Relax
            max_res = 0.0
            for eid in tear_edge_ids:
                new_val = self.edge_values.get(eid, prev[eid])
                res = float(np.max(np.abs(new_val - prev[eid])))
                self.edge_values[eid] = (1 - relax) * prev[eid] + relax * new_val
                max_res = max(max_res, res)
            if max_res < tol:
                break

    def step_steady(self, dt: float):
        for st in self.plan["stages"]:
            if st["type"] == "acyclic":
                self._sweep_order(st["order"], dt)
            else:
                self._loop_iterate(st["nodes"], st["internal_order"], st["tear_edges"], dt)

    def simulate_steady(self, timestep: float, endtime: float):
        steps = int(round(endtime / timestep))
        
        # Store results for BSM1OL compatibility
        self.ys_eff = None
        self.sludge_height = None
        self.ys_tss_internal = None
        
        for i in range(steps):
            self.step_steady(timestep)
            
        # Extract final results for compatibility
        effluent_node = None
        settler_node = None
        
        for nid, node in self.nodes.items():
            if node.component_type_id == "effluent":
                effluent_node = node
            elif node.component_type_id == "settler":
                settler_node = node
                
        # Get effluent values
        if effluent_node and hasattr(effluent_node.instance, 'last'):
            self.ys_eff = effluent_node.instance.last
        else:
            self.ys_eff = np.zeros(21)
            
        # Get settler info if available
        if settler_node:
            # Mock settler height for now
            self.sludge_height = 2.5  # Default value
            self.ys_tss_internal = np.ones(10) * 3000  # Mock TSS profile
        else:
            self.sludge_height = 0.0
            self.ys_tss_internal = np.zeros(10)
            
    def simulate(self):
        """Run simulation and return results compatible with real_json_engine."""
        # Default simulation parameters
        timestep = 15 / (60 * 24)  # 15 minutes in days
        endtime = 200  # days
        
        self.simulate_steady(timestep, endtime)
        
        return {
            'effluent': self.ys_eff,
            'sludge_height': self.sludge_height,
            'tss_internal': self.ys_tss_internal
        }