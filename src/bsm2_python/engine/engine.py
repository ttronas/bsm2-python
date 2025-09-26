from __future__ import annotations
import json
from typing import Dict, Any, List
import numpy as np

from .scheduler import schedule
from .param_resolver import resolve_params
from .nodes import NodeDC, EdgeRef, HandleDC
from .registry import REGISTRY


class SimulationEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config

        def _flatten_handle_section(sec):
            # sec kann {} (neu, gruppiert), [] (alt) oder None sein
            if isinstance(sec, dict):
                items = []
                for _, lst in sec.items():
                    if isinstance(lst, list):
                        items.extend(lst)
                return items
            elif isinstance(sec, list):
                return sec
            else:
                return []

        # Nodes aus JSON inklusive Handle-Definitionen aufbauen
        self.nodes: Dict[str, NodeDC] = {}
        for n in config["nodes"]:
            handles = (n.get("data") or {}).get("handles") or {}
            in_defs: List[HandleDC] = [
                HandleDC(id=h["id"], position=h.get("position", 0))
                for h in _flatten_handle_section(handles.get("inputs"))
            ]
            out_defs: List[HandleDC] = [
                HandleDC(id=h["id"], position=h.get("position", 0))
                for h in _flatten_handle_section(handles.get("outputs"))
            ]
            self.nodes[n["id"]] = NodeDC(
                id=n["id"],
                component_type_id=n["component_type_id"],
                label=n.get("label", n["id"]),
                parameters=n.get("parameters", {}),
                input_handles=in_defs,
                output_handles=out_defs
            )

        # Edges mappen und gegen Handle-Definitionen validieren
        for e in config["edges"]:
            eref = EdgeRef(
                id=e["id"],
                source_node_id=e["source_node_id"],
                source_handle_id=e["source_handle_id"],
                target_node_id=e["target_node_id"],
                target_handle_id=e["target_handle_id"],
            )
            src = self.nodes.get(eref.source_node_id)
            tgt = self.nodes.get(eref.target_node_id)
            if src is None or tgt is None:
                raise KeyError(
                    f"Edge {eref.id} references unknown node(s): "
                    f"{eref.source_node_id}->{eref.target_node_id}"
                )
            if not src.has_output_handle(eref.source_handle_id):
                raise ValueError(
                    f"Edge {eref.id} uses unknown source handle "
                    f"'{eref.source_handle_id}' on node '{src.id}'"
                )
            if not tgt.has_input_handle(eref.target_handle_id):
                raise ValueError(
                    f"Edge {eref.id} uses unknown target handle "
                    f"'{eref.target_handle_id}' on node '{tgt.id}'"
                )
            src.out_edges.append(eref)
            tgt.in_edges.append(eref)

        # Schnelle In-/Out-Adjazenzlisten direkt aus NodeDC erzeugen
        self.in_edges_by_node: Dict[str, List[Dict[str, Any]]] = {}
        self.out_edges_by_node: Dict[str, List[Dict[str, Any]]] = {}
        for nid, nd in self.nodes.items():
            self.in_edges_by_node[nid] = [{
                "id": e.id,
                "source_node_id": e.source_node_id,
                "source_handle_id": e.source_handle_id,
                "target_node_id": e.target_node_id,
                "target_handle_id": e.target_handle_id,
            } for e in nd.in_edges]
            self.out_edges_by_node[nid] = [{
                "id": e.id,
                "source_node_id": e.source_node_id,
                "source_handle_id": e.source_handle_id,
                "target_node_id": e.target_node_id,
                "target_handle_id": e.target_handle_id,
            } for e in nd.out_edges]

        # Ausführungsplan berechnen
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

        # DEBUG: Plan ausgeben
        for i, stage in enumerate(self.plan["stages"]):
            if stage["type"] == "acyclic":
                print(f"  Stage {i}: ACYCLIC - Order: {stage['order']}")
            else:
                print(f"  Stage {i}: LOOP - Nodes: {stage['nodes']}")
                print(f"           Internal Order: {stage['internal_order']}")
                print(f"           Tear Edges: {stage['tear_edges']}")

    @classmethod
    def from_json(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)

    def _collect_inputs(self, nid: str) -> Dict[str, np.ndarray]:
        inputs: Dict[str, np.ndarray] = {}
        for e in self.in_edges_by_node.get(nid, []):
            edge_id = e["id"]
            val = self.edge_values.get(edge_id)
            if val is not None:
                inputs[e["target_handle_id"]] = val
            else:
                # Nicht-tear Edges bei erstem Zugriff mit Nullen initialisieren
                self.edge_values[edge_id] = np.zeros(21, dtype=float)
                inputs[e["target_handle_id"]] = self.edge_values[edge_id]
        return inputs

    def _write_outputs(self, nid: str, outputs: Dict[str, np.ndarray]):
        # Outputs werden anhand der definierten Out-Edges mit passendem Handle geschrieben
        for e in self.out_edges_by_node.get(nid, []):
            src_handle = e["source_handle_id"]
            if src_handle in outputs:
                self.edge_values[e["id"]] = outputs[src_handle]

    def _sweep_order(self, node_ids: List[str], dt: float, current_step: int = 0):
        for nid in node_ids:
            nd = self.nodes[nid]
            inst = nd.instance
            inputs = self._collect_inputs(nid)

            try:
                # Alle Komponenten verwenden step(dt, current_step, inputs)
                outputs = inst.step(dt, current_step, inputs) or {}
                self._write_outputs(nid, outputs)
            except Exception as e:
                print(f"ERROR in {nid}: {e}")
                raise

    def _loop_iterate(
        self,
        component_nodes: List[str],
        internal_order: List[str],
        tear_edge_ids: List[str],
        dt: float,
        current_step: int = 0,
        tol: float = 1e-3,
        max_iter: int = 5,
        relax: float = 0.7
    ):
        # Nur Tear-Edges initialisieren (Kopie einer plausiblen Anfangszusammensetzung)
        for eid in tear_edge_ids:
            if eid not in self.edge_values:
                influent_composition = np.array([
                    30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56,
                    6.95, 10.59, 7, 211.2675, 18446, 15, 0, 0, 0, 0, 0
                ], dtype=float)
                self.edge_values[eid] = influent_composition.copy()

        for _ in range(max_iter):
            prev = {eid: self.edge_values[eid].copy() for eid in tear_edge_ids}
            self._sweep_order(internal_order, dt, current_step)

            # Konvergenz prüfen und Relaxation anwenden
            max_res = 0.0
            for eid in tear_edge_ids:
                new_val = self.edge_values.get(eid, prev[eid])
                res = float(np.max(np.abs(new_val - prev[eid])))
                self.edge_values[eid] = (1 - relax) * prev[eid] + relax * new_val
                max_res = max(max_res, res)

            if max_res < tol:
                break

    def step_steady(self, dt: float, current_step: int = 0):
        for st in self.plan["stages"]:
            if st["type"] == "acyclic":
                self._sweep_order(st["order"], dt, current_step)
            else:
                self._loop_iterate(
                    st["nodes"], st["internal_order"], st["tear_edges"], dt, current_step
                )

    def simulate_steady(self, timestep: float, endtime: float):
        steps = int(round(endtime / timestep))

        # Ergebnisse (Kompatibilität)
        self.ys_eff = None
        self.sludge_height = None
        self.ys_tss_internal = None

        for i in range(steps):
            self.step_steady(timestep, i)

        # Finalwerte extrahieren
        effluent_node = None
        settler_node = None

        for nid, node in self.nodes.items():
            if node.component_type_id == "effluent":
                effluent_node = node
            elif node.component_type_id == "settler":
                settler_node = node

        if effluent_node and hasattr(effluent_node.instance, "last"):
            self.ys_eff = effluent_node.instance.last
            print(f"\n📊 Final effluent from node: {self.ys_eff[:5] if self.ys_eff is not None else 'None'}")
        else:
            self.ys_eff = np.zeros(21)
            print(f"\n📊 Using default effluent (no effluent node found)")

        if settler_node and hasattr(settler_node.instance, "sludge_height"):
            self.sludge_height = settler_node.instance.sludge_height
            self.ys_tss_internal = settler_node.instance.ys_tss_internal
            print(f"📊 Settler sludge height: {self.sludge_height}")
            print(f"📊 Settler TSS internal: {self.ys_tss_internal[:5] if self.ys_tss_internal is not None else 'None'}")
        else:
            self.sludge_height = 0.0
            self.ys_tss_internal = np.zeros(10)
            print(f"📊 Using default settler values (no settler node or data found)")

    def simulate(self):
        """Run simulation and return results compatible with real_json_engine."""
        timestep = 15 / (60 * 24)  # 15 minutes in days
        endtime = 20  # days - shorter for debugging

        print(f"\n🎯 Simulation Configuration:")
        print(f"   Timestep: {timestep:.6f} days ({timestep*24*60:.1f} minutes)")
        print(f"   End time: {endtime} days")
        print(f"   Nodes: {len(self.nodes)}")
        print(f"   Edges: {len(self.config.get('edges', []))}")

        self.simulate_steady(timestep, endtime)

        return {
            "effluent": self.ys_eff,
            "sludge_height": self.sludge_height,
            "tss_internal": self.ys_tss_internal,
        }