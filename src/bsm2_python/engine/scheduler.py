from __future__ import annotations
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Any

def build_graph(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]):
    node_ids: Set[str] = {n["id"] for n in nodes}
    adj: Dict[str, List[str]] = defaultdict(list)
    self_loops: Set[str] = set()
    edge_ids_by_pair: Dict[Tuple[str, str], List[str]] = defaultdict(list)
    in_edges_by_node: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    out_edges_by_node: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for e in edges:
        u = e["source_node_id"]; v = e["target_node_id"]
        if u not in node_ids or v not in node_ids:
            continue
        adj[u].append(v)
        if u == v:
            self_loops.add(u)
        edge_ids_by_pair[(u, v)].append(e["id"])
        in_edges_by_node[v].append(e)
        out_edges_by_node[u].append(e)

    for nid in node_ids:
        adj.setdefault(nid, [])
        in_edges_by_node.setdefault(nid, [])
        out_edges_by_node.setdefault(nid, [])
    return node_ids, adj, self_loops, edge_ids_by_pair, in_edges_by_node, out_edges_by_node

def tarjan_scc(nodes: Set[str], adj: Dict[str, List[str]]) -> List[List[str]]:
    index = 0
    index_of: Dict[str, int] = {}
    low: Dict[str, int] = {}
    stack: List[str] = []
    onstack: Set[str] = set()
    comps: List[List[str]] = []

    def dfs(v: str):
        nonlocal index
        index_of[v] = index; low[v] = index; index += 1
        stack.append(v); onstack.add(v)
        for w in adj[v]:
            if w not in index_of:
                dfs(w)
                low[v] = min(low[v], low[w])
            elif w in onstack:
                low[v] = min(low[v], index_of[w])
        if low[v] == index_of[v]:
            comp = []
            while True:
                w = stack.pop(); onstack.remove(w); comp.append(w)
                if w == v: break
            comps.append(comp)

    for v in nodes:
        if v not in index_of:
            dfs(v)
    return comps

def build_condensation(adj: Dict[str, List[str]], sccs: List[List[str]]):
    node2comp: Dict[str, int] = {}
    for cid, comp in enumerate(sccs):
        for v in comp: node2comp[v] = cid
    H: Dict[int, Set[int]] = defaultdict(set)
    for u, nbrs in adj.items():
        cu = node2comp[u]
        for v in nbrs:
            cv = node2comp[v]
            if cu != cv:
                H[cu].add(cv)
    for cid in range(len(sccs)):
        H.setdefault(cid, set())
    return H, node2comp

def kahn_toposort(H: Dict[int, Set[int]]) -> List[int]:
    indeg = {u: 0 for u in H}
    for u in H:
        for v in H[u]:
            indeg[v] = indeg.get(v, 0) + 1
    q = deque([u for u, d in indeg.items() if d == 0])
    order: List[int] = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in H[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(order) != len(H):
        raise RuntimeError("Condensation graph unexpectedly cyclic")
    return order

def detect_tears(component: Set[str], adj: Dict[str, List[str]]) -> Set[Tuple[str, str]]:
    color = {v: 0 for v in component}  # 0 white, 1 gray, 2 black
    tears: Set[Tuple[str, str]] = set()

    def dfs(u: str):
        color[u] = 1
        for v in adj[u]:
            if v not in component: continue
            if color[v] == 0:
                dfs(v)
            elif color[v] == 1:
                tears.add((u, v))
        color[u] = 2

    for v in component:
        if color[v] == 0: dfs(v)
    return tears

def internal_order(component: Set[str], adj: Dict[str, List[str]], tears: Set[Tuple[str, str]]) -> List[str]:
    red_adj = {u: set() for u in component}
    indeg = {u: 0 for u in component}
    for u in component:
        for v in adj[u]:
            if v in component and (u, v) not in tears:
                if v not in red_adj[u]:
                    red_adj[u].add(v)
                    indeg[v] += 1
    q = deque([u for u, d in indeg.items() if d == 0])
    order: List[str] = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in red_adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0: q.append(v)
    if len(order) != len(component):
        raise RuntimeError("Internal topo order incomplete; more tears needed")
    return order

def schedule(data: Dict[str, Any]) -> Dict[str, Any]:
    nodes = data["nodes"]; edges = data["edges"]
    node_ids, adj, self_loops, edge_ids_by_pair, in_edges, out_edges = build_graph(nodes, edges)
    sccs = tarjan_scc(node_ids, adj)
    H, node2comp = build_condensation(adj, sccs)
    comp_order = kahn_toposort(H)

    # produce stages
    stages = []
    for cid in comp_order:
        comp_nodes = set(sccs[cid])
        if len(comp_nodes) == 1:
            n = next(iter(comp_nodes))
            if n not in self_loops:
                stages.append({"type": "acyclic", "nodes": [n], "order": [n], "component_id": cid})
                continue
        tears = detect_tears(comp_nodes, adj)
        try:
            order_in = internal_order(comp_nodes, adj, tears)
        except RuntimeError:
            # fallback: accept tearing all edges that still close cycles by re-running detect_tears
            tears = detect_tears(comp_nodes, adj)
            order_in = internal_order(comp_nodes, adj, tears)
        tear_edge_ids = []
        for (u, v) in tears:
            ids = edge_ids_by_pair.get((u, v), [])
            tear_edge_ids.append(ids[0] if ids else f"{u}->{v}")
        stages.append({
            "type": "loop",
            "nodes": sorted(comp_nodes),
            "internal_order": order_in,
            "tear_edges": tear_edge_ids,
            "component_id": cid
        })
    return {
        "stages": stages,
        "node_to_comp": node2comp,
        "comp_order": comp_order,
    }