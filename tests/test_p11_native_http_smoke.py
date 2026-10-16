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


    def test_missing_native_configuration_module_holds(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "ov.conf")
            path.write_text("{}", encoding="utf-8")
            result = p11.schema_preflight(path)
            # Reference CI deliberately has no OpenViking; fail closed, no details.
            self.assertEqual(result["status"], "HOLD")
            self.assertEqual(result["reason_code"], "UPSTREAM_CONFIG_PREFLIGHT_FAILED")
            self.assertIn(result["exception_kind"], {"ModuleNotFoundError", "ImportError"})

    def test_schema_preflight_accepts_valid_mocked_upstream_validator(self):
        import sys, types, json, tempfile
        from unittest.mock import patch
        pkg_names = ("openviking", "openviking.server", "openviking.server.config",
                     "openviking_cli", "openviking_cli.utils", "openviking_cli.utils.config",
                     "openviking_cli.utils.config.open_viking_config")
        mods = {name: types.ModuleType(name) for name in pkg_names}
        for name, value in mods.items():
            if name not in ("openviking.server.config", "openviking_cli.utils.config.open_viking_config"):
                value.__path__ = []
        class ServerCfg:
            host = "127.0.0.1"
            def get_effective_auth_mode(self):
                return "api_key"
        class OVConfig:
            @classmethod
            def from_dict(cls, doc):
                return types.SimpleNamespace(
                    storage=types.SimpleNamespace(workspace=doc["storage"]["workspace"]),
                    embedding=types.SimpleNamespace(dense=object()))
        mods["openviking.server.config"].load_server_config = lambda path: ServerCfg()
        mods["openviking.server.config"].validate_server_config = lambda cfg: None
        mods["openviking_cli.utils.config.open_viking_config"].OpenVikingConfig = OVConfig
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "ov.conf")
            path.write_text(json.dumps({"storage": {"workspace": "/tmp/synthetic"}}))
            with patch.dict(sys.modules, mods):
                result = p11.schema_preflight(path)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["exception_kind"], "NONE")

    def test_incidental_embedding_word_not_root_cause(self):
        self.assertEqual(p11.classify_startup_failure(
            "Traceback at any/embedding/module.py; TypeError: unrelated"),
            "UNCLASSIFIED_PROCESS_EXIT")

    def test_schema_preflight_does_not_leak_configuration_error(self):
        import sys, types, json, tempfile
        from unittest.mock import patch
        mods = {k: types.ModuleType(k) for k in (
            "openviking", "openviking.server", "openviking.server.config",
            "openviking_cli", "openviking_cli.utils", "openviking_cli.utils.config",
            "openviking_cli.utils.config.open_viking_config")}
        for name, mod in mods.items():
            if name not in ("openviking.server.config", "openviking_cli.utils.config.open_viking_config"):
                mod.__path__ = []
        secret = "sensitive-never-export-this"
        def bad_loader(path):
            raise ValueError(secret)
        mods["openviking.server.config"].load_server_config = bad_loader
        mods["openviking.server.config"].validate_server_config = lambda x: None
        mods["openviking_cli.utils.config.open_viking_config"].OpenVikingConfig = object
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "ov.conf")
            path.write_text("{}")
            with patch.dict(sys.modules, mods):
                report = p11.schema_preflight(path)
        self.assertEqual(report["status"], "HOLD")
        self.assertEqual(report["exception_kind"], "ValueError")
        self.assertNotIn(secret, str(report))


    def test_bounded_traceback_stage_and_error_type(self):
        secret="api_key=never-print-my-secret"
        fake='Traceback (most recent call last):\n  File "/private/openviking/service/core.py", line 27, in initialize\nRuntimeError: '+secret
        result=p11.traceback_stage_hint(fake)
        self.assertEqual(result["stage_hint"],"C2_CORE")
        self.assertEqual(result["exception_kind"],"RuntimeError")
        self.assertFalse(result["causal_root_established"])
        self.assertNotIn(secret,str(result))
        self.assertNotIn("/private",str(result))

    def test_traceback_unknown_fails_closed(self):
        result=p11.traceback_stage_hint('warning password=secret \nProprietaryError: failed')
        self.assertEqual(result["stage_hint"],"UNKNOWN")
        self.assertEqual(result["exception_kind"],"NOT_OBSERVED")
        self.assertFalse(result["causal_root_established"])

    def test_traceback_prioritizes_last_recognized_frame_only(self):
        raw='  File "/tmp/openviking/server/bootstrap.py", line 4, in main\n' + \
            '  File "/tmp/openviking/storage/vectordb/init.py", line 8, in initialize\nValueError: secret'
        result=p11.traceback_stage_hint(raw)
        self.assertEqual(result["stage_hint"],"C2_STORAGE")
        self.assertEqual(result["exception_kind"],"ValueError")

if __name__ == "__main__":
    unittest.main()
