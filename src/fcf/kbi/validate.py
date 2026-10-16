"""Validate a project-bound `.kbi` JSON capsule.

Checks bounded syntax and referential constraints only. No claims about
external document authority, authenticated identities or host permissions.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

FILES = ("kernel.kbi.json", "lattice.json", "sources.json", "claims.json", "promotion-gates.json")
NS = {"KBI_KERNEL", "KBI_EPISTEMIC"}
STATUSES = {"PASS", "FAIL", "HOLD", "UNKNOWN", "UNRESOLVED"}
EVIDENCE = {
    "E0_ASSERTION", "E1_REFERENCED", "E2_MECHANICALLY_VERIFIED",
    "E3_INDEPENDENTLY_REPRODUCED", "E4_CONTENT_ADDRESSED", "E5_EXTERNALLY_ATTESTED",
}
CAPABILITIES = {"read.drive", "analyze.local", "verify.local", "write.staging", "none"}
EXPECTED_GATES = {"CANONICAL_DOC_EDIT", "GITHUB_RELEASE", "LIVE_OPENVIKING"}

class KBIValidationError(ValueError):
    """Local structural validation failure; not a host authorization decision."""


def _ensure(pred: bool, explanation: str) -> None:
    if not pred:
        raise KBIValidationError(explanation)


def load_capsule(root: Path) -> dict[str, dict[str, Any]]:
    root = Path(root).resolve()
    data: dict[str, dict[str, Any]] = {}
    for name in FILES:
        path = root / name
        _ensure(path.is_file() and not path.is_symlink(), f"missing, symlink or invalid: {name}")
        _ensure(path.stat().st_size <= 512_000, f"oversized: {name}")
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (UnicodeError, ValueError) as exc:
            raise KBIValidationError(f"malformed JSON {name}: {type(exc).__name__}") from exc
        _ensure(isinstance(document, dict), f"root must be object: {name}")
        data[name] = document
    return data


def validate_capsule(data: dict[str, dict[str, Any]]) -> dict[str, Any]:
    _ensure(set(data) == set(FILES), "missing or unexpected KBI manifest file")
    k = data["kernel.kbi.json"]
    l = data["lattice.json"]
    s = data["sources.json"]
    c = data["claims.json"]
    p = data["promotion-gates.json"]
    schema_names = {"kernel.kbi.json":"fcf.kbi.kernel.v1", "lattice.json":"fcf.kbi.lattice.v1", "sources.json":"fcf.kbi.sources.v1", "claims.json":"fcf.kbi.claims.v1", "promotion-gates.json":"fcf.kbi.promotion.v1"}
    for name, schema in schema_names.items():
        _ensure(data[name].get("schema") == schema, f"schema mismatch: {name}")
    project = k.get("project_id")
    _ensure(isinstance(project,str) and project and project != "*", "invalid project identity")
    for name in FILES:
        _ensure(data[name].get("project_id") == project, f"project identity divergence: {name}")
    _ensure(k.get("default_mode") == "AUDIT_ONLY" and k.get("fail_closed") is True,
            "unsafe kernel default")
    _ensure(set(k.get("namespaces",{})) == NS, "dual KBI namespaces must remain separate")
    _ensure(k.get("operational_capability_available") == "DISCOVER_AT_RUNTIME", "capability escalation")
    _ensure(k.get("canonical_root") == s.get("canonical_root"), "canonical root mismatch")
    _ensure(isinstance(k.get("hard_invariants"), list) and len(k["hard_invariants"]) > 0, "missing invariants")
    _ensure(len(set(k["hard_invariants"])) == len(k["hard_invariants"]), "duplicate invariants")
    caps = set(k.get("capability_allowlist", []))
    _ensure(caps == CAPABILITIES, "capability allowlist changed unexpectedly")
    source_ids: set[str] = set()
    entries = s.get("sources")
    _ensure(isinstance(entries, list) and entries, "empty sources")
    for src in entries:
        _ensure(isinstance(src,dict), "invalid source entry")
        sid=src.get("id")
        _ensure(isinstance(sid,str) and sid and sid not in source_ids, "duplicate/invalid source id")
        source_ids.add(sid)
        _ensure(isinstance(src.get("url"),str) and src["url"].startswith("https://"),f"source URL missing HTTPS: {sid}")
        _ensure(src.get("authority") in {"RND_CANON","EXTERNAL_REFERENCE","UPSTREAM_DEPENDENCY"},f"unknown source authority: {sid}")
    boot_order=s.get("boot_order")
    _ensure(isinstance(boot_order,list) and len(boot_order)==2 and len(set(boot_order))==2, "missing two-record canonical boot order")
    _ensure(set(boot_order) <= source_ids, "missing canonical live boot records")
    src_by_id={item["id"]:item for item in entries}
    for sid,role in zip(boot_order,("START_HERE","STATE_AND_HANDOFF")):
        src=src_by_id[sid]
        _ensure(src.get("required") is True and src.get("authority")=="RND_CANON" and src.get("role")==role, "boot authority or role changed")
    _ensure(s.get("rule") == "LIVE_CANON_OVER_CACHED_PROJECTION", "source authority weakened")
    kernels = k.get("kernels")
    _ensure(isinstance(kernels,list) and len(kernels)>0, "no kernels")
    ids:set[str]=set()
    for ker in kernels:
        _ensure(isinstance(ker,dict),"bad kernel")
        kid=ker.get("id")
        _ensure(isinstance(kid,str) and kid and kid not in ids, "duplicate/invalid kernel id")
        ids.add(kid)
        _ensure(ker.get("namespace") in NS, "unknown kernel namespace")
        _ensure(ker.get("required_capability") in caps, "unknown/privileged kernel capability")
        _ensure(ker.get("effect") in {"NONE","STAGING_ONLY"}, "mutation beyond staging")
        _ensure(ker.get("default_decision") == "HOLD", "kernel bypasses review")
        _ensure(isinstance(ker.get("invariants"),list) and ker["invariants"] and set(ker["invariants"]) <= set(k["hard_invariants"]),"bad invariant reference")
        _ensure(isinstance(ker.get("depends_on"),list),"bad dependency list")
        if ker.get("required_capability") == "write.staging":
            _ensure(ker["effect"] == "STAGING_ONLY", "staging capability mismatched effect")
        else:
            _ensure(ker["effect"] == "NONE", "non-staging kernel declares effects")
    _ensure({n.get("id") for n in l.get("nodes",[])}==ids, "lattice node registry diverged")
    deps=set()
    for ker in kernels:
        for dep in ker["depends_on"]:
            _ensure(dep in ids and dep != ker["id"],"unknown/self dependency")
            deps.add((dep,ker["id"]))
    edges=set()
    for e in l.get("edges",[]):
        _ensure(isinstance(e,dict) and e.get("relation") == "PREREQUISITE","invalid edge")
        pair=(e.get("from"),e.get("to"))
        _ensure(pair[0] in ids and pair[1] in ids and pair not in edges,"unknown/duplicate edge")
        edges.add(pair)
    _ensure(deps == edges,"kernel/lattice dependency mismatch")
    adjacency=defaultdict(list)
    for a,b in edges:adjacency[a].append(b)
    state:dict[str,int]={}
    def dfs(node:str)->None:
        if state.get(node)==1:raise KBIValidationError("kernel lattice cycle")
        if state.get(node)==2:return
        state[node]=1
        for v in adjacency[node]:dfs(v)
        state[node]=2
    for node in ids:dfs(node)
    _ensure(l.get("acyclic_required") is True,"lattice DAG policy disabled")
    for relation in l.get("non_executable_links",[]):
        _ensure(relation.get("from") in source_ids and relation.get("to") in source_ids and relation.get("relation") in {"READ_FIRST","CONTEXT"},"invalid non-executable source link")
    gates=p.get("gates")
    _ensure(isinstance(gates,dict) and set(gates)==EXPECTED_GATES,"missing release/authority gate")
    for name,gate in gates.items():
        _ensure(gate.get("default")=="HOLD" and gate.get("enabled_by_this_package") is False and isinstance(gate.get("required"),list) and bool(gate.get("required")),f"open publication gate: {name}")
    _ensure(p.get("publication_is_separate_authority") is True,"publication authority confused")
    _ensure(p.get("evidence_levels_are_independent_axes") is True,"scalar evidence inflation")
    _ensure(set(p.get("status_vocabulary",[]))==STATUSES,"assessment vocabulary drift")
    _ensure(set(p.get("evidence_axes",[]))==EVIDENCE,"evidence vocabulary drift")
    blocked=c.get("blocked_claims")
    _ensure(isinstance(blocked,list) and bool(blocked) and len(set(blocked))==len(blocked),"missing protected blocked-claims set")
    claim_ids=set()
    for cl in c.get("claims",[]):
        _ensure(isinstance(cl,dict),"invalid claim")
        cid=cl.get("id")
        _ensure(isinstance(cid,str) and cid and cid not in claim_ids,"duplicate/invalid claim id")
        claim_ids.add(cid)
        _ensure(cl.get("status") in STATUSES|{"PENDING_EXECUTION"},"invalid claim status")
        _ensure(isinstance(cl.get("evidence"),list) and bool(cl["evidence"]) and set(cl["evidence"])<=EVIDENCE,"invalid claim evidence")
        _ensure(cl.get("source_id") in source_ids,"claim cites unknown source id")
        if cid in blocked:
            _ensure(cl.get("status")=="HOLD","protected unverified claim prematurely promoted")
    _ensure(set(blocked) <= claim_ids,"missing protected blocked claim")
    return {"verdict":"PASS_STRUCTURAL_ONLY","schema":"fcf.kbi.validation.v1","project_id":project,"kernels":len(ids),"edges":len(edges),"sources":len(source_ids),"claims":len(claim_ids),"canonical_writes":0,"publication_authorized":False,"real_runtime_verified":False}


def main(argv:list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description="Offline structural KBI capsule checker, NOT host authorization")
    parser.add_argument("--root",default=".kbi",help="capsule directory")
    ns=parser.parse_args(argv)
    try:
        result=validate_capsule(load_capsule(Path(ns.root)))
        print(json.dumps(result,indent=2))
        return 0
    except (OSError,KBIValidationError) as exc:
        print(json.dumps({"verdict":"FAIL","error":str(exc)}))
        return 1

if __name__=="__main__":raise SystemExit(main())
