# P01 acceptance and transition gates

| Gate | Required evidence | P01 status |
|---|---|---|
| G-01 Upstream pin | Exact tag SHA and main research SHA | PASS |
| G-02 Independent package | Source without vendored OpenViking code | PASS |
| G-03 Source integrity | Byte + canonical record hash, tamper tests | PASS (local) |
| G-04 Memory proposal isolation | No auto-promotion or canonical write in implementation | PASS (local) |
| G-05 Adversarial regression | Source mismatch, cross-project, role, conflict and scope tests | PASS (local) |
| G-06 Read-only source interfaces | GitHub/Drive/OpenViking adapter shape and mock tests | PASS (mock only) |
| G-07 Native OpenViking smoke | Pinned v0.5.0 real server with synthetic corpus | NOT RUN |
| G-08 Drive and GitHub live connector | User-authorized read, version and bytes verified | NOT RUN |
| G-09 Security penetration review | Auth, ACL, agent injection, all storage surfaces | NOT RUN |
| G-10 License clearance | AGPL + main README ambiguity reviewed | HOLD |
| G-11 Canonical publication | Explicit human-approved external repository/tree | NOT REQUESTED |

**P01 conclusion:** Reference package is ready for review; real-world deployment GO is **not** claimed.


## P02 extension

The newer P02 status is maintained in `docs/P02_EVIDENCE_MATRIX.md`. An upstream-conformance HTTP fixture is not an upstream runtime. The v0.5.0 `result`-envelope compatibility repair and 19 new socket-level/adversarial tests were added under P02; native service tests and legal review are still blocking.
