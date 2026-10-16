# P02 Evidence and Acceptance Matrix — 2026-10-16

| Gate | Requirement | Evidence | Status |
|---|---|---|---|
| P02-01 | Read v0.1 canonical state | P01 handoff + code inspected | PASS |
| P02-02 | Exact upstream release pin | GitHub API tag commit `20f9c113...` | PASS |
| P02-03 | Read-only HTTP contract | Local HTTP fixture with real loopback socket; 50 tests | PASS_SIMULATED |
| P02-04 | v0.5.0 `result` envelope compatibility | Adapter patched, fixture assertion | PASS_SIMULATED |
| P02-05 | Reject dev mode/version mismatch | Test suite | PASS_SIMULATED |
| P02-06 | Reject inherited wildcard ACL | Test suite | PASS_SIMULATED |
| P02-07 | User identity and non-owner denial | Two-fixture-principal HTTP test | PASS_SIMULATED |
| P02-08 | Scope confinement | Cross-project returned hit triggers exception | PASS_SIMULATED |
| P02-09 | Local source hash link | Source store binding tests; source authenticity remains unverified | PASS_LOCAL |
| P02-10 | Actual OpenViking v0.5.0 server | Requires configured VLM/embedding model and installation | NOT_RUN |
| P02-11 | Live OpenViking ACL enforcement | Need two real user keys, one protected corpus | NOT_RUN |
| P02-12 | GitHub and Drive live source import | No live FCF canonical connector transfer | NOT_RUN |
| P02-13 | Crash/reindex reconciliation on native server | No native server run | NOT_RUN |
| P02-14 | Legal/copyright clearance for deploy/distribution | Review outstanding | HOLD |
| P02-15 | Production promotion/security gate | Separate identity/policy runtime not delivered | HOLD |

**Important:** All test-passing claims above concern either reference kernel behavior or the simulated API contract. No genuine OpenViking binary/package was downloaded or executed in the artifact runtime due to disabled container DNS and absent model-service credentials.
