# Ω-OV-P03 Evidence Matrix

| Gate | Reference evidence | Outcome | Qualification |
|---|---|---|---|
| P02 regression | `tests/test_fcf.py`, `tests/test_p02_conformance.py` | PASS (50) | Existing tests rerun |
| P03 HTTP/socket contract | `tests/test_p03_live_contract.py` | PASS (18) | Real localhost socket with simulator, **not genuine OpenViking** |
| Tagged OpenViking contract | Upstream tag v0.5.0 docs | SOURCE-CHECKED | Independent source inspection via GitHub connector |
| Raw source byte integrity | P03 download + SHA-256 tests | PASS_SIMULATED | Digest matches operator supplied fixture, does not prove authenticity |
| Retrieval to exact URI | P03 simulated find | PASS_SIMULATED | Model/real vector index not run |
| Index integrity | P03 `/system/consistency` contract | PASS_SIMULATED | Fake backend only |
| Same-account negative USER read | stat + raw download denied | PASS_SIMULATED | Does not prove distinct-account isolation |
| Actual OpenViking startup | None | HOLD | Container DNS cannot resolve github.com; no installed package |
| Real server recovery | None | HOLD | Not run |
| Actual embeddings | None | HOLD | Not run |
| Authentic pinned process image | None | HOLD | HTTP `version` string alone insufficient |
| GitHub canonical repo | None | HOLD | Existing connector does not offer repository creation; user can establish desired repo |
| Google Drive canonical root | Root folder and ten subfolders | CREATED | Verified through connector; IDs in local handoff |
| Native Drive Docs | START_HERE, STATE_AND_HANDOFF, MASTER_WHITE_PAPER | CREATED | Contents updated in this turn, subject to readback |
| License legal clearance | License inventory | HOLD | Requires legal review |
| Semantic truth and production auth | None | NOT_IMPLEMENTED | Deliberate boundary |

**No test passes are allowed to substitute for native-server execution.**
