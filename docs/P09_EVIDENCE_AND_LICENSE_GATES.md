# P09 evidence matrix and publication boundaries

| Gate | Decision | Grounded evidence |
|---|---|---|
| P08 reference source `main` | PASS | Verified GitHub SHA `79fe3d803c827e3b2e24cc7b2f5c5a6e532d9303`; original v0.4.0 archive 87-file/86-hash manifest matched |
| P09 offline observation evaluator | LOCAL PASS | Explicit `--execute`, secret-safe fail-closed dry-run and negative tests; **not** a native runtime |
| Upstream OpenViking v0.5.0 running server | HOLD | Executable absent, DNS/package installer unavailable here |
| Account ACL enabled and restricted project | HOLD | Requires operator account-level configuration and real effective ACL enforcement |
| Ordinary-owner versus outsider USER | HOLD | Requires two real authenticated users and denial of stat/download |
| Cross-account isolation | HOLD | Requires *separate account* negative tests |
| Source bytes and vector index | HOLD | Requires real byte-exact resource, post-ingestion source SHA and consistency result |
| Recovery/provider failure | HOLD | Requires real restart, task and index recovery; failed/timeout model calls |
| Process/publisher attestation | HOLD | Operator-supplied SHA alone is a claim, not proof of running identity |
| OpenViking AGPL-3.0 and other dependency obligations | HOLD | Independent FCF Apache-2.0 code does not automatically clear other license obligations |
| Stable public release / production | HOLD | No published stable FCF tag, permission or external security certification |

### Non-promotable observations
A `functional_contract=OBSERVED_PASS` would only describe bounded responses from an endpoint identified by the operator. It cannot be transformed into `genuine_native_gate=PASS` without independent process/runtime attestation, or into legal/security clearance by a machine-generated statement. Use the native canonical R&D handoff for independent review decisions.

### Authority ordering
Live canonical Drive research documents > cached research context. GitHub commit hashes govern public FCF code. OpenViking retrieval remains derived/untrusted. A KBI file, model memory, or FCF HTTP client does not confer tool access or scientific truth.
