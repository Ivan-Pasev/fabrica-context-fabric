"""P10 hermetic tests: monkeypatched checks, NOT real upstream installation."""
from __future__ import annotations
import importlib.util
import io
import pathlib
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("p10native", ROOT / "scripts/p10_native_install_smoke.py")
p10 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(p10)

class FakeCompleted:
    def __init__(self, output, code=0):
        self.stdout = output
        self.stderr = ""
        self.returncode = code

class TestInstallGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        (self.root / ".git").mkdir()
        self.calls = []
    def runner(self, args, **kwargs):
        self.calls.append(tuple(args))
        return FakeCompleted(p10.EXPECTED_COMMIT + "\n" if args[0] == "git" else "usage: openviking-server [options]")
    def observed(self, **kwargs):
        return p10.check_install(self.root, runner=kwargs.get("runner", self.runner),
                 executable=kwargs.get("executable", lambda _: "/trusted/openviking-server"),
                 version=kwargs.get("version", lambda _: p10.EXPECTED_VERSION))
    def test_positive_stub_only_cli_evidence(self):
        a=self.observed()
        self.assertEqual(a["status"], "OBSERVED_PASS")
        self.assertFalse(a["genuine_server_started"])
        self.assertFalse(a["production_authorized"])
        self.assertFalse(a["acl_isolation_verified"])
    def test_not_executed_is_hold_without_subprocess(self):
        out=io.StringIO()
        with patch.object(p10,"check_install",side_effect=AssertionError("executed")):
            with redirect_stdout(out):
                self.assertEqual(p10.main(["--upstream-path",str(self.root)]),2)
        self.assertIn("NOT_EXECUTED",out.getvalue())
    def test_source_missing_is_hold(self):
        self.assertEqual(p10.check_install(self.root/"nope")["reason_code"],"UPSTREAM_SOURCE_NOT_PRESENT")
    def test_sha_mismatch_holds(self):
        bad=lambda args,**kw: FakeCompleted("f"*40 if args[0]=="git" else "usage")
        self.assertEqual(self.observed(runner=bad)["reason_code"],"UPSTREAM_SHA_MISMATCH")
    def test_wrong_installed_version_holds(self):
        self.assertEqual(self.observed(version=lambda _: "0.4.0")["reason_code"],"INSTALLED_VERSION_MISMATCH")
    def test_missing_cli_holds(self):
        self.assertEqual(self.observed(executable=lambda _: None)["reason_code"],"CLI_NOT_INSTALLED")
    def test_cli_error_holds(self):
        bad=lambda args,**kw: FakeCompleted(p10.EXPECTED_COMMIT if args[0]=="git" else "error",0 if args[0]=="git" else 1)
        self.assertEqual(self.observed(runner=bad)["reason_code"],"CLI_BOOTSTRAP_FAILED")
    def test_timeout_holds(self):
        bad=lambda args,**kw: (_ for _ in ()).throw(subprocess.TimeoutExpired(args,1))
        self.assertEqual(self.observed(runner=bad)["reason_code"],"EXECUTION_OR_PACKAGE_UNAVAILABLE")

if __name__ == "__main__":
    unittest.main()
