"""P11: bounded real OpenViking server HTTP bootstrap; NO tenant/model certification.

Only use in an isolated disposable CI runner. The configured model endpoints are
intentionally inert loopback placeholders; no embedding/VLM call is exercised.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

EXPECTED = "20f9c11362ad16193b0daa4a414e1095061af427"


def config(workspace: str, port: int, key: str) -> dict:
    if not key or len(key) < 40:
        raise ValueError("strong ephemeral root key required")
    return {
        "server": {"host": "127.0.0.1", "port": port, "auth_mode": "api_key",
                   "root_api_key": key,
                   "observability": {"metrics": {"enabled": False},
                                     "usage_audit": {"enabled": False}}},
        "storage": {"workspace": workspace,
                    "vectordb": {"name": "p11-synthetic", "backend": "local"},
                    "agfs": {"backend": "local"}},
        "embedding": {"dense": {"provider": "openai",
                                "model": "synthetic-embedding-not-operational",
                                "api_base": "http://127.0.0.1:19777/v1",
                                "api_key": "inert-synthetic-model-token",
                                "dimension": 8, "input": "text"}},
        "vlm": {"provider": "openai", "model": "synthetic-vlm-not-operational",
                "api_base": "http://127.0.0.1:19777/v1",
                "api_key": "inert-synthetic-model-token"},
    }


def observe_url(url: str, key: str | None = None, timeout: float = 2.0) -> tuple[int | None, dict]:
    headers = {"Accept": "application/json"}
    if key is not None:
        headers["X-API-Key"] = key
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as resp:
            status = resp.status
            raw = resp.read(16385)
    except urllib.error.HTTPError as ex:
        status = ex.code
        raw = ex.read(16385)
    except (OSError, ValueError):
        return None, {}
    if len(raw) > 16384:
        return status, {}
    try:
        value = json.loads(raw.decode("utf-8"))
        return status, value if isinstance(value, dict) else {}
    except (ValueError, UnicodeError):
        return status, {}


def assess(health: tuple[int | None, dict], ready: tuple[int | None, dict],
           anonymous: tuple[int | None, dict], invalid_key: tuple[int | None, dict]) -> dict:
    hs, hv = health
    rs, rv = ready
    s0, _ = anonymous
    si, _ = invalid_key
    health_pass = hs == 200 and hv.get("status") == "ok" and hv.get("healthy") is True
    ready_pass = rs == 200 and rv.get("status") == "ready"
    denied = s0 in (401, 403) and si in (401, 403)
    outcome = "OBSERVED_PASS" if health_pass and ready_pass and denied else "HOLD"
    return {"phase": "P11", "status": outcome, "reason_code": "LOCAL_REAL_SERVER_HTTP_READY" if outcome == "OBSERVED_PASS" else "READINESS_OR_AUTH_DENIAL_INCOMPLETE",
            "http_health": "PASS" if health_pass else "HOLD",
            "http_ready": "PASS" if ready_pass else "HOLD",
            "anonymous_admin_api_denied": "PASS" if denied else "HOLD",
            "observed_http_statuses": {"health": hs, "ready": rs, "anonymous": s0, "invalid_key": si},
            "upstream_source_target": EXPECTED,
            "model_provider": "INERT_LOOPBACK_NOT_VERIFIED",
            "account_acl_enforcement": "NOT_TESTED", "two_user_acl": "NOT_TESTED",
            "cross_account_acl": "NOT_TESTED", "source_integrity": "NOT_TESTED",
            "binary_process_attestation": "NOT_ESTABLISHED",
            "recovery": "NOT_TESTED", "production_authorized": False}


def run(*, execute: bool, upstream_path: Path, timeout_s: float = 90.0, port: int = 19389) -> tuple[dict, int]:
    if not execute:
        return {"phase": "P11", "status": "HOLD", "reason_code": "NOT_EXECUTED", "production_authorized": False}, 2
    if timeout_s < 5 or timeout_s > 180:
        raise ValueError("timeout out of range")
    if not upstream_path.is_dir() or not (upstream_path / ".git").exists():
        return {"phase": "P11", "status": "HOLD", "reason_code": "SOURCE_MISSING", "production_authorized": False}, 2
    try:
        sha = subprocess.run(["git", "-C", str(upstream_path), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True, timeout=10).stdout.strip()
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        sha = None
    if sha != EXPECTED:
        return {"phase": "P11", "status": "HOLD", "reason_code": "SOURCE_SHA_MISMATCH", "production_authorized": False}, 2
    key = secrets.token_urlsafe(48)
    root = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryDirectory(prefix="fcf-p11-synthetic-") as tmp:
        conf = Path(tmp, "ov.conf")
        conf.write_text(json.dumps(config(str(Path(tmp, "workspace")), port, key)), encoding="utf-8")
        os.chmod(conf, 0o600)
        with open(Path(tmp, "server.log"), "wb") as logfile:
            try:
                proc = subprocess.Popen(["openviking-server", "--config", str(conf),
                                         "--host", "127.0.0.1", "--port", str(port)],
                                        stdout=logfile, stderr=subprocess.STDOUT,
                                        env={**os.environ, "NO_COLOR": "1"})
            except OSError:
                return {"phase": "P11", "status": "HOLD", "reason_code": "SERVER_EXECUTABLE_NOT_AVAILABLE", "production_authorized": False}, 2
            try:
                start = time.monotonic()
                health = (None, {})
                while time.monotonic() - start < timeout_s:
                    if proc.poll() is not None:
                        break
                    health = observe_url(root + "/health", timeout=1.5)
                    if health[0] == 200:
                        break
                    time.sleep(1.0)
                ready = observe_url(root + "/ready")
                anon = observe_url(root + "/api/v1/system/status")
                bogus = observe_url(root + "/api/v1/system/status", key="invalid-key-only")
                report = assess(health, ready, anon, bogus)
                report["child_process_spawned"] = True
                report["child_alive_at_probe"] = proc.poll() is None
                report["server_started"] = bool(report["child_alive_at_probe"] and health[0] == 200)
                report["process_identity"] = "SUBPROCESS_LAUNCHED_FROM_PINNED_CHECKOUT_ENVIRONMENT_NOT_INDEPENDENTLY_ATTESTED"
                report["port"] = port
                return report, 0 if report["status"] == "OBSERVED_PASS" else 2
            finally:
                if proc.poll() is None:
                    proc.terminate()
                    try:
                        proc.wait(timeout=8)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                        proc.wait(timeout=5)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--upstream-path", type=Path, required=True)
    p.add_argument("--timeout", type=float, default=90)
    x = p.parse_args(argv)
    result, rc = run(execute=x.execute, upstream_path=x.upstream_path, timeout_s=x.timeout)
    print(json.dumps(result, sort_keys=True))
    return rc

if __name__ == "__main__":
    raise SystemExit(main())
