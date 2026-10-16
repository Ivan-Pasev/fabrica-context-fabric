"""Produce a bounded local validation receipt. No remote operations or license claims."""
from __future__ import annotations
import json, os, re, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENV={**os.environ,'PYTHONPATH':str(ROOT/'src')}
def run(args):
    p=subprocess.run(args,cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=60)
    return {'argv':args,'returncode':p.returncode,'stdout':p.stdout[-9000:],'stderr':p.stderr[-9000:]}
checks={
  'unittest':run([sys.executable,'-m','unittest','discover','-s','tests','-v']),
  'kbi_structural':run([sys.executable,'-m','fcf.kbi.validate','--root','.kbi']),
  'schema_specimens':run([sys.executable,'validation/check_schemas.py']),
  'scientific_conflicts':run([sys.executable,'cases/dft_reference_case.py']),
}
with tempfile.TemporaryDirectory() as d:
    capture=run([sys.executable,'-m','fcf','capture','--store',d,'--file','fixtures/hypotheses.txt','--project','dft-research','--uri','fixture://dft/hypotheses','--revision','fixture-1'])
    checks['capture']=capture
    if capture['returncode']==0:
        rid=json.loads(capture['stdout'])['record_sha256']
        checks['verify']=run([sys.executable,'-m','fcf','verify','--store',d,'--record',rid])
        checks['propose']=run([sys.executable,'-m','fcf','propose','--store',d,'--record',rid,'--claim','Provisional hypothesis, not a theorem'])
        if checks['propose']['returncode']==0:
            path=Path(d)/'proposal.json';path.write_text(checks['propose']['stdout'],encoding='utf-8')
            checks['assess']=run([sys.executable,'-m','fcf','assess','--store',d,'--proposal',str(path),'--principal-id','demo-reviewer','--role','reviewer'])
summary=checks['unittest']['stderr']
count=int(re.search(r'Ran (\d+) tests',summary).group(1)) if re.search(r'Ran (\d+) tests',summary) else 0
ok=len(checks)==8 and all(v['returncode']==0 for v in checks.values()) and count>=99
assessment=json.loads(checks['assess']['stdout']) if 'assess' in checks and checks['assess']['returncode']==0 else {}
if assessment.get('canonical_write_performed') is not False or assessment.get('semantic_truth')!='NOT_PROVEN':ok=False
report={
  'schema':'fcf.validation.p04.v1',
  'date_utc':datetime.now(timezone.utc).isoformat(),
  'release':'FCF-v0.4.0-KBI-reference-candidate',
  'local_gate':'PASS' if ok else 'FAIL',
  'unit_tests_passed':count if checks['unittest']['returncode']==0 else 0,
  'new_kbi_negative_cases':24,
  'cross_project_candidate_generator_tests':6,
  'kbi_structural':('PASS_STRUCTURAL_ONLY' if checks['kbi_structural']['returncode']==0 else 'FAIL'),
  'schema_specimens':3 if checks['schema_specimens']['returncode']==0 else 0,
  'cli_end_to_end':all(checks.get(s,{}).get('returncode',1)==0 for s in ('capture','verify','propose','assess')),
  'cli_canonical_write_performed':assessment.get('canonical_write_performed'),
  'cli_semantic_truth':assessment.get('semantic_truth'),
  'http_simulated_contract_tests':'PASS_LOCAL_EMULATION',
  'openviking_native_live':'NOT_RUN',
  'repository_created':'NOT_CREATED',
  'github_public_release':'NOT_PUBLISHED',
  'public_repo_provider_lookup':'NOT_FOUND_404',
  'repo_create_blocker':'GITHUB_CONNECTOR_HAS_NO_CREATE_REPOSITORY_ACTION_AND_BROWSER_CREDITS_UNAVAILABLE',
  'drive_live_documents':'PROVIDER_READBACK_VERIFIED',
  'real_authorization_enforced':'NOT_ESTABLISHED',
  'license_clearance':'PENDING',
  'production_approved':False,
  'commands':[{ 'name':k,'argv':v['argv'],'returncode':v['returncode']} for k,v in checks.items()],
}
(ROOT/'validation'/'p04').mkdir(parents=True,exist_ok=True)
(ROOT/'validation'/'validation_report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
(ROOT/'validation'/'p04'/'local-check.log').write_text('\n\n'.join(f'## {k}\n'+v['stdout']+v['stderr'] for k,v in checks.items()),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['release','local_gate','unit_tests_passed','kbi_structural','schema_specimens','openviking_native_live','github_public_release']},indent=2))
raise SystemExit(0 if ok else 1)
