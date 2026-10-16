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

## Verified outcome — 16 October 2026

The **real external installation and CLI smoke passed** in the [GitHub Actions run 38922647102](https://github.com/Ivan-Pasev/fabrica-context-fabric/actions/runs/38922647102) on the P10 review commit `afe7bb7d7c02f387a43526427531d86a898ca813`: the runner checked out OpenViking commit `20f9c11362ad16193b0daa4a414e1095061af427`, built and installed `openviking==0.5.0` with 167 packages (including `openviking-sdk==0.1.15`), then successfully executed `openviking-server --help`. The checker emitted `OBSERVED_PASS/PINNED_SOURCE_AND_CLI_READY` and expressly `genuine_server_started=false`, `acl_isolation_verified=false`, `server_process_attested=false`, `production_authorized=false`.

[PR #5](https://github.com/Ivan-Pasev/fabrica-context-fabric/pull/5) was merged into public `main` at `77db01f413e66e07f2c4ccadb814f94174105368`. Post-merge GitHub Actions passed on Python 3.10/3.12, including 119 reference tests and exact 87-file/86-digest original manifest parity. Revalidating this runbook itself does not launch a native OpenViking service.

**Accepted gate:** `P10_UPSTREAM_CLI_SMOKE=OBSERVED_PASS`.
**Outstanding:** `GENUINE_RUNNING_SERVER=HOLD`; `TENANT_ISOLATION=HOLD`; `PROCESS_ATTESTATION=HOLD`; `MODEL_PROVIDER=HOLD`; `LEGAL_AND_SECURITY=HOLD`; `PRODUCTION=HOLD`. See [P11 native server issue #6](https://github.com/Ivan-Pasev/fabrica-context-fabric/issues/6).
