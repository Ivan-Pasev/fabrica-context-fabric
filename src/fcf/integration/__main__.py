"""Operator-run live conformance report; never displays credentials."""
from __future__ import annotations
import argparse
import json
import os
import sys
from fcf.integration.conformance import LiveProbe
from fcf.kernel import FCFError


def main(argv=None):
    ap=argparse.ArgumentParser(description='Read-only OpenViking 0.5.0 P02 acceptance probe')
    ap.add_argument('--base-url',required=True)
    ap.add_argument('--project',required=True)
    ap.add_argument('--expected-user',required=True)
    ap.add_argument('--query',default='FRONTIER-FCF-P02-SENTINEL-7d3e9')
    ap.add_argument('--allow-https-host',action='append',default=[])
    ap.add_argument('--foreign-user',required=True,help='Same-account unprivileged user that MUST be denied')
    ap.add_argument('--expected-hit-uri',required=True,help='Exact synthetic source URI expected in results')
    ns=ap.parse_args(argv)
    key=os.getenv('FCF_P02_USER_KEY','')
    foreign=os.getenv('FCF_P02_OUTSIDER_KEY','')
    try:
        p=LiveProbe(ns.base_url,key,ns.project,ns.expected_user,allowed_https_hosts=frozenset(ns.allow_https_host))
        report=p.preflight()
        if report['outcome']=='PASS':
            results=p.read_only_find(ns.query,limit=5)
            found = any(h.get('uri')==ns.expected_hit_uri for h in results['resources'])
            report['retrieval']={'result_count':len(results['resources']),
                   'all_scoped':True,'retrieval_results_are_trusted':False,
                   'expected_source_retrieved':'PASS' if found else 'HOLD'}
            if not found: report['outcome']='HOLD'
            result=p.assert_forbidden_user(foreign_api_key=foreign,foreign_expected_user=ns.foreign_user)
            report['secondary_user_denial']=result
        report['production_authorized']=False
        print(json.dumps(report,indent=2,sort_keys=True))
        return 0 if report['outcome']=='PASS' else 2
    except (FCFError,OSError,ValueError) as exc:
        # Avoid accidental leakage of HTTP body, exception URL, or API key.
        print(json.dumps({'outcome':'HOLD','error_class':type(exc).__name__,
                          'production_authorized':False},indent=2))
        return 2

if __name__=='__main__': sys.exit(main())
