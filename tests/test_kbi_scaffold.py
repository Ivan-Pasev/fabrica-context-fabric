import copy, tempfile, unittest
from pathlib import Path
from fcf.kbi.scaffold import scaffold
from fcf.kbi.validate import KBIValidationError, load_capsule, validate_capsule

TEMPLATE=Path(__file__).resolve().parents[1]/'.kbi'
ARGS=dict(project_id='other-research',canonical_root='https://drive.google.com/drive/folders/other-live',start_url='https://docs.google.com/document/d/start_123/edit',handoff_url='https://docs.google.com/document/d/handoff_456/edit',source_template=TEMPLATE)
class ProjectScaffoldTests(unittest.TestCase):
    def test_distinct_project_can_bootstrap_and_validate(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'candidate'
            r=scaffold(destination=out,**ARGS)
            self.assertEqual(r['project_id'],'other-research')
            x=validate_capsule(load_capsule(out))
            self.assertEqual(x['sources'],2)
            self.assertFalse(x['publication_authorized'])
    def test_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'project';out.mkdir()
            with self.assertRaises(KBIValidationError):scaffold(destination=out,**ARGS)
    def test_project_id_not_reused(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(KBIValidationError):scaffold(destination=Path(d)/'out',**{**ARGS,'project_id':'../fcf'})
    def test_http_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(KBIValidationError):scaffold(destination=Path(d)/'out',**{**ARGS,'start_url':'http://localhost/unsafe'})
    def test_no_repository_root_as_drive(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(KBIValidationError):scaffold(destination=Path(d)/'out',**{**ARGS,'canonical_root':'https://github.com/owner/repo'})
    def test_generated_capsule_has_independent_source_identity(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'out';scaffold(destination=out,**ARGS)
            src=load_capsule(out)['sources.json']
            self.assertEqual(src['boot_order'],['OTHER-RESEARCH-START','OTHER-RESEARCH-HANDOFF'])
            self.assertEqual([z['authority'] for z in src['sources']],['RND_CANON','RND_CANON'])
            self.assertFalse(any('FCF-' in z['id'] for z in src['sources']))
