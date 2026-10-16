# P11.4 — Direct native core-initialization fault isolation

**Evidence chain (16 October 2026):**
- [P10 real pinned CLI installation](https://github.com/Ivan-Pasev/fabrica-context-fabric/actions/runs/38922647102): PASS.
- [P11 real upstream config validation](https://github.com/Ivan-Pasev/fabrica-context-fabric/actions/runs/38949372339): C1 PASS, child exited before HTTP.
- [P11 stage-hint native experiment](https://github.com/Ivan-Pasev/fabrica-context-fabric/actions/runs/38952056482): FAIL/HOLD. Child exit code **3**; last recognized stack frame `C2_STORAGE`; exception type `NOT_OBSERVED`; all HTTP responses null. The frame is a *location hint*, not root-cause proof.

## Goal
Remove Uvicorn's lifespan error wrapper as a source of diagnostic information loss. In a fresh GitHub Actions runner, pin the exact upstream OpenViking v0.5.0 source SHA `20f9c11362ad16193b0daa4a414e1095061af427`, install the real Python package and call `OpenVikingService.initialize()` directly via its real Python classes, using a disposable workspace and the same deliberately inert provider configuration as the P11 HTTP probe.

## Implementation
- `scripts/p11_core_init_probe.py`: requires explicit `--execute`; verifies checked-out upstream SHA; creates private ephemeral synthetic configuration and random root key; calls actual `OpenVikingConfigSingleton.initialize()` then `OpenVikingService.initialize()`; attempts resource cleanup.
- Native stdout and stderr file descriptors are redirected to `os.devnull` inside the isolated process. Only a fixed JSON observation is emitted after restoration. No root key, model placeholder credential, source path, raw traceback, native error string or user content is surfaced.
- On failure, record only `CORE_INITIALIZATION_EXCEPTION`, an allowlisted exception *class* and last recognized upstream subsystem *category*. Unrecognized exception classes and locations become `OTHER`/`UNKNOWN`, and `causal_root_established=false`.
- On successful direct core init, record `DIRECT_CORE_INITIALIZATION_RETURNED` as a **bounded core-only success**, with `http_readiness=NOT_TESTED`, `two_account_acl=NOT_TESTED`, `model_provider=INERT_NOT_TESTED` and `production_authorized=false`.
- Nine local, dependency-free contract tests exercise no-execute, missing source, error sanitization and deterministic classification. The live CI is a separate evaluation.

## Non-claims and risk controls
A direct `initialize()` result can separate a service failure from Uvicorn/auth plugin orchestration, but **does not** run the HTTP API, prove process/artefact identity beyond the checkout claim, exercise provider connectivity, authenticate users, enforce ACL or authorize production. This is a diagnostic experiment, not a workaround that bypasses required server gates.

Root workspace, account keys, source data and logs must remain synthetic and ephemeral. Upstream AGPL-3.0 remains a separate dependency; no upstream source is vendored into FCF. Stable public release, legal/security review, cross-account isolation and production remain HOLD.

Next: inspect exact native CI result and exception-kind/stage hint. Repair only a source-verified configuration or storage prerequisite, then repeat original C2–C4 HTTP acceptance before progressing.

## P11.5 — Native `EmbeddingConfigurationError` and dimension-alignment trial

The real pinned native core run [38955703188](https://github.com/Ivan-Pasev/fabrica-context-fabric/actions/runs/38955703188) ended FAIL/HOLD with exact exception class `EmbeddingConfigurationError`, categorized stage `C2_STORAGE`, and `causal_root_established=false`. The paired HTTP run [38955703079](https://github.com/Ivan-Pasev/fabrica-context-fabric/actions/runs/38955703079) also failed, child exit code 3, `C2_STORAGE` location hint, and no HTTP status values. These independent observations indicate embedding/vector storage configuration as an area for targeted experimentation, **not a proven root cause**.

Pinned upstream source verifies two direct `EmbeddingConfigurationError` raises in `openviking/storage/collection_schemas.py`: missing existing collection metadata and inability to update a local collection schema. It separately shows `VectorDBBackendConfig.dimension` defaulting to 0 whereas the controlled synthetic fixture sets `EmbeddingModelConfig.dimension=8`. Upstream may normalize or ignore that dimension; no causality should be asserted without a real comparative run.

Next candidate changes only the **direct-core synthetic trial**, setting `storage.vectordb.dimension` to the explicit synthetic dense dimension 8; the genuine HTTP experiment remains an unchanged failing control. A bounded `embedding_failure_site` enum is emitted only for two exact reviewed upstream error strings, otherwise `OTHER_EMBEDDING_CONFIGURATION`. It never publishes arbitrary exception messages, keys or paths. New local tests assert dimension alignment, safety against nonlocal backends, error-code mapping and redaction.

Successful aligned direct-core initialization, if observed, is limited to that specific synthetic configuration and is **not** a validated HTTP service, real embedding provider, effective ACL or production authority. A recurring exception must be preserved as a new failure observation, not interpreted as a contradiction to the prior run.
