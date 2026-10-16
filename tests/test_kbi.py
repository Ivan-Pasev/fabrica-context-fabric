import copy
import unittest
from pathlib import Path
from fcf.kbi.validate import KBIValidationError, load_capsule, validate_capsule, CAPABILITIES

ROOT=Path(__file__).resolve().parents[1]/'.kbi'

class KBICapsuleTests(unittest.TestCase):
    def setUp(self):self.d=load_capsule(ROOT)
    def reject(self,change):
        d=copy.deepcopy(self.d)
        change(d)
        with self.assertRaises(KBIValidationError):validate_capsule(d)
    def test_capsule_passes_offline(self):
        r=validate_capsule(self.d)
        self.assertEqual(r['verdict'],'PASS_STRUCTURAL_ONLY')
        self.assertEqual(r['canonical_writes'],0)
        self.assertFalse(r['publication_authorized'])
    def test_no_project_wildcard(self):self.reject(lambda d:d['kernel.kbi.json'].update(project_id='*'))
    def test_no_capability_escalation(self):self.reject(lambda d:d['kernel.kbi.json']['kernels'][0].update(required_capability='delete.drive'))
    def test_no_broad_capability_allowlist(self):self.reject(lambda d:d['kernel.kbi.json']['capability_allowlist'].append('publish.github'))
    def test_no_write_effect_by_reader(self):self.reject(lambda d:d['kernel.kbi.json']['kernels'][0].update(effect='STAGING_ONLY'))
    def test_no_canonical_effect(self):self.reject(lambda d:d['kernel.kbi.json']['kernels'][3].update(effect='CANONICAL_WRITE'))
    def test_no_dup_kernel(self):self.reject(lambda d:d['kernel.kbi.json']['kernels'][1].update(id=d['kernel.kbi.json']['kernels'][0]['id']))
    def test_no_unknown_invariant(self):self.reject(lambda d:d['kernel.kbi.json']['kernels'][0]['invariants'].append('INJECTED'))
    def test_no_unknown_dependency(self):self.reject(lambda d:d['kernel.kbi.json']['kernels'][0]['depends_on'].append('ghost'))
    def test_no_cycle(self):
        def mutate(d):
            d['kernel.kbi.json']['kernels'][0]['depends_on'].append('publish_candidate')
            d['lattice.json']['edges'].append({'from':'publish_candidate','to':'sense','relation':'PREREQUISITE'})
        self.reject(mutate)
    def test_no_orphan_lattice_node(self):self.reject(lambda d:d['lattice.json']['nodes'].append({'id':'injected','kernel_namespace':'KBI_KERNEL'}))
    def test_no_duplicate_edge(self):self.reject(lambda d:d['lattice.json']['edges'].append(copy.deepcopy(d['lattice.json']['edges'][0])))
    def test_no_canon_source_demotion(self):self.reject(lambda d:d['sources.json']['sources'][0].update(authority='EXTERNAL_REFERENCE'))
    def test_no_unverified_source(self):self.reject(lambda d:d['sources.json']['sources'][1].update(url='http://example.invalid/a'))
    def test_no_missing_boot(self):self.reject(lambda d:d['sources.json']['sources'].pop(0))
    def test_no_public_gate_open(self):self.reject(lambda d:d['promotion-gates.json']['gates']['GITHUB_RELEASE'].update(enabled_by_this_package=True))
    def test_no_doc_edit_gate_open(self):self.reject(lambda d:d['promotion-gates.json']['gates']['CANONICAL_DOC_EDIT'].update(default='PASS'))
    def test_no_evidence_scalar_inflation(self):self.reject(lambda d:d['promotion-gates.json'].update(evidence_levels_are_independent_axes=False))
    def test_no_publish_evidence_forgery(self):self.reject(lambda d:d['claims.json']['claims'][2].update(status='PASS'))
    def test_no_native_evidence_forgery(self):self.reject(lambda d:d['claims.json']['claims'][1].update(status='PASS'))
    def test_no_claim_missing_source(self):self.reject(lambda d:d['claims.json']['claims'][0].update(source_id='unknown'))
    def test_no_missing_dual_lineage(self):self.reject(lambda d:d['kernel.kbi.json']['namespaces'].pop('KBI_EPISTEMIC'))
    def test_no_source_root_mismatch(self):self.reject(lambda d:d['sources.json'].update(canonical_root='https://example.com/other'))
    def test_no_schema_drift(self):self.reject(lambda d:d['lattice.json'].update(schema='future-not-reviewed'))
    def test_all_capabilities_explicit(self):self.assertEqual(CAPABILITIES,set(self.d['kernel.kbi.json']['capability_allowlist']))

if __name__=='__main__':unittest.main()
