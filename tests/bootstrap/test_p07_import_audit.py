"""P07 source-promotion admission tests (no external mutations)."""
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "p07_import_audit", HERE / "scripts" / "p07_import_audit.py"
)
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)

class AuditTests(unittest.TestCase):
    def test_missing_manifest_is_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "README.md").write_text("bootstrap")
            self.assertEqual(AUDIT.audit_repo(Path(tmp))["status"], "HOLD")

    def test_unsafe_paths_rejected(self):
        for path in ("../private", "/etc/passwd", "a/../b", "a\\b"):
            with self.subTest(path=path):
                self.assertRaises(AUDIT.ImportAuditError, AUDIT._check_name, path)

    def test_hash_mismatch_rejected(self):
        sums = hashlib.sha256(b"hello").hexdigest() + "  data.txt\n"
        self.assertRaises(AUDIT.ImportAuditError, AUDIT._verify,
                          {"data.txt": b"BAD", "SHA256SUMS.txt": sums.encode()})

    def test_missing_file_rejected(self):
        self.assertRaises(AUDIT.ImportAuditError, AUDIT._verify,
                          {"SHA256SUMS.txt": b"0" * 64 + b"  missing.txt\n"})

    def test_wrong_file_count_rejected(self):
        sums = hashlib.sha256(b"OK").hexdigest() + "  data.txt\n"
        self.assertRaises(AUDIT.ImportAuditError, AUDIT._verify,
                          {"data.txt": b"OK", "SHA256SUMS.txt": sums.encode()})

if __name__ == "__main__":
    unittest.main()
