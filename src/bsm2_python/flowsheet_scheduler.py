# Flowsheet-Scheduling mit SCC + Toposort und Tear-Heuristik
# Erwartete JSON-Struktur wie in den Beispieldateien mit "nodes" und "edges".
from __future__ import annotations
import json
from collections import defaultdict, deque
from typing import Dict, List, Set, Tuple, Any

def load_flowsheet(path_or_str: str, from_string: bool = False) -> Dict[str, Any]:
    """
    Lädt die Flowsheet-Konfiguration aus JSON und gibt ein Dict mit nodes/edges zurück.
    """
    if from_string:
        data = json.loads(path_or_str)
    else:
        with open(path_or_str, "r", encoding="utf-8") as f:
            data = json.load(f)
    # einfache Validierung
    assert "nodes" in data and "edges" in data, "JSON braucht 'nodes' und 'edges'"
    return data

def build_graph(data: Dict[str, Any]):
    """
    Erzeugt Graphstrukturen: Adjazenz, inverse Adjazenz, Knotenmenge, Self-Loops, Kantenindizes.
    """
    nodes: Set[str] = {n["id"] for n in data["nodes"]}
    adj: Dict[str, List[str]] = defaultdict(list)
    radj: Dict[str, List[str]] = defaultdict(list)
    self_loops: Set[str] = set()
    # map (u,v) -> Liste von Edge-IDs (Mehrfachkanten möglich)
    edge_ids_by_pair: Dict[Tuple[str, str], List[str]] = defaultdict(list)

    for e in data["edges"]:
        u = e["source_node_id"]
        v = e["target_node_id"]
        eid = e.get("id", f"{u}->{v}")
        if u not in nodes or v not in nodes:
            # Fremdreferenzen ignorieren/validieren
            continue
        adj[u].append(v)
        radj[v].append(u)
        edge_ids_by_pair[(u, v)].append(eid)
        if u == v:
            self_loops.add(u)

    # sorge dafür, dass alle Knoten Schlüssel haben
    for n in nodes:
        adj.setdefault(n, [])
        radj.setdefault(n, [])
    return nodes, adj, radj, self_loops, edge_ids_by_pair

def tarjan_scc(nodes: Set[str], adj: Dict[str, List[str]]) -> List[List[str]]:
    """
    Tarjan-Algorithmus zur Bestimmung der SCCs, Laufzeit O(V+E).
    """
    index = 0
    index_of: Dict[str, int] = {}
    lowlink: Dict[str, int] = {}
    onstack: Set[str] = set()
    stack: List[str] = []
    comps: List[List[str]] = []

    def strongconnect(v: str):
        nonlocal index
        index_of[v] = index
        lowlink[v] = index
        index += 1
        stack.append(v)
        onstack.add(v)

        for w in adj[v]:
            if w not in index_of:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif w in onstack:
                lowlink[v] = min(lowlink[v], index_of[w])

        if lowlink[v] == index_of[v]:
            comp = []
            while True:
                w = stack.pop()
                onstack.remove(w)
                comp.append(w)
                if w == v:
                    break
            comps.append(comp)

    for v in nodes:
        if v not in index_of:
            strongconnect(v)
    return comps

def build_condensation_graph(sccs: List[List[str]],
                             adj: Dict[str, List[str]]
                             ) -> Tuple[Dict[int, Set[int]], Dict[str, int]]:
    """
    Baut den SCC-DAG (Kondensationsgraph) und liefert node->scc_id Mapping.
    """
    node_to_comp: Dict[str, int] = {}
    for cid, comp in enumerate(sccs):
        for v in comp:
            node_to_comp[v] = cid

    H: Dict[int, Set[int]] = defaultdict(set)
    for u, nbrs in adj.items():
        cu = node_to_comp[u]
        for v in nbrs:
            cv = node_to_comp[v]
            if cu != cv:
                H[cu].add(cv)

    # stelle sicher, dass alle Komponenten als Keys existieren
    for cid in range(len(sccs)):
        H.setdefault(cid, set())

    return H, node_to_comp

def kahn_toposort_dag(H: Dict[int, Set[int]]) -> List[int]:
    """
    Kahn-Toposort für den SCC-DAG.
    """
    indeg: Dict[int, int] = {u: 0 for u in H}
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
        raise RuntimeError("SCC-DAG hat Zyklus (sollte nicht passieren).")
    return order

