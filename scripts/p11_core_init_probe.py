"""Disposable P11 native core-init experiment; no HTTP or tenant certification."""
from __future__ import annotations
import argparse
import asyncio
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import tempfile
import traceback

PIN = "20f9c11362ad16193b0daa4a414e1095061af427"
ALLOWED = frozenset({"RuntimeError", "ValueError", "TypeError", "KeyError",
    "AttributeError", "ImportError", "ModuleNotFoundError", "FileNotFoundError",
    "OSError", "PermissionError", "ConnectionError", "TimeoutError",
    "ValidationError", "NotInitializedError", "EmbeddingConfigurationError", "SystemExit"})

def frame_stage(path: str) -> str:
    v = path.lower().replace("\\", "/")
    if "/openviking/storage/" in v: return "C2_STORAGE"
    if "/openviking/service/core.py" in v: return "C2_SERVICE_CORE"
    if "/openviking/utils/agfs_utils.py" in v or "/openviking/pyagfs/" in v: return "C2_AGFS"
    if "/openviking/config/" in v or "/openviking_cli/utils/config/" in v: return "C1_CONFIG"
    if "/openviking/server/auth/" in v: return "C3_AUTH"
    return "OTHER"

def aligned_synthetic_config(document: dict) -> dict:
    """One controlled hypothesis: align local vector dimension with dense embedding."""
    import copy
    fixture = copy.deepcopy(document)
    dense = fixture["embedding"]["dense"]
    dim = dense["dimension"]
    if type(dim) is not int or not (1 <= dim <= 8192):
        raise ValueError("invalid fixture dimension")
    if fixture["storage"]["vectordb"].get("backend") != "local":
        raise ValueError("nonlocal vector backend forbidden")
    fixture["storage"]["vectordb"]["dimension"] = dim
    return fixture


def embedding_failure_site(exc: BaseException) -> str:
    """Only exact reviewed upstream strings; no error messages in published output."""
    if type(exc).__name__ != "EmbeddingConfigurationError":
        return "NOT_APPLICABLE"
    signatures = {
        "Existing collection metadata is unavailable; cannot validate embedding compatibility": "COLLECTION_METADATA_UNAVAILABLE",
        "Local context collection does not support automatic schema updates": "COLLECTION_SCHEMA_UPDATE_UNSUPPORTED",
    }
    return signatures.get(str(exc), "OTHER_EMBEDDING_CONFIGURATION")


def bounded_exception(exc: BaseException) -> dict:
    kind = type(exc).__name__
    frames = [frame_stage(f.filename) for f in traceback.extract_tb(exc.__traceback__)]
    recognized = [x for x in frames if x != "OTHER"]
    return {"status": "HOLD", "reason_code": "CORE_INITIALIZATION_EXCEPTION",
        "exception_kind": kind if kind in ALLOWED else "OTHER",
        "stage_hint": recognized[-1] if recognized else "UNKNOWN",
        "embedding_failure_site": embedding_failure_site(exc),
        "causal_root_established": False, "service_initialized": False,
        "production_authorized": False}

def hold(reason: str) -> dict:
    if reason not in {"NOT_EXECUTED", "SOURCE_MISSING", "SOURCE_PIN_MISMATCH",
                      "PROBE_SETUP_FAILED"}:
        raise ValueError("unknown hold code")
    return {"status": "HOLD", "reason_code": reason, "service_initialized": False,
            "production_authorized": False, "causal_root_established": False}

async def _init_real_service(conf: Path) -> dict:
    from openviking_cli.utils.config.open_viking_config import OpenVikingConfigSingleton
    OpenVikingConfigSingleton.initialize(config_path=str(conf))
    from openviking.service.core import OpenVikingService
    service = OpenVikingService()
    try:
        await asyncio.wait_for(service.initialize(), timeout=45)
        return {"status": "OBSERVED_PASS",
            "reason_code": "DIRECT_CORE_INITIALIZATION_RETURNED",
            "service_initialized": True, "http_readiness": "NOT_TESTED",
            "model_provider": "INERT_NOT_TESTED", "two_account_acl": "NOT_TESTED",
            "production_authorized": False, "causal_root_established": False}
    finally:
        try:
            await asyncio.wait_for(service.close(), timeout=8)
        except BaseException:
            pass

def _isolated_native(conf: Path) -> dict:
    """Discard native OS stdout/stderr; restore only for bounded JSON."""
    old_out, old_err = os.dup(1), os.dup(2)
    devnull = os.open(os.devnull, os.O_WRONLY)
    try:
        sys.stdout.flush()
        sys.stderr.flush()
        os.dup2(devnull, 1)
        os.dup2(devnull, 2)
        try:
            return asyncio.run(_init_real_service(conf))
        except BaseException as exc:
            return bounded_exception(exc)
    finally:
        os.dup2(old_out, 1)
        os.dup2(old_err, 2)
        os.close(old_out)
        os.close(old_err)
        os.close(devnull)

def run(execute: bool, upstream_path: Path) -> tuple[dict, int]:
    if not execute: return hold("NOT_EXECUTED"), 2
    if not upstream_path.is_dir() or not (upstream_path / ".git").exists():
        return hold("SOURCE_MISSING"), 2
    try:
        r = subprocess.run(["git", "-C", str(upstream_path), "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=10, check=False)
        if r.returncode != 0 or r.stdout.strip() != PIN:
            return hold("SOURCE_PIN_MISMATCH"), 2
    except (OSError, subprocess.TimeoutExpired):
        return hold("SOURCE_PIN_MISMATCH"), 2
    try:
        import p11_native_http_smoke as original
        with tempfile.TemporaryDirectory(prefix="fcf-p11-core-") as tmp:
            config_file = Path(tmp, "ov.conf")
            synthetic = original.config(str(Path(tmp, "workspace")), 19391,
                                        secrets.token_urlsafe(48))
            config_file.write_text(json.dumps(aligned_synthetic_config(synthetic)),
                                   encoding="utf-8")
            os.chmod(config_file, 0o600)
            os.environ["OPENVIKING_CONFIG_FILE"] = str(config_file)
            result = _isolated_native(config_file)
    except BaseException:
        result = hold("PROBE_SETUP_FAILED")
    result = {"phase": "P11_CORE_PROBE", "upstream_source_target": PIN,
              "synthetic_dimension_alignment": "EXPERIMENTAL_VECTOR_EQUALS_DENSE",
              **result}
    return result, 0 if result["status"] == "OBSERVED_PASS" else 2

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--upstream-path", type=Path, required=True)
    x = p.parse_args(argv)
    result, code = run(x.execute, x.upstream_path)
    print(json.dumps(result, sort_keys=True))
    return code

if __name__ == "__main__":
    raise SystemExit(main())
