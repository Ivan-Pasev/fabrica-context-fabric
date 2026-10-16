# P09 — Genuine OpenViking v0.5.0 acceptance campaign

**State:** operator procedure and offline validator implemented; native OpenViking **NOT RUN** in the current environment. No production permission or certified native integration.

## Pinned sources and scope
- Upstream: [volcengine/OpenViking v0.5.0](https://github.com/volcengine/OpenViking/tree/v0.5.0), git commit `20f9c11362ad16193b0daa4a414e1095061af427`.
- [Quickstart](https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/getting-started/02-quickstart.md), [authentication](https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/guides/04-authentication.md), [ACL](https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/concepts/15-acl.md), [system API](https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/api/07-system.md), [retrieval](https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/api/06-retrieval.md), [content](https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/api/12-content.md).
- The upstream main tree is AGPL-3.0 and remains a **separate dependency**, not vendored into FCF.

## External isolated operator setup (proposed, not executed here)
Use a disposable isolated VM with synthetic text only. Record the OS, source SHA, executable/runtime dependency provenance, sanitized config and the actual process started. Reviewing a git commit alone does not prove which binary is running.

```bash
git clone https://github.com/volcengine/OpenViking.git /opt/openviking-p09
cd /opt/openviking-p09
git checkout --detach 20f9c11362ad16193b0daa4a414e1095061af427
test "$(git rev-parse HEAD)" = 20f9c11362ad16193b0daa4a414e1095061af427
uv tool install --python 3.12 'git+https://github.com/volcengine/OpenViking.git@20f9c11362ad16193b0daa4a414e1095061af427'
openviking-server init
openviking-server doctor
openviking-server
```

Configure localhost binding (127.0.0.1:1933), auth_mode=api_key, required embedding/VLM providers, and account-level ACL enforcement enabled. The OpenViking account ACL default is **disabled**; even when enabled the shared root may inherit `user:* = manage`. Use a restricted project subtree with **no inherited wildcard access**, not a permissive public root. Provision a test account, two distinct ordinary USER identities and separately a second account; no ROOT or ADMIN key may be supplied to the FCF probe.

## Create a single byte-exact synthetic source
As an authorized server operator, create `viking://resources/fcf-p09-synthetic` as a restricted subtree; explicitly grant the owner read permission, deny the outsider. Write `fixtures/p09/synthetic_note.md` preserving bytes at `viking://resources/fcf-p09-synthetic/synthetic_note.md`. Ensure ingestion/index tasks complete; do not treat empty queue as success. The included fixture has sentinel `FCF-P09-SENTINEL-2837d4`.

## Read-only, operator-initiated FCF observation
```bash
export FCF_P09_OWNER_KEY='<ordinary-owner-user-key>'
export FCF_P09_OUTSIDER_KEY='<different-ordinary-user-key>'
export FCF_P09_PROCESS_SHA256='<operator-observed-64-character-lowercase-hex-process-hash>'
export FCF_FIXTURE_SHA256="$(sha256sum fixtures/p09/synthetic_note.md | awk '{print $1}')"
PYTHONPATH=src python -m fcf.integration.p09_cli \
  --execute --base-url http://127.0.0.1:1933 \
  --project fcf-p09-synthetic --expected-user fcf-p09-owner \
  --foreign-user fcf-p09-outsider \
  --file-uri viking://resources/fcf-p09-synthetic/synthetic_note.md \
  --expected-sha256 "$FCF_FIXTURE_SHA256" \
  --query FCF-P09-SENTINEL-2837d4 --operator-reference p09-synthetic-001
```

Default without `--execute` is **HOLD**, exit code 2, zero HTTP requests. Even when the selected HTTP endpoints all behave as expected, the runner returns **READY_FOR_INDEPENDENT_REVIEW**, not a genuine image attestation, separate-account isolation PASS, production approval or scientific proof. Credentials are read from environment and not included in its JSON output. Never publish private runtime configuration, access keys or raw confidential content.

## Independent follow-on gates (not covered by this runner)
1. Independently attest the actual running server process and dependency closure to the pinned OpenViking v0.5.0 source and record a non-secret proof.
2. Verify explicit ACL enforcement and negative `find`, stat, list, read and download for a **different account**, not only another user of the same account.
3. Record a bounded crash/restart and index-recovery campaign; verify actual ingestion task state and repeat byte SHA-256 checks.
4. Simulate model-provider outages and bad indexing without weakening security or leaking secrets.
5. Inspect OVPack exports and storage for plaintext/private source leakage, backups and retention.
6. Complete an AGPL and third-party license obligations assessment, dependency/security report, and human authorization before any stable GitHub release tag.

Native OpenViking: **HOLD**. Process authenticity: **HOLD**. Cross-account isolation: **HOLD**. Stable release and production: **HOLD**.