def detect_back_edges_in_scc(component: Set[str],
                             adj: Dict[str, List[str]]) -> Set[Tuple[str, str]]:
    """
    Einfache Tear-Heuristik: wähle DFS-Back-Edges innerhalb der Komponente als Tear-Kanten.
    """
    color: Dict[str, int] = {v: 0 for v in component}  # 0=white,1=gray,2=black
    stack: List[str] = []
    tears: Set[Tuple[str, str]] = set()

    def dfs(u: str):
        color[u] = 1
        stack.append(u)
        for v in adj[u]:
            if v not in component:
                continue
            if color[v] == 0:
                dfs(v)
            elif color[v] == 1:
                # Back-Edge u->v (v ist auf dem Stack): Zyklus entdeckt -> Tear-Kandidat
                tears.add((u, v))
        color[u] = 2
        stack.pop()

    for v in component:
        if color[v] == 0:
            dfs(v)
    return tears

def internal_toposort_after_tearing(component: Set[str],
                                    adj: Dict[str, List[str]],
                                    tears: Set[Tuple[str, str]]) -> List[str]:
    """
    Entfernt Tear-Kanten und sortiert die verbleibende Teilgraph-Topologie innerhalb der Komponente.
    """
    # baue reduzierte Adjazenz und Indegrees innerhalb der Komponente
    red_adj: Dict[str, Set[str]] = {u: set() for u in component}
    indeg: Dict[str, int] = {u: 0 for u in component}
    for u in component:
        for v in adj[u]:
            if v in component and (u, v) not in tears:
                if v not in red_adj[u]:
                    red_adj[u].add(v)
                    indeg[v] += 1

    # Kahn auf Knotenebene
    q = deque([u for u, d in indeg.items() if d == 0])
    order: List[str] = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in red_adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

    if len(order) != len(component):
        raise RuntimeError("Interne Toposort nach Tearing nicht vollständig (weitere Tears nötig).")
    return order

def schedule_flowsheet(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Gesamtpipeline: Graph bauen -> SCCs -> SCC-DAG-Toposort -> Stufenplan erzeugen.
    Gibt ein Dict mit:
      - stages: Liste von Stufen; acyclisch: {'type':'acyclic','nodes':[n],'order':[n]}
                 zyklisch: {'type':'loop','nodes':[...],'tear_edges':[edge_ids], 'internal_order':[...]}
      - node_to_comp: Mapping Knoten -> SCC-ID
      - comp_order: Reihenfolge der SCCs
    zurück.
    """
    nodes, adj, _radj, self_loops, edge_ids_by_pair = build_graph(data)
    sccs = tarjan_scc(nodes, adj)
    H, node_to_comp = build_condensation_graph(sccs, adj)
    comp_order = kahn_toposort_dag(H)

    # Hilfsmenge für schnellen Lookup der Kantenpaare je SCC
    stages: List[Dict[str, Any]] = []
    for cid in comp_order:
        comp_nodes = set(sccs[cid])

        # Prüfe, ob trivialer, acyclischer Einzelknoten (kein Self-Loop)
        if len(comp_nodes) == 1:
            n = next(iter(comp_nodes))
            if n not in self_loops:
                stages.append({
                    "type": "acyclic",
                    "nodes": [n],
                    "order": [n],
                    "component_id": cid
                })
                continue

        # Zyklenfall: Tears auswählen (Back-Edges)
        tear_pairs = detect_back_edges_in_scc(comp_nodes, adj)

        # Mappen auf tatsächliche Edge-IDs (falls Mehrfachkanten, nimm die erste)
        tear_edge_ids: List[str] = []
        for (u, v) in tear_pairs:
            ids = edge_ids_by_pair.get((u, v), [])
            if ids:
                tear_edge_ids.append(ids[0])
            else:
                # Fallback: synthetische Kennung
                tear_edge_ids.append(f"{u}->{v}")

        # Interne Ordnung nach Entfernen der Tears
        try:
            internal_order = internal_toposort_after_tearing(comp_nodes, adj, tear_pairs)
        except RuntimeError:
            # Wenn Back-Edges nicht genügen, entferne zusätzlich vorwärtsgerichtete Kanten aus einfachen Zyklen
            # (Heuristik: entferne eine Kante pro noch verbleibender Zyklusentdeckung)
            # Für Kürze: delegiere an eine zweite Runde, die alle Kanten eines DFS-Zyklus reißt
            extra_tears = detect_back_edges_in_scc(comp_nodes, adj)
            tear_pairs |= extra_tears
            internal_order = internal_toposort_after_tearing(comp_nodes, adj, tear_pairs)

        stages.append({
            "type": "loop",
            "nodes": sorted(comp_nodes),
            "tear_edges": tear_edge_ids,
            "internal_order": internal_order,
            "component_id": cid
        })

    return {
        "stages": stages,
        "node_to_comp": node_to_comp,
        "comp_order": comp_order,
        "num_components": len(sccs)
    }