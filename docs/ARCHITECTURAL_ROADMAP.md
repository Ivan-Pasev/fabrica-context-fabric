# FCF development sequence

`DISCOVER -> LICENSE_CHECK -> ARCH_MAP -> CLASSIFY -> API_IMPORT -> IDENTITY_BOUNDARY -> PROVENANCE -> BUILD_VERIFY -> ADVERSARIAL_TEST -> MANIFEST -> v0.1 -> ARCHITECTURAL_MUTATION`

## P01 present (2026-10-16)
Independent offline reference kernel, unit tests, schemas, adapters, documentation. Real server not exercised.

## P02 synthetic OpenViking integration
Pin v0.5.0 SHA, install separate sandbox service, configure embedding/VLM, auth + ACL, import fixtures under `viking://resources/dft-research`, query via read-only adapter, test no external write endpoints and source-hash round trip. Verify storage consistency, asynchronous queue results and restart behavior. No confidential data.

## P03 evidence registry and trusted identity
User-authorized GitHub/Drive connector source attestations, policy-supplied principal objects, attestable revision binding, signed approval receipt, audit trail independent of model instructions. FCF kernel must maintain a data/control boundary even if downstream model follows an injected instruction.

## P04 verified promotion service
Independent review, cross-source consistency, contradiction ledger, exact-source hash bound approvals, idempotent transaction and rollback semantics. Prove no unapproved write to canonical source.

## P05 distribution
Selectable read-only MCP, IDE hook, or gateway adapters, context version trace, signed manifest, reproducible integration test and threat-model-based deployment profiles.

## Ω-OV-P04: KBI constitutional capsule, Drive-first continuous synthesis

The v0.4.0 research capsule keeps the two KBI meanings separately namespaced: KBI_KERNEL for bounded operational routing and invariant-mediated proposals; KBI_EPISTEMIC for claim, evidence and authority boundaries. The project-specific, finite DAG and fail-closed promotion manifest are under `.kbi/` and validated by `python -m fcf.kbi.validate`.

The Drive-first NEXT cycle reads live START_HERE → STATE_AND_HANDOFF → current constitutions and manuscripts → machine KBI candidate → staged proposals → verified tests → separately authorized edit → readback → handoff. Agents with folder access may reason and propose immediately; neither the kernel manifest nor AGENTS.md confers connector credentials or publication authority.

Production deployment remains blocked pending genuine OpenViking v0.5.0 runtime verification, identity/ACL isolation, recovery tests, upstream licensing assessment, and project-scoped approval. GitHub release remains separate from a passing local reference suite.
