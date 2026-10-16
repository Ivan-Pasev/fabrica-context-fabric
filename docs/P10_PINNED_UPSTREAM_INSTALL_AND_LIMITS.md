# P10 — Pinned upstream install smoke: evidence levels and limits

**Source reference:** OpenViking `v0.5.0`, exact upstream commit `20f9c11362ad16193b0daa4a414e1095061af427`.

## What this pipeline verifies

GitHub Actions uses a separate Ubuntu runner (Python 3.12), fetches the upstream Git repository into an ephemeral directory, checks out that exact SHA, installs the editable upstream Python distribution with `uv`, and invokes `openviking-server --help`. A small dependency-free checker verifies the Git checkout HEAD, Python distribution metadata version `0.5.0`, executable presence and a successful help response. The output is a bounded JSON declaration with explicit `genuine_server_started=false`.

This is **real upstream checkout and CLI/package smoke evidence** when the GitHub Actions job passes. It is **not evidence** that a configured server initialized, models or vector indexes operated, any secret was supplied, project ACLs were enforced, or two accounts were isolated. Nor is Git HEAD a binary supply-chain attestation. No OpenViking source is vendored or redistributed into FCF.

## Required follow-on real operational campaign

1. In an isolated, operator-controlled environment, pin the exact commit and separately establish running-process origin (deploy artifact/SBOM provenance).
2. Configure `auth_mode=api_key`, a real supported embedding and VLM provider, local storage, and `acl.enabled=true` for the relevant account. The v0.5.0 ACL default is disabled and root shared resources may inherit broad wildcard grants.
3. Create a new synthetic project under restricted ACL; provision owner and outsider ordinary USER identities. Verify the owner's byte hash and outsider stat/download denial using the P09 CLI.
4. Provision a second **account** and test negative list/stat/search/read/download across account and tenant boundaries; the existing P09 same-account outsider check is not enough.
5. Validate ingestion-task completion and index snapshot consistency before and after restart, service crash, and provider outage.
6. Audit OVPack export, secrets/PII handling, license obligations, and security issues before any stable release approval.

## Reproducibility

```bash
PYTHONPATH=src python -m unittest discover -s tests -p 'test_p10_native_install_smoke.py' -v
python scripts/p10_native_install_smoke.py --upstream-path /tmp/does-not-exist
# HOLD, exit code 2. No source checkout or server launch occurs without --execute.
```

The CI workflow is opt-in for the upstream dependency installation on pull requests that change P10 files, and via `workflow_dispatch` afterwards. It requests read-only repository access and no credentials. Record the **exact GitHub run ID**, installed metadata, upstream SHA and runtime checker result separately from the FCF reference unit suite.

**Current gate:** `P10_UPSTREAM_CLI_SMOKE=PENDING_CI`. `GENUINE_RUNNING_SERVER=HOLD`. `TENANT_ISOLATION=HOLD`. `PRODUCTION=HOLD`.
