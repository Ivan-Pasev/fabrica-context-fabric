"""P08 reviewed full-source parity and fail-closed compatibility regression tests."""
import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]

def module(path, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj

audit = module("scripts/p07_import_audit.py", "p08_reviewed_audit")
bootstrap = module("scripts/verify_bootstrap.py", "p08_bootstrap_contract")

class FullImportParityTests(unittest.TestCase):
    def test_exact_full_source_and_pinned_bootstrap_pass(self):
        status = audit.audit_repo(ROOT)
        self.assertEqual(status["status"], "PASS")
        self.assertEqual(status["file_count"], 87)
        self.assertEqual(status["manifest_entries"], 86)

    def test_modified_bootstrap_artifact_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = pathlib.Path(tmp) / "scripts" / "verify_bootstrap.py"
            p.parent.mkdir(parents=True)
            p.write_bytes(b"# tampered bootstrap verifier\n")
            with self.assertRaises(audit.ImportAuditError):
                audit.audit_repo(pathlib.Path(tmp))

    def test_pending_execution_is_not_claim_promotion(self):
        result = bootstrap.check(ROOT)
        self.assertEqual(result["status"], "STRUCTURAL_PASS_ONLY")
        self.assertEqual(result["nodes"], 9)

if __name__ == "__main__":
    unittest.main()
