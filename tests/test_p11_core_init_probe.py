"""Offline only: never runs the upstream OpenViking service."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p11_core_init_probe.py"
SPEC = importlib.util.spec_from_file_location("p11_core_probe", SCRIPT)
core = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(core)

class CoreProbeContract(unittest.TestCase):
    def test_no_execution_has_no_side_effects(self):
        report, rc = core.run(False, Path("/not-here"))
        self.assertEqual(rc, 2)
        self.assertEqual(report["reason_code"], "NOT_EXECUTED")
    def test_missing_source_fails_closed(self):
        report, rc = core.run(True, Path("/not-here"))
        self.assertEqual(rc, 2)
        self.assertEqual(report["reason_code"], "SOURCE_MISSING")
    def test_storage_frame(self):
        self.assertEqual(core.frame_stage("/x/openviking/storage/vectordb/init.py"), "C2_STORAGE")
    def test_service_frame(self):
        self.assertEqual(core.frame_stage("/x/openviking/service/core.py"), "C2_SERVICE_CORE")
    def test_auth_frame_not_ignored(self):
        self.assertEqual(core.frame_stage("/x/openviking/server/auth/plugins/api_key.py"), "C3_AUTH")
    def test_unrecognized_path_only_enum(self):
        self.assertEqual(core.frame_stage("/secret/hidden/file.py"), "OTHER")
    def test_exception_message_and_paths_never_exposed(self):
        private = "NEVER_EXPORT_FAKE_TEST_CREDENTIAL"
        try: raise RuntimeError(private)
        except RuntimeError as exc: observed=core.bounded_exception(exc)
        self.assertEqual(observed["exception_kind"], "RuntimeError")
        self.assertFalse(observed["causal_root_established"])
        self.assertNotIn(private, repr(observed))
        self.assertEqual(observed["status"], "HOLD")
    def test_unknown_exception_type_suppressed(self):
        class SensitiveVendorInternalException(Exception): pass
        try: raise SensitiveVendorInternalException("private value")
        except SensitiveVendorInternalException as exc: observed=core.bounded_exception(exc)
        self.assertEqual(observed["exception_kind"], "OTHER")
        self.assertNotIn("SensitiveVendorInternalException", repr(observed))
    def test_forbid_unreviewed_success_reason(self):
        with self.assertRaises(ValueError):
            core.hold("PASS")

if __name__ == "__main__":
    unittest.main()
