# Ω-OV-P02 — Local OpenViking 0.5.0 Integration Runbook

**Status:** Operator-executable runbook. **NOT EXECUTED** against genuine OpenViking in this release. Install requires network access, an isolated host, and model-provider configuration. DO NOT load confidential or unpublished research material.

## Verified source contract

- Upstream repository: https://github.com/volcengine/OpenViking
- Target Git commit: `20f9c11362ad16193b0daa4a414e1095061af427` (tag `v0.5.0`, verified through upstream GitHub API)
- Observed frontier reference: `842ae41e4b2852a3a216004362db0adac49a8fd2` (not a deployment target)
- HTTP API: `GET /health`, `GET /ready`, `GET /api/v1/system/status`, `GET /api/v1/acl?uri=...`, `GET /api/v1/fs/stat?uri=...`, and `POST /api/v1/search/find`.
- References: upstream `docs/en/api/07-system.md`, `docs/en/api/06-retrieval.md`, `docs/en/api/12-acl.md`, `docs/en/guides/04-authentication.md` on tag `v0.5.0`.

## Host preparation

1. Use an isolated Linux host/VM with Python 3.10+ and internet connectivity, the `uv` installer, and a working embedding/VLM provider. Do not put credentials in Git or this package. Do not open public ports.
2. Install by pinned source commit (review third-party dependencies, all package licenses, and build output first):

   ```bash
   uv tool install --python 3.12 'git+https://github.com/volcengine/OpenViking.git@20f9c11362ad16193b0daa4a414e1095061af427'
   openviking-server init
   openviking-server doctor
   ```

   **Unexecuted:** installation command is a proposed pinned source installation. The README's regular `uv tool install openviking` is simpler but is not commit-pinned. Neither gives a complete audited transitive dependency lock by itself.
3. Review generated `~/.openviking/ov.conf`. Select `server.host=127.0.0.1`, `server.auth_mode=api_key`, a strong root key, and separate workspace and backup paths. Use separate model-provider keys; reject `dev` or `trusted` mode for this evaluation. Secure the config file and encryption root key. If OpenViking setup defaults conflict with these controls, stop.
4. Start foreground `openviking-server` in the isolated environment. Verify `GET http://127.0.0.1:1933/health` reports `healthy:true`, `auth_mode:api_key`, `version:0.5.0` and `/ready` reports `status:ready`. The conformance probe will enforce these preconditions.

## Create an isolated synthetic account

Use `api_key` authentication; ROOT creates accounts and users, not research data. The exact upstream v0.5 endpoints are:

```text
POST /api/v1/admin/accounts
{ "account_id": "fcf-p02-lab", "admin_user_id": "fcf-admin" }
POST /api/v1/admin/accounts/fcf-p02-lab/users
{ "user_id": "fcf-researcher", "role": "user" }
POST /api/v1/admin/accounts/fcf-p02-lab/users
{ "user_id": "fcf-outsider", "role": "user" }
```

Use an authenticated administrator to activate `acl.enabled=true` for that **account**; this switch is **off by default**. On release v0.5.0, the documented operator command is `ov --sudo admin set-account-settings fcf-p02-lab --acl-enabled true`, or the legacy `PATCH /api/v1/admin/accounts/fcf-p02-lab/settings` with body `{"acl":{"enabled":true}}`. Do not assume adding an ACL to a folder activates enforcement.

Put the three returned user/admin API keys in a password manager or a local credentials file with permissions 0600. Never check them into Git, never paste them into a manuscript, and never pass ROOT credentials to the probe.

## Create protected synthetic resource

Using the account ADMIN identity, create the shared project root **with restricted ACL before importing** to avoid a window of broad inherited access:

```bash
ov mkdir viking://resources/fcf-p02-synthetic \
  --acl '{"acl_mode":"restricted","entries":[{"principal":"user:fcf-researcher","level":"read"}]}'

ov add-resource ./fixtures/p02/synthetic_note.md \
  --to viking://resources/fcf-p02-synthetic/synthetic_note.md \
  --wait --timeout 120

ov acl get viking://resources/fcf-p02-synthetic
ov task status <task_id-if-returned>
```

The commands assume `ov` has been configured with an account ADMIN key and points to the matching local server. Confirm the final URI (`ov tree`) because parser output can be organized into generated subpaths. If the final URI differs, supply the actual path to `--expected-hit-uri` in the probe below. Do **not** loosen the ACL to make a test pass. Confirm import processing reached the terminal `completed` state: an accepted task or an empty pending queue is not sufficient.

## Run probe with two distinct unprivileged user keys

```bash
# Make the operator-set variables available in THIS shell without displaying them:
# FCF_P02_USER_KEY         = key issued to fcf-researcher
# FCF_P02_OUTSIDER_KEY     = key issued to fcf-outsider

PYTHONPATH=src python -m fcf.integration \
  --base-url http://127.0.0.1:1933 \
  --project fcf-p02-synthetic \
  --expected-user fcf-researcher \
  --foreign-user fcf-outsider \
  --expected-hit-uri viking://resources/fcf-p02-synthetic/synthetic_note.md
```

The probe performs only read-only requests. It tests: claimed release, auth mode, health, readiness, authenticated user identity, effective root ACL, scoped search, and explicit denial of project-root `stat` for a separate same-account USER key. Exit 0 means **limited P02 probes passed**, not an unrestricted security certification or production authorization. Failure or missing credentials yields `HOLD` and nonzero exit.

## Additional acceptance testing (not automated by the probe)

- Supply a snapshot identity manifest that ties the *actual read bytes* of the synthetic source to the source hash, rather than trusting a retrieval preview.
- Kill the server between import and semantic index completion; restart and assess the durable task, index consistency, and source content.
- Inject an unavailable embeddings service and test timeout/circuit behavior without secrets in logs.
- Test distinct account identities, plus members of the same account, with both empty and non-empty search data.
- Verify that OVPack exports, logs, backup targets, vector indexes and gateway SQLite are protected separately.
- Test that model-generated conclusions cannot change FCF's canonical state.

## Production gates

1. Passing this conformance probe does not establish remote-source cryptographic authenticity.
2. ACL read checks are per path/principal, not a universal proof of tenant isolation.
3. External source ingestion must be separately authorized and versioned.
4. AGPL and the upstream README's rewriting notice require licensing review.
5. No background work or external repository changes are created by this package.
