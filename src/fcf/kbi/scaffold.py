"""Create offline KBI project capsule candidates; never edit Google Drive or GitHub."""
from __future__ import annotations
import argparse,copy,json,re
from pathlib import Path
from urllib.parse import urlsplit
from .validate import FILES, load_capsule, validate_capsule, KBIValidationError

PROJECT_ID=re.compile(r'^[a-z][a-z0-9-]{2,63}$')

def _https_url(url:str)->str:
    parsed=urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise KBIValidationError('source URL must be plain https:// with valid hostname')
    return url

def scaffold(project_id:str, canonical_root:str, start_url:str, handoff_url:str, destination:Path, source_template:Path)->dict:
    if not PROJECT_ID.fullmatch(project_id):raise KBIValidationError('invalid project ID')
    root=_https_url(canonical_root)
    start=_https_url(start_url)
    handoff=_https_url(handoff_url)
    if not root.startswith('https://drive.google.com/drive/folders/'):
        raise KBIValidationError('canonical root must be a Google Drive folder URL')
    if not all(x.startswith('https://docs.google.com/document/d/') for x in (start,handoff)):
        raise KBIValidationError('boot docs must be native Docs URLs')
    out=Path(destination)
    if out.exists():raise KBIValidationError('destination already exists; no overwriting permitted')
    data=copy.deepcopy(load_capsule(Path(source_template)))
    sid_start=project_id.upper()+'-START'
    sid_handoff=project_id.upper()+'-HANDOFF'
    source=data['sources.json'];source['project_id']=project_id;source['canonical_root']=root
    source['boot_order']=[sid_start,sid_handoff]
    source['sources']=[
        dict(id=sid_start,role='START_HERE',title='START_HERE',url=start,source_system='google_drive',authority='RND_CANON',content_type='native_document',required=True),
        dict(id=sid_handoff,role='STATE_AND_HANDOFF',title='STATE_AND_HANDOFF',url=handoff,source_system='google_drive',authority='RND_CANON',content_type='native_document',required=True),
    ]
    kernel=data['kernel.kbi.json'];kernel['project_id']=project_id;kernel['id']=project_id.upper().replace('-','_')+'.KBI.ROOT';kernel['canonical_root']=root
    for name in ['lattice.json','claims.json','promotion-gates.json']:data[name]['project_id']=project_id
    lattice=data['lattice.json'];lattice['non_executable_links']=[dict(**{'from':sid_start,'to':sid_handoff,'relation':'READ_FIRST'})]
    claims=data['claims.json'];claims['blocked_claims']=[project_id.upper()+'-NATIVE-VALIDATION',project_id.upper()+'-PUBLICATION']
    claims['claims']=[
        {'id':claims['blocked_claims'][0],'statement':'Genuine integration or runtime confirmed','evidence':['E0_ASSERTION'],'status':'HOLD','scope':'live target runtime only','source_id':sid_handoff},
        {'id':claims['blocked_claims'][1],'statement':'Public release has been authorized and provider-confirmed','evidence':['E0_ASSERTION'],'status':'HOLD','scope':'public release only','source_id':sid_handoff},
    ]
    result=validate_capsule(data)
    # Avoid leaving an empty or partially populated directory on invalid input.
    out.mkdir(parents=True,exist_ok=False)
    for name in FILES:(out/name).write_text(json.dumps(data[name],indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    (out/'README.md').write_text('# '+project_id+' KBI capsule CANDIDATE\n\nThis scaffold is NOT adopted law. Read live START_HERE/HANDOFF; review target permission, rights, invariants, and public-release gates before installation. All protected gates HOLD.\n',encoding='utf-8')
    return result

def main(argv:list[str]|None=None)->int:
    p=argparse.ArgumentParser(description='Generate a target-project KBI candidate; no cloud writes or permissions')
    p.add_argument('--project-id',required=True);p.add_argument('--canonical-root',required=True)
    p.add_argument('--start-url',required=True);p.add_argument('--handoff-url',required=True)
    p.add_argument('--output',required=True);p.add_argument('--template',default='.kbi')
    a=p.parse_args(argv)
    try:
        r=scaffold(a.project_id,a.canonical_root,a.start_url,a.handoff_url,Path(a.output),Path(a.template))
        print(json.dumps({'candidate':'CREATED_NOT_ADOPTED','validation':r},indent=2))
        return 0
    except (KBIValidationError,OSError) as exc:
        print(json.dumps({'candidate':'FAILED','error':str(exc)}))
        return 1
if __name__=='__main__':raise SystemExit(main())
