# Ω-OV-P03 — Genuine OpenViking v0.5.0 Evidence Protocol

**Status:** Offline read-only client contract implemented and locally tested, **genuine OpenViking server NOT RUN** in this environment. **No production authorization.**

## Governing source

- Tagged upstream: `volcengine/OpenViking`, tag `v0.5.0`, commit `20f9c11362ad16193b0daa4a414e1095061af427`.
- Original contract on tagged commit: `docs/en/api/07-system.md` (`/health`, `/ready`, `/api/v1/system/status`, `/api/v1/system/consistency`), `docs/en/api/06-retrieval.md` (`/api/v1/search/find`), `docs/en/api/12-acl.md` (`/api/v1/acl`), `docs/en/api/12-content.md` (`/api/v1/content/download`), `docs/en/guides/04-authentication.md`.
- Current FCF P03 probes cannot cryptographically authenticate the runtime binary; an operator must independently verify the package source and process image.

## 0. Isolated server and credentials

Use the P02 runbook for pinned installation and sandbox setup. Requirements:

1. Isolated operator-owned Linux VM or sandbox; Python 3.10+; required model provider and embeddings; no confidential GILC documents.
2. `uv tool install --python 3.12 'git+https://github.com/volcengine/OpenViking.git@20f9c11362ad16193b0daa4a414e1095061af427'` after source/dep approval; this command is a proposal **not executed** in ChatGPT runtime.
3. Configure `server.host=127.0.0.1`, `auth_mode=api_key`, strong root key stored out of the repository, and `acl.enabled=true` **for the chosen account**.
4. Create one synthetic account and two ordinary USER principals. A ROOT key must never be passed to FCF.
5. Create `viking://resources/fcf-p03-synthetic` as a `restricted` ACL directory granting only the test reader `read` (plus admin implicit management). The other USER must have no granted rights.
6. Validate `GET /health` and `/ready` from localhost. Ensure the genuine OpenViking process actually corresponds to the pinned commit.

## 1. Create exact synthetic source data

Source: `fixtures/p03/synthetic_note.md` (included). Use **byte-preserving content creation** rather than parsing/importing a file whose resulting text may change.

```bash
# Set operator CLI to ADMIN credentials outside project repository.
# A synthetic isolated account already exists, with enforced ACL enabled.
ov mkdir viking://resources/fcf-p03-synthetic \
  --acl '{"acl_mode":"restricted","entries":[{"principal":"user:fcf-p03-owner","level":"read"}]}'
ov write viking://resources/fcf-p03-synthetic/synthetic_note.md \
  --from-file fixtures/p03/synthetic_note.md --mode create
# Do not proceed until resource is indexed and synthetic sentinel is findable.
sha256sum fixtures/p03/synthetic_note.md
ov system consistency viking://resources/fcf-p03-synthetic
```

The `ov write` command must use an authorized ADMIN operator identity; it is **NOT invoked by the FCF probe**. For reproducibility use `sha256sum` on the exact file present on the operator workstation after any newline conversion. Never weaken ACLs to make the test pass.

## 2. Run bounded read-only acceptance

```bash
# Export secrets only in the operator's private shell/session.
export FCF_P03_USER_KEY='<test-owner-USER-key>'
export FCF_P03_OUTSIDER_KEY='<foreign-USER-key>'
export FCF_EXPECTED_SHA256="$(sha256sum fixtures/p03/synthetic_note.md | awk '{print $1}')"

PYTHONPATH=src python -m fcf.integration.p03_cli \
  --base-url http://127.0.0.1:1933 \
  --project fcf-p03-synthetic \
  --expected-user fcf-p03-owner \
  --foreign-user fcf-p03-foreign \
  --file-uri viking://resources/fcf-p03-synthetic/synthetic_note.md \
  --expected-sha256 "$FCF_EXPECTED_SHA256" \
  --query FCF-P03-SENTINEL-f12e92
```

The probe only performs network reads, with one **non-mutating POST** for `/api/v1/system/consistency` (the upstream v0.5.0 API requires POST for that report). The requested file URI is constrained to one project subtree. Redirects, oversized responses and output secrets are rejected. A nonzero exit indicates HOLD, not that the operator should disable a security control.

The tool verifies:
- `/health` claims `healthy=true`, exact `0.5.0`, `auth_mode=api_key`.
- `/ready` returns `ready` and system status reports the expected user.
- ACL effective entries show a `restricted` project root with no user wildcard and expected user entry.
- Semantic retrieval yields the exact synthetic file URI.
- Raw bytes downloaded from `/api/v1/content/download` have the **operator-supplied** SHA-256 digest.
- `/api/v1/system/consistency` reports `ok=true` for this subtree.
- A distinct unprivileged user is independently identified and forbidden both directory `stat` and file binary download.

**What PASS does not mean:** it does not prove universal cross-account isolation, authentic upstream process identity, science truth, native crash recovery, license compliance, or production readiness.

## 3. Independent experiments — separate from P03 probe

The following gates remain to be executed on a genuine server:

- Full process restart after ingest, before semantic work completes, then verify task status, bytes, and index.
- Kill worker while queue processing; record `pending + processing`, recovery, and final status; never confuse empty pending with success.
- Simulate loss of embedding/VLM availability with bounded timeouts and no secret-bearing logs.
- Verify account A cannot read account B (different **account** principal, not only user under same account), including `find`, `stat`, `read` and downloads.
- Verify native OpenViking `acl.enabled` really is active; directory ACL alone is insufficient.
- Verify OVPack export confidentiality, encrypted file storage, vector index metadata, and backup policy.
- Run an evaluation against a canonical **public** snapshot that is independently source-authenticated and signed by an authorized source registry.

## 4. Required operator-supplied evidence

A genuine-server acceptance bundle must include sanitized outputs of: `uv tool list` / exact installed Git commit, `health`, `ready`, `system/status`, `acl_get`, `find`, byte-hash readback, index-consistency, failed unauthorized requests, restart journal, and absence of leaked API keys. Keep secrets out of all committed records.

**Authoritative Google Drive continuity:** https://drive.google.com/drive/folders/PROJECT_FOLDER_ID_REDACTED

**Final judgment:** until independent genuine-server and identity-isolation evidence exists, `NATIVE_LIVE=HOLD`, `PRODUCTION_AUTHORIZATION=HOLD`.
