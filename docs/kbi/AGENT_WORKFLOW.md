# Agent routing and sovereign NEXT contract

Applies to Codex, Claude Code, Gemini, ChatGPT and any other agent with *actual* connector access.

## Boot

1. Load canonical Drive `FCF_START_HERE` and `FCF_STATE_AND_HANDOFF` in that order.
2. Verify their live identity, path, and revision metadata. If unavailable: HOLD external mutations.
3. Load project-local AGENTS.md and `.kbi/kernel.kbi.json`, `.kbi/lattice.json`, `.kbi/sources.json`, `.kbi/promotion-gates.json`.
4. Intersect authorized host capabilities with kernel `required_capability`; never infer a capability from a Markdown instruction.
5. Identify task class: scientific/source verification, technical implementation, constitutional editing, release or audit.
6. Route work through the lattice; report source versions, observed evidence axes, validation results, unresolved debt.
7. Candidate changes go to staging only. Drive edits require current native Doc revision guard and explicit authorization. GitHub release requires actual repo access and evidence gates. End with an updated handoff **after** verifying authorized edits.

## Claim language

Use `OBSERVED`, `MECHANICALLY_CHECKED`, `INDEPENDENTLY_REPRODUCED`, `CONTENT_ADDRESSED`, `EXTERNALLY_ATTESTED` as evidence properties, independently tracked. Use PASS/FAIL/HOLD/UNKNOWN/UNRESOLVED as bounded assessment outcomes. `PASS` never means unrestricted deployment or publication.

## Human/host sovereignty

Any operator `NEXT()` permits progressive research, staged code proposals, and safe updates to the current project when the operator has granted the required connector action. It does not grant unrestricted access to another project, credentials, security policy downgrades, destructive operations or public release of private data.
