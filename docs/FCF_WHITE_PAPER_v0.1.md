# FABRICA Context Fabric v0.1: Evidence-Bound Context Governance for Agentic Systems

**Research and engineering preprint (reference design, not peer-reviewed)**  
**Date:** 16 October 2026  
**Program:** FAB.SYS / GILC CodexStation  
**Upstream reference:** OpenViking v0.5.0 (independent project; see provenance lock)

## Abstract

Agentic applications increasingly persist documents, memories, conversation histories, and procedural skills in shared retrieval systems. Persisted context improves continuity but exposes an authority-confusion failure mode: a model may treat an automatically extracted memory, retrieved instruction, or generated knowledge summary as equivalent to an authenticated source or executable authorization. FABRICA Context Fabric (FCF) v0.1 addresses a restricted aspect of this problem through a dependency-free, independently authored reference kernel that separates source observations, structural integrity verification, memory proposals, and human-review eligibility. The design uses source-byte SHA-256 digests, canonical record hashes, immutable local snapshots, project-scoped references, declared-conflict holds, and read-only adapters for pinned GitHub content, connector-supplied Google Drive exports, and OpenViking retrieval. This artifact does not authenticate cloud-source authors, verify semantic truth, promote claims to canon, or prove security against arbitrary downstream prompt injection. Unit and schema checks test the implementation's local reference properties; live substrate integration and formal authority are deferred to P02/P03.

## 1. Problem definition

A modern agent process encounters four distinguishable classes of information: external source material, persistent model-derived memory, reusable procedural guidance, and authority-bearing instructions. These classes may all be representable as text and searchable by a shared retrieval engine. If context is treated as an undifferentiated string, an instruction embedded in a PDF can be confused with an orchestration command, and an unreviewed model summary can become indistinguishable from a scientific claim supported by a proof artifact.

Let `C` denote a context record and `A(C)` denote its permitted authority. A retrieval action may change the set of records available to the model, but must not alter `A(C)`. A summarization action may create a derivative record `D(C)`, but must not increase the derivative's authority without a separate trusted transition. This is a governance property, not a claim of perfect semantic understanding.

## 2. Upstream substrate

OpenViking exposes an addressable `viking://` namespace containing resources, memories, and skills. Its retrieval API includes `POST /api/v1/search/find`; its session engine captures interactions and extracts long-term memory, while context compilation can derive Wikis and knowledge graphs. A model-driven extraction engine can produce structurally valid but factually false memories; a retrieved URI similarly does not independently identify the source revision or validate its epistemic status. For these reasons, FCF is deliberately a separate control layer rather than an upstream replacement.

Primary implementation references:
- https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/api/06-retrieval.md
- https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/concepts/08-session.md
- https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/concepts/09-transaction.md
- https://github.com/volcengine/OpenViking/blob/v0.5.0/LICENSE

## 3. Typed records and authority discipline

An observed source is modeled as:

`S=(project, source_system, source_uri, revision, mime, content_sha256, content_bytes, observed_at, state)`.

The local record's SHA-256 is computed from deterministic UTF-8 JSON encoding of those fields plus explicit status markers, excluding the digest field itself. This proves byte consistency between a stored record and its content when both are held in a trusted local store. It does not authenticate the origin of the content or prove that a source revision string is honest. For this reason the observed record always has `source_authenticity=NOT_VERIFIED`, `state=OBSERVED`, and `semantic_truth=NOT_PROVEN`.

A memory proposal is modeled as:

`M=(project, claim, source_record_hashes, conflict_keys, PROPOSED, NONE, NOT_PROVEN)`.

Structural assessment may result in `HOLD` or `ELIGIBLE_FOR_HUMAN_REVIEW`. It does not issue a canonical-write token. For example, a competing hypothesis pair `H1: λ=0` and `H2: λ≠0` is preserved as separate source assertions if declared in conflict; the current engine does not attempt to adjudicate their mathematical truth.

## 4. Transition discipline

The reference state machine intentionally lacks an edge from `PROPOSED` to `CANONICAL`.

```text
UNTRUSTED_BYTES -> OBSERVED_SOURCE -> PROPOSED_MEMORY -> STRUCTURAL_ASSESSMENT
                                      |                      |
                                      |                      +-> HOLD
                                      |                      +-> ELIGIBLE_FOR_HUMAN_REVIEW
                                      |
                                      +-- no autonomous canonical promotion
```

A production state machine could add verified approval, publication and supersession transitions later, but only after independent identity and authorization evidence is available. A user-controlled CLI role string must not be mistaken for a verified identity.

## 5. Source adapters and source authority

The GitHub adapter takes an explicit 40-character commit SHA, owner, repository and normalized relative path, then reads the raw file through HTTPS without redirects. The Drive adapter accepts an exported byte snapshot and its claimed file/revision identifiers from a caller with external connector permission. The OpenViking adapter performs a project-scoped retrieval request, has no methods to modify the server, bounds responses, rejects redirects and remote plaintext HTTP, and checks that returned resources are within the requested project prefix. These measures reduce accidental scope escape and control/data confusion; they do not replace server-side identity, ACLs, or independent document provenance.

## 6. Consistency and recovery

The local store uses SHA-named blobs and records. For creation it fsyncs temporary bytes and uses no-clobber link creation, so failed writes before publication do not create a visible final object. This does not constitute a distributed transaction, a cryptographically signed event log, or multi-writer storage. A privileged local attacker can tamper with raw objects; integrity verification detects many such modifications at subsequent reads but cannot defeat all rollback attacks without an independent trust anchor.

OpenViking's storage documentation describes separate content/index/queue components and no universal atomic transaction. A future connector must reconcile cross-store state after incomplete operations and verify source versions before promotion.

## 7. Validation methodology and preliminary results

The package includes automated tests for record byte integrity, source metadata alteration, forged canonical status, project scope violations, missing evidence, declared conflicts, invalid roles, unsafe GitHub file paths, unpinned source revisions, OpenViking response escapes and interrupted local publication. These tests exercise the isolated kernel and mock adapter boundaries; they do not exercise a real OpenViking service or actual Google Drive export. Three JSON Schemas validate generated source, memory proposal, and assessment specimens. The audit report in `validation/` records exact executed tests.

No claim is made that these tests demonstrate arbitrary prompt-injection immunity, authenticated cloud-source revision fidelity, formal mathematical correctness, or production-ready security.

## 8. Research agenda

The next engineering phase should conduct live isolated OpenViking evaluation with an authenticated server and synthetic corpus; measure retrieval-source-version agreement, index consistency under injected failures, and cross-tenant access denial. The following phase must add authenticated origin attestation and signing or equivalent trusted approval, tied to exact document and proposal hashes. A separate adversarial program should evaluate claim contamination, provenance laundering, time-of-check/time-of-use races, model-assisted instruction injection and rollback integrity.

## 9. Conclusion

OpenViking is a suitable subject for substrate experimentation because it unifies agent resources, memories and skills in an inspectable context interface. FCF's contribution is orthogonal: context is evidence to be interpreted under policy, not a source of authority. v0.1 demonstrates a narrow, executable boundary that can be tested locally. It leaves canonical mutation impossible within this package and records production authorization as an open engineering obligation rather than assuming it is solved.
