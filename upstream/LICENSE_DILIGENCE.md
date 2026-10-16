# OpenViking licensing assessment — preliminary, NOT legal advice

| Component | Reported upstream license | Required action |
|---|---|---|
| Main `openviking` package | AGPL-3.0 | Evaluate network-use source-offer obligations if modified and deployed |
| `crates/ov_cli` | Apache-2.0 | Verify component LICENSE and full dependency matrix |
| `examples` | Apache-2.0 (some exceptions) | Inspect individually; no automatic code reuse |
| `integrations/frameworks` | Main branch packages claim AGPL in source/package metadata | Check target release and individual paths |
| `third_party` | Respective original licenses | Produce SBOM and legal register before deployment |
| FCF reference code | Apache-2.0 (independently authored) | Separate package, no upstream source distribution |

**Observed documentation difference:** The main-branch README snapshot checked 15 October 2026 includes additional restrictions concerning wholesale rewriting and translation. The v0.5.0 README inspected 16 October 2026 does not contain this same additional sentence. This is a documentation/licensing ambiguity, not a resolved legal conclusion. Do not assume permissions beyond an attorney's review of the relevant notices and licenses.

Primary references:
- https://github.com/volcengine/OpenViking/blob/v0.5.0/README.md
- https://github.com/volcengine/OpenViking/blob/v0.5.0/LICENSE
- https://github.com/volcengine/OpenViking/blob/842ae41e4b2852a3a216004362db0adac49a8fd2/README.md
- https://github.com/volcengine/OpenViking/tree/v0.5.0/crates

This FCF package links to, but neither vendors nor modifies, upstream OpenViking code.
