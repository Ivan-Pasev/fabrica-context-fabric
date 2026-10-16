"""P09 observation boundary: bounded HTTP success is not native-process authenticity."""
from __future__ import annotations
from typing import Any
from fcf.kernel import FCFError, check_project

UPSTREAM_COMMIT = "20f9c11362ad16193b0daa4a414e1095061af427"
REQUIRED = frozenset(("health","version","auth_mode","ready","principal","acl_structure"))

def _sha(v):
    return isinstance(v,str) and len(v)==64 and all(c in "0123456789abcdef" for c in v)

def hold_report(reason):
    if reason not in {"NOT_EXECUTED","MISSING_CREDENTIALS","MISSING_PROCESS_PIN","TRANSPORT_OR_CONTRACT_FAILURE"}:
        raise FCFError("unexpected hold code")
    return {"phase":"P09","functional_contract":"NOT_VERIFIED","genuine_native_gate":"HOLD",
            "reason_code":reason,"source_authenticity":"NOT_PROVEN",
            "semantic_truth":"NOT_PROVEN","production_authorized":False}

def observation_report(*,project_id:str,pinned_process_sha256:str,p03:dict[str,Any],operator_reference:str):
    check_project(project_id)
    if not _sha(pinned_process_sha256):
        raise FCFError("64-char lowercase process hash required")
    if not isinstance(operator_reference,str) or not (1<=len(operator_reference)<=128) or any(
        q in operator_reference for q in ("\r","\n","@","://","/","\\")):
        raise FCFError("bounded non-secret operator label required")
    if not isinstance(p03,dict) or p03.get("project_id")!=project_id:
        raise FCFError("P03 observation wrong project")
    pre=p03.get("preflight",{})
    checks=pre.get("checks",{}) if isinstance(pre,dict) else {}
    checks_ok=isinstance(checks,dict) and set(checks)==REQUIRED and all(checks[k]=="PASS" for k in REQUIRED)
    groups=[p03.get(k) for k in ("retrieval","download","index","non_owner","non_owner_download")]
    if not all(isinstance(g,dict) for g in groups):
        groups=[{} for _ in range(5)]
    retrieved,download,index,denied,denied_file=groups
    root="viking://resources/"+project_id
    uri=download.get("file_uri")
    scope_ok=isinstance(uri,str) and uri.startswith(root+"/") and all(
        seg not in ("",".","..") for seg in uri[len(root)+1:].split("/"))
    hash_ok=_sha(download.get("expected_sha256")) and download.get("observed_sha256")==download["expected_sha256"]
    functional=(p03.get("outcome")=="PASS" and isinstance(pre,dict) and
                pre.get("outcome")=="PASS" and checks_ok and
                retrieved.get("expected_hit")=="PASS" and
                type(retrieved.get("result_count")) is int and retrieved["result_count"]>0 and
                download.get("byte_integrity")=="PASS" and
                type(download.get("byte_count")) is int and download["byte_count"]>0 and hash_ok and scope_ok and
                index.get("index_consistency")=="PASS" and index.get("scope")==root and
                index.get("server_reported_ok") is True and
                denied.get("outcome")=="PASS" and denied.get("non_owner_stat")=="DENIED" and
                denied.get("status") in (403,404) and
                denied_file.get("status")=="PASS" and denied_file.get("file_read")=="DENIED" and
                denied_file.get("http_status") in (403,404))
    return {"phase":"P09","project_id":project_id,"upstream_tag_target":"v0.5.0",
            "upstream_commit_target":UPSTREAM_COMMIT,"operator_reference":operator_reference,
            "process_sha256_operator_claim":pinned_process_sha256,
            "process_origin":"UNVERIFIED_OPERATOR_ASSERTION",
            "functional_contract":"OBSERVED_PASS" if functional else "HOLD",
            "genuine_native_gate":"HOLD","native_server_authenticity":"NOT_ESTABLISHED",
            "cross_account_isolation":"NOT_ESTABLISHED","recovery":"NOT_RUN",
            "evidence_disposition":"READY_FOR_INDEPENDENT_REVIEW" if functional else "HOLD",
            "source_authenticity":"NOT_PROVEN","semantic_truth":"NOT_PROVEN",
            "production_authorized":False}
