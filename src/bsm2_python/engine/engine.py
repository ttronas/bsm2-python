from __future__ import annotations
import json
from typing import Dict, Any, List
import numpy as np

from .scheduler import schedule, build_graph
from .param_resolver import resolve_params
from .nodes import NodeDC, EdgeRef
from .registry import REGISTRY

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
        
        # DEBUG: Print execution plan
        print(f"\n🔍 DEBUG: Execution Plan:")
        for i, stage in enumerate(self.plan["stages"]):
            if stage["type"] == "acyclic":
                print(f"  Stage {i}: ACYCLIC - Order: {stage['order']}")
            else:
                print(f"  Stage {i}: LOOP - Nodes: {stage['nodes']}")
                print(f"           Internal Order: {stage['internal_order']}")
                print(f"           Tear Edges: {stage['tear_edges']}")

        # Parameter auflösen und Instanzen bauen
        for nid, nd in self.nodes.items():
            params = resolve_params(nd.parameters or {})
            factory = REGISTRY.get(nd.component_type_id)
            if factory is None:
                raise KeyError(f"No factory registered for component_type_id={nd.component_type_id}")
            nd.instance = factory(nid, params)

        # Kantenpuffer - NEW APPROACH: Only initialize tear edges, others start as zeros
        self.edge_values: Dict[str, np.ndarray] = {}
        
        # Schnelle Edge-Indexe pro Node
        _, _, _, _, self.in_edges_by_node, self.out_edges_by_node = build_graph(config["nodes"], config["edges"])
        
        # NEW: Only initialize tear edges during loop iteration, not all edges upfront
        print(f"\n🔍 DEBUG: Edge initialization strategy changed - only tear edges will be initialized")


    @classmethod
    def from_json(cls, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)

    def _collect_inputs(self, nid: str) -> Dict[str, np.ndarray]:
        inputs: Dict[str, np.ndarray] = {}
        for e in self.in_edges_by_node[nid]:
            edge_id = e["id"]
            val = self.edge_values.get(edge_id)
            if val is not None:
                inputs[e["target_handle_id"]] = val
                # DEBUG: Show what inputs are being collected
                print(f"    Input {e['target_handle_id']}: Q={val[14]:.1f}, TSS={val[13]:.1f}")
            else:
                # Initialize non-tear edges with zeros when first accessed
                self.edge_values[edge_id] = np.zeros(21, dtype=float)
                inputs[e["target_handle_id"]] = self.edge_values[edge_id]
                print(f"    Input {e['target_handle_id']}: initialized with zeros")
        return inputs

    def _write_outputs(self, nid: str, outputs: Dict[str, np.ndarray]):
        for e in self.out_edges_by_node[nid]:
            src_handle = e["source_handle_id"]
            if src_handle in outputs:
                old_flow = self.edge_values.get(e["id"], np.zeros(21))[14]
                self.edge_values[e["id"]] = outputs[src_handle]
                new_flow = outputs[src_handle][14]
                # DEBUG: Show flow changes
                print(f"    Output {src_handle}: Q {old_flow:.1f} -> {new_flow:.1f}")

    def _sweep_order(self, node_ids: List[str], dt: float, current_step: int = 0):
        print(f"\n🔄 Sweeping nodes in order: {node_ids}")
        for nid in node_ids:
            print(f"\n  Processing node: {nid} ({self.nodes[nid].component_type_id})")
            nd = self.nodes[nid]
            inst = nd.instance
            inputs = self._collect_inputs(nid)
            
            if not inputs:
                print(f"    WARNING: No inputs for {nid}")
            
            try:
                # CRITICAL FIX: Pass current_step to components that need it (like reactors)
                if hasattr(inst, 'step_with_time'):
                    outputs = inst.step_with_time(dt, current_step, inputs) or {}
                else:
                    outputs = inst.step(dt, inputs) or {}
                print(f"    Step completed, outputs: {list(outputs.keys())}")
                self._write_outputs(nid, outputs)
            except Exception as e:
                print(f"    ERROR in {nid}: {e}")
                print(f"    Inputs were: {[(k, v[14] if len(v) > 14 else 'Invalid') for k, v in inputs.items()]}")
                raise

    def _loop_iterate(self, component_nodes: List[str], internal_order: List[str],
                      tear_edge_ids: List[str], dt: float, current_step: int = 0,
                      tol: float = 1e-6, max_iter: int = 50, relax: float = 0.5):
        print(f"\n🔁 Starting loop iteration for nodes: {component_nodes}")
        print(f"   Internal order: {internal_order}")
        print(f"   Tear edges: {tear_edge_ids}")
        
        # NEW APPROACH: Initialize ONLY tear edges with _create_copies equivalent
        for eid in tear_edge_ids:
            if eid not in self.edge_values:
                # Use BSM1Base._create_copies approach - copy from first influent
                # This is equivalent to what BSM1Base does with self.y_in[0]
                influent_composition = np.array([
                    30, 69.5, 51.2, 202.32, 28.17, 0, 0, 0, 0, 31.56, 6.95, 10.59, 7, 
                    211.2675, 18446, 15, 0, 0, 0, 0, 0
                ], dtype=float)
                # Create a copy like BSM1Base._create_copies does
                self.edge_values[eid] = influent_composition.copy()
                print(f"   Initialized tear edge {eid} with _create_copies approach (Q={influent_composition[14]})")
                
        for iteration in range(max_iter):
            print(f"\n  Loop iteration {iteration + 1}/{max_iter}")
            prev = {eid: self.edge_values[eid].copy() for eid in tear_edge_ids}
            self._sweep_order(internal_order, dt, current_step)
            
            # Check convergence and relax
            max_res = 0.0
            for eid in tear_edge_ids:
                new_val = self.edge_values.get(eid, prev[eid])
                res = float(np.max(np.abs(new_val - prev[eid])))
                self.edge_values[eid] = (1 - relax) * prev[eid] + relax * new_val
                max_res = max(max_res, res)
                print(f"    Tear edge {eid} residual: {res:.2e}")
                
            print(f"  Max residual: {max_res:.2e}, tolerance: {tol:.2e}")
            if max_res < tol:
                print(f"  ✓ Converged after {iteration + 1} iterations")
                break
        else:
            print(f"  ⚠ Did not converge after {max_iter} iterations")

    def step_steady(self, dt: float, current_step: int = 0):
        print(f"\n▶ Starting step with dt={dt}, step={current_step}")
        for i, st in enumerate(self.plan["stages"]):
            print(f"\n📋 Executing Stage {i}: {st['type'].upper()}")
            if st["type"] == "acyclic":
                self._sweep_order(st["order"], dt, current_step)
            else:
                self._loop_iterate(st["nodes"], st["internal_order"], st["tear_edges"], dt, current_step)

    def simulate_steady(self, timestep: float, endtime: float):
        steps = int(round(endtime / timestep))
        
        print(f"\n🚀 Starting simulation: {steps} steps, dt={timestep:.6f} days")
        
        # Store results for BSM1OL compatibility
        self.ys_eff = None
        self.sludge_height = None
        self.ys_tss_internal = None
        
        for i in range(steps):
            print(f"\n{'='*60}")
            print(f"SIMULATION STEP {i+1}/{steps} (t={i*timestep:.4f} days)")
            print(f"{'='*60}")
            self.step_steady(timestep, i)
            
            # Stop early if there are numerical issues - REMOVED, now that step parameter is fixed
            # if i >= 2:  # Allow a few steps for debugging
            #     print(f"\n⏹ Stopping early after {i+1} steps for debugging")
            #     break
            
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
            print(f"\n📊 Final effluent from node: {self.ys_eff[:5] if self.ys_eff is not None else 'None'}")
        else:
            self.ys_eff = np.zeros(21)
            print(f"\n📊 Using default effluent (no effluent node found)")
            
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
        endtime = 20  # days - shorter for debugging
        
        print(f"\n🎯 Simulation Configuration:")
        print(f"   Timestep: {timestep:.6f} days ({timestep*24*60:.1f} minutes)")
        print(f"   End time: {endtime} days")
        print(f"   Nodes: {len(self.nodes)}")
        print(f"   Edges: {len(self.config.get('edges', []))}")
        
        self.simulate_steady(timestep, endtime)
        
        return {
            'effluent': self.ys_eff,
            'sludge_height': self.sludge_height,
            'tss_internal': self.ys_tss_internal
        }