# FCF v0.1 — threat model and residual risk

## Assets and security objectives

Assets: unpublished research manuscripts, source revisions, memory proposals, model context, credentials, and governance policies. v0.1 handles synthetic or deliberately authorized test data only.

Trust levels: `external source bytes` < `recorded observation` < `structural assessment` < `authenticated approval (future)` < `canonical publication (future)`.

## Surfaces

1. **GitHub raw content:** pin SHA, validate owner/repo/path, disable redirects. Threats: compromised GitHub/transport/source author, malicious bytes, large input. Mitigations: size caps, local byte hashing, no execution. External authenticity remains unverified.
2. **Drive connector export:** accept version-labelled bytes only. Threats: untrusted caller supplying fabricated revision, connector scope drift. Mitigation: caller must be a trusted connector orchestrator; FCF itself does not verify the revision.
3. **OpenViking find:** project-scoped target, returned-URI validation, HTTPS host allowlist. Threats: remote API exfiltration, prefix collisions, result contamination, server ignoring ACLs. Mitigations: read-only client and local result scope rejection; upstream authentication/ACL remains indispensable.
4. **Local file staging:** tamper, symlinked paths, concurrent writers, disk rollback, interrupted writes. Mitigations: content hashing, no-clobber object creation, write-and-fsync temp; residual: root must be private/trusted, no distributed atomicity or immutable storage enforcement against privileged local attackers.
5. **Memory proposal:** fabricated evidence, contradiction, role spoofing, prompt injection. Mitigation: source hash inspection and structural HOLD; content never becomes command. Residual: role is self-asserted in CLI, no semantic truth/secret detector, no real contradiction discovery.
6. **Licensing:** mixing independent code with AGPL code or prohibited large rewrites. Mitigation: no upstream vendoring; counsel review before service/commercial use.

## Attacks deliberately NOT claimed as solved

- Semantic prompt injection in a downstream LLM that receives retrieved text.
- Adversarial manipulation of a trusted reviewer or connected account.
- Authenticity of a cloud document whose revision string is supplied by a caller.
- Malicious code executed by a later IDE tool based on untrusted retrieval content.
- Physical/disk rollback, backup poisoning, multi-host concurrency, network MITM outside TLS trust roots.
- Source metadata freshness and complex scientific contradiction detection.

## Required production controls (P02+)

Use a trusted identity gateway, non-root scoped API keys, ACL restricted boundaries, tenant segregation, network egress policy, TLS, audited credential storage, service sandboxes, data-at-rest protection for indexes/logs/exports, background task budgets, and fail-closed policy enforcement at every mutation path.

## P02 additions

- **ACL-disabled false confidence:** An explicit restricted directory ACL is ineffective while account `acl.enabled` remains off. Mitigation: run same-account outsider read denial with a distinct user key, plus account ACL configuration verification.
- **Response-envelope downgrade:** In v0.5.0 the `find` endpoint can wrap results in `result`. The v0.1 adapter did not unwrap this, causing false empty hits. Patched and regression-tested in v0.2.
- **Gateway credential confusion:** The reader requires a user-scoped key and disallows unapproved remote HTTPS hosts; it must never be configured with root/admin identity for production.
- **Optimistic semantic attestation:** Binding a retrieved URI to a locally hashed source record demonstrates local snapshot consistency, not that the live server returned those exact bytes. To close this gap require an independently obtained remote read and a verified source-version mapping.
- **Limited negative test:** One denied path to one outsider does not establish tenant isolation globally. Extend with cross-account and group ACL campaigns before production release.
