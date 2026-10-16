"""Fail-closed P03 operator CLI; no secret values in output."""
import argparse
import json
import os
from fcf.integration.conformance import LiveProbe
from fcf.integration.p03 import P03Probe
from fcf.kernel import FCFError


def main(argv=None):
    a=argparse.ArgumentParser(description='P03 byte-integrity and index-consistency observation')
    a.add_argument('--base-url',default='http://127.0.0.1:1933')
    a.add_argument('--project',required=True)
    a.add_argument('--expected-user',required=True)
    a.add_argument('--foreign-user',required=True)
    a.add_argument('--file-uri',required=True)
    a.add_argument('--expected-sha256',required=True)
    a.add_argument('--query',required=True)
    a.add_argument('--allow-https-host',action='append',default=[])
    ns=a.parse_args(argv)
    try:
        p=LiveProbe(ns.base_url,os.getenv('FCF_P03_USER_KEY',''),ns.project,ns.expected_user,
                    allowed_https_hosts=frozenset(ns.allow_https_host))
        r=P03Probe(p).execute(file_uri=ns.file_uri,expected_sha256=ns.expected_sha256,
             search_query=ns.query,foreign_api_key=os.getenv('FCF_P03_OUTSIDER_KEY',''),
             foreign_user=ns.foreign_user)
        print(json.dumps(r,indent=2,sort_keys=True))
        return 0 if r['outcome']=='PASS' else 2
    except (FCFError,OSError,ValueError) as e:
        print(json.dumps({'phase':'P03','outcome':'HOLD','error_class':type(e).__name__,
                          'production_authorized':False},indent=2))
        return 2

if __name__=='__main__': raise SystemExit(main())
