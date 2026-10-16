# FABRICA CONTEXT FABRIC

## Constitutional Context Infrastructure for Governed Agent Memory, Source Provenance, and Continuous Engineering

**Working Manuscript v0.3.0 — 16 October 2026**

### Abstract

Persistent AI-agent context is useful, but historical memory and retrieval-ranked documents are not necessarily authoritative. The distinction is particularly important in scientific research and critical engineering, where older versions, abandoned hypotheses, source-of-record differences and execution privileges coexist. FABRICA Context Fabric (FCF) proposes an external governance and evidence framework above a candidate OpenViking context substrate. Its constitutional architecture separates context, authority, evolution and witness. The P03 reference implementation contains a fail-closed source snapshot kernel, proposal assessment, project-scoped retrieval and read-only OpenViking v0.5.0 HTTP protocol observation. Sixty-eight local Python tests passed, including 18 P03 socket tests against an API emulator. Native OpenViking integration remains **unperformed** because no genuine OpenViking server or embedding-provider environment was accessible here.

### 1. Problem statement

The memory of an AI agent may be derived from observations and interactions yet contain unsupported conclusions, misleading instructions or outdated facts. A useful context store is not a proof system or an authorization oracle. The problem is to preserve continuity **without** allowing context extraction or compaction to elevate the authority of an assertion or tool instruction.

### 2. Architectural decomposition

Define a candidate fabric as F = (C, A, E, W), with C the context plane, A the authority plane, E the governed evolution plane and W the provenance/witness plane. OpenViking is evaluated solely for its role within C. FCF's independently authored modules provide constraints at the other planes. The layered architecture does not imply formal correctness without verifying invariants and threat assumptions.

The central identity of a source observation is a tuple of project, source-system, origin reference, version, bytes, time, and content digest. SHA-256 equality attests agreement of examined bytes, but not original publisher control, source authenticity, semantic truth, currentness, or completeness.

### 3. Upstream context substrate

OpenViking v0.5.0 is pinned to commit `20f9c11362ad16193b0daa4a414e1095061af427`. The upstream repository documents `viking://` resources, memories and skills, summarization sidecars, vector retrieval, tenant identity and resource access control. Relevant HTTP endpoints are:

- `GET /health`, `GET /ready`, `GET /api/v1/system/status`;
- `GET /api/v1/acl?uri=...`, `GET /api/v1/fs/stat?uri=...`;
- `POST /api/v1/search/find`;
- `GET /api/v1/content/download?uri=...` for exact server bytes;
- `POST /api/v1/system/consistency` for a read-only vector/file consistency report.

The upstream release documentation warns that ACL enforcement is disabled by default. A permission-bearing directory ACL must not be mistaken for effective enforcement unless the account-level switch is enabled. A version number obtained through HTTP is self-reported by the server and is not cryptographic binary provenance.

### 4. Formal boundary conditions

1. **No memory promotion:** a model-produced observation or extracted memory never becomes canonical merely by extraction, embedding or summarization.
2. **No authority from text:** imported markdown, repositories and files are untrusted content and never execute embedded instructions as control-plane commands.
3. **Project-scoped retrieval:** source requests must remain inside their identified project; URI prefix confusion, traversal and unexpected redirects are rejected.
4. **Byte-integrity observation:** a source downloaded from a specified URI is compared with an independently provided expected digest. This comparison is a necessary but insufficient condition for source authenticity.
5. **Explicit denial:** a second real user identity must be verified and denied for the protected resource at the relevant read surface.
6. **Evidence preservation:** conflicting models, incomplete tests and uncertain claims remain explicit as such and do not disappear in consolidation.

### 5. P03 implementation

The P03 interpreter is limited to read-oriented interactions. It permits one POST to the read-only-by-contract index consistency endpoint. It obtains credentials solely through the operator's local environment, enforces user-scoped API keys, avoids URL redirects and bounds input and response size. It validates the project name and confines downloaded filenames to a descendant path of its project root.

The operator must provision a genuine OpenViking v0.5.0 server separately and create a synthetic-only account/project with restricted ACL before running the probe. The probe never provisions accounts, turns on ACL, creates sources or changes canonical data.

### 6. Adversarial tests

Sixty-eight local tests pass: 50 inherited from P02 plus 18 P03 tests. P03 exercises actual HTTP transport using a Python localhost fixture that mimics a subset of OpenViking v0.5.0. Cases include source-content modification, expected-hash mismatch, missing index records, malformed index envelopes, version mismatch, weak ACL, malformed SHA, traversal, prefix confusion, unauthorized binary download and secret redaction.

A successful simulated test does not establish native OpenViking implementation behavior. No live embedding, semantically processed source, real multi-account isolation, startup recovery or crash-recovery tests were executed in this session.

### 7. Remaining research and engineering program

Phase P04 must establish authentic pinned process identity, perform full synthetic fixture ingest and index verification, execute actual cross-account tests and restart recovery, measure retrieval quality against a benchmark corpus, preserve OpenViking's independent AGPL licensing obligations, and implement authenticated canonical promotion only with an independent human or policy-granted authorization mechanism.

### 8. Continuity and publication

The canonical human-readable working tree has been established in Google Drive under `FABRICA_CONTEXT_FABRIC_CANONICAL_WORKING_TREE`, containing native `FCF_START_HERE`, `FCF_STATE_AND_HANDOFF` and the live `FCF_MASTER_WHITE_PAPER` document. The ZIP reference release is generated locally pending distribution. A GitHub FCF source repository has not yet been created or populated.

### 9. Conclusion

The project has progressed from architectural excavation to a packaged fail-closed reference harness with verified offline behavior. This is a useful but bounded result. The next scientifically meaningful claim requires operating the real pinned OpenViking code under isolated, reproducible conditions; otherwise the release status remains `NATIVE_LIVE_HOLD`.

### Source register

- OpenViking tagged source: https://github.com/volcengine/OpenViking/tree/v0.5.0
- Retrieval API: https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/api/06-retrieval.md
- Content API: https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/api/12-content.md
- ACL API: https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/api/12-acl.md
- System API: https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/api/07-system.md
- Authentication: https://github.com/volcengine/OpenViking/blob/v0.5.0/docs/en/guides/04-authentication.md
