# External FABRICA Graph Kernel — read-only interface candidate (FGK-P4)

Status: **DRAFT / NON-OPERATIVE / NO AUTHORITY PROMOTION**  
Recorded: 2026-10-18  
Repository base: `main@4a61fa8407d7aa7b72bd51abf45aabeee1c9a4bf`

## Boundary

FABRICA.GRAPH.KERNEL (FGK) is an independently versioned **external** source-structure observation service and EGIR adapter. It must remain separate from this FCF evidence/authority reference runtime. This document is an interoperability contract only: it adds no dependency, executable handler, credentials, service endpoint, MCP plugin installation, or canonical mutation.

Current external candidate: `0.4.0-p3-candidate`, local offline unit suite **75/75 PASS reported in the originating research environment**, no independent GitHub CI in this repository. Real `graphifyy==0.9.92` execution and independent Codex host registration **NOT RUN**. Do **not** inherit local FGK test PASS into FCF P11 or OpenViking service gates.

FGK Graphify source review: `Graphify-Labs/graphify@86c57be8204673c2a1b9849a3292a7dd3ab373d8` (branch v8 snapshot). The Graphify Python package is named `graphifyy`; copying its implementation is **not** part of this PR.

## Ingress contract

1. Accept an EGIR observation only from a **separately authorized caller** and a finite, selected source scope. The graph or model must never self-declare canonical authority.
2. The caller MUST provide the actual source bytes, associated source revision/commit and source locator. Merely passing a hash reported by a graph generator is insufficient to establish source authenticity.
3. Use the existing FCF `observed_source(...)` kernel path to bind byte digest to `fcf.source.v1`. The record remains `OBSERVED`, `source_authenticity=NOT_VERIFIED`, `semantic_truth=NOT_PROVEN`; any canonical admission must use independent FCF evaluation and review.
4. A graph-level proposition can be packaged only as a non-authorizing `fcf.proposal.v1` **candidate** with `authority=NONE`. Claims about code semantics (including `calls`) must carry source ranges, extraction method, confidence and completeness uncertainty.
5. Historical `_src/_tgt` Graphify direction markers MUST take precedence over undirected layout `source/target` if both are present, with source-derived fixture tests.
6. Never infer negative dependencies from absence of edges. Preserve inferred vs extracted status, parallel edges, provenance, graph snapshots and previous contradictory evidence.
7. For generated observations, consider graph content, filenames, paths and model text **untrusted input**, including prompt injection and data disclosure hazards.

## Non-claims and isolation

`FGK OBSERVED != FCF VERIFIED != GOVERNED APPROVAL != EFFECT EXECUTION`

- No FGK source or third-party code is imported into FCF.
- No graph is ingested automatically, no policy updated, no memory admitted, no Drive/GitHub files modified by an FGK tool.
- No OpenViking service/HTTP/ACL gate is closed by this contract.
- No plugin installation or independent MCP host test is implied.
- FGK original-code license is not yet selected. Public source release and third-party NOTICE/SBOM review remain HOLD.

## Review / acceptance backlog

- [ ] Dedicated independent public FGK repository created, original-code license selected and notice rules reviewed.
- [ ] Pin FGK code, schema and all source hashes through an independent GitHub CI matrix (Python 3.10/3.12/3.13).
- [ ] Execute real Graphify v0.9.92 from isolated pinned source on a public test corpus; report precision, directionality and incompleteness instead of inherited confidence.
- [ ] Construct independent FCF source record from **actual bytes** and verify tamper/HOLD cases.
- [ ] Reproduce EGIR parallel-edge, source/target reversal, path traversal and negative incomplete graph cases.
- [ ] Keep the FCF and CodexStation release gates unchanged absent exact run receipts.
