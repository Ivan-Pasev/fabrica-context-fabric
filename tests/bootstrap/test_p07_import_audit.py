"""P07 nonmutation tests for source promotion evidence."""
import hashlib
import tempfile
import unittest
from pathlib import Path
import importlib.util

HERE = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('p07_import_audit', HERE/'scripts/p07_import_audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class AuditTests(unittest.TestCase):
    def test_repo_without_release_manifest_is_hold(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'README.md').write_text('bootstrap')
            self.assertEqual(audit.audit_repo(Path(tmp))['status'], 'HOLD')
    def test_unsafe_paths_rejected(self):
        for s in ('../private', '/etc/passwd', 'a/../b', 'a\\b'):
            with self.subTest(s=s): self.assertRaises(audit.ImportAuditError, audit._check_name, s)
    def test_hash_mismatch_rejected(self):
        sums=hashlib.sha256(b'hello').hexdigest()+'  data.txt\n'
        self.assertRaises(audit.ImportAuditError, audit._verify, {'data.txt':b'BAD', 'SHA256SUMS.txt':sums.encode()})
    def test_missing_file_rejected(self):
        self.assertRaises(audit.ImportAuditError,audit._verify,{'SHA256SUMS.txt':b'0'*64+b'  missing.txt\n'})
    def test_wrong_count_rejected(self):
        sums=hashlib.sha256(b'OK').hexdigest()+'  data.txt\n'
        self.assertRaises(audit.ImportAuditError,audit._verify, {'data.txt':b'OK','SHA256SUMS.txt':sums.encode()})

if __name__=='__main__':unittest.main()
