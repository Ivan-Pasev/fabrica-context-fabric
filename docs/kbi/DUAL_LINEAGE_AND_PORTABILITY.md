# KBI dual-lineage and portable canonical project-cell specification

**Status**: FCF-specific adaptation, reviewable implementation proposal (not a universally ratified GILC standard).

## Source-based lineage

1. **Kernel-Based Intelligence** from the Science of Fabric Reality corpus (`kernel-based-intelligence-kbi.md` and `SRC_KBI_ROOT_v0.1.md`) models a bounded reasoning kernel with domain, routing, constraints, validation and output type; latter runtime assurance variant includes typed state, permitted actions, hard/soft invariants, monitor, partial recovery and protected identity.
2. **Knowledge Boundary Intelligence** from Digital Fabrica LIVE KBI profile defines claim/evidence separation and five outcomes PASS, FAIL, HOLD, UNKNOWN, UNRESOLVED. E0–E5 label distinct evidence properties; they are not automatically a scalar truth ladder.
3. The FDF R25 *Portable Canonical KBI* expressly proposed a sovereign project-bound capsule under `.kbi/`, with START_HERE, HANDOFF, source registry, promotion gates, lattice, agents projection and non-effect validation. FCF refabricates this proposal for scientific R&D continuity.

## Namespaced operational contract

`KBI_KERNEL` operates on plans, bounded reasoning units, invariant checks and proposed transitions. It is not a model vendor, tool credential or permission grant. `KBI_EPISTEMIC` audits what claims are supported, by exactly which source versions, under what evaluation and source authenticity assumptions. It never grants canon authority. Host permission, project identity, and operator authorization are separate constraints.

## Live Drive over projected snapshot

For any NEXT cycle: read live START_HERE, then live STATE_AND_HANDOFF, then active project constitution and native manuscripts. Compare exact revisions. `.kbi` source registry is an index of expected addresses and source *roles*, not a real-time truth oracle. If versions conflict, HOLD and surface the conflict. Never rewrite a project constitution based on a cached bundle.

## Proposed cycle and gates

SENSE → CLASSIFY → ROUTE → SYNTHESIZE/STAGE → REDTEAM → VERIFY → REQUEST REVIEW → UPDATE HANDOFF PROPOSAL → RELEASE CANDIDATE. Each edge is a prerequisite in a finite DAG; no node self-authorizes. The default is AUDIT_ONLY, and stage output remains uncommitted until the host grants scoped permission and a human authorization is obtained for protected changes.

## What machine validation can prove

A local checker confirms schema shape, project identity, legal capability-name membership, source ID referential closure, graph DAG and no broadened default gates. It does NOT prove the true operator identity, lawful publication, accuracy of the cited Google Doc, source authenticity, privacy compliance, formal mathematical proof, or product security.

## Portable install procedure

1. Discover the target project in its live Drive START_HERE and HANDOFF. Read existing laws first.
2. Namespace its sovereignty and source registry. Never copy FCF IDs unchanged into a different project.
3. Propose a target-specific `.kbi` capsule and compare to existing agents policies.
4. Run schema + DAG + negative tests with no writes to canon; record result and unanswered questions.
5. Seek appropriate project-scoped authorization; install only compatible artifacts, preserve previous revisions, update handoff last.
6. Publish a GitHub code release only after tests, rights review, issue/PR review if required, and an explicit release authorization.

## Primary sources

- KBI dual-lineage: https://docs.google.com/document/d/PROJECT_SOURCE_ID_REDACTED/edit
- Knowledge Boundary LIVE: https://docs.google.com/document/d/PROJECT_SOURCE_ID_REDACTED/edit
- Kernel-Based Intelligence root: https://drive.google.com/file/d/PROJECT_FILE_ID_REDACTED/view
- FDF reusable cell: https://docs.google.com/document/d/PROJECT_SOURCE_ID_REDACTED/edit

## Executable target-project candidate generator

`python -m fcf.kbi.scaffold` accepts exact target project ID, live Drive root, native START_HERE URL and HANDOFF URL and creates a distinct `.kbi` candidate directory without any cloud writes. Static validator uses declared boot source roles rather than FCF hardcoded IDs; candidate capabilities remain read/stage only and protected release status remains HOLD. No project is modified by scaffold. Run its tests and inspect the result manually before any installation.
