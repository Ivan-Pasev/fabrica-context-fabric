# FCF Constitutional Invariants v0.1

Normative terms: **MUST**, **MUST NOT**, **SHOULD**. This is a proposed project specification, **not a formal machine-checked proof**.

## INV-FCF-001: Typed source and derived context
An observation `s` and a derived claim `c` MUST remain distinguishable. Stored `source_authenticity` and `semantic_truth` start `NOT_VERIFIED` and `NOT_PROVEN` respectively.

## INV-FCF-002: Evidence identity
Each observed byte snapshot MUST carry SHA-256 of its original bytes and a canonicalized record digest. The record digest does not authenticate the signer or origin.

## INV-FCF-003: No unreviewed promotion
For any memory proposal `m`, `state(m)=PROPOSED` and `authority(m)=NONE`; no core operation can directly make it canonical.

## INV-FCF-004: No cross-project evidence substitution
Every source used by a proposal MUST belong to its project; cross-project references require separately designed, authorized import contracts.

## INV-FCF-005: Contradiction preservation
Known and declared contradictions cause `HOLD`, without semantic merging. Full semantic contradiction discovery is NOT implemented in v0.1.

## INV-FCF-006: No data-to-control elevation
Retrieved source text MUST NOT be interpreted as authority, credentials, or commands. The kernel treats all source content as bytes.

## INV-FCF-007: Source version and observation
Source record IDs must preserve claimed revision and observation time. A source claim is NOT authenticated until independently attested.

## INV-FCF-008: No implicit agent authorization
Agent claims, model confidence, and role strings are insufficient for production authorization. The offline reference assessment NEVER issues a promotion token.

## INV-FCF-009: Bounded read-only retrieval
The OpenViking adapter MUST confine request target to project scope, refuse out-of-scope returned URIs, refuse remote HTTP, refuse redirects, bound result count, and require operator-listed HTTPS hosts.

## INV-FCF-010: Integrity and recovery
Partial temporary files must not become final snapshot objects. Observations are append-only. This is a single-node local reference; it does not claim cross-store atomicity.

### Proposed formal transition

For a proposed memory `m` with evidence `E`, `ASSESS(m,E)` is structural only:

`ASSESS(m,E) ∈ {HOLD, ELIGIBLE_FOR_HUMAN_REVIEW}`

No transition `PROPOSED -> CANONICAL` exists in the v0.1 implementation.

### P02 proof obligations

- Authenticated reviewer principal cannot be forged by a caller.
- Approval binds exact source/content hashes, policy version, principal, and project.
- Approval checks are enforced independently of model text.
- Adversarial retrieval neither escapes tenant/project scopes nor writes to sources.
- Crash/rebuild testing preserves source integrity or fails visibly.
