"""Knowledge graph — NetworkX build + JSON serialization for the dashboard."""

from __future__ import annotations

import json
import sqlite3

import networkx as nx

from .. import config


def build_graph(conn: sqlite3.Connection, max_messages: int = 4000) -> nx.DiGraph:
    """Build the case knowledge graph: Files, Messages, Persons, Locations,
    Conversations, Known entries, Device — as connected entities."""
    print("\n=== [Stage] Building Knowledge Graph ===")
    G = nx.DiGraph()

    G.add_node("device", type="device", label="Seized device", props={"mock": True})

    # ---- files ----
    for r in conn.execute("SELECT * FROM files"):
        G.add_node(
            f"file:{r['id']}",
            type="file",
            label=r["name"],
            props={
                "path": r["path"],
                "ext": r["ext"],
                "size": r["size_bytes"],
                "modified_ts": r["modified_ts"],
                "hidden": bool(r["is_hidden"]),
                "is_image": bool(r["is_image"]),
                "is_chat": bool(r["is_chat"]),
            },
        )
        G.add_edge("device", f"file:{r['id']}", type="contains")

    # ---- conversations + messages ----
    msgs = conn.execute(
        "SELECT m.*, c.title, c.chat_file_id FROM chat_messages m "
        "JOIN conversations c ON c.id=m.conv_id ORDER BY m.ts"
    ).fetchall()
    if len(msgs) > max_messages:
        msgs = msgs[-max_messages:]

    for c in conn.execute("SELECT * FROM conversations"):
        G.add_node(f"conv:{c['id']}", type="conversation", label=c["title"],
                   props={"participants": json.loads(c["participants"] or "[]"),
                          "msg_count": c["msg_count"]})
        if c["chat_file_id"]:
            G.add_edge(f"file:{c['chat_file_id']}", f"conv:{c['id']}", type="contains")

    for m in msgs:
        G.add_node(f"msg:{m['id']}", type="message",
                   label=f"{m['sender']}: {m['text'][:40]}",
                   props={"ts": m["ts"], "sender": m["sender"], "text": m["text"][:300],
                          "night": bool(m["night_hour"]),
                          "coded": bool(m["coded_marker"])})
        G.add_edge(f"conv:{m['conv_id']}", f"msg:{m['id']}", type="contains")
        G.add_edge(f"person:{m['sender']}", f"msg:{m['id']}", type="sent_by")
        if m["mentions_location"]:
            for loc in config.LOCATIONS:
                if loc.lower() in m["text"].lower():
                    G.add_edge(f"msg:{m['id']}", f"loc:{loc}", type="mentions")

    # ---- persons & locations (invented, synthetic) ----
    for p in config.PERSONS:
        G.add_node(f"person:{p}", type="person", label=p, props={"mock": True})
    for loc in config.LOCATIONS:
        G.add_node(f"loc:{loc}", type="location", label=loc, props={"mock": True})

    # ---- hash matches to known entries ----
    for hm in conn.execute(
        "SELECT hm.*, f.name FROM hash_matches hm JOIN files f ON f.id=hm.file_id "
        "WHERE hm.hash_type IN ('sha256','phash')"
    ):
        known_node = f"known:{hm['known_id']}"
        if not G.has_node(known_node):
            G.add_node(known_node, type="known", label=hm["known_id"],
                       props={"mock": True})
        G.add_edge(f"file:{hm['file_id']}", known_node, type="hash_matches",
                   props={"hash_type": hm["hash_type"], "confidence": hm["confidence"]})

    # ---- intra-device perceptual similarity ----
    for hm in conn.execute(
        "SELECT hm.* FROM hash_matches hm WHERE hm.hash_type='similar_to'"
    ):
        if hm["known_id"].startswith("FILE-"):
            G.add_edge(
                f"file:{hm['file_id']}",
                f"file:{hm['known_id'][5:]}",
                type="similar_to",
                props={"distance": hm["distance"]},
            )

    # ---- flags highlight ----
    for fl in conn.execute("SELECT * FROM flags"):
        node = f"file:{fl['file_id']}"
        if G.has_node(node):
            G.nodes[node]["props"]["flagged"] = True
            G.nodes[node]["props"]["flag_score"] = fl["score"]
            G.nodes[node]["props"]["decision"] = fl["decision"]
    return G


def compute_positions(G: nx.DiGraph, k: float = 0.5, iterations: int = 50) -> dict:
    if not G.nodes:
        return {}
    pos = nx.spring_layout(G, k=k, iterations=iterations)
    print(f"  [Graph] Layout computed for {G.number_of_nodes()} nodes, {G.number_of_edges()} edges.")
    return pos


def graph_json(G: nx.DiGraph, focus: str | None = None, depth: int = 2,
               pos: dict | None = None) -> dict:
    """Serialize (optionally a BFS subgraph around `focus`) to dashboard JSON with layout.

    `pos` (from compute_positions, cached per scan) avoids recomputing the
    expensive spring layout on every request.
    """
    if focus and G.has_node(focus):
        keep = {focus}
        frontier = {focus}
        for _ in range(depth):
            nxt = set()
            for n in frontier:
                nxt |= set(G.successors(n)) | set(G.predecessors(n))
            keep |= nxt
            frontier = nxt
        sub = G.subgraph(keep)
    else:
        sub = G

    if pos is None:
        pos = compute_positions(sub)
    elif focus and G.has_node(focus) and len(sub) <= 600:
        # focused subgraphs are small — lay them out fresh for a clean view
        pos = compute_positions(sub)
    elif focus and G.has_node(focus):
        missing = [n for n in sub if n not in pos]
        if missing:
            sub_pos = nx.spring_layout(sub.subgraph(missing), seed=7, k=0.55, iterations=20)
            pos = {**pos, **sub_pos}

    nodes = []
    for n, d in sub.nodes(data=True):
        x, y = pos.get(n, (0.0, 0.0))
        nodes.append(
            {
                "id": n,
                "type": d.get("type", "?"),
                "label": d.get("label", n),
                "x": round(float(x), 4),
                "y": round(float(y), 4),
                "props": d.get("props", {}),
            }
        )
    edges = [
        {
            "source": u,
            "target": v,
            "type": d.get("type", "?"),
            "props": d.get("props", {}),
        }
        for u, v, d in sub.edges(data=True)
    ]
    return {"nodes": nodes, "edges": edges, "focus": focus, "node_count": len(nodes)}
