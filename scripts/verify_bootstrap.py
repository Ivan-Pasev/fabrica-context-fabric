#!/usr/bin/env python3
"""Checks KBI file shape, acyclicity and fail-closed defaults, not host permissions."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def check(root=ROOT):
    base = Path(root) / ".kbi"
    lattice = json.loads((base/"lattice.json").read_text(encoding="utf-8"))
    gate_doc = json.loads((base/"promotion-gates.json").read_text(encoding="utf-8"))
    claims = json.loads((base/"claims.json").read_text(encoding="utf-8"))
    project = lattice["project_id"]
    if not project or project == "*" or any(x["project_id"] != project for x in (gate_doc, claims)):
        raise ValueError("identity disagreement")
    vertices = lattice["nodes"]
    ids = [x["id"] for x in vertices]
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("duplicate or absent nodes")
    if any(x["kernel_namespace"] not in {"KBI_KERNEL", "KBI_EPISTEMIC"} for x in vertices):
        raise ValueError("unknown namespace")
    if lattice.get("acyclic_required") is not True:
        raise ValueError("DAG not mandated")
    incoming = dict.fromkeys(ids, 0)
    adj = {x: set() for x in ids}
    for edge in lattice["edges"]:
        a,b = edge["from"],edge["to"]
        if a not in incoming or b not in incoming or a == b or b in adj[a]:
            raise ValueError("bad dependency")
        incoming[b] += 1
        adj[a].add(b)
    ready = [k for k,v in incoming.items() if v == 0]
    visited = 0
    while ready:
        at = ready.pop()
        visited += 1
        for nxt in adj[at]:
            incoming[nxt] -= 1
            if incoming[nxt] == 0:
                ready.append(nxt)
    if visited != len(ids):
        raise ValueError("cycle")
    if not gate_doc.get("evidence_levels_are_independent_axes"):
        raise ValueError("evidence conflation")
    for name, gate in gate_doc["gates"].items():
        if gate.get("default") != "HOLD" or gate.get("enabled_by_this_package") is not False or not gate.get("required"):
            raise ValueError("unsafe gate " + name)
    if any(c["status"] not in {"HOLD","PENDING_REMOTE_CI"} for c in claims["claims"]):
        raise ValueError("unauthorized status upgrade")
    return {"status":"STRUCTURAL_PASS_ONLY","nodes":len(ids),"edges":len(lattice["edges"]),"gates":len(gate_doc["gates"])}

if __name__ == "__main__":
    try:
        print(json.dumps(check(), sort_keys=True))
    except (KeyError, ValueError, OSError, json.JSONDecodeError) as exc:
        print("HOLD: " + str(exc), file=sys.stderr)
        sys.exit(1)
