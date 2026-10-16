"""Bounded, hermetic P11 tests: this never launches OpenViking."""
import importlib.util
from pathlib import Path
import unittest

_SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "p11_native_http_smoke.py"
_SPEC = importlib.util.spec_from_file_location("fcf_p11", _SCRIPT)
p11 = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(p11)

class P11SmokeGateTests(unittest.TestCase):
    def healthy(self):
        return (200, {"status": "ok", "healthy": True})
    def ready(self):
        return (200, {"status": "ready"})
    def blocked(self):
        return (401, {"status": "error"})
    def result(self, **replace):
        inputs = {"health": self.healthy(), "ready": self.ready(),
                  "anonymous": self.blocked(), "invalid_key": self.blocked()}
        inputs.update(replace)
        return p11.assess(**inputs)

    def test_healthy_http_only_never_grants_tenancy_or_production(self):
        r = self.result()
        self.assertEqual(r["status"], "OBSERVED_PASS")
        self.assertFalse(r["production_authorized"])
        self.assertEqual(r["two_user_acl"], "NOT_TESTED")
        self.assertEqual(r["cross_account_acl"], "NOT_TESTED")
        self.assertEqual(r["model_provider"], "INERT_LOOPBACK_NOT_VERIFIED")
    def test_health_failure_holds(self):
        self.assertEqual(self.result(health=(503, {}))["status"], "HOLD")
    def test_unhealthy_http_200_holds(self):
        self.assertEqual(self.result(health=(200, {"status":"ok","healthy":False}))["status"], "HOLD")
    def test_unready_holds(self):
        self.assertEqual(self.result(ready=(503, {}))["status"], "HOLD")
    def test_anonymous_access_holds(self):
        self.assertEqual(self.result(anonymous=(200, {}))["status"], "HOLD")
    def test_bad_key_not_rejected_holds(self):
        self.assertEqual(self.result(invalid_key=(200, {}))["status"], "HOLD")
    def test_non_executed_no_io(self):
        result, code = p11.run(execute=False, upstream_path=Path("/does-not-exist"))
        self.assertEqual(code, 2)
        self.assertEqual(result["reason_code"], "NOT_EXECUTED")
    def test_nonexistent_upstream_holds(self):
        result, code = p11.run(execute=True, upstream_path=Path("/does-not-exist"))
        self.assertEqual(code, 2)
        self.assertEqual(result["reason_code"], "SOURCE_MISSING")
    def test_configuration_local_only(self):
        x = p11.config("/tmp/fcf", 19389, "x" * 48)
        self.assertEqual(x["server"]["auth_mode"], "api_key")
        self.assertEqual(x["server"]["host"], "127.0.0.1")
        self.assertIn("127.0.0.1", x["embedding"]["dense"]["api_base"])
    def test_weak_root_key_rejected(self):
        with self.assertRaises(ValueError):
            p11.config("/tmp", 19389, "x")
    def test_out_of_bound_timeout_fails_closed(self):
        with self.assertRaises(ValueError):
            p11.run(execute=True, upstream_path=Path("/none"), timeout_s=1)

    def test_startup_diagnostic_classification_without_raw_secrets(self):
        secret="operator-only-unpublished-secret-value"
        failure=p11.classify_startup_failure("ValidationError: unknown config\\n" + secret)
        self.assertEqual(failure, "CONFIG_VALIDATION")
        self.assertNotIn(secret, failure)
    def test_startup_unknown_error_has_fixed_code(self):
        self.assertEqual(p11.classify_startup_failure("something private x_42"), "UNCLASSIFIED_PROCESS_EXIT")
    def test_native_vector_failure_classified_without_payload(self):
        self.assertEqual(p11.classify_startup_failure("PersistStore initialize failed"), "STORAGE_INITIALIZATION")
    def test_http_proxy_bypass_is_configured(self):
        import inspect
        self.assertIn("ProxyHandler({})", inspect.getsource(p11.observe_url))
    def test_port_guard_detects_existing_listener(self):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            sock.listen(1)
            self.assertTrue(p11.port_in_use(sock.getsockname()[1]))

if __name__ == "__main__":
    unittest.main()
