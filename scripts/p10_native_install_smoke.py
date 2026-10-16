"""P10: verify pinned upstream checkout + installed CLI bootstrap, NEVER assert running server."""
from __future__ import annotations
import argparse
import importlib.metadata
import json
import pathlib
import shutil
import subprocess
import sys

EXPECTED_COMMIT = "20f9c11362ad16193b0daa4a414e1095061af427"
EXPECTED_VERSION = "0.5.0"

def report(status, reason, **facts):
    return {
        "phase": "P10", "status": status, "reason_code": reason,
        "upstream_commit_expected": EXPECTED_COMMIT,
        "source_checkout_verified": facts.get("source_checkout_verified", False),
        "installed_version_verified": facts.get("installed_version_verified", False),
        "cli_help_observed": facts.get("cli_help_observed", False),
        "genuine_server_started": False,
        "server_process_attested": False,
        "acl_isolation_verified": False,
        "model_provider_verified": False,
        "production_authorized": False,
    }

def check_install(source: pathlib.Path, *, runner=subprocess.run,
                  executable=shutil.which, version=importlib.metadata.version):
    if not source.is_dir() or not (source / ".git").exists():
        return report("HOLD", "UPSTREAM_SOURCE_NOT_PRESENT")
    try:
        check = runner(["git", "-C", str(source), "rev-parse", "HEAD"],
                       capture_output=True, text=True, check=False, timeout=15)
        if check.returncode != 0 or check.stdout.strip() != EXPECTED_COMMIT:
            return report("HOLD", "UPSTREAM_SHA_MISMATCH")
        if version("openviking") != EXPECTED_VERSION:
            return report("HOLD", "INSTALLED_VERSION_MISMATCH", source_checkout_verified=True)
        cli = executable("openviking-server")
        if not cli:
            return report("HOLD", "CLI_NOT_INSTALLED", source_checkout_verified=True,
                          installed_version_verified=True)
        result = runner([cli, "--help"], capture_output=True, text=True,
                        check=False, timeout=45)
        if result.returncode != 0 or "usage" not in (result.stdout + result.stderr).lower():
            return report("HOLD", "CLI_BOOTSTRAP_FAILED", source_checkout_verified=True,
                          installed_version_verified=True)
        return report("OBSERVED_PASS", "PINNED_SOURCE_AND_CLI_READY",
                      source_checkout_verified=True, installed_version_verified=True,
                      cli_help_observed=True)
    except (OSError, subprocess.TimeoutExpired, ValueError,
            importlib.metadata.PackageNotFoundError):
        return report("HOLD", "EXECUTION_OR_PACKAGE_UNAVAILABLE")

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--upstream-path", type=pathlib.Path, required=True)
    x = parser.parse_args(argv)
    result = check_install(x.upstream_path) if x.execute else report("HOLD", "NOT_EXECUTED")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "OBSERVED_PASS" else 2

if __name__ == "__main__":
    sys.exit(main())
