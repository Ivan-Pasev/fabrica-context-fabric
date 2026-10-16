"""Opt-in nonmutating P09 observation: no secrets in stdout, no auto-promotion."""
from __future__ import annotations
import argparse
import json
import os
from fcf.integration.conformance import LiveProbe
from fcf.integration.p03 import P03Probe
from fcf.integration.p09_gate import hold_report, observation_report
from fcf.kernel import FCFError

def main(argv=None):
    p=argparse.ArgumentParser(description="P09 observed contract, not native-server attestation")
    p.add_argument("--execute",action="store_true")
    p.add_argument("--base-url",default="http://127.0.0.1:1933")
    for name in ("project","expected-user","foreign-user","file-uri","expected-sha256","query","operator-reference"):
        p.add_argument("--"+name,required=True)
    p.add_argument("--allow-https-host",action="append",default=[])
    x=p.parse_args(argv)
    if not x.execute:
        print(json.dumps(hold_report("NOT_EXECUTED"),sort_keys=True))
        return 2
    owner=os.getenv("FCF_P09_OWNER_KEY","")
    outsider=os.getenv("FCF_P09_OUTSIDER_KEY","")
    pin=os.getenv("FCF_P09_PROCESS_SHA256","")
    if not owner or not outsider or owner==outsider:
        print(json.dumps(hold_report("MISSING_CREDENTIALS"),sort_keys=True))
        return 2
    if not pin:
        print(json.dumps(hold_report("MISSING_PROCESS_PIN"),sort_keys=True))
        return 2
    try:
        live=LiveProbe(x.base_url,owner,x.project,x.expected_user,
                       allowed_https_hosts=frozenset(x.allow_https_host))
        p03=P03Probe(live).execute(file_uri=x.file_uri,expected_sha256=x.expected_sha256,
                                  search_query=x.query,foreign_api_key=outsider,
                                  foreign_user=x.foreign_user)
        result=observation_report(project_id=x.project,pinned_process_sha256=pin,
                                  p03=p03,operator_reference=x.operator_reference)
        print(json.dumps(result,indent=2,sort_keys=True))
        return 0 if result["evidence_disposition"]=="READY_FOR_INDEPENDENT_REVIEW" else 2
    except (FCFError,OSError,ValueError,TypeError,KeyError):
        print(json.dumps(hold_report("TRANSPORT_OR_CONTRACT_FAILURE"),sort_keys=True))
        return 2

if __name__=="__main__":
    raise SystemExit(main())
