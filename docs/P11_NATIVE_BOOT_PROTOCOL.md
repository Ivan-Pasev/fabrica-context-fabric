# P11: actual OpenViking localhost HTTP bootstrap gate

**Intent:** move past the P10 *package/CLI* smoke by launching the real pinned OpenViking `openviking-server` binary in an ephemeral GitHub Actions runner and attempting `/health`, `/ready` and an unauthenticated system-status denial. This is a narrow runtime smoke, not account isolation or model verification.

## Boundary of evidence

The harness installs upstream OpenViking from exactly commit `20f9c11362ad16193b0daa4a414e1095061af427` (`v0.5.0`), uses a fresh random root API key saved only in a temporary mode-0600 configuration, binds exclusively to `127.0.0.1:19389`, and supplies unreachable loopback embedding/VLM endpoints intentionally. The test never asks the model provider for a real completion, never imports private data, and never submits root credentials through its public HTTP checks. It writes server logs to a discarded file rather than publishing potentially sensitive configuration. The child process is terminated/force-killed on exit.

Passing conditions: real server subprocess remains alive, `/health` HTTP 200 reports status `ok` and `healthy: true`, `/ready` reports status `ready`, and both anonymous and invalid-key requests to `/api/v1/system/status` receive HTTP 401/403. An explicit `--execute` flag is required; without it the program returns HOLD and makes zero process/network calls.

If the real runtime refuses to initialize without working providers, the test deliberately fails closed and records `HOLD`. Do **not** mock the OpenViking HTTP server itself, skip FastAPI lifespan, accept a 200 with false health, or substitute dev authentication merely to make CI green. Inert providers make `MODEL_PROVIDER_VERIFIED=HOLD` in all cases.

Even if all smoke predicates pass, it is not evidence of a separately authenticated running-process binary, provider functionality, account-level ACL enablement, restricted resource ACLs, source integrity, same-account user separation, **cross-account separation**, asynchronous ingest, index recovery, OVPack protection, complete licensing review or production authorization. It is `P11_REAL_SERVER_LOCAL_HTTP_OBSERVED_PASS` only.

The full campaign remains tracked in [P11 issue #6](https://github.com/Ivan-Pasev/fabrica-context-fabric/issues/6), nested under [P09 parent issue #3](https://github.com/Ivan-Pasev/fabrica-context-fabric/issues/3). Internal canonical R&D source is on Google Drive; public code on GitHub `main` after reviewed merge only.

## Self-check

```bash
python -m unittest discover -s tests -p 'test_p11_native_http_smoke.py' -v
python scripts/p11_native_http_smoke.py --upstream-path /tmp/does-not-exist
# Exits 2, emits HOLD; no HTTP or process launch.
```

## Exit behavior

- Exit `0`, status `OBSERVED_PASS`: bounded local **real-server** health+ready+anonymous-auth-denial observations only.
- Exit `2`, status `HOLD`: missing source/config/readiness/auth denial or process failed. Preserve the failed CI step for a follow-on P11 repair; do not merge failed CI.
