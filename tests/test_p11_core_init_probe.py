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


    def test_dimension_alignment_preserves_fixture_and_source(self):
        original = {"storage": {"vectordb": {"name": "test", "backend": "local"}},
                    "embedding": {"dense": {"dimension": 8}}}
        aligned = core.aligned_synthetic_config(original)
        self.assertEqual(aligned["storage"]["vectordb"]["dimension"], 8)
        self.assertNotIn("dimension", original["storage"]["vectordb"])
    def test_dimension_alignment_rejects_broken_fixture(self):
        with self.assertRaises(ValueError):
            core.aligned_synthetic_config({"storage": {"vectordb": {"backend": "local"}},
                "embedding": {"dense": {"dimension": 0}}})
    def test_dimension_alignment_rejects_remote_backend(self):
        with self.assertRaises(ValueError):
            core.aligned_synthetic_config({"storage": {"vectordb": {"backend": "http"}},
                "embedding": {"dense": {"dimension": 8}}})
    def test_exact_upstream_embedding_error_classification_no_leak(self):
        EmbeddingConfigurationError = type("EmbeddingConfigurationError", (Exception,), {})
        ex = EmbeddingConfigurationError("Existing collection metadata is unavailable; cannot validate embedding compatibility")
        report = core.bounded_exception(ex)
        self.assertEqual(report["embedding_failure_site"], "COLLECTION_METADATA_UNAVAILABLE")
        self.assertNotIn("Existing collection metadata", repr(report))
        self.assertFalse(report["causal_root_established"])
    def test_unrecognized_embedding_error_remains_unknown(self):
        EmbeddingConfigurationError = type("EmbeddingConfigurationError", (Exception,), {})
        report = core.bounded_exception(EmbeddingConfigurationError("secret=do-not-reveal"))
        self.assertEqual(report["embedding_failure_site"], "OTHER_EMBEDDING_CONFIGURATION")
        self.assertNotIn("secret=do-not-reveal", repr(report))

if __name__ == "__main__":
    unittest.main()
